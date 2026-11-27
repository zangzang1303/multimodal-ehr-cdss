"""Phase 3 research experiments (Member 1, Backlogs 08-09). Pre-registered in
docs/11_ANALYSIS_PLAN.md, Appendix A (frozen hash in results/preregistration/).

Sub-commands (each writes per-model, per-seed prediction files under data/predictions/):
  rq1       fair model comparison + missing-modality scenarios + deployment checkpoint
  rq2       text-signal decomposition over note variants
  rq3       controlled complementarity simulation (writes results/rq3_simulation.json)
  temporal  group-aware temporal split (internal robustness)

Statistics, calibration comparison, DCA, fairness and the results registry are computed
afterwards from the saved predictions by scripts/build_results_registry.py.
"""

from __future__ import annotations

import argparse
import copy
import json
import random
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from torch import nn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data_pipeline.manifest import verify_manifest  # noqa: E402
from src.data_pipeline.note_variants import VARIANTS, add_tabular_noise, inject_cue  # noqa: E402
from src.models.baselines import CATEGORICAL_FEATURES, NUMERICAL_FEATURES, ClassicalTabularBaseline  # noqa: E402
from src.models.calibration import TemperatureScalingCalibrator  # noqa: E402
from src.models.checkpoint_io import save_checkpoint_safely  # noqa: E402
from src.models.text_tail import TailedModel, TextStates, encode_layer11, load_backbone  # noqa: E402

DATA_DIR = ROOT / "data" / "processed_rebuilt_strict"
CACHE_DIR = ROOT / "data" / "cache" / "text_states"
PRED_DIR = ROOT / "data" / "predictions"
RUN_CKPT_DIR = ROOT / "data" / "checkpoints" / "runs"
RESULTS_DIR = ROOT / "results"
SPLITS = ("train", "val", "test")
CLASSES = ("ASTHMA", "COPD", "HEART_FAILURE", "PNEUMONIA")
CATEGORY_VALUES = {
    "gender": ("M", "F", "OTHER"),
    "smoking_status": ("NEVER", "FORMER", "CURRENT"),
    "history_hypertension": ("0", "1"),
    "history_diabetes": ("0", "1"),
}
SEEDS_RQ1 = (13, 42, 101, 2024, 7)
SEEDS_RQ2 = (13, 42, 101)
SEEDS_RQ3 = (13, 42)
TAB_MISSING = (0.1, 0.3, 0.5)
MAX_LENGTH = 512
# (mode, trainable last BERT block)
NN_MODELS = {
    "ft_transformer": ("tabular", False),
    "bert_frozen": ("text", False),
    "bert_ft": ("text", True),
    "concat_frozen": ("concat", False),
    "xattn_frozen": ("cross_attention", False),
    "xattn_ft": ("cross_attention", True),
}


@dataclass
class TrainConfig:
    epochs: int = 12
    patience: int = 4
    batch_size: int = 32
    lr_head: float = 2e-4
    lr_tail: float = 2e-5
    weight_decay: float = 1e-5


# ----------------------------------------------------------------------------- data
def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def load_frames() -> dict[str, pd.DataFrame]:
    verify_manifest(DATA_DIR)
    frames = {s: pd.read_parquet(DATA_DIR / f"{s}.parquet") for s in SPLITS}
    return frames


def global_index(frames: dict[str, pd.DataFrame]) -> dict[str, np.ndarray]:
    sizes = [len(frames[s]) for s in SPLITS]
    starts = np.cumsum([0] + sizes)
    return {s: np.arange(starts[i], starts[i + 1]) for i, s in enumerate(SPLITS)}


