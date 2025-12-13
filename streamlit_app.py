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

# ============================================================================
# Multi-Area Postcode/Region Feed Mockup
# ============================================================================

st.divider()
st.header("📍 Multi-Area Community Feed (Mockup)")

# Mock postcode-to-region mapping
# NOTE: In production, replace with geocoding API (e.g., postcodes.io or Google Maps)
POSTCODE_REGION_MAP = {
    'SW1A': 'Westminster',
    'E1': 'Tower Hamlets',
    'M1': 'Manchester City Centre',
    'B1': 'Birmingham City Centre',
    'G1': 'Glasgow City Centre',
    'EH1': 'Edinburgh City Centre',
    'CF10': 'Cardiff City Centre',
    'L1': 'Liverpool City Centre',
    'LS1': 'Leeds City Centre',
    'BS1': 'Bristol City Centre',
}

def resolve_region(postcode):
    """
    Resolve a postcode to its region.
    For production: integrate with geocoding API.
    Note: Linear search is acceptable for mockup with ~10 entries.
    """
    if not postcode:
        return None
    # Normalize postcode (remove spaces, uppercase)
    normalized = postcode.upper().replace(' ', '')
    # Try exact match first, then prefix match
    for pc_prefix, region in POSTCODE_REGION_MAP.items():
        if normalized.startswith(pc_prefix.upper()):
            return region
    return None

def regions_match(region1, region2):
    """
    Forgiving region matching - handles None and case-insensitive comparison.
    """
    if region1 is None or region2 is None:
        return False
    return region1.strip().lower() == region2.strip().lower()

# Initialize session state
if 'followed_areas' not in st.session_state:
    # Default: user follows their home area
    st.session_state['followed_areas'] = ['SW1A']
    
if 'home_area' not in st.session_state:
    # Home area is the user's registered postcode
    st.session_state['home_area'] = 'SW1A'

# Advertising Rules Documentation
AD_RULES_MD = """
### 📋 Advertising Rules

**Financial Services Exclusion:**
- All financial services advertisements are excluded from the feed across all scopes.

**Local Scope - Home Area Rules:**
- When viewing your **home area** (registered postcode) with **Local** scope:
  - Sponsor logos and names are **hidden** for ads whose sponsor region does NOT match your home region.
  - A warning message explains the hidden identity.
  
**View-Only Areas:**
- Other followed areas are **view-only** and do NOT enforce home-area logo hiding.
- In combined feed view, home-area rules apply only to items from your home region.

**Regional/National Scopes:**
- Sponsor information is shown normally (unless category excluded).
"""

# Area Management UI
with st.expander("⚙️ Manage Followed Areas", expanded=False):
    st.info("""
    **Important:** Local advertising rules apply only to your **registered/home postcode**.
    Other followed areas are **view-only** and do not enforce home-area logo hiding.
    """)
    
    st.write(f"**Home Area (Registered):** `{st.session_state['home_area']}`")
    
    # Add new area
    col_add1, col_add2 = st.columns([3, 1])
    with col_add1:
        new_area = st.text_input(
            "Add a postcode to follow",
            placeholder="e.g., E1, M1, B1",
            key="new_area_input"
        )
    with col_add2:
        if st.button("➕ Add", key="add_area_btn"):
            if new_area and new_area.strip():
                new_area_clean = new_area.strip().upper()
                if new_area_clean not in st.session_state['followed_areas']:
                    if len(st.session_state['followed_areas']) < 4:
                        st.session_state['followed_areas'].append(new_area_clean)
                        st.success(f"Added {new_area_clean}")
                        st.rerun()
                    else:
                        st.error("Maximum 4 areas allowed")
                else:
                    st.warning("Already following this area")
            else:
                st.error("Please enter a valid postcode")
    
    # List followed areas with remove option
    st.write("**Currently Following:**")
    for area in st.session_state['followed_areas']:
        col_area1, col_area2, col_area3 = st.columns([2, 2, 1])
        with col_area1:
            st.write(f"`{area}` → {resolve_region(area) or 'Unknown Region'}")
        with col_area2:
            is_home = area == st.session_state['home_area']
            if is_home:
                st.write("🏠 **Home**")
            else:
                if st.button("Set as Home", key=f"set_home_{area}"):
                    st.session_state['home_area'] = area
                    st.success(f"Set {area} as home")
                    st.rerun()
        with col_area3:
            if st.button("🗑️", key=f"remove_{area}"):
                st.session_state['followed_areas'].remove(area)
                # If removed home, set first area as new home
                if area == st.session_state['home_area'] and st.session_state['followed_areas']:
                    st.session_state['home_area'] = st.session_state['followed_areas'][0]
                st.rerun()

