# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Importation des librairies


import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from functools import partial
import sqlite3

from fonction import load_session_state, store_session_state, execute_SQL, init_session_state, replace_saison2, replace_saison1
from variable import dico_met, dico_rank_SK, dico_rank_SB, dico_cat_run, dico_cat_pressure, dico_cat_passe

# Index slicer pour la sélection de donnée sur les dataframes avec multi-index
idx = pd.IndexSlice


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Connection BDD


connect = sqlite3.connect("database.db")
cursor = connect.cursor()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Mise en page de la page


st.set_page_config(layout="wide")

st.title("Évolution des métriques au cours des saisons")

st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Connection BDD


connect = sqlite3.connect("database.db")
cursor = connect.cursor()


#----------------------------------------------- DÉFINITIONS DES FONCTIONS ------------------------------------------------------------------------------------



def couleur_bg_df(col, liste_saison, df) :
    if col.name == "Évolution en %" :
        color = []
        for met in col.index :
            count_evo = 0
            for i in range (len(liste_saison) - 1) :
                count_evo += (df.loc[met, liste_saison[i + 1]] >= df.loc[met, liste_saison[i]])
            if count_evo == (len(liste_saison) - 1) :
                color.append("background-color: rgba(0, 255, 0, 0.3)")
            elif count_evo == 0 :
                color.append("background-color: rgba(255, 0, 0, 0.3)")
            elif df.loc[met, liste_saison[-1]] >= df.loc[met, liste_saison[0]] :
                color.append("background-color: rgba(255, 255, 0, 0.3)")
            else :
                color.append("background-color: rgba(255, 130, 0, 0.5)")
        return(color)
    
    else :
        return ['']*len(df)

def couleur_text_df(row) :
    color = ['']
    for i in range (len(row) - 2) :
        if row.iloc[i] < row.iloc[i + 1] :
            color.append("color : rgba(0, 200, 0)")
        else :
            color.append("color : rgba(255, 0, 0)")
    color.append('')
    return color


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Choix du fournisseur de donnée, de la compétition et du nombre de saison à comparer


columns = st.columns([2, 2, 3], gap = "large")

with columns[0] :
    load_session_state("provider")
    choix_provider = st.radio("Fournisseur data", options = ["Skill Corner", "Stats Bomb"], horizontal = True, key = "widg_provider",
                          on_change = store_session_state, args = ["provider"])
    
if choix_provider == "Skill Corner" :
    table_met = dico_met[st.session_state.cat_met][0]
    dico_rank = dico_rank_SK
    
else :
    table_met = "Métriques_SB"
    dico_rank = dico_rank_SB

params = []
stat = f"SELECT DISTINCT Compet FROM {table_met}"
liste_compet, desc = execute_SQL(cursor, stat, params)
liste_compet = [i[0] for i in liste_compet]
    
with columns[1] :
    load_session_state("compet_met")
    choix_compet = st.selectbox("Choisir compétition", options = liste_compet, key = "widg_compet_met", on_change = store_session_state,
                                args = ["compet_met"])

params = [choix_compet]
stat = f"SELECT DISTINCT Saison FROM {table_met} WHERE Compet = ?"
liste_saison, desc = execute_SQL(cursor, stat, params)
liste_saison = [i[0] for i in liste_saison]

with columns[2] :
    init_session_state("nb_saison_comp", len(liste_saison))
    load_session_state("nb_saison_comp")
    nb_saison_comp = st.number_input("Nombre de saison à comparer", min_value = 2, max_value = len(liste_saison),
                                     key = "widg_nb_saison_comp", on_change = store_session_state, args = ["nb_saison_comp"])
    
    liste_saison = liste_saison[:nb_saison_comp]

st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Importation du dataframe après avoir effectuer les choix pour le filtrage des données


params = [choix_compet] + liste_saison
stat = f"SELECT * FROM {table_met} WHERE Compet = ? and Saison IN ({', '.join('?' * len(liste_saison))})"
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
    load_session_state("nb_top_met")
    nb_top = st.slider("Nombre d'équipe dans le Top :", min_value = 1, max_value = max_nb_team, key = "widg_nb_top_met",
                                  on_change = store_session_state, args = ["nb_top_met"])

