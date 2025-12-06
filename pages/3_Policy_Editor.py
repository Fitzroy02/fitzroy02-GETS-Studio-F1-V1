import streamlit as st
import yaml
import pandas as pd

st.set_page_config(page_title="Policy Editor", page_icon="✏️", layout="wide")

# Load policy profiles
@st.cache_data
def load_policies():
    with open('policy_profiles.yaml', 'r') as f:
        return yaml.safe_load(f)

st.title("✏️ Policy-as-Code Editor")
st.write("**Version-controlled compliance profile management**")

st.divider()

try:
    policies = load_policies()
    profiles = policies.get('profiles', {})
    
    st.subheader("📦 Version Control & Governance")
    
    st.info("""
    **Best Practice:** Store `policy_profiles.yaml` in a Git repository with:
    - Branch protection on main
    - Required reviews from legal + compliance teams
    - Automated validation on pull requests
    - Immutable versioning (profile_name_v1, profile_name_v2)
    - Changelog tracking for regulator audits
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Active Profiles", len(profiles))
    with col2:
        st.metric("Policy Version", "1.0.0")
    with col3:
        st.metric("Last Updated", "2025-12-06")
    
    st.divider()
    
    # Profile selector
    st.subheader("🌍 Profile Management")
    
    selected_profile = st.selectbox(
        "Select Profile to View/Edit",
        options=list(profiles.keys())
    )
    
    if selected_profile:
        profile_data = profiles[selected_profile]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Current Profile Configuration:**")
            st.json(profile_data)
        
        with col2:
            st.write("**Profile Metadata:**")
            st.write(f"**Jurisdiction:** {profile_data.get('jurisdiction', 'N/A')}")
            st.write(f"**Regulator:** {profile_data.get('regulator', 'N/A')}")
            st.write(f"**Max Fine:** {profile_data.get('penalties', {}).get('max_fine', 'N/A')}")
            
            requirements = profile_data.get('requirements', [])
            st.write(f"**Total Requirements:** {len(requirements)}")
            
            st.divider()
            
            st.write("**⚠️ Edit Mode Disabled**")
            st.warning("""
            Direct editing is disabled in this demo. In production:
            1. Clone the policy repository
            2. Create a feature branch
            3. Edit `policy_profiles.yaml`
            4. Submit pull request with justification
            5. Require legal + compliance approval
            6. Merge to main (triggers deployment)
            """)
    
    st.divider()
    
    # Resolution rules editor
    st.subheader("⚙️ Resolution Rules Configuration")
    
    resolution_rules = policies.get('resolution_rules', {})
    
    tab1, tab2, tab3 = st.tabs(["Precedence", "Conflict Handling", "Edge Cases"])
    
    with tab1:
        st.write("**Current Signal Precedence:**")
        precedence = resolution_rules.get('precedence', [])
        for idx, signal in enumerate(precedence, 1):
            st.write(f"{idx}. `{signal}`")
        
        st.info("Higher priority signals override lower ones. Account-verified data is most reliable.")
    
    with tab2:
        st.write(f"**Conflict Strategy:** `{resolution_rules.get('conflict_handling', 'N/A')}`")
        st.write(f"**Default Profile:** `{resolution_rules.get('default_profile', 'N/A')}`")
        
        st.markdown("""
        **Conflict Resolution Logic:**
        - When signals point to different jurisdictions, apply the **stricter** compliance profile
        - Example: UK resident traveling in US → Apply UK OSA (stricter child protection)
        - Rationale: Over-compliance is safer than under-compliance
        """)
    
    with tab3:
        st.write(f"**VPN Handling:** `{resolution_rules.get('vpn_detection', 'N/A')}`")
        
        st.markdown("""
        **Edge Case Strategies:**
        
        1. **VPN/Proxy Detected:**
           - Fall back to account residency + billing country
           - Reduce confidence score by 20%
           - Flag for manual review if confidence < 60%
        
        2. **Roaming/Travel:**
           - Apply temporary overlay: local content rules + home privacy baseline
           - Re-evaluate every 24 hours
        
        3. **Insufficient Signals:**
           - Default to `strictest_global` profile
           - Prompt user to verify residency (optional, non-blocking)
           - Log for compliance review
        
        4. **Conflicting KYC:**
           - Prioritize government-issued ID over declared residency
           - Require re-verification if mismatch persists
        """)
    
    st.divider()
    
    # Signals configuration
    st.subheader("📡 Signal Configuration")
    
    signals = policies.get('signals', [])
    
    st.write("**Active Signals:**")
    
    signal_descriptions = {
        "ip_geolocation": "IP address → country/region lookup via MaxMind/IPinfo",
        "account_residency": "User-declared residency during signup (verified via KYC)",
        "billing_country": "Payment method country (credit card BIN, PayPal, etc.)",
        "device_locale": "OS language/region settings (iOS, Android)",
        "payment_bin": "Bank Identification Number from payment cards",
        "carrier_country": "Mobile carrier country from SIM card"
    }
    
    for signal in signals:
        with st.expander(f"📍 {signal}"):
            st.write(signal_descriptions.get(signal, "No description available"))
    
    st.divider()
    
    # Audit configuration
    st.subheader("📝 Audit Logging Configuration")
    
    audit_config = policies.get('audit_logging', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Status:**", "✅ Enabled" if audit_config.get('enabled') else "❌ Disabled")
        st.write("**Retention:**", audit_config.get('retention', 'N/A'))
    
    with col2:
        st.write("**Logged Fields:**")
        for field in audit_config.get('fields', []):
            st.write(f"• `{field}`")
    
    st.divider()
    
    # Raw YAML viewer
    st.subheader("📄 Raw Policy Configuration")
    
    with open('policy_profiles.yaml', 'r') as f:
        yaml_content = f.read()
    
    st.code(yaml_content, language="yaml")
    
    st.download_button(
        label="📥 Download policy_profiles.yaml",
        data=yaml_content,
        file_name="policy_profiles.yaml",
        mime="text/yaml"
    )

except Exception as e:
    st.error(f"❌ Error: {str(e)}")
