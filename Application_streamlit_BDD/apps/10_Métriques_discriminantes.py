# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Importation des librairies


import streamlit as st
import pandas as pd
import numpy as np
import sqlite3

from config_py.fonction import func_change, execute_SQL, replace_saison
from config_py.variable import dico_type, dico_rank_SK, dico_rank_SB, dico_cat_run, dico_cat_met_pressure, dico_type_passe

idx = pd.IndexSlice


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Connection BDD


connect = sqlite3.connect("database.db")
cursor = connect.cursor()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Mise en page de la page


st.set_page_config(layout = "wide")

st.title("Métriques discriminantes d'une compétition")
st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Définition des fonctions utilisées dans le programme


def req_SQL(cur, statement, params) :
    return cur.execute(statement, params)

# Modif couleur colonnes différenciant les groupes
def couleur_diff(col) :
    # On regarde si la colonne passée en argument est une colonne différenciant 2 groupes
    if col.name in ["Diff. Top avec Bottom en %", "Diff. Top avec Middle en %", "Diff. Middle avec Bottom en %"] :
        color = []

        # On regarde chaque métrique et on ajoute la couleur correspondant au signe de la différence entre les 2 groupes
        for met in col.index :
            if col.loc[met] >= 0 :
                color.append("background-color : rgba(0, 255, 0, 0.3)")
            else : 
                color.append("background-color : rgba(255, 0, 0, 0.3)")
        return color
    
    # Sinon, on n'applique pas de style à la colonne
    else :
        return ['']*len(col)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Choix de la saison et du fournisseur de donnée


columns = st.columns(3, gap = "large")
st.divider()
columns2 = st.columns(2, gap = "large", vertical_alignment = "center")

with columns[0] :
    # Choix du fournisseur de données
    func_change("select_data", "choix_data")
    choix_data = st.radio("Fournisseur data", options = ["Skill Corner", "Stats Bomb"], horizontal = True,
                          key = "select_data", on_change = func_change, args = ("choix_data", "select_data"))
    
if choix_data == "Skill Corner" :

    table_met = dico_type[st.session_state.cat_met][0]

    dico_rank = dico_rank_SK

    st.divider()
    columns3 = st.columns([2, 1, 1], vertical_alignment = "center", gap = "medium")

    with columns3[2] :
        win_met = st.checkbox("Métriques pour les équipes qui gagnent les matchs")
    
else :
    table_met = "Métriques_SB"
    win_met = False
    dico_rank = dico_rank_SB
    
# Choix Compet
params = []
stat = f"SELECT DISTINCT Compet FROM {table_met}"
liste_compet = execute_SQL(cursor, stat, params).fetchall()
liste_compet = [i[0] for i in liste_compet]
    
with columns[1] :
    choix_compet = st.selectbox("Choisir compétition", options = liste_compet, index = 0)

# Choix d'une ou plusieurs saisons sur laquelle/lesquelles on va étudier les métriques pour Skill Corner
params = [choix_compet]
stat = f"SELECT DISTINCT Saison FROM {table_met} WHERE Compet = ?"
liste_saison = execute_SQL(cursor, stat, params).fetchall()
liste_saison = [i[0] for i in liste_saison]

with columns[2] :
    choix_saison = st.multiselect("Choisir saison", replace_saison(liste_saison), default = max(replace_saison(liste_saison)))
choix_saison = [i.replace("/", "_") for i in choix_saison]

# On regarde si au moins une saison est choisie
if len(choix_saison) == 0 :
    st.stop()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Création du dataframe en choisissant le type de métrique qu'on souhaite étudier


params = [choix_compet] + choix_saison
stat = f"SELECT * FROM {table_met} WHERE Compet = ? and Saison IN ({', '.join('?' * len(choix_saison))})"
res = execute_SQL(cursor, stat, params)

df_metrique = pd.DataFrame(res.fetchall())
df_metrique.columns = [i[0] for i in res.description]
df_metrique = df_metrique.drop("Compet", axis = 1).set_index(["Saison", "team_name"])

if win_met :
    df_metrique = df_metrique[df_metrique.result == "win"]


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Choix de la taille des groupes sur lesquels aggréger les données


df_nb_team = df_metrique.reset_index()[["Saison", "team_name"]].drop_duplicates().groupby("Saison").apply(len)

max_team = max(df_nb_team)

with columns2[0] :
    # Choix du nombre d'équipe dans le Top. Possible de choisir toutes les équipes du championnat
    nb_top = st.slider("Nombre d'équipe dans le Top :", min_value = 1, max_value = max_team, value = 5)

