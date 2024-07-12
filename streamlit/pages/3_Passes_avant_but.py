import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("Moyennes du nombre de passes avant un but en ligue 2")

data = pd.read_excel("Passes avant un but/moy_passe_but.xlsx", index_col = 0)

st.dataframe(data)

st.divider()

st.line_chart(data)