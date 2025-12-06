import streamlit as st
import pandas as pd
import yaml

st.set_page_config(page_title="Comparative Analysis", page_icon="🌍", layout="wide")

st.title("🌍 Comparative Compliance Matrix")
st.write("**Cross-jurisdictional regulatory divergence and overlap analysis**")

st.divider()

# Comparative matrix data
matrix_data = {
    "Dimension": [
        "Age Limits",
        "Content Moderation",
        "Transparency",
        "Scam / Fraud Liability",
        "Advertising Rules",
        "Data Protection",
        "Enforcement Body",
        "Penalties"
    ],
    "UK – Online Safety Act (OSA)": [
        "13+ (with stricter child protections)",
        "Remove illegal content; protect children",
        "Quarterly reports to Ofcom",
        "Platforms must act against harmful content",
        "Age-appropriate ads; parental empowerment",
        "UK GDPR alignment",
        "Ofcom",
        "Up to 10% global turnover"
    ],
    "EU – Digital Services Act (DSA/DMA)": [
        "Proposed 16+ minimum; varies by member state",
        "Remove illegal content within 24h; proactive risk assessments",
        "Ad repositories, algorithmic transparency, researcher access",
        "Platforms liable for financial scams; reimbursement obligations",
        "Mandatory ad transparency; ban on targeting minors",
        "EU GDPR alignment + DSA obligations",
        "European Commission",
        "Up to 6% global revenue"
    ],
    "US – Federal & State Frameworks": [
        "COPPA: under-13 data restrictions; state bills pushing 16+",
        "Section 230 immunity (narrowing); liability for harmful content debated",
        "FTC enforcement of disclosures; proposed ad revenue tax",
        "Bills emerging on fraud/deepfake liability",
        "FTC oversight; state bills on ad restrictions",
        "COPPA + state privacy laws (e.g., California CCPA)",
        "FTC, Congress, state AGs",
        "FTC fines; liability reforms pending"
    ],
    "Asia – Key Laws (AU, MY, IN, VN)": [
        "AU: ban under-16; MY: ban under-13, restrict under-16; IN: parental consent for minors",
        "VN: proactive monitoring; MY: licensing obligations; AU: strict bans",
        "IN: data protection transparency; VN: regulator reporting",
        "MY: licensing includes fraud monitoring; VN: strict liability",
        "AU/MY: restrictions on ads to minors; IN: DPDP limits profiling",
        "IN DPDP Act; VN data localization; MY licensing includes data rules",
        "AU eSafety Commissioner; MY Communications Ministry; IN IT Ministry; VN MIC",
        "AU: A$49.5m fines; MY: licensing revocation; VN: high penalties"
    ]
}

df = pd.DataFrame(matrix_data)

st.subheader("📊 Regulatory Comparison Across Jurisdictions")

# Display the full matrix
st.dataframe(
    df,
    use_container_width=True,
    height=600
)

st.divider()

