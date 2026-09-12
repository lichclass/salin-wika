import torch

from .utils import positive_int, resolve_language, section


# AI Amended: Resolve the requested language pair before entering the translation loop.
class TranslationPipeline:
    def __init__(self, runtime, config):
        self.runtime = runtime
        self.config = config
        self.max_length = positive_int(
            section(config, "data").get("max_length"), "data.max_length"
        )
        self.source_code = None
        self.target_code = None

    def set_languages(self, source_language, target_language):
        source_code = resolve_language(
            self.config, source_language, self.runtime.tokenizer
        )
        target_code = resolve_language(
            self.config, target_language, self.runtime.tokenizer
        )
        if source_code == target_code:
            raise ValueError("Translation source and target languages must differ.")
        self.source_code = source_code
        self.target_code = target_code

    def translate_text(self, text):
        self.runtime.tokenizer.src_lang = self.source_code
        self.runtime.tokenizer.tgt_lang = self.target_code
        inputs = self.runtime.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_length,
        ).to(self.runtime.device)
        with torch.inference_mode():
            output = self.runtime.model.generate(
                **inputs,
                forced_bos_token_id=self.runtime.tokenizer.convert_tokens_to_ids(
                    self.target_code
                ),
            )
        return self.runtime.tokenizer.batch_decode(output, skip_special_tokens=True)[0]

    def run_translation(self):
        while True:
            try:
                source_language = input(
                    "Enter the source language (/exit to quit): "
                ).strip()
                if source_language == "/exit":
                    return
                target_language = input(
                    "Enter the target language (/exit to quit): "
                ).strip()
                if target_language == "/exit":
                    return
                self.set_languages(source_language, target_language)
                break
            except (EOFError, KeyboardInterrupt):
                print("")
                return
            except ValueError as error:
                print(error)

        while True:
            try:
                text = input(
                    f"[Source] {source_language.capitalize()} (/exit to quit): "
                ).strip()
            except (EOFError, KeyboardInterrupt):
                print("")
                return
            if text == "/exit":
                return
            if text:
                translation = self.translate_text(text)
                print(f"[Target] {target_language.capitalize()}: {translation}")
