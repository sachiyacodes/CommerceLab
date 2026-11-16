from __future__ import annotations

import numpy as np
import pandas as pd
from .ingestion import REQUIRED_COLUMNS


def validate_events(frame: pd.DataFrame) -> dict[str, object]:
    """Return auditable quality counts and a boolean status without silently deleting data."""
    missing_columns = sorted(REQUIRED_COLUMNS - set(frame.columns))
    if missing_columns:
        return {"passed": False, "missing_columns": missing_columns, "row_count": len(frame)}
    date_ok = pd.to_datetime(frame["event_date"], errors="coerce").notna()
    timestamp_ok = pd.to_datetime(frame["event_timestamp"], utc=True, errors="coerce", format="mixed").notna()
    price = pd.to_numeric(frame["price"], errors="coerce")
    quantity = pd.to_numeric(frame["quantity"], errors="coerce")
    price_ok = price.notna() & np.isfinite(price) & (price >= 0)
    quantity_ok = quantity.notna() & np.isfinite(quantity) & (quantity >= 0) & quantity.mod(1).eq(0)
    return {
        "passed": bool(date_ok.all() and timestamp_ok.all() and price_ok.all() and quantity_ok.all()),
        "missing_columns": [],
        "row_count": int(len(frame)),
        "invalid_dates": int((~date_ok).sum()),
        "invalid_timestamps": int((~timestamp_ok).sum()),
        "invalid_prices": int((~price_ok).sum()),
        "invalid_quantities": int((~quantity_ok).sum()),
        "duplicate_event_rows": int(frame.duplicated(["event_timestamp", "event_name", "user_pseudo_id", "transaction_id", "item_id"]).sum()),
        "null_user_ids": int(frame["user_pseudo_id"].isna().sum()),
        "event_counts": {str(k): int(v) for k, v in frame["event_name"].value_counts(dropna=False).items()},
    }