# Key insights
st.subheader("⚖️ Strategic Insights for Automatic Enforcement")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Layered Compliance Approach:**
    
    1. **UK as Foundation**
       - Strong fines (10% global turnover)
       - Ofcom oversight with teeth
       - Child protection baseline (13+)
       - Quarterly transparency reports
    
    2. **EU Layer (Additional)**
       - Scam liability + reimbursement
       - 24h content removal SLA
       - Researcher data access
       - Algorithmic transparency
       - Stricter age limit (16+)
    
    3. **US Layer (Emerging)**
       - COPPA baseline (under-13)
       - Section 230 narrowing
       - State-level age verification
       - Fraud/deepfake liability bills
    """)

with col2:
    st.markdown("""
    **Asia Layer (Most Restrictive):**
    
    - **Australia:**
      - Under-16 social media ban
      - A$49.5m max penalties
      - eSafety Commissioner enforcement
    
    - **Malaysia:**
      - Under-13 ban, under-16 restrictions
      - Platform licensing requirements
      - Fraud monitoring obligations
    
    - **India:**
      - DPDP Act compliance
      - Parental consent for minors
      - Limited profiling/targeting
    
    - **Vietnam:**
      - Proactive content monitoring
      - Data localization requirements
      - Strict liability regime
    """)

st.divider()

# Divergence analysis
st.subheader("🔀 Key Divergences & Overlaps")

tab1, tab2, tab3, tab4 = st.tabs(["Age Limits", "Content Moderation", "Transparency", "Penalties"])

with tab1:
    st.markdown("""
    ### Age Limit Variance
    
    | Jurisdiction | Minimum Age | Verification | Notes |
    |--------------|-------------|--------------|-------|
    | UK | 13+ | Moderate | Stricter protections for children |
    | EU | 16+ (proposed) | Varies | Member state discretion |
    | US | 13+ (COPPA) | Emerging | State bills pushing 16+ |
    | Australia | 16+ (ban) | Strict | Social media ban under-16 |
    | Malaysia | 13+ (ban) | Required | Under-13 banned, under-16 restricted |
    | India | Varies | Parental consent | DPDP Act requirements |
    
    **Resolution Strategy:**
    - Apply **highest age limit** when signals conflict
    - AU user in EU → Apply AU ban (stricter)
    - US user with UK residency → Apply UK 13+ with protections
    """)

with tab2:
    st.markdown("""
    ### Content Moderation Requirements
    
    **Immediate Action (< 24h):**
    - EU DSA: 24h SLA for illegal content
    - Vietnam: Proactive monitoring required
    - Malaysia: Licensing obligations include monitoring
    
    **Risk-Based Approach:**
    - UK: Focus on child protection
    - US: Section 230 immunity narrowing
    - Australia: Strict bans on harmful content
    
    **Enforcement Priority:**
    1. Child sexual abuse material (CSAM) - global zero tolerance
    2. Terrorism content - EU 1h removal, UK immediate
    3. Hate speech - EU/UK proactive, US reactive
    4. Misinformation - varies widely by jurisdiction
    """)

with tab3:
    st.markdown("""
    ### Transparency Obligations
    
    **UK (Ofcom):**
    - Quarterly transparency reports
    - Child safety metrics
    - Complaints handling data
    
    **EU (Commission):**
    - Ad repositories (public access)
    - Algorithmic transparency reports
    - Researcher data access APIs
    - Risk assessment documentation
    
    **US (FTC):**
    - Disclosure of data practices
    - Ad revenue reporting (proposed)
    - State-level transparency bills
    
    **Asia:**
    - India: DPDP transparency notices
    - Vietnam: Regular regulator reporting
    - Malaysia: Licensing compliance audits
    """)

with tab4:
    st.markdown("""
    ### Penalty Comparison
    
    | Jurisdiction | Max Fine | Basis | Additional Sanctions |
    |--------------|----------|-------|---------------------|
    | UK | 10% global turnover | Annual revenue | Criminal liability for executives |
    | EU | 6% global revenue | Annual revenue | Service blocking |
    | US | Varies | Per violation | FTC enforcement actions |
    | Australia | A$49.5m | Fixed cap | eSafety blocking orders |
    | Malaysia | Licensing revocation | N/A | Criminal penalties |
    | Vietnam | High penalties | Varies | Service suspension |
    
    **Risk-Weighted Enforcement:**
    - UK has highest financial exposure (10% turnover)
    - Asia adds operational risk (licensing, blocking)
    - EU adds liability for scams/fraud
    - US adds emerging deepfake/fraud liability
    """)

st.divider()

# Automatic resolution logic
st.subheader("🧭 How Automatic Resolution Works")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **Step 1: Signal Collection**
    ```
    → IP Geolocation
    → Account Residency
    → Billing Country
    → Device Locale
    → Carrier Country
    → Payment BIN
    ```
    """)

with col2:
    st.markdown("""
    **Step 2: Jurisdiction Resolution**
    ```
    Precedence:
    1. Account (verified)
    2. Billing (payment)
    3. IP (location)
    4. Device (locale)
    
    → Apply stricter profile
    → Log decision trail
    → Calculate confidence
    ```
    """)

with col3:
    st.markdown("""
    **Step 3: Profile Application**
    ```
    → Age verification
    → Content filters
    → Ad restrictions
    → Data handling
    → Transparency notices
    → Audit logging
    ```
    """)

st.info("""
**Zero User Choice Principle:**
- Users never select their region
- No VPN circumvention allowed
- Automatic re-evaluation on signal change
- Appeals handled by human review (not user override)
""")

