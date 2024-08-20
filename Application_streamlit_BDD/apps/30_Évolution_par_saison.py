import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from functools import partial
import sqlite3

from config_py.fonction import func_change, execute_SQL, replace_saison2
from config_py.variable import dico_type, dico_rank_SK, dico_cat_run, dico_cat_met_pressure, dico_type_passe, dico_rank_SB

st.set_page_config(layout="wide")

st.title("Évolution des métriques au cours des saisons")
st.divider()

idx = pd.IndexSlice

pd.set_option('future.no_silent_downcasting', True)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Connection BDD


connect = sqlite3.connect("database.db")
cursor = connect.cursor()


#----------------------------------------------- DÉFINITIONS DES FONCTIONS ------------------------------------------------------------------------------------


st.markdown(
    """
    <style>
    .highlight1 {
        background-color: rgba(0, 255, 0, 0.5); /* Couleur de l'arrière-plan */
        padding: 10px;
        border-radius: 5px;
        font-size: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    .highlight2 {
        background-color: rgba(255, 255, 0, 0.7); /* Couleur de l'arrière-plan */
        padding: 10px;
        border-radius: 5px;
        font-size: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    .highlight3 {
        background-color: rgba(255, 130, 0, 0.7); /* Couleur de l'arrière-plan */
        padding: 10px;
        border-radius: 5px;
        font-size: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    .highlight4 {
        background-color: rgba(255, 0, 0, 0.5); /* Couleur de l'arrière-plan */
        padding: 10px;
        border-radius: 5px;
        font-size: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


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
# Choix de la saison et du fournisseur de donnée


columns = st.columns([2, 2, 3], gap = "large")

with columns[0] :
    # Choix du fournisseur de données
    func_change("select_data", "choix_data")
    choix_data = st.radio("Fournisseur data", options = ["Skill Corner", "Stats Bomb"], horizontal = True,
                          key = "select_data", on_change = func_change, args = ("choix_data", "select_data"))
    
if choix_data == "Skill Corner" :

    table_met = dico_type[st.session_state.cat_met][0]
    dico_rank = dico_rank_SK
    
else :
    table_met = "Métriques_SB"
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
    nb_saison_comp = st.number_input("Nombre de saison à comparer", min_value = 2, max_value = len(liste_saison), value = len(liste_saison))
    liste_saison = liste_saison[:nb_saison_comp]

st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Création du dataframe en choisissant le type de métrique qu'on souhaite étudier


params = [choix_compet] + liste_saison
stat = f"SELECT * FROM {table_met} WHERE Compet = ? and Saison IN ({', '.join('?' * len(liste_saison))})"
res = execute_SQL(cursor, stat, params)

df_metrique = pd.DataFrame(res.fetchall())
df_metrique.columns = [i[0] for i in res.description]
df_metrique = df_metrique.drop("Compet", axis = 1).set_index(["Saison", "team_name"])


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Choix de la taille des groupes sur lesquels aggréger les données


df_nb_team = df_metrique.reset_index()[["Saison", "team_name"]].drop_duplicates().groupby("Saison").apply(len)

max_team = min(df_nb_team)

columns = st.columns(2, gap = "large", vertical_alignment = "center")

with columns[0] :
    # Choix du nombre d'équipe dans le Top. Possible de choisir toutes les équipes du championnat
    nb_top = st.slider("Nombre d'équipe dans le Top :", min_value = 1, max_value = max_team, value = 5)

with columns[1] :
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
# Sélection des métriques via l'interface Streamlit


# Filtrage des métriques uniquement dans le cas Skill Corner
if choix_data == "Skill Corner" :

    st.divider()
    columns = st.columns([2, 1, 1], vertical_alignment = "center", gap = "medium")

    with columns[0] :
        # Choix de la catégorie de métrique
        func_change("select_cat_met", "cat_met")
        cat_met = st.radio("Catégorie de métrique", dico_type.keys(), horizontal = True, key = 'select_cat_met',
                            on_change = func_change, args = ("cat_met", "select_cat_met"))

    with columns[1] :
        # Choix de la moyenne pour la catégorie de métrique choisie
        cat_moy = st.radio("Moyenne de la métrique", dico_type[cat_met][1].keys(), horizontal = True)

    with columns[2] :
        if st.checkbox("Métriques pour les équipes qui gagnent les matchs") :
            df_metrique = df_metrique[df_metrique.result == "win"]
    
    df_metrique.drop(["Journée", "result"], axis = 1, inplace = True)
    
    # On garde les métriques avec la moyenne choisie
    cat_type = dico_type[cat_met][1][cat_moy]

    # col_keep est une liste de taille = nombre total de métrique et qui contient des True/False pour savoir si on garde ou non
    # la métrique correspondante
    # Les métriques ratios ne sont pas aggrégés par durée ou nombre d'évènement
    col_keep = [(cat_type in i) or ("ratio" in i) for i in df_metrique.columns]
    df_metrique = df_metrique[df_metrique.columns[col_keep]]

    # Les catégories autres que Physiques contiennent des type de métrique : type de course et type de pression
    if cat_met != "Physiques" :
        # Sélection du type de métrique
        col_keep = [False]*df_metrique.shape[1]
        liste_cat_type1 = st.multiselect(dico_type[cat_met][2], dico_type[cat_met][3].keys(), default = dico_type[cat_met][3].keys())
        for cat_type in liste_cat_type1 :
            cat_type = dico_type[cat_met][3][cat_type]
            col_keep = np.logical_or(col_keep, [(cat_type in i) or ("ratio" in i and cat_type in i) for i in df_metrique.columns])
        df_metrique = df_metrique[df_metrique.columns[col_keep]]

        # On filtre ensuite les métriques au cas par cas pour chaque catégorie de métrique
        # col_keep va être modifier au fur et à mesure des filtres choisit
        if cat_met == "Courses sans ballon avec la possession" :
            col_keep = [True]*df_metrique.shape[1]
            columns = st.columns([2, 1, 1], vertical_alignment = "center", gap = "large")
            with columns[0] :
                liste_cat_run = ["All"] + list(dico_cat_run.keys())
                cat_run_choice = st.multiselect("Catégorie du run", options = liste_cat_run, default = liste_cat_run)
                if "All" not in cat_run_choice :
                    col_keep = [False]*df_metrique.shape[1]
                    for cat_run in dico_cat_run.values() :
                        col_keep = np.logical_or(col_keep, [cat_run in i for i in df_metrique.columns])
                for cat_run in dico_cat_run.keys() :
                    if cat_run not in cat_run_choice :
                        col_keep = np.logical_and(col_keep, [dico_cat_run[cat_run] not in i for i in df_metrique.columns])

            with columns[1] :
                if not(st.checkbox('Métrique "threat"', value = True)) :
                    col_keep = np.logical_and(col_keep, ["threat" not in i for i in df_metrique.columns])

            with columns[2] :
                liste_type_passe_run = ["Targeted", "Received"]
                type_passe_run = st.multiselect("Type de passe liée au run", liste_type_passe_run, default = liste_type_passe_run)
                if "Targeted" not in type_passe_run :
                    col_keep = np.logical_and(col_keep, ["targeted" not in i for i in df_metrique.columns])
                if "Received" not in type_passe_run :
                    col_keep = np.logical_and(col_keep, ["received" not in i for i in df_metrique.columns])


        elif cat_met == "Action sous pression" :
            col_keep = [False]*df_metrique.shape[1]
            columns = st.columns(3, vertical_alignment = "center", gap = "large")
            with columns[0] :
                cat_met_pressure = st.multiselect("Catégorie de métrique liée au pressing", dico_cat_met_pressure.keys(),
                                                default = dico_cat_met_pressure.keys())
                for cat_met in cat_met_pressure :
                    col_keep = np.logical_or(col_keep, [dico_cat_met_pressure[cat_met] in i for i in df_metrique.columns])

            if "Passes" in cat_met_pressure :
                with columns[1] :
                    dico_type_passe_pressure = {"All" : [(("pass_completion" not in i) or ("dangerous" in i) or ("difficult" in i)) and 
                        ("count_completed_pass" not in i) and ("count_pass_attempts" not in i) for i in df_metrique.columns],
                        "Dangerous" : ["dangerous" not in i for i in df_metrique.columns], 
                        "Difficult" : ["difficult" not in i for i in df_metrique.columns]}
                    type_passe_pressure = st.multiselect("Type de passe", dico_type_passe_pressure.keys(), default = dico_type_passe_pressure.keys())
                    for type_passe in dico_type_passe_pressure.keys() :
                        if type_passe not in type_passe_pressure :
                            col_keep = np.logical_and(col_keep, dico_type_passe_pressure[type_passe])
                    result_pass_pressure = st.multiselect("Résultat de la passe sous pression", ["Attempts", "Completed"],
                                                        default = ["Attempts", "Completed"])
                    if "Attempts" not in result_pass_pressure :
                        col_keep = np.logical_and(col_keep, ["attempts" not in i for i in df_metrique.columns])
                    if "Completed" not in result_pass_pressure :
                        col_keep = np.logical_and(col_keep, ["completed" not in i for i in df_metrique.columns])

            with columns[-1] :
                if "Passes" in cat_met_pressure :
                    if not(st.checkbox("Ratio lié aux passes", value = True)) :
                        col_keep = np.logical_and(col_keep, [("pass" not in i) or ("ratio" not in i) for i in df_metrique.columns])                   
                if "Conservation du ballon" in cat_met_pressure :
                    if not(st.checkbox("Ratio lié à la conservation du ballon", value = True)) :
                        col_keep = np.logical_and(col_keep, ["ball_retention_ratio" not in i for i in df_metrique.columns])


        else :
            col_keep = [True]*df_metrique.shape[1]
            columns = st.columns([2, 1, 1, 2], vertical_alignment = "center", gap = "large")

            with columns[0] :
                liste_cat_run = ["All"] + list(dico_cat_run.keys())
                cat_run_choice = st.multiselect("Catégorie du run", options = liste_cat_run, default = liste_cat_run)
                if "All" not in cat_run_choice :
                    col_keep = [False]*df_metrique.shape[1]
                    for cat_run in dico_cat_run.values() :
                        col_keep = np.logical_or(col_keep, [cat_run in i for i in df_metrique.columns])
                for cat_run in dico_cat_run.keys() :
                    if cat_run not in cat_run_choice :
                        col_keep = np.logical_and(col_keep, [dico_cat_run[cat_run] not in i for i in df_metrique.columns])

            with columns[3] :
                choix_type_passe = st.multiselect("Type de passe", dico_type_passe.keys(), default = dico_type_passe.keys())
                col_keep_passe = [False]*df_metrique.shape[1]
                for type_passe in choix_type_passe :
                    col_keep_passe = np.logical_or(col_keep_passe, [dico_type_passe[type_passe] in i for i in df_metrique.columns])
                col_keep = np.logical_and(col_keep, col_keep_passe)
                if "All" in cat_run_choice :
                    col_keep = np.logical_or(col_keep, ["teammate" in i for i in df_metrique.columns])

            with columns[1] :
                if not(st.checkbox('Métrique "threat"', value = True)) :
                    col_keep = np.logical_and(col_keep, ["threat" not in i for i in df_metrique.columns])

            with columns[2] :
                if st.checkbox("Ratio", True) :
                    col_keep = np.logical_or(col_keep, ["ratio" in i for i in df_metrique.columns])
    
        df_metrique = df_metrique[df_metrique.columns[col_keep]]


    df_metrique = df_metrique.groupby(level = [0, 1], sort = False)

    # Calcul du nombre de match joué par équipe sur la saison et tri des équipes en fonction de leur classement sur la saison
    nb_matchs_team = df_metrique.apply(len)

    # On fait la somme pour chaque métrique sur toutes les journées de la saison
    df_metrique = df_metrique.sum()

    # On divise pour faire la moyenne par saison pour chaque équipe pour chaque métrique
    df_metrique = df_metrique.divide(nb_matchs_team, axis = 0)


if df_metrique.shape[1] == 0 :
    st.stop()


#----------------------------------------------- CRÉATION DF FINAL ------------------------------------------------------------------------------------


multi_index_liste = [df_metrique.columns, ["Top", "Middle", "Bottom"]]
multi_index = pd.MultiIndex.from_product(multi_index_liste, names=["Métrique", "Groupe"])

liste_saison.reverse()
df_final = pd.DataFrame(index = multi_index)

for saison in liste_saison :

    liste_rank = dico_rank[saison]

    df_final.loc[idx[:, "Top"], saison] = df_metrique.loc[idx[saison, liste_rank[:nb_top]], :].mean(axis = 0).values
    df_final.loc[idx[:, "Middle"], saison] = df_metrique.loc[idx[saison, liste_rank[nb_top:nb_top + nb_middle.loc[saison]]], :].mean(axis = 0).values
    df_final.loc[idx[:, "Bottom"], saison] = df_metrique.loc[idx[saison, liste_rank[nb_top + nb_middle.loc[saison]:]], :].mean(axis = 0).values

df_final.columns = replace_saison2(liste_saison)

df_final.dropna(axis = 0, how = "all", inplace = True)
df_final.replace({0 : np.nan}, inplace = True)
first_year = df_final.columns[0]
last_year = df_final.columns[-1]

df_final["Évolution en %"] = 100*(df_final[last_year] - df_final[first_year])/abs(df_final[first_year])
df_final.replace({np.nan : 0}, inplace = True)

df_final = df_final.reindex(abs(df_final.loc[:, "Top", :]).sort_values(by = ["Évolution en %"], ascending = False).index, level = 0)


#----------------------------------------------- AFFICHAGE DATAFRAME ------------------------------------------------------------------------------------


st.divider()

couleur_bg_df_partial = partial(couleur_bg_df, liste_saison = df_final.columns[:-1], df = df_final)

df_style = df_final.style.apply(couleur_bg_df_partial, axis = 0)
df_style = df_style.apply(couleur_text_df, axis = 1)

st.markdown(f"<p style='text-align: center;'>Tableau de l'évolution de chaque métrique entre la saison {first_year} et {last_year}</p>",
            unsafe_allow_html=True)

met_sel = st.dataframe(df_style, width = 10000, on_select = "rerun", selection_mode = "multi-row")


st.markdown(f"<p style='text-align: center;'>Code couleur de l'évolution des métriques entre la saison {first_year} et {last_year} :</p>",
            unsafe_allow_html=True)


# Afficher le texte avec le style défini

columns = st.columns(4)
with columns[0] :
    st.markdown('<div class="highlight1">Augmentation constante</div>', unsafe_allow_html=True)
with columns[1] :
    st.markdown('<div class="highlight2">Tendance haussière</div>', unsafe_allow_html=True)
with columns[2] :
    st.markdown('<div class="highlight3">Tendance baissière</div>', unsafe_allow_html=True)
with columns[3] :
    st.markdown('<div class="highlight4">Diminution constante</div>', unsafe_allow_html=True)


#----------------------------------------------- AFFICHAGE GRAPHIQUE ------------------------------------------------------------------------------------


if len(met_sel.selection.rows) == 0 :
    st.stop()

st.divider()

evo_graphe = df_style.data.iloc[met_sel.selection.rows].drop("Évolution en %", axis = 1)
new_index = []
for i in df_style.index[met_sel.selection.rows] :
    new_index.append(i[1] + " - " + i[0])
evo_graphe = evo_graphe.reset_index()
evo_graphe.index = new_index
evo_graphe = evo_graphe.drop(["Métrique", "Groupe"], axis = 1).T
fig = plt.figure()
plt.plot(evo_graphe, linewidth = 0.7)
plt.title("Graphique de l'évolution des métriques sélectionnées", fontweight = "heavy", y = 1.05, fontsize = 9)
plt.grid()
plt.legend(evo_graphe.columns, loc = "lower center", bbox_to_anchor=(0.5, -0.35 - 0.08*(int((len(evo_graphe.columns) + 1)/2) - 1)),
        fontsize = "small", ncol = 2)
plt.xlabel("Saison", fontsize = "small", fontstyle = "italic", labelpad = 10)
plt.ylabel("Métrique", fontsize = "small", fontstyle = "italic", labelpad = 10)
plt.tick_params(labelsize = 8)
ax = plt.gca()
ax.spines[:].set_visible(False)
st.pyplot(fig)