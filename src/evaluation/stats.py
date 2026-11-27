"""Statistical inference for Phase 3 (docs/11_ANALYSIS_PLAN.md sections 2.3, 3 and A.1-A.5).

* record-level (paired) bootstrap (resampling unit = patient_id record) confidence intervals and two-sided p-values
* Holm step-down adjustment
* decision-curve net benefit with the Vickers et al. (2016) net-reduction formula
* equal-mass ECE, class-wise ECE, vector scaling and one-vs-rest isotonic calibration
"""

from __future__ import annotations

from typing import Callable, Sequence

import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import roc_auc_score

Metric = Callable[[np.ndarray, np.ndarray], float]


def macro_auroc(y: np.ndarray, p: np.ndarray) -> float:
    return float(roc_auc_score(y, p, multi_class="ovr", average="macro", labels=list(range(p.shape[1]))))


def bootstrap_indices(n: int, n_boot: int, seed: int, y: np.ndarray | None = None) -> np.ndarray:
    """Resample patients with replacement; redraw samples that miss a class (AUROC undefined)."""
    rng = np.random.default_rng(seed)
    out = np.empty((n_boot, n), dtype=np.int64)
    n_classes = None if y is None else len(np.unique(y))
    for b in range(n_boot):
        while True:
            idx = rng.integers(0, n, size=n)
            if n_classes is None or len(np.unique(y[idx])) == n_classes:
                out[b] = idx
                break
    return out


def bootstrap_ci(y: np.ndarray, p: np.ndarray, metric: Metric = macro_auroc, n_boot: int = 2000,
                 seed: int = 2026, alpha: float = 0.05, indices: np.ndarray | None = None) -> dict:
    idx = bootstrap_indices(len(y), n_boot, seed, y) if indices is None else indices
    stats = np.array([metric(y[i], p[i]) for i in idx])
    lo, hi = np.quantile(stats, [alpha / 2, 1 - alpha / 2])
    return {"estimate": float(metric(y, p)), "ci95": [float(lo), float(hi)], "n_boot": int(len(idx))}


def paired_bootstrap(y: np.ndarray, p_a: np.ndarray, p_b: np.ndarray, metric: Metric = macro_auroc,
                     n_boot: int = 2000, seed: int = 2026, indices: np.ndarray | None = None) -> dict:
    """Difference metric(a) - metric(b) on the same resampled patients.

    p-value: two-sided percentile-bootstrap test of H0: difference = 0, computed as
    2 * min(P(diff* <= 0), P(diff* >= 0)) with a +1 correction (never exactly 0).
    """
    idx = bootstrap_indices(len(y), n_boot, seed, y) if indices is None else indices
    diffs = np.array([metric(y[i], p_a[i]) - metric(y[i], p_b[i]) for i in idx])
    point = metric(y, p_a) - metric(y, p_b)
    lo, hi = np.quantile(diffs, [0.025, 0.975])
    p_le = (np.sum(diffs <= 0) + 1) / (len(diffs) + 1)
    p_ge = (np.sum(diffs >= 0) + 1) / (len(diffs) + 1)
    return {"delta": float(point), "ci95": [float(lo), float(hi)], "p_value": float(min(1.0, 2 * min(p_le, p_ge))),
            "n_boot": int(len(idx))}


def holm(p_values: Sequence[float]) -> list[float]:
    """Holm step-down adjusted p-values (same order as the input)."""
    p = np.asarray(p_values, dtype=float)
    order = np.argsort(p)
    m = len(p)
    adjusted = np.empty(m)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * p[i])
        adjusted[i] = min(1.0, running)
    return adjusted.tolist()


# ------------------------------------------------------------------------------- DCA
def net_benefit(y_bin: np.ndarray, risk: np.ndarray, threshold: float) -> float:
    n = len(y_bin)
    treat = risk >= threshold
    tp = np.sum(treat & (y_bin == 1))
    fp = np.sum(treat & (y_bin == 0))
    return float(tp / n - fp / n * threshold / (1 - threshold))


