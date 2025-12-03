import streamlit as st
import pandas as pd

st.title("🏁 Race Statistics")
st.write("Detailed race statistics for Formula 1 analysis.")

stats = {
    "Race": ["Monaco", "Silverstone", "Spa"],
    "Laps": [78, 52, 44],
    "Track Length (km)": [3.34, 5.89, 7.00]
}
df = pd.DataFrame(stats)

st.dataframe(df)
st.bar_chart(df.set_index("Race"))
