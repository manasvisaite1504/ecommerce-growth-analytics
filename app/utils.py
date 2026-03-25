import duckdb
import pandas as pd

DB_PATH = "ecom.duckdb"

def get_kpis():
    con = duckdb.connect(DB_PATH)

    kpi_df = con.execute("""
        WITH orders_clean AS (
            SELECT order_id, customer_id
            FROM orders
            WHERE order_status='delivered'
        ),
        order_revenue AS (
            SELECT order_id, SUM(price + freight_value) AS revenue
            FROM order_items
            GROUP BY order_id
        )
        SELECT
            COUNT(DISTINCT oc.order_id) AS total_orders,
            COUNT(DISTINCT oc.customer_id) AS total_customers,
            ROUND(SUM(orv.revenue),2) AS total_revenue,
            ROUND(AVG(orv.revenue),2) AS avg_order_value
        FROM orders_clean oc
        JOIN order_revenue orv ON oc.order_id = orv.order_id;
    """).df()

    trend_df = con.execute("""
        WITH orders_clean AS (
            SELECT
                order_id,
                CAST(order_purchase_timestamp AS TIMESTAMP) AS purchase_ts
            FROM orders
            WHERE order_status='delivered'
              AND order_purchase_timestamp IS NOT NULL
        ),
        order_revenue AS (
            SELECT order_id, SUM(price + freight_value) AS revenue
            FROM order_items
            GROUP BY order_id
        )
        SELECT
            DATE_TRUNC('month', oc.purchase_ts) AS month,
            COUNT(DISTINCT oc.order_id) AS orders,
            ROUND(SUM(orv.revenue),2) AS revenue
        FROM orders_clean oc
        JOIN order_revenue orv ON oc.order_id = orv.order_id
        GROUP BY 1
        ORDER BY 1;
    """).df()

    con.close()
    return kpi_df.iloc[0].to_dict(), trend_df

def load_csv(path):
    return pd.read_csv(path)
