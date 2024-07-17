import streamlit as st

import matplotlib.patheffects as path_effects

import pandas as pd

from mplsoccer import Pitch, VerticalPitch

import matplotlib.pyplot as plt

import cmasher as cmr

st.set_page_config(layout="wide")

st.title("Heatmap des zones de tir")

st.divider()

col1, col2, col3, col4 = st.columns(4, gap = "large")

with col1 :
    annee = st.radio("Choisir année", options = ["2020_2021", "2021_2022", "2022_2023", "2023_2024"], horizontal = True)

with col2 :
    bins_h = st.number_input("Nombre de zone horizontale pour la Heatmap de gauche", min_value = 1, step = 1, value = 6)

with col3 :
    bins_v = st.number_input("Nombre de zone verticale pour la Heatmap de gauche", min_value = 1, step = 1, value = 5)

with col4 :
    top = st.radio("Groupe à afficher", options = ["Top 5", "Bottom 15", "Top 20"], horizontal = True)

st.divider()

df = pd.read_excel(f"Heatmap SB/zone_tir/Tableaux/{annee}.xlsx", index_col = 0)

if top == "Top 5" :
    df_sort = df[df["Top 5"]]

elif top == "Bottom 15" :
    df_sort = df[~df["Top 5"]]

else :
    df_sort = df

st.markdown(f"<p style='text-align: center;'>Heatmap pour le {top} de Ligue 2 sur la saison {annee}</p>", unsafe_allow_html=True)


@st.cache_data
def heatmap_percen(data, bins_h, bins_v, choix_percent, choix_line) :
    path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'), path_effects.Normal()]
    pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#f4edf0', line_color = "#f4edf0", half = True, linewidth = 2*(1 - choix_line), spot_scale = 0.002*(1 - choix_line))
    fig1, ax1 = pitch.draw(constrained_layout=True, tight_layout=False)
    ax1.set_ylim([80, 120])
    fig1.set_facecolor("none")
    ax1.set_facecolor("none")
    fig1.set_edgecolor("none")
    bin_statistic1 = pitch.bin_statistic(data.x, data.y, statistic='count', bins=(bins_v*3, int(4*bins_h/3) + 1), normalize=True)
    pitch.heatmap(bin_statistic1, ax = ax1, cmap = cmr.nuclear, edgecolor='#FF0000')
    if not(choix_percent) :
        labels = pitch.label_heatmap(bin_statistic1, fontsize = int(100/(bins_v + bins_h)) + 2, color='#f4edf0', ax = ax1, ha='center', va='center', str_format='{:.0%}', path_effects=path_eff  )
    st.pyplot(fig1)

@st.cache_data
def heatmap_smooth(data, choix_line) :
    path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'), path_effects.Normal()]
    pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#f4edf0', line_color = "#f4edf0", half = True, linewidth = 2*(1 - choix_line), spot_scale = 0.002*(1 - choix_line))
    fig2, ax2 = pitch.draw(constrained_layout=True, tight_layout=False)
    ax2.set_ylim([80, 120])
    fig2.set_facecolor("none")
    ax2.set_facecolor("none")
    fig2.set_edgecolor("none")
    kde = pitch.kdeplot(data.x, data.y, ax = ax2, fill = True, levels = 100, thresh = 0, cmap = cmr.nuclear)
    st.pyplot(fig2)

col1, col2 = st.columns(2, vertical_alignment = "bottom")
with col1 :
    choix_percent = st.checkbox("Cacher les '%' des zones")
with col2 :
    choix_line = st.checkbox("Cacher les lignes du terrain")

col1, col2 = st.columns(2, vertical_alignment = "bottom")

with col1 :
    heatmap_percen(df_sort, bins_h, bins_v, choix_percent, choix_line)
with col2 :
    heatmap_smooth(df_sort, choix_line)