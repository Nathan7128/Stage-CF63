import streamlit as st

import numpy as np

import pandas as pd

from mplsoccer import VerticalPitch

import matplotlib.patches as patches

import sqlite3

from config_py.variable import path_effect_2, dico_rank_SB, colormapblue, colormapred

from config_py.fonction import label_heatmap, execute_SQL, replace_saison1, replace_saison2

idx = pd.IndexSlice

st.set_page_config(layout="wide")


st.title("Heatmap des zones de tir")

st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Connection BDD


connect = sqlite3.connect("database.db")
cursor = connect.cursor()


#----------------------------------------------- FILTRAGE DES DATAS ------------------------------------------------------------------------------------


columns = st.columns([1, 2, 2], vertical_alignment = "center", gap = "large")

# Choix Compet
params = []
stat = f"SELECT DISTINCT Compet FROM Zone_tir"
liste_compet = execute_SQL(cursor, stat, params).fetchall()
liste_compet = [i[0] for i in liste_compet]
    
with columns[0] :
    choix_compet = st.selectbox("Choisir compétition", options = liste_compet, index = 0)

# Choix d'une ou plusieurs saisons sur laquelle/lesquelles on va étudier les métriques pour Skill Corner
params = [choix_compet]
stat = f"SELECT DISTINCT Saison FROM Zone_tir WHERE Compet = ?"
liste_saison = execute_SQL(cursor, stat, params).fetchall()
liste_saison = [i[0] for i in liste_saison]

with columns[1] :
    choix_saison = st.multiselect("Choisir saison", replace_saison2(liste_saison), default = replace_saison2(liste_saison))
choix_saison = replace_saison1(choix_saison)

with columns[2] :
    choix_groupe = st.radio("Choix groupe", ["Choisir Top/Middle/Bottom", "Choisir équipe"], label_visibility = "hidden")

# On regarde si au moins une saison est choisie
if len(choix_saison) == 0 :
    st.stop()

st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Création du dataframe en choisissant le type de métrique qu'on souhaite étudier


params = [choix_compet] + choix_saison
stat = f"SELECT * FROM Zone_tir WHERE Compet = ? and Saison IN ({', '.join('?' * len(choix_saison))})"
res = execute_SQL(cursor, stat, params)

df = pd.DataFrame(res.fetchall())
df.columns = [i[0] for i in res.description]

df = df.drop(["Compet", "index"], axis = 1).set_index(["Saison", "Équipe"])


#----------------------------------------------- CHOIX GROUPE ------------------------------------------------------------------------------------


if choix_groupe == "Choisir Top/Middle/Bottom" :

    df_groupe = pd.DataFrame(0, index = ["Top", "Middle", "Bottom"], columns = ["Taille", "Slider"])
    df_groupe["Slider"] = "Nombre d'équipe dans le " + df_groupe.index

    columns = st.columns(4, gap = "large", vertical_alignment = "center")
    with columns[0] :
        df_groupe.loc["Top", "Taille"] = st.slider(df_groupe.loc["Top", "Slider"], min_value = 1, max_value = 20, value = 5)
    with columns[1] :
        if df_groupe.loc["Top", "Taille"] == 20 :
            df_groupe.loc["Bottom", "Taille"] = 20 - df_groupe.loc["Top", "Taille"]
            st.write(f"Nombre d'équipe dans le Bottom : {df_groupe.loc['Bottom', 'Taille']}")
        else :
            df_groupe.loc["Bottom", "Taille"] = st.slider(df_groupe.loc["Bottom", "Slider"], min_value = 0,
                                                          max_value = 20 - df_groupe.loc["Top", "Taille"])
    with columns[2] :
        df_groupe.loc["Middle", "Taille"] = 20 - df_groupe.loc["Top", "Taille"] - df_groupe.loc["Bottom", "Taille"]
        st.write(f"Nombre d'équipe dans le Middle : {df_groupe.loc['Middle', 'Taille']}")

    with columns[3] :
        groupe_non_vide = df_groupe[df_groupe.Taille > 0].index
        groupe_plot = st.radio("Groupe à afficher", groupe_non_vide.tolist()*(df_groupe.loc["Top", "Taille"] != 20) + ["Global"],
                               horizontal = True)

