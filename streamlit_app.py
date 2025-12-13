import streamlit as st
import streamlit.components.v1 as components
import yaml
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from io import BytesIO
import html
import re

# Constants
ALLOCATION_ROUNDING_TOLERANCE = 0.01  # Tolerance for rounding drift correction

# Load policy profiles
@st.cache_data
def load_policies():
    with open('policy_profiles.yaml', 'r') as f:
        return yaml.safe_load(f)

# Load hospital configuration
@st.cache_data
def load_hospital_config():
    """Load hospital_config.yaml if it exists, return empty dict otherwise."""
    try:
        with open('hospital_config.yaml', 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        st.warning(f"Error loading hospital_config.yaml: {str(e)}")
        return {}

def sanitize_filename(name):
    """Sanitize a string to be safe for use in filenames."""
    # Remove or replace unsafe characters
    safe_name = re.sub(r'[^\w\s-]', '', name)
    safe_name = re.sub(r'[\s]+', '_', safe_name)
    safe_name = safe_name.strip('_').lower()
    # Prevent empty filenames
    if not safe_name:
        safe_name = 'hospital_scorecard'
    return safe_name

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

# ============================================================================
# Multi-Area Postcode/Region Feed Mockup
# ============================================================================

st.divider()
st.header("📍 Multi-Area Feed Mockup")

# Advertising Rules Documentation
AD_RULES_MD = """
### 📜 Advertising Rules

**Local Advertising Rules (applies to Home Area only):**
- Financial category ads are excluded across all scopes
- When viewing your **Home Area** with **Local** scope:
  - Ads from sponsors outside your home region will have their logos and names hidden
  - A warning message explains why the sponsor identity is hidden
- Other followed areas are **view-only** and do not apply home-area logo hiding
- Regional and National scopes show all sponsors normally (except excluded categories)

**Important:** Local advertising rules apply only to your registered/home postcode. Other followed areas are view-only.
"""

st.markdown(AD_RULES_MD)

# Defaults for session state
DEFAULT_HOME_AREA = 'SW1A'  # London
DEFAULT_FOLLOWED_AREAS = [DEFAULT_HOME_AREA]

# CSS Styles for feed items
STYLE_POST = "background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 10px;"
STYLE_AD = "background-color: #e8f5e9; padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 2px solid #4caf50;"
STYLE_WARNING = "background-color: #fff3cd; padding: 8px; border-radius: 5px; margin-top: 5px; font-size: 0.85em;"
BADGE_HOME = '<span style="background-color: #FFD700; padding: 2px 6px; border-radius: 3px; font-size: 0.8em;">🏠 Home</span>'
BADGE_HOME_LOCAL_RULES = '<span style="background-color: #FFD700; padding: 2px 6px; border-radius: 3px; font-size: 0.8em;">🏠 Home - Local Rules Apply</span>'
BADGE_VIEW_ONLY = '<span style="background-color: #87CEEB; padding: 2px 6px; border-radius: 3px; font-size: 0.8em;">👁️ View Only</span>'

# Postcode to Region Mapping (Mock data - in production, replace with geocoding API)
POSTCODE_REGION_MAP = {
    # London postcodes
    'SW1A': 'London',
    'E1': 'London',
    'W1': 'London',
    'N1': 'London',
    'SE1': 'London',
    'EC1': 'London',
    # Manchester postcodes
    'M1': 'Manchester',
    'M2': 'Manchester',
    'M3': 'Manchester',
    'M4': 'Manchester',
    # Birmingham postcodes
    'B1': 'Birmingham',
    'B2': 'Birmingham',
    'B3': 'Birmingham',
    # Leeds postcodes
    'LS1': 'Leeds',
    'LS2': 'Leeds',
    # Glasgow postcodes
    'G1': 'Glasgow',
    'G2': 'Glasgow',
    # Edinburgh postcodes
    'EH1': 'Edinburgh',
    'EH2': 'Edinburgh',
    # Bristol postcodes
    'BS1': 'Bristol',
    'BS2': 'Bristol',
}

def resolve_postcode_to_region(postcode):
    """
    Mock postcode to region resolver.
    In production, replace with geocoding API (e.g., postcodes.io, Google Maps API).
    
    Args:
        postcode: String like 'SW1A', 'M1', etc.
    
    Returns:
        Region name or 'Unknown'
    """
    postcode_clean = postcode.strip().upper()
    return POSTCODE_REGION_MAP.get(postcode_clean, 'Unknown')

def regions_match(region1, region2):
    """
    Forgiving region matcher.
    Case-insensitive, handles whitespace variations.
    
    Args:
        region1: First region string
        region2: Second region string
    
    Returns:
        True if regions match (case-insensitive, stripped), False otherwise
    """
    if not region1 or not region2:
        return False
    return region1.strip().lower() == region2.strip().lower()

# Initialize session state
if 'followed_areas' not in st.session_state:
    st.session_state['followed_areas'] = DEFAULT_FOLLOWED_AREAS.copy()
if 'home_area' not in st.session_state:
    st.session_state['home_area'] = DEFAULT_HOME_AREA

# Area Management UI
with st.expander("🗺️ Manage Followed Areas", expanded=False):
    st.info("""
    **Note:** Local advertising rules apply only to your registered/home postcode.
    Other followed areas are view-only and do not enforce home-area logo hiding.
    """)
    
    st.write("**Your Followed Areas:**")
    
    # Display current areas with badges and controls
    for i, area in enumerate(st.session_state['followed_areas']):
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        
        with col1:
            is_home = (area == st.session_state['home_area'])
            region = resolve_postcode_to_region(area)
            if is_home:
                st.write(f"📍 **{area}** ({region}) 🏠 *Home - Local Rules Apply*")
            else:
                st.write(f"📍 **{area}** ({region}) 👁️ *Viewing Only*")
        
        with col2:
            if not is_home:
                if st.button(f"Set as Home", key=f"home_{i}"):
                    st.session_state['home_area'] = area
                    st.rerun()
        
        with col3:
            pass  # Reserved for future controls
        
        with col4:
            if len(st.session_state['followed_areas']) > 1:
                if st.button("❌", key=f"remove_{i}"):
                    st.session_state['followed_areas'].pop(i)
                    # If removed area was home, set first area as new home
                    if area == st.session_state['home_area'] and st.session_state['followed_areas']:
                        st.session_state['home_area'] = st.session_state['followed_areas'][0]
                    st.rerun()
    
    # Add new area
    st.write("**Add New Area:**")
    col_add1, col_add2 = st.columns([3, 1])
    
    with col_add1:
        new_area = st.text_input(
            "Enter postcode (e.g., SW1A, M1, B1)",
            key="new_area_input",
            help="Examples: SW1A (London), M1 (Manchester), B1 (Birmingham)"
        )
    
    with col_add2:
        st.write("")  # Spacer
        st.write("")  # Spacer
        if st.button("➕ Add", key="add_area_btn"):
            if new_area and new_area not in st.session_state['followed_areas']:
                if len(st.session_state['followed_areas']) < 4:
                    st.session_state['followed_areas'].append(new_area.strip().upper())
                    st.rerun()
                else:
                    st.warning("⚠️ Maximum 4 areas allowed")
            elif new_area in st.session_state['followed_areas']:
                st.info("ℹ️ Area already followed")

# Feed Scope Selection
st.write("**Feed Scope:**")
feed_scope = st.radio(
    "Select feed scope",
    options=["Local", "Regional", "National"],
    horizontal=True,
    help="Local: Area-specific content with advertising rules. Regional: Broader region. National: Nationwide content."
)

# Mock Feed Data Generator
def generate_mock_feed(scope, followed_areas, home_area):
    """
    Generate mock feed data with posts and ads.
    
    Args:
        scope: 'Local', 'Regional', or 'National'
        followed_areas: List of postcodes
        home_area: User's home postcode
    
    Returns:
        List of feed items (dicts with type, content, metadata)
    """
    feed_items = []
    
    # For each followed area, generate content
    for area in followed_areas:
        region = resolve_postcode_to_region(area)
        is_home = (area == home_area)
        
        # Posts
        feed_items.append({
            'type': 'post',
            'area': area,
            'region': region,
            'is_home': is_home,
            'content': f'Community update from {area} ({region}): Local park renovation project completed!',
            'author': 'Community Council',
            'timestamp': '2 hours ago'
        })
        
        # Local business ad (same region as area)
        feed_items.append({
            'type': 'ad',
            'area': area,
            'region': region,
            'is_home': is_home,
            'content': f'Special offer: 20% off at {region} Coffee Shop!',
            'sponsor_name': f'{region} Local Business',
            'sponsor_region': region,
            'sponsor_logo': '☕',
            'category': 'local_business',
            'scope': scope
        })
        
        # Ad from different region (for demo purposes)
        # Get a list of all available regions and pick one different from current
        all_regions = list(set(POSTCODE_REGION_MAP.values()))
        other_regions = [r for r in all_regions if r != region]
        other_region = other_regions[0] if other_regions else 'London'
        
        feed_items.append({
            'type': 'ad',
            'area': area,
            'region': region,
            'is_home': is_home,
            'content': f'New restaurant opening in {other_region}!',
            'sponsor_name': f'{other_region} Dining Co.',
            'sponsor_region': other_region,
            'sponsor_logo': '🍽️',
            'category': 'dining',
            'scope': scope
        })
        
        # Financial ad (should be excluded)
        feed_items.append({
            'type': 'ad',
            'area': area,
            'region': region,
            'is_home': is_home,
            'content': 'Investment opportunity - High returns!',
            'sponsor_name': 'Finance Corp',
            'sponsor_region': region,
            'sponsor_logo': '💰',
            'category': 'financial',
            'scope': scope
        })
        
        # Another post
        feed_items.append({
            'type': 'post',
            'area': area,
            'region': region,
            'is_home': is_home,
            'content': f'Event announcement: {region} Arts Festival next weekend!',
            'author': 'Local Events Team',
            'timestamp': '5 hours ago'
        })
    
    return feed_items

# Generate and render feed
st.subheader(f"📱 Combined Feed ({feed_scope} Scope)")

feed_items = generate_mock_feed(feed_scope, st.session_state['followed_areas'], st.session_state['home_area'])

# Render feed items
for item in feed_items:
    # Rule 1: Exclude financial category across all scopes
    if item.get('category') == 'financial':
        continue
    
    # Determine if logo/name hiding applies
    hide_sponsor_identity = False
    
    if item['type'] == 'ad' and feed_scope == 'Local':
        # Check if this is the home area and sponsor is from different region
        if item['is_home']:
            home_region = resolve_postcode_to_region(st.session_state['home_area'])
            sponsor_region = item.get('sponsor_region', '')
            
            if not regions_match(home_region, sponsor_region):
                hide_sponsor_identity = True
    
    # Render the item
    if item['type'] == 'post':
        badge = BADGE_HOME if item['is_home'] else BADGE_VIEW_ONLY
        with st.container():
            st.markdown(f"""
            <div style='{STYLE_POST}'>
                <strong>📝 {item['author']}</strong> · <em>{item['timestamp']}</em> · 📍 {item['area']} ({item['region']})
                {badge}
                <p>{item['content']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    elif item['type'] == 'ad':
        with st.container():
            # Determine sponsor display
            if hide_sponsor_identity:
                sponsor_display = "⚠️ [Sponsor Identity Hidden]"
                logo_display = "❓"
                warning_msg = f"""
                <div style='{STYLE_WARNING}'>
                    <strong>ℹ️ Notice:</strong> Sponsor logo and name hidden due to local advertising rules. 
                    This sponsor is not from your home region ({resolve_postcode_to_region(st.session_state['home_area'])}).
                </div>
                """
            else:
                sponsor_display = item.get('sponsor_name', 'Unknown Sponsor')
                logo_display = item.get('sponsor_logo', '📢')
                warning_msg = ""
            
            badge = BADGE_HOME_LOCAL_RULES if item['is_home'] else BADGE_VIEW_ONLY
            st.markdown(f"""
            <div style='{STYLE_AD}'>
                <strong>📢 Sponsored</strong> · 📍 {item['area']} ({item['region']})
                {badge}
                <p>{logo_display} <strong>{sponsor_display}</strong></p>
                <p>{item['content']}</p>
                {warning_msg}
            </div>
            """, unsafe_allow_html=True)

st.divider()

# ============================================================================
# Hospital Preventive Care Scorecard
# ============================================================================

st.divider()
st.header("🏥 Hospital Preventive Care Scorecard")

# Load hospital configuration
hospital_config_data = load_hospital_config()
hospital_config = hospital_config_data.get('hospital', {})

# Check if configuration exists
if not hospital_config:
    st.info("""
    ℹ️ **Configuration not found**
    
    To customize funding levels and allocation rules, add a `hospital_config.yaml` file at the repository root.
    
    The file should include:
    - Hospital name and reporting period
    - Department funding levels (low/medium/high)
    - Reward allocation ratios
    - Preventive gate score threshold
    """)

# Default values and configuration
hospital_name = hospital_config.get('name', 'General Hospital')
reporting_period = hospital_config.get('reporting_period', '5-Year Rolling Average')
sapling_cost = hospital_config.get('sapling_cost_gbp', 50)
least_funded_ratio = hospital_config.get('reward_split', {}).get('least_funded_ratio', 0.8)
others_ratio = hospital_config.get('reward_split', {}).get('others_ratio', 0.2)
preventive_gate_score = hospital_config.get('preventive_gate_score', 60)

# Display header information
st.subheader(f"📊 {hospital_name}")
st.write(f"**Period:** {reporting_period}")
st.write(f"**Sapling Cost:** £{sapling_cost} per tree")

# Default department data (sample dataset)
default_data = {
    'Department': ['Paediatrics', 'Mental Health', 'Cardiology', 'Obstetrics/Gynecology', 'Community Health'],
    'Points (5yr avg)': [950, 820, 880, 1050, 790],
    'Score (%)': [78, 65, 72, 85, 62]
}

# Create DataFrame
df = pd.DataFrame(default_data)

# Apply funding levels and notes from config if available
config_departments = hospital_config.get('departments', {})
if config_departments:
    df['Funding Level'] = df['Department'].map(
        lambda dept: config_departments.get(dept, {}).get('funding_level', 'medium')
    )
    df['Notes'] = df['Department'].map(
        lambda dept: config_departments.get(dept, {}).get('notes', '')
    )
else:
    df['Funding Level'] = 'medium'
    df['Notes'] = ''

# Determine least-funded department
# Priority: 1) funding_level == 'low' from config, 2) fallback to lowest score
least_funded_dept = None
selection_method = "Not determined"

low_funded_depts = df[df['Funding Level'] == 'low']['Department'].tolist()
if low_funded_depts:
    least_funded_dept = low_funded_depts[0]  # Pick first if multiple
    selection_method = "Config (funding_level: low)"
else:
    # Fallback to lowest score
    lowest_score_idx = df['Score (%)'].idxmin()
    least_funded_dept = df.loc[lowest_score_idx, 'Department']
    selection_method = "Fallback (lowest score)"

# Display least-funded department metric
st.metric(
    label="🎯 Least-Funded Department",
    value=least_funded_dept,
    help=f"Selection method: {selection_method}"
)

# Calculate total fund (sum of points * sapling cost)
total_points = df['Points (5yr avg)'].sum()
total_fund = total_points * sapling_cost

st.write(f"**Total Fund Available:** £{total_fund:,.2f}")

# Compute allocations
# Majority amount goes to least-funded department
majority_amount = total_fund * least_funded_ratio
remaining_amount = total_fund * others_ratio

# Initialize allocations
df['Allocation (£)'] = 0.0

# Allocate majority to least-funded department
df.loc[df['Department'] == least_funded_dept, 'Allocation (£)'] = majority_amount

# Distribute remaining among departments meeting preventive gate score
eligible_for_minority = df[(df['Department'] != least_funded_dept) & (df['Score (%)'] >= preventive_gate_score)]

if len(eligible_for_minority) > 0:
    # Distribute proportionally by Points (5yr avg)
    eligible_points_total = eligible_for_minority['Points (5yr avg)'].sum()
    
    for idx in eligible_for_minority.index:
        dept_points = df.loc[idx, 'Points (5yr avg)']
        proportion = dept_points / eligible_points_total
        df.loc[idx, 'Allocation (£)'] = remaining_amount * proportion
else:
    # No departments meet the gate - hold the minority share
    st.warning(f"""
    ⚠️ **Preventive Gate Not Met**
    
    No departments (other than the least-funded) meet the preventive gate score threshold of {preventive_gate_score}%.
    The minority allocation of £{remaining_amount:,.2f} is being held and not distributed.
    """)

# Fix rounding drift - ensure allocations sum to total_fund
# Round allocations first
df['Allocation (£)'] = df['Allocation (£)'].round(2)

# Then check and fix any drift
allocation_sum = df['Allocation (£)'].sum()
if allocation_sum > 0 and abs(allocation_sum - total_fund) > ALLOCATION_ROUNDING_TOLERANCE:
    # Adjust the department with the largest allocation to fix drift
    # This is typically the least-funded department, but we find it dynamically
    max_allocation_idx = df['Allocation (£)'].idxmax()
    adjustment = round(total_fund - allocation_sum, 2)
    df.loc[max_allocation_idx, 'Allocation (£)'] += adjustment

# Display the scorecard table
st.subheader("📋 Department Scorecard")

# Format for display
display_df = df.copy()
display_df['Points (5yr avg)'] = display_df['Points (5yr avg)'].astype(int)
display_df['Score (%)'] = display_df['Score (%)'].astype(int)

st.dataframe(display_df, use_container_width=True, hide_index=True)

# Visualizations
st.subheader("📊 Visualizations")

col1, col2 = st.columns(2)

with col1:
    # Bar chart for points
    fig_points = go.Figure(data=[
        go.Bar(
            x=df['Department'],
            y=df['Points (5yr avg)'],
            marker_color='lightblue',
            text=df['Points (5yr avg)'],
            textposition='outside'
        )
    ])
    fig_points.update_layout(
        title='Points (5-Year Average)',
        xaxis_title='Department',
        yaxis_title='Points',
        height=400
    )
    st.plotly_chart(fig_points, use_container_width=True)

with col2:
    # Horizontal bar chart for scores
    fig_scores = go.Figure(data=[
        go.Bar(
            y=df['Department'],
            x=df['Score (%)'],
            orientation='h',
            marker_color='lightgreen',
            text=df['Score (%)'].apply(lambda x: f"{x}%"),
            textposition='outside'
        )
    ])
    fig_scores.update_layout(
        title='Preventive Care Score (%)',
        xaxis_title='Score (%)',
        yaxis_title='Department',
        height=400
    )
    st.plotly_chart(fig_scores, use_container_width=True)

# Pie/Donut chart for allocation
fig_allocation = go.Figure(data=[
    go.Pie(
        labels=df['Department'],
        values=df['Allocation (£)'],
        hole=0.4,
        textinfo='label+percent',
        hovertemplate='%{label}<br>£%{value:,.2f}<extra></extra>'
    )
])
fig_allocation.update_layout(
    title='Fund Allocation Distribution',
    height=500
)
st.plotly_chart(fig_allocation, use_container_width=True)

# Download buttons
st.subheader("📥 Export Data")

col_export1, col_export2 = st.columns(2)

with col_export1:
    # CSV download
    csv_buffer = display_df.to_csv(index=False)
    safe_filename = sanitize_filename(hospital_name)
    st.download_button(
        label="📄 Download as CSV",
        data=csv_buffer,
        file_name=f"hospital_scorecard_{safe_filename}.csv",
        mime="text/csv"
    )

with col_export2:
    # Excel download
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        display_df.to_excel(writer, index=False, sheet_name='Scorecard')
    excel_buffer.seek(0)
    
    safe_filename = sanitize_filename(hospital_name)
    st.download_button(
        label="📊 Download as Excel",
        data=excel_buffer,
        file_name=f"hospital_scorecard_{safe_filename}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Printable HTML Report
st.subheader("🖨️ Printable Report")

# Escape all user-controlled data for HTML safety
safe_hospital_name = html.escape(hospital_name)
safe_reporting_period = html.escape(reporting_period)
safe_least_funded_dept = html.escape(least_funded_dept)
safe_selection_method = html.escape(selection_method)

# Generate HTML report
html_report = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Hospital Scorecard Report</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        @media print {{
            body {{
                margin: 0;
                padding: 0;
            }}
            .no-print {{
                display: none;
            }}
        }}
        body {{
            font-family: Arial, sans-serif;
            max-width: 210mm;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #1f77b4;
            border-bottom: 2px solid #1f77b4;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #333;
            margin-top: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #1f77b4;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        .summary {{
            background-color: #e7f3ff;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 12px;
            color: #666;
        }}
        button {{
            background-color: #1f77b4;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }}
        button:hover {{
            background-color: #145a8a;
        }}
    </style>
</head>
<body>
    <h1>🏥 {safe_hospital_name}</h1>
    <p><strong>Reporting Period:</strong> {safe_reporting_period}</p>
    <p><strong>Sapling Cost:</strong> £{sapling_cost} per tree</p>
    
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Total Fund Available:</strong> £{total_fund:,.2f}</p>
        <p><strong>Least-Funded Department:</strong> {safe_least_funded_dept} ({safe_selection_method})</p>
        <p><strong>Majority Allocation ({least_funded_ratio*100:.0f}%):</strong> £{majority_amount:,.2f}</p>
        <p><strong>Minority Allocation ({others_ratio*100:.0f}%):</strong> £{remaining_amount:,.2f}</p>
        <p><strong>Preventive Gate Score:</strong> {preventive_gate_score}%</p>
    </div>
    
    <h2>Department Scorecard</h2>
    <table>
        <thead>
            <tr>
                <th>Department</th>
                <th>Points (5yr avg)</th>
                <th>Score (%)</th>
                <th>Funding Level</th>
                <th>Allocation (£)</th>
            </tr>
        </thead>
        <tbody>
"""

for _, row in display_df.iterrows():
    # Escape all string values for HTML safety
    safe_dept = html.escape(str(row['Department']))
    safe_funding_level = html.escape(str(row['Funding Level']))
    html_report += f"""
            <tr>
                <td>{safe_dept}</td>
                <td>{row['Points (5yr avg)']}</td>
                <td>{row['Score (%)']}%</td>
                <td>{safe_funding_level}</td>
                <td>£{row['Allocation (£)']:,.2f}</td>
            </tr>
"""

html_report += f"""
        </tbody>
    </table>
    
    <div class="footer">
        <p>Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Hospital Preventive Care Scorecard - {safe_hospital_name}</p>
    </div>
    
    <div class="no-print" style="text-align: center; margin-top: 30px;">
        <button onclick="window.print()">🖨️ Print Report</button>
    </div>
</body>
</html>
"""

# Display HTML preview with print button
components.html(html_report, height=800, scrolling=True)
