import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from functools import partial

st.set_page_config(layout="wide")

st.title("Évolution des métriques au cours des saisons")
st.divider()

idx = pd.IndexSlice

pd.set_option('future.no_silent_downcasting', True)


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

@st.cache_data
def import_df(saison_df, choix_data_df, file_metrique_df) :
    return pd.read_excel(f"Métriques discriminantes/Tableau métriques/{saison_df}/{choix_data_df}/{file_metrique_df}",
                                    index_col= [0, 1])

def func_change(key1, key2) :
    st.session_state[key1] = st.session_state[key2]

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


#----------------------------------------------- DÉFINITIONS DES DICTIONNAIRES ------------------------------------------------------------------------------------


dico_met = {
    "Physiques" : ["physical.xlsx", {"30 min. tip" : "_per30tip", "30 min. otip" : "_per30otip",
        "Match all possession" : "_per_Match"}],
    "Courses sans ballon avec la possession" : ["running.xlsx", {"Match" : "per_match",
        "100 runs" : "per_100_runs", "30 min. tip" : "per_30_min_tip"}, ["runs_in_behind", "runs_ahead_of_the_ball",
        "support_runs", "pulling_wide_runs", "coming_short_runs", "underlap_runs", "overlap_runs", "dropping_off_runs",
        "pulling_half_space_runs", "cross_receiver_runs"]],
    "Action sous pression" : ["pressure.xlsx", {"Match" : "per_match",
        "100 pressures" : "per_100_pressures", "30 min. tip" : "per_30_min_tip"}, ["low", "medium", "high"]],
    "Passes à un coéquipier effectuant une course" : ["passes.xlsx", {"Match" : "per_match",
        "100 passes opportunities" : "_per_100_pass_opportunities", "30 min. tip" : "per_30_min_tip"}, ["runs_in_behind",
        "runs_ahead_of_the_ball", "support_runs", "pulling_wide_runs", "coming_short_runs", "underlap_runs", "overlap_runs",
        "dropping_off_runs", "pulling_half_space_runs", "cross_receiver_runs"]]
    }


dico_saison_fourn = {
    "Stats Bomb" : {"2020_2021" : "2020/2021", "2021_2022" : "2021/2022", "2022_2023" : "2022/2023", "2023_2024" : "2023/2024"},
    "Skill Corner" : {"2021_2022" : "2021/2022", "2022_2023" : "2022/2023", "2023_2024" : "2023/2024"}
               }
dico_df_saison = {}


dico_rank = {"2023_2024" : ["AJ Auxerre", "Angers SCO", "AS Saint-Étienne", "Rodez Aveyron", "Paris FC", "SM Caen", "Stade Lavallois Mayenne FC",
           "Amiens Sporting Club", "En Avant de Guingamp", "Pau FC", "Grenoble Foot 38", "Girondins de Bordeaux", "SC Bastia",
           "FC Annecy", "AC Ajaccio", "Dunkerque", "ES Troyes AC", "US Quevilly-Rouen", "US Concarneau", "Valenciennes FC"],
           "2022_2023" : ["Le Havre AC", "FC Metz", "Girondins de Bordeaux", "SC Bastia", "SM Caen", "En Avant de Guingamp", "Paris FC",
           "AS Saint-Étienne", "FC Sochaux-Montbéliard", "Grenoble Foot 38", "US Quevilly-Rouen", "Amiens Sporting Club", "Pau FC",
           "Rodez Aveyron", "Stade Lavallois Mayenne FC", "Valenciennes FC", "FC Annecy", "Dijon FCO", "Nîmes Olympique", "Chamois Niortais FC"],
           "2021_2022" : ["Toulouse FC", "AC Ajaccio", "AJ Auxerre", "Paris FC", "FC Sochaux-Montbéliard", "En Avant de Guingamp",
                             "SM Caen", "Le Havre AC", "Nîmes Olympique", "Pau FC", "Dijon FCO", "SC Bastia", "Chamois Niortais FC", 
                             "Amiens Sporting Club", "Grenoble Foot 38", "Valenciennes FC", "Rodez Aveyron", "US Quevilly-Rouen",
                             "Dunkerque", "AS Nancy-Lorraine"]}

