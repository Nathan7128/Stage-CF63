# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Importation des librairies


import streamlit as st
import pandas as pd
from mplsoccer import VerticalPitch
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches
import sqlite3

from fonction import execute_SQL, load_session_state, store_session_state, init_session_state, replace_saison1, replace_saison2, filtre_session_state, label_heatmap_centre
from variable import dico_rank_SB, dico_label, path_effect_2, colormapred, colormapblue

# Index slicer pour la sélection de donnée sur les dataframes avec multi-index
idx = pd.IndexSlice


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Connection BDD


connect = sqlite3.connect("database.db")
cursor = connect.cursor()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Mise en page de la page


st.set_page_config(layout="wide")

st.title("Heatmap des zones de départ/réception de centre")

st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Choix de la compétition, de la saison et du groupe à afficher


columns = st.columns([2, 4, 3], vertical_alignment = "center", gap = "large")

params = []
stat = f"SELECT DISTINCT Compet FROM Passes_avant_un_but"
liste_compet, desc = execute_SQL(cursor, stat, params)
liste_compet = [i[0] for i in liste_compet]
    
with columns[0] :
    load_session_state("compet_heatmap")
    choix_compet = st.selectbox("Choisir compétition", options = liste_compet, key = "widg_compet_heatmap",
                            on_change = store_session_state, args = ["compet_heatmap"])

params = [choix_compet]
stat = f"SELECT DISTINCT Saison FROM Passes_avant_un_but WHERE Compet = ?"
liste_saison, desc = execute_SQL(cursor, stat, params)
liste_saison = [i[0] for i in liste_saison]

with columns[1] :
    init_session_state("saison_heatmap", [max(replace_saison1(liste_saison))])
    load_session_state("saison_heatmap")
    choix_saison = st.multiselect("Choisir saison", replace_saison1(liste_saison), key = "widg_saison_heatmap",
                                  on_change = store_session_state, args = ["saison_heatmap"])

choix_saison = replace_saison2(choix_saison)

with columns[2] :
    load_session_state("groupe_heatmap")
    choix_groupe = st.radio("Choix groupe", ["Choisir Top/Middle/Bottom", "Choisir équipe"], label_visibility = "hidden",
                            key = "widg_groupe_heatmap", on_change = store_session_state, args = ["groupe_heatmap"])

if len(choix_saison) == 0 :
    st.stop()

st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Importation du dataframe après avoir effectuer les choix pour le filtrage des données


params = [choix_compet] + choix_saison
stat = f"SELECT * FROM Centre WHERE Compet = ? and Saison IN ({', '.join('?' * len(choix_saison))})"
res, desc = execute_SQL(cursor, stat, params)

df = pd.DataFrame(res)
df.columns = [i[0] for i in desc]
df = df.drop(["Compet", "index"], axis = 1).set_index(["Saison", "Équipe"])

stat = f"SELECT * FROM Info_matchs_SB WHERE Compet = ? and Saison IN ({', '.join('?' * len(choix_saison))})"
res, desc = execute_SQL(cursor, stat, params)

df_info_matchs = pd.DataFrame(res)
df_info_matchs.columns = [i[0] for i in desc]


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Choix taille des groupes et ceux à afficher ou choix des équipes


liste_équipe = df.index.levels[1]

