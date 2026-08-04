import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _find_date_column(df: pd.DataFrame):
    DATE_KEYWORDS = ("date", "month", "year", "week", "quarter", "period", "time", "trunc")

    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col

        col_lower = col.lower()

        if any(kw in col_lower for kw in DATE_KEYWORDS):
            if pd.api.types.is_integer_dtype(df[col]) or pd.api.types.is_float_dtype(df[col]):
                sample = df[col].dropna()
                looks_like_year = len(sample) > 0 and sample.between(1900, 2100).all()
                looks_like_plain_month = len(sample) > 0 and sample.between(1, 12).all()
                if not looks_like_year and looks_like_plain_month:
                    continue
                if not looks_like_year and not looks_like_plain_month:
                    continue
            if df[col].dtype == object:
                try:
                    parsed = pd.to_datetime(df[col], errors="coerce")
                    if parsed.notna().sum() >= len(df) * 0.8:
                        return col
                except Exception:
                    pass
            elif not (pd.api.types.is_integer_dtype(df[col]) or pd.api.types.is_float_dtype(df[col])):
                return col

    for col in df.columns:
        if df[col].dtype == object and not pd.api.types.is_numeric_dtype(df[col]):
            try:
                parsed = pd.to_datetime(df[col], errors="coerce")
                non_null = df[col].notna().sum()
                if non_null > 0 and parsed.notna().sum() >= non_null * 0.8:
                    return col
            except Exception:
                continue

    return None


def _find_numeric_column(df: pd.DataFrame, exclude=None, prefer=None):
    exclude = exclude or []
    prefer = prefer or []

    numeric_cols = [
        col for col in df.columns
        if col not in exclude and pd.api.types.is_numeric_dtype(df[col])
    ]
    if not numeric_cols:
        return None

    for pref in prefer:
        for col in numeric_cols:
            if pref.lower() in col.lower():
                return col

    return numeric_cols[0]


def _find_categorical_column(df: pd.DataFrame, exclude=None):
    exclude = exclude or []
    for col in df.columns:
        if col in exclude:
            continue
        if not pd.api.types.is_numeric_dtype(df[col]):
            return col
    return None


def make_chart(df: pd.DataFrame, title: str = "", prefer_numeric=None):
    if df is None or df.empty:
        return None

    if len(df) == 1 and df.shape[1] == 1:
        return None

    if prefer_numeric is None:
        prefer_numeric = ["rate_percent", "rate", "percent"]

    date_col = _find_date_column(df)
    numeric_col = _find_numeric_column(
        df, exclude=[date_col] if date_col else [], prefer=prefer_numeric
    )

    if date_col and numeric_col:
        df_sorted = df.copy()
        df_sorted[date_col] = pd.to_datetime(df_sorted[date_col])
        df_sorted = df_sorted.sort_values(date_col)

        cat_col = _find_categorical_column(df, exclude=[date_col, numeric_col])
        if cat_col:
            fig = px.line(
                df_sorted, x=date_col, y=numeric_col, color=cat_col,
                title=title, markers=True,
            )
        else:
            fig = px.line(df_sorted, x=date_col, y=numeric_col, title=title, markers=True)
        return fig

    if numeric_col:
        cat_col = _find_categorical_column(df, exclude=[numeric_col])
        if cat_col:
            df_sorted = df.sort_values(numeric_col, ascending=False)
            fig = px.bar(df_sorted, x=cat_col, y=numeric_col, title=title)
            fig.update_layout(xaxis_tickangle=-30)
            return fig

    return None


def make_investigation_charts(investigation_result: dict) -> dict:
    charts = {}
    step_titles = {
        "main": "Main Result",
        "time_trend": "Trend Over Time",
        "by_category": "Breakdown by Product Category",
        "by_territory": "Breakdown by Territory",
        "sales_volume_by_territory": "Sales Volume by Territory",
        "rate_by_territory": "Rate by Territory (%)",
    }

    for step_name, step_data in investigation_result.get("steps", {}).items():
        df = step_data.get("data")
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            continue
        title = step_titles.get(step_name, step_name)
        fig = make_chart(df, title=title)
        if fig is not None:
            charts[step_name] = fig

    return charts


if __name__ == "__main__":
    from analysis import investigate

    question = "Why were returns higher in Australia than other territories in 2022?"
    result = investigate(question)

    charts = make_investigation_charts(result)
    print(f"\nGenerated {len(charts)} chart(s):")
    for name, fig in charts.items():
        print(f"  - {name}")
        filename = f"chart_{name}.html"
        fig.write_html(filename)
        print(f"    saved to {filename}")