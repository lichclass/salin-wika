import csv
from types import SimpleNamespace

import pytest
import torch


# AI Amended: Share small NLLB stand-ins so module tests stay offline and fast.
class FakeBatch(dict):
    def to(self, device):
        self.device = device
        return self


class FakeTokenizer:
    unk_token_id = 0
    pad_token_id = 99

    def __init__(self):
        self.ids = {
            "ceb_Latn": 10,
            "tgl_Latn": 11,
            "ilo_Latn": 12,
            "war_Latn": 13,
            "pag_Latn": 14,
        }
        self.src_lang = None
        self.tgt_lang = None
        self.calls = []
        self.saved_to = None

    def __len__(self):
        return 100 + len(self.ids)

    def convert_tokens_to_ids(self, token):
        return self.ids.get(token, self.unk_token_id)

    def add_special_tokens(self, tokens, replace_extra_special_tokens=False):
        assert replace_extra_special_tokens is False
        added = 0
        for token in tokens["additional_special_tokens"]:
            if token not in self.ids:
                self.ids[token] = 100 + len(self.ids)
                added += 1
        return added

    def __call__(self, text, **kwargs):
        self.calls.append((text, kwargs, self.src_lang, self.tgt_lang))
        return FakeBatch(
            input_ids=torch.tensor([[1, 2]]),
            attention_mask=torch.tensor([[1, 1]]),
        )

    def batch_decode(self, values, skip_special_tokens=True):
        return ["translated"] * len(values)

    def save_pretrained(self, output_dir):
        self.saved_to = output_dir


class FakeModel:
    def __init__(self):
        self.generation_config = SimpleNamespace(
            max_length=200,
            max_new_tokens=20,
            num_beams=1,
        )
        self.device = None
        self.eval_called = False
        self.generate_kwargs = None
        self.resized_to = None

    def to(self, device):
        self.device = device
        return self

    def eval(self):
        self.eval_called = True
        return self

    def generate(self, **kwargs):
        self.generate_kwargs = kwargs
        return torch.tensor([[5, 6]])

    def resize_token_embeddings(self, size):
        self.resized_to = size


@pytest.fixture
def config(tmp_path):
    return {
        "device": "cpu",
        "model": {
            "version": "default",
            "default_name_or_path": "facebook/nllb-200-distilled-600M",
            "directory": str(tmp_path / "models"),
        },
        "languages": {
            "tagalog": "tgl_Latn",
            "cebuano": "ceb_Latn",
            "ilocano": "ilo_Latn",
            "waray": "war_Latn",
            "pangasinense": "pag_Latn",
        },
        "generation": {"max_length": 32, "num_beams": 2},
        "data": {
            "train_size": 0.6,
            "valid_size": 0.2,
            "test_size": 0.2,
            "max_length": 32,
        },
        "fine_tuning": {
            "run_name": "fine",
            "corpus_path": "unused.csv",
            "switch_source_target": False,
        },
        "adaptation": {
            "run_name": "adapted",
            "corpus_path": "unused.csv",
            "switch_source_target": False,
            "new_language": {"name": "bikol", "code": "bik_Latn"},
        },
        "training": {
            "per_device_train_batch_size": 1,
            "per_device_eval_batch_size": 1,
            "num_train_epochs": 1,
            "learning_rate": 0.00002,
            "optimizer": "adamw_torch",
            "weight_decay": 0.0,
            "warmup_steps": 0,
            "max_grad_norm": 1.0,
            "early_stopping_patience": 0,
            "save_total_limit": 1,
            "logging_steps": 1,
            "num_workers": 0,
            "pin_memory": False,
            "fp16": False,
            "bf16": False,
            "seed": 42,
            "resume_from_checkpoint": False,
        },
    }


@pytest.fixture
def runtime():
    return SimpleNamespace(
        tokenizer=FakeTokenizer(),
        model=FakeModel(),
        device=torch.device("cpu"),
        model_path="facebook/nllb-200-distilled-600M",
    )


@pytest.fixture
def write_corpus(tmp_path):
    def write(rows, columns=None, name="corpus.csv"):
        path = tmp_path / name
        columns = columns or (
            "source_sentence",
            "target_sentence",
            "src_lang",
            "tgt_lang",
        )
        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(columns)
            writer.writerows(rows)
        return path

    return write