def all_rows(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return pd.concat([frames[s] for s in SPLITS], ignore_index=True)


class TextCache:
    """Layer-11 states for every row of the canonical data, one file per note variant."""

    def __init__(self, device: torch.device) -> None:
        self.device = device
        self._backbone = None

    def backbone(self):
        if self._backbone is None:
            self._backbone = load_backbone(self.device)
        return self._backbone

    def get(self, key: str, notes: list[str]) -> TextStates:
        path = CACHE_DIR / f"{key}.pt"
        if path.is_file():
            states = TextStates.load(path)
            if len(states) == len(notes):
                return states
        tokenizer, backbone, revision = self.backbone()
        t0 = time.time()
        states = encode_layer11(notes, tokenizer, backbone, self.device, MAX_LENGTH, revision=revision)
        states.save(path)
        print(f"  encoded {key}: {len(notes)} notes in {time.time() - t0:.0f}s", flush=True)
        return states

    def empty_note(self, n: int) -> TextStates:
        single = self.get("empty_note", [""])
        flat = single.flat.repeat(n, 1)
        length = len(single.flat)
        return TextStates(flat, torch.arange(n + 1) * length, single.revision)

    def release(self) -> None:
        self._backbone = None
        torch.cuda.empty_cache()


class TabularPrep:
    """Train-fitted preprocessing shared by every model (raw values -> tensors)."""

    def __init__(self, train: pd.DataFrame) -> None:
        self.median = train[NUMERICAL_FEATURES].median()
        self.mode = {c: train[c].astype(str).mode().iloc[0] for c in CATEGORICAL_FEATURES}
        self.scaler = StandardScaler().fit(train[NUMERICAL_FEATURES].to_numpy(np.float32))
        self.sd = train[NUMERICAL_FEATURES].std().to_numpy()

    def tensors(self, frame: pd.DataFrame) -> tuple[torch.Tensor, torch.Tensor]:
        num = self.scaler.transform(frame[NUMERICAL_FEATURES].to_numpy(np.float32)).astype(np.float32)
        cat = np.zeros((len(frame), len(CATEGORICAL_FEATURES)), dtype=np.int64)
        for j, col in enumerate(CATEGORICAL_FEATURES):
            mapping = {v: i + 1 for i, v in enumerate(CATEGORY_VALUES[col])}
            cat[:, j] = frame[col].astype(str).map(mapping).fillna(0).to_numpy(np.int64)
        return torch.from_numpy(num), torch.from_numpy(cat)

    def preprocessing_dict(self) -> dict:
        return {"numerical_features": list(NUMERICAL_FEATURES),
                "categorical_features": list(CATEGORICAL_FEATURES),
                "category_values": {k: list(v) for k, v in CATEGORY_VALUES.items()},
                "scaler_mean": self.scaler.mean_.tolist(), "scaler_scale": self.scaler.scale_.tolist()}

    # --- missing-modality scenarios (analysis plan section 4) ---
    def no_tabular(self, frame: pd.DataFrame) -> pd.DataFrame:
        out = frame.copy()
        for col in NUMERICAL_FEATURES:
            out[col] = self.median[col]
        for col in CATEGORICAL_FEATURES:
            out[col] = self.mode[col]
        return out

    def random_missing(self, frame: pd.DataFrame, fraction: float, seed: int = 2026) -> pd.DataFrame:
        out = frame.copy()
        rng = np.random.default_rng(seed)
        k = int(round(fraction * len(NUMERICAL_FEATURES)))
        values = out[NUMERICAL_FEATURES].to_numpy(dtype=float, copy=True)
        for row in range(len(out)):
            drop = rng.choice(len(NUMERICAL_FEATURES), size=k, replace=False)
            values[row, drop] = self.median.to_numpy()[drop]
        out[NUMERICAL_FEATURES] = values
        return out


def scenarios(prep: TabularPrep, test: pd.DataFrame) -> dict[str, pd.DataFrame]:
    out = {"full": test, "no_tabular": prep.no_tabular(test), "no_text": test}
    for p in TAB_MISSING:
        out[f"tab_missing_{int(p * 100)}"] = prep.random_missing(test, p)
    return out


# ------------------------------------------------------------------- calibration utils
def to_logits(probs: np.ndarray) -> np.ndarray:
    return np.log(np.clip(probs, 1e-7, 1.0))


def fit_temperature(val_logits: np.ndarray, y_val: np.ndarray) -> float:
    cal = TemperatureScalingCalibrator().fit(torch.tensor(val_logits, dtype=torch.float32),
                                            torch.tensor(y_val, dtype=torch.long))
    return float(cal.temperature)


def softmax_t(logits: np.ndarray, t: float) -> np.ndarray:
    z = logits / t
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def save_prediction(path: Path, *, model: str, seed: int, frames, val_logits, test_logits,
                    scenario_logits: dict[str, np.ndarray] | None = None, extra: dict | None = None) -> dict:
    y_val = frames["val"].diagnosis_label.to_numpy()
    y_test = frames["test"].diagnosis_label.to_numpy()
    t = fit_temperature(val_logits, y_val)
    val_nll = float(log_loss(y_val, softmax_t(val_logits, 1.0), labels=list(range(4))))
    payload = {"model": model, "seed": seed, "temperature": t, "val_nll": val_nll,
               "y_val": y_val, "y_test": y_test,
               "patient_id_val": frames["val"].patient_id.to_numpy().astype(str),
               "patient_id_test": frames["test"].patient_id.to_numpy().astype(str),
               "val_logits": val_logits.astype(np.float32), "test_logits": test_logits.astype(np.float32)}
    for name, logits in (scenario_logits or {}).items():
        payload[f"test_logits__{name}"] = logits.astype(np.float32)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **payload, meta=json.dumps(extra or {}))
    auroc = roc_auc_score(y_test, softmax_t(test_logits, t), multi_class="ovr")
    print(f"    {model:<16} seed={seed:<5} T={t:.3f} valNLL={val_nll:.4f} testAUROC={auroc:.4f}", flush=True)
    return {"temperature": t, "val_nll": val_nll, "test_auroc": float(auroc)}


