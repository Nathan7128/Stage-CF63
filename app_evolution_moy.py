import streamlit as st
import pandas as pd

st.set_page_config(page_title= "Évolution des métriques pour les clubs de Ligue 2", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

col1, col2 = st.columns(2)

with col1 :
    choix_data = st.radio("Fournisseur data", options = ["Skill Corner", "Stats Bomb"])

with col2 :
    if choix_data == "Skill Corner" :
        path_evo = ["evo_physical.xlsx", "evo_running.xlsx", "evo_pressure.xlsx", "evo_passes.xlsx"]
        liste_cat_met = ["Physiques", "Courses sans ballon avec la possession",
                    "Action sous pression", "Passes à un coéquipier effectuant une course"]
        cat_met = st.radio("Catégorie de métrique", liste_cat_met)
        index_cat = liste_cat_met.index(cat_met)
        file_evo = path_evo[index_cat]
    else :
        file_evo = "evo_SB.xlsx"


evo = pd.read_excel(f"Tableau métriques/Evolutions métriques/{file_evo}")
evo.rename({evo.columns[0] : "Métriques"}, axis = 1, inplace = True)

st.divider()

st.markdown("<p style='text-align: center;'>Tableau de l'évolutions de chaque métriques entre la saison 2021/2022 et 2023/2024</p>", unsafe_allow_html=True)
st.dataframe(evo, hide_index=True, width = 10000)