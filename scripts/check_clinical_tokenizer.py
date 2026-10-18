"""Download and smoke-test the tokenizer configured for the text baseline."""

from pathlib import Path

import yaml
from transformers import AutoTokenizer


def main() -> None:
    config_path = Path(__file__).resolve().parents[1] / "configs" / "model_config.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    model_name = config["clinical_bert"]["pretrained_model_name"]
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokens = tokenizer("Patient has cough and shortness of breath.")
    if not tokens["input_ids"]:
        raise RuntimeError("Tokenizer returned no token IDs")
    print(f"Tokenizer loaded successfully: {model_name}, vocab size: {tokenizer.vocab_size}")


if __name__ == "__main__":
    main()
