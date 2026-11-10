"""Validation-only scalar temperature calibration."""

from __future__ import annotations

import torch
from torch import Tensor, nn


class TemperatureScalingCalibrator(nn.Module):
    def __init__(self, temperature: float = 1.0) -> None:
        super().__init__()
        if temperature <= 0:
            raise ValueError("Temperature must be positive")
        self.log_temperature = nn.Parameter(torch.tensor(float(temperature)).log())

    @property
    def temperature(self) -> float:
        return float(self.log_temperature.detach().exp())

    def forward(self, logits: Tensor) -> Tensor:
        return logits / self.log_temperature.exp()

    def predict_proba(self, logits: Tensor) -> Tensor:
        return torch.softmax(self(logits), dim=-1)

    def fit(self, validation_logits: Tensor, validation_labels: Tensor,
            max_iter: int = 100) -> "TemperatureScalingCalibrator":
        if validation_logits.ndim != 2 or validation_labels.shape != (validation_logits.shape[0],):
            raise ValueError("Expected validation logits [N,C] and labels [N]")
        if validation_logits.shape[0] < 2 or not torch.isfinite(validation_logits).all():
            raise ValueError("Validation logits must contain at least two finite rows")
        logits = validation_logits.detach().float().cpu()
        labels = validation_labels.detach().long().cpu()
        self.cpu()
        optimizer = torch.optim.LBFGS([self.log_temperature], lr=0.1, max_iter=max_iter,
                                      line_search_fn="strong_wolfe")

        def closure() -> Tensor:
            optimizer.zero_grad()
            loss = nn.functional.cross_entropy(self(logits), labels)
            loss.backward()
            return loss

        optimizer.step(closure)
        with torch.no_grad():
            self.log_temperature.clamp_(min=-6.0, max=6.0)
        return self
