from pathlib import Path
from commercelab.ingestion import load_events
from commercelab.validation import validate_events

root=Path(__file__).resolve().parents[1]
frame=load_events(root/'data'/'sample'/'events.csv')
report=validate_events(frame)
print(f"Rows: {len(frame):,}; unique users: {frame.user_pseudo_id.nunique():,}; validation passed: {report['passed']}")
if not report['passed']:
    raise SystemExit(1)
