# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Importation des librairies


import streamlit as st
import pandas as pd
import matplotlib.patches as patches
import sqlite3
from functools import partial

from fonction import execute_SQL, load_session_state, key_widg, init_session_state, filtre_session_state, push_session_state, get_session_state, heatmap_gauche_deb_action, heatmap_droite_deb_action
from variable import dico_rank_SB, df_taille_groupe, dico_label

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
# Définition des fonctions de mofication du session state


load_session_state = partial(load_session_state, suffixe = "_deb_action")
key_widg = partial(key_widg, suffixe = "_deb_action")
get_session_state = partial(get_session_state, suffixe = "_deb_action")
init_session_state = partial(init_session_state, suffixe = "_deb_action")
push_session_state = partial(push_session_state, suffixe = "_deb_action")
filtre_session_state = partial(filtre_session_state, suffixe = "_deb_action")


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Choix de la compétition, de la saison et du groupe à afficher


columns = st.columns([2, 4, 3], vertical_alignment = "center", gap = "large")

params = []
stat = f"SELECT DISTINCT Compet FROM Passes_avant_un_but"
liste_compet, desc = execute_SQL(cursor, stat, params)
liste_compet = [i[0] for i in liste_compet]
    
with columns[0] :
    load_session_state("compet")
    choix_compet = st.selectbox("Choisir compétition", options = liste_compet, **key_widg("compet"))

params = [choix_compet]
stat = f"SELECT DISTINCT Saison FROM Passes_avant_un_but WHERE Compet = ?"
liste_saison, desc = execute_SQL(cursor, stat, params)
liste_saison = [i[0] for i in liste_saison]

with columns[1] :
    init_session_state("saison", [max(liste_saison)])
    load_session_state("saison")
    choix_saison = st.multiselect("Choisir saison", liste_saison, **key_widg("saison"))

with columns[2] :
    load_session_state("groupe")
    choix_groupe = st.radio("Choix groupe", ["Choisir Top/Middle/Bottom", "Choisir équipe"], label_visibility = "hidden",
                            **key_widg("groupe"))

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


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Choix taille des groupes et ceux à afficher ou choix des équipes


liste_équipe = df.index.levels[1]

if choix_groupe == "Choisir Top/Middle/Bottom" :
    df_nb_team = df.reset_index()[["Saison", "Équipe"]].drop_duplicates().groupby("Saison").apply(len)

    max_nb_team = min(df_nb_team)

    columns = st.columns(3, gap = "large", vertical_alignment = "center")

    with columns[0] :
        load_session_state("nb_top")
        df_taille_groupe.loc["Top", "Taille"] = st.slider(df_taille_groupe.loc["Top", "Slider"], min_value = 1,
                max_value = max_nb_team, **key_widg("nb_top"))    
        
    with columns[1] :
        if df_taille_groupe.loc["Top", "Taille"] == max_nb_team :
            push_session_state("nb_bottom", max_nb_team - df_taille_groupe.loc["Top", "Taille"])

        else :
            push_session_state("nb_bottom", min(max_nb_team - df_taille_groupe.loc["Top", "Taille"], get_session_state("nb_bottom")))
            load_session_state("nb_bottom")
            st.slider(df_taille_groupe.loc["Bottom", "Slider"], min_value = 0,
                    max_value = max_nb_team - df_taille_groupe.loc["Top", "Taille"], **key_widg("nb_bottom"))
            
        df_taille_groupe.loc["Bottom", "Taille"] = get_session_state("nb_bottom")
    
    df_taille_groupe.loc["Middle", "Taille"] = max_nb_team - df_taille_groupe.loc["Top", "Taille"] - df_taille_groupe.loc["Bottom", "Taille"]

    with columns[2] :
        groupe_non_vide = df_taille_groupe[df_taille_groupe.Taille > 0].index.tolist()*(df_taille_groupe.loc["Top", "Taille"] != max_nb_team) + ["Global"]
        
        if "groupe_plot_deb_action" in st.session_state and st.session_state["groupe_plot_deb_action"] not in groupe_non_vide :
            del st.session_state["groupe_plot_deb_action"]
        load_session_state("groupe_plot")
        groupe_plot = st.radio("Groupe à afficher", groupe_non_vide, horizontal = True, **key_widg("groupe_plot"))

