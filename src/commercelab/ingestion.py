from __future__ import annotations

from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = {
    "event_date", "event_timestamp", "event_name", "user_pseudo_id", "session_id",
    "channel", "country", "device_category", "transaction_id", "item_id", "item_name",
    "quantity", "price", "currency"
}


def load_events(path: str | Path) -> pd.DataFrame:
    """Read the normalized CommerceLab event schema from CSV."""
    frame = pd.read_csv(path)
    missing = sorted(REQUIRED_COLUMNS - set(frame.columns))
    if missing:
        raise ValueError(f"Missing required event columns: {', '.join(missing)}")
    frame["event_date"] = pd.to_datetime(frame["event_date"], errors="coerce").dt.date
    frame["event_timestamp"] = pd.to_datetime(frame["event_timestamp"], utc=True, errors="coerce")
    frame["quantity"] = pd.to_numeric(frame["quantity"], errors="coerce")
    frame["price"] = pd.to_numeric(frame["price"], errors="coerce")
    return frame


def write_events(frame: pd.DataFrame, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)
