import streamlit as st
import datetime
import json
import os

DATA_FILE = "gallery_data.json"
EXPIRY_YEARS = 2
REFUND_WINDOW_DAYS = 7

# ---------------------------
# Helpers for JSON persistence
# ---------------------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        return {"items": [], "slots": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ---------------------------
# Load gallery data
# ---------------------------
if "gallery_data" not in st.session_state:
    st.session_state.gallery_data = load_data()

data = st.session_state.gallery_data

st.title("JSON-backed Artist Gallery with Save/Load/Download")

# ---------------------------
# Save/Load controls
# ---------------------------
st.header("Save / Load / Download Controls")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💾 Save Gallery State"):
        save_data(data)
        st.success(f"Gallery state saved to {DATA_FILE}")

with col2:
    if st.button("📂 Load Gallery State"):
        st.session_state.gallery_data = load_data()
        st.success(f"Gallery state loaded from {DATA_FILE}")
        st.experimental_rerun()

with col3:
    # Convert current state to JSON string
    json_bytes = json.dumps(data, indent=2).encode("utf-8")
    st.download_button(
        label="⬇️ Download Gallery JSON",
        data=json_bytes,
        file_name="gallery_data.json",
        mime="application/json",
        help="Download the current gallery state as a JSON file."
    )