# Display area tiles
st.subheader("📍 Your Areas")
area_cols = st.columns(min(4, len(st.session_state['followed_areas'])))

for idx, area in enumerate(st.session_state['followed_areas'][:4]):
    with area_cols[idx]:
        region = resolve_region(area) or 'Unknown'
        is_home = area == st.session_state['home_area']
        
        badge_text = "🏠 Local Rules Apply (Home)" if is_home else "👁️ Viewing Only"
        badge_color = "blue" if is_home else "gray"
        
        # Escape user-controlled variables for HTML safety
        safe_area = html.escape(area)
        safe_region = html.escape(region)
        safe_badge_text = html.escape(badge_text)
        # Validate badge_color is a safe value
        safe_badge_color = badge_color if badge_color in ["blue", "gray"] else "gray"
        
        st.markdown(f"""
        <div style="border: 2px solid {safe_badge_color}; border-radius: 8px; padding: 12px; margin: 4px;">
            <h4 style="margin: 0;">{safe_area}</h4>
            <p style="margin: 4px 0; color: gray;">{safe_region}</p>
            <span style="background-color: {safe_badge_color}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">
                {safe_badge_text}
            </span>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# Advertising Rules Info Box
with st.expander("📋 View Advertising Rules", expanded=False):
    st.markdown(AD_RULES_MD)

# Feed Controls
st.subheader("🔍 Feed Filters")

col_filter1, col_filter2 = st.columns(2)

with col_filter1:
    feed_scope = st.selectbox(
        "Scope",
        options=["Local", "Regional", "National"],
        index=0,
        help="Select the geographic scope for the feed"
    )

with col_filter2:
    if len(st.session_state['followed_areas']) > 1:
        feed_area_filter = st.selectbox(
            "Filter by Area",
            options=["All Areas"] + st.session_state['followed_areas'],
            index=0,
            help="Show items from a specific area or all followed areas"
        )
    else:
        feed_area_filter = "All Areas"

# Mock Feed Data
# Each item has: type (post/ad), area, category, content, sponsor info (for ads)
MOCK_FEED_ITEMS = [
    {
        'type': 'post',
        'area': 'SW1A',
        'category': 'community',
        'title': 'Community Garden Opening',
        'content': 'Join us for the grand opening of Westminster Community Garden this Saturday!',
        'author': 'Westminster Community Group',
    },
    {
        'type': 'ad',
        'area': 'SW1A',
        'category': 'retail',
        'title': 'Local Shop Sale - 20% Off',
        'content': 'Visit our Westminster location for exclusive discounts on fresh produce.',
        'sponsor_name': 'Westminster Market Co.',
        'sponsor_region': 'Westminster',
        'sponsor_logo': '🛒',
    },
    {
        'type': 'ad',
        'area': 'SW1A',
        'category': 'financial',
        'title': 'Investment Opportunity',
        'content': 'Grow your wealth with our investment services.',
        'sponsor_name': 'City Finance Ltd',
        'sponsor_region': 'Westminster',
        'sponsor_logo': '💰',
    },
    {
        'type': 'ad',
        'area': 'SW1A',
        'category': 'health',
        'title': 'Free Health Checkup',
        'content': 'Book your free health screening at our Tower Hamlets clinic.',
        'sponsor_name': 'Health Plus Clinics',
        'sponsor_region': 'Tower Hamlets',
        'sponsor_logo': '🏥',
    },
    {
        'type': 'post',
        'area': 'E1',
        'category': 'events',
        'title': 'Street Fair Next Weekend',
        'content': 'Tower Hamlets annual street fair with food, music, and local vendors!',
        'author': 'Tower Hamlets Events',
    },
    {
        'type': 'ad',
        'area': 'E1',
        'category': 'retail',
        'title': 'New Coffee Shop Opening',
        'content': 'Try our artisan coffee at the new Tower Hamlets location.',
        'sponsor_name': 'Bean & Brew',
        'sponsor_region': 'Tower Hamlets',
        'sponsor_logo': '☕',
    },
    {
        'type': 'post',
        'area': 'M1',
        'category': 'news',
        'title': 'City Centre Renovation Complete',
        'content': 'Manchester city centre renovation project completed ahead of schedule.',
        'author': 'Manchester News',
    },
    {
        'type': 'ad',
        'area': 'M1',
        'category': 'financial',
        'title': 'Mortgage Offers',
        'content': 'Special mortgage rates for Manchester residents.',
        'sponsor_name': 'Manchester Mortgages',
        'sponsor_region': 'Manchester City Centre',
        'sponsor_logo': '🏦',
    },
]

# Feed Rendering with Rules Enforcement
st.subheader("📰 Community Feed")

# Resolve home region
home_region = resolve_region(st.session_state['home_area'])

# Filter and render feed items
filtered_items = []
for item in MOCK_FEED_ITEMS:
    # Filter by area if specified
    if feed_area_filter != "All Areas" and item['area'] != feed_area_filter:
        continue
    
    # Only show items from followed areas
    if item['area'] not in st.session_state['followed_areas']:
        continue
    
    # RULE 1: Exclude all financial category items
    if item.get('category') == 'financial':
        continue
    
    filtered_items.append(item)

# Display feed items
if not filtered_items:
    st.info("No items to display. Try adjusting your filters or following more areas.")
else:
    for item in filtered_items:
        item_region = resolve_region(item['area'])
        is_home_area_item = item['area'] == st.session_state['home_area']
        
        # Determine if we should hide sponsor identity
        hide_sponsor = False
        show_warning = False
        
        if item['type'] == 'ad' and feed_scope == "Local":
            # Check if this ad is in the user's home area
            if is_home_area_item:
                # Apply home-area rules: hide sponsor if regions don't match
                sponsor_region = item.get('sponsor_region')
                if not regions_match(sponsor_region, home_region):
                    hide_sponsor = True
                    show_warning = True
        
        # Render the feed item
        with st.container():
            # Card-like styling
            # Validate type and set safe colors
            if item['type'] == 'ad':
                border_color = "#FFD700"  # Gold for ads
                type_label = "📢 Sponsored"
            else:
                border_color = "#4A90E2"  # Blue for posts
                type_label = "📝 Post"
            
            # Validate border_color is a hex color
            if not (border_color.startswith('#') and len(border_color) == 7):
                border_color = "#CCCCCC"  # Fallback to gray
            
            st.markdown(f"""
            <div style="border-left: 4px solid {border_color}; padding-left: 12px; margin-bottom: 16px;">
            """, unsafe_allow_html=True)
            
            # Header
            col_header1, col_header2 = st.columns([3, 1])
            with col_header1:
                st.markdown(f"**{type_label}** · `{item['area']}` ({item_region or 'Unknown'})")
            with col_header2:
                area_badge = "🏠" if is_home_area_item else "👁️"
                st.markdown(f"<div style='text-align: right;'>{area_badge}</div>", unsafe_allow_html=True)
            
            # Title
            st.markdown(f"### {item['title']}")
            
            # Sponsor info (for ads)
            if item['type'] == 'ad':
                if hide_sponsor:
                    st.markdown("**Sponsor:** 🔒 *[Identity Hidden - Non-Local Sponsor]*")
                    if show_warning:
                        st.warning(
                            f"⚠️ **Local Advertising Rule Applied:** This sponsor is not from your home region "
                            f"({home_region}). Sponsor identity is hidden per local advertising rules."
                        )
                else:
                    sponsor_logo = item.get('sponsor_logo', '')
                    sponsor_name = item.get('sponsor_name', 'Unknown')
                    sponsor_region = item.get('sponsor_region', 'Unknown')
                    st.markdown(f"**Sponsor:** {sponsor_logo} {sponsor_name} · *{sponsor_region}*")
            else:
                # Author for posts
                st.markdown(f"**Author:** {item.get('author', 'Unknown')}")
            
            # Content
            st.write(item['content'])
            
            # Category tag
            st.markdown(f"<small style='color: gray;'>Category: {item.get('category', 'general')}</small>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("---")

st.divider()

# Summary info
st.info(f"""
**Feed Summary:**
- Followed Areas: {len(st.session_state['followed_areas'])}
- Home Area: {st.session_state['home_area']} ({home_region or 'Unknown'})
- Scope: {feed_scope}
- Items Displayed: {len(filtered_items)}
- Rules Applied: Financial exclusion ✓, Local sponsor hiding (home area only) ✓
""")
