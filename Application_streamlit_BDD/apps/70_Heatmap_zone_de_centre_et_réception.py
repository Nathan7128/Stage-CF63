import streamlit as st

import pandas as pd

from mplsoccer import VerticalPitch

import matplotlib.pyplot as plt

import numpy as np

from config_py.variable import path_effect_2, dico_rank_SB, colormapblue, colormapred

import matplotlib.patches as patches

from config_py.fonction import label_heatmap_centre, best_zone

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

if not saison_choice :
    st.stop()

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

df = df.reset_index(drop = True).set_index(["match_id", "centre_id"])
df_centre = df[df.Centre == 1]


#----------------------------------------------- FILTRAGE HEATMAPS ------------------------------------------------------------------------------------


if len(df_centre) == 0 :
    st.stop()

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

if len(df_centre) == 0 :
    st.stop()

with columns[1] :
    liste_type_compt = (["Pourcentage", "Pourcentage sans %", "Valeur", "Aucune valeur"] 
                        + (1 - choix_goal)*["Pourcentage de but"] + (1 - choix_goal)*["Pourcentage de but sans %"])
    count_type_g = st.selectbox("Type de comptage Heatmap de gauche", liste_type_compt)
    count_type_d = st.selectbox("Type de comptage Heatmap de droite", liste_type_compt)

st.divider()

""
""

columns = st.columns(2, vertical_alignment = "center", gap = "large")

with columns[0] :
    columns2 = st.columns(2)
    with columns2[0] :
        nombre_ligne_gauche = st.number_input("Nombre de ligne pour la Heatmap de gauche", min_value = 1, step = 1, value = 5)
    with columns2[1] :
        nombre_col_gauche = st.number_input("Nombre de colonne pour la Heatmap de gauche", min_value = 1, step = 1, value = 6)
    choix_ligne_gauche = st.number_input("Choisir une ligne pour la Heatmap de gauche", min_value = 0, step = 1,
                                            max_value = nombre_ligne_gauche)
    choix_col_gauche = st.number_input("Choisir une colonne pour la Heatmap de gauche", min_value = 0, step = 1,
                                    max_value = nombre_col_gauche)

with columns[1] :
    columns2 = st.columns(2)
    with columns2[0] :
        nombre_ligne_droite = st.number_input("Nombre de ligne pour la Heatmap de droite",
                                min_value = 1, step = 1, value = 5)
    with columns2[1] :
        nombre_col_droite = st.number_input("Nombre de colonne pour la Heatmap de droite",
                            min_value = 1, step = 1, value = 6)
        
st.divider()


#----------------------------------------------- AFFICHAGE HEATMAPS ------------------------------------------------------------------------------------


df_centre_zone_gauche = df_centre.copy()
df_shot_select = pd.DataFrame()

if (choix_ligne_gauche != 0) & (choix_col_gauche != 0) :

    df_centre_zone_gauche = df_centre[(df_centre.x >= (60 + (60/nombre_ligne_gauche)*(choix_ligne_gauche - 1))) &
                    (df_centre.x < (60 + (60/nombre_ligne_gauche)*(choix_ligne_gauche))) &
                    (df_centre.y >= (80/nombre_col_gauche)*(choix_col_gauche - 1)) &
                    (df_centre.y < (80/nombre_col_gauche)*(choix_col_gauche))]
    
    with columns[1] :
        choix_ligne_droite = st.number_input("Choisir une ligne pour la Heatmap de droite", min_value = 0, step = 1,
                                        max_value = nombre_ligne_droite)
        choix_col_droite = st.number_input("Choisir une colonne pour la Heatmap de droite", min_value = 0, step = 1,
                                        max_value = nombre_col_droite)

    df_shot_select = df.loc[df_centre_zone_gauche.index]
    df_shot_select = df_shot_select[~df_shot_select.Tireur.isna()]
    if choix_goal :
        df_shot_select = df_shot_select[df_shot_select.But == "Oui"]

    if (choix_ligne_droite != 0) & (choix_col_droite != 0) :
        df_shot_select = df_shot_select[(df_shot_select.x >= (60 + (60/nombre_ligne_droite)*(choix_ligne_droite - 1))) &
                        (df_shot_select.x < (60 + (60/nombre_ligne_droite)*(choix_ligne_droite))) &
                        (df_shot_select.y >= (80/nombre_col_droite)*(choix_col_droite - 1)) &
                        (df_shot_select.y < (80/nombre_col_droite)*(choix_col_droite))]


if len(df_centre_zone_gauche) == 0 :
    count_type_d = "Aucune valeur"


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


# ------------------------------------------------- AFFICHAGE DE LA HEATMAP --------------------------------------------------------


