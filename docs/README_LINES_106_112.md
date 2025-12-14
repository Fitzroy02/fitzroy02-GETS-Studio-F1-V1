Please note the exact file paths and run instructions used in this repository:

- Governance flow image: docs/images/governance_flow.png — ensure this file exists relative to this README so GitHub renders it.
- Streamlit app entrypoint: streamlit run examples/unified_healthcare_dashboard.py (run from the repository root).
- Sample data file (used by the examples): data/dashboard_data.json. Either run with DATA_FILE set to "data/dashboard_data.json", or copy it to the repo root as dashboard_data.json before running.
- Exported CSV filenames (filtered by role/date as shown in the UI):
  - audit_daily_summary_filtered.csv
  - audit_quarterly_summary_filtered.csv
  - audit_trail_filtered.csv
