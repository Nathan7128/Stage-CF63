import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

st.title("Métriques différenciant le Top 5 du Bottom 15 de Ligue 2")


#----------------------------------------------- DÉFINITIONS DES DICTIONNAIRES ------------------------------------------------------------------------------------


dico_type = {
    "Physiques" : ["moyenne_physical.xlsx", "metrique_physical.xlsx",
        {"30 min. tip" : "_per30tip", "30 min. otip" : "_per30otip", "Match all possession" : "_per_Match"}],
    
    "Courses sans ballon avec la possession" : ["moyenne_running.xlsx", "metrique_running.xlsx",
        {"Match" : "per_match", "100 runs" : "per_100_runs", "30 min. tip" : "per_30_min_tip"},
        "Type de course",
        {"Runs in behind" : "runs_in_behind", "Runs ahead of the ball" : "runs_ahead_of_the_ball", "Support runs" : "support_runs",
        "Pulling wide runs" : "pulling_wide_runs", "Coming short runs" : "coming_short_runs", "Underlap runs" : "underlap_runs",
        "Overlap runs" : "overlap_runs", "Dropping off runs" : "dropping_off_runs",
        "Pulling half space runs" : "pulling_half_space_runs", "Cross receiver runs" : "cross_receiver_runs"},
        {"Leading to goal" : "leading_to_goal", "Leading to shot" : "leading_to_shot", "Received" : "received", "Threat" : "threat",
        "Targeted" : "targeted", "Dangerous" : "dangerous"}],

    "Action sous pression" : ["moyenne_pressure.xlsx", "metrique_pressure.xlsx",
        {"Match" : "per_match", "100 pressures" : "per_100_pressures", "30 min. tip" : "per_30_min_tip"},
        "Intensité de pression",
        {"Low" : "low", "Medium" : "medium", "High" : "high"}],
    
    "Passes à un coéquipier effectuant une course" : ["moyenne_passes.xlsx", "metrique_passes.xlsx",
        {"Match" : "per_match", "100 passes opportunities" : "per_100_pass_opportunities", "30 min. tip" : "per_30_min_tip"},
        "Type de course",
        {"Runs in behind" : "runs_in_behind", "Runs ahead of the ball" : "runs_ahead_of_the_ball", "Support runs" : "support_runs",
        "Pulling wide runs" : "pulling_wide_runs", "Coming short runs" : "coming_short_runs", "Underlap runs" : "underlap_runs",
        "Overlap runs" : "overlap_runs", "Dropping off runs" : "dropping_off_runs",
        "Pulling half space runs" : "pulling_half_space_runs", "Cross receiver runs" : "cross_receiver_runs"}]
}


#----------------------------------------------- FILTRAGE DES DATAS ------------------------------------------------------------------------------------


col1, col2 = st.columns([1, 5], gap = "large")

with col1 :
    choix_data = st.radio("Fournisseur data", options = ["Skill Corner", "Stats Bomb"])
    if choix_data == "Skill Corner" :
        annee = st.radio("Choisir saison", options = ["2023/2024", "2022/2023", "2021/2022"])
    else :
        annee = st.radio("Choisir saison", options = ["2023/2024", "2022/2023", "2021/2022", "2020/2021"])
    annee = annee.replace("/", "_")