with columns[1] :
    if nb_top == max_nb_team :
        st.session_state["nb_bottom_met"] = max_nb_team - nb_top

    else :
        st.session_state["nb_bottom_met"] = min(max_nb_team - nb_top, st.session_state["nb_bottom_met"])
        load_session_state("nb_bottom_met")
        st.slider(f"Nombre d'équipe dans le Bottom", min_value = 0, max_value = max_nb_team - nb_top, key = "widg_nb_bottom_met",
                                  on_change = store_session_state, args = ["nb_bottom_met"])

    nb_bottom = st.session_state["nb_bottom_met"]

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
        cat_met = st.radio("Catégorie de métrique", dico_met.keys(), horizontal = True, key = 'widg_cat_met',
                            on_change = store_session_state, args = ["cat_met"])


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Filtrage de la moyenne de la catégorie de métrique et choix de la condition de victoire sur les matchs


    with columns[1] :
        load_session_state(f"moy_cat_{cat_met}")
        moy_cat = st.radio("Moyenne de la métrique", dico_met[cat_met][1].keys(), horizontal = True, key = f'widg_moy_cat_{cat_met}',
                            on_change = store_session_state, args = [f"moy_cat_{cat_met}"])
        moy_cat = dico_met[cat_met][1][moy_cat]

    with columns[2] :
        load_session_state("win_match")
        if st.checkbox("Métriques pour les équipes qui gagnent les matchs", key = 'widg_win_match', on_change = store_session_state,
                       args = ["win_match"]) :
            df_metrique = df_metrique[df_metrique.result == "win"]
    
    df_metrique.drop(["Journée", "result"], axis = 1, inplace = True)
    
    col_keep = [(moy_cat in i) or ("ratio" in i) for i in df_metrique.columns]
    df_metrique = df_metrique[df_metrique.columns[col_keep]]


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Filtrage des types de course ou de pression dans le cas ou on a pas choisi les données Physical


    if cat_met != "Physiques" :
        col_keep = [False]*df_metrique.shape[1]

        liste_type_cat = list(dico_met[cat_met][3].keys())

        init_session_state(f"type_cat_{cat_met}", liste_type_cat)
        load_session_state(f"type_cat_{cat_met}")
        choix_type_cat = st.multiselect(dico_met[cat_met][2], liste_type_cat, key = f'widg_type_cat_{cat_met}',
                                        on_change = store_session_state,
                                        args = [f"type_cat_{cat_met}"])
        
        for type_cat in choix_type_cat :
            type_cat = dico_met[cat_met][3][type_cat]

            col_keep = np.logical_or(col_keep, [(type_cat in i) or ("ratio" in i and type_cat in i) for i in df_metrique.columns])

        df_metrique = df_metrique[df_metrique.columns[col_keep]]


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Filtrage des métriques dans le cas ou on a choisi les données de Running


        if cat_met == "Courses sans ballon avec la possession" :
            col_keep = [True]*df_metrique.shape[1]

            columns = st.columns([2, 1, 1], vertical_alignment = "center", gap = "large")

            with columns[0] :
                liste_cat_run = ["All"] + list(dico_cat_run.keys())

                init_session_state("cat_run", liste_cat_run)
                load_session_state("cat_run")
                choix_cat_run = st.multiselect("Catégorie du run", options = liste_cat_run, key = 'widg_cat_run',
                            on_change = store_session_state, args = ["cat_run"])
                
                if "All" not in choix_cat_run :
                    col_keep = [False]*df_metrique.shape[1]

                    for cat_run in dico_cat_run.values() :
                        col_keep = np.logical_or(col_keep, [cat_run in i for i in df_metrique.columns])

                for cat_run in dico_cat_run.keys() :
                    if cat_run not in choix_cat_run :
                        col_keep = np.logical_and(col_keep, [dico_cat_run[cat_run] not in i for i in df_metrique.columns])

            with columns[1] :
                load_session_state("threat_run")
                if not(st.checkbox('Métrique "threat"', key = 'widg_threat_run', on_change = store_session_state, args = ["threat_run"])) :
                    col_keep = np.logical_and(col_keep, ["threat" not in i for i in df_metrique.columns])

            with columns[2] :
                liste_type_passe_run = ["Targeted", "Received"]

                init_session_state("type_passe_run", liste_type_passe_run)
                load_session_state("type_passe_run")
                type_passe_run = st.multiselect("Type de passe liée au run", liste_type_passe_run, key = 'widg_type_passe_run',
                                                on_change = store_session_state, args = ["type_passe_run"])
                
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
                liste_cat_pressure = list(dico_cat_pressure.keys())
                
                init_session_state("cat_pressure", liste_cat_pressure)
                load_session_state("cat_pressure")
                choix_cat_pressure = st.multiselect("Catégorie de métrique liée au pressing", liste_cat_pressure,
                                    key = 'widg_cat_pressure', on_change = store_session_state, args = ["cat_pressure"])
                
                for cat_pressure in choix_cat_pressure :
                    col_keep = np.logical_or(col_keep, [dico_cat_pressure[cat_pressure] in i for i in df_metrique.columns])

            if "Passes" in choix_cat_pressure :
                with columns[1] :
                    dico_cat_passe_pressure = {"All" : [(("pass_completion" not in i) or ("dangerous" in i) or ("difficult" in i))
                        and ("count_completed_pass" not in i) and ("count_pass_attempts" not in i) for i in df_metrique.columns],
                        "Dangerous" : ["dangerous" not in i for i in df_metrique.columns], 
                        "Difficult" : ["difficult" not in i for i in df_metrique.columns]}
                    
                    liste_cat_passe_pressure = list(dico_cat_passe_pressure.keys())

                    init_session_state("cat_passe_pressure", liste_cat_passe_pressure)
                    load_session_state("cat_passe_pressure")
                    choix_type_passe_pressure = st.multiselect("Type de passe", liste_cat_passe_pressure,
                        key = 'widg_cat_passe_pressure', on_change = store_session_state, args = ["cat_passe_pressure"])
                    
                    for cat_passe_pressure in liste_cat_passe_pressure :
                        if cat_passe_pressure not in choix_type_passe_pressure :
                            col_keep = np.logical_and(col_keep, dico_cat_passe_pressure[cat_passe_pressure])

                    load_session_state("result_passe_pressure")
                    result_passe_pressure = st.multiselect("Résultat de la passe sous pression", ["Attempts", "Completed"],
                        key = 'widg_result_passe_pressure', on_change = store_session_state, args = ["result_passe_pressure"])
                    
                    if "Attempts" not in result_passe_pressure :
                        col_keep = np.logical_and(col_keep, ["attempts" not in i for i in df_metrique.columns])

                    if "Completed" not in result_passe_pressure :
                        col_keep = np.logical_and(col_keep, ["completed" not in i for i in df_metrique.columns])

            with columns[-1] :
                if "Passes" in choix_cat_pressure :
                    load_session_state("ratio_passe_pressure")
                    if not(st.checkbox("Ratio lié aux passes", key = 'widg_ratio_passe_pressure', on_change = store_session_state,
                                       args = ["ratio_passe_pressure"])) :
                        col_keep = np.logical_and(col_keep, [("pass" not in i) or ("ratio" not in i) for i in df_metrique.columns])                   
                
                if "Conservation du ballon" in choix_cat_pressure :
                    load_session_state("ratio_conserv_pressure")
                    if not(st.checkbox("Ratio lié à la conservation du ballon", key = 'widg_ratio_conserv_pressure',
                                       on_change = store_session_state, args = ["ratio_conserv_pressure"])) :
                        col_keep = np.logical_and(col_keep, ["ball_retention_ratio" not in i for i in df_metrique.columns])


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Filtrage des métriques dans le cas ou on a choisi les données de Passes


        else :
            col_keep = [True]*df_metrique.shape[1]

            columns = st.columns([2, 1, 1, 2], vertical_alignment = "center", gap = "large")

            with columns[0] :
                liste_cat_run = ["All"] + list(dico_cat_run.keys())

                init_session_state("cat_run_passe", liste_cat_run)
                load_session_state("cat_run_passe")
                choix_cat_run_passe = st.multiselect("Catégorie du run", options = liste_cat_run, key = 'widg_cat_run_passe',
                                       on_change = store_session_state, args = ["cat_run_passe"])
                
                if "All" not in choix_cat_run_passe :
                    col_keep = [False]*df_metrique.shape[1]

                    for cat_run_passe in dico_cat_run.values() :
                        col_keep = np.logical_or(col_keep, [cat_run_passe in i for i in df_metrique.columns])
                
                for cat_run_passe in dico_cat_run.keys() :
                    if cat_run_passe not in choix_cat_run_passe :
                        col_keep = np.logical_and(col_keep, [dico_cat_run[cat_run_passe] not in i for i in df_metrique.columns])

            with columns[3] :

                liste_type_passe = list(dico_cat_passe.keys())

                init_session_state("type_passe", liste_type_passe)
                load_session_state("type_passe")
                choix_type_passe = st.multiselect("Type de passe", dico_cat_passe.keys(), key = 'widg_type_passe',
                                       on_change = store_session_state, args = ["type_passe"])
                
                col_keep_passe = [False]*df_metrique.shape[1]

                for type_passe in choix_type_passe :
                    col_keep_passe = np.logical_or(col_keep_passe, [dico_cat_passe[type_passe] in i for i in df_metrique.columns])

                col_keep = np.logical_and(col_keep, col_keep_passe)

                if "All" in choix_cat_run_passe :
                    col_keep = np.logical_or(col_keep, ["teammate" in i for i in df_metrique.columns])

            with columns[1] :
                load_session_state("threat_passe")
                if not(st.checkbox('Métrique "threat"', key = 'widg_threat_passe', on_change = store_session_state,
                                   args = ["threat_passe"])) :
                    col_keep = np.logical_and(col_keep, ["threat" not in i for i in df_metrique.columns])

            with columns[2] :
                load_session_state("ratio_passe")
                if st.checkbox("Ratio", key = 'widg_ratio_passe', on_change = store_session_state,
                                   args = ["ratio_passe"]) :
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


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Création du dataframe de l'évolution des métriques à afficher


