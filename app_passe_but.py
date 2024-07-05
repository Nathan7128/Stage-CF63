import streamlit as st
import pandas as pd

st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

st.title("Moyennes du nombre de passes avant un but en ligue 2")

data = pd.read_excel("Passes avant un but/moy_passe_but.xlsx")

annee = st.dataframe(data, on_select = "rerun", selection_mode = "multi-row")

data_sort = data.loc[data.columns[annee.selection.rows]]

st.divider()

st.line_chart(data_sort)