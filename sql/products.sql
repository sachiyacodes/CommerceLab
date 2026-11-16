SELECT item_id, item_name,
 COUNTIF(event_name='view_item') AS item_views,
 COUNTIF(event_name='add_to_cart') AS add_to_cart_events,
 SUM(IF(event_name='purchase' AND currency=@currency,quantity,0)) AS units_sold,
 SUM(IF(event_name='purchase' AND currency=@currency,quantity*price,0)) AS revenue
FROM `project.dataset.commercelab_events`
WHERE item_id IS NOT NULL
GROUP BY item_id,item_name ORDER BY revenue DESC;
