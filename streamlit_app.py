import html
import json
import re
from datetime import datetime
from pathlib import Path
import pandas as pd
import streamlit as st
import yaml
CONFIG_PATH = Path("hospital_config.yaml")
AUDIT_LOG_PATH = Path("audit_log.jsonl")  # newline-delimited JSON entries
# --- Helpers ---
def load_config(path: Path) -> dict:
    """Load YAML config defensively; return empty dict on error."""
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        # surface config load error in UI but continue with defaults
        st.error(f"Error loading {path.name}: {e}")
        return {}
def audit_event(action: str, details: dict | None = None) -> None:
    """Append an audit entry (JSONL) with timestamp, user (if available), and details."""
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action": action,
        "user": st.session_state.get("user", None) if "user" in st.session_state else None,
        "details": details or {},
    }
    try:
        with AUDIT_LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        # do not crash the app on logging failure; show a non-blocking warning
        st.warning(f"Failed to write audit log: {e}")
def sanitize_text(s: str) -> str:
    """Minimal sanitization for display (escape HTML)."""
    return html.escape(s)
# --- Load config ---
hospital_config = load_config(CONFIG_PATH)
# --- Basic hospital info (from config or sensible defaults) ---
hospital_name = hospital_config.get("hospital_name", "Example Hospital")
reporting_period = hospital_config.get("reporting_period", "2025 Q1")
sapling_cost = hospital_config.get("sapling_cost", 10.0)
# Header and disclaimer (explicitly non-budgetary reward policy)
st.subheader(f"📊 {sanitize_text(hospital_name)}")
st.write(f"**Period:** {sanitize_text(reporting_period)}")
st.write(f"**Sapling Cost:** £{sapling_cost:.2f} per tree")
st.markdown(
    """
**Non-budgetary reward disclaimer**
This tool recommends recognition and non-financial rewards (e.g., tree plantings, certificates, public recognition) only.
It is not a mechanism to allocate or transfer budget or funds between departments.
Any budgetary actions must follow formal finance procedures.
"""
)
# --- Default data (fallback) ---
default_data = {
    "Department": [
        "Paediatrics",
        "Mental Health",
        "Cardiology",
        "Obstetrics/Gynecology",
        "Community Health",
    ],
    "Points (5yr avg)": [950, 820, 880, 1050, 790],
    "Score (%)": [78, 65, 72, 85, 62],
}
df = pd.DataFrame(default_data)
# Apply department-specific config overrides if present
config_departments = hospital_config.get("departments", {})
if config_departments:
    # map funding level and notes per department
    df["Funding Level"] = df["Department"].map(
        lambda d: config_departments.get(d, {}).get("funding_level", "medium")
    )
    df["Notes"] = df["Department"].map(
        lambda d: config_departments.get(d, {}).get("notes", "")
    )
else:
    df["Funding Level"] = "medium"
    df["Notes"] = ""
# --- Determine least-funded department (preference: explicit 'low', fallback: lowest points then score) ---
least_funded_dept = None
selection_method = "Not determined"
low_funded_depts = df[df["Funding Level"].str.lower() == "low"]["Department"].tolist()
if low_funded_depts:
    least_funded_dept = low_funded_depts[0]
    selection_method = "Config (funding_level: low)"
else:
    # fallback: pick department with lowest Points (5yr avg), tie-breaker = Score (%)
    try:
        idx = df["Points (5yr avg)"].idxmin()
        candidates = df[df["Points (5yr avg)"] == df.loc[idx, "Points (5yr avg)"]]
        if len(candidates) > 1:
            # tie-break by lowest Score
            idx2 = candidates["Score (%)"].idxmin()
            least_funded_dept = df.loc[idx2, "Department"]
            selection_method = "Lowest points (tie-broken by score)"
        else:
            least_funded_dept = df.loc[idx, "Department"]
            selection_method = "Lowest points"
    except Exception:
        least_funded_dept = None
        selection_method = "Failed to determine (data issue)"
# Display table and selection
st.dataframe(df)
if least_funded_dept:
    st.success(
        f"Selected department for additional non-budgetary recognition: {sanitize_text(least_funded_dept)}"
    )
else:
    st.error("Could not determine a department for non-budgetary recognition.")
st.write(f"Selection method: {sanitize_text(selection_method)}")
# Audit the selection determination (non-sensitive details only)
audit_event("selection_determined", {"department": least_funded_dept, "method": selection_method})
# --- Export functionality (download CSV) ---
st.markdown("### Export")
st.write(
    "Export the current table as CSV. Exports are logged for audit purposes. "
    "This export is for record-keeping / recognition planning and does not constitute a budget transfer."
)
csv_bytes = df.to_csv(index=False).encode("utf-8")
if st.download_button(label="Download CSV", data=csv_bytes, file_name="department_report.csv", mime="text/csv"):
    audit_event("export_csv", {"rows": len(df), "file": "department_report.csv"})
# Allow copying or saving the audit log (admins)
st.markdown("### Audit log")
if AUDIT_LOG_PATH.exists():
    try:
        with AUDIT_LOG_PATH.open("r", encoding="utf-8") as fh:
            audit_preview = "".join(fh.readlines()[-20:])  # show last 20 lines
    except Exception as e:
        audit_preview = f"Failed to read audit log: {e}"
else:
    audit_preview = "No audit entries yet."
st.text_area("Recent audit (JSONL)", value=audit_preview, height=200)
main
