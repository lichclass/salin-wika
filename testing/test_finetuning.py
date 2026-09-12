import pytest

from src import finetuning


# AI Amended: Verify multilingual corpus resolution and the optional direction switch.
def test_fine_tuning_accepts_multilingual_rows_and_switches_them(
    monkeypatch, config, runtime, write_corpus, tmp_path
):
    corpus = write_corpus(
        [
            ("maayo", "mabuti", "cebuano", "tagalog"),
            ("naimbag", "mabuti", "ilocano", "tagalog"),
            ("salamat", "salamat", "cebuano", "tagalog"),
        ]
    )
    config["fine_tuning"].update(
        corpus_path=str(corpus),
        switch_source_target=True,
    )
    captured = {}

    def fake_train_model(**kwargs):
        captured.update(kwargs)
        return tmp_path / "models" / "fine", {"spBLEU": 12.0}

    monkeypatch.setattr(finetuning, "train_model", fake_train_model)

    metrics = finetuning.FineTuningPipeline(runtime, config).run_fine_tuning()

    assert metrics == {"spBLEU": 12.0}
    assert captured["run_name"] == "fine"
    assert {(record[2], record[3]) for record in captured["records"]} == {
        ("tgl_Latn", "ceb_Latn"),
        ("tgl_Latn", "ilo_Latn"),
    }
    assert captured["records"][0][:2] == ("mabuti", "maayo")


def test_fine_tuning_rejects_unavailable_languages(
    monkeypatch, config, runtime, write_corpus
):
    corpus = write_corpus(
        [
            ("maayo", "mabuti", "hiligaynon", "tagalog"),
            ("salamat", "salamat", "hiligaynon", "tagalog"),
            ("oo", "opo", "hiligaynon", "tagalog"),
        ]
    )
    config["fine_tuning"]["corpus_path"] = str(corpus)
    monkeypatch.setattr(
        finetuning,
        "train_model",
        lambda **kwargs: pytest.fail("training must not start"),
    )

    with pytest.raises(ValueError, match="run adaptation first"):
        finetuning.FineTuningPipeline(runtime, config).run_fine_tuning()
