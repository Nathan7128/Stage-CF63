import streamlit as st

import matplotlib.patheffects as path_effects

import pandas as pd

from mplsoccer import Pitch, VerticalPitch

import streamlit_vertical_slider as svs

import matplotlib.pyplot as plt

import cmasher as cmr

import numpy as np

import matplotlib.patches as patches

st.set_page_config(layout="wide")

st.title("Heatmap des zones de départ/récepetion de centre")

st.divider()

col1, col2, col3 = st.columns(3, gap = "large")

with col1 :
    annee = st.radio("Choisir année", options = ["2020_2021", "2021_2022", "2022_2023", "2023_2024"], horizontal = True)
with col2 :
    top = st.radio("Groupe à afficher", options = ["Top 5", "Bottom 15", "Top 20"], horizontal = True)

with col3 :
    choix_goal = st.checkbox("Filter les centres ayant amenés à un but (dans les 4 évènements suivants le centre)")

st.divider()



# ---------------------------------------------- IMPORTATION ----------------------------------------------------------------------------


@st.cache_data
def import_df(path) :
    return pd.read_excel(path, index_col = 0)

df = import_df(f"Heatmap SB/centre/Tableaux/{annee}.xlsx")


# ---------------------------------------------- TRI DF ----------------------------------------------------------------------------

if top == "Top 5" :
    df_sort = df[df["Top 5"]]

elif top == "Bottom 15" :
    df_sort = df[~df["Top 5"]]

else :
    df_sort = df

if choix_goal :
    df_sort = df_sort[df_sort.goal == 1]


# ---------------------------------------------- EN-TETE ----------------------------------------------------------------------------



st.markdown(f"<p style='text-align: center;'>Heatmap pour le {top} de Ligue 2 sur la saison {annee}</p>", unsafe_allow_html=True)
st.write("")
st.write("")

columns = st.columns([1, 2, 2], vertical_alignment = "center", gap = "large")
with columns[0] :
    if not(choix_goal) :
        choix_percent = st.checkbox("Cacher les '%' des zones")
    else :
        choix_percent = True
    choix_line = st.checkbox("Cacher les lignes du terrain")

with columns[1] :
    columns2 = st.columns(2)
    with columns2[0] :
        bins_gv = st.number_input("Nombre de zone verticale pour la Heatmap de gauche",
                                min_value = 1, step = 1, value = 5)
    with columns2[1] :
        bins_gh = st.number_input("Nombre de zone horizontale pour la Heatmap de gauche",
                             min_value = 1, step = 1, value = 6)
    choix_bins_v = st.number_input("Choisir la ligne de la zone (0 pour tout afficher)",
                                    min_value = 0, step = 1, max_value = bins_gv)

with columns[2] :
    columns2 = st.columns(2)
    with columns2[0] :
        bins_dv = st.number_input("Nombre de zone verticale pour la Heatmap de droite",
                                min_value = 1, step = 1, value = 5)
    with columns2[1] :
        bins_dh = st.number_input("Nombre de zone horizontale pour la Heatmap de droite",
                             min_value = 1, step = 1, value = 6)
    choix_bins_h = st.number_input("Choisir la colonne de la zone (0 pour tout afficher)",
                                   min_value = 0, step = 1, max_value = bins_gh)

df_sort2 = df_sort
if (choix_bins_h != 0) & (choix_bins_v != 0) :
    df_sort2 = df_sort[(df_sort.x >= (60 + (60/bins_gv)*(choix_bins_v - 1))) &
                       (df_sort.x < (60 + (60/bins_gv)*(choix_bins_v))) &
                       (df_sort.y >= (80/bins_gh)*(choix_bins_h - 1)) &
                       (df_sort.y < (80/bins_gh)*(choix_bins_h))]

# ------------------------------------------------- AFFICHAGE DE LA HEATMAP --------------------------------------------------------


