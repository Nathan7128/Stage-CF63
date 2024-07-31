import streamlit as st

import numpy as np

import pandas as pd

from mplsoccer import Pitch, VerticalPitch

import matplotlib.pyplot as plt

import matplotlib.patches as patches

from config_py.variable import path_effect_2, dico_rank_SB, colormapblue, colormapred

st.set_page_config(layout="wide")


st.title("Heatmap des zones de tir")

st.divider()



#----------------------------------------------- DÉFINITION FONCTIONS ------------------------------------------------------------------------------------


@st.cache_data
def import_df(saison_df) :
    return pd.read_excel(f"Heatmap SB/zone_tir/Tableaux/{saison_df}.xlsx", index_col = 0)


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
    liste_équipe += df_import.Équipe.unique().tolist()
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
        fig1, ax1 = pitch.draw(constrained_layout=True, tight_layout=False)

        ax1.set_xticks(np.arange(80/(2*bins_h), 80 - 80/(2*bins_h) + 1, 80/bins_h), labels = np.arange(1, bins_h + 1, dtype = int))
        ax1.set_yticks(np.arange(80 + 40/(2*bins_v), 120 - 40/(2*bins_v) + 1, 40/bins_v),
                    labels = np.arange(1, bins_v + 1, dtype = int))
        ax1.tick_params(axis = "y", right = False, labelright = False)
        ax1.spines[:].set_visible(False)
        ax1.tick_params(axis = "x", top = False, labeltop = False)
        fig1.set_facecolor("none")
        ax1.set_facecolor((1, 1, 1))
        fig1.set_edgecolor("none")
        ax1.set_xlim(0, 80)
        ax1.set_ylim([80, 125])
        bin_statistic1 = pitch.bin_statistic(data.x, data.y, statistic='count', bins=(bins_v*3, bins_h),
                                                normalize = "Pourcentage" in count_type)
        pitch.heatmap(bin_statistic1, ax = ax1, cmap = colormapred, edgecolor='#000000', linewidth = 0.2)

        dico_label_heatmap1 = {
            "Pourcentage" : {"statistique" : np.round(bin_statistic1["statistic"], 2), "str_format" : '{:.0%}'},
            "Pourcentage sans %" : {"statistique" : 100*np.round(bin_statistic1["statistic"], 2), "str_format" : '{:.0f}'},
            "Valeur" : {"statistique" : bin_statistic1["statistic"], "str_format" : '{:.0f}'},
        }

        if count_type != "Aucune valeur" :
            dico_label_heatmap1 = dico_label_heatmap1[count_type]
            bin_statistic1["statistic"] = dico_label_heatmap1["statistique"]
            labels1 = pitch.label_heatmap(bin_statistic1, exclude_zeros = True, fontsize = int(100/(bins_h + bins_v)) + 2,
                color='#f4edf0', ax = ax1, ha='center', va='center', str_format=dico_label_heatmap1["str_format"], path_effects=path_effect_2)

        return fig1, ax1

    @st.cache_data
    def heatmap_smooth(data) :
        pitch = VerticalPitch(pitch_type='statsbomb', pitch_color = None, line_zorder=2, line_color = "green", half = True,
                    linewidth = 1.5, spot_scale = 0.002, goal_type = "box")
        fig2, ax2 = pitch.draw(constrained_layout=True, tight_layout=False)
        ax2.set_xlim([0, 80])
        ax2.set_ylim([80, 125])
        fig2.set_facecolor("none")
        ax2.set_facecolor((1, 1, 1))
        fig2.set_edgecolor("none")
        kde = pitch.kdeplot(data.x, data.y, ax = ax2, fill = True, levels = 100, thresh = 0, cmap = colormapblue)
        
        return fig2, ax2



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