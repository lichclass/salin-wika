import pytest

from src.translation import TranslationPipeline


# AI Amended: Exercise the interactive translation flow with an in-memory runtime.
def test_translation_prompts_for_languages_and_translates(
    monkeypatch, capsys, config, runtime
):
    responses = iter(["cebuano", "tagalog", "Maayong buntag.", "/exit"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(responses))

    pipeline = TranslationPipeline(runtime, config)
    pipeline.run_translation()

    assert runtime.tokenizer.calls[0][2:] == ("ceb_Latn", "tgl_Latn")
    assert runtime.model.generate_kwargs["forced_bos_token_id"] == 11
    assert "[Target] Tagalog: translated" in capsys.readouterr().out


def test_translation_rejects_the_same_language(config, runtime):
    pipeline = TranslationPipeline(runtime, config)

    with pytest.raises(ValueError, match="must differ"):
        pipeline.set_languages("tagalog", "tgl_Latn")
