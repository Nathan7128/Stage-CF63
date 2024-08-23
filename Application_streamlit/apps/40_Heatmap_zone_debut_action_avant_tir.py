# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Importation des librairies


import streamlit as st
import pandas as pd
from mplsoccer import VerticalPitch
import matplotlib.patches as patches
import numpy as np
import sqlite3

from fonction import execute_SQL, load_session_state, store_session_state, init_session_state, replace_saison1, replace_saison2, filtre_session_state, label_heatmap
from variable import dico_rank_SB, dico_label, colormapred, colormapblue, path_effect_1

# Index slicer pour la sélection de donnée sur les dataframes avec multi-index
idx = pd.IndexSlice


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Connection BDD


connect = sqlite3.connect("database.db")
cursor = connect.cursor()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Mise en page de la page


st.set_page_config(layout="wide")

st.title("Heatmap des zones de début d'action menant à un tir")

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
stat = f"SELECT * FROM Debut_action WHERE Compet = ? and Saison IN ({', '.join('?' * len(choix_saison))})"
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

if len(df) == 0 :
    st.stop()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Filtre des types de début d'action souhaités


liste_type_action = df.type_action.unique().tolist()

filtre_session_state("type_action_heatmap", liste_type_action)
load_session_state("type_action_heatmap")

type_action = st.multiselect("Choisir le type de début d'action", options = liste_type_action, key = "widg_type_action_heatmap",
                             on_change = store_session_state, args = ["type_action_heatmap"])

if len(type_action) == 0 :
    st.stop()

df = df[df.type_action.isin(type_action)]

st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Choix de la taille des zones de la Heatmap de gauche


columns = st.columns(2, gap = "large", vertical_alignment = "bottom")

with columns[0] :
    init_session_state("nb_col_deb_action", 5)
    load_session_state("nb_col_deb_action")
    nb_col = st.number_input("Nombre de colonne pour la Heatmap de gauche", min_value = 1, step = 1, key = "widg_nb_col_deb_action",
                             on_change = store_session_state, args = ["nb_col_deb_action"])
    
    init_session_state("nb_ligne_deb_action", 10)
    load_session_state("nb_ligne_deb_action")
    nb_ligne = st.number_input("Nombre de colonne pour la Heatmap de gauche", min_value = 1, step = 1, key = "widg_nb_ligne_deb_action",
                             on_change = store_session_state, args = ["nb_ligne_deb_action"])
    

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Choix de la condition sur les buts et du type de comptage afficher sur la heatmap de gauche


with columns[1] :
    load_session_state("but_deb_action")
    choix_but = st.checkbox("Sélectionner uniquement les débuts d'actions menant à un but", key = "widg_but_deb_action",
                            on_change = store_session_state, args = ["but_deb_action"])

    if choix_but :
        df = df[df.But == 1]
    
    load_session_state("type_compt_deb_action")
    type_compt = st.selectbox("Type de comptage", ["Pourcentage", "Pourcentage sans %", "Valeur", "Aucune valeur"],
                    key = "widg_type_compt_deb_action", on_change = store_session_state, args = ["type_compt_deb_action"])


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Possibilité de sélectionner une zone de la heatmap pour laquelle afficher les informations des actions dans le cas ou on choisit
# une ou plusieurs équipes


if choix_groupe == "Choisir équipe" :
    columns = st.columns(2)

    with columns[0] :
        init_session_state("choix_col_deb_action", 0)
        st.session_state["choix_col_deb_action"] = min(nb_col, st.session_state["choix_col_deb_action"])
        load_session_state("choix_col_deb_action")
        choix_col = st.number_input("Choisir une colonne", min_value = 0, step = 1, max_value = nb_col,
                            key = "widg_choix_col_deb_action", on_change = store_session_state, args = ["choix_col_deb_action"])    

    with columns[1] :
        init_session_state("choix_ligne_deb_action", 0)
        st.session_state["choix_ligne_deb_action"] = min(nb_ligne, st.session_state["choix_ligne_deb_action"])
        load_session_state("choix_ligne_deb_action")
        choix_ligne = st.number_input("Choisir une colonne", min_value = 0, step = 1, max_value = nb_ligne,
                            key = "widg_choix_ligne_deb_action", on_change = store_session_state, args = ["choix_ligne_deb_action"])

    if (choix_col != 0) & (choix_ligne != 0) :
        df_sort = df[(df.x >= ((120/nb_ligne)*(choix_ligne - 1))) &
                        (df.x <= ((120/nb_ligne)*(choix_ligne))) &
                        (df.y >= (80/nb_col)*(choix_col - 1)) &
                        (df.y <= (80/nb_col)*(choix_col))]


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Affichage du titre

    
st.divider()

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
# Fonction pour la création de la heatmap de gauche