@st.cache_data
def heatmap_percen(data, data2, nombre_col_gauche, nombre_ligne_gauche, nombre_col_droite, nombre_ligne_droite,
                    count_type_g, count_type_d) :
    
    pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color=None, line_color = "green", half = True,
                axis = True, label = True, tick = True, linewidth = 1.5, spot_scale = 0.002, goal_type = "box")
    

    fig1, ax1 = pitch.draw(constrained_layout=True, tight_layout=False)
    ax1.set_xticks(np.arange(80/(2*nombre_col_gauche), 80 - 80/(2*nombre_col_gauche) + 1, 80/nombre_col_gauche), labels = np.arange(1, nombre_col_gauche + 1, dtype = int))
    ax1.set_yticks(np.arange(60 + 60/(2*nombre_ligne_gauche), 120 - 60/(2*nombre_ligne_gauche) + 1, 60/nombre_ligne_gauche),
                labels = np.arange(1, nombre_ligne_gauche + 1, dtype = int))
    ax1.tick_params(axis = "y", right = False, labelright = False)
    ax1.spines[:].set_visible(False)
    ax1.tick_params(axis = "x", top = False, labeltop = False)
    ax1.set_xlim(0, 80)
    ax1.set_ylim(60, 125)
    fig1.set_facecolor("none")
    ax1.set_facecolor((1, 1, 1))
    fig1.set_edgecolor("none")



    fig2, ax2 = pitch.draw(constrained_layout=True, tight_layout=False)
    ax2.set_xticks(np.arange(80/(2*nombre_col_droite), 80 - 80/(2*nombre_col_droite) + 1, 80/nombre_col_droite), labels = np.arange(1, nombre_col_droite + 1, dtype = int))
    ax2.set_yticks(np.arange(60 + 60/(2*nombre_ligne_droite), 120 - 60/(2*nombre_ligne_droite) + 1, 60/nombre_ligne_droite),
                labels = np.arange(1, nombre_ligne_droite + 1, dtype = int))
    ax2.tick_params(axis = "y", right = False, labelright = False)
    ax2.spines[:].set_visible(False)
    ax2.tick_params(axis = "x", top = False, labeltop = False)
    ax2.set_xlim(0, 80)
    ax2.set_ylim(60, 125)
    fig2.set_facecolor("none")
    ax2.set_facecolor((1, 1, 1))
    fig2.set_edgecolor("none")

    bin_statistic1 = pitch.bin_statistic(data.x, data.y, statistic='count', bins=(nombre_ligne_gauche*2, nombre_col_gauche),
                                            normalize = count_type_g in liste_type_compt[:2])
    bin_statistic2 = pitch.bin_statistic(data2.x_end, data2.y_end, statistic='count', bins=(nombre_ligne_droite*2, nombre_col_droite),
                                            normalize = count_type_d in liste_type_compt[:2])

    if count_type_g != "Aucune valeur" :
        bin_statistic_but1 = pitch.bin_statistic(data[data.But == "Oui"].x, data[data.But == "Oui"].y, statistic='count',
                                bins=(nombre_ligne_gauche*2, nombre_col_gauche)) 
        dico_label_heatmap1 = label_heatmap_centre(bin_statistic1["statistic"], bin_statistic_but1["statistic"])
        dico_label_heatmap1 = dico_label_heatmap1[count_type_g]
        bin_statistic1["statistic"] = dico_label_heatmap1["statistique"]
        str_format1 = dico_label_heatmap1["str_format"]
        pitch.label_heatmap(bin_statistic1, exclude_zeros = True, fontsize = int(100/(nombre_col_gauche + nombre_ligne_gauche)) + 2,
            color='#f4edf0', ax = ax1, ha='center', va='center', str_format=str_format1, path_effects=path_effect_2)
        
    if count_type_d != "Aucune valeur" :
        bin_statistic_but2 = pitch.bin_statistic(data2[data2.But == "Oui"].x_end, data2[data2.But == "Oui"].y_end, statistic='count',
                                    bins=(nombre_ligne_droite*2, nombre_col_droite))
        dico_label_heatmap2 = label_heatmap_centre(bin_statistic2["statistic"], bin_statistic_but2["statistic"])
        dico_label_heatmap2 = dico_label_heatmap2[count_type_d]
        bin_statistic2["statistic"] = dico_label_heatmap2["statistique"]
        str_format2 = dico_label_heatmap2["str_format"]
        pitch.label_heatmap(bin_statistic2, exclude_zeros = True, fontsize = int(100/(nombre_col_droite + nombre_ligne_droite)) + 2,
            color='#f4edf0', ax = ax2, ha='center', va='center', str_format=str_format2, path_effects=path_effect_2)
        
    pitch.heatmap(bin_statistic1, ax = ax1, cmap = colormapred, edgecolor='#000000', linewidth = 0.2)

    pitch.heatmap(bin_statistic2, ax = ax2, cmap = colormapblue, edgecolor='#000000', linewidth = 0.2)
        
    return(fig1, fig2, ax1, ax2)

