# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Importation des librairies


import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3

from fonction import execute_SQL, load_session_state, store_session_state, init_session_state, replace_saison2, replace_saison1, filtre_session_state, load_session_state_met, store_session_state_met
from variable import dico_met, dico_rank_SK

# Index slicer pour la sélection de donnée sur les dataframes avec multi-index
idx = pd.IndexSlice


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Connection BDD


connect = sqlite3.connect("database.db")
cursor = connect.cursor()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Mise en page de la page


st.set_page_config(layout = "wide")

st.title("Évolution des métriques au cours des journées")

st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Définition des variables


groupe_plot = []

groupe_non_vide = []

équipe_plot = []


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Choix de la compétition, de la saison et du type de groupe (équipe et/ou rank)


columns = st.columns(3, gap = "large")

table_met = dico_met[st.session_state.cat_met][0]

dico_rank = dico_rank_SK
    
params = []
stat = f"SELECT DISTINCT Compet FROM {table_met}"
liste_compet, desc = execute_SQL(cursor, stat, params)
liste_compet = [i[0] for i in liste_compet]
    
with columns[0] :
    load_session_state("compet_met")
    choix_compet = st.selectbox("Choisir compétition", options = liste_compet, key = "widg_compet_met", on_change = store_session_state,
                                args = ["compet_met"])

params = [choix_compet]
stat = f"SELECT DISTINCT Saison FROM {table_met} WHERE Compet = ?"
liste_saison, desc = execute_SQL(cursor, stat, params)
liste_saison = [i[0] for i in liste_saison]

with columns[1] :
    init_session_state("saison_evo_jour", max(replace_saison1(liste_saison)))
    load_session_state("saison_evo_jour")
    choix_saison = st.selectbox("Choisir saison", replace_saison1(liste_saison), key = "widg_saison_evo_jour",
                                  on_change = store_session_state, args = ["saison_evo_jour"])

choix_saison = replace_saison2(choix_saison)

with columns[2] :
    ""

    load_session_state("groupe_rank_evo_jour")
    choix_groupe_rank = st.checkbox("Sélectionner Top/Middle/Bottom", key = "widg_groupe_rank_evo_jour", on_change = store_session_state,
                                    args = ["groupe_rank_evo_jour"])
    
    load_session_state("groupe_équipe_evo_jour")
    choix_groupe_équipe = st.checkbox("Sélectionner équipe", key = "widg_groupe_équipe_evo_jour", on_change = store_session_state,
                                    args = ["groupe_équipe_evo_jour"])


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Importation du dataframe après avoir effectuer les choix pour le filtrage des données


params = [choix_compet, choix_saison]
stat = f"SELECT * FROM {table_met} WHERE Compet = ? and Saison = ?"
res, desc = execute_SQL(cursor, stat, params)

df = pd.DataFrame(res)
df.columns = [i[0] for i in desc]
df.set_index(["Journée", "team_name"], inplace = True)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Choix taille des groupes et ceux à afficher ou choix des équipes


liste_équipe = df.reindex(dico_rank[choix_saison], level = 1, axis = 0).index.levels[1]

max_nb_team = len(df.index.levels[1])

if choix_groupe_rank :
    st.divider()

    df_taille_groupe = pd.DataFrame(0, index = ["Top", "Middle", "Bottom"], columns = ["Taille", "Slider"])

    df_taille_groupe["Slider"] = "Nombre d'équipe dans le " + df_taille_groupe.index

    columns = st.columns(3, gap = "large", vertical_alignment = "center")

    with columns[0] :
        load_session_state("nb_top_met")
        df_taille_groupe.loc["Top", "Taille"] = st.slider(df_taille_groupe.loc["Top", "Slider"], min_value = 1,
                max_value = max_nb_team, key = "widg_nb_top_met", on_change = store_session_state, args = ["nb_top_met"])
        
    with columns[1] :
        if df_taille_groupe.loc["Top", "Taille"] == max_nb_team :
            st.session_state["nb_bottom_met"] = max_nb_team - df_taille_groupe.loc["Top", "Taille"]

        else :
            st.session_state["nb_bottom_met"] = min(max_nb_team - df_taille_groupe.loc["Top", "Taille"],
                                                    st.session_state["nb_bottom_met"])
            load_session_state("nb_bottom_met")
            st.slider(df_taille_groupe.loc["Bottom", "Slider"], min_value = 0,
                    max_value = max_nb_team - df_taille_groupe.loc["Top", "Taille"], key = "widg_nb_bottom_met",
                    on_change = store_session_state, args = ["nb_bottom_met"])
            
        df_taille_groupe.loc["Bottom", "Taille"] = st.session_state["nb_bottom_met"]
            
    df_taille_groupe.loc["Middle", "Taille"] = max_nb_team - df_taille_groupe.loc["Top", "Taille"] - df_taille_groupe.loc["Bottom", "Taille"]

    with columns[2] :
        groupe_non_vide = df_taille_groupe[df_taille_groupe.Taille > 0].index

        filtre_session_state("groupe_evo_jour", groupe_non_vide)
        load_session_state("groupe_evo_jour")
        groupe_plot = st.multiselect("Groupe à afficher", groupe_non_vide, key = "widg_groupe_evo_jour", on_change = store_session_state,
                                     args = ["groupe_evo_jour"])

