# Architecture

<!-- AI Amended: Describe the maintained three-pipeline NLLB architecture. -->

SalinWika is a configuration-driven CLI built around one shared NLLB runtime and
three pipelines: translation, full fine-tuning, and new-language adaptation.

## Execution flow

`main.py` loads `config.yaml`, preloads the selected tokenizer and model, and
dispatches one command:

- `translate` starts interactive translation.
- `finetune` trains on languages already supported by the selected model.
- `adapt` adds one unsupported language token and trains it from parallel data.

The preloader resolves `device`, loads the tokenizer before the model, applies
`generation.max_length` and `generation.num_beams`, moves the model to the
selected device, and returns one shared `Runtime`. Transformer progress bars are
disabled in `src/preloading.py`.

## Model selection

`model.version: default` loads `model.default_name_or_path`. Any other version
loads `models/<version>` or the directory configured by `model.directory`.
Local versions must be directory names, not arbitrary paths.

The same selection applies to all three pipelines. A saved fine-tuned or adapted
model can therefore be used for later translation or training by changing only
`model.version`.

## Translation pipeline

`src/translation.py` prompts for the source and target language before accepting
text. Both values may be configured language names or NLLB codes. The resolver
requires the language to exist in `languages` and in the selected tokenizer.

For each input, the pipeline:

1. Sets the tokenizer source and target language codes.
2. Tokenizes and truncates the source text.
3. Forces the target language token during beam-search generation.
4. Decodes the generated token IDs without special tokens.
5. Continues until `/exit`, EOF, or interruption.

## Fine-tuning pipeline

`src/finetuning.py` performs full-weight fine-tuning. Its CSV may contain any
number of language pairs, but every row must use this schema:

```text
source_sentence,target_sentence,src_lang,tgt_lang
```

`src_lang` and `tgt_lang` may be configured names or NLLB codes. Every language
must be present in `languages` and supported by the selected tokenizer. If any
language is unavailable, the entire run stops and directs the user to adaptation.

When `fine_tuning.switch_source_target` is true, all four source/target fields are
reversed before language resolution and splitting.

## Adaptation pipeline

`src/adaptation.py` is transfer learning from NLLB, not pretraining from random
weights. It accepts the same four-column corpus format as fine-tuning.

`adaptation.new_language` defines one language name and one NLLB-style code. The
name/code must not already be configured or supported by the selected tokenizer.
Every corpus row must place that new language on exactly one side; the other side
may be any configured, tokenizer-supported language.

After validation, the pipeline adds the language token, resizes the model token
embeddings, and runs the shared full-weight training flow. Setting
`adaptation.switch_source_target` reverses every row. Reverse examples are not
created automatically.

## Shared training flow

`src/utils.py` owns corpus validation, deterministic splitting, lazy per-row
tokenization, trainer construction, artifact saving, and evaluation.

The configured train, validation, and test proportions must be positive and sum
to one. Each split must contain at least one row. Training uses
`Seq2SeqTrainer`, dynamic sequence-to-sequence padding, epoch validation and
checkpointing, optional early stopping, and best-model restoration by validation
loss. Gradient accumulation is not configured, so the Trainer value remains one.

Held-out records are grouped by target language so generation forces the correct
target token for every pair. Final test metrics include loss, FLORES-200 spBLEU,
and chrF++.

Training only directly optimizes the language directions present in the corpus.
Transfer to an unseen pair, such as an adapted language to another configured
language, may occur but is not guaranteed without parallel data for that pair.

## Artifacts

Each training run writes to `models/<run_name>` or the configured model directory.
The directory contains the model, tokenizer, Trainer state, bounded checkpoints,
the effective YAML configuration, and train, validation, and test metrics.

The source repository and the selected NLLB weights retain their respective
licenses; saving a local version does not change the NLLB model license.
