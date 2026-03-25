import streamlit as st
import plotly.express as px
import pandas as pd
from utils import load_csv

st.title("Cohort Retention")

cohort = load_csv("data/processed/cohort_retention_monthly.csv")

st.sidebar.header("Filters")

min_index = int(cohort["cohort_index"].min())
max_index = int(cohort["cohort_index"].max())

if max_index > min_index:
    max_show = st.sidebar.slider(
        "Max months since first purchase",
        min_value=min_index,
        max_value=max_index,
        value=min(12, max_index)
    )
    cohort = cohort[cohort["cohort_index"] <= max_show]
else:
    st.sidebar.info("Only cohort month (index 0) available right now.")

# Pivot for heatmap
heat = cohort.pivot(index="cohort_month", columns="cohort_index", values="active_customers").fillna(0)
heat.index = heat.index.astype(str)

# Retention %
cohort_sizes = heat[min_index].replace(0, pd.NA)  # usually heat[0]
retention = (heat.div(cohort_sizes, axis=0) * 100).fillna(0)

st.subheader("Retention Heatmap (%)")
fig = px.imshow(
    retention,
    labels=dict(x="Months since first purchase", y="Cohort month", color="Retention %"),
    aspect="auto"
)
st.plotly_chart(fig, use_container_width=True)

with st.expander("Download cohort tables"):
    st.download_button("Download cohort counts CSV", cohort.to_csv(index=False), "cohort_counts.csv", "text/csv")
    st.download_button("Download retention % CSV", retention.reset_index().to_csv(index=False), "cohort_retention_pct.csv", "text/csv")

st.subheader("Raw Cohort Data")
st.dataframe(cohort, use_container_width=True)
