from dataclasses import dataclass

import torch
import transformers
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from .utils import positive_int, resolve_device, resolve_model_path, section


transformers.logging.disable_progress_bar()


@dataclass
class Runtime:
    tokenizer: object
    model: object
    device: torch.device
    model_path: str


# AI Amended: Load the selected original or local model once for every pipeline.
def preload(config):
    generation = section(config, "generation")
    max_length = positive_int(generation.get("max_length"), "generation.max_length")
    num_beams = positive_int(generation.get("num_beams"), "generation.num_beams")
    model_path = resolve_model_path(config)
    device = resolve_device(config.get("device", "auto"))

    print(f"Loading tokenizer and model from '{model_path}' on {device}...")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
    model.generation_config.max_length = max_length
    model.generation_config.max_new_tokens = None
    model.generation_config.num_beams = num_beams
    model.to(device)
    model.eval()
    print("Tokenizer and model loaded.")

    return Runtime(
        tokenizer=tokenizer,
        model=model,
        device=device,
        model_path=model_path,
    )
