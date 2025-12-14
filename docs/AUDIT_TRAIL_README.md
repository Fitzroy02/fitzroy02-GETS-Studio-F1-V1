# Audit Trail Dashboard — Daily & Quarterly Activity

## 📘 Overview
This dashboard provides transparency across doctor, patient, and co‑worker actions. It visualizes audit trail entries and allows exporting filtered summaries for compliance and governance.

## 🔎 Features
- **Daily Activity Summary**  
  Interactive bar chart showing counts of actions per role per day.
- **Quarterly Activity Summary**  
  Bar chart showing counts of actions per role per quarter (e.g., 2025‑Q4).
- **Timeline View**  
  Scatter plot of individual events (role vs. time) with hover details.
- **Filtered CSV Exports**  
  - Daily summary (actions per role per day).  
  - Quarterly summary (actions per role per quarter).  
  - Raw audit trail (full event log with timestamps, actor, role, action, target, notes).  
  Exports respect the role/date filters applied in the dashboard.

## 🛠️ Usage
1. Run the dashboard with:
   ```bash
   streamlit run examples/unified_healthcare_dashboard.py
   ```
2. Select **Audit Trail** from the sidebar.
3. Apply filters:
   - **Role filter:** Doctor, Patient, Co‑worker, or All.  
   - **Date range filter:** Choose start and end dates.
4. Review visualizations:
   - Daily bar chart.  
   - Quarterly bar chart.  
   - Timeline scatter plot (expandable).
5. Export filtered data:
   - Click the download buttons to save CSV summaries or the raw event log.

## 📂 File Outputs
- `audit_daily_summary_filtered.csv` — Daily counts per role (filtered).  
- `audit_quarterly_summary_filtered.csv` — Quarterly counts per role (filtered).  
- `audit_trail_filtered.csv` — Raw filtered audit trail entries.

## 🔄 Governance Notes
- Every action (report edits, file uploads, meeting scheduling) is logged.  
- Audit trail ensures accountability across all roles.  
- CSV exports allow external review and compliance checks.  
- Role/date filters ensure exports match the view you are auditing.

---

## ✅ Governance Checklist for Auditors

### Daily Review
- [ ] Apply role filter (Doctor, Patient, Co‑worker).  
- [ ] Export `audit_daily_summary_filtered.csv`.  
- [ ] Verify counts match dashboard visualization.  
- [ ] Cross‑check raw events in `audit_trail_filtered.csv` for anomalies.  

### Quarterly Review
- [ ] Export `audit_quarterly_summary_filtered.csv`.  
- [ ] Confirm quarterly totals align with daily roll‑ups.  
- [ ] Compare role balance (e.g., Doctor vs. Patient vs. Co‑worker contributions).  
- [ ] Document findings in compliance report.  

### Raw Event Log Review
- [ ] Export `audit_trail_filtered.csv`.  
- [ ] Inspect timestamps, actor names, actions, and notes.  
- [ ] Flag unusual activity (e.g., repeated disputes, missing confirmations).  
- [ ] Archive CSVs for governance record‑keeping.  

---

## 🧭 Governance Flow Diagram

Below is the governance flow diagram showing how Roles → Actions → Audit Trail → Exports connect.

![Governance Flow](images/governance_flow.png)

> Note: If your viewer does not render the image, ensure `images/governance_flow.png` exists relative to this README.

---

## 📝 Notes & Next Steps
- Add `requirements.txt` with: streamlit, pandas, plotly for reproducibility.
- GitHub does not render Mermaid natively — embedding a PNG/SVG ensures the diagram shows up for all viewers.
- I can add a static image (`images/governance_flow.png` or `docs/images/governance_flow.png`) and commit both files so the README renders correctly on GitHub.
