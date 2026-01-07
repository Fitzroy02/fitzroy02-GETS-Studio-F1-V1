import pandas as pd
import streamlit as st
import yaml

# Load the team and driver info from the YAML file
with open('data/teams_drivers.yaml', 'r') as file:
    data = yaml.safe_load(file)

teams = data['teams']
drivers = data['drivers']

# Title and description
st.title("🏎️ F1 Dashboard - GETS Studio")
st.markdown("Welcome to the F1 Dashboard. Select options below to explore team and driver information.")

# Sidebar for navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Teams", "Drivers", "Multi-Area Feed"])

if page == "Home":
    st.header("Home")
    st.write("This is the home page. Use the sidebar to navigate to different sections.")
    
elif page == "Teams":
    st.header("Teams")
    team_names = [team['name'] for team in teams]
    selected_team = st.selectbox("Select a team", team_names)
    
    # Display selected team info
    for team in teams:
        if team['name'] == selected_team:
            st.subheader(f"{team['name']}")
            st.write(f"**Base:** {team['base']}")
            st.write(f"**Team Chief:** {team['team_chief']}")
            st.write(f"**Technical Chief:** {team['technical_chief']}")
            st.write(f"**Chassis:** {team['chassis']}")
            st.write(f"**Power Unit:** {team['power_unit']}")
            st.write(f"**First Team Entry:** {team['first_team_entry']}")
            st.write(f"**World Championships:** {team['world_championships']}")
            st.write(f"**Pole Positions:** {team['pole_positions']}")
            st.write(f"**Fastest Laps:** {team['fastest_laps']}")
            break

elif page == "Drivers":
    st.header("Drivers")
    driver_names = [f"{driver['name']} ({driver['team']})" for driver in drivers]
    selected_driver_display = st.selectbox("Select a driver", driver_names)
    
    # Extract the driver name from the selection
    selected_driver_name = selected_driver_display.split(" (")[0]
    
    # Display selected driver info
    for driver in drivers:
        if driver['name'] == selected_driver_name:
            st.subheader(f"{driver['name']}")
            st.write(f"**Team:** {driver['team']}")
            st.write(f"**Country:** {driver['country']}")
            st.write(f"**Podiums:** {driver['podiums']}")
            st.write(f"**Points:** {driver['points']}")
            st.write(f"**Grands Prix Entered:** {driver['grands_prix_entered']}")
            st.write(f"**World Championships:** {driver['world_championships']}")
            st.write(f"**Highest Race Finish:** {driver['highest_race_finish']}")
            st.write(f"**Highest Grid Position:** {driver['highest_grid_position']}")
            st.write(f"**Date of Birth:** {driver['date_of_birth']}")
            st.write(f"**Place of Birth:** {driver['place_of_birth']}")
            break

elif page == "Multi-Area Feed":
    st.header("Multi-Area Feed")
    st.markdown("### Live Updates from Multiple Areas")
    
    # Create three columns for different feeds
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📊 Team Standings")
        st.markdown("---")
        # Mock team standings data
        team_standings = pd.DataFrame({
            'Position': [1, 2, 3, 4, 5],
            'Team': ['Red Bull Racing', 'Mercedes', 'Ferrari', 'McLaren', 'Aston Martin'],
            'Points': [860, 409, 406, 302, 280]
        })
        st.dataframe(team_standings, hide_index=True)
        
        st.markdown("**Latest Update:**")
        st.info("🏆 Red Bull Racing extends lead after Abu Dhabi GP")
    
    with col2:
        st.subheader("🏁 Race Results")
        st.markdown("---")
        # Mock recent race results
        race_results = pd.DataFrame({
            'Position': [1, 2, 3, 4, 5],
            'Driver': ['Max Verstappen', 'Sergio Perez', 'Charles Leclerc', 'Lewis Hamilton', 'Carlos Sainz'],
            'Time': ['1:30:45.123', '+5.432', '+12.567', '+18.234', '+22.789']
        })
        st.dataframe(race_results, hide_index=True)
        
        st.markdown("**Race Highlight:**")
        st.success("🚀 Verstappen takes pole and victory in dominant display")
    
    with col3:
        st.subheader("📰 Breaking News")
        st.markdown("---")
        st.markdown("""
        - **Just Now**: Red Bull secures constructor's championship
        - **5 min ago**: Hamilton sets fastest lap in Q3
        - **15 min ago**: Safety car deployed after Turn 4 incident
        - **30 min ago**: Ferrari announces strategy change
        - **1 hour ago**: Weather update: Track temperature rising
        """)
        
        st.markdown("**Social Buzz:**")
        st.warning("🔥 Trending: #F1AbuDhabi - 1.2M tweets")
    
    # Additional section below the columns
    st.markdown("---")
    st.subheader("📈 Live Telemetry Dashboard")
    
    # Create two columns for telemetry mockup
    tel_col1, tel_col2 = st.columns(2)
    
    with tel_col1:
        st.markdown("**Driver Performance**")
        performance_data = pd.DataFrame({
            'Driver': ['Verstappen', 'Perez', 'Hamilton', 'Leclerc'],
            'Speed (km/h)': [325, 318, 322, 320],
            'Tire Life (%)': [78, 65, 82, 71]
        })
        st.dataframe(performance_data, hide_index=True)
    
    with tel_col2:
        st.markdown("**Track Conditions**")
        st.metric("Track Temperature", "42°C", "+3°C")
        st.metric("Air Temperature", "28°C", "+1°C")
        st.metric("Humidity", "45%", "-2%")
    
    st.markdown("---")
    st.caption("⚡ Live feed updates every 30 seconds | Last updated: Just now")