if choix_groupe == "Choisir Top/Middle/Bottom" :
    df_nb_team = df.reset_index()[["Saison", "Équipe"]].drop_duplicates().groupby("Saison").apply(len)

    max_nb_team = min(df_nb_team)

    df_taille_groupe = pd.DataFrame(0, index = ["Top", "Middle", "Bottom"], columns = ["Taille", "Slider"])

    df_taille_groupe["Slider"] = "Nombre d'équipe dans le " + df_taille_groupe.index

    columns = st.columns(3, gap = "large", vertical_alignment = "center")

    with columns[0] :
        load_session_state("nb_top_heatmap")
        df_taille_groupe.loc["Top", "Taille"] = st.slider(df_taille_groupe.loc["Top", "Slider"], min_value = 1,
                max_value = max_nb_team, key = "widg_nb_top_heatmap", on_change = store_session_state, args = ["nb_top_heatmap"])    
        
    with columns[1] :
        if df_taille_groupe.loc["Top", "Taille"] == max_nb_team :
            st.session_state["nb_bottom_heatmap"] = max_nb_team - df_taille_groupe.loc["Top", "Taille"]

        else :
            st.session_state["nb_bottom_heatmap"] = min(max_nb_team - df_taille_groupe.loc["Top", "Taille"],
                                                    st.session_state["nb_bottom_heatmap"])
            load_session_state("nb_bottom_heatmap")
            st.slider(df_taille_groupe.loc["Bottom", "Slider"], min_value = 0,
                    max_value = max_nb_team - df_taille_groupe.loc["Top", "Taille"], key = "widg_nb_bottom_heatmap",
                    on_change = store_session_state, args = ["nb_bottom_heatmap"])
            
        df_taille_groupe.loc["Bottom", "Taille"] = st.session_state["nb_bottom_heatmap"]
    
    df_taille_groupe.loc["Middle", "Taille"] = max_nb_team - df_taille_groupe.loc["Top", "Taille"] - df_taille_groupe.loc["Bottom", "Taille"]

    with columns[2] :
        groupe_non_vide = df_taille_groupe[df_taille_groupe.Taille > 0].index.tolist()*(df_taille_groupe.loc["Top", "Taille"] != max_nb_team) + ["Global"]
        
        if "groupe_plot_heatmap" in st.session_state and st.session_state["groupe_plot_heatmap"] not in groupe_non_vide :
            del st.session_state["groupe_plot_heatmap"]
        load_session_state("groupe_plot_heatmap")
        groupe_plot = st.radio("Groupe à afficher", groupe_non_vide, horizontal = True, key = "widg_groupe_plot_heatmap",
                    on_change = store_session_state, args = ["groupe_plot_heatmap"])

else :
    filtre_session_state("équipe_heatmap", liste_équipe)
    load_session_state("équipe_heatmap")
    équipe_plot = st.multiselect("Équipe à afficher", liste_équipe, key = "widg_équipe_heatmap", on_change = store_session_state,
                                     args = ["équipe_heatmap"])

st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Filtrage du dataframe selon les groupes/équipes choisit


if choix_groupe == "Choisir Top/Middle/Bottom" :
    if groupe_plot != "Global" :
        for saison in choix_saison :
            liste_rank = dico_rank_SB[saison]

            df.loc[idx[saison, liste_rank[:df_nb_team[saison] - df_taille_groupe.loc["Middle", "Taille"] - df_taille_groupe.loc["Bottom", "Taille"]]], "Groupe"] = "Top"
            df.loc[idx[saison, liste_rank[df_nb_team[saison] - df_taille_groupe.loc["Middle", "Taille"] - df_taille_groupe.loc["Bottom", "Taille"]:df_nb_team[saison] - df_taille_groupe.loc["Bottom", "Taille"]]], "Groupe"] = "Middle"
            df.loc[idx[saison, liste_rank[df_nb_team[saison] - df_taille_groupe.loc["Bottom", "Taille"]:]], "Groupe"] = "Bottom"
        
        df = df[df.Groupe == groupe_plot]
    
else :
    df = df.loc[:, équipe_plot, :]

df = df.reset_index().set_index(["match_id", "centre_id"])
df_centre = df[df.Centre == 1]

if len(df_centre) == 0 :
    st.stop()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Choix de la condition sur les centres amenant à un but, de la symétrie sur les zones de centres, de la partie du corps utilisée
# pour centrer et du type de comptage pour les deux heatmaps


columns = st.columns(2, vertical_alignment = "center", gap = "large")

