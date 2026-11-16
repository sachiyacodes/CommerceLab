from __future__ import annotations

import numpy as np
import pandas as pd


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total <= 0:
        return 0.0, 0.0
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    margin = z * np.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return max(0.0, float(center - margin)), min(1.0, float(center + margin))


def bootstrap_mean_interval(values: pd.Series, seed: int = 42, draws: int = 2000) -> tuple[float, float]:
    clean = pd.to_numeric(values, errors="coerce").dropna().to_numpy(dtype=float)
    if clean.size == 0:
        return 0.0, 0.0
    rng = np.random.default_rng(seed)
    means = rng.choice(clean, size=(draws, clean.size), replace=True).mean(axis=1)
    return tuple(float(v) for v in np.quantile(means, [0.025, 0.975]))


def conversion_interval(successes: int, total: int) -> tuple[float, float]:
    return wilson_interval(successes, total)