else :
    choix_équipe = st.multiselect("Choisir équipe", sorted(liste_équipe))

st.divider()



#----------------------------------------------- FILTRAGE DF ------------------------------------------------------------------------------------

df = pd.DataFrame()

if choix_groupe == "Choisir Top/Middle/Bottom" :
    
    for saison in dico_df_saison.keys() :
        df_saison = dico_df_saison[saison]
    
        if groupe_plot == "Top" :
            df_saison = df_saison[df_saison.Équipe.isin(dico_rank_SB[saison][:df_groupe.loc["Top", "Taille"]])]

        elif groupe_plot == "Middle" :
            df_saison = df_saison[df_saison.Équipe.isin(dico_rank_SB[saison][df_groupe.loc["Top", "Taille"]:df_groupe.loc["Top", "Taille"] + df_groupe.loc["Middle", "Taille"]])]

        elif groupe_plot == "Bottom" :  
            df_saison = df_saison[df_saison.Équipe.isin(dico_rank_SB[saison][df_groupe.loc["Top", "Taille"] + df_groupe.loc["Middle", "Taille"]:])]
        df = pd.concat([df, df_saison[['x', 'y']]], axis = 0)

    
else :
    for saison in dico_df_saison.keys() :
        df_saison = dico_df_saison[saison]
        df_saison = df_saison[df_saison.Équipe.isin(choix_équipe)]
        df_saison = pd.merge(df_saison, dico_info_matchs[saison], on = "match_id")
        df = pd.concat([df, df_saison], axis = 0)



#----------------------------------------------- FILTRAGE HEATMAPS ------------------------------------------------------------------------------------

if len(df) > 0 :

    columns = st.columns([2, 1], gap = "large", vertical_alignment = "center")


    with columns[0] :
        bins_h = st.number_input("Nombre de colonne pour la Heatmap de gauche", min_value = 1, step = 1, value = 5)
        bins_v = st.number_input("Nombre de ligne pour la Heatmap de gauche", min_value = 1, step = 1, value = 5)
        

    with columns[1] :  
        count_type = st.selectbox("Type de comptage", ["Pourcentage", "Pourcentage sans %", "Valeur", "Aucune valeur"])
        

    if choix_groupe == "Choisir équipe" :
        columns = st.columns(2)

        with columns[0] :
            choix_bins_v = st.number_input("Choisir une ligne", min_value = 0, step = 1, max_value = bins_v)

        with columns[1] :
            choix_bins_h = st.number_input("Choisir une colonne", min_value = 0, step = 1, max_value = bins_h)

        if (choix_bins_h != 0) & (choix_bins_v != 0) :
            df_sort = df[(df.x >= (80 + (40/bins_v)*(choix_bins_v - 1))) &
                            (df.x <= (80 + (40/bins_v)*(choix_bins_v))) &
                            (df.y >= (80/bins_h)*(choix_bins_h - 1)) &
                            (df.y <= (80/bins_h)*(choix_bins_h))]

    st.divider()


