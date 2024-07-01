import streamlit as st
import pandas as pd

col1, col2 = st.columns(2)

with col1 :
    annee = st.radio("Choisir année", options = ["2021_2022", "2022_2023", "2023_2024"])


