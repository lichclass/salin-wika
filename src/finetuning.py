from .utils import (
    read_parallel_corpus,
    resolve_language,
    section,
    switch_source_target,
    train_model,
)


# AI Amended: Fine-tune only after verifying every corpus language.
class FineTuningPipeline:
    def __init__(self, runtime, config):
        self.runtime = runtime
        self.config = config
        self.pipeline_config = section(config, "fine_tuning")

    def run_fine_tuning(self):
        records = read_parallel_corpus(self.pipeline_config.get("corpus_path"))
        switch = self.pipeline_config.get("switch_source_target", False)

        if not isinstance(switch, bool):
            raise ValueError("fine_tuning.switch_source_target must be a boolean.")
        if switch:
            records = switch_source_target(records)

        language_codes = {}
        discrepancies = []
        corpus_languages = {record[2] for record in records} | {
            record[3] for record in records
        }

        for language in sorted(corpus_languages):
            try:
                language_codes[language] = resolve_language(
                    config=self.config,
                    language=language,
                    tokenizer=self.runtime.tokenizer,
                )
            except ValueError as error:
                discrepancies.append(str(error))

        if discrepancies:
            details = "\n- ".join(discrepancies)
            raise ValueError(
                "Fine-tuning stopped because the corpus contains unavailable "
                "languages. Add NLLB-supported languages to config.yaml or run "
                "adaptation first:\n- "
                f"{details}"
            )

        resolved_records = [
            (source, target, language_codes[source_lang], language_codes[target_lang])
            for source, target, source_lang, target_lang in records
        ]

        output_dir, metrics = train_model(
            config=self.config,
            runtime=self.runtime,
            records=resolved_records,
            run_name=self.pipeline_config.get("run_name"),
        )
        print(f"Fine-tuned model saved to '{output_dir}'.")

        return metrics
