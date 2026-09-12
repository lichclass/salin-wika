import pytest

from src import adaptation


# AI Amended: Verify one new token can be adapted against multiple known languages.
def test_adaptation_adds_the_new_language_and_switches_rows(
    monkeypatch, config, runtime, write_corpus, tmp_path
):
    corpus = write_corpus(
        [
            ("marhay", "maganda", "bikol", "tagalog"),
            ("dios mabalos", "salamat", "bik_Latn", "cebuano"),
            ("iyo", "oo", "bikol", "tagalog"),
        ]
    )
    config["adaptation"].update(
        corpus_path=str(corpus),
        switch_source_target=True,
        new_language={"name": " Bikol ", "code": "bik_Latn"},
    )
    captured = {}

    def fake_train_model(**kwargs):
        captured.update(kwargs)
        return tmp_path / "models" / "adapted", {"chrF++": 34.0}

    monkeypatch.setattr(adaptation, "train_model", fake_train_model)

    metrics = adaptation.AdaptationPipeline(runtime, config).run_adaptation()

    assert metrics == {"chrF++": 34.0}
    assert runtime.tokenizer.convert_tokens_to_ids("bik_Latn") != 0
    assert runtime.model.resized_to == len(runtime.tokenizer)
    assert {(record[2], record[3]) for record in captured["records"]} == {
        ("tgl_Latn", "bik_Latn"),
        ("ceb_Latn", "bik_Latn"),
    }
    assert "bikol" not in config["languages"]


def test_adaptation_requires_the_new_language_on_one_side(
    monkeypatch, config, runtime, write_corpus
):
    corpus = write_corpus(
        [
            ("marhay", "maganda", "bikol", "tagalog"),
            ("maayo", "mabuti", "cebuano", "tagalog"),
            ("iyo", "oo", "bikol", "tagalog"),
        ]
    )
    config["adaptation"]["corpus_path"] = str(corpus)
    monkeypatch.setattr(
        adaptation,
        "train_model",
        lambda **kwargs: pytest.fail("training must not start"),
    )

    with pytest.raises(ValueError, match="exactly one side"):
        adaptation.AdaptationPipeline(runtime, config).run_adaptation()