if choix_groupe_équipe :
    st.divider()

    filtre_session_state("équipe_evo_jour", liste_équipe)
    load_session_state("équipe_evo_jour")
    équipe_plot = st.multiselect("Équipe à afficher", liste_équipe, key = "widg_équipe_evo_jour", on_change = store_session_state,
                                     args = ["équipe_evo_jour"])


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Filtrage des métriques et choix de la condition de victoire sur les matchs


st.divider()

columns = st.columns([2, 1, 1], vertical_alignment = "center", gap = "large")

with columns[0] :
    load_session_state("cat_met")
    cat_met = st.radio("Catégorie de métrique", dico_met.keys(), horizontal = True, key = "widg_cat_met",
                on_change = store_session_state, args = ["cat_met"])

with columns[2] :
    load_session_state("win_match")
    if st.checkbox("Métriques pour les équipes qui gagnent les matchs", key = 'widg_win_match', on_change = store_session_state,
                   args = ["win_match"]) :
        df = df[df.result == "win"]

with columns[1] :
    load_session_state(f"moy_cat_{cat_met}")
    moy_cat = st.radio("Moyenne de la métrique", dico_met[cat_met][1].keys(), horizontal = True, key = f'widg_moy_cat_{cat_met}',
                        on_change = store_session_state, args = [f"moy_cat_{cat_met}"])

    moy_cat = dico_met[cat_met][1][moy_cat]

    col_keep = [(moy_cat in i) or ("ratio" in i) for i in df.columns]
    df = df[df.columns[col_keep]]


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Choix de la métrique


if cat_met != "Physiques" :
    columns = st.columns([1, 2])

    with columns[0] :
        load_session_state(f"type_cat_{cat_met}_evo_jour")
        type_cat = st.selectbox(dico_met[cat_met][2], dico_met[cat_met][3], key = f'widg_type_cat_{cat_met}_evo_jour',
                        on_change = store_session_state, args = [f"type_cat_{cat_met}_evo_jour"])
        
        type_cat = dico_met[cat_met][3][type_cat]
        df = df[df.columns[[type_cat in i for i in df.columns]]]

    with columns[1] :
        load_session_state_met(f"met_{cat_met}{type_cat}_evo_jour", moy_cat)
        choix_metrique = st.selectbox("Choisir la métrique", df.columns, key = f'widg_met_{cat_met}{type_cat}_evo_jour',
                        on_change = store_session_state_met, args = [f"met_{cat_met}{type_cat}_evo_jour", moy_cat])

else :
    load_session_state_met(f"met_{cat_met}_evo_jour", moy_cat)
    choix_metrique = st.selectbox("Choisir la métrique", df.columns, key = f'widg_met_{cat_met}_evo_jour',
                        on_change = store_session_state_met, args = [f"met_{cat_met}_evo_jour", moy_cat])

df = df[choix_metrique]


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Création du dataframe qui contient les données à afficher pour la métrique et les groupes/équipes choisit


df_final = pd.DataFrame(index = df.index.levels[0])

if "Top" in groupe_plot :
    df_final["Top"] = df.loc[:, liste_équipe[:df_taille_groupe.loc["Top", "Taille"]], :].groupby("Journée").mean()
if "Middle" in groupe_plot :
    df_final["Middle"] = df.loc[:, liste_équipe[df_taille_groupe.loc["Top", "Taille"]:df_taille_groupe.loc["Top", "Taille"] + df_taille_groupe.loc["Middle", "Taille"]], :].groupby("Journée").mean()
if "Bottom" in groupe_plot :
    df_final["Bottom"] = df.loc[:, liste_équipe[df_taille_groupe.loc["Top", "Taille"] + df_taille_groupe.loc["Middle", "Taille"]:], :].groupby("Journée").mean()

for équipe in équipe_plot :
    df_final[équipe] = df.loc[:, équipe, :]


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Affichage des données


if len(groupe_plot) + len(équipe_plot) == 0 :
    st.stop()

st.divider()

fig = plt.figure(figsize = (8, 4))

plt.plot(df_final, marker = "o", markersize = 3, linewidth = 0.7)

bool_taille_grp = len(df_final.columns) > 1
grp_title = []
grp_title.append(f'{df_final.columns[0]}')
grp_title.append(f'{", ".join(df_final.columns[:-1])} et {df_final.columns[-1]}')
plt.title(f"Graphe de la métrique {choix_metrique}\npour{' le'*(len(groupe_plot) > 0)} {grp_title[bool_taille_grp]} \nau cours des journées de la saison {replace_saison1(choix_saison)}",
            fontweight = "heavy", y = 1.05, fontsize = 9)

plt.legend(df_final.columns, bbox_to_anchor=(0.5, -0.25), fontsize = "small", ncol = 2)

plt.grid()

plt.xlabel("Journée", fontsize = "small", fontstyle = "italic", labelpad = 10)
plt.ylabel(choix_metrique, fontsize = "small", fontstyle = "italic", labelpad = 10)

plt.xticks(np.arange(1, df.index.levels[0][-1], 3))
plt.tick_params(labelsize = 8)

ax = plt.gca()
ax.spines[:].set_visible(False)

st.pyplot(fig)