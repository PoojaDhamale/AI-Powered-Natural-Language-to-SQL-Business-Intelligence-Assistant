import pandas as pd
from visualize import make_chart


def test_single_scalar_returns_no_chart():
    df = pd.DataFrame({"total_revenue": [9185437.85]})
    fig = make_chart(df)
    assert fig is None


def test_empty_dataframe_returns_no_chart():
    df = pd.DataFrame()
    fig = make_chart(df)
    assert fig is None


def test_category_plus_number_produces_bar_chart():
    df = pd.DataFrame({
        "category_name": ["Bikes", "Accessories", "Clothing"],
        "revenue": [23642500.06, 906656.58, 365410.54],
    })
    fig = make_chart(df, title="Revenue by category")
    assert fig is not None
    assert len(fig.data) > 0


def test_date_plus_number_produces_line_chart():
    df = pd.DataFrame({
        "month": pd.to_datetime(["2022-01-01", "2022-02-01", "2022-03-01"]),
        "revenue": [1000, 1200, 1100],
    })
    fig = make_chart(df, title="Monthly revenue")
    assert fig is not None
    assert len(fig.data) > 0


def test_prefers_rate_percent_over_raw_count():
    df = pd.DataFrame({
        "region": ["Australia", "France", "Germany"],
        "total_returns": [208, 113, 83],
        "rate_percent": [2.19, 2.67, 1.74],
    })
    fig = make_chart(df, title="Return rate by region")
    assert fig is not None
    y_axis_values = list(fig.data[0].y)
    assert 2.19 in y_axis_values or 2.67 in y_axis_values
