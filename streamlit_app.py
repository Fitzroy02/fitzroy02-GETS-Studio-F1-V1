import streamlit as st
import yaml
import pandas as pd
from pathlib import Path

# Load policy profiles
@st.cache_data
def load_policies():
    with open('policy_profiles.yaml', 'r') as f:
        return yaml.safe_load(f)

st.set_page_config(page_title="GETS Compliance Studio", page_icon="⚖️", layout="wide")

st.title("⚖️ GETS Compliance Studio")
st.write("**Policy-as-Code Governance Platform for Social Media Compliance**")

st.markdown("""
### Purpose
Automatic jurisdiction-aware enforcement without user controls. This platform resolves regional 
compliance requirements using signal-based detection and applies policy profiles server-side.

### Architecture
- **Policy-as-Code:** Versioned YAML profiles for UK OSA, EU DSA, US Federal, AU Ban, MY OSA
- **Jurisdiction Resolution:** Multi-signal detection (IP, account, billing, device)
- **Audit Logging:** Regulator-ready decision trails with 12-month retention
- **Zero User Choice:** Automatic profile assignment with transparency notices

### Tech Stack
- Streamlit · Python · YAML · Pandas
""")

st.divider()

# Display policy overview
st.subheader("📋 Active Policy Profiles")

try:
    policies = load_policies()
    profiles = policies.get('profiles', {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Jurisdictions", len(profiles))
    with col2:
        st.metric("Signal Sources", len(policies.get('signals', [])))
    with col3:
        st.metric("Audit Retention", policies.get('audit_logging', {}).get('retention', 'N/A'))
    
    st.divider()
    
    # Show profiles in expandable sections
    for profile_name, profile_data in profiles.items():
        with st.expander(f"🌍 {profile_data.get('jurisdiction', 'Unknown')} - {profile_name}"):
            st.write(f"**Regulator:** {profile_data.get('regulator', 'N/A')}")
            st.write(f"**Max Penalty:** {profile_data.get('penalties', {}).get('max_fine', 'N/A')}")
            
            requirements = profile_data.get('requirements', [])
            if requirements:
                st.write("**Requirements:**")
                for req in requirements:
                    if isinstance(req, dict):
                        for key, value in req.items():
                            st.write(f"- {key}: `{value}`")
                    else:
                        st.write(f"- {req}")

except FileNotFoundError:
    st.error("⚠️ policy_profiles.yaml not found. Please ensure the configuration file exists.")
except Exception as e:
    st.error(f"⚠️ Error loading policies: {str(e)}")
