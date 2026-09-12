import re

from .utils import (
    read_parallel_corpus,
    resolve_language,
    section,
    switch_source_target,
    train_model,
)


LANGUAGE_CODE_PATTERN = re.compile(r"^[a-z]{3}_[A-Z][a-z]{3}$")


# AI Amended: Add one unknown language token and train it with known languages.
class AdaptationPipeline:
    def __init__(self, runtime, config):
        self.runtime = runtime
        self.config = config
        self.pipeline_config = section(config, "adaptation")

    def run_adaptation(self):
        new_language = self.pipeline_config.get("new_language")

        if not isinstance(new_language, dict):
            raise ValueError("adaptation.new_language must be a YAML mapping.")

        new_name = new_language.get("name")
        new_code = new_language.get("code")

        if not isinstance(new_name, str) or not new_name.strip():
            raise ValueError("adaptation.new_language.name must be a non-empty string.")
        if not isinstance(new_code, str) or not LANGUAGE_CODE_PATTERN.fullmatch(
            new_code
        ):
            raise ValueError("adaptation.new_language.code must look like 'hil_Latn'.")

        new_name = new_name.strip().lower()
        available = section(self.config, "languages")

        if new_name in available or new_code in available.values():
            raise ValueError(
                f"'{new_name}' is already configured; use fine-tuning instead."
            )
        if (
            self.runtime.tokenizer.convert_tokens_to_ids(new_code)
            != self.runtime.tokenizer.unk_token_id
        ):
            raise ValueError(
                f"'{new_code}' is already supported by the selected model; add it to "
                "config.yaml and use fine-tuning instead."
            )

        records = read_parallel_corpus(self.pipeline_config.get("corpus_path"))
        switch = self.pipeline_config.get("switch_source_target", False)

        if not isinstance(switch, bool):
            raise ValueError("adaptation.switch_source_target must be a boolean.")
        if switch:
            records = switch_source_target(records)

        known_codes = {}
        resolved_records = []
        discrepancies = []

        for row_number, (source, target, source_lang, target_lang) in enumerate(
            records, start=2
        ):
            source_is_new = source_lang.lower() == new_name or source_lang == new_code
            target_is_new = target_lang.lower() == new_name or target_lang == new_code

            if source_is_new == target_is_new:
                discrepancies.append(
                    f"CSV row {row_number} must contain the new language on "
                    "exactly one side."
                )
                continue

            known_language = target_lang if source_is_new else source_lang

            if known_language not in known_codes:
                try:
                    known_codes[known_language] = resolve_language(
                        self.config, known_language, self.runtime.tokenizer
                    )
                except ValueError as error:
                    discrepancies.append(str(error))
                    continue

            source_code = new_code if source_is_new else known_codes[known_language]
            target_code = new_code if target_is_new else known_codes[known_language]
            resolved_records.append((source, target, source_code, target_code))

        if discrepancies:
            details = "\n- ".join(dict.fromkeys(discrepancies))
            raise ValueError(f"Adaptation corpus validation failed:\n- {details}")

        added = self.runtime.tokenizer.add_special_tokens(
            {"additional_special_tokens": [new_code]},
            replace_extra_special_tokens=False,
        )

        if added != 1:
            raise ValueError(f"Could not add the new language token '{new_code}'.")

        self.runtime.model.resize_token_embeddings(len(self.runtime.tokenizer))

        output_dir, metrics = train_model(
            config=self.config,
            runtime=self.runtime,
            records=resolved_records,
            run_name=self.pipeline_config.get("run_name"),
        )
        print(f"Adapted model saved to '{output_dir}'.")

        return metrics
