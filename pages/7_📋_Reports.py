"""
Reports Page - Column 2: Reports Implementation

Provides contributors with clear, periodic summaries of their activity,
contributions, and ecological impact.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import json

# Import helper functions
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from report_utils import generate_report_summary, format_time_spent
from streamlit_app import audit_event, AUDIT_LOG_PATH

# Page configuration
st.set_page_config(
    page_title="Reports",
    page_icon="📋",
    layout="wide"
)

# --- Initialize session state ---
if 'selected_period' not in st.session_state:
    st.session_state.selected_period = 'weekly'

# --- Header ---
st.title("📋 Reports")
st.markdown("**Clear, periodic summaries of your activity, contributions, and ecological impact**")
st.divider()

# --- Report Selector ---
st.subheader("Select a Time Period")
st.caption("Select a time period to view your summary")

# Create three columns for the period selector
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📅 Weekly", use_container_width=True, 
                 type="primary" if st.session_state.selected_period == 'weekly' else "secondary"):
        st.session_state.selected_period = 'weekly'
        audit_event("report_period_selected", {"period": "weekly"})

with col2:
    if st.button("📆 Monthly", use_container_width=True,
                 type="primary" if st.session_state.selected_period == 'monthly' else "secondary"):
        st.session_state.selected_period = 'monthly'
        audit_event("report_period_selected", {"period": "monthly"})

with col3:
    if st.button("📊 Lifetime", use_container_width=True,
                 type="primary" if st.session_state.selected_period == 'lifetime' else "secondary"):
        st.session_state.selected_period = 'lifetime'
        audit_event("report_period_selected", {"period": "lifetime"})

st.divider()

# --- Generate Report ---
try:
    report = generate_report_summary(AUDIT_LOG_PATH, st.session_state.selected_period)
    
    # Display date range
    st.info(f"**{report['period']} Report**: {report['date_range']}")
    
    # Check if there's data
    if report['total_entries'] == 0:
        st.warning("📭 **No data yet**\n\nYour activity will appear here as you use the app. Start exploring to see your contributions!")
    else:
        # --- Section 1: Activity Summary ---
        st.markdown("### ⏰ Activity Summary")
        if st.session_state.selected_period == 'lifetime':
            st.markdown(f"**Your Lifetime Activity**")
        else:
            st.markdown(f"**Your Activity This {report['period']}**")
        st.caption("A simple overview of your engagement.")
        
        # Activity metrics
        activity = report['activity']
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Sessions", activity['sessions'])
        with col2:
            st.metric("Time Spent", format_time_spent(activity['time_spent_minutes']))
        with col3:
            st.metric("Pages Visited", activity['pages_visited'])
        
        # Expandable activity details
        with st.expander("📊 View Activity Breakdown"):
            st.markdown("**Your Activity Breakdown**")
            st.markdown(f"""
- **Sessions:** How many times you opened the app.
- **Time Spent:** The total time you've spent exploring.
- **Pages Visited:** The number of pages you've viewed.

**What This Means**

Your activity helps the system understand how you use the app. It does not affect your rewards directly, but it helps improve your experience.
            """)
            
            # Timeline visualization
            if activity['pages_visited'] > 0:
                st.markdown("**Activity Timeline**")
                # Create sample timeline data
                timeline_data = pd.DataFrame({
                    'Metric': ['Sessions', 'Pages Visited'],
                    'Count': [activity['sessions'], activity['pages_visited']]
                })
                st.bar_chart(timeline_data.set_index('Metric'))
        
        st.divider()
        
        # --- Section 2: Contribution Summary ---
        st.markdown("### 🍃 Contribution Summary")
        st.markdown("**Your Contributions**")
        st.caption("Your actions support the ecosystem.")
        
        # Contribution metrics
        contributions = report['contributions']
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Items Added", contributions['items_added'])
        with col2:
            st.metric("Items Reviewed", contributions['items_reviewed'])
        with col3:
            st.metric("Community Tasks", contributions['community_tasks'])
        
        # Expandable contribution details
        with st.expander("📊 View Contribution Breakdown"):
            st.markdown("**Your Contributions Breakdown**")
            st.markdown(f"""
- **Items Added:** New entries you've created.
- **Items Reviewed:** Items you've checked or verified.
- **Community Tasks:** Actions that support the wider ecosystem.

**What This Means**

