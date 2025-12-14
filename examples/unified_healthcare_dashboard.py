import streamlit as st
import json
import datetime

DATA_FILE = "dashboard_data.json"

# ---------------------------
# Load JSON data
# ---------------------------
def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

data = load_data()

st.set_page_config(page_title="Unified Healthcare Dashboard", layout="wide")
st.title("Unified Healthcare Dashboard")

# ---------------------------
# Sidebar navigation
# ---------------------------
tab = st.sidebar.radio("Select Dashboard", ["Doctor", "Patient", "Co-worker", "Audit Trail"])

# ---------------------------
# Audit Trail Tab
# ---------------------------
if tab == "Audit Trail":
    st.header("📜 Audit Trail")

    # Build DataFrame from audit trail
    import pandas as pd
    rows = []
    users = {u["id"]: u for u in data.get("users", [])}
    for entry in data["audit_trail"]:
        ts = datetime.datetime.fromisoformat(entry["timestamp"].replace("Z", ""))
        actor_id = entry["actor_id"]
        actor = users.get(actor_id, {})
        role = actor.get("role", "Unknown")
        rows.append({
            "timestamp": ts,
            "date": ts.date(),
            "actor_id": actor_id,
            "actor_name": actor.get("name", actor_id),
            "role": role,
            "action": entry.get("action"),
            "target": entry.get("target"),
            "notes": entry.get("notes", "")
        })
    df = pd.DataFrame(rows)

    # Filters
    roles = ["All"] + sorted(df["role"].dropna().unique().tolist())
    selected_role = st.selectbox("Filter by Role", roles)
    date_min, date_max = df["date"].min(), df["date"].max()
    start_date = st.date_input("Start Date", value=date_min)
    end_date = st.date_input("End Date", value=date_max)

    mask = (df["date"] >= start_date) & (df["date"] <= end_date)
    if selected_role != "All":
        mask &= df["role"] == selected_role
    df_f = df.loc[mask].copy()

    st.subheader("Daily Activity Summary")
    if df_f.empty:
        st.warning("No events in the selected range/role for daily summary.")
    else:
        daily = df_f.groupby(["date", "role"]).size().reset_index(name="count")
        import plotly.express as px
        fig_daily = px.bar(
            daily, x="date", y="count", color="role",
            barmode="group", title="Actions per Role per Day"
        )
        st.plotly_chart(fig_daily, use_container_width=True)

    st.subheader("Quarterly Activity Summary")
    if df_f.empty:
        st.warning("No events in the selected range/role for quarterly summary.")
    else:
        df_f["quarter"] = df_f["timestamp"].dt.to_period("Q").astype(str)
        quarterly = df_f.groupby(["quarter", "role"]).size().reset_index(name="count")
        fig_quarter = px.bar(
            quarterly, x="quarter", y="count", color="role",
            barmode="group", title="Actions per Role per Quarter"
        )
        st.plotly_chart(fig_quarter, use_container_width=True)

    with st.expander("Show timeline (compact view)"):
        if df_f.empty:
            st.write("No events to show.")
        else:
            fig_timeline = px.scatter(
                df_f, x="timestamp", y="role", color="role",
                hover_data=["actor_name", "action", "target", "notes"],
                title="Audit Timeline (role vs time)"
            )
            fig_timeline.update_traces(marker=dict(size=10))
            st.plotly_chart(fig_timeline, use_container_width=True)

# ---------------------------
# Doctor Dashboard
# ---------------------------
elif tab == "Doctor":
    st.header("👩‍⚕️ Doctor Dashboard")
    st.subheader("Patient Records")
    for record in data["records"]:
        st.write(f"**{record['title']}** — {record['notes']}")
        st.caption(f"Created by {record['created_by']} on {record['created_at']}")
        if st.button(f"Edit {record['title']}"):
            st.text_area("Update Notes", value=record["notes"], key=f"edit_{record['record_id']}")

    st.subheader("Meetings")
    for meeting in data["meetings"]:
        st.write(f"📅 {meeting['title']} — {meeting['scheduled_at']}")
        st.caption(f"Participants: {', '.join(meeting['participants'])}")

    st.subheader("Files")
    for file in data["files"]:
        st.write(f"📄 {file['title']} ({file['type']})")
        st.caption(f"Shared with: {', '.join(file['shared_with'])}")

# ---------------------------
# Patient Dashboard
# ---------------------------
elif tab == "Patient":
    st.header("🧑 Patient Dashboard")
    patient_id = "u002"  # Example patient
    st.subheader("My Records")
    for record in data["records"]:
        if record["patient_id"] == patient_id:
            st.write(f"**{record['title']}** — {record['notes']}")
            st.caption(f"Doctor: {record['created_by']} • Status: {record['status']}")

    st.subheader("My Meetings")
    for meeting in data["meetings"]:
        if patient_id in meeting["participants"]:
            st.write(f"📅 {meeting['title']} — {meeting['scheduled_at']}")
            st.caption(f"Location: {meeting['location']}")

    st.subheader("My Files")
    for file in data["files"]:
        if patient_id in file["shared_with"]:
            st.write(f"📄 {file['title']} ({file['type']})")
            st.caption(f"Permissions: {file['permissions'].get(patient_id)}")

# ---------------------------
# Co-worker Dashboard
# ---------------------------
elif tab == "Co-worker":
    st.header("👩‍💼 Co-worker Dashboard")
    st.subheader("Reports to Fill")
    for record in data["records"]:
        st.write(f"**{record['title']}** — {record['notes']}")
        if st.button(f"Add Notes to {record['title']}"):
            st.text_area("Nursing Observations", key=f"coworker_{record['record_id']}")

    st.subheader("Team Meetings")
    for meeting in data["meetings"]:
        st.write(f"📅 {meeting['title']} — {meeting['scheduled_at']}")
        st.caption(f"Participants: {', '.join(meeting['participants'])}")

    st.subheader("Shared Files")
    for file in data["files"]:
        if "u003" in file["shared_with"]:
            st.write(f"📄 {file['title']} ({file['type']})")
            st.caption(f"Permissions: {file['permissions'].get('u003')}")
