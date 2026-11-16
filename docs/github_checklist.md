# GitHub publishing checklist

- [x] Review tracked files: no credentials, `.env`, personal data, or private analytics exports are included.
- [x] Keep the bundled CSV provenance note and demo/simulation labels intact.
- [x] Install project dependencies; `ruff check src tests scripts`, `pytest -q`, and `python scripts/validate_demo.py` pass locally.
- [x] Run the Streamlit app, verify all tabs, and capture desktop/mobile screenshots from the running app.
- [x] Confirm BigQuery is optional, credentials are supplied via ADC, and the billing warning is visible in README.
- [x] Check local Markdown links and review spelling in README and docs.
- [x] Suggested repository name: `commercelab`. Description: `GA4 ecommerce customer behavior and product analytics with a reproducible Streamlit demo.`
- [x] Local Git repository initialized on `main`; reviewed and committed locally. The branch is ready to connect to a remote.
- [ ] Create the remote repository as public only after reviewing its contents; push the default branch.
- [ ] Confirm GitHub Actions runs on the remote and update the README only with the observed CI status.
- [ ] If a BigQuery run is demonstrated, record date range, billing project configuration, and exact query/schema version; do not upload credentials.
