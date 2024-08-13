import streamlit as st

import pandas as pd

from mplsoccer import Pitch, VerticalPitch

import matplotlib.pyplot as plt

import numpy as np

from config_py.variable import path_effect_2, dico_rank_SB, colormapblue, colormapred

import matplotlib.patches as patches

from config_py.fonction import label_heatmap_centre, best_zone

import time

st.set_page_config(layout="wide")

st.title("Heatmap des zones de départ/réception de centre")

st.divider()


#----------------------------------------------- DÉFINITION FONCTIONS ------------------------------------------------------------------------------------


@st.cache_data
def import_df(saison_df) :
    return pd.read_excel(f"Heatmap SB/centre/Tableaux/{saison_df}.xlsx", index_col = 0)


dico_df_saison = {}
dico_info_matchs = {}

liste_équipe = []


#----------------------------------------------- FILTRAGE DES DATAS ------------------------------------------------------------------------------------


columns = st.columns(2, gap = "large")

with columns[0] :
    saison_choice = st.multiselect("Choisir saison", options = ["2023/2024", "2022/2023", "2021/2022", "2020/2021"], default = "2023/2024")
    saison_choice.sort()
    liste_saison = [i.replace("/", "_") for i in saison_choice]

with columns[1] :
    choix_groupe = st.radio("Choix groupe", ["Choisir Top/Middle/Bottom", "Choisir équipe"], label_visibility = "hidden")


for saison in liste_saison :
    df_import = import_df(saison)
    dico_df_saison[saison] = df_import
    liste_équipe += df_import["Équipe attaquante"].unique().tolist()
    dico_info_matchs[saison] = pd.read_excel(f"Info matchs/Stats Bomb/{saison}.xlsx", index_col = 0)

liste_équipe = list(set(liste_équipe))

st.divider()


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
            df_saison = df_saison[df_saison["Équipe attaquante"].isin(dico_rank_SB[saison][:df_groupe.loc["Top", "Taille"]])]

        elif groupe_plot == "Middle" :
            df_saison = df_saison[df_saison["Équipe attaquante"].isin(dico_rank_SB[saison][df_groupe.loc["Top", "Taille"]:df_groupe.loc["Top", "Taille"] + df_groupe.loc["Middle", "Taille"]])]

        elif groupe_plot == "Bottom" :  
            df_saison = df_saison[df_saison["Équipe attaquante"].isin(dico_rank_SB[saison][df_groupe.loc["Top", "Taille"] + df_groupe.loc["Middle", "Taille"]:])]
        df = pd.concat([df, df_saison], axis = 0)

    
else :
    for saison in dico_df_saison.keys() :
        df_saison = dico_df_saison[saison]
        df_saison = df_saison[df_saison["Équipe attaquante"].isin(choix_équipe)]
        df_saison = pd.merge(df_saison, dico_info_matchs[saison][["match_id", "match_date", "match_week", "home_team", "away_team"]], on = "match_id", how = "left")
        df = pd.concat([df, df_saison], axis = 0)

df = df.reset_index().set_index(["match_id", "centre_id"])
df_centre = df.groupby(level = [0, 1]).head(1)


#----------------------------------------------- FILTRAGE HEATMAPS ------------------------------------------------------------------------------------


