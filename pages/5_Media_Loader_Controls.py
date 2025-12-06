import streamlit as st
import yaml
import pandas as pd

st.set_page_config(page_title="Media Loader Controls", page_icon="🎬", layout="wide")

# Load configurations
@st.cache_data
def load_loader_config():
    with open('loader_config.yaml', 'r') as f:
        return yaml.safe_load(f)

@st.cache_data
def load_policies():
    with open('policy_profiles.yaml', 'r') as f:
        return yaml.safe_load(f)

st.title("🎬 Media Loader Governance")
st.write("**Jurisdiction-aware media controls without user override**")

st.divider()

try:
    loader_config = load_loader_config()
    policies = load_policies()
    
    # Overview metrics
    st.subheader("📊 Media Controls Overview")
    
    media_types = loader_config.get('media_types', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Media Types", len(media_types))
    with col2:
        age_gated = sum(1 for m in media_types.values() if m.get('controls', {}).get('age_gating', False))
        st.metric("Age-Gated Types", age_gated)
    with col3:
        audit_enabled = loader_config.get('audit_logging', {}).get('enabled', False)
        st.metric("Audit Logging", "✅ Enabled" if audit_enabled else "❌ Disabled")
    with col4:
        retention = loader_config.get('audit_logging', {}).get('retention', 'N/A')
        st.metric("Log Retention", retention)
    
    st.divider()
    
    # Media type selector
    st.subheader("🎯 Media Type Controls")
    
    selected_media = st.selectbox(
        "Select Media Type",
        options=list(media_types.keys()),
        format_func=lambda x: f"📁 {x.title()}"
    )
    
    if selected_media:
        media_data = media_types[selected_media]
        controls = media_data.get('controls', {})
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write("**General Controls:**")
            age_gating = controls.get('age_gating', False)
            st.write(f"• Age Gating: {'✅ Yes' if age_gating else '❌ No'}")
            
            st.divider()
            
            st.write("**Applicable Jurisdictions:**")
            jurisdiction_rules = controls.get('jurisdiction_rules', {})
            for profile in jurisdiction_rules.keys():
                st.write(f"• `{profile}`")
        
        with col2:
            st.write("**Jurisdiction-Specific Rules:**")
            
            jurisdiction_rules = controls.get('jurisdiction_rules', {})
            
            # Create comparison table
            comparison_data = []
            for profile_name, rules in jurisdiction_rules.items():
                row = {"Profile": profile_name}
                row.update(rules)
                comparison_data.append(row)
            
            if comparison_data:
                df = pd.DataFrame(comparison_data)
                st.dataframe(df, use_container_width=True)
        
        st.divider()
        
        # Detailed jurisdiction breakdown
        st.subheader(f"📋 {selected_media.title()} Rules by Jurisdiction")
        
        tabs = st.tabs(list(jurisdiction_rules.keys()))
        
        for idx, (profile_name, rules) in enumerate(jurisdiction_rules.items()):
            with tabs[idx]:
                # Get jurisdiction info from policy profiles
                profile_data = policies.get('profiles', {}).get(profile_name, {})
                jurisdiction = profile_data.get('jurisdiction', 'Unknown')
                regulator = profile_data.get('regulator', 'Unknown')
                
                st.write(f"**Jurisdiction:** {jurisdiction}")
                st.write(f"**Regulator:** {regulator}")
                
                st.divider()
                
                st.write(f"**Media Controls for {selected_media.title()}:**")
                
                for rule_key, rule_value in rules.items():
                    if rule_key == 'access':
                        if rule_value == 'disabled':
                            st.error(f"🚫 **Access:** Completely disabled")
                        elif rule_value == 'restricted':
                            st.warning(f"⚠️ **Access:** Restricted with conditions")
                        elif rule_value == 'allowed':
                            st.success(f"✅ **Access:** Allowed")
                        else:
                            st.info(f"ℹ️ **Access:** {rule_value}")
                    elif rule_key == 'min_age':
                        st.info(f"🎂 **Minimum Age:** {rule_value}+")
                    else:
                        formatted_key = rule_key.replace('_', ' ').title()
                        st.write(f"• **{formatted_key}:** `{rule_value}`")
    
    st.divider()
    
    # Media access matrix
    st.subheader("🗺️ Media Access Matrix Across Jurisdictions")
    
    # Build access matrix
    matrix_data = []
    profiles_list = list(policies.get('profiles', {}).keys())[:5]  # Top 5 profiles
    
    for media_type in media_types.keys():
        row = {"Media Type": media_type.title()}
        jurisdiction_rules = media_types[media_type].get('controls', {}).get('jurisdiction_rules', {})
        
        for profile in profiles_list:
            rules = jurisdiction_rules.get(profile, {})
            access = rules.get('access', 'allowed')
            min_age = rules.get('min_age', '-')
            
            if access == 'disabled':
                status = "🚫 Disabled"
            elif access == 'restricted':
                status = f"⚠️ Restricted ({min_age}+)" if min_age != '-' else "⚠️ Restricted"
            else:
                status = f"✅ Allowed ({min_age}+)" if min_age != '-' else "✅ Allowed"
            
            row[profile] = status
        
        matrix_data.append(row)
    
    matrix_df = pd.DataFrame(matrix_data)
    st.dataframe(matrix_df, use_container_width=True, height=300)
    
    st.divider()
    
    # Simulator
    st.subheader("🧪 Media Access Simulator")
    st.write("Test media access based on jurisdiction and user age")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sim_profile = st.selectbox(
            "Jurisdiction Profile",
            options=list(policies.get('profiles', {}).keys())
        )
    
    with col2:
        sim_media = st.selectbox(
            "Media Type",
            options=list(media_types.keys()),
            format_func=lambda x: x.title()
        )
    
    with col3:
        sim_age = st.number_input("User Age", min_value=1, max_value=100, value=15)
    
    if st.button("🎯 Check Access", type="primary"):
        media_rules = media_types[sim_media].get('controls', {}).get('jurisdiction_rules', {}).get(sim_profile, {})
        
        access_status = media_rules.get('access', 'allowed')
        min_age_requirement = media_rules.get('min_age', 0)
        
        st.divider()
        
        # Determine access
        if access_status == 'disabled':
            st.error(f"🚫 **Access Denied**")
            st.write(f"**Reason:** {sim_media.title()} is completely disabled in this jurisdiction.")
        elif access_status == 'restricted':
            if min_age_requirement and sim_age < min_age_requirement:
                st.error(f"🚫 **Access Denied**")
                st.write(f"**Reason:** User age ({sim_age}) is below minimum requirement ({min_age_requirement}+).")
            else:
                st.warning(f"⚠️ **Restricted Access Granted**")
                st.write(f"**Conditions:** Content is restricted but accessible with conditions.")
        else:
            if min_age_requirement and sim_age < min_age_requirement:
                st.error(f"🚫 **Access Denied**")
                st.write(f"**Reason:** User age ({sim_age}) is below minimum requirement ({min_age_requirement}+).")
            else:
                st.success(f"✅ **Access Granted**")
                st.write(f"**Status:** User meets all requirements for {sim_media.title()} content.")
        
        # Show applied rules
        st.divider()
        st.write("**Applied Rules:**")
        
        for rule_key, rule_value in media_rules.items():
            formatted_key = rule_key.replace('_', ' ').title()
            st.write(f"• {formatted_key}: `{rule_value}`")
        
        # Audit log entry
        st.divider()
        st.write("**Audit Log Entry:**")
        st.code(f"""{{
  "timestamp": "2025-12-06T10:45:00Z",
  "media_type": "{sim_media}",
  "jurisdiction_applied": "{sim_profile}",
  "user_age": {sim_age},
  "access_decision": "{'granted' if (access_status != 'disabled' and (not min_age_requirement or sim_age >= min_age_requirement)) else 'denied'}",
  "rules_applied": {media_rules},
  "override_reason": null
}}""", language="json")
    
    st.divider()
    
    # Default behavior
    st.subheader("🌐 Default Behavior for Unknown Jurisdictions")
    
    default_behavior = loader_config.get('default_behavior', {}).get('unknown_jurisdiction', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Applied Profile:** `{default_behavior.get('apply_profile', 'N/A')}`")
        st.warning(f"**Default Access:** `{default_behavior.get('access', 'N/A')}`")
    
    with col2:
        st.write("**User Notice:**")
        st.info(default_behavior.get('notices', 'N/A'))
    
    st.divider()
    
    # Audit configuration
    st.subheader("📝 Media Access Audit Configuration")
    
    audit_config = loader_config.get('audit_logging', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Status:**", "✅ Enabled" if audit_config.get('enabled') else "❌ Disabled")
        st.write("**Retention:**", audit_config.get('retention', 'N/A'))
    
    with col2:
        st.write("**Logged Fields:**")
        for field in audit_config.get('fields', []):
            st.write(f"• `{field}`")
    
    st.divider()
    
    # Raw config viewer
    st.subheader("📄 Raw Media Loader Configuration")
    
    with open('loader_config.yaml', 'r') as f:
        yaml_content = f.read()
    
    st.code(yaml_content, language="yaml")
    
    st.download_button(
        label="📥 Download loader_config.yaml",
        data=yaml_content,
        file_name="loader_config.yaml",
        mime="text/yaml"
    )

except FileNotFoundError as e:
    st.error(f"⚠️ Configuration file not found: {str(e)}")
except Exception as e:
    st.error(f"❌ Error loading media loader configuration: {str(e)}")

st.divider()

# Integration notes
st.subheader("🔧 Integration Notes")

st.markdown("""
**Server-Side Enforcement:**

```python
def get_media_access(user_age, jurisdiction_profile, media_type):
    # Load loader_config.yaml
    config = load_loader_config()
    
    # Get media rules for jurisdiction
    rules = config['media_types'][media_type]['controls']['jurisdiction_rules'].get(
        jurisdiction_profile, 
        config['default_behavior']['unknown_jurisdiction']
    )
    
    # Check access status
    access = rules.get('access', 'allowed')
    min_age = rules.get('min_age', 0)
    
    if access == 'disabled':
        return {'allowed': False, 'reason': 'Media type disabled in jurisdiction'}
    
    if min_age and user_age < min_age:
        return {'allowed': False, 'reason': f'Age requirement not met ({min_age}+)'}
    
    # Log decision
    audit_log({
        'timestamp': datetime.now(),
        'media_type': media_type,
        'jurisdiction_applied': jurisdiction_profile,
        'access_decision': 'granted',
        'user_age': user_age
    })
    
    return {'allowed': True, 'rules': rules}
```

**Key Principles:**
- Media controls applied **server-side** based on resolved jurisdiction
- No user selector for region or age bypass
- Access decisions logged for audit trail
- Unknown jurisdictions default to strictest_global behavior
- Appeals handled through compliance review, not user override
""")