def net_benefit_treat_all(y_bin: np.ndarray, threshold: float) -> float:
    prevalence = float(np.mean(y_bin))
    return prevalence - (1 - prevalence) * threshold / (1 - threshold)


def net_reduction_in_interventions(nb_model: float, nb_all: float, threshold: float) -> float:
    """Net reduction in interventions per 100 patients (Vickers et al., 2016)."""
    return (nb_model - nb_all) * (1 - threshold) / threshold * 100


def decision_curve(y_bin: np.ndarray, risks: dict[str, np.ndarray], thresholds: np.ndarray,
                   n_boot: int = 2000, seed: int = 2026) -> dict:
    idx = bootstrap_indices(len(y_bin), n_boot, seed, y_bin)
    curves = {"threshold": thresholds.tolist(),
              "treat_all": [net_benefit_treat_all(y_bin, t) for t in thresholds],
              "treat_none": [0.0] * len(thresholds)}
    for name, risk in risks.items():
        point = [net_benefit(y_bin, risk, t) for t in thresholds]
        boot = np.array([[net_benefit(y_bin[i], risk[i], t) for t in thresholds] for i in idx])
        curves[name] = {"net_benefit": point,
                        "ci95_low": np.quantile(boot, 0.025, axis=0).tolist(),
                        "ci95_high": np.quantile(boot, 0.975, axis=0).tolist()}
    return curves


# ----------------------------------------------------------------------- calibration
def ece_equal_mass(y: np.ndarray, p: np.ndarray, n_bins: int = 15) -> float:
    conf = p.max(axis=1)
    correct = (p.argmax(axis=1) == y).astype(float)
    order = np.argsort(conf)
    bins = np.array_split(order, n_bins)
    return float(sum(len(b) / len(y) * abs(correct[b].mean() - conf[b].mean()) for b in bins if len(b)))


def classwise_ece(y: np.ndarray, p: np.ndarray, n_bins: int = 10) -> float:
    edges = np.linspace(0, 1, n_bins + 1)
    total = 0.0
    for k in range(p.shape[1]):
        yk = (y == k).astype(float)
        pk = p[:, k]
        bins = np.clip(np.digitize(pk, edges[1:-1]), 0, n_bins - 1)
        total += sum(np.mean(bins == b) * abs(yk[bins == b].mean() - pk[bins == b].mean())
                     for b in range(n_bins) if np.any(bins == b))
    return float(total / p.shape[1])


def softmax(z: np.ndarray) -> np.ndarray:
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def fit_vector_scaling(logits: np.ndarray, y: np.ndarray, steps: int = 500, lr: float = 0.05):
    """Per-class scale w and bias b: softmax(w * z + b), fitted by NLL on validation."""
    import torch

    z = torch.tensor(logits, dtype=torch.float64)
    target = torch.tensor(y, dtype=torch.long)
    w = torch.ones(z.shape[1], dtype=torch.float64, requires_grad=True)
    b = torch.zeros(z.shape[1], dtype=torch.float64, requires_grad=True)
    optimizer = torch.optim.LBFGS([w, b], lr=lr, max_iter=steps)

    def closure():
        optimizer.zero_grad()
        loss = torch.nn.functional.cross_entropy(z * w + b, target)
        loss.backward()
        return loss

    optimizer.step(closure)
    w_np, b_np = w.detach().numpy(), b.detach().numpy()
    return lambda new_logits: softmax(new_logits * w_np + b_np)


def fit_isotonic_ovr(probs: np.ndarray, y: np.ndarray):
    models = [IsotonicRegression(out_of_bounds="clip", y_min=0, y_max=1).fit(probs[:, k], (y == k).astype(float))
              for k in range(probs.shape[1])]

    def apply(new_probs: np.ndarray) -> np.ndarray:
        out = np.column_stack([m.predict(new_probs[:, k]) for k, m in enumerate(models)])
        out = np.clip(out, 1e-6, None)
        return out / out.sum(axis=1, keepdims=True)

    return apply