if len(df_centre) > 0 :

    df_zone_centre = df_centre.copy()

    columns = st.columns(2, vertical_alignment = "center", gap = "large")

    with columns[0] :
        choix_goal = st.checkbox("Filter les centres ayant amenés à un but (dans les 5 évènements suivants le centre)")
        choix_sym_g = st.checkbox("Afficher tous les centres du même coté sur la Heatmap de gauche")
        choix_body_part = st.selectbox("Partie du corps utilisée pour centrer", ["Pied gauche", "Pied droit", "All"], index = 2)

    if choix_sym_g :
        df_centre.loc[df_centre.y > 40, ["y", "y_end"]] = 80 - df_centre.loc[df_centre.y > 40, ["y", "y_end"]]

    if choix_goal :
        df_centre = df_centre[df_centre.But == "Oui"]

    if choix_body_part == "Pied droit" :
        df_centre = df_centre[df_centre["Partie du corps"] == "Right Foot"]
    elif choix_body_part == "Pied gauche" :
        df_centre = df_centre[df_centre["Partie du corps"] == "Left Foot"]


    with columns[1] :
        liste_type_compt = (["Pourcentage", "Pourcentage sans %", "Valeur", "Aucune valeur"] 
                            + (1 - choix_goal)*["Pourcentage de but"] + (1 - choix_goal)*["Pourcentage de but sans %"])
        count_type_g = st.selectbox("Type de comptage Heatmap de gauche", liste_type_compt)
        count_type_d = st.selectbox("Type de comptage Heatmap de droite", liste_type_compt)


    ""
    ""

    columns = st.columns(2, vertical_alignment = "center", gap = "large")

    with columns[0] :
        columns2 = st.columns(2)
        with columns2[0] :
            bins_gv = st.number_input("Nombre de ligne pour la Heatmap de gauche",
                                    min_value = 1, step = 1, value = 5)
        with columns2[1] :
            bins_gh = st.number_input("Nombre de colonne pour la Heatmap de gauche",
                                min_value = 1, step = 1, value = 6)
        choix_bins_v = st.number_input("Choisir une ligne",
                                        min_value = 0, step = 1, max_value = bins_gv)

    with columns[1] :
        columns2 = st.columns(2)
        with columns2[0] :
            bins_dv = st.number_input("Nombre de ligne pour la Heatmap de droite",
                                    min_value = 1, step = 1, value = 5)
        with columns2[1] :
            bins_dh = st.number_input("Nombre de colonne pour la Heatmap de droite",
                                min_value = 1, step = 1, value = 6)
        choix_bins_h = st.number_input("Choisir une colonne",
                                    min_value = 0, step = 1, max_value = bins_gh)

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


    df_centre_sort = df_centre.copy()
    if (choix_bins_h != 0) & (choix_bins_v != 0) :
        df_centre_sort = df_centre[(df_centre.x >= (60 + (60/bins_gv)*(choix_bins_v - 1))) &
                        (df_centre.x < (60 + (60/bins_gv)*(choix_bins_v))) &
                        (df_centre.y >= (80/bins_gh)*(choix_bins_h - 1)) &
                        (df_centre.y < (80/bins_gh)*(choix_bins_h))]
    if len(df_centre_sort) == 0 :
        count_type_d = "Aucune valeur"