# ---------------------------------------------------------------------- sklearn models
def fit_lr_tabular(frames, prep: TabularPrep, eval_frames: dict[str, pd.DataFrame]):
    enc = OneHotEncoder(handle_unknown="ignore").fit(frames["train"][CATEGORICAL_FEATURES].astype(str))

    def features(frame):
        num = prep.scaler.transform(frame[NUMERICAL_FEATURES].to_numpy(np.float32))
        return np.hstack([num, enc.transform(frame[CATEGORICAL_FEATURES].astype(str)).toarray()])

    best = None
    for c in (0.25, 1.0, 4.0, 16.0):  # C selected on validation NLL
        model = LogisticRegression(C=c, max_iter=5000).fit(features(frames["train"]), frames["train"].diagnosis_label)
        nll = log_loss(frames["val"].diagnosis_label, model.predict_proba(features(frames["val"])), labels=list(range(4)))
        if best is None or nll < best[0]:
            best = (nll, c, model)
    _, c, model = best
    return {name: to_logits(model.predict_proba(features(f))) for name, f in eval_frames.items()}, {"C": c}


def fit_tfidf_lr(train_notes, y_train, val_notes, y_val, eval_notes: dict[str, list[str]]):
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    x_train = vec.fit_transform(train_notes)
    x_val = vec.transform(val_notes)
    best = None
    for c in (0.25, 1.0, 4.0, 16.0):
        model = LogisticRegression(C=c, max_iter=5000).fit(x_train, y_train)
        nll = log_loss(y_val, model.predict_proba(x_val), labels=list(range(4)))
        if best is None or nll < best[0]:
            best = (nll, c, model)
    _, c, model = best
    return {name: to_logits(model.predict_proba(vec.transform(n))) for name, n in eval_notes.items()}, {"C": c}


def fit_catboost(frames, seed: int, eval_frames: dict[str, pd.DataFrame]):
    model = ClassicalTabularBaseline(estimator="catboost", random_state=seed)
    model.fit(frames["train"], frames["train"].diagnosis_label)
    return {name: to_logits(model.predict_proba(f)) for name, f in eval_frames.items()}, model


# ------------------------------------------------------------------------ torch models
class Batches:
    """Index-based mini-batches over (tabular tensors, global text indices, labels)."""

    def __init__(self, num, cat, text_idx, labels, states: TextStates, uses_text: bool):
        self.num, self.cat, self.text_idx, self.labels = num, cat, text_idx, labels
        self.states, self.uses_text = states, uses_text

    def __len__(self):
        return len(self.labels)

    def iterate(self, batch_size: int, generator: torch.Generator | None = None):
        order = torch.randperm(len(self), generator=generator) if generator is not None else torch.arange(len(self))
        for start in range(0, len(self), batch_size):
            idx = order[start:start + batch_size]
            if self.uses_text:
                hidden, mask = self.states.batch(self.text_idx[idx.numpy()].tolist())
            else:
                hidden, mask = torch.zeros(len(idx), 1, 768, dtype=torch.float16), torch.ones(len(idx), 1, dtype=torch.long)
            yield self.num[idx], self.cat[idx], hidden, mask, self.labels[idx]


def predict_torch(model: nn.Module, batches: Batches, device, batch_size: int = 64) -> np.ndarray:
    model.eval()
    out = []
    with torch.inference_mode(), torch.autocast("cuda", dtype=torch.float16, enabled=device.type == "cuda"):
        for num, cat, hidden, mask, _ in batches.iterate(batch_size):
            out.append(model(num.to(device), cat.to(device), hidden.to(device), mask.to(device)).float().cpu())
    return torch.cat(out).numpy()


