import os
import duckdb
import pandas as pd

DB_PATH = "ecom.duckdb"
OUT_DIR = "data/processed"

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    con = duckdb.connect(DB_PATH)

    # customer-level RFM using delivered orders + order revenue
    rfm = con.execute("""
        WITH orders_clean AS (
            SELECT
                order_id,
                customer_id,
                CAST(order_purchase_timestamp AS TIMESTAMP) AS purchase_ts
            FROM orders
            WHERE order_status = 'delivered'
              AND order_purchase_timestamp IS NOT NULL
        ),
        order_revenue AS (
            SELECT
                order_id,
                SUM(price + freight_value) AS order_revenue
            FROM order_items
            GROUP BY order_id
        ),
        customer_orders AS (
            SELECT
                oc.customer_id,
                COUNT(DISTINCT oc.order_id) AS frequency,
                SUM(orv.order_revenue) AS monetary,
                MAX(oc.purchase_ts) AS last_purchase_ts
            FROM orders_clean oc
            JOIN order_revenue orv ON oc.order_id = orv.order_id
            GROUP BY oc.customer_id
        ),
        ref AS (
            SELECT MAX(CAST(order_purchase_timestamp AS TIMESTAMP)) AS ref_date
            FROM orders
            WHERE order_status = 'delivered'
              AND order_purchase_timestamp IS NOT NULL
        )
        SELECT
            co.customer_id,
            DATE_DIFF('day', co.last_purchase_ts, ref.ref_date) AS recency_days,
            co.frequency,
            ROUND(co.monetary, 2) AS monetary
        FROM customer_orders co
        CROSS JOIN ref
    """).df()

    # Simple segment rules (easy + explainable)
    def segment(row):
        r, f, m = row["recency_days"], row["frequency"], row["monetary"]
        if f >= 3 and r <= 60 and m >= 500:
            return "Champions"
        if f >= 2 and r <= 90:
            return "Loyal"
        if r <= 60 and f == 1:
            return "New Customers"
        if r > 180 and f >= 2:
            return "At Risk"
        if r > 180 and f == 1:
            return "Lost"
        return "Potential Loyalist"

    rfm["segment"] = rfm.apply(segment, axis=1)

    out_path = os.path.join(OUT_DIR, "rfm_segments.csv")
    rfm.to_csv(out_path, index=False)

    print(f"✅ Saved: {out_path}")
    print(rfm.head(10).to_string(index=False))

    con.close()

if __name__ == "__main__":
    main()
