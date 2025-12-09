# Artist Gallery & Escrow Flow (Streamlit Integration)

This repository demonstrates how to manage an artist gallery with:
- **3×3 grid layout** (nine slots, rearrangeable)
- **2-year expiry per item** (refreshable upon notification)
- **7-day refund window** (escrow release logic)
- **Eco-impact anchors** (trees planted, ocean credits)

## Features
- Customer pays the app → funds held in escrow.
- Artist ships item → tracking recorded.
- Customer confirms receipt OR carrier shows delivered.
- 7-day refund/dispute window before auto-release.
- Notifications for expiry (2 years) and refund window (7 days).
- Gallery grid editable via Streamlit interface.

## Usage
1. Launch Streamlit app:
   ```bash
   streamlit run app.py
   ```
