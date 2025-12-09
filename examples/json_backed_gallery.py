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
        # Initialize empty structure if file missing
        return {"items": [], "slots": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def expiry_date(upload_date):
    upload = datetime.date.fromisoformat(upload_date)
    try:
        return upload.replace(year=upload.year + EXPIRY_YEARS)
    except ValueError:
        return upload + datetime.timedelta(days=365 * EXPIRY_YEARS + 1)

# ---------------------------
# Load gallery data
# ---------------------------
data = load_data()

st.title("JSON-backed Artist Gallery")

# Display slots
st.header("Gallery Grid")
cols = st.columns(3)
slot_labels = list(data["slots"].keys())

for i, slot in enumerate(slot_labels):
    with cols[i % 3]:
        current_item = data["slots"].get(slot)
        st.write(f"**{slot}:** {current_item if current_item else 'Empty'}")

# ---------------------------
# Delivery confirmation
# ---------------------------
st.header("Delivery Confirmation")
for item in data["items"]:
    title = item["title"]
    delivery_date = item.get("delivery_date")
    if delivery_date:
        deadline = datetime.date.fromisoformat(delivery_date) + datetime.timedelta(days=REFUND_WINDOW_DAYS)
        st.info(f"{title} delivered on {delivery_date}. Refund window closes {deadline}.")
    else:
        if st.button(f"Mark Delivered: {title}"):
            item["delivery_date"] = str(datetime.date.today())
            save_data(data)
            st.success(f"Delivery confirmed for {title}.")

# ---------------------------
# Expiry notices
# ---------------------------
st.header("Expiry Notices")
today = datetime.date.today()
for item in data["items"]:
    exp = expiry_date(item["upload_date"])
    days_left = (exp - today).days
    if days_left <= 30:
        st.warning(f"🔔 {item['title']} will expire on {exp} ({days_left} days left).")
