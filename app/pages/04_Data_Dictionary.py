import streamlit as st
import pandas as pd

st.title("Data Dictionary")

rows = [
    ("cohort_retention_monthly.csv", "cohort_month", "Month of first purchase for a cohort"),
    ("cohort_retention_monthly.csv", "cohort_index", "Months since first purchase (0 = cohort month)"),
    ("cohort_retention_monthly.csv", "active_customers", "Number of active customers in that cohort/month"),
    ("rfm_segments.csv", "recency_days", "Days since last purchase (lower = more recent)"),
    ("rfm_segments.csv", "frequency", "Number of orders per customer"),
    ("rfm_segments.csv", "monetary", "Total customer spend"),
    ("rfm_segments.csv", "segment", "Rule-based segment label (Champions/Loyal/etc.)"),
    ("churn_repeat_purchase_dataset.csv", "label_repeat_60d", "1 if customer repurchased within 60 days, else 0"),
]

df = pd.DataFrame(rows, columns=["File", "Column", "Meaning"])
st.dataframe(df, use_container_width=True)