with columns2[1] :
    # On regarde si le top correspond à toutes les équipes du championnat ou non. Si oui, le slider bug donc d'ou le if/else
    if nb_top == max_team :
        nb_bottom = max_team - nb_top
        st.write(f"Nombre d'équipe dans le Bottom : {nb_bottom}")

    else :
        # Choix de la taille du groupe bottom, initialisé à 0.
        nb_bottom = st.slider(f"Nombre d'équipe dans le Bottom", min_value = 0, max_value = max_team - nb_top)

# Calcul par différence de la taille du groupe Middle
nb_middle = df_nb_team - nb_top - nb_bottom


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Création du dataframe qu'on va afficher sur la page


if choix_data == "Skill Corner" :

    df_metrique.drop(["result", "Journée"], inplace = True, axis = 1)
        
    # Calcul du nombre de match joué par équipe sur la saison et tri des équipes en fonction de leur classement sur la saison
    nb_matchs_team = df_metrique.apply(len)

    # On fait la somme pour chaque métrique sur toutes les journées de la saison
    df_metrique = df_metrique.sum()

    # On divise pour faire la moyenne par saison pour chaque équipe pour chaque métrique
    df_metrique = df_metrique.divide(nb_matchs_team, axis = 0)


# Le dataframe final aura comme index la liste des métriques sélectionnées

for saison in choix_saison :
    liste_rank = dico_rank[saison]
    
    df_metrique.loc[idx[saison, liste_rank[:nb_top]], "Groupe"] = "Top"
    df_metrique.loc[idx[saison, liste_rank[nb_top:nb_top + nb_middle.loc[saison]]], "Groupe"] = "Middle"
    df_metrique.loc[idx[saison, liste_rank[nb_top + nb_middle.loc[saison]:]], "Groupe"] = "Bottom"

df_rank_team = df_metrique.pop("Groupe")

# Le dataframe final aura comme index la liste des métriques sélectionnées
df_final = pd.DataFrame(index = df_metrique.columns)

# Dataframe ne comprenant que les équipes du top
df_top = df_metrique[df_rank_team == "Top"]

# Dataframe ne comprenant que les équipes du middle
df_middle = df_metrique[df_rank_team == "Middle"]

# Dataframe ne comprenant que les équipes du bottom
df_bottom = df_metrique[df_rank_team == "Bottom"]

# Moyenne du top pour chaque métrique
df_final["Moyenne Top"] = df_top.mean(axis = 0)

# Moyenne du bottom pour chaque métrique
df_final["Moyenne Middle"] = df_middle.mean(axis = 0)

# Moyenne du middle pour chaque métrique
df_final["Moyenne Bottom"] = df_bottom.mean(axis = 0)

# Calcul des différences entre les différents groupes
# Méthode de calcul de la différence entre a et b : diff = (b - a)/(abs(a))
df_final["Diff. Top avec Bottom en %"] = (100*(df_final["Moyenne Top"] - df_final["Moyenne Bottom"])/abs(df_final["Moyenne Bottom"])).round(2)
df_final["Diff. Top avec Middle en %"] = (100*(df_final["Moyenne Top"] - df_final["Moyenne Middle"])/abs(df_final["Moyenne Middle"])).round(2)
df_final["Diff. Middle avec Bottom en %"] = (100*(df_final["Moyenne Middle"] - df_final["Moyenne Bottom"])/abs(df_final["Moyenne Bottom"])).round(2)

# Calcul de différente stats sur les différents groupes, dans le cas ou au moins 2 équipes appartiennent au groupe
if len(df_top) > 1 :
    df_final["Ecart type Top"] = df_top.std(axis = 0)
    df_final["Min Top"] = df_top.min(axis = 0)
    df_final["Max Top"] = df_top.max(axis = 0)

if len(df_middle) > 1 :
    df_final["Ecart type Middle"] = df_middle.std(axis = 0)
    df_final["Min Middle"] = df_middle.std(axis = 0)
    df_final["Max Middle"] = df_middle.std(axis = 0)

if len(df_bottom) > 1 :
    df_final["Ecart type Bottom"] = df_bottom.std(axis = 0)
    df_final["Min Bottom"] = df_bottom.min(axis = 0)
    df_final["Max Bottom"] = df_bottom.max(axis = 0)

# Si le bottom est non vide, on trie le df final en fonction de la diff. entre le top et bottom, de manière décroissante
if nb_bottom > 0 :
    df_final = df_final.reindex(abs(df_final).sort_values(by = "Diff. Top avec Bottom en %", ascending = False).index)

# Si le bottom est vide mais pas le middle, on trie le df final en fonction de la diff. entre le top et bottom,
# de manière décroissante
elif len(nb_middle) > 0 :
    df_final = df_final.reindex(abs(df_final).sort_values(by = "Diff. Top avec Middle en %", ascending = False).index)

# Si le bottom et le middle sont vides, on ne trie pas le dataframe final

