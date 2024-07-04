import streamlit as st
import pandas as pd
import numpy as np

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


evo = pd.read_excel(f"Tableau métriques/Evolutions métriques/{file_evo}", index_col = [0, 1])

def couleur_text_df(col) :
    color = []
    for met in evo.index :
        if col.name == "Évolution en %" :
            if evo.loc[met, "2023_2024"] >= evo.loc[met, "2022_2023"] and evo.loc[met, "2022_2023"] >= evo.loc[met, "2021_2022"] :
                color.append("background-color: green")
            elif evo.loc[met, "2023_2024"] >= evo.loc[met, "2022_2023"] and evo.loc[met, "2022_2023"] < evo.loc[met, "2021_2022"] :
                color.append("background-color: blue")
            elif evo.loc[met, "2023_2024"] < evo.loc[met, "2022_2023"] and evo.loc[met, "2022_2023"] >= evo.loc[met, "2021_2022"] :
                color.append("background-color: yellow")
            else :
                color.append("background-color: red")
        else :
            color.append('')
    return color

evo_style = evo.style.apply(couleur_text_df, axis = 0)

st.divider()

st.markdown("<p style='text-align: center;'>Tableau de l'évolutions de chaque métriques entre la saison 2021/2022 et 2023/2024</p>", unsafe_allow_html=True)
met_sel = st.dataframe(evo_style, width = 10000, on_select = "rerun", selection_mode = "multi-row")

col1, col2, col3, col4 = st.columns(4)
with col1 :
    "Vert : Strictement croissant"
with col2 :
    "Bleu : Décroissant puis croissant"
with col3 :
    "Jaune : Croissant puis décroissant"
with col4 :
    "Rouge : Strictement décroissant"

st.divider()
st.markdown("<p style='text-align: center;'>Graphique de l'évolution des métriques sélectionnées</p>", unsafe_allow_html=True)

evo_graphe = evo_style.data.iloc[met_sel.selection.rows].drop("Évolution en %", axis = 1)
new_index = []
for i in evo_style.index[met_sel.selection.rows] :
    new_index.append(i[1] + " - " + i[0])
evo_graphe = evo_graphe.reset_index()
evo_graphe.index = new_index
# couleur = (evo_graphe.Top == "Top 5").replace({True : "#FF0000", False : '#0000FF'})
evo_graphe = evo_graphe.drop(["Métriques", "Top"], axis = 1)
st.line_chart(evo_graphe.T)