# Code Guide

<!-- AI Amended: Map source, configuration, and tests to the current architecture. -->

## Entry point

`main.py` parses `translate`, `finetune`, or `adapt`, loads `config.yaml`, creates
the shared runtime through `preload()`, and instantiates the selected pipeline.
All runtime and training settings come from YAML.

## Source modules

### `src/preloading.py`

- `Runtime` holds the tokenizer, model, device, and selected model path.
- `preload()` resolves the model version and device, loads the Hugging Face
  objects, and applies generation settings.

### `src/translation.py`

- `TranslationPipeline.set_languages()` validates an interactive language pair.
- `TranslationPipeline.translate_text()` tokenizes, generates, and decodes one
  input.
- `TranslationPipeline.run_translation()` owns the CLI loop and `/exit` handling.

### `src/finetuning.py`

- `FineTuningPipeline` loads the standardized multilingual corpus.
- It optionally switches source and target fields.
- It resolves every distinct corpus language before starting shared training.

### `src/adaptation.py`

- `AdaptationPipeline` validates one new language name/code.
- It requires the new language on exactly one side of every corpus row.
- It adds the new token, resizes token embeddings, and starts shared training.

### `src/utils.py`

- Configuration, device, model-version, and language resolvers.
- Four-column CSV loading and source/target switching.
- Deterministic train/validation/test splitting.
- `TranslationDataset` for lazy multilingual tokenization.
- `Seq2SeqTrainingArguments` and `Seq2SeqTrainer` construction.
- Output preparation, checkpoint resume handling, and artifact saving.
- Target-aware test generation with spBLEU and chrF++ metrics.

Shared code belongs here only when more than one pipeline uses it. Pipeline-specific
validation stays in its pipeline module so each flow remains easy to trace.

## Corpus contract

Fine-tuning and adaptation use one UTF-8 CSV layout:

```csv
source_sentence,target_sentence,src_lang,tgt_lang
Maayong buntag.,Magandang umaga.,cebuano,tagalog
Naimbag a bigat.,Magandang umaga.,ilocano,tagalog
```

Sentence and language cells must contain non-blank text. The language columns can
mix multiple pairs in one file. Fine-tuning accepts only configured and supported
languages; adaptation accepts one configured new language and one known language
per row.

## Configuration ownership

- `model` selects the original checkpoint or a version below `models/`.
- `languages` maps user-facing names to model language codes.
- `generation` controls maximum generation length and beam count.
- `data` controls split proportions and tokenizer maximum length.
- `fine_tuning` and `adaptation` own their corpus, run name, and direction switch.
- `training` owns Trainer hyperparameters. Gradient accumulation is intentionally
  absent.

## Tests

Tests mirror the source layout:

- `testing/test_preloading.py`
- `testing/test_translation.py`
- `testing/test_finetuning.py`
- `testing/test_adaptation.py`
- `testing/test_utils.py`

`testing/conftest.py` contains the shared configuration and small tokenizer/model
fakes. The tests use pytest and never download the NLLB checkpoint or start real
training.

Run all tests with:

```bash
python -m pytest -q
```
