from pathlib import Path
import unittest

import pandas as pd

from commercelab.abtest import simulate_ab_test
from commercelab.analytics import (
    channel_performance, conversion_summary, funnel, product_performance,
    retention_cohorts, rfm_segments,
)
from commercelab.bigquery import QUERY
from commercelab.ingestion import load_events
from commercelab.statistics import bootstrap_mean_interval, wilson_interval
from commercelab.validation import validate_events


def fixture_events() -> pd.DataFrame:
    rows = []
    def add(day, event, user, session, tx="", price=10, quantity=1):
        rows.append({
            "event_date": f"2021-01-{day:02d}",
            "event_timestamp": f"2021-01-{day:02d}T12:00:00Z",
            "event_name": event,
            "user_pseudo_id": user,
            "session_id": session,
            "channel": "Organic Search",
            "country": "US",
            "device_category": "mobile",
            "transaction_id": tx,
            "item_id": "p1" if event == "purchase" else "",
            "item_name": "Test item" if event == "purchase" else "",
            "quantity": quantity if event == "purchase" else 0,
            "price": price if event == "purchase" else 0,
            "currency": "USD",
        })
    for user in ("u1", "u2"):
        add(1, "session_start", user, user)
        add(1, "view_item", user, user)
    add(1, "purchase", "u1", "u1", "t1")
    add(8, "session_start", "u1", "u1b")
    add(8, "purchase", "u1", "u1b", "t2", price=20)
    add(15, "session_start", "u2", "u2b")
    return pd.DataFrame(rows)


class CommerceLabTests:
    """Shared test helpers; tests run under unittest and pytest."""

    def setUp(self):
        self.events = fixture_events()

    def test_validation_passes_and_flags_bad_price(self):
        self.assertTrue(validate_events(self.events)["passed"])
        broken = self.events.copy()
        broken.loc[0, "price"] = -1
        result = validate_events(broken)
        self.assertFalse(result["passed"])
        self.assertEqual(result["invalid_prices"], 1)
        broken.loc[broken.index[0], "event_timestamp"] = "not-a-timestamp"
        self.assertEqual(validate_events(broken)["invalid_timestamps"], 1)
        broken["quantity"] = broken["quantity"].astype(float)
        broken.loc[broken.index[0], "quantity"] = 1.5
        self.assertEqual(validate_events(broken)["invalid_quantities"], 1)

    def test_funnel_and_conversion(self):
        stages = funnel(self.events)
        self.assertEqual(stages.iloc[0]["users"], 2)
        self.assertEqual(stages.loc[stages.event.eq("purchase"), "users"].iloc[0], 1)
        result = conversion_summary(self.events)
        self.assertEqual((result["visitors"], result["buyers"], result["orders"]), (2, 1, 2))

    def test_cohorts_and_rfm(self):
        cohorts = retention_cohorts(self.events)
        self.assertFalse(cohorts.empty)
        self.assertTrue(cohorts.retention.between(0, 1).all())
        segments = rfm_segments(self.events)
        self.assertEqual(segments.user_pseudo_id.nunique(), 1)
        self.assertEqual(segments.iloc[0].frequency, 2)

    def test_intervals_are_bounded_and_bootstrap_reproducible(self):
        low, high = wilson_interval(25, 100)
        self.assertTrue(0 < low < 0.25 < high < 1)
        values = pd.Series([1, 2, 3])
        self.assertEqual(bootstrap_mean_interval(values, seed=9), bootstrap_mean_interval(values, seed=9))

    def test_ab_simulation_is_seeded(self):
        one, result = simulate_ab_test(400, seed=3)
        two, result2 = simulate_ab_test(400, seed=3)
        pd.testing.assert_frame_equal(one, two)
        self.assertEqual(result, result2)
        self.assertEqual(set(one.assignment), {"Control", "Variant"})
        self.assertEqual((result["n_control"], result["n_variant"]), (200, 200))

    def test_ab_rejects_invalid_probabilities(self):
        with self.assertRaises(ValueError):
            simulate_ab_test(200, baseline=1.2)

    def test_currency_selection_changes_money_metrics_not_visitor_counts(self):
        events = self.events.copy()
        events.loc[events.transaction_id.eq("t2"), "currency"] = "LKR"

        summary = conversion_summary(events, ["USD"])
        self.assertEqual((summary["visitors"], summary["buyers"], summary["orders"]), (2, 1, 2))
        self.assertEqual(summary["revenue"], 10)

        channels = channel_performance(events, ["USD"])
        self.assertEqual(int(channels.sessions.sum()), 4)
        self.assertEqual(int(channels.orders.sum()), 1)
        self.assertEqual(float(channels.revenue.sum()), 10)

        products = product_performance(events, ["USD"])
        purchased = products[products.event_name.eq("purchase")]
        self.assertEqual(int(purchased.units.sum()), 1)
        self.assertEqual(float(purchased.revenue.sum()), 10)
        segments = rfm_segments(events, ["USD"])
        self.assertEqual(int(segments.iloc[0].frequency), 1)
        self.assertEqual(float(segments.iloc[0].monetary), 10)

    def test_bigquery_currency_uses_event_parameter_not_item_field(self):
        self.assertNotIn("item.currency", QUERY)
        self.assertIn("ep.key = 'currency'", QUERY)
        sql = (Path(__file__).resolve().parents[1] / "sql" / "normalize_ga4_events.sql").read_text()
        self.assertNotIn("item.currency", sql)
        self.assertIn("p.key='currency'", sql)
        for filename in ("acquisition.sql", "products.sql", "rfm.sql"):
            query = (Path(__file__).resolve().parents[1] / "sql" / filename).read_text()
            self.assertIn("@currency", query)

    def test_bundled_demo_data_validates(self):
        path = Path(__file__).resolve().parents[1] / "data" / "sample" / "events.csv"
        sample = load_events(path)
        self.assertTrue(validate_events(sample)["passed"])
        self.assertGreater(sample.user_pseudo_id.nunique(), 100)


# Make the cases discoverable by pytest without requiring pytest-specific fixtures.
class TestCommerceLab(CommerceLabTests, unittest.TestCase):
    pass
