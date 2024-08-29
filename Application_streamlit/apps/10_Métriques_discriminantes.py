# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Importation des librairies


import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from functools import partial

from fonction import couleur_diff, load_session_state, key_widg, get_session_state, execute_SQL, init_session_state, filtre_session_state, push_session_state
from variable import dico_met, dico_rank_SK, dico_rank_SB, liste_cat_run, dico_cat_run, dico_cat_pressure, dico_cat_passe, liste_type_passe_run, liste_cat_pressure, liste_cat_passe_pressure, liste_type_passe

# Index slicer pour la sélection de donnée sur les dataframes avec multi-index
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
# Définition des fonctions


load_session_state = partial(load_session_state, suffixe = "_met_disc")
key_widg = partial(key_widg, suffixe = "_met_disc")
get_session_state = partial(get_session_state, suffixe = "_met_disc")
init_session_state = partial(init_session_state, suffixe = "_met_disc")
filtre_session_state = partial(filtre_session_state, suffixe = "_met_disc")
push_session_state = partial(push_session_state, suffixe = "_met_disc")


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Choix du fournisseur de donnée, de la compétition et de la ou des saisons


columns = st.columns([1, 2, 3], gap = "large")

with columns[0] :
    load_session_state("provider")
    choix_provider = st.radio("Fournisseur data", options = ["Skill Corner", "Stats Bomb"], horizontal = True, **key_widg("provider"))
    
if choix_provider == "Skill Corner" :
    table_met = dico_met[get_session_state("cat_met")][0]
    dico_rank = dico_rank_SK
    
else :
    table_met = "Métriques_SB"
    dico_rank = dico_rank_SB

params = []
stat = f"SELECT DISTINCT Compet FROM {table_met}"
liste_compet, desc = execute_SQL(cursor, stat, params)
liste_compet = [i[0] for i in liste_compet]
    
with columns[1] :
    load_session_state("compet")
    choix_compet = st.selectbox("Choisir compétition", options = liste_compet, **key_widg("compet"))

params = [choix_compet]
stat = f"SELECT DISTINCT Saison FROM {table_met} WHERE Compet = ?"
liste_saison, desc = execute_SQL(cursor, stat, params)
liste_saison = [i[0] for i in liste_saison]

with columns[2] :
    init_session_state("saison", [max(liste_saison)])
    filtre_session_state("saison", liste_saison)
    load_session_state("saison")
    choix_saison = st.multiselect("Choisir saison", liste_saison, **key_widg("saison"))

if len(choix_saison) == 0 :
    st.stop()

st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Importation du dataframe après avoir effectuer les choix pour le filtrage des données


params = [choix_compet] + choix_saison
stat = f"SELECT * FROM {table_met} WHERE Compet = ? and Saison IN ({', '.join('?' * len(choix_saison))})"
res, desc = execute_SQL(cursor, stat, params)

df_metrique = pd.DataFrame(res)
df_metrique.columns = [i[0] for i in desc]
df_metrique = df_metrique.drop("Compet", axis = 1).set_index(["Saison", "team_name"])


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Choix de la taille des groupes sur lesquels aggréger les données


df_nb_team = df_metrique.reset_index()[["Saison", "team_name"]].drop_duplicates().groupby("Saison").apply(len)

max_nb_team = min(df_nb_team)

columns = st.columns(2, gap = "large", vertical_alignment = "center")

with columns[0] :
    load_session_state("nb_top")
    nb_top = st.slider("Nombre d'équipe dans le Top :", min_value = 1, max_value = max_nb_team, **key_widg("nb_top"))

with columns[1] :
    if nb_top == max_nb_team :
        push_session_state("nb_bottom", max_nb_team - nb_top)

    else :
        push_session_state("nb_bottom", min(max_nb_team - nb_top, get_session_state("nb_bottom")))
        load_session_state("nb_bottom")
        st.slider(f"Nombre d'équipe dans le Bottom", min_value = 0, max_value = max_nb_team - nb_top, **key_widg("nb_bottom"))

    nb_bottom = get_session_state("nb_bottom")

nb_middle = max_nb_team - nb_top - nb_bottom


# Si on sélectionne plusieurs saisons, avec par exemple une à 18 équipes et les autres à 20 :
# On aura max_nb_team = 18. Si on choisit 18, 17, 16... équipes pour le Top, cela correspondra aux 20, 19, 18 premières équipes
# Pour les saisons à 20 équipes.
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Filtrage de la catégorie de métrique