# ------------------------------------------------- AFFICHAGE DE LA HEATMAP --------------------------------------------------------


    @st.cache_data
    def heatmap_percen(data, data2, bins_gh, bins_gv, bins_dh, bins_dv, count_type_g, count_type_d) :
        pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color=None, line_color = "green", half = True,
                    axis = True, label = True, tick = True, linewidth = 1.5, spot_scale = 0.002, goal_type = "box")
        

        fig1, ax1 = pitch.draw(constrained_layout=True, tight_layout=False)
        ax1.set_xticks(np.arange(80/(2*bins_gh), 80 - 80/(2*bins_gh) + 1, 80/bins_gh), labels = np.arange(1, bins_gh + 1, dtype = int))
        ax1.set_yticks(np.arange(60 + 60/(2*bins_gv), 120 - 60/(2*bins_gv) + 1, 60/bins_gv),
                    labels = np.arange(1, bins_gv + 1, dtype = int))
        ax1.tick_params(axis = "y", right = False, labelright = False)
        ax1.spines[:].set_visible(False)
        ax1.tick_params(axis = "x", top = False, labeltop = False)
        ax1.set_xlim(0, 80)
        ax1.set_ylim(60, 125)
        fig1.set_facecolor("none")
        ax1.set_facecolor((1, 1, 1))
        fig1.set_edgecolor("none")



        fig2, ax2 = pitch.draw(constrained_layout=True, tight_layout=False)
        ax2.set_xticks(np.arange(80/(2*bins_dh), 80 - 80/(2*bins_dh) + 1, 80/bins_dh), labels = np.arange(1, bins_dh + 1, dtype = int))
        ax2.set_yticks(np.arange(60 + 60/(2*bins_dv), 120 - 60/(2*bins_dv) + 1, 60/bins_dv),
                    labels = np.arange(1, bins_dv + 1, dtype = int))
        ax2.tick_params(axis = "y", right = False, labelright = False)
        ax2.spines[:].set_visible(False)
        ax2.tick_params(axis = "x", top = False, labeltop = False)
        ax2.set_xlim(0, 80)
        ax2.set_ylim(60, 125)
        fig2.set_facecolor("none")
        ax2.set_facecolor((1, 1, 1))
        fig2.set_edgecolor("none")

        bin_statistic1 = pitch.bin_statistic(data.x, data.y, statistic='count', bins=(bins_gv*2, bins_gh),
                                                normalize = count_type_g in liste_type_compt[:2])
        bin_statistic2 = pitch.bin_statistic(data2.x_end, data2.y_end, statistic='count', bins=(bins_dv*2, bins_dh),
                                                normalize = count_type_d in liste_type_compt[:2])

        if count_type_g != "Aucune valeur" :
            bin_statistic_but1 = pitch.bin_statistic(data[data.But == 1].x, data[data.But == 1].y, statistic='count',
                                    bins=(bins_gv*2, bins_gh)) 
            dico_label_heatmap1 = label_heatmap_centre(bin_statistic1["statistic"], bin_statistic_but1["statistic"])
            dico_label_heatmap1 = dico_label_heatmap1[count_type_g]
            bin_statistic1["statistic"] = dico_label_heatmap1["statistique"]
            str_format1 = dico_label_heatmap1["str_format"]
            pitch.label_heatmap(bin_statistic1, exclude_zeros = True, fontsize = int(100/(bins_gh + bins_gv)) + 2,
                color='#f4edf0', ax = ax1, ha='center', va='center', str_format=str_format1, path_effects=path_effect_2)
            
        if count_type_d != "Aucune valeur" :
            bin_statistic_but2 = pitch.bin_statistic(data2[data2.But == 1].x_end, data2[data2.But == 1].y_end, statistic='count',
                                        bins=(bins_dv*2, bins_dh))
            dico_label_heatmap2 = label_heatmap_centre(bin_statistic2["statistic"], bin_statistic_but2["statistic"])
            dico_label_heatmap2 = dico_label_heatmap2[count_type_d]
            bin_statistic2["statistic"] = dico_label_heatmap2["statistique"]
            str_format2 = dico_label_heatmap2["str_format"]
            pitch.label_heatmap(bin_statistic2, exclude_zeros = True, fontsize = int(100/(bins_dh + bins_dv)) + 2,
                color='#f4edf0', ax = ax2, ha='center', va='center', str_format=str_format2, path_effects=path_effect_2)
            
        pitch.heatmap(bin_statistic1, ax = ax1, cmap = colormapred, edgecolor='#000000', linewidth = 0.2)

        pitch.heatmap(bin_statistic2, ax = ax2, cmap = colormapblue, edgecolor='#000000', linewidth = 0.2)
            
        return(fig1, fig2, ax1, ax2)

    fig1, fig2, ax1, ax2 = heatmap_percen(df_centre, df_centre_sort, bins_gh, bins_gv, bins_dh, bins_dv, count_type_g, count_type_d)

    if (choix_bins_h != 0) & (choix_bins_v != 0) :
        rect = patches.Rectangle(((80/bins_gh)*(choix_bins_h - 1), 60 + (60/bins_gv)*(choix_bins_v - 1)),
                                    80/bins_gh, 60/bins_gv, linewidth=5, edgecolor='r', facecolor='r', alpha=0.6)
        ax1.add_patch(rect)

    col5, col6 = st.columns(2, vertical_alignment = "top", gap = "large")
    with col5 :
        st.pyplot(fig1)
    with col6 :
        st.pyplot(fig2)

    df_shot_select = df.loc[df_centre_sort.index]
    df_shot_select = df_shot_select[~df_shot_select.Tireur.isna()]

    if len(df_shot_select) > 0 and choix_bins_h > 0 and choix_bins_v > 0 and len(df_centre_sort) > 0 :

        with col5 :
            pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color=None, line_color = "green", half = True,
                    linewidth = 1.5, spot_scale = 0.002, goal_type = "box")

            fig, ax = pitch.draw(constrained_layout=True, tight_layout=False)

            ax.set_ylim(min(df_shot_select.x) - 5, 125)

            pitch.arrows(df_shot_select.x, df_shot_select.y, df_shot_select.x_end, df_shot_select.y_end, ax = ax, width = 1)

            st.pyplot(fig)

    
        if choix_groupe == "Choisir équipe" :

            st.divider()

            expander = st.expander("Tableau des tirs/buts pour la zone sélectionnée")

            with expander :

                st.dataframe(df_shot_select[["match_date", "match_week", "home_team", "away_team", "minute", "Centreur", "Tireur", "Équipe attaquante"]],
                            hide_index = True)
        


    st.divider()

    # expander = st.expander("Zones de centre optimales")

    # with expander :
    #     columns = st.columns(3)
    #     with columns[0] :
    #         nb_but_zone = st.number_input("Nombre de but minimum par zone", min_value = 1, max_value = 30, value = 3)
    #     with columns[1] :
    #         taille_min_zone = st.number_input("Taille minimale zone de centre", min_value = 1.0, max_value = 15.0, value = 2.5, step = 0.5)
    #     with columns[2] :
    #         taille_max_zone = st.number_input("Taille maximale zone de centre", min_value = 1.0, max_value = 15.0, value = 5.0, step = 0.5)
    #     df_zone_optimal = best_zone(df_zone_centre, taille_min_zone, taille_max_zone, nb_but_zone)
    #     df_zone_optimal.index = range(1, len(df_zone_optimal) + 1)
        
    #     with st.columns([1, 1, 8, 1])[2] :
    #         st.dataframe(df_zone_optimal)

    st.markdown(f"<p style='text-align: center;'>Nombre total de centres : {len(df_centre)}</p>", unsafe_allow_html=True)
