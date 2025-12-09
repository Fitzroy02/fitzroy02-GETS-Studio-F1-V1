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
role = st.sidebar.radio("Select Dashboard", ["Doctor", "Patient", "Co-worker"])

# ---------------------------
# Doctor Dashboard
# ---------------------------
if role == "Doctor":
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
elif role == "Patient":
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
elif role == "Co-worker":
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




