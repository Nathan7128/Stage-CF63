import streamlit as st

import matplotlib.patheffects as path_effects

import pandas as pd

from mplsoccer import Pitch, VerticalPitch

import matplotlib.pyplot as plt

import cmasher as cmr

st.set_page_config(layout="wide")

if "type_action" not in st.session_state :
    st.session_state.type_action = []



#----------------------------------------------- FILTRAGE DES DATAS ------------------------------------------------------------------------------------

st.title("Heatmap des zones de début d'actions menant à un tir")

st.divider()

columns = st.columns(2, gap = "large")

with columns[0] :
    annee_choice = st.radio("Choisir saison", options = ["2023/2024", "2022/2023", "2021/2022", "2020/2021"], horizontal = True)
    annee = annee_choice.replace("/", "_")

with columns[1] :
    st.radio("Groupe à afficher", options = ["Top 5", "Bottom 15", "Global", "Équipe"], horizontal = True, key = "groupe")
    groupe = st.session_state.groupe

df = pd.read_excel(f"Heatmap SB/deb_action/Tableaux/{annee}.xlsx", index_col = 0)

st.divider()

liste_team = [0]

if groupe == "Top 5" :
    df_sort = df[df["Top 5"]]

elif groupe == "Bottom 15" :
    df_sort = df[~df["Top 5"]]

elif groupe == "Équipe" :
    liste_team = st.multiselect("Choisir équipe", df.Équipe.unique())
    df_sort = df[df.Équipe.isin(liste_team)]

else :
    df_sort = df.copy()



columns = st.columns(2, gap = "large")


with columns[0] :
    bins_h = st.number_input("Nombre de colonne pour la Heatmap de gauche", min_value = 1, step = 1, value = 5)
    bins_v = st.number_input("Nombre de ligne pour la Heatmap de gauche", min_value = 1, step = 1, value = 10)

with columns[1] :
    choix_goal = st.checkbox("Sélectionner uniquement les débuts d'actions menant à un but")

    if choix_goal :
        df_sort = df_sort[df.But]

    st.multiselect("Choisir le type de début d'action", options = df.type_action.unique(),
                   default = st.session_state.type_action, key = "type_action")
    df_sort = df_sort[df_sort.type_action.isin(st.session_state.type_action)]

st.divider()

col1, col2 = st.columns(2, vertical_alignment = "bottom")
with col1 :
    choix_percent = st.checkbox("Cacher les '%' des zones")
with col2 :
    choix_line = st.checkbox("Cacher les lignes du terrain")



#----------------------------------------------- AFFICHAGE HEATMAPS ------------------------------------------------------------------------------------

if len(liste_team) > 0 and len(st.session_state.type_action) > 0 :
    
    st.divider()

    if groupe != "Équipe" :
        st.markdown(f"<p style='text-align: center;'>Heatmap pour le {groupe} de Ligue 2 sur la saison {annee_choice}</p>", unsafe_allow_html=True)

    else :
        st.markdown(f"<p style='text-align: center;'>Heatmap pour les équipes sélectionnées de Ligue 2 sur la saison {annee_choice}</p>", unsafe_allow_html=True)



    @st.cache_data
    def heatmap_percen(data, bins_h, bins_v, choix_percent, choix_line) :
        path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'), path_effects.Normal()]
        pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#f4edf0', line_color = "#f4edf0",
                            goal_type = "box", linewidth = 1*(1 - choix_line), spot_scale = 0.002*(1 - choix_line))
        fig1, ax1 = pitch.draw(constrained_layout=True, tight_layout=False)
        fig1.set_facecolor("none")
        ax1.set_facecolor((98/255, 98/255, 98/255))
        fig1.set_edgecolor("none")
        bin_statistic1 = pitch.bin_statistic(data.x, data.y, statistic='count', bins=(bins_v, bins_h), normalize=True)
        pitch.heatmap(bin_statistic1, ax = ax1, cmap = cmr.nuclear, edgecolor='#FF0000')
        if not(choix_percent) :
            labels = pitch.label_heatmap(bin_statistic1, fontsize = int(50/(bins_v + bins_h)) + 2, color='#f4edf0', ax = ax1,
                                            ha='center', va='center', str_format='{:.0%}', path_effects=path_eff)
        st.pyplot(fig1)

    @st.cache_data
    def heatmap_smooth(data, choix_line) :
        path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'), path_effects.Normal()]
        pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#f4edf0', line_color = "#f4edf0",
                            goal_type = "box", linewidth = 1*(1 - choix_line), spot_scale = 0.002*(1 - choix_line))
        fig2, ax2 = pitch.draw(constrained_layout=True, tight_layout=False)
        fig2.set_facecolor("none")
        ax2.set_facecolor((98/255, 98/255, 98/255))
        fig2.set_edgecolor("none")
        kde = pitch.kdeplot(data.x, data.y, ax = ax2, fill = True, levels = 100, thresh = 0, cmap = cmr.nuclear)
        st.pyplot(fig2)




    col1, col2 = st.columns(2, vertical_alignment = "bottom")
    with col1 :
        heatmap_percen(df_sort, bins_h, bins_v, choix_percent, choix_line)
    with col2 :
        heatmap_smooth(df_sort, choix_line)