else :
    filtre_session_state("équipe", liste_équipe)
    load_session_state("équipe")
    équipe_plot = st.multiselect("Équipe à afficher", liste_équipe, **key_widg("équipe"))

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

filtre_session_state("type_action", liste_type_action)
load_session_state("type_action")
type_action = st.multiselect("Choisir le type de début d'action", options = liste_type_action, **key_widg("type_action"))

if len(type_action) == 0 :
    st.stop()

df = df[df.type_action.isin(type_action)]

st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Choix de la taille des zones de la Heatmap de gauche


columns = st.columns(2, gap = "large", vertical_alignment = "bottom")

with columns[0] :
    load_session_state("nb_col")
    nb_col = st.number_input("Nombre de colonne pour la Heatmap de gauche", min_value = 1, step = 1, **key_widg("nb_col"))
    
    init_session_state("nb_ligne", 10)
    load_session_state("nb_ligne")
    nb_ligne = st.number_input("Nombre de ligne pour la Heatmap de gauche", min_value = 1, step = 1, **key_widg("nb_ligne"))
    

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Choix de la condition sur les buts et du type de comptage afficher sur la heatmap de gauche


with columns[1] :
    load_session_state("but")
    choix_but = st.checkbox("Sélectionner uniquement les débuts d'actions menant à un but", **key_widg("but"))

    if choix_but :
        df = df[df.But == 1]
    
    load_session_state("type_compt")
    type_compt = st.selectbox("Type de comptage", ["Pourcentage", "Pourcentage sans %", "Valeur", "Aucune valeur"],
                    **key_widg("type_compt"))


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Possibilité de sélectionner une zone de la heatmap pour laquelle afficher les informations des actions dans le cas ou on choisit
# une ou plusieurs équipes


if choix_groupe == "Choisir équipe" :
    columns = st.columns(2)

    with columns[0] :
        push_session_state("choix_col", min(nb_col, get_session_state("choix_col")))
        load_session_state("choix_col")
        choix_col = st.number_input("Choisir une colonne", min_value = 0, step = 1, max_value = nb_col, **key_widg("choix_col"))    

    with columns[1] :
        push_session_state("choix_ligne", min(nb_ligne, get_session_state("choix_ligne")))
        load_session_state("choix_ligne")
        choix_ligne = st.number_input("Choisir une ligne", min_value = 0, step = 1, max_value = nb_ligne, **key_widg("choix_ligne"))

    if (choix_col != 0) & (choix_ligne != 0) :
        df_sort = df[(df.x_loc >= ((120/nb_ligne)*(choix_ligne - 1))) &
                        (df.x_loc <= ((120/nb_ligne)*(choix_ligne))) &
                        (df.y_loc >= (80/nb_col)*(choix_col - 1)) &
                        (df.y_loc <= (80/nb_col)*(choix_col))]


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Affichage du titre

    
st.divider()

choix_saison.sort()

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
# Affichage des heatmaps


columns = st.columns(2)

with columns[0] :
    fig_gauche, ax_gauche = heatmap_gauche_deb_action(df, nb_col, nb_ligne, type_compt)

    if choix_groupe == "Choisir équipe" and (choix_col != 0) & (choix_ligne != 0) :
        rect = patches.Rectangle(((80/nb_col)*(choix_col - 1), (120/nb_ligne)*(choix_ligne - 1)), 80/nb_col, 120/nb_ligne,
                                 linewidth=4, edgecolor='r', facecolor='r', alpha=0.8)
        ax_gauche.add_patch(rect)

    st.pyplot(fig_gauche)

with columns[1] :
    fig_droite, ax_droite = heatmap_droite_deb_action(df)

    st.pyplot(fig_droite)

liste_goal_label = ["tirs", "buts"]
st.markdown(f"<p style='text-align: center;'>Nombre total de {liste_goal_label[choix_but]} : {len(df)}</p>", unsafe_allow_html=True)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Affichage des infos sur les actions dans le cas ou une zone est sélectionnée


if choix_groupe == "Choisir équipe" and choix_col > 0 and choix_ligne > 0 and len(df_sort) > 0  :
    st.divider()

    expander = st.expander("Tableau informatif pour la zone sélectionnée sur la Heatmap de gauche")

    with expander :
        st.dataframe(df_sort.reset_index()[["Date", "Journée", "Domicile", "Extérieur", "Minute", "Équipe"]], hide_index = True)