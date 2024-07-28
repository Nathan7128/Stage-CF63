import streamlit as st
import pandas as pd
import numpy as np
import signal

st.set_page_config(layout = "wide")

st.title("Métriques discriminantes d'une compétition")
st.divider()

#----------------------------------------------- DÉFINITIONS DES FONCTIONS ------------------------------------------------------------------------------------


@st.cache_data
def import_df(saison_df, choix_data_df, file_metrique_df) :
    return pd.read_excel(f"Métriques discriminantes/Tableau métriques/{saison_df}/{choix_data_df}/{file_metrique_df}",
                                    index_col=[0, 1])

def couleur_diff(col) :
    if col.name in ["Diff. Top avec Bottom en %", "Diff. Top avec Middle en %", "Diff. Middle avec Bottom en %"] :
        color = []
        for met in col.index :
            if col.loc[met] >= 0 :
                color.append("background-color : rgba(0, 255, 0, 0.3)")
            else : 
                color.append("background-color : rgba(255, 0, 0, 0.3)")
        return color
    else :
        return ['']*len(col)

#----------------------------------------------- DÉFINITIONS DES DICTIONNAIRES ------------------------------------------------------------------------------------

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

dico_type = {
    "Physiques" : ["physical.xlsx",
        {"30 min. tip" : "_per30tip", "30 min. otip" : "_per30otip", "Match all possession" : "_per_Match"}],
    
    "Courses sans ballon avec la possession" : ["running.xlsx",
        {"Match" : "per_match", "100 runs" : "per_100_runs", "30 min. tip" : "per_30_min_tip"},
        "Type de course",
        {"Runs in behind" : "runs_in_behind", "Runs ahead of the ball" : "runs_ahead_of_the_ball", "Support runs" : "support_runs",
        "Pulling wide runs" : "pulling_wide_runs", "Coming short runs" : "coming_short_runs", "Underlap runs" : "underlap_runs",
        "Overlap runs" : "overlap_runs", "Dropping off runs" : "dropping_off_runs",
        "Pulling half space runs" : "pulling_half_space_runs", "Cross receiver runs" : "cross_receiver_runs"},
        {"Leading to goal" : "leading_to_goal", "Leading to shot" : "leading_to_shot", "Received" : "received", "Threat" : "threat",
        "Targeted" : "targeted", "Dangerous" : "dangerous"}],

    "Action sous pression" : ["pressure.xlsx",
        {"Match" : "per_match", "100 pressures" : "per_100_pressures", "30 min. tip" : "per_30_min_tip"},
        "Intensité de pression",
        {"Low" : "low", "Medium" : "medium", "High" : "high"}],
    
    "Passes à un coéquipier effectuant une course" : ["passes.xlsx",
        {"Match" : "per_match", "100 passes opportunities" : "per_100_pass_opportunities", "30 min. tip" : "per_30_min_tip"},
        "Type de course",
        {"Runs in behind" : "runs_in_behind", "Runs ahead of the ball" : "runs_ahead_of_the_ball", "Support runs" : "support_runs",
        "Pulling wide runs" : "pulling_wide_runs", "Coming short runs" : "coming_short_runs", "Underlap runs" : "underlap_runs",
        "Overlap runs" : "overlap_runs", "Dropping off runs" : "dropping_off_runs",
        "Pulling half space runs" : "pulling_half_space_runs", "Cross receiver runs" : "cross_receiver_runs"}]
}

#----------------------------------------------- CHOIX ANNÉE + FOURNISSEUR ------------------------------------------------------------------------------------


col1, col2 = st.columns([1, 3], gap = "large")

with col1 :
    choix_data = st.radio("Fournisseur data", options = ["Skill Corner", "Stats Bomb"], horizontal = True)
    if choix_data == "Skill Corner" :
        choix_saison = st.multiselect("Choisir saison", options = ["2023/2024", "2022/2023", "2021/2022"], default = "2023/2024")
        win_met = st.checkbox("Métriques pour les équipes qui gagnent les matchs")
    else :
        choix_saison = st.multiselect("Choisir saison", options = ["2023/2024", "2022/2023", "2021/2022", "2020/2021"],
                                      default = "2023/2024")
    liste_saison = [i.replace("/", "_") for i in choix_saison]
    

