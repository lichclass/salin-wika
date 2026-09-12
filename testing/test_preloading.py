import torch

from src import preloading


# AI Amended: Verify preloading configuration without retrieving model weights.
def test_preload_configures_the_selected_model(monkeypatch, config, runtime):
    tokenizer = runtime.tokenizer
    model = runtime.model
    calls = []

    monkeypatch.setattr(
        preloading.AutoTokenizer,
        "from_pretrained",
        lambda path: calls.append(("tokenizer", path)) or tokenizer,
    )
    monkeypatch.setattr(
        preloading.AutoModelForSeq2SeqLM,
        "from_pretrained",
        lambda path: calls.append(("model", path)) or model,
    )

    runtime = preloading.preload(config)

    model_path = "facebook/nllb-200-distilled-600M"
    assert calls == [("tokenizer", model_path), ("model", model_path)]
    assert runtime.tokenizer is tokenizer
    assert runtime.model is model
    assert runtime.device == torch.device("cpu")
    assert runtime.model_path == model_path
    assert model.generation_config.max_length == 32
    assert model.generation_config.max_new_tokens is None
    assert model.generation_config.num_beams == 2
    assert model.device == torch.device("cpu")
    assert model.eval_called
