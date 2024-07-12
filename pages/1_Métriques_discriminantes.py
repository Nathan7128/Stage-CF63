import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

st.title("Métriques différenciant le Top 5 du Bottom 15 de Ligue 2")




col1, col2 = st.columns([1, 5], gap = "large")

with col1 :
    choix_data = st.radio("Fournisseur data", options = ["Skill Corner", "Stats Bomb"])
    if choix_data == "Skill Corner" :
        annee = st.radio("Choisir saison", options = ["2021_2022", "2022_2023", "2023_2024"])
    else :
        annee = st.radio("Choisir saison", options = ["2020_2021", "2021_2022", "2022_2023", "2023_2024"])

with col2 :    
    if choix_data == "Skill Corner" :
        dico_type = {
            "Physiques" : ["moyenne_physical.xlsx", "metrique_physical.xlsx", ["tip", "otip", "all"]],
            "Courses sans ballon avec la possession" : ["moyenne_running.xlsx", "metrique_running.xlsx", ["runs_in_behind",
                "runs_ahead_of_the_ball", "support_runs", "pulling_wide_runs", "coming_short_runs", "underlap_runs", "overlap_runs",
                "dropping_off_runs", "pulling_half_space_runs", "cross_receiver_runs"]],
            "Action sous pression" : ["moyenne_pressure.xlsx", "metrique_pressure.xlsx", ["low", "medium", "high"]],
            "Passes à un coéquipier effectuant une course" : ["moyenne_passes.xlsx", "metrique_passes.xlsx", ["runs_in_behind",
                "runs_ahead_of_the_ball", "support_runs", "pulling_wide_runs", "coming_short_runs", "underlap_runs", "overlap_runs",
                "dropping_off_runs", "pulling_half_space_runs", "cross_receiver_runs"]]
        }
        liste_cat_met = ["Physiques", "Courses sans ballon avec la possession",
                    "Action sous pression", "Passes à un coéquipier effectuant une course"]
        cat_met = st.radio("Catégorie de métrique", liste_cat_met, horizontal = True)
        liste_cat_type = st.multiselect("Type de la catégorie", dico_type[cat_met][2], default = dico_type[cat_met][2])
        file_moyenne = dico_type[cat_met][0]
        file_metrique = dico_type[cat_met][1]

        moyenne = pd.read_excel(f"Métriques discriminantes/Tableau métriques/moyenne/{annee}/{choix_data}/{file_moyenne}", index_col = 0)

        col_keep = [False]*len(moyenne)
        if cat_met == "Physiques" :
            for cat_type in liste_cat_type :
                col_keep = np.logical_or(col_keep, ["_" + cat_type in i for i in moyenne.index])

        else :
            for cat_type in liste_cat_type :
                col_keep = np.logical_or(col_keep, [cat_type in i for i in moyenne.index])

        moyenne = moyenne.iloc[col_keep]
    else :
        file_moyenne = "moyenne_metriques.xlsx"
        file_metrique = "metriques.xlsx"

        moyenne = pd.read_excel(f"Métriques discriminantes/Tableau métriques/moyenne/{annee}/{choix_data}/{file_moyenne}", index_col = 0)


@st.cache_data
def couleur_df(val) :
    color = 'green' if val >= 0 else 'red'
    return f'background-color : {color}'

st.divider()


if len(moyenne) > 0 :
    nb_metrique = st.slider("Nombre de métriques gardées", min_value=0, max_value = moyenne.shape[0], value = moyenne.shape[0])
    moyenne_sort = moyenne.loc[moyenne.index[:nb_metrique]]

    moyenne_sort = moyenne_sort.style.applymap(couleur_df, subset = ["Diff. Top 5 avec Bottom 15 en %"])
    col_df = st.multiselect("Données des métriques à afficher", moyenne.columns, moyenne.columns.tolist())

    st.divider()

    st.markdown("<p style='text-align: center;'>Tableau des métriques trier par rapport à la différence entre la moyenne du Top 5 et du Bottom 15</p>", unsafe_allow_html=True)


    moyenne_sort_df = st.data_editor(moyenne_sort, num_rows = "dynamic", disabled = ["Diff. Top 5 avec Bottom 15 en %"])

    metrique_moyenne = pd.read_excel(f"Métriques discriminantes/Tableau métriques/moyenne/{annee}/{choix_data}/{file_metrique}", index_col=0)

    metrique_moyenne_sort = metrique_moyenne[moyenne_sort_df.index]
    st.markdown(f"<p style='text-align: center;'>Tableau des métriques retenues, par équipes, en moyenne par match</p>", unsafe_allow_html=True)
    st.dataframe(metrique_moyenne_sort)