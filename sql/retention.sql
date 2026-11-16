WITH user_month AS (
 SELECT user_pseudo_id, DATE_TRUNC(event_date, MONTH) AS activity_month
 FROM `project.dataset.commercelab_events`
 WHERE event_name IN ('session_start','purchase') AND user_pseudo_id IS NOT NULL
 GROUP BY 1,2
), cohort AS (
 SELECT user_pseudo_id, MIN(activity_month) AS cohort_month FROM user_month GROUP BY 1
), retained AS (
 SELECT c.cohort_month, DATE_DIFF(u.activity_month,c.cohort_month,MONTH) AS month_number,
        COUNT(DISTINCT u.user_pseudo_id) AS active_users
 FROM user_month u JOIN cohort c USING(user_pseudo_id)
 GROUP BY 1,2
), sizes AS (SELECT cohort_month, COUNT(*) AS cohort_size FROM cohort GROUP BY 1)
SELECT r.*, s.cohort_size, SAFE_DIVIDE(active_users,cohort_size) AS retention_rate
FROM retained r JOIN sizes s USING(cohort_month) ORDER BY cohort_month, month_number;
