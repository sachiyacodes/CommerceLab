from __future__ import annotations

import os
import pandas as pd


QUERY = """
SELECT
  PARSE_DATE('%Y%m%d', event_date) AS event_date,
  TIMESTAMP_MICROS(event_timestamp) AS event_timestamp,
  event_name,
  user_pseudo_id,
  CAST((SELECT ep.value.int_value FROM UNNEST(event_params) ep WHERE ep.key = 'ga_session_id') AS STRING) AS raw_session_id,
  traffic_source.source AS source,
  traffic_source.medium AS medium,
  device.category AS device_category,
  geo.country AS country,
  ecommerce.transaction_id AS transaction_id,
  item.item_id AS item_id,
  item.item_name AS item_name,
  COALESCE(item.quantity, 0) AS quantity,
  COALESCE(item.price, 0) AS price,
  COALESCE((SELECT ep.value.string_value FROM UNNEST(event_params) ep WHERE ep.key = 'currency'), 'Unknown') AS currency
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*` AS e
LEFT JOIN UNNEST(e.items) AS item ON TRUE
WHERE _TABLE_SUFFIX BETWEEN @start_date AND @end_date
"""


def load_public_sample(
    project_id: str | None = None,
    start_date: str = "20201101",
    end_date: str = "20210131",
    maximum_bytes_billed: int = 10_000_000_000,
) -> pd.DataFrame:
    """Query the public GA4 sample. BigQuery query-job billing and credentials are required."""
    from google.cloud import bigquery

    project = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise ValueError("Set GOOGLE_CLOUD_PROJECT to a billing project before using BigQuery.")
    client = bigquery.Client(project=project)
    config = bigquery.QueryJobConfig(maximum_bytes_billed=maximum_bytes_billed, query_parameters=[
        bigquery.ScalarQueryParameter("start_date", "STRING", start_date),
        bigquery.ScalarQueryParameter("end_date", "STRING", end_date),
    ])
    raw = client.query(QUERY, job_config=config).to_dataframe()
    if raw.empty:
        return raw
    raw["session_id"] = raw["user_pseudo_id"].fillna("unknown") + "." + raw["raw_session_id"].fillna("no_session")
    raw["channel"] = raw.apply(_channel, axis=1)
    raw["currency"] = raw["currency"].fillna("Unknown")
    return raw.drop(columns=["raw_session_id", "source", "medium"])


def _channel(row: pd.Series) -> str:
    source = str(row.get("source", "")).lower()
    medium = str(row.get("medium", "")).lower()
    if medium == "organic":
        return "Organic Search"
    if medium in {"cpc", "ppc", "paidsearch"}:
        return "Paid Search"
    if medium == "email":
        return "Email"
    if medium == "affiliate":
        return "Affiliates"
    if medium in {"social", "organic_social"} or source in {"facebook", "instagram", "youtube"}:
        return "Social"
    if not source or source == "(direct)":
        return "Direct"
    return "Referral / Other"