with columns[0] :
    load_session_state("choix_goal_centre")
    choix_goal = st.checkbox("Filter les centres ayant amenés à un but (dans les 5 évènements suivants le centre)",
            key = "widg_choix_goal_centre", on_change = store_session_state, args = ["choix_goal_centre"])
    
    load_session_state("choix_sym_gauche")
    if st.checkbox("Afficher tous les centres du même coté sur la Heatmap de gauche", key = "widg_choix_sym_gauche",
                              on_change = store_session_state, args = ["choix_sym_gauche"]) :
        df_centre.loc[df_centre.y > 40, ["y", "y_end"]] = 80 - df_centre.loc[df_centre.y > 40, ["y", "y_end"]]
    
    load_session_state("partie_corps")
    partie_corps = st.selectbox("Partie du corps utilisée pour centrer", ["Pied gauche", "Pied droit", "All"],
                    key = "widg_partie_corps", on_change = store_session_state, args = ["partie_corps"])

if choix_goal :
    df_centre = df_centre[df_centre.But == "Oui"]

if partie_corps == "Pied droit" :
    df_centre = df_centre[df_centre["Partie du corps"] == "Right Foot"]

elif partie_corps == "Pied gauche" :
    df_centre = df_centre[df_centre["Partie du corps"] == "Left Foot"]

with columns[1] :
    liste_type_compt = (["Pourcentage", "Pourcentage sans %", "Valeur", "Aucune valeur"] 
                        + (1 - choix_goal)*["Pourcentage de but"] + (1 - choix_goal)*["Pourcentage de but sans %"])
    
    load_session_state("type_compt_gauche")
    type_compt_gauche = st.selectbox("Type de comptage Heatmap de gauche", liste_type_compt, key = "widg_type_compt_gauche",
                                     on_change = store_session_state, args = ["type_compt_gauche"])
    
    load_session_state("type_compt_droite")
    type_compt_droite = st.selectbox("Type de comptage Heatmap de droite", liste_type_compt, key = "widg_type_compt_droite",
                                     on_change = store_session_state, args = ["type_compt_droite"])

st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Choix de la taille des zones des deux heatmaps ainsi que d'une zone sur la heatmap de gauche


columns = st.columns(2, vertical_alignment = "center", gap = "large")

with columns[0] :
    columns2 = st.columns(2)

    with columns2[0] :
        init_session_state("nb_col_gauche", 6)
        load_session_state("nb_col_gauche")
        nb_col_gauche = st.number_input("Nombre de colonne pour la Heatmap de gauche", min_value = 1, step = 1,
                                key = "widg_nb_col_gauche", on_change = store_session_state, args = ["nb_col_gauche"])

    with columns2[1] :        
        init_session_state("nb_ligne_gauche", 5)
        load_session_state("nb_ligne_gauche")
        nb_ligne_gauche = st.number_input("Nombre de ligne pour la Heatmap de gauche", min_value = 1, step = 1,
                key = "widg_nb_ligne_gauche", on_change = store_session_state, args = ["nb_ligne_gauche"])
    
    init_session_state("choix_col_gauche", 0)
    st.session_state["choix_col_gauche"] = min(nb_col_gauche, st.session_state["choix_col_gauche"])
    load_session_state("choix_col_gauche")
    choix_col_gauche = st.number_input("Choisir une colonne pour la Heatmap de gauche", min_value = 0, step = 1,
        max_value = nb_col_gauche, key = "widg_choix_col_gauche", on_change = store_session_state, args = ["choix_col_gauche"])
    
    init_session_state("choix_ligne_gauche", 0)
    st.session_state["choix_ligne_gauche"] = min(nb_ligne_gauche, st.session_state["choix_ligne_gauche"])
    load_session_state("choix_ligne_gauche")
    choix_ligne_gauche = st.number_input("Choisir une ligne pour la Heatmap de gauche", min_value = 0, step = 1,
        max_value = nb_ligne_gauche, key = "widg_choix_ligne_gauche", on_change = store_session_state, args = ["choix_ligne_gauche"])

with columns[1] :
    columns2 = st.columns(2)

    with columns2[0] :
        init_session_state("nb_col_droite", 6)
        load_session_state("nb_col_droite")
        nb_col_droite = st.number_input("Nombre de colonne pour la Heatmap de droite", min_value = 1, step = 1,
                                key = "widg_nb_col_droite", on_change = store_session_state, args = ["nb_col_droite"])

    with columns2[1] :        
        init_session_state("nb_ligne_droite", 5)
        load_session_state("nb_ligne_droite")
        nb_ligne_droite = st.number_input("Nombre de ligne pour la Heatmap de droite", min_value = 1, step = 1,
                key = "widg_nb_ligne_droite", on_change = store_session_state, args = ["nb_ligne_droite"])
        
