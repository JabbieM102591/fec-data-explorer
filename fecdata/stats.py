import numpy as np


def _positive(values):
    arr = np.asarray(list(values), dtype=float)
    arr = arr[np.isfinite(arr)]
    return arr[arr > 0]


def hhi(values):
    """Herfindahl-Hirschman Index on a 0 to 10,000 scale.

    N equal shares give 10,000 / N. One holder with everything gives 10,000.
    """
    x = _positive(values)
    if x.size == 0:
        return 0.0
    shares = x / x.sum()
    return float((shares ** 2).sum() * 10000)


def gini(values):
    """Gini coefficient: 0 is perfectly even, values near 1 mean a few hold most."""
    x = np.sort(_positive(values))
    n = x.size
    if n == 0:
        return 0.0
    ranks = np.arange(1, n + 1)
    return float(2 * (ranks * x).sum() / (n * x.sum()) - (n + 1) / n)


def mean_median(values):
    x = _positive(values)
    if x.size == 0:
        return {"mean": 0.0, "median": 0.0, "mean_to_median": 0.0}
    mean, median = float(x.mean()), float(np.median(x))
    ratio = mean / median if median else 0.0
    return {"mean": mean, "median": median, "mean_to_median": ratio}


def bootstrap_ci(values, stat=np.median, n_boot=2000, alpha=0.05, seed=42):
    """Percentile bootstrap interval for a statistic of one sample."""
    x = _positive(values)
    if x.size == 0:
        return 0.0, 0.0
    rng = np.random.default_rng(seed)
    est = np.array([stat(rng.choice(x, size=x.size, replace=True)) for _ in range(n_boot)])
    lo, hi = np.percentile(est, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(lo), float(hi)


def bootstrap_share_ci(amounts, flags, n_boot=2000, alpha=0.05, seed=42):
    """Share of dollars where flags is True, with a bootstrap interval.

    Rows are resampled as whole gifts. Returns (share, low, high).
    """
    a = np.asarray(amounts, dtype=float)
    f = np.asarray(flags, dtype=bool)
    keep = np.isfinite(a) & (a > 0)
    a, f = a[keep], f[keep]
    if a.size == 0:
        return 0.0, 0.0, 0.0
    point = float(a[f].sum() / a.sum())
    rng = np.random.default_rng(seed)
    n = a.size
    shares = np.empty(n_boot)
    for b in range(n_boot):
        i = rng.integers(0, n, n)
        total = a[i].sum()
        shares[b] = a[i][f[i]].sum() / total if total else 0.0
    lo, hi = np.percentile(shares, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return point, float(lo), float(hi)


def summary(values, seed=42):
    x = _positive(values)
    mm = mean_median(x)
    lo, hi = bootstrap_ci(x, np.median, seed=seed)
    return {
        "n": int(x.size),
        "total": float(x.sum()),
        "mean": mm["mean"],
        "median": mm["median"],
        "mean_to_median": mm["mean_to_median"],
        "hhi": hhi(x),
        "gini": gini(x),
        "median_ci_low": lo,
        "median_ci_high": hi,
    }
