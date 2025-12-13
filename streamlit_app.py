import streamlit as st
import pandas as pd
import plotly.express as px
import yaml
from pathlib import Path
from io import BytesIO
import json
from datetime import datetime

# --- Load hospital config (defensive) ---
config_path = Path("hospital_config.yaml")
hospital_config = {}
if config_path.exists():
    try:
        with config_path.open("r", encoding="utf-8") as f:
            hospital_config = yaml.safe_load(f) or {}
    except Exception as e:
        st.error(f"Error loading hospital_config.yaml: {e}")
        hospital_config = {}
else:
    st.warning("hospital_config.yaml not found. Using example/default values.")

# Provide safe defaults if config missing or incomplete
hospital = hospital_config.get("hospital", {}) if isinstance(hospital_config, dict) else {}
hospital_name = hospital.get("name", "General Hospital")
sapling_cost = hospital.get("sapling_cost_gbp", 50)
preventive_gate = hospital.get("preventive_gate_score", 60)

# --- Enforce non-budgetary policy flag ---
rbi_value = hospital.get("reward_budget_integration", None)
if rbi_value is None:
    st.info("Configuration note: 'reward_budget_integration' not set. Recommended: 'prohibited'.")
elif str(rbi_value).strip().lower() != "prohibited":
    st.error(
        "Configuration error: 'reward_budget_integration' must be set to 'prohibited' "
        "to preserve non-budgetary incentive status. External budget integration settings will be ignored."
    )
    # Defensive: remove any external budget keys if present
    hospital.pop("external_budget_source", None)
    hospital.pop("external_reward_split", None)

# --- Example dataset (replace with public record pull) ---
data = [
    {"Department": "Paediatrics", "Score (%)": 82, "Reward (£)": 60},
    {"Department": "Mental Health", "Score (%)": 65, "Reward (£)": 480},
    {"Department": "Cardiology", "Score (%)": 74, "Reward (£)": 30},
    {"Department": "Obstetrics/Gyn.", "Score (%)": 79, "Reward (£)": 20},
    {"Department": "Community Health", "Score (%)": 55, "Reward (£)": 10},  # deliberately below gate
]
df = pd.DataFrame(data)

# --- Normalize and sanitize inputs ---
# Ensure numeric, coerce errors to 0, and clip negatives to zero (policy: negative results normalized to zero)
df["Score (%)"] = pd.to_numeric(df["Score (%)"], errors="coerce").fillna(0).clip(lower=0)
df["Reward (£)"] = pd.to_numeric(df["Reward (£)"], errors="coerce").fillna(0).clip(lower=0)

# --- Preventive gate enforcement ---
df["Reward (£)"] = df.apply(
    lambda row: row["Reward (£)"] if row["Score (%)"] >= preventive_gate else 0,
    axis=1
)

# --- Zero reset indicator column ---
df["Status"] = df.apply(
    lambda row: "Eligible" if row["Score (%)"] >= preventive_gate else "Reset to Zero",
    axis=1
)

# --- Civic-poetic header & policy banner ---
st.markdown("## 🌿 Hospital Preventive Care Scorecard")
st.markdown("_Let every department be a garden of care. Where saplings become stethoscopes, and rhythm becomes remedy._")

policy_disclaimer_text = """
### ⚖️ Policy Disclaimer

- Rewards provided through this app are **independent civic incentives**.  
- They **must not** be recorded, reported, or included in any government- or council-funded project or institution's budget.  
- Rewards are symbolic conversions (saplings → cash → equipment) designed to support preventive care, not subsidies or budget supplements.  
- **Negative performance results** in any department are automatically normalized to zero for calculation purposes.  
  - This prevents distortions in reward allocation.  
  - Departments with negative results receive no allocation until performance improves.  
- All figures are derived from public records; hospitals are not required to submit data manually.  
- This scorecard is intended for **recognition and stewardship only**, not for financial accounting or compliance reporting.
"""
st.info(policy_disclaimer_text)