if choix_provider == "Skill Corner" :

    st.divider()
    columns = st.columns([2, 1, 1], vertical_alignment = "center", gap = "medium")

    with columns[0] :
        load_session_state("cat_met")
        cat_met = st.radio("Catégorie de métrique", dico_met.keys(), horizontal = True, **key_widg("cat_met"))


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Filtrage de la moyenne de la catégorie de métrique et choix de la condition de victoire sur les matchs


    with columns[1] :
        load_session_state(f"moy_cat_{cat_met}")
        moy_cat = st.radio("Moyenne de la métrique", dico_met[cat_met][1].keys(), horizontal = True, **key_widg(f"moy_cat_{cat_met}"))
        moy_cat = dico_met[cat_met][1][moy_cat]

    with columns[2] :
        load_session_state("win_match")
        if st.checkbox("Métriques pour les équipes qui gagnent les matchs", **key_widg("win_match")) :
            df_metrique = df_metrique[df_metrique.result == "win"]
    
    df_metrique.drop(["Journée", "result"], axis = 1, inplace = True)
    
    col_keep = [(moy_cat in i) or ("ratio" in i) for i in df_metrique.columns]
    df_metrique = df_metrique[df_metrique.columns[col_keep]]


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Filtrage des types de course ou de pression dans le cas ou on a pas choisi les données Physical


    if cat_met != "Physique" :
        col_keep = [False]*df_metrique.shape[1]

        liste_type_cat = list(dico_met[cat_met][3].keys())

        init_session_state(f"type_cat_{cat_met}", liste_type_cat)
        load_session_state(f"type_cat_{cat_met}")
        choix_type_cat = st.multiselect(dico_met[cat_met][2], liste_type_cat, **key_widg(f"type_cat_{cat_met}"))
        
        for type_cat in choix_type_cat :
            type_cat = dico_met[cat_met][3][type_cat]

            col_keep = np.logical_or(col_keep, [(type_cat in i) or ("ratio" in i and type_cat in i) for i in df_metrique.columns])

        df_metrique = df_metrique[df_metrique.columns[col_keep]]


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Filtrage des métriques dans le cas ou on a choisi les données de Running


        if cat_met == "Course sans ballon avec la possession" :
            col_keep = [True]*df_metrique.shape[1]

            columns = st.columns([2, 1, 1], vertical_alignment = "center", gap = "large")

            with columns[0] :
                init_session_state("cat_run", liste_cat_run)
                load_session_state("cat_run")
                choix_cat_run = st.multiselect("Catégorie du run", options = liste_cat_run, **key_widg("cat_run"))
                
                if "All" not in choix_cat_run :
                    col_keep = [False]*df_metrique.shape[1]

                    for cat_run in dico_cat_run.values() :
                        col_keep = np.logical_or(col_keep, [cat_run in i for i in df_metrique.columns])

                for cat_run in dico_cat_run.keys() :
                    if cat_run not in choix_cat_run :
                        col_keep = np.logical_and(col_keep, [dico_cat_run[cat_run] not in i for i in df_metrique.columns])

            with columns[1] :
                load_session_state("threat_run")
                if not(st.checkbox('Métrique "threat"', **key_widg("threat_run"))) :
                    col_keep = np.logical_and(col_keep, ["threat" not in i for i in df_metrique.columns])

            with columns[2] :
                init_session_state("type_passe_run", liste_type_passe_run)
                load_session_state("type_passe_run")
                type_passe_run = st.multiselect("Type de passe liée au run", liste_type_passe_run, **key_widg("type_passe_run"))
                
                if "Targeted" not in type_passe_run :
                    col_keep = np.logical_and(col_keep, ["targeted" not in i for i in df_metrique.columns])

                if "Received" not in type_passe_run :
                    col_keep = np.logical_and(col_keep, ["received" not in i for i in df_metrique.columns])


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Filtrage des métriques dans le cas ou on a choisi les données de Pressure


        elif cat_met == "Action sous pression" :
            col_keep = [False]*df_metrique.shape[1]

            columns = st.columns(3, vertical_alignment = "center", gap = "large")

            with columns[0] :                
                init_session_state("cat_pressure", liste_cat_pressure)
                load_session_state("cat_pressure")
                choix_cat_pressure = st.multiselect("Catégorie de métrique liée au pressing", liste_cat_pressure,
                                                    **key_widg("cat_pressure"))
                
                for cat_pressure in choix_cat_pressure :
                    col_keep = np.logical_or(col_keep, [dico_cat_pressure[cat_pressure] in i for i in df_metrique.columns])

            if "Passes" in choix_cat_pressure :
                with columns[1] :
                    dico_cat_passe_pressure = {"All" : [(("pass_completion" not in i) or ("dangerous" in i) or ("difficult" in i))
                        and ("count_completed_pass" not in i) and ("count_pass_attempts" not in i) for i in df_metrique.columns],
                        "Dangerous" : ["dangerous" not in i for i in df_metrique.columns], 
                        "Difficult" : ["difficult" not in i for i in df_metrique.columns]}
                    
                    init_session_state("cat_passe_pressure", liste_cat_passe_pressure)
                    load_session_state("cat_passe_pressure")
                    choix_type_passe_pressure = st.multiselect("Type de passe", liste_cat_passe_pressure, **key_widg("cat_passe_pressure"))
                    
                    for cat_passe_pressure in liste_cat_passe_pressure :
                        if cat_passe_pressure not in choix_type_passe_pressure :
                            col_keep = np.logical_and(col_keep, dico_cat_passe_pressure[cat_passe_pressure])

                    load_session_state("result_passe_pressure")
                    result_passe_pressure = st.multiselect("Résultat de la passe sous pression", ["Attempts", "Completed"],
                                                           **key_widg("result_passe_pressure"))
                    
                    if "Attempts" not in result_passe_pressure :
                        col_keep = np.logical_and(col_keep, ["attempts" not in i for i in df_metrique.columns])

                    if "Completed" not in result_passe_pressure :
                        col_keep = np.logical_and(col_keep, ["completed" not in i for i in df_metrique.columns])

            with columns[-1] :
                if "Passes" in choix_cat_pressure :
                    load_session_state("ratio_passe_pressure")
                    if not(st.checkbox("Ratio lié aux passes", **key_widg("ratio_passe_pressure"))) :
                        col_keep = np.logical_and(col_keep, [("pass" not in i) or ("ratio" not in i) for i in df_metrique.columns])                   
                
                if "Conservation du ballon" in choix_cat_pressure :
                    load_session_state("ratio_conserv_pressure")
                    if not(st.checkbox("Ratio lié à la conservation du ballon", **key_widg("ratio_conserv_pressure"))) :
                        col_keep = np.logical_and(col_keep, ["ball_retention_ratio" not in i for i in df_metrique.columns])


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Filtrage des métriques dans le cas ou on a choisi les données de Passes


        else :
            col_keep = [True]*df_metrique.shape[1]

            columns = st.columns([2, 1, 1, 2], vertical_alignment = "center", gap = "large")

            with columns[0] :
                init_session_state("cat_run_passe", liste_cat_run)
                load_session_state("cat_run_passe")
                choix_cat_run_passe = st.multiselect("Catégorie du run", options = liste_cat_run, **key_widg("cat_run_passe"))
                
                if "All" not in choix_cat_run_passe :
                    col_keep = [False]*df_metrique.shape[1]

                    for cat_run_passe in dico_cat_run.values() :
                        col_keep = np.logical_or(col_keep, [cat_run_passe in i for i in df_metrique.columns])
                
                for cat_run_passe in dico_cat_run.keys() :
                    if cat_run_passe not in choix_cat_run_passe :
                        col_keep = np.logical_and(col_keep, [dico_cat_run[cat_run_passe] not in i for i in df_metrique.columns])

            with columns[3] :
                init_session_state("type_passe", liste_type_passe)
                load_session_state("type_passe")
                choix_type_passe = st.multiselect("Type de passe", dico_cat_passe.keys(), **key_widg("type_passe"))
                
                col_keep_passe = [False]*df_metrique.shape[1]

                for type_passe in choix_type_passe :
                    col_keep_passe = np.logical_or(col_keep_passe, [dico_cat_passe[type_passe] in i for i in df_metrique.columns])

                col_keep = np.logical_and(col_keep, col_keep_passe)

                if "All" in choix_cat_run_passe :
                    col_keep = np.logical_or(col_keep, ["teammate" in i for i in df_metrique.columns])

            with columns[1] :
                load_session_state("threat_passe")
                if not(st.checkbox('Métrique "threat"', **key_widg("threat_passe"))) :
                    col_keep = np.logical_and(col_keep, ["threat" not in i for i in df_metrique.columns])

            with columns[2] :
                load_session_state("ratio_passe")
                if st.checkbox("Ratio", **key_widg("ratio_passe")) :
                    col_keep = np.logical_or(col_keep, ["ratio" in i for i in df_metrique.columns])
    

        df_metrique = df_metrique[df_metrique.columns[col_keep]]


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Aggrégation des métriques sur une saison pour chaque équipe


    df_metrique = df_metrique.groupby(level = [0, 1], sort = False)

    nb_matchs_team = df_metrique.apply(len)

    df_metrique = df_metrique.sum()

    df_metrique = df_metrique.divide(nb_matchs_team, axis = 0)


