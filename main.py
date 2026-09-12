import argparse
from pathlib import Path

import yaml

from src.preloading import preload
from src.translation import TranslationPipeline
from src.finetuning import FineTuningPipeline
from src.adaptation import AdaptationPipeline

CONFIG_PATH = Path("config.yaml")


# AI Amended: Expose the four NLLB pipelines through a small config-driven CLI.
def load_config(config_path=CONFIG_PATH):

    print("Loading configs...")

    with open(config_path, encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if not isinstance(config, dict):
        raise ValueError(f"'{config_path}' must contain a YAML mapping.")
    
    print("Loaded: configs...")
    
    return config


def create_parser():

    parser = argparse.ArgumentParser(description="Run NLLB multilingual translation pipelines.")

    parser.add_argument(
        "command",
        choices=("translate", "finetune", "adapt"),
        help="Pipeline to run; all settings come from config.yaml.",
    )

    return parser


def main():

    args = create_parser().parse_args()
    config = load_config()
    runtime = preload(config)

    pipeline_args = {
        "runtime": runtime,
        "config": config,
    }

    if args.command == "translate":
        translation_pipeline = TranslationPipeline(**pipeline_args)
        translation_pipeline.run_translation()

    elif args.command == "finetune":
        finetuning_pipeline = FineTuningPipeline(**pipeline_args)
        finetuning_pipeline.run_fine_tuning()

    elif args.command == "adapt":
        adaptation_pipeline = AdaptationPipeline(**pipeline_args)
        adaptation_pipeline.run_adaptation()


if __name__ == "__main__":
    main()