# --- Bar chart with zero reset indicator ---
colors = df["Status"].map({"Eligible": "steelblue", "Reset to Zero": "lightgrey"})
fig_scores = px.bar(
    df,
    x="Department",
    y="Score (%)",
    title="Departmental Preventive Scores (Zero Reset Applied)",
    text="Score (%)",
    color="Status",
    color_discrete_map={"Eligible": "steelblue", "Reset to Zero": "lightgrey"}
)
st.plotly_chart(fig_scores, use_container_width=True)

# --- Pie chart for reward distribution ---
fig_rewards = px.pie(df, values="Reward (£)", names="Department", title="Reward Allocation (£)")
st.plotly_chart(fig_rewards, use_container_width=True)

# --- Table view ---
st.dataframe(df)

# --- Export buttons (CSV + Excel including disclaimer) ---
# CSV: append a final disclaimer row (quick approach)
csv_core = df.to_csv(index=False)
disclaimer_line = (
    "\"Non-budgetary incentive — For preventive care recognition only. "
    "Not to be recorded in official government or council budgets.\"\n"
)
csv_with_disclaimer = (csv_core + "\n" + disclaimer_line).encode("utf-8")
st.download_button(
    "Download CSV",
    csv_with_disclaimer,
    f"scorecard_{hospital_name.replace(' ', '_').lower()}.csv",
    "text/csv"
)

# Excel: add a 'Disclaimer' sheet
excel_buffer = BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="Scorecard")
    pd.DataFrame(
        [
            [
                "Non-budgetary incentive — For preventive care recognition only. "
                "Not to be recorded in official government or council budgets."
            ]
        ],
        columns=["Disclaimer"],
    ).to_excel(writer, index=False, sheet_name="Disclaimer")
excel_buffer.seek(0)
st.download_button(
    "Download Excel",
    excel_buffer.getvalue(),
    f"scorecard_{hospital_name.replace(' ', '_').lower()}.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

# --- Printable report layout ---
with st.expander("📜 Printable Report"):
    st.markdown(f"""
    ### Hospital Preventive Care Scorecard
    **Hospital:** {hospital_name}  
    **Period:** 5-Year Rolling Average  
    **Total Reward Fund:** £{df['Reward (£)'].sum():,.2f}  
    **Sapling Conversion Rate:** £{sapling_cost} per sapling  

    ---
    ### Departmental Performance (Gate ≥ {preventive_gate}%)
    """)
    for _, row in df.iterrows():
        status_icon = "✅" if row["Status"] == "Eligible" else "❌"
        st.markdown(f"- {row['Department']}: Score {row['Score (%)']}% → £{int(row['Reward (£)'])} ({status_icon} {row['Status']})")

    st.markdown("""
    ---
    ### Reward Distribution
    - Rewards allocated only to departments meeting preventive gate.
    - Departments below threshold are reset to zero until performance improves.

    ---
    _Designed for sustainability, equity, and dignity._
    """)

    # Printable footer disclaimer
    st.markdown(
        "_Non-budgetary incentive — For preventive care recognition only. Not to be recorded in official government or council budgets._"
    )

# --- Audit log entry (append to audit_log.json) ---
audit_entry = {
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "event": "reward_allocation",
    "hospital": hospital_name,
    "total_reward_fund": float(df["Reward (£)"].sum()),
    "note": "Non-budgetary incentive — rewards are recorded separately and not reclassified into government/council budgets.",
    "allocations": df[["Department", "Reward (£)", "Status"]].to_dict(orient="records"),
}
audit_log_path = Path("audit_log.json")
try:
    if audit_log_path.exists():
        existing = json.loads(audit_log_path.read_text(encoding="utf-8").strip() or "[]")
    else:
        existing = []
    existing.append(audit_entry)
    audit_log_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
except Exception as e:
    st.warning(f"Could not write audit log: {e}")
