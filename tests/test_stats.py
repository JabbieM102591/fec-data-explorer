import numpy as np

from fecdata import stats


def test_hhi_equal_shares():
    assert round(stats.hhi([5, 5, 5, 5])) == 2500


def test_hhi_single_holder():
    assert round(stats.hhi([100])) == 10000


def test_gini_known_values():
    assert abs(stats.gini([1, 2, 3, 4]) - 0.25) < 1e-9
    assert abs(stats.gini([7, 7, 7])) < 1e-9


def test_mean_median_skew():
    r = stats.mean_median([1, 1, 1, 9])
    assert r["mean"] == 3 and r["median"] == 1 and r["mean_to_median"] == 3


def test_ignores_refunds_and_zeros():
    assert stats.hhi([10, -5, 0, 10]) == stats.hhi([10, 10])


def test_bootstrap_ci_constant_and_repeatable():
    assert stats.bootstrap_ci([4, 4, 4, 4]) == (4.0, 4.0)
    data = [1, 2, 3, 4, 5, 6, 7, 8]
    assert stats.bootstrap_ci(data, seed=1) == stats.bootstrap_ci(data, seed=1)
    lo, hi = stats.bootstrap_ci(data, np.mean)
    assert lo <= np.mean(data) <= hi


def test_share_ci_all_flagged():
    assert stats.bootstrap_share_ci([10, 20, 30], [True, True, True]) == (1.0, 1.0, 1.0)


def test_share_ci_point_estimate():
    share, lo, hi = stats.bootstrap_share_ci([60, 40], [True, False])
    assert abs(share - 0.6) < 1e-9 and lo <= share <= hi


def test_summary_has_expected_keys():
    s = stats.summary([10, 20, 30, 40])
    for key in ["n", "total", "mean", "median", "hhi", "gini", "median_ci_low"]:
        assert key in s
    assert s["n"] == 4 and s["total"] == 100
