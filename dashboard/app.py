"""
HR Analytics Dashboard — Streamlit app.
Reads from BigQuery fct_attrition_stats & dim_employees tables
and displays interactive visualizations.
"""

import os
import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

# ── Config ──────────────────────────────────────────────
st.set_page_config(page_title="HR Attrition Dashboard", layout="wide")

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "")
DATASET = os.environ.get("BQ_DATASET", "hr_analytics_dataset")
CREDENTIALS_PATH = os.environ.get(
    "GOOGLE_APPLICATION_CREDENTIALS", "/app/google_credentials.json"
)


@st.cache_data(ttl=600)
def load_data(table: str) -> pd.DataFrame:
    """Load a BigQuery table into a DataFrame."""
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH
    )
    client = bigquery.Client(project=PROJECT_ID, credentials=credentials)
    query = f"SELECT * FROM `{PROJECT_ID}.{DATASET}.{table}`"
    return client.query(query).to_dataframe()


# ── Load data ───────────────────────────────────────────
try:
    df_fact = load_data("fct_attrition_stats")
    df_dim = load_data("dim_employees")
    data_loaded = True
except Exception as e:
    data_loaded = False
    error_msg = str(e)

# ── Header ──────────────────────────────────────────────
st.title("📊 HR Analytics: Employee Attrition Dashboard")
st.markdown(
    "Interactive exploration of employee attrition patterns across "
    "departments, income brackets, and tenure."
)

if not data_loaded:
    st.error(f"Could not connect to BigQuery: {error_msg}")
    st.info(
        "Make sure your `google_credentials.json` is mounted and "
        "environment variables (GCP_PROJECT_ID, BQ_DATASET) are set."
    )
    st.stop()

# ── KPI Row ─────────────────────────────────────────────
total_employees = len(df_fact)
attrition_count = int(df_fact["attrition_flag"].sum())
attrition_rate = round(attrition_count / total_employees * 100, 1)

col1, col2, col3 = st.columns(3)
col1.metric("Total Employees", f"{total_employees:,}")
col2.metric("Attrition Count", f"{attrition_count:,}")
col3.metric("Attrition Rate", f"{attrition_rate}%")

st.divider()

# ── TILE 1: Attrition Rate by Department (bar chart) ───
st.subheader("📌 Tile 1 — Attrition Rate by Department")

dept_stats = (
    df_fact.groupby("department")
    .agg(total=("attrition_flag", "count"), left=("attrition_flag", "sum"))
    .reset_index()
)
dept_stats["attrition_rate_pct"] = round(dept_stats["left"] / dept_stats["total"] * 100, 1)

st.bar_chart(dept_stats, x="department", y="attrition_rate_pct", color="department")

st.caption(
    "This chart shows the percentage of employees who left in each department. "
    "Higher bars indicate departments with greater turnover risk."
)

# ── TILE 2: Attrition by Years at Company (line chart) ─
st.subheader("📌 Tile 2 — Attrition by Years at Company")

tenure_stats = (
    df_fact.groupby("years_at_company")
    .agg(total=("attrition_flag", "count"), left=("attrition_flag", "sum"))
    .reset_index()
    .sort_values("years_at_company")
)
tenure_stats["attrition_rate_pct"] = round(
    tenure_stats["left"] / tenure_stats["total"] * 100, 1
)

st.line_chart(tenure_stats, x="years_at_company", y="attrition_rate_pct")

st.caption(
    "This line chart visualizes turnover risk across the employee lifecycle. "
    "Peaks indicate critical tenure milestones where employees are most likely to leave."
)

st.divider()

# ── BONUS TILE: Income Bracket Distribution ─────────────
st.subheader("💰 Income Bracket vs Attrition")

income_stats = (
    df_dim.groupby("income_bracket")
    .agg(total=("employee_age", "count"))
    .reset_index()
)

# Merge attrition data
income_attr = (
    df_fact.assign(
        income_bracket=pd.cut(
            df_fact["monthly_income"],
            bins=[0, 5000, 10000, float("inf")],
            labels=["Entry Level", "Mid Level", "Senior Level"],
        )
    )
    .groupby("income_bracket", observed=True)
    .agg(total=("attrition_flag", "count"), left=("attrition_flag", "sum"))
    .reset_index()
)
income_attr["attrition_rate_pct"] = round(
    income_attr["left"] / income_attr["total"] * 100, 1
)

st.bar_chart(income_attr, x="income_bracket", y="attrition_rate_pct")

st.caption(
    "Employees at entry-level income brackets tend to have higher turnover rates."
)

# ── Footer ──────────────────────────────────────────────
st.divider()
st.markdown(
    "*Data Engineering Zoomcamp — Final Project | "
    "Data: IBM HR Analytics Employee Attrition Dataset*"
)
