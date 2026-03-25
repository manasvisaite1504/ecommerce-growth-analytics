import streamlit as st
import plotly.express as px
from utils import load_csv

st.title("Churn / Repeat Purchase Risk")

data_path = "data/processed/churn_repeat_purchase_dataset.csv"
df = load_csv(data_path)

st.subheader("Label Distribution (repeat within horizon)")
label_counts = df["label_repeat_60d"].value_counts().reset_index()
label_counts.columns = ["label", "count"]
st.dataframe(label_counts, use_container_width=True)

fig = px.bar(label_counts, x="label", y="count")
st.plotly_chart(fig, use_container_width=True)

st.caption("Next improvement: use a longer horizon (90/180 days) and create a scoring table for top at-risk customers.")

st.subheader("Modelling Dataset (sample)")
st.dataframe(df.head(300), use_container_width=True)

st.download_button("Download modelling dataset", df.to_csv(index=False), "churn_dataset.csv", "text/csv")
