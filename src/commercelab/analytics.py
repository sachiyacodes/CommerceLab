from __future__ import annotations

import pandas as pd

FUNNEL_EVENTS = ["session_start", "view_item", "add_to_cart", "begin_checkout", "purchase"]


def funnel(events: pd.DataFrame) -> pd.DataFrame:
    users = events[events.event_name.isin(FUNNEL_EVENTS)].groupby("event_name")["user_pseudo_id"].nunique()
    rows = []
    previous = None
    for step, name in enumerate(FUNNEL_EVENTS):
        count = int(users.get(name, 0))
        rows.append({"step": step + 1, "event": name, "users": count,
                     "step_conversion": (count / previous if previous else 1.0 if count else 0.0)})
        previous = count
    return pd.DataFrame(rows)


def _currency_mask(events: pd.DataFrame, currencies: list[str] | None) -> pd.Series:
    if currencies is None:
        return pd.Series(True, index=events.index)
    return events["currency"].fillna("Unknown").astype(str).isin(currencies)


def conversion_summary(events: pd.DataFrame, currencies: list[str] | None = None) -> dict[str, float | int]:
    visitors = int(events.loc[events.event_name.isin(["session_start", "first_visit"]), "user_pseudo_id"].nunique())
    buyers = int(events.loc[events.event_name.eq("purchase"), "user_pseudo_id"].nunique())
    all_purchases = events[events.event_name.eq("purchase")]
    purchases = all_purchases[_currency_mask(all_purchases, currencies)]
    return {"visitors": visitors, "buyers": buyers, "orders": int(all_purchases.transaction_id.nunique()),
            "conversion_rate": buyers / visitors if visitors else 0.0,
            "revenue": float((purchases.price * purchases.quantity).sum())}


def channel_performance(events: pd.DataFrame, currencies: list[str] | None = None) -> pd.DataFrame:
    sessions = events[events.event_name.eq("session_start")].groupby("channel").agg(sessions=("session_id", "nunique"), users=("user_pseudo_id", "nunique"))
    purchase_mask = events.event_name.eq("purchase") & _currency_mask(events, currencies)
    bought = events[purchase_mask].groupby("channel").agg(orders=("transaction_id", "nunique"), revenue=("price", lambda s: float((s * events.loc[s.index, "quantity"]).sum())))
    out = sessions.join(bought, how="outer").fillna(0).reset_index()
    out["conversion_rate"] = out["orders"] / out["sessions"].replace(0, pd.NA)
    return out.fillna(0).sort_values("revenue", ascending=False)


def retention_cohorts(events: pd.DataFrame) -> pd.DataFrame:
    visits = events[events.event_name.isin(["session_start", "purchase"])].dropna(subset=["user_pseudo_id"]).copy()
    visits["period"] = pd.to_datetime(visits.event_date).dt.to_period("M")
    first = visits.groupby("user_pseudo_id").period.min().rename("cohort")
    visits = visits.join(first, on="user_pseudo_id")
    visits["age"] = (visits.period.dt.year - visits.cohort.dt.year) * 12 + visits.period.dt.month - visits.cohort.dt.month
    cohort_sizes = first.groupby(first).size()
    active = visits.groupby(["cohort", "age"]).user_pseudo_id.nunique().rename("users")
    result = active.reset_index()
    result["cohort_size"] = result.cohort.map(cohort_sizes)
    result["retention"] = result.users / result.cohort_size
    result["cohort"] = result.cohort.astype(str)
    return result


def product_performance(events: pd.DataFrame, currencies: list[str] | None = None) -> pd.DataFrame:
    items = events[events.event_name.isin(["view_item", "add_to_cart", "purchase"])].copy()
    purchase_mask = items.event_name.eq("purchase") & _currency_mask(items, currencies)
    grouped = items.groupby(["item_id", "item_name", "event_name"]).agg(
        event_count=("event_name", "size"),
        users=("user_pseudo_id", "nunique"),
        units=("quantity", lambda s: int((s * purchase_mask.loc[s.index]).sum())),
        revenue=("price", lambda s: float((s * items.loc[s.index, "quantity"] * purchase_mask.loc[s.index]).sum())),
    ).reset_index()
    return grouped


def rfm_segments(events: pd.DataFrame, currencies: list[str] | None = None) -> pd.DataFrame:
    purchases = events[events.event_name.eq("purchase") & _currency_mask(events, currencies)].copy()
    if purchases.empty:
        return pd.DataFrame(columns=["user_pseudo_id", "recency_days", "frequency", "monetary", "segment"])
    purchases["event_date"] = pd.to_datetime(purchases.event_date)
    purchases["revenue"] = purchases.price * purchases.quantity
    snapshot = purchases.event_date.max() + pd.Timedelta(days=1)
    rfm = purchases.groupby("user_pseudo_id").agg(recency_days=("event_date", lambda s: int((snapshot - s.max()).days)), frequency=("transaction_id", "nunique"), monetary=("revenue", "sum")).reset_index()
    rfm["segment"] = "Occasional"
    rfm.loc[(rfm.frequency >= 2) & (rfm.monetary >= rfm.monetary.median()), "segment"] = "Loyal value"
    rfm.loc[(rfm.frequency == 1) & (rfm.recency_days <= 14), "segment"] = "New customers"
    rfm.loc[rfm.recency_days > 45, "segment"] = "At risk"
    return rfm
