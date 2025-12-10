# Minimal Streamlit snippet to surface contribution instructions
# Run with: pip install streamlit && streamlit run streamlit_app_contrib_snippet.py

import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Contributing", layout="centered")
st.title("How to Contribute")

st.markdown(
    """
This small helper app shows the repository's CONTRIBUTING guidelines and quick steps
to get started locally.

- Read the guideline below.
- Follow the "Getting started" section to set up your dev environment.
- Run tests and open a PR when ready.
"""
)

# Attempt to load CONTRIBUTING.md from a common path
possible_paths = [
    Path("contributing-guidelines/CONTRIBUTING.md"),
    Path("CONTRIBUTING.md"),
]

content = None
for p in possible_paths:
    if p.exists():
        content = p.read_text(encoding="utf-8")
        st.subheader(f"Loaded from {p}")
        break

if content:
    st.markdown(content)
else:
    st.warning(
        "CONTRIBUTING.md not found in repository paths. Place the file at "
        "`contributing-guidelines/CONTRIBUTING.md` or `CONTRIBUTING.md`."
    )

st.info("To run locally: `streamlit run streamlit_app_contrib_snippet.py`")
