import streamlit as st
import pandas as pd

st.title("🏆 Team Standings")
st.write("Team performance overview.")

teams = {
    "Team": ["Mercedes", "Red Bull", "Ferrari"],
    "Points": [650, 620, 500]
}
df = pd.DataFrame(teams)

st.dataframe(df)
st.bar_chart(df.set_index("Team"))