if len(liste_saison) > 0 :

    #----------------------------------------------- CHOIX TAILLE GROUPES ------------------------------------------------------------------------------------

    st.divider()

    columns = st.columns(3, gap = "large", vertical_alignment = "center")
    with columns[0] :
        nb_top = st.slider("Nombre d'équipe dans le Top", min_value = 1, max_value = 20, value = 5)
    with columns[1] :
        if nb_top == 20 :
            nb_bottom = 20 - nb_top
            st.write(f"Nombre d'équipe dans le Bottom : {nb_bottom}")
        else :
            nb_bottom = st.slider("Nombre d'équipe dans le Bottom", min_value = 0, max_value = 20 - nb_top)
    with columns[2] :
        nb_middle = 20 - nb_top - nb_bottom
        st.write(f"Nombre d'équipe dans le Middle : {nb_middle}")

    st.divider()

    #----------------------------------------------- IMPORTATION DATAFRAME ------------------------------------------------------------------------------------



    if choix_data == "Skill Corner" :
        with col2 :
            cat_met = st.radio("Catégorie de métrique", dico_type.keys(), horizontal = True)

            cat_moy = st.radio("Moyenne de la métrique", dico_type[cat_met][1].keys(), horizontal = True)

        file_metrique = dico_type[cat_met][0]

    else :
        file_metrique = "metriques.xlsx"
    
    liste_df_metrique = []
    for saison in liste_saison :
        df_metrique = import_df(saison, choix_data, file_metrique)
        
        if choix_data == "Skill Corner" :

            if win_met :
                df_metrique = df_metrique[df_metrique.result == "win"]
            
            nb_matchs_team = df_metrique.groupby("team_name").apply(len).reindex(dico_rank[saison])

            df_metrique = df_metrique.reset_index().drop(["Journée", "result"], axis = 1).groupby("team_name", as_index = True, sort = False).sum().reindex(dico_rank[saison])

            df_metrique = df_metrique.divide(nb_matchs_team, axis = 0)
            
        liste_df_metrique.append(df_metrique)

    # ------------------------------------------------ CRÉATION DATAFRAME MOYENNE -------------------------------------------------------------


    with col2 :

        liste_df_moyenne = []
        for df_metrique in liste_df_metrique :

            moyenne = pd.DataFrame(index = df_metrique.columns)

            df_top = df_metrique.iloc[:nb_top]
            df_middle = df_metrique.iloc[nb_top:nb_top + nb_middle]
            df_bottom = df_metrique.iloc[nb_top + nb_middle:]

            moyenne["Moyenne Top"] = df_top.mean(axis = 0)

            moyenne["Moyenne Bottom"] = df_bottom.mean(axis = 0)

            moyenne["Moyenne Middle"] = df_middle.mean(axis = 0)
                
            liste_df_moyenne.append(moyenne)


        moyenne = sum(liste_df_moyenne)/len(liste_df_moyenne)

        moyenne["Diff. Top avec Bottom en %"] = (100*(moyenne["Moyenne Top"] - moyenne["Moyenne Bottom"])/abs(moyenne["Moyenne Bottom"])).round(2)
        moyenne["Diff. Top avec Middle en %"] = (100*(moyenne["Moyenne Top"] - moyenne["Moyenne Middle"])/abs(moyenne["Moyenne Middle"])).round(2)
        moyenne["Diff. Middle avec Bottom en %"] = (100*(moyenne["Moyenne Middle"] - moyenne["Moyenne Bottom"])/abs(moyenne["Moyenne Bottom"])).round(2)

        if nb_top > 1 :
            moyenne["Ecart type Top"] = df_top.std(axis = 0)
            moyenne["Min Top"] = df_top.min(axis = 0)
            moyenne["Max Top"] = df_top.max(axis = 0)

        if nb_middle > 1 :
            moyenne["Ecart type Middle"] = df_middle.std(axis = 0)
            moyenne["Min Middle"] = df_middle.std(axis = 0)
            moyenne["Max Middle"] = df_middle.std(axis = 0)

        if nb_bottom > 1 :
            moyenne["Ecart type Bottom"] = df_bottom.std(axis = 0)
            moyenne["Min Bottom"] = df_bottom.min(axis = 0)
            moyenne["Max Bottom"] = df_bottom.max(axis = 0)

        if nb_bottom > 0 :
            moyenne = moyenne.reindex(abs(moyenne).sort_values(by = "Diff. Top avec Bottom en %", ascending = False).index)

        elif nb_middle > 0 :
            moyenne = moyenne.reindex(abs(moyenne).sort_values(by = "Diff. Top avec Middle en %", ascending = False).index)

        moyenne.dropna(axis = 1, how = "all", inplace = True)



    #----------------------------------------------- FILTRAGE MÉTRIQUES SKILLCORNER ------------------------------------------------------------------------------------



    if choix_data == "Skill Corner" :
        cat_type = dico_type[cat_met][1][cat_moy]
        col_keep = [(cat_type in i) or ("ratio" in i) for i in moyenne.index]
        moyenne = moyenne.iloc[col_keep]

        if cat_met != "Physiques" :
            col_keep = [False]*len(moyenne)
            liste_cat_type1 = st.multiselect(dico_type[cat_met][2], dico_type[cat_met][3].keys(), default = dico_type[cat_met][3].keys())
            for cat_type in liste_cat_type1 :
                cat_type = dico_type[cat_met][3][cat_type]
                col_keep = np.logical_or(col_keep, [(cat_type in i) or ("ratio" in i and cat_type in i) for i in moyenne.index])
            moyenne = moyenne.iloc[col_keep]


            if cat_met == "Courses sans ballon avec la possession" :
                col_keep = [True]*len(moyenne)
                columns = st.columns([2, 1, 1], vertical_alignment = "center", gap = "large")
                with columns[0] :
                    dico_cat_run = {"Dangerous" : "dangerous",
                                    "Leading to shot" : "leading_to_shot",
                                    "Leading to goal" : "leading_to_goal"}
                    liste_cat_run = ["All"] + list(dico_cat_run.keys())
                    cat_run_choice = st.multiselect("Catégorie du run", options = liste_cat_run, default = liste_cat_run)
                    if "All" not in cat_run_choice :
                        col_keep = [False]*len(moyenne)
                        for cat_run in dico_cat_run.values() :
                            col_keep = np.logical_or(col_keep, [cat_run in i for i in moyenne.index])
                    for cat_run in dico_cat_run.keys() :
                        if cat_run not in cat_run_choice :
                            col_keep = np.logical_and(col_keep, [dico_cat_run[cat_run] not in i for i in moyenne.index])

                with columns[1] :
                    if not(st.checkbox('Métrique "threat"', value = True)) :
                        col_keep = np.logical_and(col_keep, ["threat" not in i for i in moyenne.index])

                with columns[2] :
                    liste_type_passe_run = ["Targeted", "Received"]
                    type_passe_run = st.multiselect("Type de passe liée au run", liste_type_passe_run, default = liste_type_passe_run)
                    if "Targeted" not in type_passe_run :
                        col_keep = np.logical_and(col_keep, ["targeted" not in i for i in moyenne.index])
                    if "Received" not in type_passe_run :
                        col_keep = np.logical_and(col_keep, ["received" not in i for i in moyenne.index])


            elif cat_met == "Action sous pression" :
                col_keep = [False]*len(moyenne)
                columns = st.columns(3, vertical_alignment = "center", gap = "large")
                with columns[0] :
                    dico_cat_met_pressure = {"Passes" : "pass", "Conservation du ballon" : "ball_retention", "Perte de balle" : "forced_losses",
                                            "Pression reçue" : "received_per"}
                    cat_met_pressure = st.multiselect("Catégorie de métrique liée au pressing", dico_cat_met_pressure.keys(),
                                                    default = dico_cat_met_pressure.keys())
                    for cat_met in cat_met_pressure :
                        col_keep = np.logical_or(col_keep, [dico_cat_met_pressure[cat_met] in i for i in moyenne.index])

                if "Passes" in cat_met_pressure :
                    with columns[1] :
                        dico_type_passe_pressure = {"All" : [(("pass_completion" not in i) or ("dangerous" in i) or ("difficult" in i)) and 
                            ("count_completed_pass" not in i) and ("count_pass_attempts" not in i) for i in moyenne.index],
                            "Dangerous" : ["dangerous" not in i for i in moyenne.index], 
                            "Difficult" : ["difficult" not in i for i in moyenne.index]}
                        type_passe_pressure = st.multiselect("Type de passe", dico_type_passe_pressure.keys(), default = dico_type_passe_pressure.keys())
                        for type_passe in dico_type_passe_pressure.keys() :
                            if type_passe not in type_passe_pressure :
                                col_keep = np.logical_and(col_keep, dico_type_passe_pressure[type_passe])
                        result_pass_pressure = st.multiselect("Résultat de la passe sous pression", ["Attempts", "Completed"],
                                                            default = ["Attempts", "Completed"])
                        if "Attempts" not in result_pass_pressure :
                            col_keep = np.logical_and(col_keep, ["attempts" not in i for i in moyenne.index])
                        if "Completed" not in result_pass_pressure :
                            col_keep = np.logical_and(col_keep, ["completed" not in i for i in moyenne.index])

                with columns[-1] :
                    if "Passes" in cat_met_pressure :
                        if not(st.checkbox("Ratio lié aux passes", value = True)) :
                            col_keep = np.logical_and(col_keep, [("pass" not in i) or ("ratio" not in i) for i in moyenne.index])                   
                    if "Conservation du ballon" in cat_met_pressure :
                        if not(st.checkbox("Ratio lié à la conservation du ballon", value = True)) :
                            col_keep = np.logical_and(col_keep, ["ball_retention_ratio" not in i for i in moyenne.index])


            else :
                col_keep = [True]*len(moyenne)
                columns = st.columns([2, 1, 1, 2], vertical_alignment = "center", gap = "large")

                with columns[0] :
                    dico_cat_run = {"Dangerous" : "dangerous",
                                    "Leading to shot" : "leading_to_shot",
                                    "Leading to goal" : "leading_to_goal"}
                    liste_cat_run = ["All"] + list(dico_cat_run.keys())
                    cat_run_choice = st.multiselect("Catégorie du run", options = liste_cat_run, default = liste_cat_run)
                    if "All" not in cat_run_choice :
                        col_keep = [False]*len(moyenne)
                        for cat_run in dico_cat_run.values() :
                            col_keep = np.logical_or(col_keep, [cat_run in i for i in moyenne.index])
                    for cat_run in dico_cat_run.keys() :
                        if cat_run not in cat_run_choice :
                            col_keep = np.logical_and(col_keep, [dico_cat_run[cat_run] not in i for i in moyenne.index])

                with columns[3] :
                    dico_type_passe = {"Attempts" : "attempt", "Completed" : "completed", "Opportunities" : "opportunities"}
                    choix_type_passe = st.multiselect("Type de passe", dico_type_passe.keys(), default = dico_type_passe.keys())
                    col_keep_passe = [False]*len(moyenne)
                    for type_passe in choix_type_passe :
                        col_keep_passe = np.logical_or(col_keep_passe, [dico_type_passe[type_passe] in i for i in moyenne.index])
                    col_keep = np.logical_and(col_keep, col_keep_passe)
                    if "All" in cat_run_choice :
                        col_keep = np.logical_or(col_keep, ["teammate" in i for i in moyenne.index])

                with columns[1] :
                    if not(st.checkbox('Métrique "threat"', value = True)) :
                        col_keep = np.logical_and(col_keep, ["threat" not in i for i in moyenne.index])

                with columns[2] :
                    if st.checkbox("Ratio", True) :
                        col_keep = np.logical_or(col_keep, ["ratio" in i for i in moyenne.index])


            moyenne = moyenne.iloc[col_keep]


            st.divider()


    if len(moyenne) > 0 :
        nb_metrique = st.slider("Nombre de métriques gardées", min_value=0, max_value = moyenne.shape[0], value = moyenne.shape[0])
        moyenne = moyenne.loc[moyenne.index[:nb_metrique]]

        col_df = st.multiselect("Données des métriques à afficher", moyenne.columns, moyenne.columns.tolist())

        moyenne_sort = moyenne[col_df]

        if len(col_df) > 0 :



    #----------------------------------------------- STYLE ET AFFICHAGE DATAFRAME --------------------------------------------------------------------------

            st.divider()

            st.markdown("<p style='text-align: center;'>Tableau des métriques discriminantes</p>", unsafe_allow_html=True)
            
            moyenne_sort_style = moyenne_sort.style.apply(couleur_diff, axis = 0)

            moyenne_sort_df = st.dataframe(moyenne_sort_style, on_select = "rerun", selection_mode = "multi-row")

            if len(moyenne_sort_df.selection.rows) > 0 :

                for i in range (len(liste_saison)) :
                    st.divider()
                    st.markdown(f"<p style='text-align: center;'>Tableau des métriques retenues, par équipes, en moyenne par match lors de la saison {choix_saison[i]} </p>", unsafe_allow_html=True)
                    metrique_moyenne_sort = liste_df_metrique[i][moyenne.index[moyenne_sort_df.selection.rows]]
                    st.dataframe(metrique_moyenne_sort)