@st.cache_data
def heatmap_percen(data, data2, bins_gh, bins_gv, bins_dh, bins_dv, choix_percent, choix_line, choix_goal) :
    path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'), path_effects.Normal()]
    pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#f4edf0', line_color = "#f4edf0", half = True,
                axis = True, label = True, tick = True, linewidth = 2*(1 - choix_line), spot_scale = 0.002*(1 - choix_line))
    fig1, ax1 = pitch.draw(constrained_layout=True, tight_layout=False)



    ax1.set_xticks(np.arange(80/(2*bins_gh), 80 - 80/(2*bins_gh) + 1, 80/bins_gh), labels = np.arange(1, bins_gh + 1, dtype = int))
    ax1.set_yticks(np.arange(60 + 60/(2*bins_gv), 120 - 60/(2*bins_gv) + 1, 60/bins_gv),
                   labels = np.arange(1, bins_gv + 1, dtype = int))
    ax1.tick_params(axis = "y", right = False, labelright = False)
    ax1.spines["right"].set_visible(False)
    ax1.tick_params(axis = "x", bottom = False, labelbottom = False)
    ax1.spines["bottom"].set_visible(False)
    ax1.spines["top"].set_position(("data", 120))
    ax1.spines["left"].set_position(("data", 0))
    ax1.set_xlim(0, 80)
    ax1.set_ylim(60, 120)
    fig1.set_facecolor("none")
    ax1.set_facecolor("none")
    fig1.set_edgecolor("none")



    fig2, ax2 = pitch.draw(constrained_layout=True, tight_layout=False)
    ax2.set_xticks(np.arange(80/(2*bins_dh), 80 - 80/(2*bins_dh) + 1, 80/bins_dh),
                   labels = np.arange(1, bins_dh + 1, dtype = int))
    ax2.set_yticks(np.arange(60 + 60/(2*bins_dv), 120 - 60/(2*bins_dv) + 1, 60/bins_dv),
                   labels = np.arange(1, bins_dv + 1, dtype = int))
    ax2.tick_params(axis = "y", right = False, labelright = False, left = False, labelleft = False)
    ax2.tick_params(axis = "x", bottom = False, labelbottom = False, top = False, labeltop = False)
    ax2.spines[:].set_visible(False)
    ax2.set_xlim(0, 80)
    ax2.set_ylim(60, 120)
    fig2.set_facecolor("none")
    ax2.set_facecolor("none")
    fig2.set_edgecolor("none")

        

    if choix_goal :
        bin_statistic1 = pitch.bin_statistic(data.x, data.y, statistic='count', bins=(bins_gv*2, bins_gh))
        pitch.heatmap(bin_statistic1, ax = ax1, cmap = cmr.nuclear, edgecolor='#FF0000', alpha = 1)
        bin_statistic1["statistic"] = bin_statistic1["statistic"].astype(int)

        bin_statistic2 = pitch.bin_statistic(data2.x_end, data2.y_end, statistic='count', bins=(bins_dv*2, bins_dh))
        pitch.heatmap(bin_statistic2, ax = ax2, cmap = cmr.nuclear, edgecolor='#FF0000')
        bin_statistic2["statistic"] = bin_statistic2["statistic"].astype(int)

        labels = pitch.label_heatmap(bin_statistic1, fontsize = int(100/(bins_gv + bins_gh)) + 2, color='#f4edf0',
                                    ax = ax1, ha='center', va='center', path_effects=path_eff)
        labels = pitch.label_heatmap(bin_statistic2, fontsize = int(100/(bins_dv + bins_dh)) + 2, color='#f4edf0',
                                    ax = ax2, ha='center', va='center', path_effects=path_eff)
    else :
        bin_statistic1 = pitch.bin_statistic(data.x, data.y, statistic='count', bins=(bins_gv*2, bins_gh), normalize=True)
        pitch.heatmap(bin_statistic1, ax = ax1, cmap = cmr.nuclear, edgecolor='#FF0000', alpha = 1)
        if not(choix_percent) :
            labels = pitch.label_heatmap(bin_statistic1, fontsize = int(100/(bins_gv + bins_gh)) + 2, color='#f4edf0',
                                        ax = ax1, ha='center', va='center', str_format='{:.0%}', path_effects=path_eff)        
    
        if len(data2) == 0 :
            bin_statistic2 = pitch.bin_statistic(data2.x_end, data2.y_end, statistic='count', bins=(bins_dv*2, bins_dh))
            bin_statistic2["statistic"] = bin_statistic2["statistic"].astype(int)
            pitch.heatmap(bin_statistic2, ax = ax2, cmap = cmr.nuclear, edgecolor='#FF0000')
            labels = pitch.label_heatmap(bin_statistic2, fontsize = int(100/(bins_dv + bins_dh)) + 2, color='#f4edf0',
                                        ax = ax2, ha='center', va='center', path_effects=path_eff)            
        else :
            bin_statistic2 = pitch.bin_statistic(data2.x_end, data2.y_end, statistic='count', bins=(bins_dv*2, bins_dh),
                                                 normalize=True)
            pitch.heatmap(bin_statistic2, ax = ax2, cmap = cmr.nuclear, edgecolor='#FF0000')
            if not(choix_percent) :
                labels = pitch.label_heatmap(bin_statistic2, fontsize = int(100/(bins_dv + bins_dh)) + 2, color='#f4edf0',
                                        ax = ax2, ha='center', va='center', path_effects=path_eff, str_format='{:.0%}')
    
    return(fig1, fig2, ax1, ax2)

st.divider()

fig1, fig2, ax1, ax2 = heatmap_percen(df_sort, df_sort2, bins_gh, bins_gv, bins_dh, bins_dv, choix_percent, choix_line, choix_goal)

if (choix_bins_h != 0) & (choix_bins_v != 0) :
    rect = patches.Rectangle(((80/bins_gh)*(choix_bins_h - 1), 60 + (60/bins_gv)*(choix_bins_v - 1)),
                                80/bins_gh, 60/bins_gv, linewidth=5, edgecolor='r', facecolor='r', alpha=0.6)
    ax1.add_patch(rect)

col5, col6 = st.columns(2, vertical_alignment = "bottom")
with col5 :
    st.pyplot(fig1)
with col6 :
    st.pyplot(fig2)




# # ------------------------------------------------- AFFICHAGE DU KDEPLOT --------------------------------------------------------

# st.divider()

# @st.cache_data
# def heatmap_smooth(data, choix_line) :
#     path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'), path_effects.Normal()]
#     pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, line_color = "#C2BFBF", half = True, linewidth = 1 - choix_line)

#     fig1, ax1 = pitch.draw(constrained_layout=True, tight_layout=False)
#     fig1.set_facecolor("none")
#     ax1.set_facecolor("none")
#     fig1.set_edgecolor("none")
#     kde = pitch.kdeplot(data.x, data.y, ax = ax1, fill = True, levels = 100, thresh = 0, cmap = cmr.nuclear)

#     fig2, ax2 = pitch.draw(constrained_layout=True, tight_layout=False)
#     fig2.set_facecolor("none")
#     ax2.set_facecolor("none")
#     fig2.set_edgecolor("none")
#     kde = pitch.kdeplot(data.x_end, data.y_end, ax = ax2, fill = True, thresh = 0, levels = 100, cmap = cmr.nuclear)
    
#     col1, col2 = st.columns(2)
#     with col1 :
#         st.pyplot(fig1)
#     with col2 :
#         st.pyplot(fig2)

# heatmap_smooth(df_sort, choix_line)