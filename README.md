# SalinWika

<!-- AI Amended: Align project usage with the current three-pipeline architecture. -->

SalinWika is a configuration-driven CLI for multilingual translation, full
fine-tuning, and new-language adaptation using Meta's
`facebook/nllb-200-distilled-600M` checkpoint.

> NLLB uses the CC BY-NC 4.0 license. Its model card describes it as a research
> model that is not intended for production, certified, medical, legal, or
> document translation.

## Setup

Use Python 3.12 or newer:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

All runtime and training settings live in `config.yaml`. `device` accepts
`auto`, `cuda`, `mps`, or `cpu`; requesting an unavailable device raises an
error instead of silently falling back.

## CLI

SalinWika has three pipelines:

```bash
python main.py translate
python main.py finetune
python main.py adapt
```

- `translate` prompts for the source and target language, then translates until
  `/exit`.
- `finetune` updates all model weights using configured, model-supported
  languages.
- `adapt` adds one unsupported language token, resizes the token embeddings, and
  updates all model weights from parallel data.

Every command first loads the selected tokenizer and model. The default configured
languages are Tagalog, Cebuano, Ilocano, Waray, and Pangasinense.

## Model versions

The original NLLB checkpoint is selected with:

```yaml
model:
  version: default
  default_name_or_path: facebook/nllb-200-distilled-600M
  directory: models
```

To use a trained model saved as `models/multilingual-finetuned`, set:

```yaml
model:
  version: multilingual-finetuned
  default_name_or_path: facebook/nllb-200-distilled-600M
  directory: models
```

For an adapted model, also add the new language name and code to `languages`
before using it for translation or fine-tuning.

## Corpus format

Fine-tuning and adaptation require a UTF-8 CSV with these exact columns:

```csv
source_sentence,target_sentence,src_lang,tgt_lang
Maayong buntag.,Magandang umaga.,cebuano,tagalog
Naimbag a bigat.,Magandang umaga.,ilocano,tagalog
```

One corpus may contain more than two languages and multiple translation pairs.
All cells must contain non-blank text.

Fine-tuning requires every language to exist in `languages` and in the selected
tokenizer. If NLLB already supports a language that is missing from `languages`,
add its name/code mapping and use fine-tuning.

Adaptation accepts one new language per run. The new code must not already be
supported by the selected tokenizer, and every row must contain the new language
on exactly one side. The other side may use any configured, supported language.

Set `switch_source_target: true` in the selected pipeline section to reverse all
source sentences, target sentences, and language fields. Reverse rows are not
created automatically.

## Training and outputs

Training uses Hugging Face `Seq2SeqTrainer`, dynamic padding, deterministic data
splits, epoch validation and checkpointing, optional early stopping, and
best-model restoration by validation loss. It performs full-weight updates with
no gradient accumulation.

Held-out results include loss, FLORES-200 spBLEU, and chrF++. Mixed target
languages are evaluated with the correct forced target token for each group.

Each run is saved below `models/<run_name>` and contains:

- model and tokenizer files loadable with `from_pretrained()`;
- bounded checkpoints and Trainer state;
- `effective_config.yaml`;
- train, validation, and test metrics.

Training only directly optimizes corpus directions. An adapted Hiligaynon–Tagalog
model may transfer to Hiligaynon–Cebuano, but that direction is not guaranteed
without corresponding parallel examples.

The 600M model should be trained on a capable GPU. CPU is suitable for tests and
limited inference but is impractical for substantial training. The first spBLEU
evaluation may download SacreBLEU's FLORES-200 tokenizer.

## Tests

The pytest layout mirrors the five modules in `src/` and uses lightweight fakes,
so tests do not download or train NLLB:

```bash
python -m pytest -q
```

## Docker

```bash
docker build -t salinwika .
docker run --rm salinwika --help
docker run --rm -it \
  -v "$PWD/config.yaml:/app/config.yaml:ro" \
  -v "$PWD/models:/app/models" \
  salinwika translate
docker run --rm -it --gpus all \
  -v "$PWD/config.yaml:/app/config.yaml:ro" \
  -v "$PWD/corpus:/app/corpus:ro" \
  -v "$PWD/models:/app/models" \
  salinwika finetune
```

Apple MPS is available only to local macOS Python, not inside the Linux
container.

See [Architecture](docs/ARCHITECTURE.md), [Code Guide](docs/CODE_GUIDE.md), the
[Frontend Guide](docs/FRONTEND_GUIDE.md), the
[NLLB documentation](https://huggingface.co/docs/transformers/model_doc/nllb),
and the
[official model card](https://huggingface.co/facebook/nllb-200-distilled-600M).