#----------------------------------------------- CHOIX SAISON ET MÉTRIQUE ------------------------------------------------------------------------------------


columns = st.columns([2, 3, 2], gap = "large")

with columns[0] :
    func_change("select_data", "choix_data")
    choix_data = st.radio("Fournisseur data", options = ["Skill Corner", "Stats Bomb"], horizontal = True,
                          key = "select_data", on_change = func_change, args = ("choix_data", "select_data"))
    dico_saison = dico_saison_fourn[choix_data]
    nb_saison_comp = st.number_input("Nombre de saison à comparer", min_value = 2, max_value = len(dico_saison), value = len(dico_saison))
    dico_saison = dict(list(dico_saison.items())[-nb_saison_comp:])

if choix_data == "Skill Corner" :
    with columns[1] :
        func_change("select_cat_met", "cat_met")
        cat_met = st.radio("Catégorie de métrique", dico_met.keys(), horizontal = True, key = 'select_cat_met',
                            on_change = func_change, args = ("cat_met", "select_cat_met"))
        win_met = st.checkbox("Métriques pour les équipes qui gagnent les matchs")

    with columns[2] :
        moy_met = st.multiselect("Moyenne de la métrique", list(dico_met[cat_met][1].keys()), default = list(dico_met[cat_met][1].keys()))


#----------------------------------------------- IMPORTATION DATAFRAME SKILL CORNER ------------------------------------------------------------------------------------
    
    for saison in list(dico_saison.keys()) :
        df_import = import_df(saison, "Skill Corner", dico_met[cat_met][0])

        if win_met :
                df_import = df_import[df_import.result == "win"]
            
        nb_matchs_team = df_import.groupby("team_name").apply(len).reindex(dico_rank[saison])

        df_import = df_import.reset_index().drop(["Journée", "result"], axis = 1).groupby("team_name", as_index = True, sort = False).sum().reindex(dico_rank[saison])

        df_import = df_import.divide(nb_matchs_team, axis = 0)

        col_keep = [False]*df_import.shape[1]
        for cat_type in moy_met :
            cat_type = dico_met[cat_met][1][cat_type]
            col_keep = np.logical_or(col_keep, [(cat_type in i) or ("ratio" in i) for i in df_import.columns])
        df_import = df_import[df_import.columns[col_keep]]
        dico_df_saison[saison] = df_import