@st.cache_data
def heatmap_percen(data, nb_col, nb_ligne, type_compt) :
    pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color=None, line_color = "green", axis = True, label = True,
                          tick = True, goal_type = "box", linewidth = 1, spot_scale = 0.002)
    
    fig, ax = pitch.draw(constrained_layout=True, tight_layout=False)

    ax.spines[:].set_visible(False)

    fig.set_facecolor("none")
    fig.set_edgecolor("none")
    ax.set_facecolor((1, 1, 1))

    ax.set_xticks(np.arange(80/(2*nb_col), 80 - 80/(2*nb_col) + 1, 80/nb_col), labels = np.arange(1, nb_col + 1, dtype = int))
    ax.set_yticks(np.arange(120/(2*nb_ligne), 120 - 120/(2*nb_ligne) + 1, 120/nb_ligne),
                  labels = np.arange(1, nb_ligne + 1, dtype = int))
    ax.tick_params(axis = "y", right = False, labelright = False, labelsize = "xx-small")
    ax.tick_params(axis = "x", top = False, labeltop = False, labelsize = "xx-small")

    ax.set_xlim(0, 80)
    ax.set_ylim(0, 125)

    bin_statistic = pitch.bin_statistic(data.x, data.y, statistic='count', bins=(nb_ligne, nb_col),
                                        normalize = "Pourcentage" in type_compt)
    
    pitch.heatmap(bin_statistic, ax = ax, cmap = colormapred, edgecolor='#000000', linewidth = 0.2)

    if type_compt != "Aucune valeur" :
        dico_label_heatmap = label_heatmap(bin_statistic["statistic"])[type_compt]

        bin_statistic["statistic"] = dico_label_heatmap["statistique"]

        str_format = dico_label_heatmap["str_format"]

        pitch.label_heatmap(bin_statistic, exclude_zeros = True, fontsize = int(50/(nb_ligne + nb_col)) + 2, color='#f4edf0',
                            ax = ax, ha='center', va='center', str_format=str_format, path_effects=path_effect_1)

    return fig, ax


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Fonction pour la création de la heatmap de droite


@st.cache_data
def heatmap_smooth(data) :
    pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color=None, line_color = "green", goal_type = "box",
                          linewidth = 1, spot_scale = 0.002)
    
    fig, ax = pitch.draw(constrained_layout=True, tight_layout=False)

    fig.set_facecolor("none")
    fig.set_edgecolor("none")
    ax.set_facecolor((1, 1, 1))

    ax.set_xlim([0, 87])
    ax.set_ylim([0, 125])
    
    pitch.kdeplot(data.x, data.y, ax = ax, fill = True, levels = 100, thresh = 0, cmap = colormapblue)

    return fig, ax


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Affichage des heatmaps


columns = st.columns(2)

with columns[0] :
    fig_gauche, ax_gauche = heatmap_percen(df, nb_col, nb_ligne, type_compt)

    if choix_groupe == "Choisir équipe" and (choix_col != 0) & (choix_ligne != 0) :
        rect = patches.Rectangle(((80/nb_col)*(choix_col - 1), (120/nb_ligne)*(choix_ligne - 1)), 80/nb_col, 120/nb_ligne,
                                 linewidth=4, edgecolor='r', facecolor='r', alpha=0.8)
        ax_gauche.add_patch(rect)

    st.pyplot(fig_gauche)

with columns[1] :
    fig_droite, ax_droite = heatmap_smooth(df)

    st.pyplot(fig_droite)

liste_goal_label = ["tirs", "buts"]
st.markdown(f"<p style='text-align: center;'>Nombre total de {liste_goal_label[choix_but]} : {len(df)}</p>", unsafe_allow_html=True)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Affichage des infos sur les actions dans le cas ou une zone est sélectionnée


if choix_groupe == "Choisir équipe" and choix_col > 0 and choix_ligne > 0 and len(df_sort) > 0  :
    st.divider()

    expander = st.expander("Tableau informatif pour la zone sélectionnée sur la Heatmap de gauche")

    with expander :
        df_sort = pd.merge(df_sort.reset_index(), df_info_matchs, on = "match_id")  

        st.dataframe(df_sort[["match_date", "match_week", "home_team", "away_team", "minute", "Équipe"]], hide_index = True)