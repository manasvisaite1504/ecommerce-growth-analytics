import os
import duckdb

DB_PATH = "ecom.duckdb"
OUT_DIR = "data/processed"

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    con = duckdb.connect(DB_PATH)

    df = con.execute("""
        WITH orders_clean AS (
            SELECT
                order_id,
                customer_id,
                CAST(order_purchase_timestamp AS TIMESTAMP) AS purchase_ts
            FROM orders
            WHERE order_status = 'delivered'
              AND order_purchase_timestamp IS NOT NULL
        ),
        customer_map AS (
            SELECT
                customer_id,
                customer_unique_id
            FROM customers
        ),
        order_revenue AS (
            SELECT
                order_id,
                SUM(price + freight_value) AS order_revenue
            FROM order_items
            GROUP BY order_id
        ),
        orders_enriched AS (
            SELECT
                cm.customer_unique_id,
                oc.order_id,
                oc.purchase_ts,
                orv.order_revenue
            FROM orders_clean oc
            JOIN customer_map cm ON oc.customer_id = cm.customer_id
            JOIN order_revenue orv ON oc.order_id = orv.order_id
        ),
        global_max AS (
            SELECT MAX(purchase_ts) AS max_ts FROM orders_enriched
        ),
        params AS (
            SELECT (max_ts - INTERVAL '60 days') AS cutoff_ts
            FROM global_max
        ),
        train_orders AS (
            SELECT oe.*
            FROM orders_enriched oe
            CROSS JOIN params p
            WHERE oe.purchase_ts <= p.cutoff_ts
        ),
        customer_agg AS (
            SELECT
                customer_unique_id,
                COUNT(DISTINCT order_id) AS frequency,
                SUM(order_revenue) AS monetary,
                AVG(order_revenue) AS avg_order_value,
                MIN(purchase_ts) AS first_purchase_ts,
                MAX(purchase_ts) AS last_purchase_ts
            FROM train_orders
            GROUP BY customer_unique_id
        ),
        features AS (
            SELECT
                ca.customer_unique_id,
                DATE_DIFF('day', ca.last_purchase_ts, p.cutoff_ts) AS recency_days,
                ca.frequency,
                ROUND(ca.monetary, 2) AS monetary,
                ROUND(ca.avg_order_value, 2) AS avg_order_value,
                DATE_DIFF('day', ca.first_purchase_ts, ca.last_purchase_ts) AS customer_lifetime_days,
                ca.last_purchase_ts
            FROM customer_agg ca
            CROSS JOIN params p
        ),
        next_purchase AS (
            SELECT
                f.customer_unique_id,
                MIN(oe.purchase_ts) AS next_purchase_ts
            FROM features f
            LEFT JOIN orders_enriched oe
              ON oe.customer_unique_id = f.customer_unique_id
             AND oe.purchase_ts > f.last_purchase_ts
            GROUP BY f.customer_unique_id
        )
        SELECT
            f.customer_unique_id,
            f.recency_days,
            f.frequency,
            f.monetary,
            f.avg_order_value,
            f.customer_lifetime_days,
            CASE
              WHEN np.next_purchase_ts IS NOT NULL
               AND np.next_purchase_ts <= f.last_purchase_ts + INTERVAL '60 days'
              THEN 1 ELSE 0
            END AS label_repeat_60d
        FROM features f
        LEFT JOIN next_purchase np USING(customer_unique_id);
    """).df()

    out_path = os.path.join(OUT_DIR, "churn_repeat_purchase_dataset.csv")
    df.to_csv(out_path, index=False)

    print(f"✅ Saved: {out_path}")
    print(df.head(10).to_string(index=False))
    print("\nLabel distribution:")
    print(df["label_repeat_60d"].value_counts(dropna=False))

    con.close()

if __name__ == "__main__":
    main()