#----------------------------------------------- FILTRAGE MÉTRIQUE ------------------------------------------------------------------------------------

    if cat_met != "Physiques" :
        st.divider()
        
        type_met = st.multiselect("Type de la métrique", dico_met[cat_met][2], default = dico_met[cat_met][2])
        col_keep_type_met = [False]*df_import.shape[1]
        for cat_type in type_met :
            col_keep_type_met = np.logical_or(col_keep_type_met, [(cat_type in i) or ("ratio" in i and cat_type in i) for i in df_import.columns])
        
        for saison in dico_df_saison.keys() :
            dico_df_saison[saison] = dico_df_saison[saison][dico_df_saison[saison].columns[col_keep_type_met]]

        df = dico_df_saison[saison]
        if cat_met == "Courses sans ballon avec la possession" :
            col_keep = [True]*df.shape[1]
            columns = st.columns([2, 1, 1], vertical_alignment = "center", gap = "large")
            with columns[0] :
                dico_cat_run = {"Dangerous" : "dangerous",
                                "Leading to shot" : "leading_to_shot",
                                "Leading to goal" : "leading_to_goal"}
                liste_cat_run = ["All"] + list(dico_cat_run.keys())
                cat_run_choice = st.multiselect("Catégorie du run", options = liste_cat_run, default = liste_cat_run)
                if "All" not in cat_run_choice :
                    col_keep = [False]*df.shape[1]
                    for cat_run in dico_cat_run.values() :
                        col_keep = np.logical_or(col_keep, [cat_run in i for i in df.columns])
                for cat_run in dico_cat_run.keys() :
                    if cat_run not in cat_run_choice :
                        col_keep = np.logical_and(col_keep, [dico_cat_run[cat_run] not in i for i in df.columns])

            with columns[1] :
                if not(st.checkbox('Métrique "threat"', value = True)) :
                    col_keep = np.logical_and(col_keep, ["threat" not in i for i in df.columns])

            with columns[2] :
                liste_type_passe_run = ["Targeted", "Received"]
                type_passe_run = st.multiselect("Type de passe liée au run", liste_type_passe_run, default = liste_type_passe_run)
                if "Targeted" not in type_passe_run :
                    col_keep = np.logical_and(col_keep, ["targeted" not in i for i in df.columns])
                if "Received" not in type_passe_run :
                    col_keep = np.logical_and(col_keep, ["received" not in i for i in df.columns])


        elif cat_met == "Action sous pression" :
            col_keep = [False]*df.shape[1]
            columns = st.columns(3, vertical_alignment = "center", gap = "large")
            with columns[0] :
                dico_cat_met_pressure = {"Passes" : "pass", "Conservation du ballon" : "ball_retention", "Perte de balle" : "forced_losses",
                                        "Pression reçue" : "received_per"}
                cat_met_pressure = st.multiselect("Catégorie de métrique liée au pressing", dico_cat_met_pressure.keys(),
                                                default = dico_cat_met_pressure.keys())
                for cat_met in cat_met_pressure :
                    col_keep = np.logical_or(col_keep, [dico_cat_met_pressure[cat_met] in i for i in df.columns])

            if "Passes" in cat_met_pressure :
                with columns[1] :
                    dico_type_passe_pressure = {"All" : [(("pass_completion" not in i) or ("dangerous" in i) or ("difficult" in i)) and 
                        ("count_completed_pass" not in i) and ("count_pass_attempts" not in i) for i in df.columns],
                        "Dangerous" : ["dangerous" not in i for i in df.columns], 
                        "Difficult" : ["difficult" not in i for i in df.columns]}
                    type_passe_pressure = st.multiselect("Type de passe", dico_type_passe_pressure.keys(), default = dico_type_passe_pressure.keys())
                    for type_passe in dico_type_passe_pressure.keys() :
                        if type_passe not in type_passe_pressure :
                            col_keep = np.logical_and(col_keep, dico_type_passe_pressure[type_passe])
                    result_pass_pressure = st.multiselect("Résultat de la passe sous pression", ["Attempts", "Completed"],
                                                        default = ["Attempts", "Completed"])
                    if "Attempts" not in result_pass_pressure :
                        col_keep = np.logical_and(col_keep, ["attempts" not in i for i in df.columns])
                    if "Completed" not in result_pass_pressure :
                        col_keep = np.logical_and(col_keep, ["completed" not in i for i in df.columns])

            with columns[-1] :
                if "Passes" in cat_met_pressure :
                    if not(st.checkbox("Ratio lié aux passes", value = True)) :
                        col_keep = np.logical_and(col_keep, [("pass" not in i) or ("ratio" not in i) for i in df.columns])                   
                if "Conservation du ballon" in cat_met_pressure :
                    if not(st.checkbox("Ratio lié à la conservation du ballon", value = True)) :
                        col_keep = np.logical_and(col_keep, ["ball_retention_ratio" not in i for i in df.columns])


        else :
            col_keep = [True]*df.shape[1]
            columns = st.columns([2, 1, 1, 2], vertical_alignment = "center", gap = "large")

            with columns[0] :
                dico_cat_run = {"Dangerous" : "dangerous",
                                "Leading to shot" : "leading_to_shot",
                                "Leading to goal" : "leading_to_goal"}
                liste_cat_run = ["All"] + list(dico_cat_run.keys())
                cat_run_choice = st.multiselect("Catégorie du run", options = liste_cat_run, default = liste_cat_run)
                if "All" not in cat_run_choice :
                    col_keep = [False]*df.shape[1]
                    for cat_run in dico_cat_run.values() :
                        col_keep = np.logical_or(col_keep, [cat_run in i for i in df.columns])
                for cat_run in dico_cat_run.keys() :
                    if cat_run not in cat_run_choice :
                        col_keep = np.logical_and(col_keep, [dico_cat_run[cat_run] not in i for i in df.columns])

            with columns[3] :
                dico_type_passe = {"Attempts" : "attempt", "Completed" : "completed", "Opportunities" : "opportunities"}
                choix_type_passe = st.multiselect("Type de passe", dico_type_passe.keys(), default = dico_type_passe.keys())
                col_keep_passe = [False]*df.shape[1]
                for type_passe in choix_type_passe :
                    col_keep_passe = np.logical_or(col_keep_passe, [dico_type_passe[type_passe] in i for i in df.columns])
                col_keep = np.logical_and(col_keep, col_keep_passe)
                if "All" in cat_run_choice :
                    col_keep = np.logical_or(col_keep, ["teammate" in i for i in df.columns])

            with columns[1] :
                if not(st.checkbox('Métrique "threat"', value = True)) :
                    col_keep = np.logical_and(col_keep, ["threat" not in i for i in df.columns])

            with columns[2] :
                if st.checkbox("Ratio", True) :
                    col_keep = np.logical_or(col_keep, ["ratio" in i for i in df.columns])


        for saison in dico_df_saison.keys() :
            dico_df_saison[saison] = dico_df_saison[saison][dico_df_saison[saison].columns[col_keep]]



