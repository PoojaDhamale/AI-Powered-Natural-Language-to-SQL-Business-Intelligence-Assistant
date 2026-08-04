import matplotlib
matplotlib.use('Agg')
import streamlit as st
import pandas as pd

from nl2sql import ask
from analysis import investigate
from visualize import make_chart, make_investigation_charts

st.set_page_config(
    page_title="AI-Powered NL2SQL Business Intelligence Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #f5f7ff;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; max-width: 100% !important; }

.hero {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4338ca 75%, #6d28d9 100%);
    border-radius: 0 0 28px 28px;
    padding: 3rem 3.5rem 2.8rem;
    margin-bottom: 2.2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute; top: -60px; right: -60px;
    width: 320px; height: 320px;
    background: radial-gradient(circle, rgba(167,139,250,0.18) 0%, transparent 70%);
    border-radius: 50%;
}
.hero::after {
    content: '';
    position: absolute; bottom: -40px; left: 30%;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-eyebrow {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #a5b4fc;
    margin-bottom: 0.6rem;
}
.hero-title {
    font-size: 2.5rem;
    font-weight: 800;
    line-height: 1.18;
    color: #ffffff;
    margin-bottom: 0.75rem;
}
.hero-title span { color: #a5b4fc; }
.hero-subtitle {
    font-size: 1.05rem;
    font-weight: 400;
    color: #c7d2fe;
    max-width: 660px;
    line-height: 1.65;
    margin-bottom: 1.5rem;
}
.badge-row { display: flex; flex-wrap: wrap; gap: 8px; }
.badge {
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.22);
    color: #e0e7ff;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.76rem;
    font-weight: 500;
    backdrop-filter: blur(6px);
}

.section-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #1e1b4b;
    margin-bottom: 0.2rem;
}
.section-sub {
    font-size: 0.85rem;
    color: #6b7280;
    margin-bottom: 1.2rem;
}

.about-card {
    background: #ffffff;
    border: 1px solid #e0e7ff;
    border-radius: 16px;
    padding: 1.4rem 1.5rem;
    height: 100%;
    box-shadow: 0 2px 12px rgba(99,102,241,0.07);
    transition: box-shadow 0.2s;
}
.about-card:hover { box-shadow: 0 6px 24px rgba(99,102,241,0.14); }
.about-card-icon {
    font-size: 1.9rem;
    margin-bottom: 0.6rem;
    display: block;
}
.about-card-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #1e1b4b;
    margin-bottom: 0.45rem;
}
.about-card-text {
    font-size: 0.83rem;
    color: #4b5563;
    line-height: 1.65;
}
.about-card-text b { color: #4338ca; }

.steps-row { display: flex; gap: 0; margin-bottom: 2rem; }
.step {
    flex: 1;
    background: #ffffff;
    border: 1px solid #e0e7ff;
    padding: 1.1rem 1.2rem;
    position: relative;
    box-shadow: 0 1px 6px rgba(99,102,241,0.06);
}
.step:first-child { border-radius: 14px 0 0 14px; }
.step:last-child  { border-radius: 0 14px 14px 0; }
.step-num {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: #a5b4fc;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}
.step-icon { font-size: 1.4rem; margin-bottom: 0.3rem; display: block; }
.step-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: #1e1b4b;
    margin-bottom: 0.2rem;
}
.step-desc { font-size: 0.77rem; color: #6b7280; line-height: 1.5; }
.step-arrow {
    position: absolute; right: -13px; top: 50%;
    transform: translateY(-50%);
    width: 26px; height: 26px;
    background: #4338ca;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    color: white; font-size: 0.8rem;
    z-index: 2;
    box-shadow: 0 2px 8px rgba(67,56,202,0.3);
}

.pill-direct {
    display: inline-flex; align-items: center; gap: 6px;
    background: #ecfdf5; color: #065f46;
    border: 1px solid #6ee7b7;
    border-radius: 30px; padding: 5px 16px;
    font-size: 0.78rem; font-weight: 600;
    margin-bottom: 1rem;
}
.pill-invest {
    display: inline-flex; align-items: center; gap: 6px;
    background: #fef9c3; color: #854d0e;
    border: 1px solid #fde047;
    border-radius: 30px; padding: 5px 16px;
    font-size: 0.78rem; font-weight: 600;
    margin-bottom: 1rem;
}

.answer-header {
    font-size: 1.05rem;
    font-weight: 700;
    color: #1e1b4b;
    margin-bottom: 0.8rem;
    display: flex; align-items: center; gap: 8px;
}
.insight-card {
    background: linear-gradient(135deg, #f0f4ff 0%, #faf5ff 100%);
    border-left: 5px solid #6366f1;
    border-radius: 0 14px 14px 0;
    padding: 1.2rem 1.6rem;
    font-size: 0.96rem;
    line-height: 1.75;
    color: #1e1b4b;
    margin-bottom: 1.2rem;
    box-shadow: 0 2px 10px rgba(99,102,241,0.08);
}

section[data-testid="stSidebar"] {
    background: #1e1b4b !important;
}
section[data-testid="stSidebar"] * { color: #e0e7ff !important; }
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(165,180,252,0.25) !important;
    color: #c7d2fe !important;
    border-radius: 10px !important;
    font-size: 0.78rem !important;
    text-align: left !important;
    padding: 7px 12px !important;
    margin-bottom: 2px !important;
    transition: background 0.18s !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(165,180,252,0.18) !important;
    border-color: #a5b4fc !important;
    color: #ffffff !important;
}
.sidebar-cat {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #818cf8 !important;
    margin: 1rem 0 0.4rem;
    padding-left: 2px;
}
.sidebar-brand {
    font-size: 1rem;
    font-weight: 700;
    color: #ffffff !important;
    margin-bottom: 0.1rem;
}
.sidebar-tagline {
    font-size: 0.75rem;
    color: #a5b4fc !important;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

QUESTIONS_CHART = [
    "What are the top 5 products by revenue in 2021?",
    "Show monthly revenue trend for 2022",
    "Which territory had the most returns in 2022?",
    "Show revenue by product category for all years",
    "What are the top 5 best-selling products last year?",
    "Show monthly returns trend in 2021",
    "Which product subcategory had the highest revenue in 2020?",
]
QUESTIONS_SCALAR = [
    "What was the total revenue in 2022?",
    "How many customers are homeowners?",
    "What is the average annual income of customers?",
    "How many returns were there in 2021?",
    "How many orders were placed in 2020?",
]
QUESTIONS_WHY = [
    "Why were returns higher in Australia than other territories in 2022?",
    "Why did returns increase in 2022 compared to 2021?",
    "Explain why Bikes dominate revenue compared to other categories",
]
QUESTIONS_COMPARE = [
    "Do married customers spend more on average than single customers?",
    "Which gender has a higher average annual income?",
    "Compare revenue between 2021 and 2022",
]

WHY_KEYWORDS = ["why", "reason", "cause", "explain"]

def is_investigation_question(q: str) -> bool:
    return any(kw in q.lower() for kw in WHY_KEYWORDS)

with st.sidebar:
    st.markdown('<div class="sidebar-brand">📊 NL2SQL BI Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">Click any question to load it →</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<div class="sidebar-cat">📈 Chart & Trend Questions</div>', unsafe_allow_html=True)
    for q in QUESTIONS_CHART:
        if st.button(q, key=f"c_{q}", width="stretch"):
            st.session_state["q_input"] = q

    st.markdown('<div class="sidebar-cat">🔢 Single-Value Questions</div>', unsafe_allow_html=True)
    for q in QUESTIONS_SCALAR:
        if st.button(q, key=f"s_{q}", width="stretch"):
            st.session_state["q_input"] = q

    st.markdown('<div class="sidebar-cat">🔍 "Why" Investigation Questions</div>', unsafe_allow_html=True)
    for q in QUESTIONS_WHY:
        if st.button(q, key=f"w_{q}", width="stretch"):
            st.session_state["q_input"] = q

    st.markdown('<div class="sidebar-cat">⚖️ Comparison Questions</div>', unsafe_allow_html=True)
    for q in QUESTIONS_COMPARE:
        if st.button(q, key=f"x_{q}", width="stretch"):
            st.session_state["q_input"] = q

st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">🎓 AI / Data Analytics Portfolio Project</div>
  <div class="hero-title">AI-Powered <span>Natural Language to SQL</span><br>Business Intelligence Assistant</div>
  <div class="hero-subtitle">
    Ask any business question in plain English — the assistant converts it to SQL,
    runs it on a live PostgreSQL database, and returns answers, charts, and
    AI-written explanations. No SQL knowledge required.
  </div>
  <div class="badge-row">
    <span class="badge">🤖 LLaMA 3.3-70B via Groq</span>
    <span class="badge">🐘 PostgreSQL</span>
    <span class="badge">📅 AdventureWorks 2020–2022</span>
    <span class="badge">🛡️ SQL Safety Validated</span>
    <span class="badge">📈 Auto-Visualised with Plotly</span>
    <span class="badge">🔍 Multi-Step Investigation Engine</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">About This Project</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">What it does, what data it uses, and what makes it unique.</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
<div class="about-card">
  <span class="about-card-icon">🧠</span>
  <div class="about-card-title">Natural Language → SQL Pipeline</div>
  <div class="about-card-text">
    Type a business question in plain English. The app sends it to
    <b>LLaMA 3.3-70B</b> (via Groq API) along with the full database schema,
    receives a valid PostgreSQL query, runs a <b>safety check</b> to block
    any destructive statements, then executes it live against the database.
  </div>
</div>
""", unsafe_allow_html=True)

with col2:
    st.markdown("""
<div class="about-card">
  <span class="about-card-icon">🗄️</span>
  <div class="about-card-title">The Data</div>
  <div class="about-card-text">
    Built on the <b>AdventureWorks</b> bicycle & outdoor equipment dataset
    (2020–2022). Contains <b>8 relational tables</b>: Dates, Sales, Returns, Customers,
    Products, Subcategories, Categories, and Territories — covering revenue,
    profitability, customer demographics, and regional performance.
  </div>
</div>
""", unsafe_allow_html=True)

with col3:
    st.markdown("""
<div class="about-card">
  <span class="about-card-icon">🔍</span>
  <div class="about-card-title">"Why" Investigation Engine</div>
  <div class="about-card-text">
    For <b>"why" questions</b>, a structured investigation runs automatically:
    5 breakdown queries (time-trend, category, territory, sales volume) +
    a <b>normalized rate comparison</b> to account for volume differences +
    an <b>LLM-synthesized plain-English explanation</b> grounded in the actual
    query results.
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<div class="section-title">How It Works</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Five steps from your question to a chart-backed answer.</div>', unsafe_allow_html=True)

st.markdown("""
<div class="steps-row">
  <div class="step">
    <div class="step-num">Step 01</div>
    <span class="step-icon">✍️</span>
    <div class="step-title">You Ask</div>
    <div class="step-desc">Type any business question in plain English — no SQL needed.</div>
    <div class="step-arrow">→</div>
  </div>
  <div class="step">
    <div class="step-num">Step 02</div>
    <span class="step-icon">🤖</span>
    <div class="step-title">LLM Generates SQL</div>
    <div class="step-desc">LLaMA 3.3-70B converts the question into a valid PostgreSQL query using schema context.</div>
    <div class="step-arrow">→</div>
  </div>
  <div class="step">
    <div class="step-num">Step 03</div>
    <span class="step-icon">🛡️</span>
    <div class="step-title">Safety Check</div>
    <div class="step-desc">Code-level guard blocks INSERT, DELETE, DROP and any destructive operations.</div>
    <div class="step-arrow">→</div>
  </div>
  <div class="step">
    <div class="step-num">Step 04</div>
    <span class="step-icon">🐘</span>
    <div class="step-title">PostgreSQL Executes</div>
    <div class="step-desc">The validated query runs against the live AdventureWorks database.</div>
    <div class="step-arrow">→</div>
  </div>
  <div class="step">
    <div class="step-num">Step 05</div>
    <span class="step-icon">📊</span>
    <div class="step-title">Results + Charts</div>
    <div class="step-desc">Data is auto-visualised as bar or line charts. "Why" questions get an AI explanation.</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.divider()

st.markdown('<div class="section-title">Ask a Business Question</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Use the sidebar to load a sample, or type your own below.</div>', unsafe_allow_html=True)

col_in, col_btn = st.columns([5, 1])
with col_in:
    question = st.text_input(
        label="🔎 Your Question",
        key="q_input",
        placeholder="e.g.  What are the top 5 products by revenue in 2021?   |   Why were returns higher in Australia?",
    )
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    ask_clicked = st.button("Ask  ➜", type="primary", width="stretch")

if ask_clicked and question.strip():
    investigation_mode = is_investigation_question(question)

    if investigation_mode:
        st.markdown('<span class="pill-invest">🔍 Investigation Mode — multi-step analysis</span>',
                    unsafe_allow_html=True)
        st.info(
            "**'Why' question detected** — running a full investigation: "
            "5 SQL queries + normalized rate comparison + AI-written explanation. "
            "This takes **20–40 seconds**.",
            icon="⏳",
        )

        with st.spinner("Running investigation queries…"):
            try:
                result = investigate(question)
                charts = make_investigation_charts(result)
            except Exception as e:
                st.error(f"Investigation failed: {e}")
                st.stop()

        st.markdown('<div class="answer-header">💡 AI Explanation</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="insight-card">{result["explanation"]}</div>',
            unsafe_allow_html=True,
        )

        st.divider()
        st.markdown('<div class="answer-header">📂 Supporting Data & Charts</div>', unsafe_allow_html=True)

        step_labels = {
            "main":                      ("📌 Main Result",                                    True),
            "time_trend":                ("📅 Trend Over Time",                                False),
            "by_category":               ("🏷️ Breakdown by Product Category",                  False),
            "by_territory":              ("🌍 Breakdown by Territory",                          False),
            "sales_volume_by_territory": ("📦 Sales Volume by Territory",                      False),
            "rate_by_territory":         ("📊 Return Rate by Territory — normalized (% of sales)", True),
        }

        for step_name, step_data in result["steps"].items():
            label, default_open = step_labels.get(step_name, (step_name, False))
            with st.expander(label, expanded=default_open):
                if "error" in step_data:
                    st.warning(f"This step failed: {step_data['error']}")
                    continue
                df  = step_data.get("data")
                sql = step_data.get("sql")
                if sql:
                    st.code(sql, language="sql")
                if df is not None and not df.empty:
                    st.dataframe(df, width="stretch")
                if step_name in charts:
                    fig = charts[step_name]
                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(248,250,255,1)",
                        font=dict(family="Inter"),
                    )
                    st.plotly_chart(fig, width="stretch")

    else:
        st.markdown('<span class="pill-direct">⚡ Direct Query Mode</span>', unsafe_allow_html=True)

        with st.spinner("Generating SQL and fetching results…"):
            try:
                sql, df = ask(question)
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.stop()

        st.markdown('<div class="answer-header">📋 Answer</div>', unsafe_allow_html=True)

        if df.empty:
            st.warning("The query ran successfully but returned no rows.")

        elif df.shape == (1, 1):
            value = df.iloc[0, 0]
            formatted = (
                f"{value:,.2f}" if isinstance(value, float)
                else f"{value:,}"  if isinstance(value, int)
                else str(value)
            )
            st.metric(label=df.columns[0].replace("_", " ").title(), value=formatted)

        elif df.shape[0] == 1:
            cols = st.columns(min(len(df.columns), 4))
            for i, col_name in enumerate(df.columns):
                val = df.iloc[0, i]
                formatted = (
                    f"{val:,.2f}" if isinstance(val, float)
                    else f"{val:,}"  if isinstance(val, int)
                    else str(val)
                )
                cols[i % 4].metric(label=col_name.replace("_", " ").title(), value=formatted)

        else:
            st.dataframe(df, width="stretch")
            fig = make_chart(df, title=question)
            if fig is not None:
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(248,250,255,1)",
                    font=dict(family="Inter"),
                    title_font=dict(family="Inter", size=14, color="#1e1b4b"),
                )
                st.plotly_chart(fig, width="stretch")

        with st.expander("🔎 View Generated SQL", expanded=False):
            st.code(sql, language="sql")

elif ask_clicked:
    st.warning("Please type a question before clicking Ask.")