st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Dans le cas ou une zone a été sélectionnée sur la Heatmap de gauche : filtre du dataframe des zones de réceptions de centre et
# possibilité de choisir une zone sur la Heatmap de droite pour laquelle afficher les positions de départ et d'arrivée des tirs.

df_recep_select = df_centre.copy()
df_shot_select = pd.DataFrame()

if (choix_ligne_gauche != 0) & (choix_col_gauche != 0) :

    df_recep_select = df_centre[(df_centre.x >= (60 + (60/nb_ligne_gauche)*(choix_ligne_gauche - 1))) &
                    (df_centre.x < (60 + (60/nb_ligne_gauche)*(choix_ligne_gauche))) &
                    (df_centre.y >= (80/nb_col_gauche)*(choix_col_gauche - 1)) &
                    (df_centre.y < (80/nb_col_gauche)*(choix_col_gauche))]
    
    with columns[1] :

        init_session_state("choix_col_droite", 0)
        st.session_state["choix_col_droite"] = min(nb_col_droite, st.session_state["choix_col_droite"])
        load_session_state("choix_col_droite")
        choix_col_droite = st.number_input("Choisir une colonne pour la Heatmap de droite", min_value = 0, step = 1,
            max_value = nb_col_droite, key = "widg_choix_col_droite", on_change = store_session_state, args = ["choix_col_droite"])
        
        init_session_state("choix_ligne_droite", 0)
        st.session_state["choix_ligne_droite"] = min(nb_ligne_droite, st.session_state["choix_ligne_droite"])
        load_session_state("choix_ligne_droite")
        choix_ligne_droite = st.number_input("Choisir une ligne pour la Heatmap de droite", min_value = 0, step = 1,
            max_value = nb_ligne_droite, key = "widg_choix_ligne_droite", on_change = store_session_state,
            args = ["choix_ligne_droite"])

    df_shot_select = df.loc[df_recep_select.index]
    df_shot_select = df_shot_select[df_shot_select.Tireur != ""]
    
    if choix_goal :
        df_shot_select = df_shot_select[df_shot_select.But == "Oui"]

    if (choix_ligne_droite != 0) & (choix_col_droite != 0) :
        df_shot_select = df_shot_select[(df_shot_select.x >= (60 + (60/nb_ligne_droite)*(choix_ligne_droite - 1))) &
                        (df_shot_select.x < (60 + (60/nb_ligne_droite)*(choix_ligne_droite))) &
                        (df_shot_select.y >= (80/nb_col_droite)*(choix_col_droite - 1)) &
                        (df_shot_select.y < (80/nb_col_droite)*(choix_col_droite))]


if len(df_recep_select) == 0 :
    type_compt_droite = "Aucune valeur"


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Affichage du titre


choix_saison = sorted(replace_saison1(choix_saison))

bool_taille_saison = (len(choix_saison) > 1)
saison_title = []
saison_title.append(f'la saison {choix_saison[0]}')
saison_title.append(f'les saisons {", ".join(choix_saison[:-1])} et {choix_saison[-1]}')

if choix_groupe == "Choisir Top/Middle/Bottom" :
    bool_taille_groupe = 0
    grp_title = [groupe_plot]

else :
    bool_taille_groupe = (len(équipe_plot) > 1)
    grp_title = [f'{équipe_plot[0]}', f'{", ".join(équipe_plot[:-1])} et {équipe_plot[-1]}']

st.markdown(f"<p style='text-align: center;'>Heatmap {dico_label[choix_groupe][0]} {grp_title[bool_taille_groupe]} sur {saison_title[bool_taille_saison]}</p>",
                unsafe_allow_html=True)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Fonction pour la création des 2 heatmaps


