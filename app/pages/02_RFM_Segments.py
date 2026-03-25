import streamlit as st
import plotly.express as px
from utils import load_csv

st.title("RFM Segmentation")

rfm = load_csv("data/processed/rfm_segments.csv")

st.sidebar.header("Filters")
seg = st.sidebar.multiselect("Segments", sorted(rfm["segment"].unique()), default=sorted(rfm["segment"].unique()))
rfm_f = rfm[rfm["segment"].isin(seg)]

st.subheader("Customers by Segment")
seg_counts = rfm_f["segment"].value_counts().reset_index()
seg_counts.columns = ["segment", "customers"]

fig = px.bar(seg_counts, x="segment", y="customers")
st.plotly_chart(fig, use_container_width=True)

st.subheader("RFM Table (sample)")
st.dataframe(rfm_f.head(300), use_container_width=True)

st.download_button("Download RFM CSV", rfm_f.to_csv(index=False), "rfm_segments_filtered.csv", "text/csv")
