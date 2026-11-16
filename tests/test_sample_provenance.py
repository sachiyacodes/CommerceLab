"""Keep the sample's published counts tied to its actual contents."""
import csv
from pathlib import Path


def test_sample_provenance_counts():
    sample = Path(__file__).resolve().parents[1] / "data" / "sample"
    with (sample / "events.csv").open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    users = {row["user_pseudo_id"] for row in rows}
    note = (sample / "README.md").read_text(encoding="utf-8")
    assert f"{len(rows):,} events" in note
    assert f"{len(users)} observed user IDs" in note
    assert "pool of 620 possible user IDs" in note
