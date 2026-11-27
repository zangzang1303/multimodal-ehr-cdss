"""Build results/registry.json - the single source of truth for every number in the
paper, slides and UI (Phase 3, Backlog 08 M1-1.4 and Backlog 09).

Reads only saved per-patient predictions (data/predictions/**.npz), the RQ3 simulation
log and the Member 3 RAG/latency reports. Never trains a model. Re-running it on the
same inputs reproduces the registry exactly.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import confusion_matrix, f1_score, log_loss  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data_pipeline.manifest import verify_manifest  # noqa: E402
from src.evaluation.metrics import compute_multiclass_metrics, expected_calibration_error  # noqa: E402
from src.evaluation.stats import (  # noqa: E402
    bootstrap_ci, bootstrap_indices, classwise_ece, decision_curve, ece_equal_mass, fit_isotonic_ovr,
    fit_vector_scaling, holm, macro_auroc, net_benefit, net_benefit_treat_all, net_reduction_in_interventions,
    paired_bootstrap, softmax,
)

PRED = ROOT / "data" / "predictions"
RESULTS = ROOT / "results"
FIG_DIR = ROOT / "docs" / "paper_latex" / "figures" / "generated"
PLOT_DIR = ROOT / "data" / "evaluation_plots"
DATA_DIR = ROOT / "data" / "processed_rebuilt_strict"
N_BOOT = 2000
BOOT_SEED = 2026
CLASSES = ("ASTHMA", "COPD", "HEART_FAILURE", "PNEUMONIA")
DEPLOY = "xattn_frozen"
HF = 2
LABELS = {
    "lr_tabular": "Logistic Regression (bảng)", "catboost": "CatBoost (bảng)",
    "ft_transformer": "FT-Transformer (bảng)", "tfidf_lr": "TF-IDF + LR (văn bản)",
    "bert_frozen": "Bio_ClinicalBERT đóng băng (văn bản)", "bert_ft": "Bio_ClinicalBERT fine-tune (văn bản)",
    "concat_frozen": "Concat fusion (đóng băng)", "xattn_frozen": "Cross-attention (đóng băng) – triển khai",
    "xattn_ft": "Cross-attention (fine-tune)", "ensemble_cb_bertft": "Ensemble CatBoost + BERT-FT",
}
MODALITY = {"lr_tabular": "tabular", "catboost": "tabular", "ft_transformer": "tabular", "tfidf_lr": "text",
            "bert_frozen": "text", "bert_ft": "text", "concat_frozen": "fusion", "xattn_frozen": "fusion",
            "xattn_ft": "fusion", "ensemble_cb_bertft": "fusion"}
RQ1_ORDER = list(LABELS)


# ---------------------------------------------------------------------------- loading
class Run:
    def __init__(self, path: Path):
        z = np.load(path, allow_pickle=False)
        self.model, self.seed = str(z["model"]), int(z["seed"])
        self.t, self.val_nll = float(z["temperature"]), float(z["val_nll"])
        self.y_val, self.y_test = z["y_val"], z["y_test"]
        self.pid_test = z["patient_id_test"]
        self.val_logits, self.test_logits = z["val_logits"], z["test_logits"]
        self.scen = {k.split("__", 1)[1]: z[k] for k in z.files if k.startswith("test_logits__")}
        self.meta = json.loads(str(z["meta"]))

    def probs(self, split: str = "test", scenario: str | None = None, calibrated: bool = True) -> np.ndarray:
        logits = self.val_logits if split == "val" else (self.test_logits if scenario in (None, "full")
                                                         else self.scen[scenario])
        return softmax(logits / (self.t if calibrated else 1.0))


class Ensemble:
    """Probability average of two calibrated runs with the same seed."""

    def __init__(self, a: Run, b: Run, name: str):
        self.model, self.seed, self.a, self.b = name, a.seed, a, b
        self.y_val, self.y_test, self.pid_test = a.y_val, a.y_test, a.pid_test
        self.t = 1.0
        self.val_nll = float(log_loss(self.y_val, self.probs("val"), labels=list(range(4))))
        self.scen = {k: None for k in set(a.scen) | set(b.scen)}

    def probs(self, split="test", scenario=None, calibrated=True):
        def one(run):
            s = scenario if scenario in run.scen else None
            return run.probs(split, s, calibrated)
        return 0.5 * one(self.a) + 0.5 * one(self.b)


def load_runs(folder: Path) -> dict[str, dict[int, Run]]:
    runs: dict[str, dict[int, Run]] = defaultdict(dict)
    for path in sorted(folder.glob("*.npz")):
        run = Run(path)
        runs[run.model][run.seed] = run
    return dict(runs)


def representative(runs: dict[int, Run]):
    return min(runs.values(), key=lambda r: r.val_nll)


def r4(x):
    return None if x is None else round(float(x), 4)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# -------------------------------------------------------------------------------- RQ1
def build_rq1(runs, idx):
    if "catboost" in runs and "bert_ft" in runs:
        runs["ensemble_cb_bertft"] = {s: Ensemble(runs["catboost"][s], runs["bert_ft"][s], "ensemble_cb_bertft")
                                      for s in runs["catboost"] if s in runs["bert_ft"]}
    y = representative(runs[DEPLOY]).y_test
    rows, reps = [], {}
    for name in RQ1_ORDER:
        if name not in runs:
            continue
        per_seed = {s: compute_multiclass_metrics(r.y_test, r.probs()) for s, r in runs[name].items()}
        rep = representative(runs[name])
        reps[name] = rep
        ci = bootstrap_ci(y, rep.probs(), indices=idx)
        agg = {m: [v[m] for v in per_seed.values()] for m in ("macro_auroc", "macro_auprc", "macro_f1",
                                                               "accuracy", "brier_score", "ece")}
        rows.append({"model": name, "label": LABELS[name], "modality": MODALITY[name], "n_seeds": len(per_seed),
                     "seeds": sorted(per_seed), "representative_seed": rep.seed,
                     **{f"{m.replace('macro_', '')}_mean": r4(np.mean(v)) for m, v in agg.items()},
                     **{f"{m.replace('macro_', '')}_sd": r4(np.std(v, ddof=1)) if len(v) > 1 else 0.0
                        for m, v in agg.items()},
                     "auroc_rep_seed": r4(ci["estimate"]), "auroc_ci95": [r4(c) for c in ci["ci95"]],
                     "per_seed_auroc": {str(s): r4(v["macro_auroc"]) for s, v in per_seed.items()}})
    # paired comparisons: deployment model vs every other model (Holm over all comparisons)
    comps = []
    for name, rep in reps.items():
        if name == DEPLOY:
            continue
        pb = paired_bootstrap(y, reps[DEPLOY].probs(), rep.probs(), indices=idx)
        comps.append({"comparator": name, **{k: (r4(v) if not isinstance(v, list) else [r4(x) for x in v])
                                             for k, v in pb.items()}})
    for comp, adj in zip(comps, holm([c["p_value"] for c in comps])):
        comp["holm_adjusted_p"] = r4(adj)
    unimodal = [r for r in rows if r["modality"] in ("tabular", "text")]
    best_uni = max(unimodal, key=lambda r: r["auroc_mean"])
    by_comp = {c["comparator"]: c for c in comps}
    for row in rows:
        row["delta_auroc_vs_best_unimodal"] = r4(row["auroc_mean"] - best_uni["auroc_mean"])
        row["holm_adjusted_p"] = by_comp.get(row["model"], {}).get("holm_adjusted_p")
    return {"is_mock": False, "primary_metric": "macro AUROC (one-vs-rest), temperature-calibrated on validation",
            "test_n": int(len(y)), "best_unimodal_by_mean_auroc": best_uni["model"],
            "note": "Mean ± SD over seeds; CI95 = record-level bootstrap (B=2000; records share Synthea source "
                    "patients, so CIs understate uncertainty - see data_provenance) on the seed with lowest "
                    "validation NLL. Comparisons: deployment model (xattn_frozen) minus comparator, "
                    "Holm-adjusted over all comparators.",
            "models": rows, "comparisons_vs_deployment_model": comps}, reps


# -------------------------------------------------------------------------------- RQ2
VARIANT_LABEL = {"full": "Ghi chú gốc", "num_masked": "Che mọi con số", "no_vitals": "Bỏ sinh hiệu/xét nghiệm",
                 "narrative_only": "Chỉ phần tự sự"}


def build_rq2(rq1_rows, idx):
    out = []
    tab_ref = {r["model"]: r["auroc_mean"] for r in rq1_rows if r["modality"] == "tabular"}
    for variant in VARIANT_LABEL:
        folder = PRED / "rq2" / variant
        if not folder.is_dir():
            continue
        runs = load_runs(folder)
        entry = {"variant": variant, "label": VARIANT_LABEL[variant]}
        for name, runs_m in runs.items():
            aurocs = [macro_auroc(r.y_test, r.probs()) for r in runs_m.values()]
            rep = representative(runs_m)
            ci = bootstrap_ci(rep.y_test, rep.probs(), indices=idx)
            entry[name] = r4(np.mean(aurocs))
            entry[f"{name}_sd"] = r4(np.std(aurocs, ddof=1)) if len(aurocs) > 1 else 0.0
            entry[f"{name}_ci95"] = [r4(c) for c in ci["ci95"]]
        # frontend contract
        entry["clinical_bert"] = entry.get("bert_ft")
        entry["cross_attention"] = entry.get("xattn_frozen")
        out.append(entry)
    return {"is_mock": False, "tabular_only_reference_auroc": {k: r4(v) for k, v in tab_ref.items()},
            "note": "Mean macro AUROC over seeds 13/42/101 (TF-IDF deterministic). Variants defined in "
                    "src/data_pipeline/note_variants.py. Tabular-only models do not use notes; their AUROC is "
                    "the reference a fusion model can fall back to.", "variants": out}


# -------------------------------------------------------------------------------- RQ3
def build_rq3():
    path = RESULTS / "rq3_simulation.json"
    if not path.is_file():
        return None
    runs = pd.DataFrame(json.loads(path.read_text(encoding="utf-8"))["runs"])
    mean = runs.groupby(["model", "rho", "sigma"]).test_macro_auroc.mean()
    grid = []
    for rho in sorted(runs.rho.unique()):
        for sigma in sorted(runs.sigma.unique()):
            tab = mean.get(("tabular", runs.rho.min(), sigma))
            txt = mean.get(("text", rho, runs.sigma.min()))
            xat = mean.get(("cross_attention", rho, sigma))
            cat = mean.get(("concat", rho, sigma))
            if None in (tab, txt, xat):
                continue
            grid.append({"rho": rho, "sigma": sigma, "tabular": r4(tab), "text": r4(txt), "concat": r4(cat),
                         "cross_attention": r4(xat), "delta_xattn_vs_best_unimodal": r4(xat - max(tab, txt)),
                         "delta_concat_vs_best_unimodal": r4(cat - max(tab, txt)) if cat is not None else None})
    return {"is_mock": False, "simulation": True,
            "note": "SIMULATION (docs/11_ANALYSIS_PLAN.md A.3): class cues injected into number-masked notes for a "
                    "fraction rho of patients (10% wrong-class cues); Gaussian noise sigma*SD on tabular features. "
                    "Mean of seeds 13/42. Measures mechanism, not clinical performance.",
            "n_runs": int(len(runs)), "grid": grid}


# ---------------------------------------------------------------------- calibration
def build_calibration(rep, idx):
    y_val, y = rep.y_val, rep.y_test
    raw_val, raw_test = softmax(rep.val_logits), softmax(rep.test_logits)
    vector = fit_vector_scaling(rep.val_logits, y_val)
    iso = fit_isotonic_ovr(raw_val, y_val)
    methods = {"uncalibrated": raw_test, "temperature": rep.probs(), "vector_scaling": vector(rep.test_logits),
               "isotonic_ovr": iso(raw_test)}
    out = {}
    for name, p in methods.items():
        m = compute_multiclass_metrics(y, p)
        ci = bootstrap_ci(y, p, metric=lambda a, b: expected_calibration_error(a, b, 10), indices=idx)
        out[name] = {"ece_10_equal_width": r4(m["ece"]), "ece_ci95": [r4(c) for c in ci["ci95"]],
                     "ece_15_equal_mass": r4(ece_equal_mass(y, p)), "classwise_ece": r4(classwise_ece(y, p)),
                     "brier": r4(m["brier_score"]), "nll": r4(log_loss(y, p, labels=list(range(4)))),
                     "macro_auroc": r4(m["macro_auroc"]), "accuracy": r4(m["accuracy"])}
    plot_reliability(y, methods)
    return {"is_mock": False, "model": DEPLOY, "seed": rep.seed, "temperature": r4(rep.t),
            "target_ece": 0.05, "target_met_by": [k for k, v in out.items() if v["ece_10_equal_width"] < 0.05],
            "note": "All calibrators fitted on validation (N=273) only; metrics on strict test (N=302).",
            "methods": out}


# ------------------------------------------------------------------------ robustness
SCEN_LABEL = {"full": "Đầy đủ", "tab_missing_10": "Thiếu 10% biến số", "tab_missing_30": "Thiếu 30% biến số",
              "tab_missing_50": "Thiếu 50% biến số", "no_tabular": "Mất toàn bộ bảng", "no_text": "Mất văn bản"}


def build_robustness(runs):
    models = ["xattn_frozen", "xattn_ft", "concat_frozen", "catboost", "lr_tabular", "ft_transformer",
              "bert_ft", "bert_frozen", "tfidf_lr", "ensemble_cb_bertft"]
    table = {}
    for scen in SCEN_LABEL:
        table[scen] = {}
        for name in models:
            if name not in runs:
                continue
            vals = []
            for r in runs[name].values():
                if scen != "full" and scen not in r.scen:
                    continue
                vals.append(macro_auroc(r.y_test, r.probs(scenario=scen)))
            if vals:
                table[scen][name] = {"mean": r4(np.mean(vals)), "sd": r4(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0}
    scenarios = [{"scenario": s, "label": SCEN_LABEL[s],
                  "cross_attention_auroc": table[s].get("xattn_frozen", {}).get("mean"),
                  "tabular_only_auroc": table[s].get("catboost", {}).get("mean"),
                  "text_only_auroc": table[s].get("bert_ft", {}).get("mean")} for s in SCEN_LABEL]
    plot_missing_modality(table)
    return {"is_mock": False, "note": "Mean macro AUROC over seeds. Missing text = empty note string encoded by the "
            "same BERT; missing tabular = train median / mode; random missingness imputed with train median "
            "(analysis plan section 4). Models were trained on complete data (no modality dropout).",
            "scenarios": scenarios, "by_model": table}


# ------------------------------------------------------------------------------- DCA
def build_dca(reps, idx):
    thresholds = np.round(np.arange(0.05, 0.3001, 0.01), 2)
    y = reps[DEPLOY].y_test
    y_bin = (y == HF).astype(int)
    names = [m for m in (DEPLOY, "catboost", "bert_ft", "ensemble_cb_bertft", "lr_tabular") if m in reps]
    risks = {m: reps[m].probs()[:, HF] for m in names}
    curves = decision_curve(y_bin, risks, thresholds, n_boot=N_BOOT, seed=BOOT_SEED)
    at = {}
    for pt in (0.10, 0.20):
        nb_all = net_benefit_treat_all(y_bin, pt)
        at[f"pt_{pt:.2f}"] = {"treat_all": r4(nb_all), "models": {
            m: {"net_benefit": r4(net_benefit(y_bin, risks[m], pt)),
                "delta_nb_vs_treat_all": r4(net_benefit(y_bin, risks[m], pt) - nb_all),
                "net_reduction_in_interventions_per_100": r4(net_reduction_in_interventions(
                    net_benefit(y_bin, risks[m], pt), nb_all, pt))} for m in names}}
    plot_dca(curves, names)
    return {"is_mock": False, "target_disease": "HEART_FAILURE", "target_class": HF,
            "hypothetical_intervention": "NT-proBNP + siêu âm tim sớm (analysis plan 3.2)",
            "test_sample_size": int(len(y)), "heart_failure_test_prevalence": r4(y_bin.mean()),
            "predefined_threshold_range": [0.05, 0.30],
            "formula": "Net reduction per 100 = (NB_model - NB_treat_all) * (1 - p_t) / p_t * 100 (Vickers 2016)",
            "prevalence_note": "HF prevalence 35.1% in the synthetic test set; net benefit is a within-cohort "
                               "comparison and does not transfer to primary care.",
            "at_thresholds": at, "curves": curves}


# -------------------------------------------------------------------------- fairness
def build_fairness(rep, idx_seed=BOOT_SEED):
    test = pd.read_parquet(DATA_DIR / "test.parquet").set_index("patient_id").loc[rep.pid_test]
    p, y = rep.probs(), rep.y_test
    groups = {"gender_M": test.gender.astype(str).eq("M").to_numpy(),
              "gender_F": test.gender.astype(str).eq("F").to_numpy(),
              "age_under_65": (test.age < 65).to_numpy(), "age_65_and_older": (test.age >= 65).to_numpy()}
    for s in ("NEVER", "FORMER", "CURRENT"):
        groups[f"smoking_{s}"] = test.smoking_status.astype(str).eq(s).to_numpy()
    out = {}
    for name, mask in groups.items():
        ys, ps = y[mask], p[mask]
        present = [k for k in range(4) if 0 < np.sum(ys == k) < len(ys)]
        entry = {"sample_size": int(mask.sum()), "class_counts": np.bincount(ys, minlength=4).tolist(),
                 "classes_in_auroc": [CLASSES[k] for k in present]}
        if len(present) >= 2:
            def ovr_macro(yy, pp, ks=tuple(present)):
                from sklearn.metrics import roc_auc_score
                vals = [roc_auc_score(yy == k, pp[:, k]) for k in ks if 0 < np.sum(yy == k) < len(yy)]
                return float(np.mean(vals))
            rng = np.random.default_rng(idx_seed)
            boot = []
            for _ in range(N_BOOT):
                i = rng.integers(0, len(ys), len(ys))
                if all(0 < np.sum(ys[i] == k) < len(i) for k in present):
                    boot.append(i)
            a = bootstrap_ci(ys, ps, metric=ovr_macro, indices=np.array(boot))
            f = bootstrap_ci(ys, ps, metric=lambda yy, pp: f1_score(yy, pp.argmax(1), average="macro",
                                                                    labels=present), indices=np.array(boot))
            entry.update({"macro_auroc": r4(a["estimate"]), "macro_auroc_ci95": [r4(c) for c in a["ci95"]],
                          "macro_f1": r4(f["estimate"]), "macro_f1_ci95": [r4(c) for c in f["ci95"]]})
            if len(present) < 4:
                entry["note"] = "one-vs-rest AUROC averaged over the classes present in this subgroup only"
        else:
            entry.update({"macro_auroc": None, "macro_auroc_ci95": None, "macro_f1": None, "macro_f1_ci95": None,
                          "note": "fewer than two classes present (or empty subgroup) - not estimable"})
        out[name] = entry
    return {"metadata": {"total_test_samples": int(len(y)), "n_bootstrap": N_BOOT, "model_evaluated": DEPLOY,
                         "seed": rep.seed, "disclaimer": "Synthetic cohort: subgroup results describe the "
                         "pipeline, not fairness on real patients."}, "subgroups": out}


# ------------------------------------------------------------------- error analysis
def build_errors(rep):
    test = pd.read_parquet(DATA_DIR / "test.parquet").set_index("patient_id").loc[rep.pid_test].reset_index()
    p = rep.probs()
    pred = p.argmax(1)
    cm = confusion_matrix(rep.y_test, pred, labels=list(range(4)))
    pairs = sorted(((cm[i, j] + cm[j, i], i, j) for i in range(4) for j in range(i + 1, 4)), reverse=True)[:3]
    cases = []
    for _, i, j in pairs:
        wrong = np.where(((rep.y_test == i) & (pred == j)) | ((rep.y_test == j) & (pred == i)))[0]
        wrong = wrong[np.argsort(-p[wrong].max(1))][:10]
        for k in wrong:
            row = test.iloc[k]
            cases.append({"pair": f"{CLASSES[i]}<->{CLASSES[j]}", "patient_id": row.patient_id,
                          "true": CLASSES[rep.y_test[k]], "pred": CLASSES[pred[k]], "confidence": r4(p[k].max()),
                          "age": int(row.age), "spo2": r4(row.spo2), "temperature": r4(row.temperature),
                          "wbc": r4(row.wbc_count), "crp": r4(row.crp), "smoking": str(row.smoking_status),
                          "note_is_mtsamples": bool("VITALS AT ADMISSION" in row.clinical_note)})
    case_studies = {}
    for pid in ("PT-0044", "PT-0254"):
        hit = np.where(rep.pid_test == pid)[0]
        if len(hit):
            k = hit[0]
            case_studies[pid] = {"split": "test", "true": CLASSES[rep.y_test[k]],
                                 "probabilities": {c: r4(v) for c, v in zip(CLASSES, p[k])}}
        else:
            case_studies[pid] = {"split": "not in strict test (train/val) - not reported as a test case"}
    plot_confusion(cm)
    return {"confusion_matrix": cm.tolist(), "top_confused_pairs": [f"{CLASSES[i]}<->{CLASSES[j]} ({n})"
                                                                     for n, i, j in pairs],
            "cases": cases, "case_studies": case_studies}


# -------------------------------------------------------------------------- temporal
def build_temporal(strict_reps):
    runs = load_runs(PRED / "temporal")
    if not runs:
        return None
    out = {}
    meta = None
    for name, by_seed in runs.items():
        r = next(iter(by_seed.values()))
        meta = meta or r.meta
        ci = bootstrap_ci(r.y_test, r.probs(), n_boot=N_BOOT, seed=BOOT_SEED)
        strict = strict_reps.get(name)
        strict_auc = macro_auroc(strict.y_test, strict.probs()) if strict else None
        out[name] = {"macro_auroc_temporal": r4(ci["estimate"]), "ci95": [r4(c) for c in ci["ci95"]],
                     "macro_auroc_strict": r4(strict_auc),
                     "delta_macro_auroc": r4(ci["estimate"] - strict_auc) if strict_auc else None}
    split_meta = {k: v for k, v in (meta or {}).items() if k in ("train", "val", "test")}
    return {"split_method": "Temporal split, group-aware (patient + note source groups ordered by earliest "
                            "encounter; 70/15/15)",
            "validation_nature": "Internal robustness check on synthetic timestamps - NOT external hospital validation",
            "train_samples": split_meta.get("train", {}).get("n"), "val_samples": split_meta.get("val", {}).get("n"),
            "test_samples": split_meta.get("test", {}).get("n"), "split_detail": split_meta,
            "metrics": out.get(DEPLOY, {}), "by_model": out}


# ----------------------------------------------------------------------------- plots
def _save(fig, name):
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_DIR / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(PLOT_DIR / f"{name}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_rq1(rq1):
    comps = rq1["comparisons_vs_deployment_model"]
    fig, ax = plt.subplots(figsize=(7, 0.45 * len(comps) + 1))
    for i, c in enumerate(comps):
        ax.errorbar(c["delta"], i, xerr=[[c["delta"] - c["ci95"][0]], [c["ci95"][1] - c["delta"]]], fmt="o",
                    color="#1f4e79", capsize=3)
    ax.axvline(0, color="grey", lw=1, ls="--")
    ax.set_yticks(range(len(comps)), [LABELS[c["comparator"]] for c in comps], fontsize=8)
    ax.set_xlabel("ΔAUROC macro = Cross-attention (đóng băng) − mô hình so sánh  [CI 95%]")
    _save(fig, "fig_rq1_forest")


def plot_rq2(rq2):
    v = rq2["variants"]
    models = [("tfidf_lr", "TF-IDF+LR"), ("bert_frozen", "BERT đóng băng"), ("bert_ft", "BERT fine-tune"),
              ("xattn_frozen", "Cross-attention")]
    x = np.arange(len(v))
    fig, ax = plt.subplots(figsize=(8, 3.6))
    for k, (m, lab) in enumerate(models):
        ax.bar(x + (k - 1.5) * 0.2, [e.get(m) or 0 for e in v], 0.2, label=lab)
    for m, val in rq2["tabular_only_reference_auroc"].items():
        if m == "lr_tabular":
            ax.axhline(val, color="black", ls="--", lw=1, label="LR chỉ dữ liệu bảng")
    ax.axhline(0.5, color="grey", ls=":", lw=1)
    ax.set_xticks(x, [e["label"] for e in v])
    ax.set_ylim(0.4, 1.0)
    ax.set_ylabel("Macro AUROC (test)")
    ax.legend(fontsize=7, ncol=3, loc="lower left")
    _save(fig, "fig_rq2_text_decomposition")


def plot_rq3(rq3):
    g = pd.DataFrame(rq3["grid"])
    piv = g.pivot(index="sigma", columns="rho", values="delta_xattn_vs_best_unimodal")
    fig, ax = plt.subplots(figsize=(5.5, 3))
    im = ax.imshow(piv.values, cmap="RdBu", vmin=-0.1, vmax=0.1, origin="lower")
    for (i, j), val in np.ndenumerate(piv.values):
        ax.text(j, i, f"{val:+.3f}", ha="center", va="center", fontsize=8)
    ax.set_xticks(range(len(piv.columns)), piv.columns)
    ax.set_yticks(range(len(piv.index)), piv.index)
    ax.set_xlabel("ρ – tỷ lệ ca có tín hiệu văn bản")
    ax.set_ylabel("σ – nhiễu dữ liệu bảng (×SD)")
    fig.colorbar(im, ax=ax, label="Δ AUROC fusion − max(đơn phương thức)")
    _save(fig, "fig_rq3_heatmap")


def plot_reliability(y, methods):
    fig, axes = plt.subplots(1, len(methods), figsize=(3 * len(methods), 3), sharey=True)
    for ax, (name, p) in zip(axes, methods.items()):
        conf, correct = p.max(1), (p.argmax(1) == y)
        edges = np.linspace(0, 1, 11)
        b = np.clip(np.digitize(conf, edges[1:-1]), 0, 9)
        xs = [conf[b == i].mean() for i in range(10) if np.any(b == i)]
        ys = [correct[b == i].mean() for i in range(10) if np.any(b == i)]
        ax.plot([0, 1], [0, 1], "--", color="grey")
        ax.plot(xs, ys, "o-")
        ax.set_title(f"{name}\nECE={expected_calibration_error(y, p):.3f}", fontsize=9)
        ax.set_xlabel("Độ tin cậy")
    axes[0].set_ylabel("Độ chính xác")
    _save(fig, "fig_calibration")


def plot_missing_modality(table):
    models = [("xattn_frozen", "Cross-attention"), ("catboost", "CatBoost"), ("bert_ft", "BERT fine-tune"),
              ("ensemble_cb_bertft", "Ensemble")]
    scen = list(SCEN_LABEL)
    x = np.arange(len(scen))
    fig, ax = plt.subplots(figsize=(8, 3.4))
    for k, (m, lab) in enumerate(models):
        ax.bar(x + (k - 1.5) * 0.2, [table[s].get(m, {}).get("mean") or 0 for s in scen], 0.2, label=lab)
    ax.axhline(0.5, color="grey", ls=":")
    ax.set_xticks(x, [SCEN_LABEL[s] for s in scen], fontsize=8)
    ax.set_ylim(0.3, 1.0)
    ax.set_ylabel("Macro AUROC (test)")
    ax.legend(fontsize=7, ncol=4)
    _save(fig, "fig_missing_modality")


def plot_dca(curves, names):
    t = curves["threshold"]
    fig, ax = plt.subplots(figsize=(6, 3.8))
    for m in names:
        c = curves[m]
        ax.plot(t, c["net_benefit"], label=LABELS[m])
        ax.fill_between(t, c["ci95_low"], c["ci95_high"], alpha=0.12)
    ax.plot(t, curves["treat_all"], "k--", label="Can thiệp tất cả")
    ax.plot(t, curves["treat_none"], "k:", label="Không can thiệp")
    ax.set_xlabel("Ngưỡng xác suất p_t (suy tim, one-vs-rest)")
    ax.set_ylabel("Net benefit")
    ax.set_ylim(-0.05, 0.4)
    ax.legend(fontsize=7)
    _save(fig, "fig_dca")


def plot_confusion(cm):
    fig, ax = plt.subplots(figsize=(4, 3.6))
    ax.imshow(cm, cmap="Blues")
    for (i, j), v in np.ndenumerate(cm):
        ax.text(j, i, str(v), ha="center", va="center")
    ax.set_xticks(range(4), [c[:5] for c in CLASSES])
    ax.set_yticks(range(4), [c[:5] for c in CLASSES])
    ax.set_xlabel("Dự đoán")
    ax.set_ylabel("Thực tế")
    _save(fig, "fig_confusion_matrix")





# ------------------------------------------------------------------- data provenance
def build_provenance() -> dict:
    """Effective sample size: records are generated from a small number of Synthea source patients."""
    out = {}
    for split in ("train", "val", "test"):
        d = pd.read_parquet(DATA_DIR / f"{split}.parquet")
        out[split] = {"records": int(len(d)), "distinct_source_patients": int(d.source_patient_group.nunique()),
                      "records_per_class": {CLASSES[int(k)]: int(v) for k, v in d.diagnosis_label.value_counts().sort_index().items()},
                      "distinct_source_patients_per_class": {CLASSES[int(k)]: int(v) for k, v in
                                                             d.groupby("diagnosis_label").source_patient_group.nunique().items()}}
    out["warning"] = ("Records are generated from a small number of Synthea source patients (e.g. all HEART_FAILURE and "
                      "all PNEUMONIA test records each come from ONE source patient). Bootstrap CIs resample records "
                      "and therefore understate uncertainty; per-class results for those classes describe single "
                      "synthetic patients. See also sensitivity_grouped_cv_posthoc.")
    return out

# --------------------------------------------------------------- post-hoc grouped CV
def build_cv():
    folds = sorted((PRED / "cv").glob("fold*")) if (PRED / "cv").is_dir() else []
    if not folds:
        return None
    per_model: dict[str, list[float]] = defaultdict(list)
    sizes = []
    for folder in folds:
        runs = load_runs(folder)
        if "catboost" in runs and "bert_ft" in runs:
            runs["ensemble_cb_bertft"] = {42: Ensemble(runs["catboost"][42], runs["bert_ft"][42], "ensemble_cb_bertft")}
        for name, by_seed in runs.items():
            r = next(iter(by_seed.values()))
            per_model[name].append(macro_auroc(r.y_test, r.probs()))
        sizes.append(int(len(next(iter(next(iter(runs.values())).values())).y_test)))
    models = [{"model": m, "label": LABELS.get(m, m), "fold_auroc": [r4(v) for v in vals],
               "auroc_mean": r4(np.mean(vals)), "auroc_sd": r4(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0}
              for m, vals in per_model.items()]
    models.sort(key=lambda r: RQ1_ORDER.index(r["model"]) if r["model"] in RQ1_ORDER else 99)
    return {"post_hoc": True, "design": "StratifiedGroupKFold(5) over all 2,000 rows on merged patient+note "
            "groups; 15% of remaining groups as validation; seed 42 (docs/11_ANALYSIS_PLAN.md A.6)",
            "n_folds": len(folds), "test_fold_sizes": sizes, "models": models}

# ------------------------------------------------------------- API compatibility files
def export_api_artifacts(rq1_runs, reps, registry) -> None:
    """Rewrite the legacy files read by the API routes from the official RQ1 predictions."""
    rep = reps[DEPLOY]
    np.savez_compressed(ROOT / "data" / "holdout_predictions.npz", y_true=rep.y_test,
                        prob_mcdss=rep.probs(), prob_tabular=reps["catboost"].probs(),
                        prob_text=reps["bert_ft"].probs(), patient_id=rep.pid_test)
    variants = {}
    for variant, model in (("tabular", "ft_transformer"), ("text", "bert_frozen"), ("concat", "concat_frozen"),
                           ("cross_attention", DEPLOY)):
        r = reps[model]
        m = compute_multiclass_metrics(r.y_test, r.probs())
        variants[variant] = {"model_key": model, "seed": r.seed, "temperature": r.t, "validation_nll": r.val_nll,
                             "test": m}
    ablation = {"metadata": {"generated_at": registry["metadata"]["generated_at"],
                             "split": "data/processed_rebuilt_strict",
                             "split_rows": {"train": 1425, "val": 273, "test": int(len(rep.y_test))},
                             "source": "results/registry.json (representative seed = lowest validation NLL)",
                             "note": "Frozen Bio_ClinicalBERT for text/concat/cross-attention; see registry for all seeds."},
                "variants": variants}
    (ROOT / "data" / "ablation_results.json").write_text(json.dumps(ablation, indent=2), encoding="utf-8")
    (ROOT / "data" / "fairness_report.json").write_text(
        json.dumps(registry["fairness"], indent=2, ensure_ascii=False), encoding="utf-8")
    deploy_metrics = compute_multiclass_metrics(rep.y_test, rep.probs())
    (ROOT / "data" / "multimodal_training_results.json").write_text(json.dumps({
        "metadata": {"generated_at": registry["metadata"]["generated_at"], "data_dir": "data/processed_rebuilt_strict",
                     "model": DEPLOY, "seed": rep.seed, "temperature": rep.t,
                     "source": "results/registry.json (deployment checkpoint data/checkpoints/multimodal_best.pt)"},
        "test_metrics_uncalibrated": compute_multiclass_metrics(rep.y_test, rep.probs(calibrated=False)),
        "test_metrics_calibrated": deploy_metrics}, indent=2), encoding="utf-8")

# ------------------------------------------------------------------------------ main
def main() -> None:
    verify_manifest(DATA_DIR)
    rq1_runs = load_runs(PRED / "rq1")
    if DEPLOY not in rq1_runs:
        raise SystemExit("RQ1 predictions missing - run scripts/run_research_experiments.py rq1 first")
    y = representative(rq1_runs[DEPLOY]).y_test
    idx = bootstrap_indices(len(y), N_BOOT, BOOT_SEED, y)  # shared resamples => paired comparisons

    rq1, reps = build_rq1(rq1_runs, idx)
    plot_rq1(rq1)
    registry = {
        "metadata": {
            "registry_version": "2.0.0", "generated_at": datetime.now(timezone.utc).isoformat(),
            "generator": "scripts/build_results_registry.py",
            "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                                         text=True).stdout.strip(),
            "data_manifest_sha256": sha256(ROOT / "data" / "DATA_MANIFEST.json"),
            "analysis_plan_freeze": json.loads((RESULTS / "preregistration" / "analysis_plan_freeze.json")
                                               .read_text(encoding="utf-8")),
            "seeds": sorted({s for runs in rq1_runs.values() for s in runs if s}),
            "n_bootstrap": N_BOOT, "bootstrap_seed": BOOT_SEED, "deployment_model": DEPLOY,
            "deployment_seed": reps[DEPLOY].seed, "is_mock_for_member1_member2": False,
        },
        "data_provenance": build_provenance(),
        "rq1_multiseed_comparison": rq1,
    }
    rq2 = build_rq2(rq1["models"], idx)
    if rq2["variants"]:
        registry["rq2_text_signal_decomposition"] = rq2
        plot_rq2(rq2)
    rq3 = build_rq3()
    if rq3 and rq3["grid"]:
        registry["rq3_complementarity_simulation"] = rq3
        plot_rq3(rq3)
    registry["rq4_calibration"] = build_calibration(reps[DEPLOY], idx)
    registry["rq4_missing_modality"] = build_robustness(rq1_runs)
    registry["rq4_dca"] = build_dca(reps, idx)
    registry["fairness"] = build_fairness(reps[DEPLOY])
    registry["error_analysis"] = build_errors(reps[DEPLOY])
    temporal = build_temporal(reps)
    if temporal:
        registry["generalization"] = temporal
    cv = build_cv()
    if cv:
        registry["sensitivity_grouped_cv_posthoc"] = cv
    # backwards-compatible aliases used by Member 2 tests / API consumers
    registry["dca"] = registry["rq4_dca"]
    registry["robustness"] = registry["rq4_missing_modality"]
    # Member 3 sections (RAG, latency): latest reports written by scripts/eval_rag.py and
    # scripts/benchmark_latency.py; fall back to the pre-merge registry snapshot if absent.
    m3_snapshot = RESULTS / "raw" / "registry_member3_9ecaf31.json"
    snapshot = json.loads(m3_snapshot.read_text(encoding="utf-8")) if m3_snapshot.is_file() else {}
    for key, report in (("rag", "rag_evaluation_report.json"), ("latency", "latency_report.json")):
        path = RESULTS / report
        if path.is_file():
            registry[key] = json.loads(path.read_text(encoding="utf-8"))
        elif key in snapshot:
            registry[key] = snapshot[key]
    docker_latency = RESULTS / "latency_report_docker_lightweight_2026-11-19.json"
    if docker_latency.is_file():
        registry["latency_docker_lightweight"] = json.loads(docker_latency.read_text(encoding="utf-8"))
    registry["superseded"] = {
        "member2_backlog09_2026-11-19": "DCA, robustness, temporal and fairness numbers produced by "
        "scripts/evaluate_research_hardening_member2.py on the 2026-11-18 dataset are withdrawn: that dataset "
        "leaked labels through unredacted diagnoses and reused MTSamples notes (TF-IDF AUROC 0.962 with numbers "
        "masked); the script trained its own fusion model without validation and with a fixed temperature of "
        "1.15, and the intervention formula divided by p_t instead of p_t/(1-p_t).",
    }
    export_api_artifacts(rq1_runs, reps, registry)
    out = RESULTS / "registry.json"
    out.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] wrote {out}")


if __name__ == "__main__":
    main()