if choix_data == "Skill Corner" :

    with col2 :

        cat_met = st.radio("Catégorie de métrique", dico_type.keys(), horizontal = True)

        file_moyenne = dico_type[cat_met][0]
        file_metrique = dico_type[cat_met][1]

        moyenne = pd.read_excel(f"Métriques discriminantes/Tableau métriques/moyenne/{annee}/{choix_data}/{file_moyenne}", 
                            index_col = 0)

        cat_moy = st.radio("Moyenne de la métrique", dico_type[cat_met][2].keys(), horizontal = True)

        cat_type = dico_type[cat_met][2][cat_moy]
        col_keep = [(cat_type in i) or ("ratio" in i) for i in moyenne.index]
        moyenne = moyenne.iloc[col_keep]

    if cat_met != "Physiques" :
        col_keep = [False]*len(moyenne)
        liste_cat_type1 = st.multiselect(dico_type[cat_met][3], dico_type[cat_met][4].keys(), default = dico_type[cat_met][4].keys())
        for cat_type in liste_cat_type1 :
            cat_type = dico_type[cat_met][4][cat_type]
            col_keep = np.logical_or(col_keep, [(cat_type in i) or ("ratio" in i and cat_type in i) for i in moyenne.index])
        moyenne = moyenne.iloc[col_keep]

        # columns = st.columns([3, 1, 1], vertical_alignment = "bottom")

        # moyenne_index = moyenne.index
        # col_keep = [False]*len(moyenne)

        # with columns[0] :
        #     liste_cat_type2 = st.multiselect("Catégorie", dico_type[cat_met][5].keys(), default = dico_type[cat_met][5].keys())

        # with columns[2] :
        #     if st.checkbox("Afficher le count total") :
        #         for cat_type in liste_cat_type1 :
        #             cat_type = dico_type[cat_met][4][cat_type]
        #             col_keep = np.logical_or(col_keep, [f"count_{cat_type}_{dico_type[cat_met][2][cat_moy]}" == i 
        #                                                 for i in moyenne.index])

        # for cat_type in liste_cat_type2 :
        #     cat_type = dico_type[cat_met][5][cat_type]
        #     col_keep = np.logical_or(col_keep, [(cat_type in i) or ("ratio" in i and cat_type in i) for i in moyenne_index])
        # moyenne = moyenne.iloc[col_keep]


else :
    file_moyenne = "moyenne_metriques.xlsx"
    file_metrique = "metriques.xlsx"

    moyenne = pd.read_excel(f"Métriques discriminantes/Tableau métriques/moyenne/{annee}/{choix_data}/{file_moyenne}",
                            index_col = 0)



st.divider()


if len(moyenne) > 0 :
    nb_metrique = st.slider("Nombre de métriques gardées", min_value=0, max_value = moyenne.shape[0], value = moyenne.shape[0])
    moyenne_sort = moyenne.loc[moyenne.index[:nb_metrique]]

    col_df = st.multiselect("Données des métriques à afficher", moyenne.columns, moyenne.columns.tolist())

    moyenne_sort = moyenne_sort[col_df]

    if len(col_df) > 0 :



#----------------------------------------------- STYLE ET AFFICHAGE DATAFRAME --------------------------------------------------------------------------


        if "Diff. Top 5 avec Bottom 15 en %" in col_df :

            @st.cache_data
            def couleur_df(val) :
                color = 'background-color : rgba(0, 255, 0, 0.3)' if val >= 0 else 'background-color : rgba(255, 0, 0, 0.3)'
                return color

            moyenne_sort = moyenne_sort.style.applymap(couleur_df, subset = ["Diff. Top 5 avec Bottom 15 en %"])


        st.divider()

        st.markdown("<p style='text-align: center;'>Tableau des métriques trier par rapport à la différence entre la moyenne du Top 5 et du Bottom 15</p>", unsafe_allow_html=True)


        moyenne_sort_df = st.dataframe(moyenne_sort, on_select = "rerun", selection_mode = "multi-row")


        metrique_moyenne = pd.read_excel(f"Métriques discriminantes/Tableau métriques/moyenne/{annee}/{choix_data}/{file_metrique}",
                                         index_col=0)

        metrique_moyenne_sort = metrique_moyenne[moyenne.index[moyenne_sort_df.selection.rows]]
        st.markdown(f"<p style='text-align: center;'>Tableau des métriques retenues, par équipes, en moyenne par match</p>",
                    unsafe_allow_html=True)
        st.dataframe(metrique_moyenne_sort)