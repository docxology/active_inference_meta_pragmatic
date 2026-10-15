import numpy as np
import pytest

from visualization.resource_calibration import calibration_points


def test_calibration_uses_bin_means_retains_endpoints_and_omits_empty_bins():
    trials = [
        {"forecast_p1": 0.0, "state": 0},
        {"forecast_p1": 0.05, "state": 1},
        {"forecast_p1": 0.15, "state": 1},
        {"forecast_p1": 1.0, "state": 1},
    ]
    points = calibration_points(trials, "forecast")
    np.testing.assert_allclose(points, [[0.025, 0.5, 2], [0.15, 1, 1], [1, 1, 1]])
    assert points[:, 2].sum() == 4
    assert points[0, 0] != pytest.approx(0.05)
    assert calibration_points([], "forecast").shape == (0, 3)
