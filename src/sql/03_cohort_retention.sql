-- Cohort retention by month (customers who purchased again)
-- Cohort month = first purchase month

WITH orders_clean AS (
  SELECT
    customer_id,
    CAST(order_purchase_timestamp AS TIMESTAMP) AS purchase_ts
  FROM orders
  WHERE order_status = 'delivered'
    AND order_purchase_timestamp IS NOT NULL
),
first_purchase AS (
  SELECT
    customer_id,
    DATE_TRUNC('month', MIN(purchase_ts)) AS cohort_month
  FROM orders_clean
  GROUP BY customer_id
),
orders_with_cohort AS (
  SELECT
    oc.customer_id,
    fp.cohort_month,
    DATE_TRUNC('month', oc.purchase_ts) AS order_month
  FROM orders_clean oc
  JOIN first_purchase fp USING(customer_id)
),
cohort_activity AS (
  SELECT DISTINCT
    customer_id,
    cohort_month,
    order_month,
    DATE_DIFF('month', cohort_month, order_month) AS cohort_index
  FROM orders_with_cohort
)
SELECT
  cohort_month,
  cohort_index,
  COUNT(DISTINCT customer_id) AS active_customers
FROM cohort_activity
GROUP BY cohort_month, cohort_index
ORDER BY cohort_month, cohort_index;