fig1, fig2, ax1, ax2 = heatmap_percen(df_centre, df_centre_zone_gauche, nombre_col_gauche, nombre_ligne_gauche, nombre_col_droite, nombre_ligne_droite, count_type_g, count_type_d)

if (choix_col_gauche != 0) & (choix_ligne_gauche != 0) :
    rect = patches.Rectangle(((80/nombre_col_gauche)*(choix_col_gauche - 1), 60 + (60/nombre_ligne_gauche)*(choix_ligne_gauche - 1)),
                                80/nombre_col_gauche, 60/nombre_ligne_gauche, linewidth=5, edgecolor='r', facecolor='r', alpha=0.6)
    ax1.add_patch(rect)

    if (choix_ligne_droite != 0) & (choix_col_droite != 0) :
        rect = patches.Rectangle(((80/nombre_col_droite)*(choix_col_droite - 1), 60 + (60/nombre_ligne_droite)*(choix_ligne_droite - 1)),
                                    80/nombre_col_droite, 60/nombre_ligne_droite, linewidth=5, edgecolor='r', facecolor='r', alpha=0.6)
        ax2.add_patch(rect)

col5, col6 = st.columns(2, vertical_alignment = "top", gap = "large")
with col5 :
    st.pyplot(fig1)
with col6 :
    st.pyplot(fig2)


# ------------------------------------------------- AFFICHAGE INFORMATIONS TIRS --------------------------------------------------------


if len(df_shot_select) > 0 :

    st.divider()

    col5, col6 = st.columns(2, vertical_alignment = "bottom", gap = "large")

    with col5 :
        
        pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=1, pitch_color=None, line_color = "green", half = True,
                linewidth = 1.5, spot_scale = 0.002, goal_type = "box")

        fig, ax = pitch.draw(constrained_layout=True, tight_layout=False)

        ax.set_ylim(min(df_shot_select.x) - 5, 125)
        
        arrows_color = pd.Series("red", index = df_shot_select.index)
        arrows_color[df_shot_select.But == "Oui"] = "blue"
        pitch.arrows(df_shot_select.x, df_shot_select.y, df_shot_select.x_end, df_shot_select.y_end, color = arrows_color,
                        ax = ax, width = 1)

        st.pyplot(fig)

    with col6 :
        fig_cage = plt.figure(figsize=(20,8))

        ax_cage = fig_cage.gca()
        ax_cage.set_axis_off()

        rapport_dim = 80/68
        width_poteaux = rapport_dim*0.12
        rayon_ballon = 0.11*rapport_dim

        x1=[36, 36, 44, 44, 44 + width_poteaux, 44 + width_poteaux, 36 - width_poteaux, 36 - width_poteaux]
        y1=[0, 2.67, 2.67, 0, 0, 2.67 + width_poteaux, 2.67 + width_poteaux, 0]
        
        plot_poteaux = patches.Polygon(np.array([x1, y1]).T, color = "black")
        ax_cage.add_patch(plot_poteaux)

        x_lim_min = 36 - rapport_dim
        x_lim_max = 44 + rapport_dim
        ax_cage.set_xlim(x_lim_min, x_lim_max)

        y_lim_min = -0.2
        y_lim_max = 2.67 + rapport_dim
        ax_cage.set_ylim(y_lim_min, y_lim_max)

        df_shot_select_cage = df_shot_select[(~df_shot_select.z_end.isna()) & (df_shot_select.x_end > 120 - rapport_dim) &
            (df_shot_select.y_end > x_lim_min + rayon_ballon) & (df_shot_select.y_end < x_lim_max - rayon_ballon)
            & (df_shot_select.z_end < y_lim_max - rayon_ballon)]
        
        shot_color = pd.Series("red", index = df_shot_select_cage.index)
        shot_color[df_shot_select_cage.But == "Oui"] = "blue"

        ax_cage.scatter(df_shot_select_cage["y_end"], df_shot_select_cage["z_end"], s = 27**2, marker = "o", edgecolors = "black", lw = 2,
            color = shot_color)

        st.pyplot(fig_cage)


    if choix_groupe == "Choisir équipe" :

        st.divider()

        expander = st.expander("Tableau des tirs/buts pour la zone sélectionnée sur la Heatmap de gauche")

        with expander :

            st.dataframe(df_shot_select[["match_date", "match_week", "home_team", "away_team", "minute", "Centreur", "But", "Tireur",
                        "Équipe attaquante"]], hide_index = True)
    


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