def train_torch(mode: str, trainable_tail: bool, data: dict[str, Batches], backbone, seed: int,
                device, cfg: TrainConfig) -> tuple[nn.Module, dict]:
    set_seed(seed)
    model = TailedModel(mode, backbone, trainable_tail).to(device)
    head_params = [p for n, p in model.named_parameters() if not n.startswith("tail.") and p.requires_grad]
    groups = [{"params": head_params, "lr": cfg.lr_head}]
    if trainable_tail:
        groups.append({"params": [p for p in model.tail.parameters()], "lr": cfg.lr_tail})
    optimizer = torch.optim.AdamW(groups, weight_decay=cfg.weight_decay)
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    gen = torch.Generator().manual_seed(seed)
    best = (float("inf"), None, 0)
    stale, epoch = 0, 0
    y_val = data["val"].labels.numpy()
    for epoch in range(1, cfg.epochs + 1):
        model.train()
        for num, cat, hidden, mask, target in data["train"].iterate(cfg.batch_size, gen):
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast("cuda", dtype=torch.float16, enabled=device.type == "cuda"):
                logits = model(num.to(device), cat.to(device), hidden.to(device), mask.to(device))
                loss = nn.functional.cross_entropy(logits.float(), target.to(device))
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(optimizer)
            scaler.update()
        val_logits = predict_torch(model, data["val"], device)
        val_nll = float(log_loss(y_val, softmax_t(val_logits, 1.0), labels=list(range(4))))
        if val_nll < best[0] - 1e-5:
            best = (val_nll, copy.deepcopy({k: v.detach().cpu() for k, v in model.state_dict().items()}), epoch)
            stale = 0
        else:
            stale += 1
            if stale >= cfg.patience:
                break
    model.load_state_dict(best[1])
    return model, {"selected_epoch": best[2], "epochs_run": epoch, "val_nll_early_stop": best[0]}


def make_batches(prep: TabularPrep, frame: pd.DataFrame, text_idx: np.ndarray, states: TextStates,
                 uses_text: bool) -> Batches:
    num, cat = prep.tensors(frame)
    labels = torch.tensor(frame.diagnosis_label.to_numpy(np.int64))
    return Batches(num, cat, np.asarray(text_idx), labels, states, uses_text)


