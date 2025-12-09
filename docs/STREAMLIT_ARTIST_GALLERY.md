# Streamlit Artist Gallery — Expiry & Escrow Notices

## Features
- **3×3 gallery grid:** Nine slots, rearranged via select boxes.
- **2-year expiry:** Visible per item; warnings at **30 days** before expiry.
- **7-day refund window:** Starts on delivery confirmation; auto-release after window if no dispute.
- **Notices dashboard:** Summarizes upcoming expiries and active refund windows.

## Usage
1. **Install:** `pip install streamlit`
2. **Run:** `streamlit run app.py`
3. **Arrange gallery:** Use the selectors for Slot 1–9.
4. **Confirm delivery:** Click “Mark Delivered” per item to start the 7-day refund window.
5. **Monitor notices:** See expiry and refund windows in the Notices section.

## Governance
- **Payment direction:** Customer pays the app; funds held in escrow.
- **Verification logic:** Customer Received or carrier Delivered; if no dispute after 7 days, funds auto-release.
- **Expiry:** Each item expires **2 years** from upload; refresh upon notification.
- **Audit:** Log delivery confirmations and window closures (extend with external logs as needed).

## Customization
- **Item data:** Replace `SAMPLE_ITEMS` in `app.py` with your data source (JSON/DB/API).
- **Expiry windows:** Tune `EXPIRY_SOON_DAYS` and `EXPIRY_YEARS`.
- **Refund window:** Adjust `REFUND_WINDOW_DAYS` if governance changes.
