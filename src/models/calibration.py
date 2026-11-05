"""
Temperature Scaling Probability Calibration Module
Multimodal EHR CDSS - Phase 2 / Backlog 04 (Member 1 / Member 3 Deliverable)

Implements:
- TemperatureScalingCalibrator: Post-processing parametric calibration optimizing
  Negative Log-Likelihood (NLL) on validation logits via L-BFGS to drive ECE < 0.05.

Mathematical Specification:
docs/02_MULTIMODAL_ARCHITECTURE_AND_MATH.md Section 5
Guo et al., "On Calibration of Modern Neural Networks", ICML 2017.
"""

from __future__ import annotations

import torch
import torch.nn.functional as F
from torch import Tensor, nn


class TemperatureScalingCalibrator(nn.Module):
    """
    Post-processing Probability Calibrator using Temperature Scaling.

    For an input logits vector z in R^K, computes calibrated probabilities:
        p_hat_k = exp(z_k / T) / sum_j exp(z_j / T)
    where T > 0 is the learned temperature parameter.
    
    T > 1 softens overconfident predictions.
    T < 1 sharpens underconfident predictions.
    Preserves logit rank-order and multiclass AUROC.
    """

    def __init__(self, initial_temperature: float = 1.0) -> None:
        super().__init__()
        if initial_temperature <= 0:
            raise ValueError(f"initial_temperature must be positive, got {initial_temperature}")
        self.temperature = nn.Parameter(torch.ones(1) * float(initial_temperature))

    @property
    def current_temperature(self) -> float:
        """Return the current temperature value as a Python float clamped to >= 0.01."""
        return float(torch.clamp(self.temperature, min=0.01).item())

    def scale_logits(self, logits: Tensor) -> Tensor:
        """Divide logits by temperature T."""
        temp = torch.clamp(self.temperature, min=0.01)
        return logits / temp

    def forward(self, logits: Tensor) -> Tensor:
        """
        Compute calibrated probability distribution.

        Args:
            logits: Logits tensor of shape [Batch, K].

        Returns:
            calibrated_probabilities: Normalized probabilities of shape [Batch, K] summing to 1.0.
        """
        scaled_logits = self.scale_logits(logits)
        return F.softmax(scaled_logits, dim=-1)

    def fit(
        self,
        val_logits: Tensor,
        val_labels: Tensor,
        lr: float = 0.01,
        max_iter: int = 100,
    ) -> float:
        """
        Fit temperature T by minimizing Negative Log-Likelihood (NLL) on validation data.

        Args:
            val_logits: Tensor of shape [N_val, K].
            val_labels: Target class indices of shape [N_val] or one-hot [N_val, K].
            lr: Learning rate for L-BFGS optimizer.
            max_iter: Maximum number of L-BFGS iterations.

        Returns:
            optimal_temperature: The calibrated temperature value.
        """
        if val_labels.ndim == 2:
            target = val_labels.argmax(dim=-1).long()
        else:
            target = val_labels.long()

        nll_criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.LBFGS([self.temperature], lr=lr, max_iter=max_iter)

        def eval_step():
            optimizer.zero_grad()
            temp = torch.clamp(self.temperature, min=0.01)
            loss = nll_criterion(val_logits / temp, target)
            loss.backward()
            return loss

        optimizer.step(eval_step)
        with torch.no_grad():
            self.temperature.clamp_(min=0.01)

        return self.current_temperature

