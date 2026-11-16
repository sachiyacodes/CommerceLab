-- CommerceLab's normalized event grain is one row per event-item pair. An event without items
-- remains one row with NULL item fields. Source attribution uses GA4's first-user traffic_source.
SELECT
  PARSE_DATE('%Y%m%d', event_date) AS event_date,
  TIMESTAMP_MICROS(event_timestamp) AS event_timestamp,
  event_name, user_pseudo_id,
  CONCAT(COALESCE(user_pseudo_id, 'unknown'), '.', COALESCE(CAST((SELECT p.value.int_value FROM UNNEST(event_params) p WHERE p.key='ga_session_id') AS STRING), 'no_session')) AS session_id,
  traffic_source.source AS source,
  traffic_source.medium AS medium,
  CASE
    WHEN traffic_source.medium = 'organic' THEN 'Organic Search'
    WHEN traffic_source.medium IN ('cpc','ppc','paidsearch') THEN 'Paid Search'
    WHEN traffic_source.medium = 'email' THEN 'Email'
    WHEN traffic_source.medium = 'affiliate' THEN 'Affiliates'
    WHEN traffic_source.medium IN ('social','organic_social') THEN 'Social'
    WHEN traffic_source.source = '(direct)' OR traffic_source.source IS NULL THEN 'Direct'
    ELSE 'Referral / Other'
  END AS channel,
  geo.country AS country, device.category AS device_category,
  ecommerce.transaction_id AS transaction_id,
  item.item_id, item.item_name, COALESCE(item.quantity, 0) AS quantity,
  COALESCE(item.price, 0) AS price,
  COALESCE((SELECT p.value.string_value FROM UNNEST(event_params) p WHERE p.key='currency'), 'Unknown') AS currency
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*` e
LEFT JOIN UNNEST(e.items) item
WHERE _TABLE_SUFFIX BETWEEN @start_date AND @end_date;
