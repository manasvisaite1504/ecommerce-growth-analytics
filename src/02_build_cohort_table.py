import os
import duckdb

DB_PATH = "ecom.duckdb"
OUT_DIR = "data/processed"
SQL_PATH = "/Users/manasvi15/Desktop/ecommerce-growth-analytics/src/sql/03_cohort_retention.sql"

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    con = duckdb.connect(DB_PATH)

    with open(SQL_PATH, "r", encoding="utf-8") as f:
        cohort_sql = f.read()

    cohort_df = con.execute(cohort_sql).df()
    out_path = os.path.join(OUT_DIR, "cohort_retention_monthly.csv")
    cohort_df.to_csv(out_path, index=False)

    print(f"✅ Saved: {out_path}")
    print(cohort_df.head(10).to_string(index=False))

    con.close()

if __name__ == "__main__":
    main()
