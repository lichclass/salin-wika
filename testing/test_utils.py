from types import SimpleNamespace

import pytest
import torch

from src import utils


# AI Amended: Cover the shared corpus, training, and evaluation boundaries directly.
def test_parallel_corpus_contract_and_direction_switch(write_corpus):
    corpus = write_corpus(
        [
            (" maayo ", " mabuti ", " cebuano ", " tagalog "),
            ("naimbag", "mabuti", "ilocano", "tagalog"),
            ("salamat", "salamat", "cebuano", "tagalog"),
        ]
    )

    records = utils.read_parallel_corpus(corpus)

    assert records[0] == ("maayo", "mabuti", "cebuano", "tagalog")
    assert utils.switch_source_target(records)[0] == (
        "mabuti",
        "maayo",
        "tagalog",
        "cebuano",
    )


def test_parallel_corpus_requires_standard_columns(write_corpus):
    corpus = write_corpus(
        [("maayo", "mabuti")],
        columns=("cebuano", "tagalog"),
    )

    with pytest.raises(ValueError, match="Missing corpus column"):
        utils.read_parallel_corpus(corpus)


def test_split_records_is_deterministic_and_non_overlapping(config):
    records = [(index, index) for index in range(10)]

    first = utils.split_records(records, config["data"], seed=7)
    second = utils.split_records(records, config["data"], seed=7)

    assert first == second
    assert [len(split) for split in first] == [6, 2, 2]
    assert set(first[0]).isdisjoint(first[1])
    assert set(first[0]).isdisjoint(first[2])


def test_training_arguments_do_not_accumulate_gradients(config, tmp_path):
    arguments = utils.training_arguments(
        config,
        tmp_path / "run",
        torch.device("cpu"),
    )

    assert arguments.gradient_accumulation_steps == 1
    assert arguments.generation_max_length == 32
    assert arguments.generation_num_beams == 2


def test_translation_metrics_include_spbleu_and_chrf_plus_plus(monkeypatch):
    class Metric:
        def __init__(self, score):
            self.score = score

        def corpus_score(self, hypotheses, references):
            assert hypotheses == ["translation"]
            assert references == [["reference"]]
            return SimpleNamespace(score=self.score)

    monkeypatch.setattr(utils, "BLEU", lambda tokenize: Metric(21.5))
    monkeypatch.setattr(utils, "CHRF", lambda word_order: Metric(48.0))

    assert utils.translation_metrics(["translation"], ["reference"]) == {
        "spBLEU": 21.5,
        "chrF++": 48.0,
    }


def test_train_model_runs_the_shared_training_flow(monkeypatch, config, runtime):
    records = [
        (f"source {index}", f"target {index}", "ceb_Latn", "tgl_Latn")
        for index in range(10)
    ]
    captured = {}

    class Trainer:
        def train(self, resume_from_checkpoint):
            captured["resume"] = resume_from_checkpoint
            return SimpleNamespace(metrics={"train_loss": 1.0})

        def save_model(self, output_dir):
            captured["saved_model"] = output_dir

        def save_state(self):
            captured["state_saved"] = True

        def save_metrics(self, split, metrics):
            captured[split] = metrics

        def evaluate(self):
            return {"eval_loss": 0.5}

    trainer = Trainer()

    def fake_build_trainer(
        loaded_config, loaded_runtime, output_dir, train_dataset, valid_dataset
    ):
        captured["train_records"] = train_dataset.records
        captured["valid_records"] = valid_dataset.records
        return trainer

    def fake_evaluate(trainer, test_records, tokenizer, max_length):
        captured["test_records"] = test_records
        return {"spBLEU": 10.0, "chrF++": 20.0}

    monkeypatch.setattr(utils, "build_trainer", fake_build_trainer)
    monkeypatch.setattr(utils, "evaluate_multilingual", fake_evaluate)

    output_dir, metrics = utils.train_model(config, runtime, records, "run")

    assert [
        len(captured["train_records"]),
        len(captured["valid_records"]),
        len(captured["test_records"]),
    ] == [6, 2, 2]
    assert captured["resume"] is False
    assert captured["saved_model"] == str(output_dir)
    assert captured["state_saved"]
    assert runtime.tokenizer.saved_to == str(output_dir)
    assert (output_dir / "effective_config.yaml").is_file()
    assert metrics == {"spBLEU": 10.0, "chrF++": 20.0}