multi_index_liste = [df_metrique.columns, ["Top", "Middle", "Bottom"]]
multi_index = pd.MultiIndex.from_product(multi_index_liste, names=["Métrique", "Groupe"])

df_final = pd.DataFrame(index = multi_index)

liste_saison.reverse()

for saison in liste_saison :
    liste_rank = dico_rank[saison]

    df_final.loc[idx[:, "Top"], saison] = df_metrique.loc[idx[saison, liste_rank[:df_nb_team[saison] - nb_bottom - nb_middle]], :].mean(axis = 0).values
    df_final.loc[idx[:, "Middle"], saison] = df_metrique.loc[idx[saison, liste_rank[df_nb_team[saison] - nb_bottom - nb_middle:df_nb_team[saison] - nb_bottom]], :].mean(axis = 0).values
    df_final.loc[idx[:, "Bottom"], saison] = df_metrique.loc[idx[saison, liste_rank[df_nb_team[saison] - nb_bottom:]], :].mean(axis = 0).values

df_final.columns = replace_saison1(liste_saison)

df_final = df_final.dropna(axis = 0, how = "all").replace({0 : np.nan})

first_year = df_final.columns[0]
last_year = df_final.columns[-1]

df_final["Évolution en %"] = 100*(df_final[last_year] - df_final[first_year])/abs(df_final[first_year])
df_final.replace({np.nan : 0}, inplace = True)

