import streamlit as st
import pandas as pd

st.title("👥 Driver Analysis")
st.write("Compare drivers across wins and podiums.")

drivers = {
    "Driver": ["Hamilton", "Verstappen", "Leclerc"],
    "Wins": [95, 55, 20],
    "Podiums": [180, 95, 45]
}
df = pd.DataFrame(drivers)

st.dataframe(df)
st.bar_chart(df.set_index("Driver"))