#----------------------------------------------- AFFICHAGE HEATMAPS ------------------------------------------------------------------------------------


    bool_len_grp = (len(saison_choice) > 1)
    saison_title = []
    saison_title.append(f'la saison {saison_choice[0]}')
    saison_title.append(f'les saisons {", ".join(saison_choice[:-1])} et {saison_choice[-1]}')
    
    if choix_groupe != "Choisir équipe" :
        st.markdown(f"<p style='text-align: center;'>Heatmap pour le {groupe_plot} de Ligue 2 sur {saison_title[bool_len_grp]}</p>", unsafe_allow_html=True)

    else :
        bool_len_éq = (len(choix_équipe) > 1)
        éq_title = []
        éq_title.append(f'{choix_équipe[0]}')
        éq_title.append(f'{", ".join(choix_équipe[:-1])} et {choix_équipe[-1]}')
        st.markdown(f"<p style='text-align: center;'>Heatmap pour {éq_title[bool_len_éq]} sur {saison_title[bool_len_grp]}</p>", unsafe_allow_html=True)


    @st.cache_data
    def heatmap_percen(data, bins_h, bins_v, count_type) :
        pitch = VerticalPitch(pitch_type='statsbomb', pitch_color = None, line_zorder=2, line_color = "green", half = True, axis = True,
                label = True, tick = True, linewidth = 1.5, spot_scale = 0.002, goal_type = "box")
        fig, ax = pitch.draw(constrained_layout=True, tight_layout=False)

        ax.set_xticks(np.arange(80/(2*bins_h), 80 - 80/(2*bins_h) + 1, 80/bins_h), labels = np.arange(1, bins_h + 1, dtype = int))
        ax.set_yticks(np.arange(80 + 40/(2*bins_v), 120 - 40/(2*bins_v) + 1, 40/bins_v),
                    labels = np.arange(1, bins_v + 1, dtype = int))
        ax.tick_params(axis = "y", right = False, labelright = False)
        ax.spines[:].set_visible(False)
        ax.tick_params(axis = "x", top = False, labeltop = False)
        fig.set_facecolor("none")
        ax.set_facecolor((1, 1, 1))
        fig.set_edgecolor("none")
        ax.set_xlim(0, 80)
        ax.set_ylim([80, 125])
        bin_statistic = pitch.bin_statistic(data.x, data.y, statistic='count', bins=(bins_v*3, bins_h),
                                                normalize = "Pourcentage" in count_type)
        pitch.heatmap(bin_statistic, ax = ax, cmap = colormapred, edgecolor='#000000', linewidth = 0.2)

        

        if count_type != "Aucune valeur" :
            dico_label_heatmap = label_heatmap(bin_statistic["statistic"])
            dico_label_heatmap = dico_label_heatmap[count_type]
            bin_statistic["statistic"] = dico_label_heatmap["statistique"]
            str_format = dico_label_heatmap["str_format"]
            pitch.label_heatmap(bin_statistic, exclude_zeros = True, fontsize = int(100/(bins_h + bins_v)) + 2,
                color='#f4edf0', ax = ax, ha='center', va='center', str_format=str_format, path_effects=path_effect_2)

        return fig, ax

    @st.cache_data
    def heatmap_smooth(data) :
        pitch = VerticalPitch(pitch_type='statsbomb', pitch_color = None, line_zorder=2, line_color = "green", half = True,
                    linewidth = 1.5, spot_scale = 0.002, goal_type = "box")
        fig, ax = pitch.draw(constrained_layout=True, tight_layout=False)
        ax.set_xlim([0, 80])
        ax.set_ylim([80, 125])
        fig.set_facecolor("none")
        ax.set_facecolor((1, 1, 1))
        fig.set_edgecolor("none")
        pitch.kdeplot(data.x, data.y, ax = ax, fill = True, levels = 100, thresh = 0, cmap = colormapblue)
        
        return fig, ax



    col1, col2 = st.columns(2)

    with col1 :
        fig1, ax1 = heatmap_percen(df, bins_h, bins_v, count_type)
        if choix_groupe == "Choisir équipe" and (choix_bins_h != 0) & (choix_bins_v != 0) :
            rect = patches.Rectangle(((80/bins_h)*(choix_bins_h - 1), 80 + (40/bins_v)*(choix_bins_v - 1)),
                                    80/bins_h, 40/bins_v, linewidth=5, edgecolor='r', facecolor='r', alpha=0.6)
            ax1.add_patch(rect)
        st.pyplot(fig1)
    with col2 :
        fig2, ax2 = heatmap_smooth(df)
        st.pyplot(fig2)

    st.markdown(f"<p style='text-align: center;'>Nombre total de tirs : {len(df)}</p>",
                        unsafe_allow_html=True)
    
    if choix_groupe == "Choisir équipe" and choix_bins_h > 0 and choix_bins_v > 0 and len(df_sort) > 0  :
        st.dataframe(df_sort[["match_date", "match_week", "home_team", "away_team", "minute", "joueur", "Équipe"]],
                hide_index = True)