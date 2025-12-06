import streamlit as st
import yaml
import pandas as pd
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="Compliance Monitoring", page_icon="📊", layout="wide")

# Load policy profiles
@st.cache_data
def load_policies():
    with open('policy_profiles.yaml', 'r') as f:
        return yaml.safe_load(f)

# Generate sample audit data
@st.cache_data
def generate_sample_audit_logs():
    profiles = ["UK_OSA_v1", "EU_DSA_v1", "US_Federal_v1", "AU_Ban_v1", "MY_OSA_v1"]
    signals = ["account_residency", "billing_country", "ip_geolocation", "device_locale"]
    
    logs = []
    for i in range(100):
        log = {
            "timestamp": datetime.now() - timedelta(days=random.randint(0, 30)),
            "session_id": f"sess_{random.randint(10000, 99999)}",
            "resolved_profile": random.choice(profiles),
            "confidence_score": random.randint(60, 100),
            "signals_used": random.sample(signals, k=random.randint(2, 4)),
            "vpn_detected": random.choice([True, False]),
            "overrides": random.choice([None, "manual_review", "appeal_granted"])
        }
        logs.append(log)
    
    return pd.DataFrame(logs)

st.title("📊 Compliance Monitoring & Audit")
st.write("**Regulator-ready transparency and enforcement tracking**")

st.divider()

try:
    policies = load_policies()
    audit_config = policies.get('audit_logging', {})
    
    # Audit configuration display
    st.subheader("⚙️ Audit Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Audit Logging", "✅ Enabled" if audit_config.get('enabled') else "❌ Disabled")
    with col2:
        st.metric("Data Retention", audit_config.get('retention', 'N/A'))
    with col3:
        st.metric("Logged Fields", len(audit_config.get('fields', [])))
    
    with st.expander("📋 Logged Fields"):
        for field in audit_config.get('fields', []):
            st.write(f"• `{field}`")
    
    st.divider()
    
    # Sample audit logs
    st.subheader("📝 Audit Log Entries (Last 30 Days)")
    
    df = generate_sample_audit_logs()
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        profile_filter = st.multiselect(
            "Filter by Profile",
            options=df['resolved_profile'].unique(),
            default=df['resolved_profile'].unique()
        )
    
    with col2:
        vpn_filter = st.selectbox("VPN Status", ["All", "Detected", "Not Detected"])
    
    with col3:
        min_confidence = st.slider("Min Confidence Score", 0, 100, 0)
    
    # Apply filters
    filtered_df = df[df['resolved_profile'].isin(profile_filter)]
    
    if vpn_filter == "Detected":
        filtered_df = filtered_df[filtered_df['vpn_detected'] == True]
    elif vpn_filter == "Not Detected":
        filtered_df = filtered_df[filtered_df['vpn_detected'] == False]
    
    filtered_df = filtered_df[filtered_df['confidence_score'] >= min_confidence]
    
    # Display stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Sessions", len(filtered_df))
    with col2:
        st.metric("VPN Detected", len(filtered_df[filtered_df['vpn_detected'] == True]))
    with col3:
        st.metric("Avg Confidence", f"{filtered_df['confidence_score'].mean():.1f}%")
    with col4:
        st.metric("Manual Overrides", len(filtered_df[filtered_df['overrides'].notna()]))
    
    # Profile distribution
    st.subheader("📈 Profile Distribution")
    profile_counts = filtered_df['resolved_profile'].value_counts()
    st.bar_chart(profile_counts)
    
    # Confidence distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Confidence Score Distribution")
        confidence_hist = pd.cut(filtered_df['confidence_score'], bins=[0, 60, 70, 80, 90, 100]).value_counts().sort_index()
        st.bar_chart(confidence_hist)
    
    with col2:
        st.subheader("🕒 Resolution Activity (Last 7 Days)")
        last_7_days = filtered_df[filtered_df['timestamp'] >= datetime.now() - timedelta(days=7)]
        daily_counts = last_7_days.groupby(last_7_days['timestamp'].dt.date).size()
        st.line_chart(daily_counts)
    
    st.divider()
    
    # Detailed log table
    st.subheader("🔍 Detailed Audit Logs")
    
    display_df = filtered_df.copy()
    display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    display_df['signals_used'] = display_df['signals_used'].apply(lambda x: ', '.join(x))
    
    st.dataframe(
        display_df[['timestamp', 'session_id', 'resolved_profile', 'confidence_score', 'signals_used', 'vpn_detected', 'overrides']],
        use_container_width=True,
        height=400
    )
    
    st.divider()
    
    # Transparency report
    st.subheader("📄 Transparency Report Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Profile-wise Enforcement**")
        for profile in df['resolved_profile'].unique():
            count = len(df[df['resolved_profile'] == profile])
            percentage = (count / len(df)) * 100
            st.write(f"• {profile}: {count} sessions ({percentage:.1f}%)")
    
    with col2:
        st.write("**Resolution Quality Metrics**")
        high_confidence = len(df[df['confidence_score'] >= 90])
        medium_confidence = len(df[(df['confidence_score'] >= 70) & (df['confidence_score'] < 90)])
        low_confidence = len(df[df['confidence_score'] < 70])
        
        st.write(f"• High confidence (≥90%): {high_confidence}")
        st.write(f"• Medium confidence (70-89%): {medium_confidence}")
        st.write(f"• Low confidence (<70%): {low_confidence}")
        st.write(f"• VPN-affected: {len(df[df['vpn_detected'] == True])}")
        st.write(f"• Manual overrides: {len(df[df['overrides'].notna()])}")
    
    # Export button
    st.divider()
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Audit Logs (CSV)",
        data=csv,
        file_name=f"audit_logs_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"❌ Error loading monitoring data: {str(e)}")

st.divider()

# Appeals & transparency
st.subheader("📢 User Transparency & Appeals")

ux_config = policies.get('ux_transparency', {})

col1, col2 = st.columns(2)

with col1:
    st.write("**User Notices:**")
    for notice in ux_config.get('notices', []):
        st.info(notice)

with col2:
    st.write("**Appeals Process:**")
    st.write(f"Channel: `{ux_config.get('appeals_channel', 'N/A')}`")
    st.write("Users can contest jurisdiction misclassification through in-app form with human review.")
