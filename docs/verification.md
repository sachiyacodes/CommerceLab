# Verification record

Verification performed locally on 2026-11-15. The active project environment is Python 3.14.4, Pandas 3.1.1, NumPy 2.5.4, pytest 8.4.2, Ruff 0.17.5, Streamlit 1.67.0, and Altair 6.3.0. Altair 6 is required for Python 3.14 compatibility.

## Completed checks

- `python -m pytest -q`: 9 tests passed, including currency-filter behavior and a guard that BigQuery currency comes from event parameters.
- `ruff check src tests scripts`: passed.
- `python scripts/validate_demo.py`: passed; 5,757 rows and 585 unique generated users.
- `python -m compileall -q src tests scripts`: passed.
- Launched the Streamlit app and checked all seven tabs in the browser. The retention chart and sidebar controls rendered with readable contrast; browser console reported no errors.
- Captured the running app at desktop and mobile widths in `screenshots/dashboard.png` and `screenshots/dashboard-mobile.png`. At 390 px wide, the document had no horizontal overflow.
- `python -m pip wheel --no-deps --no-build-isolation .`: built `commercelab-1.0.0-py3-none-any.whl` successfully.
- A final repeat of the wheel build was blocked because `setuptools` is absent from the active virtual environment and PyPI could not be reached; the earlier local wheel build above succeeded.
- `node scripts/generate_demo_data.js`: regenerated the deterministic sample successfully. Its dates are 2020-11-01 through 2021-01-31 across six event types.
- Read-only review against Google's GA4 export schema corrected currency extraction to use the event parameter rather than an item field.
- The default branch is published at [CommerceLab](https://github.com/sachiyacodes/CommerceLab). CI passed for baseline commit `a6296e99919fb1e1e5f2a78d38a3245d24d92860`: [observed run](https://github.com/sachiyacodes/CommerceLab/actions/runs/43823667896).

## Not run

- BigQuery was not executed because no Google Cloud credentials or billing project are configured. The public query and schema were reviewed, but no cloud results or costs are claimed.
- BigQuery results remain unverified; local sample validation does not prove cloud query execution.

## Source release scope

The 1.0.0 milestone supports the documented source checkout and editable installation. CSV and SQL resources remain repository files; no standalone wheel or PyPI installation is promised. The November 15 checks above are historical evidence. Release maintenance updates require fresh tests, lint, sample validation, and successful CI for the published commit.

Maintenance verification on November 16, 2026 used an isolated Python 3.12.10 environment with pytest 9.2.0. All 10 tests passed, including a regression check of observed sample counts. Ruff, compile checks, dependency consistency, and sample validation passed. Running the generator in a temporary directory reproduced the tracked CSV exactly after Git line-ending normalization. The bundled CSV was not changed. Hosted CI must pass for the release commit before publication.
