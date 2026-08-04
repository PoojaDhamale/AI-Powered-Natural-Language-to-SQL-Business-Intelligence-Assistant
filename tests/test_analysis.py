import pandas as pd
from analysis import compute_rate


def test_compute_rate_basic_calculation():
    metric = pd.DataFrame({"region": ["Australia", "France"], "total_returns": [10, 20]})
    volume = pd.DataFrame({"region": ["Australia", "France"], "total_units_sold": [100, 200]})

    result = compute_rate(metric, volume)

    aus_row = result[result["region"] == "Australia"].iloc[0]
    assert aus_row["rate_percent"] == 10.0


def test_compute_rate_sorts_highest_first():
    metric = pd.DataFrame({"region": ["A", "B"], "total_returns": [5, 50]})
    volume = pd.DataFrame({"region": ["A", "B"], "total_units_sold": [1000, 100]})

    result = compute_rate(metric, volume)

    assert result.iloc[0]["region"] == "B"


def test_compute_rate_empty_metric_returns_empty():
    empty = pd.DataFrame()
    volume = pd.DataFrame({"region": ["A"], "total_units_sold": [100]})

    result = compute_rate(empty, volume)

    assert result.empty


def test_compute_rate_missing_region_column_returns_empty():
    metric = pd.DataFrame({"not_region": ["A"], "total_returns": [10]})
    volume = pd.DataFrame({"region": ["A"], "total_units_sold": [100]})

    result = compute_rate(metric, volume)

    assert result.empty


def test_compute_rate_no_matching_regions_returns_empty():
    metric = pd.DataFrame({"region": ["Australia"], "total_returns": [10]})
    volume = pd.DataFrame({"region": ["Germany"], "total_units_sold": [100]})

    result = compute_rate(metric, volume)

    assert result.empty