if df_metrique.shape[1] == 0 :
    st.stop()

st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Filtre du dataframe selon les groupes choisit


for saison in choix_saison :
    liste_rank = dico_rank[saison]
    
    df_metrique.loc[idx[saison, liste_rank[:df_nb_team[saison] - nb_bottom - nb_middle]], "Groupe"] = "Top"
    df_metrique.loc[idx[saison, liste_rank[df_nb_team[saison] - nb_bottom - nb_middle:df_nb_team[saison] - nb_bottom]], "Groupe"] = "Middle"
    df_metrique.loc[idx[saison, liste_rank[df_nb_team[saison] - nb_bottom:]], "Groupe"] = "Bottom"

df_rank_team = df_metrique.pop("Groupe")

df_top = df_metrique[df_rank_team == "Top"]

df_middle = df_metrique[df_rank_team == "Middle"]

df_bottom = df_metrique[df_rank_team == "Bottom"]


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Création du dataframe final qui va contenir les informations sur les métriques


df_final = pd.DataFrame(index = df_metrique.columns)

df_final["Moyenne Top"] = df_top.mean(axis = 0)

df_final["Moyenne Middle"] = df_middle.mean(axis = 0)

df_final["Moyenne Bottom"] = df_bottom.mean(axis = 0)

df_final["Diff. Top avec Bottom en %"] = (100*(df_final["Moyenne Top"] - df_final["Moyenne Bottom"])/abs(df_final["Moyenne Bottom"])).round(2)
df_final["Diff. Top avec Middle en %"] = (100*(df_final["Moyenne Top"] - df_final["Moyenne Middle"])/abs(df_final["Moyenne Middle"])).round(2)
df_final["Diff. Middle avec Bottom en %"] = (100*(df_final["Moyenne Middle"] - df_final["Moyenne Bottom"])/abs(df_final["Moyenne Bottom"])).round(2)

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

