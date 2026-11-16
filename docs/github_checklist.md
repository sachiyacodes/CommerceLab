# GitHub publishing checklist

- [x] Review tracked files: no credentials, `.env`, personal data, or private analytics exports are included.
- [x] Keep the bundled CSV provenance note and demo/simulation labels intact.
- [x] Install project dependencies; `ruff check src tests scripts`, `pytest -q`, and `python scripts/validate_demo.py` pass locally.
- [x] Run the Streamlit app, verify all tabs, and capture desktop/mobile screenshots from the running app.
- [x] Confirm BigQuery is optional, credentials are supplied via ADC, and the billing warning is visible in README.
- [x] Check local Markdown links and review spelling in README and docs.
- [x] Suggested repository name: `commercelab`. Description: `GA4 ecommerce customer behavior and product analytics with a reproducible Streamlit demo.`
- [x] Default branch published at `sachiyacodes/CommerceLab`.
- [x] Public source reviewed and pushed; synthetic data contains no private analytics exports.
- [x] GitHub Actions passed for published baseline `a6296e99919fb1e1e5f2a78d38a3245d24d92860`; see the verification record. Every release still requires CI at its exact commit.
- [ ] If a BigQuery run is demonstrated, record date range, billing project configuration, and exact query/schema version; do not upload credentials.
