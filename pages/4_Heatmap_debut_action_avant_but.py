import streamlit as st

import pandas as pd

from mplsoccer import Pitch

import matplotlib.pyplot as plt

import cmasher as cmr

st.set_page_config(layout="wide")

st.title("Heatmap des zones de début d'actions menant à un but")

st.divider()

pitch = Pitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#f4edf0')

col1, col2, col3, col4 = st.columns(4)

with col1 :
    annee = st.radio("Choisir année", options = ["2021_2022", "2022_2023", "2023_2024"], horizontal = True)

with col2 :
    bins_h = st.number_input("Nombe de zones (horizontal)", min_value = 1, step = 1, value = 6)

with col3 :
    bins_v = st.number_input("Nombe de zones (vertical)", min_value = 1, step = 1, value = 5)

with col4 :
    top = st.multiselect("Groupe à afficher", options = ["Top 5", "Bottom 15", "Top 20"], default = ["Top 5", "Bottom 15", "Top 20"])

st.divider()

df = pd.read_excel(f"Heatmap SB/deb_action/Avant un but/Tableaux/{annee}/loc_deb_action.xlsx", index_col = 0)

if "Top 5" in top :
    col1, col2 = st.columns(2)
    with col1 :
        fig1, ax1 = pitch.draw()
        fig1.set_facecolor('#f4edf0')
        bin_statistic1 = pitch.bin_statistic(df[df["Top 5"]].x, df[df["Top 5"]].y, statistic='count', bins=(bins_h, bins_v), normalize=True)
        pitch.heatmap(bin_statistic1, ax = ax1, cmap = cmr.nuclear, edgecolor='#f9f9f9')
        labels = pitch.label_heatmap(bin_statistic1, color='#f4edf0', ax = ax1, ha='center', va='center', str_format='{:.0%}')
        st.pyplot(fig1)
    with col2 :
        fig2, ax2 = pitch.draw()
        kde = pitch.kdeplot(df[df["Top 5"]].x, df[df["Top 5"]].y, cmap = cmr.nuclear, ax = ax2, fill = True, levels = 100, thresh = 0)
        st.pyplot(fig2)