import os
import duckdb

RAW_DIR = "data/raw"
DB_PATH = "ecom.duckdb"

def file_path(filename: str) -> str:
    return os.path.join(RAW_DIR, filename)

def main():
    con = duckdb.connect(DB_PATH)

    # Update filenames if your CSV names are different
    con.execute(f"""
        CREATE OR REPLACE TABLE orders AS
        SELECT * FROM read_csv_auto('{file_path("olist_orders_dataset.csv")}', header=True);
    """)
    con.execute(f"""
        CREATE OR REPLACE TABLE customers AS
        SELECT * FROM read_csv_auto('{file_path("olist_customers_dataset.csv")}', header=True);
    """)
    con.execute(f"""
        CREATE OR REPLACE TABLE order_items AS
        SELECT * FROM read_csv_auto('{file_path("olist_order_items_dataset.csv")}', header=True);
    """)

    con.execute("""
        CREATE OR REPLACE VIEW orders_clean AS
        SELECT
            order_id,
            customer_id,
            order_status,
            CAST(order_purchase_timestamp AS TIMESTAMP) AS purchase_ts
        FROM orders
        WHERE order_status = 'delivered'
          AND order_purchase_timestamp IS NOT NULL;
    """)

    con.execute("""
        CREATE OR REPLACE VIEW order_revenue AS
        SELECT
            order_id,
            SUM(price + freight_value) AS order_revenue
        FROM order_items
        GROUP BY order_id;
    """)

    kpis = con.execute("""
        SELECT
            COUNT(DISTINCT oc.order_id) AS total_orders,
            COUNT(DISTINCT oc.customer_id) AS total_customers,
            ROUND(SUM(orv.order_revenue), 2) AS total_revenue,
            ROUND(AVG(orv.order_revenue), 2) AS avg_order_value
        FROM orders_clean oc
        JOIN order_revenue orv ON oc.order_id = orv.order_id;
    """).df()

    print("\n=== FIRST KPI CHECK ===")
    print(kpis.to_string(index=False))

    con.close()

if __name__ == "__main__":
    main()
