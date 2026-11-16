from __future__ import annotations

import numpy as np
import pandas as pd


def simulate_ab_test(sample_size: int = 1200, baseline: float = 0.035, lift: float = 0.006, seed: int = 42) -> tuple[pd.DataFrame, dict[str, float]]:
    """Generate a synthetic randomized test solely to demonstrate analysis mechanics."""
    if sample_size < 2 or not 0 < baseline < 1 or not 0 <= baseline + lift < 1:
        raise ValueError("Use sample_size >= 2 and valid conversion probabilities in [0, 1].")
    rng = np.random.default_rng(seed)
    variant = np.repeat(["Control", "Variant"], [sample_size // 2, sample_size - sample_size // 2])
    probability = np.where(variant == "Variant", baseline + lift, baseline)
    converted = rng.binomial(1, probability)
    frame = pd.DataFrame({"assignment": variant, "converted": converted})
    n0, n1 = (frame.assignment == "Control").sum(), (frame.assignment == "Variant").sum()
    p0 = frame.loc[frame.assignment.eq("Control"), "converted"].mean()
    p1 = frame.loc[frame.assignment.eq("Variant"), "converted"].mean()
    pooled = (p0 * n0 + p1 * n1) / (n0 + n1)
    se = np.sqrt(pooled * (1 - pooled) * (1 / n0 + 1 / n1))
    z = (p1 - p0) / se if se else 0.0
    # Two-sided normal approximation; erfc avoids an optional scipy dependency.
    from math import erfc, sqrt
    p_value = erfc(abs(float(z)) / sqrt(2))
    return frame, {"control_rate": float(p0), "variant_rate": float(p1), "absolute_lift": float(p1 - p0),
                   "z_score": float(z), "p_value": float(p_value), "n_control": int(n0), "n_variant": int(n1)}
