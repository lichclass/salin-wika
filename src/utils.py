import math
import random
from pathlib import Path

import numpy as np
import polars as pl
import torch
import yaml
from sacrebleu.metrics import BLEU, CHRF
from torch.utils.data import Dataset
from transformers import (
    DataCollatorForSeq2Seq,
    EarlyStoppingCallback,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)


CORPUS_COLUMNS = ("source_sentence", "target_sentence", "src_lang", "tgt_lang")


def section(config, name):
    value = config.get(name)

    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a YAML mapping.")

    return value


def positive_int(value, name, allow_zero=False):
    if allow_zero:
        minimum = 0
    else:
        minimum = 1

    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        if allow_zero:
            qualifier = "non-negative"
        else:
            qualifier = "positive"

        raise ValueError(f"{name} must be a {qualifier} integer.")

    return value


# AI Amended: Resolve the original NLLB checkpoint or one saved model version.
def resolve_model_path(config):
    model_config = section(config, "model")
    version = model_config.get("version", "default")

    if not isinstance(version, str) or not version.strip():
        raise ValueError("model.version must be a non-empty string.")

    if version == "default":
        model_name = model_config.get("default_name_or_path")

        if not isinstance(model_name, str) or not model_name.strip():
            raise ValueError("model.default_name_or_path must be a non-empty string.")

        return model_name

    if version != Path(version).name:
        raise ValueError("model.version must be a directory name, not a path.")

    model_path = Path(model_config.get("directory", "models")) / version

    if not model_path.is_dir():
        raise FileNotFoundError(f"Model version not found: {model_path}")

    return str(model_path)


def resolve_device(configured_device):
    if configured_device == "auto":
        if torch.cuda.is_available():
            configured_device = "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            configured_device = "mps"
        else:
            configured_device = "cpu"

    if configured_device == "cuda" and not torch.cuda.is_available():
        raise ValueError("CUDA was requested but is not available.")

    if configured_device == "mps" and not (
        hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
    ):
        raise ValueError("MPS was requested but is not available.")

    if configured_device not in {"cpu", "cuda", "mps"}:
        raise ValueError("device must be one of: auto, cpu, cuda, mps.")

    return torch.device(configured_device)


def resolve_language(config, language, tokenizer):
    languages = section(config, "languages")

    if not isinstance(language, str) or not language.strip():
        raise ValueError("Language must be a non-empty name or NLLB code.")

    value = language.strip()
    code = languages.get(value.lower())

    if code is None and value in languages.values():
        code = value

    if not isinstance(code, str):
        choices = ", ".join(sorted(languages))
        raise ValueError(f"Unknown language '{value}'. Available: {choices}.")

    if tokenizer.convert_tokens_to_ids(code) == tokenizer.unk_token_id:
        raise ValueError(f"The selected model does not support '{code}'.")

    return code


# AI Amended: Enforce one multilingual corpus contract for fine-tuning and adaptation.
def read_parallel_corpus(path):
    corpus_path = Path(path)

    if not corpus_path.is_file():
        raise FileNotFoundError(f"Corpus not found: {corpus_path}")

    frame = pl.read_csv(corpus_path)
    missing = [column for column in CORPUS_COLUMNS if column not in frame.columns]

    if missing:
        raise ValueError(f"Missing corpus column(s): {', '.join(missing)}.")

    records = []
    rows = frame.select(CORPUS_COLUMNS).iter_rows()
    for row_number, values in enumerate(rows, start=2):
        if any(not isinstance(value, str) or not value.strip() for value in values):
            raise ValueError(f"Blank or non-text value at CSV row {row_number}.")

        records.append(tuple(value.strip() for value in values))

    if len(records) < 3:
        raise ValueError("The corpus must contain at least three sentence pairs.")

    return records


def switch_source_target(records):
    return [
        (target, source, target_lang, source_lang)
        for source, target, source_lang, target_lang in records
    ]


