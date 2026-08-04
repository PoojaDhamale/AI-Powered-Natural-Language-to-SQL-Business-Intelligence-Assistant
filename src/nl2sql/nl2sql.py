import os
import re
import streamlit as st
import pandas as pd
from groq import Groq
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

from schema_context import SCHEMA_CONTEXT

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise RuntimeError(
        "GROQ_API_KEY not found. Please set it in Streamlit Secrets or your .env file."
    )

DATABASE_URL = st.secrets.get("connections", {}).get("postgresql", {}).get("url")

if not DATABASE_URL:
    DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Please provide it in your Streamlit Secrets block or .env file."
    )


engine = create_engine(DATABASE_URL)
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

MODEL_NAME = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = f"""You are a PostgreSQL expert helping a business analyst assistant
convert natural language questions into SQL queries.

Here is the database schema you must use:

{SCHEMA_CONTEXT}

Rules:
1. Only write PostgreSQL-compatible SELECT queries. Never write INSERT, UPDATE,
   DELETE, DROP, ALTER, TRUNCATE, or any statement that modifies data or schema.
2. Only use the exact table and column names given above. Do not invent columns.
3. Always use lowercase table/column names exactly as shown.
4. When the question involves revenue, cost, or profit, you MUST join to
   product_lookup to get product_price / product_cost, since sales_data has
   no price column itself.
5. Return ONLY the raw SQL query. No explanation, no markdown code fences,
   no commentary — just the SQL statement, ending with a semicolon.
6. Return EXACTLY ONE SQL statement. Never return multiple alternative queries,
   multiple versions, or more than one SELECT statement, even if the question
   seems ambiguous — pick the single best interpretation and write one query.
7. Whenever you use an aggregate function (SUM, COUNT, AVG, MIN, MAX) alongside
   any non-aggregated column in the SELECT list, you MUST include a GROUP BY
   clause listing every one of those non-aggregated columns. This applies to
   EACH SELECT block individually, including each side of a UNION or UNION ALL —
   do not forget GROUP BY just because the query has multiple parts.
"""


def generate_sql(question: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Question: {question}\n\nWrite the SQL query."},
        ],
    )
    sql = response.choices[0].message.content.strip()
    sql = re.sub(r"^```sql\s*|\s*```$", "", sql.strip(), flags=re.IGNORECASE | re.MULTILINE)
    sql = sql.strip()

    if ";" in sql:
        first_statement = sql.split(";")[0].strip()
        if first_statement:
            sql = first_statement + ";"

    return sql


def is_safe_select(sql: str) -> bool:
    normalized = sql.strip().lower()

    if not normalized.startswith("select"):
        return False

    forbidden_keywords = [
        "insert", "update", "delete", "drop", "alter",
        "truncate", "create", "grant", "revoke", "--", ";--",
    ]
    body = normalized.rstrip(";")
    if ";" in body:
        return False

    for kw in forbidden_keywords:
        if re.search(rf"\b{kw}\b", body):
            return False

    return True


def run_query(sql: str) -> pd.DataFrame:
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        rows = result.fetchall()
        columns = result.keys()
    df = pd.DataFrame(rows, columns=columns)

    for col in df.columns:
        if df[col].dtype == object:
            converted = pd.to_numeric(df[col], errors="coerce")
            non_null_original = int(df[col].notna().sum())
            non_null_converted = int(converted.notna().sum())
            if non_null_original > 0 and non_null_converted >= non_null_original * 0.95:
                df[col] = converted

    return df


def ask(question: str):
    sql = generate_sql(question)

    if not is_safe_select(sql):
        raise ValueError(f"Generated SQL failed safety check, refusing to execute:\n{sql}")

    df = run_query(sql)
    return sql, df


if __name__ == "__main__":
    question = "What was the total revenue in 2022?"
    sql, df = ask(question)
    print(df)