#----------------------------------------------- IMPORTATION DATAFRAME STATS BOMB ------------------------------------------------------------------------------------


else :
    for saison in dico_saison.keys() :
        df_import = pd.read_excel(f"Métriques discriminantes/Tableau métriques/{saison}/{choix_data}/metriques.xlsx", index_col = 0)
        dico_df_saison[saison] = df_import


#----------------------------------------------- CHOIX GROUPES ------------------------------------------------------------------------------------


st.divider()

df_groupe = pd.DataFrame(0, index = ["Top", "Middle", "Bottom"], columns = ["Taille", "Slider"])
df_groupe["Slider"] = "Nombre d'équipe dans le " + df_groupe.index

columns = st.columns(3, gap = "large", vertical_alignment = "center")
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


#----------------------------------------------- CRÉATION DF FINAL ------------------------------------------------------------------------------------


multi_index_liste = [dico_df_saison[saison].columns, df_groupe.index.tolist()]
multi_index = pd.MultiIndex.from_product(multi_index_liste, names=["Métrique", "Groupe"])

df_final = pd.DataFrame(index = multi_index, columns = [dico_saison[i] for i in dico_df_saison.keys()])

if len(df_final) > 0 :

    for saison in dico_df_saison.keys() :
        df = dico_df_saison[saison]
        saison = dico_saison[saison]

        df_final.loc[idx[:, "Top"], saison] = df.iloc[:df_groupe.loc["Top", "Taille"]].mean(axis = 0).values
        df_final.loc[idx[:, "Middle"], saison] = df.iloc[df_groupe.loc["Top", "Taille"]:df_groupe.loc["Top", "Taille"] + df_groupe.loc["Middle", "Taille"]].mean(axis = 0).values
        df_final.loc[idx[:, "Bottom"], saison] = df.iloc[df_groupe.loc["Top", "Taille"] + df_groupe.loc["Middle", "Taille"]:].mean(axis = 0).values

    df_final.dropna(axis = 0, how = "all", inplace = True)
    df_final.replace({0 : np.nan}, inplace = True)
    first_year = dico_saison[list(dico_df_saison.keys())[0]]
    last_year = dico_saison[list(dico_df_saison.keys())[-1]]
    df_final["Évolution en %"] = 100*(df_final[last_year] - df_final[first_year])/abs(df_final[first_year])
    df_final.replace({np.nan : 0}, inplace = True)

    df_final = df_final.reindex(abs(df_final.loc[:, "Top", :]).sort_values(by = ["Évolution en %"], ascending = False).index, level = 0)


    st.divider()



#----------------------------------------------- AFFICHAGE DATAFRAME ------------------------------------------------------------------------------------

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



    if len(met_sel.selection.rows) > 0 :

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