def split_records(records, data_config, seed):
    sizes = tuple(
        data_config.get(name)
        for name in ("train_size", "valid_size", "test_size")
    )

    if any(
        not isinstance(size, (int, float)) or isinstance(size, bool)
        for size in sizes
    ):
        raise ValueError("data split sizes must be numbers.")

    if any(size <= 0 for size in sizes) or not math.isclose(sum(sizes), 1.0):
        raise ValueError("data split sizes must be positive and sum to 1.0.")

    shuffled = list(records)
    random.Random(seed).shuffle(shuffled)

    train_count = int(len(shuffled) * sizes[0])
    valid_count = int(len(shuffled) * sizes[1])

    if min(train_count, valid_count, len(shuffled) - train_count - valid_count) == 0:
        raise ValueError("Each data split must contain at least one sentence pair.")

    splits = (
        shuffled[:train_count],
        shuffled[train_count : train_count + valid_count],
        shuffled[train_count + valid_count :],
    )

    return splits


class TranslationDataset(Dataset):
    def __init__(self, records, tokenizer, max_length):
        self.records = records
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.records)

    def __getitem__(self, index):
        source, target, source_code, target_code = self.records[index]
        self.tokenizer.src_lang = source_code
        self.tokenizer.tgt_lang = target_code

        return self.tokenizer(
            source,
            text_target=target,
            truncation=True,
            max_length=self.max_length,
        )


# AI Amended: Read each option once and build one explicit Trainer configuration.
def training_arguments(config, output_dir, device):
    training = section(config, "training")
    generation = section(config, "generation")

    fp16 = training.get("fp16", False)
    bf16 = training.get("bf16", False)
    pin_memory = training.get("pin_memory", True)

    if not isinstance(fp16, bool) or not isinstance(bf16, bool) or fp16 and bf16:
        raise ValueError(
            "training.fp16 and training.bf16 must be booleans and cannot both be true."
        )
    if not isinstance(pin_memory, bool):
        raise ValueError("training.pin_memory must be a boolean.")
    if device.type == "cpu" and (fp16 or bf16):
        raise ValueError("Mixed precision is not supported by this CLI on CPU.")

    train_batch_size = positive_int(
        training.get("per_device_train_batch_size"),
        "training.per_device_train_batch_size",
    )
    eval_batch_size = positive_int(
        training.get("per_device_eval_batch_size"),
        "training.per_device_eval_batch_size",
    )
    warmup_steps = positive_int(
        training.get("warmup_steps", 0),
        "training.warmup_steps",
        allow_zero=True,
    )
    save_total_limit = positive_int(
        training.get("save_total_limit"),
        "training.save_total_limit",
    )
    logging_steps = positive_int(
        training.get("logging_steps"),
        "training.logging_steps",
    )
    num_workers = positive_int(
        training.get("num_workers", 0),
        "training.num_workers",
        allow_zero=True,
    )
    seed = positive_int(training.get("seed"), "training.seed", allow_zero=True)
    max_length = positive_int(generation.get("max_length"), "generation.max_length")
    num_beams = positive_int(generation.get("num_beams"), "generation.num_beams")

    arguments = Seq2SeqTrainingArguments(
        output_dir=str(output_dir),
        per_device_train_batch_size=train_batch_size,
        per_device_eval_batch_size=eval_batch_size,
        num_train_epochs=training.get("num_train_epochs"),
        learning_rate=training.get("learning_rate"),
        optim=training.get("optimizer", "adamw_torch"),
        weight_decay=training.get("weight_decay", 0.0),
        warmup_steps=warmup_steps,
        max_grad_norm=training.get("max_grad_norm", 1.0),
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        save_total_limit=save_total_limit,
        logging_strategy="steps",
        logging_steps=logging_steps,
        predict_with_generate=True,
        generation_max_length=max_length,
        generation_num_beams=num_beams,
        dataloader_num_workers=num_workers,
        dataloader_pin_memory=pin_memory and device.type == "cuda",
        fp16=fp16,
        bf16=bf16,
        use_cpu=device.type == "cpu",
        report_to="none",
        seed=seed,
        data_seed=seed,
    )

    return arguments


def prepare_output(config, run_name):
    if not isinstance(run_name, str) or not run_name or run_name != Path(run_name).name:
        raise ValueError("run_name must be a directory name, not a path.")

    output_dir = Path(section(config, "model").get("directory", "models")) / run_name
    resume = section(config, "training").get("resume_from_checkpoint", False)

    if not isinstance(resume, bool):
        raise ValueError("training.resume_from_checkpoint must be a boolean.")
    if output_dir.exists() and any(output_dir.iterdir()) and not resume:
        raise FileExistsError(
            f"'{output_dir}' is not empty; choose another run_name or enable "
            "checkpoint resume."
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "effective_config.yaml", "w", encoding="utf-8") as file:
        yaml.safe_dump(config, file, sort_keys=False, allow_unicode=True)

    return output_dir, resume


