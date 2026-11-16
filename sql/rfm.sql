WITH orders AS (
 SELECT user_pseudo_id, transaction_id, event_date, SUM(quantity*price) AS order_value
 FROM `project.dataset.commercelab_events`
 WHERE event_name='purchase' AND transaction_id IS NOT NULL AND currency=@currency
 GROUP BY user_pseudo_id,transaction_id,event_date
), base AS (
 SELECT user_pseudo_id,
        DATE_DIFF((SELECT MAX(event_date) FROM orders),MAX(event_date),DAY) AS recency_days,
        COUNT(DISTINCT transaction_id) AS frequency, SUM(order_value) AS monetary
 FROM orders GROUP BY user_pseudo_id
), threshold AS (SELECT APPROX_QUANTILES(monetary,2)[OFFSET(1)] AS median_spend FROM base)
SELECT b.*, CASE
 WHEN recency_days > 45 THEN 'At risk'
 WHEN frequency >= 2 AND monetary >= t.median_spend THEN 'Loyal value'
 WHEN frequency = 1 THEN 'New / one-time'
 ELSE 'Occasional' END AS segment
FROM base b CROSS JOIN threshold t;
