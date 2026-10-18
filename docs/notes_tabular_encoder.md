# Phase 1 encoder and tokenizer notes

The Phase 1 tabular baseline uses the FT-Transformer feature tokenizer described by
[Gorishniy et al.](https://arxiv.org/abs/2106.11959). Each numerical feature gets
its own learned affine projection, `x_j * w_j + b_j`, into a 128-dimensional token.
Each categorical feature gets a learned embedding. The resulting feature tokens and
a classification token pass through four Transformer blocks with four attention
heads. Pooling the classification token gives four diagnosis logits. The settings
in [`configs/model_config.yaml`](../configs/model_config.yaml) are the team's
starting experiment settings, not a claim that these values are optimal.

The text baseline uses the tokenizer from
[`emilyalsentzer/Bio_ClinicalBERT`](https://huggingface.co/emilyalsentzer/Bio_ClinicalBERT).
Run `python scripts/check_clinical_tokenizer.py` once with Hugging Face access to
populate the local cache. The configured maximum sequence length is 512 tokens;
week 2/3 training code must truncate or segment longer notes consistently.

The model card describes English MIMIC-III training notes, while our synthetic
notes are Vietnamese. Tokenizer loading alone does not establish useful Vietnamese
clinical performance. Benchmark the text baseline on this dataset before relying
on its predictions. The raw notes also include synthetic identifiers and future
information; de-identification and temporal filtering belong before training.
