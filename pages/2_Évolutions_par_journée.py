import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

st.title("Évolutions des métriques au cours des saisons")



col1, col2 = st.columns(2, gap = "Large")

with col1 :
    choix_data = st.radio("Fournisseur data", options = ["Skill Corner", "Stats Bomb"], horizontal = True)

with col2 :
    annee = st.radio("Choisir saison", options = ["2021_2022", "2022_2023", "2023_2024"], horizontal = True)

st.divider()

path_evo = ["physical_", "running_", "pressure_", "passes_"]
liste_cat_met = ["Physiques", "Courses sans ballon avec la possession",
            "Action sous pression", "Passes à un coéquipier effectuant une course"]
cat_met = st.radio("Catégorie de métrique", liste_cat_met, horizontal = True)
index_cat = liste_cat_met.index(cat_met)
file_evo = path_evo[index_cat]

dico_type = {
    "Physiques" : ["tip", "otip", "all"],
    "Courses sans ballon avec la possession" : ["runs_in_behind",
        "runs_ahead_of_the_ball", "support_runs", "pulling_wide_runs", "coming_short_runs", "underlap_runs", "overlap_runs",
        "dropping_off_runs", "pulling_half_space_runs", "cross_receiver_runs"],
    "Action sous pression" : ["low", "medium", "high"],
    "Passes à un coéquipier effectuant une course" : ["runs_in_behind",
        "runs_ahead_of_the_ball", "support_runs", "pulling_wide_runs", "coming_short_runs", "underlap_runs", "overlap_runs",
        "dropping_off_runs", "pulling_half_space_runs", "cross_receiver_runs"]
}
liste_cat_type = st.multiselect("Type de la catégorie", dico_type[cat_met], default = dico_type[cat_met])

st.divider()


evo_équipe = pd.read_excel(f"Métriques discriminantes/Tableau métriques/Evolutions métriques/Par journée/{annee}/Skill Corner/{file_evo}équipe.xlsx", index_col = [0, 1])
evo_journée = pd.read_excel(f"Métriques discriminantes/Tableau métriques/Evolutions métriques/Par journée/{annee}/Skill Corner/{file_evo}journée.xlsx", index_col = 0)

col_keep = [False]*evo_équipe.shape[1]
if cat_met == "Physiques" :
    for cat_type in liste_cat_type :
        col_keep = np.logical_or(col_keep, ["_" + cat_type in i for i in evo_équipe.columns])

else :
    for cat_type in liste_cat_type :
        col_keep = np.logical_or(col_keep, [cat_type in i for i in evo_équipe.columns])

evo_équipe = evo_équipe[evo_équipe.columns[col_keep]]
evo_journée = evo_journée[evo_journée.columns[col_keep]]

choix_métriques = st.multiselect("Métriques gardées", options = evo_journée.columns)
evo_équipe = evo_équipe[choix_métriques].reset_index().set_index("Journée")
evo_journée = evo_journée[choix_métriques]

if st.checkbox("Afficher le tableau des métriques par journée") :
    st.dataframe(evo_journée, on_select = "rerun", selection_mode = "multi-column")

st.divider()

columns = st.columns(2)
with columns[0] :
    if len(choix_métriques) > 0 :
        met_graphe = st.radio("Métrique à afficher sur le graphe", choix_métriques, horizontal = True)

with columns[1] :
    équipe_graphe = st.multiselect("Équipe à afficher sur le graphe (Sélectionner toutes les équipes pour avoir la moyenne du TOP 20)",
                                   evo_équipe.team_name.unique(), default = evo_équipe.team_name.unique().tolist())


if len(équipe_graphe) == len(evo_équipe.team_name.unique().tolist()) :
    st.line_chart(evo_journée[met_graphe])
else :
    st.dataframe(evo_équipe[evo_équipe.team_name.isin(équipe_graphe)].reset_index().set_index(["Journée", "team_name"])[met_graphe].unstack(level = "team_name"))

# def couleur_text_df(col) :
#     color = []
#     for met in evo.index :
#         if col.name == "Évolution en %" :
#             if evo.loc[met, "2023_2024"] >= evo.loc[met, "2022_2023"] and evo.loc[met, "2022_2023"] >= evo.loc[met, "2021_2022"] :
#                 color.append("background-color: rgba(0, 255, 0, 0.3)")
#             elif evo.loc[met, "2023_2024"] >= evo.loc[met, "2022_2023"] and evo.loc[met, "2022_2023"] < evo.loc[met, "2021_2022"] :
#                 color.append("background-color: rgba(0, 0, 255, 0.3)")
#             elif evo.loc[met, "2023_2024"] < evo.loc[met, "2022_2023"] and evo.loc[met, "2022_2023"] >= evo.loc[met, "2021_2022"] :
#                 color.append("background-color: rgba(255, 255, 0, 0.3)")
#             else :
#                 color.append("background-color: rgba(255, 0, 0, 0.3)")
#         else :
#             color.append('')
#     return color

# evo_style = evo.style.apply(couleur_text_df, axis = 0)

# st.divider()

# st.markdown("<p style='text-align: center;'>Tableau de l'évolution de chaque métrique entre la saison 2021/2022 et 2023/2024</p>", unsafe_allow_html=True)
# met_sel = st.dataframe(evo_style, width = 10000, on_select = "rerun", selection_mode = "multi-row")

# with st.columns([1.5, 4, 1])[1] :
#     st.markdown("<p style='text-align: center;'>Code couleur de l'évolution des métriques entre la saison 2021/2022 et 2023/2024 :</p>", unsafe_allow_html=True)

# col1, col2, col3, col4 = st.columns(4)
# with col1 :
#     "Vert : Strictement croissant"
# with col2 :
#     "Bleu : Décroissant puis croissant"
# with col3 :
#     "Jaune : Croissant puis décroissant"
# with col4 :
#     "Rouge : Strictement décroissant"

# st.divider()


# evo_graphe = evo_style.data.iloc[met_sel.selection.rows].drop("Évolution en %", axis = 1)
# new_index = []
# for i in evo_style.index[met_sel.selection.rows] :
#     new_index.append(i[1] + " - " + i[0])
# evo_graphe = evo_graphe.reset_index()
# evo_graphe.index = new_index
# # couleur = (evo_graphe.Top == "Top 5").replace({True : "#FF0000", False : '#0000FF'})
# evo_graphe = evo_graphe.drop(["Métriques", "Top"], axis = 1)
# contain1 = st.container(border = True)
# with contain1 :
#     st.markdown("<p style='text-align: center;'>Graphique de l'évolution des métriques sélectionnées</p>", unsafe_allow_html=True)
#     st.line_chart(evo_graphe.T)