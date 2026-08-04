import pandas as pd
from groq import Groq
import os
from dotenv import load_dotenv

from nl2sql import ask, client, MODEL_NAME

load_dotenv()


def investigate(question: str) -> dict:
    results = {"question": question, "steps": {}}

    try:
        sql_main, df_main = ask(question)
        results["steps"]["main"] = {"sql": sql_main, "data": df_main}
    except Exception as e:
        results["steps"]["main"] = {"error": str(e)}
        df_main = pd.DataFrame()

    trend_question = (
        f"For the same underlying metric and filters as this question: '{question}', "
        f"break the result down by month (use DATE_TRUNC('month', order_date) or "
        f"DATE_TRUNC('month', return_date) as appropriate), ordered chronologically."
    )
    try:
        sql_trend, df_trend = ask(trend_question)
        results["steps"]["time_trend"] = {"sql": sql_trend, "data": df_trend}
    except Exception as e:
        results["steps"]["time_trend"] = {"error": str(e)}
        df_trend = pd.DataFrame()

    category_question = (
        f"For the same underlying metric and filters as this question: '{question}', "
        f"break the result down by product category_name, ordered from highest to lowest."
    )
    try:
        sql_category, df_category = ask(category_question)
        results["steps"]["by_category"] = {"sql": sql_category, "data": df_category}
    except Exception as e:
        results["steps"]["by_category"] = {"error": str(e)}
        df_category = pd.DataFrame()

    territory_question = (
        f"For the same underlying metric and filters as this question: '{question}', "
        f"break the result down by territory region, ordered from highest to lowest."
    )
    try:
        sql_territory, df_territory = ask(territory_question)
        results["steps"]["by_territory"] = {"sql": sql_territory, "data": df_territory}
    except Exception as e:
        results["steps"]["by_territory"] = {"error": str(e)}
        df_territory = pd.DataFrame()

    volume_question = (
        f"For the same time period as this question: '{question}', calculate the "
        f"total order_quantity (units sold) from sales_data, broken down by "
        f"territory region, ordered from highest to lowest."
    )
    try:
        sql_volume, df_volume = ask(volume_question)
        results["steps"]["sales_volume_by_territory"] = {"sql": sql_volume, "data": df_volume}
    except Exception as e:
        results["steps"]["sales_volume_by_territory"] = {"error": str(e)}
        df_volume = pd.DataFrame()

    df_rate = compute_rate(df_territory, df_volume)
    results["steps"]["rate_by_territory"] = {"data": df_rate}

    explanation = generate_insight(question, df_main, df_trend, df_category, df_territory, df_rate)
    results["explanation"] = explanation

    return results


def compute_rate(df_metric: pd.DataFrame, df_volume: pd.DataFrame) -> pd.DataFrame:
    if df_metric.empty or df_volume.empty:
        return pd.DataFrame()

    if "region" not in df_metric.columns or "region" not in df_volume.columns:
        return pd.DataFrame()

    metric_numeric_cols = [c for c in df_metric.columns if pd.api.types.is_numeric_dtype(df_metric[c])]
    volume_numeric_cols = [c for c in df_volume.columns if pd.api.types.is_numeric_dtype(df_volume[c])]

    if not metric_numeric_cols or not volume_numeric_cols:
        return pd.DataFrame()

    metric_col = metric_numeric_cols[0]
    volume_col = volume_numeric_cols[0]

    merged = df_metric[["region", metric_col]].merge(
        df_volume[["region", volume_col]], on="region", how="inner"
    )
    if merged.empty:
        return pd.DataFrame()

    merged["rate_percent"] = (merged[metric_col] / merged[volume_col] * 100).round(2)
    merged = merged.sort_values("rate_percent", ascending=False)
    return merged


def generate_insight(question, df_main, df_trend, df_category, df_territory, df_rate=None) -> str:
    context_parts = [f"Original question: {question}\n"]

    if not df_main.empty:
        context_parts.append(f"Main result:\n{df_main.to_string(index=False)}\n")
    if not df_trend.empty:
        context_parts.append(f"Monthly breakdown:\n{df_trend.to_string(index=False)}\n")
    if not df_category.empty:
        context_parts.append(f"Breakdown by product category:\n{df_category.to_string(index=False)}\n")
    if not df_territory.empty:
        context_parts.append(f"Breakdown by territory:\n{df_territory.to_string(index=False)}\n")
    if df_rate is not None and not df_rate.empty:
        context_parts.append(
            f"Rate per territory (metric value as a % of units sold -- this is a "
            f"FAIRER comparison than raw counts, since it accounts for territories "
            f"having different sales volumes):\n{df_rate.to_string(index=False)}\n"
        )

    data_context = "\n".join(context_parts)

    insight_prompt = f"""You are a business analyst. Based ONLY on the data below
(do not invent numbers not shown here), write a short, clear explanation
(3-5 sentences) answering the original question. Where possible, cite specific
numbers from the data to support your explanation.

IMPORTANT: If a "rate per territory" table is provided, prefer reasoning from
the RATE (percentage) rather than the raw count, since raw counts are naturally
higher for territories with more sales volume. A high raw count with an average
or low rate suggests the difference is just due to sales volume, not an actual
underlying problem -- point this out if it's the case.

If the data doesn't fully explain the "why", say what the data shows and what
it suggests, without overclaiming certainty.

{data_context}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0.3,
        messages=[
            {"role": "user", "content": insight_prompt},
        ],
    )
    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    question = "Why were returns higher in Australia than other territories in 2022?"
    result = investigate(question)

    print("\n" + "=" * 60)
    print("FINAL EXPLANATION:")
    print("=" * 60)
    print(result["explanation"])