Your contributions are the heart of the system. They help maintain quality, support others, and grow the shared knowledge base.
            """)
            
            # Contribution type breakdown
            if contributions['items_added'] + contributions['items_reviewed'] + contributions['community_tasks'] > 0:
                st.markdown("**Contribution Distribution**")
                contrib_data = pd.DataFrame({
                    'Type': ['Items Added', 'Items Reviewed', 'Community Tasks'],
                    'Count': [
                        contributions['items_added'],
                        contributions['items_reviewed'],
                        contributions['community_tasks']
                    ]
                })
                st.bar_chart(contrib_data.set_index('Type'))
        
        st.divider()
        
        # --- Section 3: Rewards & Ecological Impact ---
        st.markdown("### 🌳 Rewards & Ecological Impact")
        st.markdown("**Your Rewards**")
        st.caption("Every 4,000 points = 1 sapling.")
        
        # Reward metrics
        rewards = report['rewards']
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Points Earned", f"{rewards['points_earned']:,}")
            if st.session_state.selected_period != 'lifetime':
                st.caption(f"For this {st.session_state.selected_period} period")
        with col2:
            st.metric("Saplings Equivalent", f"{rewards['saplings']:.2f}")
            if st.session_state.selected_period != 'lifetime':
                st.caption(f"For this {st.session_state.selected_period} period")
        with col3:
            # For lifetime, show total; for periods, show contribution count
            if st.session_state.selected_period == 'lifetime':
                st.metric("Lifetime Total", f"{rewards['saplings']:.2f} saplings")
            else:
                st.metric("Contributions", rewards['contribution_count'])
        
        # Expandable reward details
        with st.expander("📊 View Rewards Breakdown"):
            st.markdown("**Your Rewards Breakdown**")
            st.markdown(f"""
- **Points Earned:** Total points from your contributions.
- **Saplings Equivalent:** Your ecological impact.
- **Lifetime Total:** Your cumulative rewards.

**What This Means**

Rewards reflect your contribution to the ecosystem. Every 4,000 points equals one sapling planted on your behalf.

**Calculation Example:**
- Your points: {rewards['points_earned']:,}
- Sapling ratio: 4,000 points = 1 sapling
- Your saplings: {rewards['points_earned']:,} ÷ 4,000 = {rewards['saplings']:.2f} saplings
            """)
            
            # Progress to next sapling
            points_to_next_sapling = 4000 - (rewards['points_earned'] % 4000)
            if points_to_next_sapling < 4000:
                progress_percent = ((rewards['points_earned'] % 4000) / 4000) * 100
                st.markdown(f"**Progress to Next Sapling**")
                st.progress(progress_percent / 100)
                st.caption(f"{points_to_next_sapling:,} points until your next sapling")
        
        st.divider()
        
        # --- Export Functionality ---
        st.subheader("📥 Export Report")
        st.write("Download your report data for your records.")
        
        # Prepare CSV data
        export_data = {
            'Report Period': [report['period']],
            'Date Range': [report['date_range']],
            'Sessions': [activity['sessions']],
            'Time Spent (minutes)': [activity['time_spent_minutes']],
            'Pages Visited': [activity['pages_visited']],
            'Items Added': [contributions['items_added']],
            'Items Reviewed': [contributions['items_reviewed']],
            'Community Tasks': [contributions['community_tasks']],
            'Points Earned': [rewards['points_earned']],
            'Saplings Equivalent': [rewards['saplings']],
        }
        
        export_df = pd.DataFrame(export_data)
        csv_data = export_df.to_csv(index=False).encode('utf-8')
        
        if st.download_button(
            label="📥 Download Report as CSV",
            data=csv_data,
            file_name=f"report_{st.session_state.selected_period}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        ):
            audit_event("report_exported", {
                "period": st.session_state.selected_period,
                "format": "csv",
                "date": datetime.now().isoformat()
            })
            st.success("✅ Report exported successfully!")
        
        st.divider()

except Exception as e:
    st.error(f"❌ **Error generating report**: {str(e)}")
    st.info("Please refresh the page or contact support if the issue persists.")

# --- Troubleshooting Section ---
st.subheader("❓ Troubleshooting")

with st.expander("My report isn't generating"):
    st.markdown("""
**My report isn't generating**

Reports may take a moment to load. If it doesn't appear, refresh the page or check your connection.
    """)

with st.expander("My totals don't match Monitoring"):
    st.markdown("""
**My totals don't match Monitoring**

Monitoring shows real-time data. Reports show data for a specific period. Check that you selected the correct timeframe.
    """)

with st.expander("My saplings look wrong"):
    st.markdown("""
**My saplings look wrong**

Saplings are calculated using a fixed ratio: 4,000 points = 1 sapling. Check your points total for this period.
    """)

with st.expander("I don't understand a number"):
    st.markdown("""
**I don't understand a number**

Tap any section for a plain-English explanation. Each metric includes a detailed breakdown when you expand the section.
    """)

# Footer
st.divider()
st.caption("💚 Your contributions help grow the ecosystem. Thank you for your stewardship!")