# dropna qui permet de modifier les colonnes correspondant aux groupes vides
df_final.dropna(axis = 1, how = "all", inplace = True)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Sélection des métriques via l'interface Streamlit


# Filtrage des métriques uniquement dans le cas Skill Corner
if choix_data == "Skill Corner" :

    with columns3[0] :
        # Choix de la catégorie de métrique
        func_change("select_cat_met", "cat_met")
        cat_met = st.radio("Catégorie de métrique", dico_type.keys(), horizontal = True, key = 'select_cat_met',
                            on_change = func_change, args = ("cat_met", "select_cat_met"))

    with columns3[1] :
        # Choix de la moyenne pour la catégorie de métrique choisie
        cat_moy = st.radio("Moyenne de la métrique", dico_type[cat_met][1].keys(), horizontal = True)

    # On garde les métriques avec la moyenne choisie
    cat_type = dico_type[cat_met][1][cat_moy]

    # col_keep est une liste de taille = nombre total de métrique et qui contient des True/False pour savoir si on garde ou non
    # la métrique correspondante
    # Les métriques ratios ne sont pas aggrégés par durée ou nombre d'évènement
    col_keep = [(cat_type in i) or ("ratio" in i) for i in df_final.index]
    df_final = df_final.iloc[col_keep]

    # Les catégories autres que Physiques contiennent des type de métrique : type de course et type de pression
    if cat_met != "Physiques" :
        # Sélection du type de métrique
        col_keep = [False]*len(df_final)
        liste_cat_type1 = st.multiselect(dico_type[cat_met][2], dico_type[cat_met][3].keys(), default = dico_type[cat_met][3].keys())
        for cat_type in liste_cat_type1 :
            cat_type = dico_type[cat_met][3][cat_type]
            col_keep = np.logical_or(col_keep, [(cat_type in i) or ("ratio" in i and cat_type in i) for i in df_final.index])
        df_final = df_final.iloc[col_keep]

        # On filtre ensuite les métriques au cas par cas pour chaque catégorie de métrique
        # col_keep va être modifier au fur et à mesure des filtres choisit
        if cat_met == "Courses sans ballon avec la possession" :
            col_keep = [True]*len(df_final)
            columns = st.columns([2, 1, 1], vertical_alignment = "center", gap = "large")
            with columns[0] :
                liste_cat_run = ["All"] + list(dico_cat_run.keys())
                cat_run_choice = st.multiselect("Catégorie du run", options = liste_cat_run, default = liste_cat_run)
                if "All" not in cat_run_choice :
                    col_keep = [False]*len(df_final)
                    for cat_run in dico_cat_run.values() :
                        col_keep = np.logical_or(col_keep, [cat_run in i for i in df_final.index])
                for cat_run in dico_cat_run.keys() :
                    if cat_run not in cat_run_choice :
                        col_keep = np.logical_and(col_keep, [dico_cat_run[cat_run] not in i for i in df_final.index])

            with columns[1] :
                if not(st.checkbox('Métrique "threat"', value = True)) :
                    col_keep = np.logical_and(col_keep, ["threat" not in i for i in df_final.index])

            with columns[2] :
                liste_type_passe_run = ["Targeted", "Received"]
                type_passe_run = st.multiselect("Type de passe liée au run", liste_type_passe_run, default = liste_type_passe_run)
                if "Targeted" not in type_passe_run :
                    col_keep = np.logical_and(col_keep, ["targeted" not in i for i in df_final.index])
                if "Received" not in type_passe_run :
                    col_keep = np.logical_and(col_keep, ["received" not in i for i in df_final.index])


        elif cat_met == "Action sous pression" :
            col_keep = [False]*len(df_final)
            columns = st.columns(3, vertical_alignment = "center", gap = "large")
            with columns[0] :
                cat_met_pressure = st.multiselect("Catégorie de métrique liée au pressing", dico_cat_met_pressure.keys(),
                                                default = dico_cat_met_pressure.keys())
                for cat_met in cat_met_pressure :
                    col_keep = np.logical_or(col_keep, [dico_cat_met_pressure[cat_met] in i for i in df_final.index])

            if "Passes" in cat_met_pressure :
                with columns[1] :
                    dico_type_passe_pressure = {"All" : [(("pass_completion" not in i) or ("dangerous" in i) or ("difficult" in i)) and 
                        ("count_completed_pass" not in i) and ("count_pass_attempts" not in i) for i in df_final.index],
                        "Dangerous" : ["dangerous" not in i for i in df_final.index], 
                        "Difficult" : ["difficult" not in i for i in df_final.index]}
                    type_passe_pressure = st.multiselect("Type de passe", dico_type_passe_pressure.keys(), default = dico_type_passe_pressure.keys())
                    for type_passe in dico_type_passe_pressure.keys() :
                        if type_passe not in type_passe_pressure :
                            col_keep = np.logical_and(col_keep, dico_type_passe_pressure[type_passe])
                    result_pass_pressure = st.multiselect("Résultat de la passe sous pression", ["Attempts", "Completed"],
                                                        default = ["Attempts", "Completed"])
                    if "Attempts" not in result_pass_pressure :
                        col_keep = np.logical_and(col_keep, ["attempts" not in i for i in df_final.index])
                    if "Completed" not in result_pass_pressure :
                        col_keep = np.logical_and(col_keep, ["completed" not in i for i in df_final.index])

            with columns[-1] :
                if "Passes" in cat_met_pressure :
                    if not(st.checkbox("Ratio lié aux passes", value = True)) :
                        col_keep = np.logical_and(col_keep, [("pass" not in i) or ("ratio" not in i) for i in df_final.index])                   
                if "Conservation du ballon" in cat_met_pressure :
                    if not(st.checkbox("Ratio lié à la conservation du ballon", value = True)) :
                        col_keep = np.logical_and(col_keep, ["ball_retention_ratio" not in i for i in df_final.index])


        else :
            col_keep = [True]*len(df_final)
            columns = st.columns([2, 1, 1, 2], vertical_alignment = "center", gap = "large")

            with columns[0] :
                liste_cat_run = ["All"] + list(dico_cat_run.keys())
                cat_run_choice = st.multiselect("Catégorie du run", options = liste_cat_run, default = liste_cat_run)
                if "All" not in cat_run_choice :
                    col_keep = [False]*len(df_final)
                    for cat_run in dico_cat_run.values() :
                        col_keep = np.logical_or(col_keep, [cat_run in i for i in df_final.index])
                for cat_run in dico_cat_run.keys() :
                    if cat_run not in cat_run_choice :
                        col_keep = np.logical_and(col_keep, [dico_cat_run[cat_run] not in i for i in df_final.index])

            with columns[3] :
                choix_type_passe = st.multiselect("Type de passe", dico_type_passe.keys(), default = dico_type_passe.keys())
                col_keep_passe = [False]*len(df_final)
                for type_passe in choix_type_passe :
                    col_keep_passe = np.logical_or(col_keep_passe, [dico_type_passe[type_passe] in i for i in df_final.index])
                col_keep = np.logical_and(col_keep, col_keep_passe)
                if "All" in cat_run_choice :
                    col_keep = np.logical_or(col_keep, ["teammate" in i for i in df_final.index])

            with columns[1] :
                if not(st.checkbox('Métrique "threat"', value = True)) :
                    col_keep = np.logical_and(col_keep, ["threat" not in i for i in df_final.index])

            with columns[2] :
                if st.checkbox("Ratio", True) :
                    col_keep = np.logical_or(col_keep, ["ratio" in i for i in df_final.index])


        df_final = df_final.iloc[col_keep]

        st.divider()