def build_trainer(config, runtime, output_dir, train_dataset, valid_dataset):
    patience = positive_int(
        section(config, "training").get("early_stopping_patience", 0),
        "training.early_stopping_patience",
        allow_zero=True,
    )

    callbacks = (
        [EarlyStoppingCallback(early_stopping_patience=patience)]
        if patience
        else []
    )

    trainer = Seq2SeqTrainer(
        model=runtime.model,
        args=training_arguments(config, output_dir, runtime.device),
        train_dataset=train_dataset,
        eval_dataset=valid_dataset,
        processing_class=runtime.tokenizer,
        data_collator=DataCollatorForSeq2Seq(
            tokenizer=runtime.tokenizer,
            model=runtime.model,
        ),
        callbacks=callbacks,
    )

    return trainer


def decode_predictions(prediction_output, tokenizer):
    predictions = prediction_output.predictions

    if isinstance(predictions, tuple):
        predictions = predictions[0]

    labels = np.where(
        prediction_output.label_ids == -100,
        tokenizer.pad_token_id,
        prediction_output.label_ids,
    )

    hypotheses = [
        text.strip()
        for text in tokenizer.batch_decode(predictions, skip_special_tokens=True)
    ]

    references = [
        text.strip()
        for text in tokenizer.batch_decode(labels, skip_special_tokens=True)
    ]

    return hypotheses, references


def translation_metrics(hypotheses, references):
    scores = {
        "spBLEU": BLEU(tokenize="flores200")
        .corpus_score(hypotheses, [references])
        .score,
        "chrF++": CHRF(word_order=2)
        .corpus_score(hypotheses, [references])
        .score,
    }

    return scores


# AI Amended: Force the correct target token for each language group.
def evaluate_multilingual(trainer, records, tokenizer, max_length):
    grouped = {}

    for record in records:
        grouped.setdefault(record[3], []).append(record)

    hypotheses = []
    references = []
    weighted_loss = 0.0

    for target_code, group in grouped.items():
        dataset = TranslationDataset(group, tokenizer, max_length)

        output = trainer.predict(
            dataset,
            metric_key_prefix="test",
            forced_bos_token_id=tokenizer.convert_tokens_to_ids(target_code),
        )

        group_hypotheses, group_references = decode_predictions(output, tokenizer)
        hypotheses.extend(group_hypotheses)
        references.extend(group_references)
        weighted_loss += output.metrics.get("test_loss", 0.0) * len(group)

    metrics = {"test_loss": weighted_loss / len(records)}
    metrics.update(translation_metrics(hypotheses, references))
    trainer.save_metrics("test", metrics)

    return metrics


# AI Amended: Share full-weight training while keeping pipeline validation visible.
def train_model(config, runtime, records, run_name):
    data_config = section(config, "data")
    training = section(config, "training")
    max_length = positive_int(data_config.get("max_length"), "data.max_length")
    seed = positive_int(training.get("seed"), "training.seed", allow_zero=True)
    train_records, valid_records, test_records = split_records(
        records, data_config, seed
    )
    train_dataset = TranslationDataset(train_records, runtime.tokenizer, max_length)
    valid_dataset = TranslationDataset(valid_records, runtime.tokenizer, max_length)

    output_dir, resume = prepare_output(config, run_name)
    trainer = build_trainer(config, runtime, output_dir, train_dataset, valid_dataset)

    train_result = trainer.train(resume_from_checkpoint=resume)
    trainer.save_model(str(output_dir))

    runtime.tokenizer.save_pretrained(str(output_dir))
    trainer.save_state()
    trainer.save_metrics("train", train_result.metrics)
    trainer.save_metrics("validation", trainer.evaluate())
    metrics = evaluate_multilingual(
        trainer,
        test_records,
        runtime.tokenizer,
        max_length,
    )

    return output_dir, metrics