# ------------------------------------------------------------------------------- RQ1
def run_rq1(args, device) -> None:
    frames = load_frames()
    gidx = global_index(frames)
    rows = all_rows(frames)
    prep = TabularPrep(frames["train"])
    cache = TextCache(device)
    states = cache.get("full", rows.clinical_note.astype(str).tolist())
    empty = cache.empty_note(len(frames["test"]))
    tokenizer, backbone, revision = cache.backbone()
    scen = scenarios(prep, frames["test"])
    out_dir = PRED_DIR / "rq1"
    summary: dict = {}

    # deterministic sklearn models (run once)
    evals = {"val": frames["val"], **{f"test__{k}": v for k, v in scen.items()}}
    logits, info = fit_lr_tabular(frames, prep, evals)
    summary["lr_tabular"] = {0: save_prediction(out_dir / "lr_tabular_seed0.npz", model="lr_tabular", seed=0,
                                                frames=frames, val_logits=logits["val"],
                                                test_logits=logits["test__full"],
                                                scenario_logits={k: logits[f"test__{k}"] for k in scen if k != "full"},
                                                extra=info)}
    notes = {s: frames[s].clinical_note.astype(str).tolist() for s in SPLITS}
    logits, info = fit_tfidf_lr(notes["train"], frames["train"].diagnosis_label, notes["val"],
                                frames["val"].diagnosis_label,
                                {"val": notes["val"], "test": notes["test"], "no_text": [""] * len(notes["test"])})
    summary["tfidf_lr"] = {0: save_prediction(out_dir / "tfidf_lr_seed0.npz", model="tfidf_lr", seed=0, frames=frames,
                                              val_logits=logits["val"], test_logits=logits["test"],
                                              scenario_logits={"no_text": logits["no_text"]}, extra=info)}

    cfg = TrainConfig()
    for seed in args.seeds:
        print(f"[RQ1] seed {seed}", flush=True)
        logits, cb_model = fit_catboost(frames, seed, evals)
        summary.setdefault("catboost", {})[seed] = save_prediction(
            out_dir / f"catboost_seed{seed}.npz", model="catboost", seed=seed, frames=frames,
            val_logits=logits["val"], test_logits=logits["test__full"],
            scenario_logits={k: logits[f"test__{k}"] for k in scen if k != "full"})
        if seed == 42:
            import joblib
            RUN_CKPT_DIR.mkdir(parents=True, exist_ok=True)
            joblib.dump(cb_model, RUN_CKPT_DIR / "catboost_seed42.joblib")
        for name, (mode, trainable) in NN_MODELS.items():
            if args.models and name not in args.models:
                continue
            uses_text = mode != "tabular"
            data = {s: make_batches(prep, frames[s], gidx[s], states, uses_text) for s in ("train", "val")}
            t0 = time.time()
            model, train_info = train_torch(mode, trainable, data, backbone, seed, device, cfg)
            val_logits = predict_torch(model, data["val"], device)
            scen_logits = {}
            for key, frame in scen.items():
                text_states, text_idx = (empty, np.arange(len(frame))) if key == "no_text" else (states, gidx["test"])
                scen_logits[key] = predict_torch(model, make_batches(prep, frame, text_idx, text_states, uses_text), device)
            test_logits = scen_logits.pop("full")
            train_info["train_seconds"] = round(time.time() - t0, 1)
            summary.setdefault(name, {})[seed] = {**save_prediction(
                out_dir / f"{name}_seed{seed}.npz", model=name, seed=seed, frames=frames, val_logits=val_logits,
                test_logits=test_logits, scenario_logits=scen_logits, extra=train_info), **train_info}
            if name == "xattn_frozen":
                RUN_CKPT_DIR.mkdir(parents=True, exist_ok=True)
                torch.save({"model_state": model.head_model.state_dict(), "seed": seed,
                            "temperature": summary[name][seed]["temperature"],
                            "val_nll": summary[name][seed]["val_nll"], "train_info": train_info},
                           RUN_CKPT_DIR / f"xattn_frozen_seed{seed}.pt")
            if name in ("ft_transformer", "bert_ft") and seed == 42:
                torch.save({"state": model.state_dict(), "mode": mode, "trainable_tail": trainable,
                            "temperature": summary[name][seed]["temperature"]}, RUN_CKPT_DIR / f"{name}_seed42.pt")
            del model
            torch.cuda.empty_cache()
    if not args.models:
        save_deployment_checkpoint(summary, prep, revision)
    (RESULTS_DIR / "raw").mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "raw" / "rq1_training_summary.json").write_text(
        json.dumps(summary, indent=2, default=str), encoding="utf-8")


def save_deployment_checkpoint(summary: dict, prep: TabularPrep, revision: str | None) -> None:
    runs = summary["xattn_frozen"]
    best_seed = min(runs, key=lambda s: runs[s]["val_nll"])
    run = torch.load(RUN_CKPT_DIR / f"xattn_frozen_seed{best_seed}.pt", map_location="cpu", weights_only=False)
    payload = {
        "model_state": run["model_state"], "model_mode": "cross_attention",
        "model_config": {"text_width": 768, "d_token": 128, "num_classes": 4, "n_blocks": 4, "n_heads": 4},
        "text_model": "emilyalsentzer/Bio_ClinicalBERT", "text_backbone_frozen": True,
        "max_length": MAX_LENGTH, "temperature": float(run["temperature"]), "classes": CLASSES,
        "preprocessing": prep.preprocessing_dict(), "source_split": "data/processed_rebuilt_strict",
        "seed": int(best_seed),
        "provenance": {"backbone_revision": revision, "selection_rule": "lowest validation NLL over seeds "
                       + ",".join(map(str, sorted(runs))), "analysis_plan": "docs/11_ANALYSIS_PLAN.md#A.1"},
        "training_metadata": {"trained_at": datetime.now(timezone.utc).isoformat(),
                              "best_epoch": int(run["train_info"]["selected_epoch"]),
                              "epochs_total": int(run["train_info"]["epochs_run"]),
                              "best_val_loss": float(run["train_info"]["val_nll_early_stop"])},
    }
    path = save_checkpoint_safely(payload, ROOT / "data" / "checkpoints" / "multimodal_best.pt",
                                  epochs_trained=payload["training_metadata"]["epochs_total"])
    print(f"[RQ1] deployment checkpoint (seed {best_seed}) -> {path}", flush=True)


