import streamlit as st
import pandas as pd

st.set_page_config(page_title= "Métriques différenciant le Top 5 du Bottom 15 de Ligue 2", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

col1, col2 = st.columns(2)

with col1 :
    annee = st.radio("Choisir année", options = ["2021_2022", "2022_2023", "2023_2024"])

with col2 :
    choix_data = st.radio("Fournisseur data", options = ["Skill Corner", "Stats Bomb"])
    if choix_data == "Skill Corner" :
        path_moyenne = ["moyenne_physical.xlsx", "moyenne_running.xlsx", "moyenne_pressure.xlsx", "moyenne_passes.xlsx"]
        path_metrique = ["metrique_physical.xlsx", "metrique_running.xlsx", "metrique_pressure.xlsx", "metrique_passes.xlsx"]
        liste_cat_met = ["Physiques", "Courses sans ballon avec la possession",
                    "Action sous pression", "Passes à un coéquipier effectuant une course"]
        cat_met = st.radio("Catégorie de métrique", liste_cat_met)
        index_cat = liste_cat_met.index(cat_met)
        file_moyenne = path_moyenne[index_cat]
        file_metrique = path_metrique[index_cat]
    else :
        file_moyenne = "moyenne_metriques.xlsx"
        file_metrique = "metriques.xlsx"

@st.cache_data
def couleur_df(val) :
    color = 'green' if val >= 0 else 'red'
    return f'background-color : {color}'

st.divider()

moyenne = pd.read_excel(f"Tableau métriques/moyenne/{annee}/{choix_data}/{file_moyenne}")
moyenne.rename({moyenne.columns[0] : "Métriques"}, axis = 1, inplace = True)
nb_metrique = st.slider("Nombre de métriques gardées", min_value=0, max_value = moyenne.shape[0], value = moyenne.shape[0])
moyenne_sort = moyenne.loc[moyenne.index[:nb_metrique]]

moyenne_sort = moyenne_sort.style.applymap(couleur_df, subset = ["Diff. Top 5 avec Bottom 15 en %"])

col_df = st.multiselect("Données des métriques à afficher", moyenne.columns, moyenne.columns.tolist())

st.divider()

st.markdown("<p style='text-align: center;'>Tableau des métriques trier par rapport à la différence entre la moyenne du Top 5 et du Bottom 15</p>", unsafe_allow_html=True)
moyenne_sort_df = st.dataframe(moyenne_sort, hide_index=True, on_select = "rerun", selection_mode = "multi-row")

st.divider()

metrique_moyenne = pd.read_excel(f"Tableau métriques/moyenne/{annee}/{choix_data}/{file_metrique}", index_col=0)
metrique_moyenne_sort = metrique_moyenne[moyenne["Métriques"][moyenne_sort_df.selection.rows]]
st.markdown(f"<p style='text-align: center;'>Tableau des métriques retenues, par équipes, en moyenne par match</p>", unsafe_allow_html=True)
st.dataframe(metrique_moyenne_sort)