@st.cache_data
def heatmap_percen(data_centre, data_recep, nb_col_gauche, nb_ligne_gauche, nb_col_droite, nb_ligne_droite, type_compt_gauche,
                   type_compt_droite) :
    pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color=None, line_color = "green", half = True, axis = True,
                          label = True, tick = True, linewidth = 1.5, spot_scale = 0.002, goal_type = "box")
    
    fig_centre, ax_centre = pitch.draw(constrained_layout=True, tight_layout=False)

    ax_centre.spines[:].set_visible(False)

    fig_centre.set_facecolor("none")
    fig_centre.set_edgecolor("none")
    ax_centre.set_facecolor((1, 1, 1))

    ax_centre.set_xticks(np.arange(80/(2*nb_col_gauche), 80 - 80/(2*nb_col_gauche) + 1, 80/nb_col_gauche),
                labels = np.arange(1, nb_col_gauche + 1, dtype = int))
    ax_centre.set_yticks(np.arange(60 + 60/(2*nb_ligne_gauche), 120 - 60/(2*nb_ligne_gauche) + 1, 60/nb_ligne_gauche),
                labels = np.arange(1, nb_ligne_gauche + 1, dtype = int))
    ax_centre.tick_params(axis = "y", right = False, labelright = False)
    ax_centre.tick_params(axis = "x", top = False, labeltop = False)

    ax_centre.set_xlim(0, 80)
    ax_centre.set_ylim(60, 125)

    fig_recep, ax_recep = pitch.draw(constrained_layout=True, tight_layout=False)

    ax_recep.spines[:].set_visible(False)

    fig_recep.set_facecolor("none")
    fig_recep.set_edgecolor("none")
    ax_recep.set_facecolor((1, 1, 1))

    ax_recep.set_xticks(np.arange(80/(2*nb_col_droite), 80 - 80/(2*nb_col_droite) + 1, 80/nb_col_droite),
                        labels = np.arange(1, nb_col_droite + 1, dtype = int))
    ax_recep.set_yticks(np.arange(60 + 60/(2*nb_ligne_droite), 120 - 60/(2*nb_ligne_droite) + 1, 60/nb_ligne_droite),
                labels = np.arange(1, nb_ligne_droite + 1, dtype = int))
    ax_recep.tick_params(axis = "y", right = False, labelright = False)
    ax_recep.tick_params(axis = "x", top = False, labeltop = False)

    ax_recep.set_xlim(0, 80)
    ax_recep.set_ylim(60, 125)

    bin_statistic_centre = pitch.bin_statistic(data_centre.x, data_centre.y, statistic='count',
                        bins=(nb_ligne_gauche*2, nb_col_gauche), normalize = type_compt_gauche in liste_type_compt[:2])
    
    bin_statistic_recep = pitch.bin_statistic(data_recep.x_end, data_recep.y_end, statistic='count',
                        bins=(nb_ligne_droite*2, nb_col_droite), normalize = type_compt_droite in liste_type_compt[:2])

    if type_compt_gauche != "Aucune valeur" :
        bin_statistic_but_centre = pitch.bin_statistic(data_centre[data_centre.But == "Oui"].x,
                            data_centre[data_centre.But == "Oui"].y, statistic='count', bins=(nb_ligne_gauche*2, nb_col_gauche))
         
        dico_label_heatmap_centre = label_heatmap_centre(bin_statistic_centre["statistic"], bin_statistic_but_centre["statistic"])[type_compt_gauche]

        bin_statistic_centre["statistic"] = dico_label_heatmap_centre["statistique"]

        str_format_centre = dico_label_heatmap_centre["str_format"]

        pitch.label_heatmap(bin_statistic_centre, exclude_zeros = True, fontsize = int(100/(nb_col_gauche + nb_ligne_gauche)) + 2,
            color='#f4edf0', ax = ax_centre, ha='center', va='center', str_format=str_format_centre, path_effects=path_effect_2)
        
    if type_compt_droite != "Aucune valeur" :
        bin_statistic_but_recep = pitch.bin_statistic(data_recep[data_recep.But == "Oui"].x_end,
                            data_recep[data_recep.But == "Oui"].y_end, statistic='count', bins=(nb_ligne_droite*2, nb_col_droite))
        
        dico_label_heatmap_recep = label_heatmap_centre(bin_statistic_recep["statistic"], bin_statistic_but_recep["statistic"])[type_compt_droite]

        bin_statistic_recep["statistic"] = dico_label_heatmap_recep["statistique"]

        str_format_recep = dico_label_heatmap_recep["str_format"]

        pitch.label_heatmap(bin_statistic_recep, exclude_zeros = True, fontsize = int(100/(nb_col_droite + nb_ligne_droite)) + 2,
            color='#f4edf0', ax = ax_recep, ha='center', va='center', str_format=str_format_recep, path_effects=path_effect_2)
        
    pitch.heatmap(bin_statistic_centre, ax = ax_centre, cmap = colormapred, edgecolor='#000000', linewidth = 0.2)

    pitch.heatmap(bin_statistic_recep, ax = ax_recep, cmap = colormapblue, edgecolor='#000000', linewidth = 0.2)
        
    return(fig_centre, fig_recep, ax_centre, ax_recep)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Affichage des heatmaps