# ------------------------------------------------------------------------------- RQ2
def run_rq2(args, device) -> None:
    frames = load_frames()
    gidx = global_index(frames)
    rows = all_rows(frames)
    prep = TabularPrep(frames["train"])
    cache = TextCache(device)
    cfg = TrainConfig()
    for variant, transform in VARIANTS.items():
        if args.variants and variant not in args.variants:
            continue
        print(f"[RQ2] variant {variant}", flush=True)
        notes_all = rows.clinical_note.astype(str).map(transform).tolist()
        states = cache.get(variant, notes_all)
        _, backbone, _ = cache.backbone()
        out_dir = PRED_DIR / "rq2" / variant
        notes = {s: [notes_all[i] for i in gidx[s]] for s in SPLITS}
        logits, info = fit_tfidf_lr(notes["train"], frames["train"].diagnosis_label, notes["val"],
                                    frames["val"].diagnosis_label, {"val": notes["val"], "test": notes["test"]})
        save_prediction(out_dir / "tfidf_lr_seed0.npz", model="tfidf_lr", seed=0, frames=frames,
                        val_logits=logits["val"], test_logits=logits["test"], extra=info)
        for seed in args.seeds:
            for name in ("bert_frozen", "bert_ft", "xattn_frozen"):
                mode, trainable = NN_MODELS[name]
                data = {s: make_batches(prep, frames[s], gidx[s], states, True) for s in SPLITS}
                model, info = train_torch(mode, trainable, data, backbone, seed, device, cfg)
                save_prediction(out_dir / f"{name}_seed{seed}.npz", model=name, seed=seed, frames=frames,
                                val_logits=predict_torch(model, data["val"], device),
                                test_logits=predict_torch(model, data["test"], device), extra=info)
                del model
                torch.cuda.empty_cache()
        del states


# ------------------------------------------------------------------------------- RQ3
def run_rq3(args, device) -> None:
    frames = load_frames()
    gidx = global_index(frames)
    rows = all_rows(frames)
    cache = TextCache(device)
    cfg = TrainConfig()
    base = rows.clinical_note.astype(str).map(VARIANTS["num_masked"])
    results = []
    out_path = RESULTS_DIR / "rq3_simulation.json"
    done = {(r["rho"], r["sigma"], r["model"], r["seed"]) for r in
            (json.loads(out_path.read_text(encoding="utf-8"))["runs"] if out_path.is_file() else [])}
    if out_path.is_file():
        results = json.loads(out_path.read_text(encoding="utf-8"))["runs"]
    for rho in args.rhos:
        notes = [inject_cue(n, int(lbl), str(pid), rho) for n, lbl, pid in
                 zip(base, rows.diagnosis_label, rows.patient_id)]
        states = cache.get(f"rq3_rho{int(rho * 100)}", notes)
        _, backbone, _ = cache.backbone()
        for sigma in args.sigmas:
            noisy = {}
            train_sd = frames["train"][NUMERICAL_FEATURES].std().to_numpy()
            for i, s in enumerate(SPLITS):
                f = frames[s].copy()
                f[NUMERICAL_FEATURES] = add_tabular_noise(f[NUMERICAL_FEATURES].to_numpy(float), train_sd, sigma,
                                                          seed=1000 + i)
                noisy[s] = f
            prep = TabularPrep(noisy["train"])
            for seed in args.seeds:
                for mode in ("tabular", "text", "concat", "cross_attention"):
                    # tabular ignores rho, text ignores sigma: train each only once per grid axis
                    if mode == "tabular" and rho != args.rhos[0]:
                        continue
                    if mode == "text" and sigma != args.sigmas[0]:
                        continue
                    key = (rho, sigma, mode, seed)
                    if key in done:
                        continue
                    data = {s: make_batches(prep, noisy[s], gidx[s], states, mode != "tabular") for s in SPLITS}
                    model, info = train_torch(mode, False, data, backbone, seed, device, cfg)
                    val_logits = predict_torch(model, data["val"], device)
                    t = fit_temperature(val_logits, frames["val"].diagnosis_label.to_numpy())
                    test_probs = softmax_t(predict_torch(model, data["test"], device), t)
                    auroc = float(roc_auc_score(frames["test"].diagnosis_label, test_probs, multi_class="ovr"))
                    results.append({"rho": rho, "sigma": sigma, "model": mode, "seed": seed,
                                    "test_macro_auroc": auroc, "temperature": t, **info})
                    print(f"  [RQ3] rho={rho} sigma={sigma} {mode:<16} seed={seed} AUROC={auroc:.4f}", flush=True)
                    out_path.write_text(json.dumps({"description": "Controlled complementarity simulation "
                                                    "(docs/11_ANALYSIS_PLAN.md A.3). SIMULATION - not clinical "
                                                    "performance.", "runs": results}, indent=2), encoding="utf-8")
                    del model
                    torch.cuda.empty_cache()
        del states