st.divider()

# Policy layering visualization
st.subheader("📚 Policy Layering Strategy")

layering_example = st.selectbox(
    "Select a scenario to see layered compliance:",
    [
        "UK Resident in UK (Simple)",
        "UK Resident Traveling in EU (Overlay)",
        "EU Resident with US Billing (Conflict)",
        "AU Minor Attempting Access (Strict Ban)",
        "VPN User with Mixed Signals (Fallback)"
    ]
)

if layering_example == "UK Resident in UK (Simple)":
    st.success("✅ **Single Profile Application: UK_OSA_v1**")
    st.markdown("""
    **Applied Rules:**
    - Age limit: 13+
    - UK GDPR compliance
    - Quarterly transparency reports
    - Child protection filters enabled
    - Max penalty exposure: 10% global turnover
    
    **Confidence:** 95% (account residency + IP match)
    """)

elif layering_example == "UK Resident Traveling in EU (Overlay)":
    st.warning("⚠️ **Temporary Overlay: UK_OSA_v1 + EU_DSA_v1 (local content)**")
    st.markdown("""
    **Layered Rules:**
    - Base profile: UK_OSA_v1 (privacy baseline)
    - Overlay: EU_DSA_v1 (local content moderation)
    - Age limit: Apply stricter (16+, per EU)
    - Content: EU local laws + UK protections
    - Data: UK GDPR baseline maintained
    
    **Duration:** Re-evaluate every 24 hours
    **Confidence:** 85% (account vs. IP conflict)
    """)

elif layering_example == "EU Resident with US Billing (Conflict)":
    st.info("🔄 **Conflict Resolution: Apply Stricter → EU_DSA_v1**")
    st.markdown("""
    **Resolution Logic:**
    1. Account residency: EU (verified)
    2. Billing country: US (payment card)
    3. **Decision:** Prioritize account residency
    4. **Applied profile:** EU_DSA_v1
    
    **Applied Rules:**
    - Age limit: 16+ (stricter than US 13+)
    - EU GDPR + DSA obligations
    - Scam liability: Yes
    - Researcher access: Required
    
    **Confidence:** 90% (account precedence)
    """)

elif layering_example == "AU Minor Attempting Access (Strict Ban)":
    st.error("🚫 **Access Denied: AU_Ban_v1 (Under-16 Ban)**")
    st.markdown("""
    **Enforcement:**
    - Age verification: Strict (government ID or equivalent)
    - Social media access: **BLOCKED** for under-16
    - Penalty risk: A$49.5m for non-compliance
    - Appeals: Human review only (no user override)
    
    **User Notice:**
    > "Access to social media services is restricted for users under 16 in Australia. 
    > This is required by law. If you believe this is an error, you may appeal through 
    > our verification process."
    
    **No circumvention allowed** (VPN detection active)
    """)

elif layering_example == "VPN User with Mixed Signals (Fallback)":
    st.warning("⚠️ **Fallback Mode: Apply Strictest_Global + Manual Review Flag**")
    st.markdown("""
    **Detected Issues:**
    - VPN/proxy detected: ✅
    - IP location: Obfuscated
    - Account residency: Not verified
    - Billing country: Available (fallback signal)
    
    **Resolution:**
    1. Fall back to billing country + device locale
    2. Reduce confidence score by 20%
    3. Apply **strictest_global** profile if confidence < 60%
    4. Flag for manual review
    
    **Applied Profile:** Strictest_Global (composite)
    - Age limit: 16+ (EU standard)
    - Content moderation: Proactive (VN/MY standard)
    - Data protection: GDPR+ (EU standard)
    - Penalties: Highest exposure
    
    **Confidence:** 55% (VPN penalty applied)
    **Review Status:** Queued for human verification
    """)

st.divider()

# Export matrix
st.subheader("📥 Export Compliance Matrix")

csv = df.to_csv(index=False)
st.download_button(
    label="Download Comparative Matrix (CSV)",
    data=csv,
    file_name="compliance_matrix.csv",
    mime="text/csv"
)

# JSON export for developers
matrix_json = df.to_json(orient="records", indent=2)
st.download_button(
    label="Download as JSON (Developer Format)",
    data=matrix_json,
    file_name="compliance_matrix.json",
    mime="application/json"
)