df_final = df_final.reindex(abs(df_final.loc[:, "Top", :]).sort_values(by = ["Évolution en %"], ascending = False).index, level = 0)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Stylisation et affichage du dataframe final


st.divider()

couleur_bg_df_partial = partial(couleur_bg_df, liste_saison = df_final.columns[:-1], df = df_final)

df_style = df_final.style.apply(couleur_bg_df_partial, axis = 0)
df_style = df_style.apply(couleur_text_df, axis = 1)

st.markdown(f"<p style='text-align: center;'>Tableau de l'évolution de chaque métrique entre la saison {first_year} et {last_year}</p>",
            unsafe_allow_html=True)

row_select_met = st.dataframe(df_style, width = 10000, on_select = "rerun", selection_mode = "multi-row").selection.rows


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Affichage du code couleur


first_year = replace_saison1(first_year)
last_year = replace_saison1(last_year)
st.markdown(f"<p style='text-align: center;'>Code couleur de l'évolution des métriques entre la saison {first_year} et {last_year} :</p>",
            unsafe_allow_html=True)

columns = st.columns(4, gap = "small")

font_size = "20px"

with columns[0] :
    st.markdown(f'<span style="background-color: rgba(0, 255, 0, 0.3); font-size: {font_size};">Augmentation constante</span>',
                unsafe_allow_html=True)
    
with columns[1] :
    st.markdown(f'<span style="background-color: rgba(255, 255, 0, 0.3); font-size: {font_size};">Tendance haussière</span>',
                unsafe_allow_html=True)

with columns[2] :
    st.markdown(f'<span style="background-color: rgba(255, 130, 0, 0.5); font-size: {font_size};">Tendance baissière</span>',
                unsafe_allow_html=True)
    
with columns[3] :
    st.markdown(f'<span style="background-color: rgba(255, 0, 0, 0.3); font-size: {font_size};">Diminution constante</span>',
                unsafe_allow_html=True)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Affichage du graphique de l'évolution des métriques sélectionnées sur les saisons sélectionnées


if len(row_select_met) == 0 :
    st.stop()

st.divider()

graphe_evo = df_style.data.iloc[row_select_met].drop("Évolution en %", axis = 1)

new_index = []
for i in df_style.index[row_select_met] :
    new_index.append(i[1] + " - " + i[0])

graphe_evo.index = new_index

fig = plt.figure()

plt.plot(graphe_evo.T, linewidth = 0.7)

plt.title(f"Graphique de l'évolution des métriques sélectionnées entre la saison {first_year} et {last_year}", fontweight = "heavy",
          y = 1.05, fontsize = 9)

plt.grid()

plt.legend(graphe_evo.index, loc = "lower center", bbox_to_anchor=(0.5, -0.35 - 0.08*(int((len(graphe_evo.index) + 1)/2) - 1)),
        fontsize = "small", ncol = 2)

plt.xlabel("Saison", fontsize = "small", fontstyle = "italic", labelpad = 10)
plt.ylabel("Métrique", fontsize = "small", fontstyle = "italic", labelpad = 10)
plt.tick_params(labelsize = 8)

ax = plt.gca()
ax.spines[:].set_visible(False)

st.pyplot(fig)