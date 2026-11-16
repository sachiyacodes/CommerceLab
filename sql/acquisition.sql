-- Attribution caveat: public sample source/medium is first-user traffic_source, not session source.
SELECT channel, COUNT(DISTINCT session_id) AS sessions,
  COUNT(DISTINCT IF(event_name='purchase' AND currency=@currency, transaction_id, NULL)) AS orders,
  SUM(IF(event_name='purchase' AND currency=@currency, quantity*price, 0)) AS revenue,
  SAFE_DIVIDE(COUNT(DISTINCT IF(event_name='purchase' AND currency=@currency, transaction_id, NULL)), COUNT(DISTINCT session_id)) AS order_per_session
FROM `project.dataset.commercelab_events`
GROUP BY channel ORDER BY revenue DESC;
