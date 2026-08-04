import pandas as pd
from nl2sql import ask

TEST_QUESTIONS = [
    "How many customers are there in total?",
    "How many customers are homeowners?",
    "What is the average annual income of customers?",
    "What was the total revenue in 2022?",
    "How many returns were there in 2021?",
    "What is the average annual income of customers with a Bachelors education level?",
    "What are the top 5 products by revenue in 2021?",
    "Which product category had the highest revenue in 2021?",
    "Which territory had the most returns in 2022?",
    "Which product subcategory had the highest revenue in 2020?",
    "Do married customers spend more on average than single customers?",
    "What were the top 5 best-selling products last year?",
    "What is the most common payment method used by customers?",
    "What is the best product?",
]


def run_evaluation():
    results = []

    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n[{i}/{len(TEST_QUESTIONS)}] {question}")
        row = {"question": question, "sql": None, "status": None, "row_count": None, "error": None}

        try:
            sql, df = ask(question)
            row["sql"] = sql
            row["status"] = "success"
            row["row_count"] = len(df)
            print(f"  -> success, {len(df)} row(s) returned")
        except Exception as e:
            row["status"] = "failed"
            row["error"] = str(e)[:200]
            print(f"  -> FAILED: {row['error']}")

        results.append(row)

    df_results = pd.DataFrame(results)

    total = len(df_results)
    succeeded = (df_results["status"] == "success").sum()
    failed = total - succeeded

    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Total questions: {total}")
    print(f"Succeeded (ran without error): {succeeded} ({succeeded/total*100:.1f}%)")
    print(f"Failed (errored or rejected): {failed} ({failed/total*100:.1f}%)")

    df_results.to_csv("evaluation_results.csv", index=False)
    print("\nFull results saved to evaluation_results.csv")

    return df_results


if __name__ == "__main__":
    run_evaluation()