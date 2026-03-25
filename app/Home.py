import streamlit as st
import plotly.express as px
from utils import get_kpis

st.set_page_config(page_title="E-commerce Analytics + ML", layout="wide")
st.title("E-commerce Growth Analytics Suite")
st.caption("KPIs • Cohort Retention • RFM Segments • Churn Risk")

kpis, trend = get_kpis()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Orders", f"{int(kpis['total_orders']):,}")
c2.metric("Total Customers", f"{int(kpis['total_customers']):,}")
c3.metric("Total Revenue", f"{kpis['total_revenue']:,.2f}")
c4.metric("Avg Order Value", f"{kpis['avg_order_value']:.2f}")

st.subheader("Revenue & Orders Trend (Monthly)")
fig1 = px.line(trend, x="month", y="revenue", markers=True)
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.bar(trend, x="month", y="orders")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("So what? (Insights & Recommendations)")
st.markdown("""
- Identify high-value segments (RFM) and create targeted retention campaigns.
- Use cohort retention to measure whether customers return after first purchase.
- Monitor churn risk list (top probability) for proactive outreach.
""")