if len(df_final) == 0 :
    st.stop()

st.divider()

# On peut choisir le nombre final de métrique que l'on souhaite gardé parmis les métriques filtrées
nb_metrique = st.slider("Nombre de métriques gardées", min_value=0, max_value = df_final.shape[0], value = df_final.shape[0])
df_final = df_final.loc[df_final.index[:nb_metrique]]

# Choix des colonnes du df final
col_df = st.multiselect("Données des métriques à afficher", df_final.columns, df_final.columns.tolist())

moyenne_sort = df_final[col_df]

# On vérifie qu'au moins une colonne ai été gardée
if len(col_df) == 0 :
    st.stop()

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Style et affichage du dataframe


st.divider()

st.markdown("<p style='text-align: center;'>Tableau des métriques discriminantes</p>", unsafe_allow_html=True)

# Application du style
moyenne_sort_style = moyenne_sort.style.apply(couleur_diff, axis = 0)

# Affichage du dataframe stylisé
moyenne_sort_df = st.dataframe(moyenne_sort_style, on_select = "rerun", selection_mode = "multi-row")


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Affichage des stats pour les métriques sélectionnées par équipe pour les saisons sélectionnées


# On vérifie qu'au moins une métrique est sélectionnée
if len(moyenne_sort_df.selection.rows) == 0 :
    st.stop()

for saison in choix_saison :
    
    saison_widg = replace_saison(saison)
    st.divider()
    st.markdown(f"<p style='text-align: center;'>Tableau des métriques retenues, par équipes, en moyenne par match lors de la saison {saison_widg} </p>", unsafe_allow_html=True)
    metrique_moyenne_sort = df_metrique.loc[saison, :][df_final.index[moyenne_sort_df.selection.rows]]
    st.dataframe(metrique_moyenne_sort)