if nb_bottom > 0 :
    df_final = df_final.reindex(abs(df_final).sort_values(by = "Diff. Top avec Bottom en %", ascending = False).index)

elif len(df_middle) > 0 :
    df_final = df_final.reindex(abs(df_final).sort_values(by = "Diff. Top avec Middle en %", ascending = False).index)

df_final.dropna(axis = 1, how = "all", inplace = True)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Choix du nombre de métrique à garder et des informations sur les métriques à afficher dans le tableau


nb_metrique = st.slider("Nombre de métriques gardées", min_value=0, max_value = len(df_final), value = len(df_final))

df_final = df_final.loc[df_final.index[:nb_metrique]]

col_df = st.multiselect("Données des métriques à afficher", df_final.columns, default = df_final.columns.tolist())

df_final = df_final[col_df]

if len(col_df) == 0 :
    st.stop()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Style et affichage du dataframe


st.divider()

st.markdown("<p style='text-align: center;'>Tableau des métriques discriminantes</p>", unsafe_allow_html=True)

df_final_style = df_final.style.apply(couleur_diff, axis = 0)

row_select_met = st.dataframe(df_final_style, on_select = "rerun", selection_mode = "multi-row").selection.rows


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Affichage des stats pour les métriques sélectionnées par équipe pour les saisons sélectionnées


if len(row_select_met) > 0 :
    st.divider()

    for saison in choix_saison :
        st.markdown(f"<p style='text-align: center;'>Tableau des métriques retenues, par équipes, en moyenne par match lors de la saison {saison} </p>", unsafe_allow_html=True)
        
        metrique_df_final = df_metrique.loc[saison, :][df_final.index[row_select_met]]

        st.dataframe(metrique_df_final)