# -------------------------------------------------------------------------- temporal
def temporal_split(rows: pd.DataFrame) -> dict[str, np.ndarray]:
    """Group-aware 70/15/15 split ordered by the earliest encounter of each source group."""
    parent = list(range(len(rows)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for col in ("source_patient_group", "source_note_group"):
        first: dict[str, int] = {}
        for i, value in enumerate(rows[col].astype(str)):
            if value in first:
                a, b = find(i), find(first[value])
                if a != b:
                    parent[b] = a
            else:
                first[value] = i
    groups = np.array([find(i) for i in range(len(rows))])
    ts = pd.to_datetime(rows.encounter_timestamp)
    group_time = pd.Series(ts.values).groupby(groups).min().sort_values()
    cum = rows.groupby(groups).size().loc[group_time.index].cumsum() / len(rows)
    train_g = set(cum[cum <= 0.70].index)
    val_g = set(cum[(cum > 0.70) & (cum <= 0.85)].index)
    return {"train": np.where(np.isin(groups, list(train_g)))[0],
            "val": np.where(np.isin(groups, list(val_g)))[0],
            "test": np.where(~np.isin(groups, list(train_g | val_g)))[0]}


def run_temporal(args, device) -> None:
    frames0 = load_frames()
    rows = all_rows(frames0)
    split = temporal_split(rows)
    frames = {s: rows.iloc[idx].reset_index(drop=True) for s, idx in split.items()}
    ts = pd.to_datetime(rows.encounter_timestamp)
    meta = {s: {"n": int(len(idx)), "from": str(ts.iloc[idx].min()), "to": str(ts.iloc[idx].max()),
                "class_counts": rows.iloc[idx].diagnosis_label.value_counts().sort_index().to_dict()}
            for s, idx in split.items()}
    print("[temporal]", json.dumps(meta, default=str), flush=True)
    prep = TabularPrep(frames["train"])
    cache = TextCache(device)
    states = cache.get("full", rows.clinical_note.astype(str).tolist())
    _, backbone, _ = cache.backbone()
    out_dir = PRED_DIR / "temporal"
    seed = 42
    logits, _ = fit_catboost(frames, seed, {"val": frames["val"], "test": frames["test"]})
    save_prediction(out_dir / "catboost_seed42.npz", model="catboost", seed=seed, frames=frames,
                    val_logits=logits["val"], test_logits=logits["test"], extra=meta)
    notes = {s: frames[s].clinical_note.astype(str).tolist() for s in SPLITS}
    logits, _ = fit_tfidf_lr(notes["train"], frames["train"].diagnosis_label, notes["val"],
                             frames["val"].diagnosis_label, {"val": notes["val"], "test": notes["test"]})
    save_prediction(out_dir / "tfidf_lr_seed0.npz", model="tfidf_lr", seed=0, frames=frames,
                    val_logits=logits["val"], test_logits=logits["test"], extra=meta)
    for name in ("bert_frozen", "xattn_frozen"):
        mode, trainable = NN_MODELS[name]
        data = {s: make_batches(prep, frames[s], split[s], states, True) for s in SPLITS}
        model, info = train_torch(mode, trainable, data, backbone, seed, device, TrainConfig())
        save_prediction(out_dir / f"{name}_seed{seed}.npz", model=name, seed=seed, frames=frames,
                        val_logits=predict_torch(model, data["val"], device),
                        test_logits=predict_torch(model, data["test"], device), extra={**meta, **info})



# ------------------------------------------------------------------- post-hoc CV (A.6)
def source_groups(rows: pd.DataFrame) -> np.ndarray:
    parent = list(range(len(rows)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for col in ("source_patient_group", "source_note_group"):
        first: dict[str, int] = {}
        for i, value in enumerate(rows[col].astype(str)):
            if value in first:
                a, b = find(i), find(first[value])
                if a != b:
                    parent[b] = a
            else:
                first[value] = i
    return np.array([find(i) for i in range(len(rows))])


def run_cv(args, device) -> None:
    from sklearn.model_selection import StratifiedGroupKFold

    frames0 = load_frames()
    rows = all_rows(frames0)
    groups = source_groups(rows)
    y_all = rows.diagnosis_label.to_numpy()
    cache = TextCache(device)
    states = cache.get("full", rows.clinical_note.astype(str).tolist())
    _, backbone, _ = cache.backbone()
    outer = StratifiedGroupKFold(5, shuffle=True, random_state=42)
    seed = 42
    for fold, (trval, test) in enumerate(outer.split(rows, y_all, groups)):
        inner = StratifiedGroupKFold(7, shuffle=True, random_state=42)  # ~15% of the remainder
        tr_rel, va_rel = next(inner.split(trval, y_all[trval], groups[trval]))
        split = {"train": trval[tr_rel], "val": trval[va_rel], "test": test}
        frames = {s: rows.iloc[idx].reset_index(drop=True) for s, idx in split.items()}
        meta = {"fold": fold, **{s: int(len(idx)) for s, idx in split.items()}}
        print(f"[CV] fold {fold}: {meta}", flush=True)
        out_dir = PRED_DIR / "cv" / f"fold{fold}"
        prep = TabularPrep(frames["train"])
        logits, _ = fit_lr_tabular(frames, prep, {"val": frames["val"], "test": frames["test"]})
        save_prediction(out_dir / "lr_tabular_seed0.npz", model="lr_tabular", seed=0, frames=frames,
                        val_logits=logits["val"], test_logits=logits["test"], extra=meta)
        logits, _ = fit_catboost(frames, seed, {"val": frames["val"], "test": frames["test"]})
        save_prediction(out_dir / "catboost_seed42.npz", model="catboost", seed=seed, frames=frames,
                        val_logits=logits["val"], test_logits=logits["test"], extra=meta)
        notes = {s: frames[s].clinical_note.astype(str).tolist() for s in SPLITS}
        logits, _ = fit_tfidf_lr(notes["train"], frames["train"].diagnosis_label, notes["val"],
                                 frames["val"].diagnosis_label, {"val": notes["val"], "test": notes["test"]})
        save_prediction(out_dir / "tfidf_lr_seed0.npz", model="tfidf_lr", seed=0, frames=frames,
                        val_logits=logits["val"], test_logits=logits["test"], extra=meta)
        for name in ("bert_frozen", "bert_ft", "xattn_frozen"):
            mode, trainable = NN_MODELS[name]
            data = {s: make_batches(prep, frames[s], split[s], states, True) for s in SPLITS}
            model, info = train_torch(mode, trainable, data, backbone, seed, device, TrainConfig())
            save_prediction(out_dir / f"{name}_seed{seed}.npz", model=name, seed=seed, frames=frames,
                            val_logits=predict_torch(model, data["val"], device),
                            test_logits=predict_torch(model, data["test"], device), extra={**meta, **info})
            del model
            torch.cuda.empty_cache()

# ------------------------------------------------------------------------------ main
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("rq1", "rq2", "rq3", "temporal", "cv"))
    parser.add_argument("--seeds", type=int, nargs="+")
    parser.add_argument("--models", nargs="+", help="RQ1: restrict to these NN models (no deployment checkpoint)")
    parser.add_argument("--variants", nargs="+", choices=tuple(VARIANTS))
    parser.add_argument("--rhos", type=float, nargs="+", default=[0.0, 0.25, 0.5, 0.75, 1.0])
    parser.add_argument("--sigmas", type=float, nargs="+", default=[0.0, 0.5, 1.0])
    args = parser.parse_args()
    defaults = {"rq1": SEEDS_RQ1, "rq2": SEEDS_RQ2, "rq3": SEEDS_RQ3, "temporal": (42,), "cv": (42,)}
    args.seeds = tuple(args.seeds or defaults[args.command])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.backends.cudnn.benchmark = False
    print(f"[{args.command}] device={device} seeds={args.seeds}", flush=True)
    {"rq1": run_rq1, "rq2": run_rq2, "rq3": run_rq3, "temporal": run_temporal, "cv": run_cv}[args.command](args, device)


if __name__ == "__main__":
    main()
