WITH counts AS (
 SELECT event_name, COUNT(DISTINCT user_pseudo_id) AS users
 FROM `project.dataset.commercelab_events`
 WHERE event_name IN ('session_start','view_item','add_to_cart','begin_checkout','purchase')
 GROUP BY event_name
), stages AS (
 SELECT 'session_start' AS event_name, 1 AS stage_order UNION ALL
 SELECT 'view_item',2 UNION ALL SELECT 'add_to_cart',3 UNION ALL
 SELECT 'begin_checkout',4 UNION ALL SELECT 'purchase',5
)
SELECT s.event_name, s.stage_order, COALESCE(c.users,0) AS users,
 SAFE_DIVIDE(COALESCE(c.users,0), LAG(COALESCE(c.users,0)) OVER (ORDER BY stage_order)) AS conversion_from_previous_stage
FROM stages s LEFT JOIN counts c USING(event_name)
ORDER BY stage_order;
-- Unique-user stage counts are descriptive and not proof that users followed that ordered path.
