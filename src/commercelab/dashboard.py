from pathlib import Path
import altair as alt
import pandas as pd
import streamlit as st

from commercelab.abtest import simulate_ab_test
from commercelab.analytics import (
    channel_performance, conversion_summary, funnel, product_performance,
    retention_cohorts, rfm_segments,
)
from commercelab.ingestion import load_events
from commercelab.statistics import bootstrap_mean_interval, conversion_interval
from commercelab.validation import validate_events

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA = ROOT / "data" / "sample" / "events.csv"

st.set_page_config(page_title="CommerceLab | GA4 Analytics", layout="wide")
st.markdown("""
<style>
.stApp {background:#f5f7fb;color:#17223b;font-family:Arial,sans-serif}
h1,h2,h3 {font-family:Arial,sans-serif}
.block-container {padding-top:1.7rem;max-width:1440px}
[data-testid="stMetric"] {background:white;border:1px solid #e6eaf2;border-radius:14px;padding:16px 18px}
[data-testid="stSidebar"] {background:#101d35}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {color:#edf3ff}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"],
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] * {color:#334155!important}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {color:#17223b!important}
[data-testid="stSidebar"] [data-testid="stDateInput"] input,
[data-testid="stSidebar"] [data-testid="stMultiSelect"] input {color:#17223b!important;-webkit-text-fill-color:#17223b!important}
[data-testid="stSidebar"] [data-testid="stDateInput"] button {color:#475569!important}
[data-testid="stSidebar"] [data-testid="stAlert"] {background:#e8f5ec;color:#166534}
[data-testid="stSidebar"] [data-testid="stAlert"] * {color:#166534!important}
.hero {background:linear-gradient(120deg,#17294a,#25477a);color:#fff;padding:26px 30px;border-radius:18px;margin-bottom:22px}
.hero p {color:#cad7ed;margin-bottom:0}
.note {padding:12px 16px;background:#fff7e5;border-left:4px solid #e2a42d;border-radius:8px;color:#543d0a}
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>CommerceLab</h1><p>Customer behavior and product analytics from GA4 ecommerce events</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Data source")
    upload = st.file_uploader("Upload normalized event CSV", type="csv")
    st.caption("Expected fields are documented in docs/data_dictionary.md. Local demo needs no cloud credentials.")

try:
    events = load_events(upload if upload is not None else DEFAULT_DATA)
except Exception as exc:
    st.error(f"Could not load event data: {exc}")
    st.stop()
quality = validate_events(events)
if not quality["passed"]:
    st.error("Data validation failed. Check dates, required fields, prices, and quantities.")
    st.json(quality)
    st.stop()
source_label = "Uploaded normalized data" if upload is not None else "Bundled synthetic demo data"
st.sidebar.success(source_label)
st.sidebar.caption("The bundled sample is simulated; it is not exported from Google Analytics.")

min_date = pd.to_datetime(events.event_date).min().date()
max_date = pd.to_datetime(events.event_date).max().date()
with st.sidebar:
    date_range = st.date_input("Event date range", (min_date, max_date), min_value=min_date, max_value=max_date)
    country_options = sorted(events.country.dropna().astype(str).unique())
    selected_countries = st.multiselect("Country", country_options, default=country_options)
    purchase_currency = events.loc[events.event_name.eq("purchase"), "currency"].fillna("Unknown").astype(str)
    currency_counts = purchase_currency.value_counts()
    currency_options = sorted(currency_counts.index.tolist())
    default_currency = [str(currency_counts.index[0])] if len(currency_counts) else []
    selected_currencies = st.multiselect("Revenue currency", currency_options, default=default_currency)
    st.caption("Currency selection filters monetary metrics; visitor and event counts keep all selected countries and dates.")
if isinstance(date_range, tuple) and len(date_range) == 2:
    lo, hi = date_range
else:
    lo = hi = date_range
filter_dates = pd.to_datetime(events.event_date).dt.date
filtered = events[filter_dates.between(lo, hi) & events.country.astype(str).isin(selected_countries)]
if filtered.empty:
    st.warning("No events match the selected filters.")
    st.stop()

st.caption(f"Data: {source_label} | {len(filtered):,} filtered event rows | Validation passed")
summary = conversion_summary(filtered, selected_currencies)
visitors, buyers = summary["visitors"], summary["buyers"]
ci = conversion_interval(buyers, visitors)
a, b, c, d = st.columns(4)
a.metric("Visitors", f"{visitors:,}")
b.metric("Purchasing users", f"{buyers:,}")
c.metric("Visitor conversion", f"{summary['conversion_rate']:.1%}", help=f"Wilson 95% interval: {ci[0]:.1%} to {ci[1]:.1%}")
currency = selected_currencies[0] if len(selected_currencies) == 1 else "Mixed currencies" if selected_currencies else "No currency selected"
if len(selected_currencies) > 1:
    st.warning("Revenue and customer spend combine selected currencies without conversion. Select one currency for monetary comparisons.")
if "Unknown" in selected_currencies:
    st.warning("Some purchase rows have no currency parameter. Their monetary values are labeled Unknown and may not be comparable.")
d.metric("Observed revenue", f"{currency} {summary['revenue']:,.2f}", help="Revenue is not currency-converted.")

funnel_tab, channel_tab, retention_tab, product_tab, customer_tab, experiment_tab, quality_tab = st.tabs([
    "Funnel", "Acquisition", "Retention", "Products", "Customers", "A/B simulation", "Data quality"
])
with funnel_tab:
    st.subheader("Shopping funnel")
    f = funnel(filtered)
    funnel_chart = alt.Chart(f).mark_bar(color="#4878c5", cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
        x=alt.X("event:N", sort=None, title="Event"),
        y=alt.Y("users:Q", title="Unique users"),
        tooltip=["event", "users", alt.Tooltip("step_conversion:Q", format=".1%")],
    ).properties(height=340)
    st.altair_chart(funnel_chart, use_container_width=True)
    st.dataframe(f.assign(step_conversion=f.step_conversion.map(lambda x: f"{x:.1%}")), hide_index=True, use_container_width=True)
    st.caption("Unique users with each event in the selected period. This descriptive funnel does not reconstruct event order within sessions.")
with channel_tab:
    st.subheader("Acquisition channel performance")
    channels = channel_performance(filtered, selected_currencies)
    channel_chart = alt.Chart(channels).mark_bar(color="#35a58b").encode(
        x=alt.X("channel:N", sort="-y"), y="revenue:Q",
        tooltip=["channel", "sessions", "orders", "revenue", alt.Tooltip("conversion_rate:Q", format=".1%")],
    ).properties(height=330)
    st.altair_chart(channel_chart, use_container_width=True)
    st.dataframe(channels, hide_index=True, use_container_width=True)
    st.caption("Channel attribution may be first-user source/medium rather than session attribution in the public sample.")
with retention_tab:
    st.subheader("Monthly customer retention")
    cohorts = retention_cohorts(filtered)
    if cohorts.empty:
        st.info("No cohort activity in this selection.")
    else:
        chart = alt.Chart(cohorts).mark_rect().encode(
            x=alt.X("age:O", title="Months since first observed visit"),
            y=alt.Y("cohort:O", title="First observed month"),
            color=alt.Color("retention:Q", scale=alt.Scale(scheme="blues"), title="Retention", legend=alt.Legend(format=".0%")),
            tooltip=["cohort", "age", "users", "cohort_size", alt.Tooltip("retention:Q", format=".1%")],
        ).properties(height=320)
        st.altair_chart(chart, use_container_width=True)
        st.caption("Cohorts use the first month visible in the selection; partial months can lower observed retention.")
with product_tab:
    st.subheader("Product engagement and sales")
    products = product_performance(filtered, selected_currencies)
    if products.empty:
        st.info("No item-level events in this selection.")
    else:
        st.dataframe(products.sort_values(["event_name", "revenue"], ascending=[True, False]), hide_index=True, use_container_width=True)
with customer_tab:
    st.subheader("Purchase behavior segments")
    segments = rfm_segments(filtered, selected_currencies)
    if segments.empty:
        st.info("No purchases in this selection.")
    else:
        st.dataframe(segments, hide_index=True, use_container_width=True)
        st.caption("RFM labels use only purchases in the selected range and illustrative thresholds; they are not validated lifetime value predictions.")
        low, high = bootstrap_mean_interval(segments.monetary)
        st.metric("Average customer spend (bootstrap 95% CI)", f"{currency} {segments.monetary.mean():,.2f}", help=f"Percentile interval: {currency} {low:,.2f} to {currency} {high:,.2f}.")
with experiment_tab:
    st.subheader("Simulated randomized A/B test")
    st.markdown('<div class="note"><b>Teaching demo only.</b> These outcomes are generated from seeded synthetic random assignment. They are not from the GA4 public sample or a real experiment.</div>', unsafe_allow_html=True)
    visitors_per_arm = st.slider("Synthetic visitors per arm", 200, 5000, 1200, 100)
    assumed_lift = st.slider("Assumed variant effect", 0.0, 0.03, 0.006, 0.001)
    _, result = simulate_ab_test(sample_size=visitors_per_arm * 2, lift=assumed_lift)
    left, right = st.columns(2)
    left.metric("Control conversion", f"{result['control_rate']:.2%}", f"n={result['n_control']}")
    right.metric("Variant conversion", f"{result['variant_rate']:.2%}", f"difference {result['absolute_lift']:+.2%}")
    st.write(f"Two-sided z-test p-value (normal approximation): **{result['p_value']:.4f}**")
    st.caption("The p-value from a synthetic draw is unstable and does not validate a product change. Causal claims require recorded randomized assignment and exposure, a pre-specified design, and outcome data.")
with quality_tab:
    st.subheader("Validation report")
    st.json(quality)
    st.download_button("Download filtered events", filtered.to_csv(index=False), "commercelab_events.csv", "text/csv")

st.divider()
st.caption("CommerceLab | GA4 event analytics portfolio project | Local demo is simulated | No personal identifiers are included.")