fig_centre, fig_recep, ax_centre, ax_recep = heatmap_percen(df_centre, df_recep_select, nb_col_gauche, nb_ligne_gauche, nb_col_droite,
                                                            nb_ligne_droite, type_compt_gauche, type_compt_droite)

if (choix_col_gauche != 0) & (choix_ligne_gauche != 0) :
    rect = patches.Rectangle(((80/nb_col_gauche)*(choix_col_gauche - 1), 60 + (60/nb_ligne_gauche)*(choix_ligne_gauche - 1)),
                                80/nb_col_gauche, 60/nb_ligne_gauche, linewidth=5, edgecolor='r', facecolor='r', alpha=0.6)
    ax_centre.add_patch(rect)

    if (choix_ligne_droite != 0) & (choix_col_droite != 0) :
        rect = patches.Rectangle(((80/nb_col_droite)*(choix_col_droite - 1), 60 + (60/nb_ligne_droite)*(choix_ligne_droite - 1)),
                                    80/nb_col_droite, 60/nb_ligne_droite, linewidth=5, edgecolor='r', facecolor='r', alpha=0.6)
        ax_recep.add_patch(rect)

columns = st.columns(2, vertical_alignment = "top", gap = "large")

with columns[0] :
    st.pyplot(fig_centre)

with columns[1] :
    st.pyplot(fig_recep)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Affichage des positions des tirs dans le cas ou une zone de réception a été sélectionnée


if len(df_shot_select) == 0 :
    st.stop()

st.divider()

columns = st.columns(2, vertical_alignment = "bottom", gap = "large")

with columns[0] :
    
    pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=1, pitch_color=None, line_color = "green", half = True,
            linewidth = 1.5, spot_scale = 0.002, goal_type = "box")

    fig_shot, ax_shot = pitch.draw(constrained_layout=True, tight_layout=False)

    ax_shot.set_ylim(min(df_shot_select.x) - 5, 125)
    
    arrows_color = pd.Series("red", index = df_shot_select.index)
    arrows_color[df_shot_select.But == "Oui"] = "blue"

    pitch.arrows(df_shot_select.x, df_shot_select.y, df_shot_select.x_end, df_shot_select.y_end, color = arrows_color, ax = ax_shot,
                 width = 1)

    st.pyplot(fig_shot)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Affichage des positions des tirs dans la cage dans le cas ou une zone de réception a été sélectionnée


with columns[1] :
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


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Affichage des informations sur les tirs venant de la zone de centre sélectionnée dans le cas ou une équipe a été sélectionnée
# Affichage également du nombre de centre total

if choix_groupe == "Choisir équipe" :

    st.divider()

    expander = st.expander("Tableau des tirs/buts pour la zone sélectionnée sur la Heatmap de gauche")

    with expander :
        df_shot_select = pd.merge(df_shot_select.reset_index(), df_info_matchs, on = "match_id")
        
        st.dataframe(df_shot_select[["match_date", "match_week", "home_team", "away_team", "minute", "Centreur", "But", "Tireur",
                    "Équipe"]], hide_index = True)

st.divider()

st.markdown(f"<p style='text-align: center;'>Nombre total de centres : {len(df_centre)}</p>", unsafe_allow_html=True)