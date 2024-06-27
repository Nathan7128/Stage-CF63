import pandas as pd

import numpy as np

import streamlit as st

tri = pd.read_csv("Tableau_metrique.csv", index_col=0)

k = st.slider("Choisir pvalue max", min_value=0.0, max_value=1.0)
st.write("Nombre de métrique choisies:", (tri[tri.pvalue < k]).shape[0], "/", tri.shape[0])
st.dataframe(tri[tri.pvalue < k], width = 500)