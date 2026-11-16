from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from commercelab.bigquery import load_public_sample
from commercelab.ingestion import write_events

ROOT = Path(__file__).resolve().parents[1]

def valid_date(value: str) -> str:
    try:
        datetime.strptime(value, "%Y%m%d")
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Date must use YYYYMMDD.") from exc
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest Google's public GA4 ecommerce sample into normalized CSV.")
    parser.add_argument("--project", help="Google Cloud billing project; defaults to GOOGLE_CLOUD_PROJECT.")
    parser.add_argument("--start-date", type=valid_date, default="20201101")
    parser.add_argument("--end-date", type=valid_date, default="20210131")
    parser.add_argument("--max-bytes-billed", type=int, default=10_000_000_000,
                        help="BigQuery scan cap in bytes (default: 10 GB).")
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "processed" / "public_ga4_events.csv")
    args = parser.parse_args()
    if args.start_date > args.end_date:
        parser.error("--start-date must be on or before --end-date")
    if args.max_bytes_billed <= 0:
        parser.error("--max-bytes-billed must be positive")
    events = load_public_sample(args.project, args.start_date, args.end_date, args.max_bytes_billed)
    write_events(events, args.output)
    print(f"Wrote {len(events):,} normalized event-item rows to {args.output}")


if __name__ == "__main__":
    main()
