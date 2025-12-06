import streamlit as st
import yaml
import pandas as pd
import random

st.set_page_config(page_title="Jurisdiction Resolution", page_icon="🌐", layout="wide")

# Load policy profiles
@st.cache_data
def load_policies():
    with open('policy_profiles.yaml', 'r') as f:
        return yaml.safe_load(f)

st.title("🌐 Jurisdiction Resolution Engine")
st.write("**Signal-based policy profile assignment without user controls**")

st.divider()

# Resolution rules display
st.subheader("📋 Resolution Rules")

try:
    policies = load_policies()
    resolution_rules = policies.get('resolution_rules', {})
    signals = policies.get('signals', [])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Signal Precedence Order:**")
        for idx, signal in enumerate(resolution_rules.get('precedence', []), 1):
            st.write(f"{idx}. `{signal}`")
        
        st.write("")
        st.write(f"**Conflict Handling:** `{resolution_rules.get('conflict_handling', 'N/A')}`")
        st.write(f"**VPN Detection:** `{resolution_rules.get('vpn_detection', 'N/A')}`")
        st.write(f"**Default Profile:** `{resolution_rules.get('default_profile', 'N/A')}`")
    
    with col2:
        st.write("**Available Signals:**")
        for signal in signals:
            st.write(f"• `{signal}`")
    
    st.divider()
    
    # Simulator
    st.subheader("🔬 Resolution Simulator")
    st.write("Simulate jurisdiction detection based on signal inputs")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        account_residency = st.selectbox("Account Residency", ["", "United Kingdom", "European Union", "United States", "Australia", "Malaysia"])
        billing_country = st.selectbox("Billing Country", ["", "UK", "FR", "DE", "US", "AU", "MY"])
    
    with col2:
        ip_location = st.selectbox("IP Geolocation", ["", "London, UK", "Paris, FR", "New York, US", "Sydney, AU", "Kuala Lumpur, MY"])
        device_locale = st.selectbox("Device Locale", ["", "en-GB", "en-US", "en-AU", "fr-FR", "de-DE", "ms-MY"])
    
    with col3:
        carrier = st.selectbox("Carrier Country", ["", "UK", "US", "AU", "FR", "MY"])
        vpn_detected = st.checkbox("VPN Detected")
    
    if st.button("🎯 Resolve Jurisdiction", type="primary"):
        # Simple resolution logic for demo
        profile_map = {
            "United Kingdom": "UK_OSA_v1",
            "European Union": "EU_DSA_v1",
            "United States": "US_Federal_v1",
            "Australia": "AU_Ban_v1",
            "Malaysia": "MY_OSA_v1"
        }
        
        resolved_profile = None
        confidence = 0
        signals_used = []
        
        # Precedence: account_residency > billing_country > ip_geolocation
        if account_residency:
            resolved_profile = profile_map.get(account_residency)
            confidence = 95
            signals_used.append("account_residency")
        elif billing_country:
            # Map billing to region
            billing_map = {"UK": "UK_OSA_v1", "FR": "EU_DSA_v1", "DE": "EU_DSA_v1", 
                          "US": "US_Federal_v1", "AU": "AU_Ban_v1", "MY": "MY_OSA_v1"}
            resolved_profile = billing_map.get(billing_country)
            confidence = 85
            signals_used.append("billing_country")
        elif ip_location:
            # Map IP to region
            if "UK" in ip_location:
                resolved_profile = "UK_OSA_v1"
            elif "FR" in ip_location or "DE" in ip_location:
                resolved_profile = "EU_DSA_v1"
            elif "US" in ip_location:
                resolved_profile = "US_Federal_v1"
            elif "AU" in ip_location:
                resolved_profile = "AU_Ban_v1"
            elif "MY" in ip_location:
                resolved_profile = "MY_OSA_v1"
            confidence = 70
            signals_used.append("ip_geolocation")
        
        if vpn_detected:
            confidence -= 20
            signals_used.append("vpn_detection_applied")
        
        if device_locale:
            signals_used.append("device_locale")
        
        if resolved_profile:
            st.success(f"✅ **Resolved Profile:** `{resolved_profile}`")
            st.info(f"🎯 **Confidence Score:** {confidence}%")
            st.write(f"**Signals Used:** {', '.join(signals_used)}")
            
            # Show profile details
            profiles = policies.get('profiles', {})
            profile_data = profiles.get(resolved_profile, {})
            
            st.divider()
            st.write("**Applied Profile Details:**")
            st.write(f"📍 **Jurisdiction:** {profile_data.get('jurisdiction', 'N/A')}")
            st.write(f"🏛️ **Regulator:** {profile_data.get('regulator', 'N/A')}")
            st.write(f"💰 **Max Penalty:** {profile_data.get('penalties', {}).get('max_fine', 'N/A')}")
            
            # User notice
            st.divider()
            ux_notice = policies.get('ux_transparency', {}).get('notices', [])[0] if policies.get('ux_transparency', {}).get('notices') else "Content adjusted for local compliance."
            st.warning(f"👤 **User Notice:** {ux_notice}")
        else:
            st.error("⚠️ Unable to resolve jurisdiction. Applying `strictest_global` profile.")
            st.write("**Reason:** Insufficient or conflicting signals")

except Exception as e:
    st.error(f"❌ Error: {str(e)}")

st.divider()

# Audit log preview
st.subheader("📝 Sample Audit Log Entry")
st.code("""
{
  "timestamp": "2025-12-06T10:30:45Z",
  "user_id": "hashed_12345",
  "resolved_profile": "UK_OSA_v1",
  "signals_used": ["account_residency", "billing_country"],
  "confidence_score": 95,
  "overrides": null,
  "vpn_detected": false
}
""", language="json")
