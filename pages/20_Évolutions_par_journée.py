import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("Évolutions des métriques au cours des saisons")

idx = pd.IndexSlice

col1, col2 = st.columns(2, gap = "Large")

with col1 :
    choix_data = st.radio("Fournisseur data", options = ["Skill Corner"], horizontal = True)

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

if len(liste_cat_type) > 0 :

    st.divider()


    evo_équipe = pd.read_excel(f"Métriques discriminantes/Tableau métriques/Evolutions métriques/Par journée/{annee}/Skill Corner/{file_evo}équipe.xlsx", index_col = [0, 1])

    col_keep = [False]*evo_équipe.shape[1]
    if cat_met == "Physiques" :
        for cat_type in liste_cat_type :
            col_keep = np.logical_or(col_keep, ["_" + cat_type in i for i in evo_équipe.columns])

    else :
        for cat_type in liste_cat_type :
            col_keep = np.logical_or(col_keep, [cat_type in i for i in evo_équipe.columns])

    evo_équipe = evo_équipe[evo_équipe.columns[col_keep]]

    columns = st.columns(2)
    with columns[0] :
        met_graphe = st.selectbox("Métrique à afficher sur le graphe", evo_équipe.columns)

    with columns[1] :
        choix_groupe = st.selectbox("Groupe à afficher sur le graphe", options = ["Moyenne Top 5", "Moyenne Bottom 15", "Moyenne Top 5 & Bottom 15", "Moyenne globale", "Choisir équipe"])

    st.divider()

    liste_graphe = []

    if choix_groupe == "Choisir équipe" :
        équipe_graphe = st.multiselect("Équipe à afficher sur le graphe", evo_équipe.index.levels[1])
        evo_équipe = evo_équipe.loc[idx[:, équipe_graphe], met_graphe]
        for team in équipe_graphe :
            liste_graphe.append(evo_équipe.loc[:, team, :])
        title_graphe = f"Graphe des équipes sélectionnées pour la métrique {met_graphe}\nau cours des journées de la saison {annee}"
        legend_graphe = équipe_graphe

    elif choix_groupe == "Moyenne Top 5 & Bottom 15" :
        top5_import = pd.read_excel(f"Métriques discriminantes/Tableau métriques/Evolutions métriques/Par journée/{annee}/Skill Corner/{file_evo}top5.xlsx", index_col = 0)
        bottom15_import = pd.read_excel(f"Métriques discriminantes/Tableau métriques/Evolutions métriques/Par journée/{annee}/Skill Corner/{file_evo}bottom15.xlsx", index_col = 0)

        top5 = top5_import[met_graphe]
        bottom15 = bottom15_import[met_graphe]
        liste_graphe = [top5, bottom15]
        legend_graphe = ["top5", "bottom15"]
        title_graphe = f"Graphe du Top 5 et Bottom 15 pour la métrique {met_graphe}\nau cours des journées de la saison {annee}"

    else :
        dico_groupe = {"Moyenne Top 5" : "top5", "Moyenne Bottom 15" : "bottom15", "Moyenne globale" : "top20"}
        evo_journée = pd.read_excel(f"Métriques discriminantes/Tableau métriques/Evolutions métriques/Par journée/{annee}/Skill Corner/{file_evo}{dico_groupe[choix_groupe]}.xlsx", index_col = 0)
        evo_journée = evo_journée[met_graphe]
        liste_graphe.append(evo_journée)
        legend_graphe = 0
        title_graphe = f"Graphe du {choix_groupe} de Ligue 2 pour la métrique {met_graphe}\nau cours des journées de la saison {annee}"

    fig = plt.figure(figsize = (6, 3))
    for graphe in liste_graphe :
        plt.plot(graphe, linewidth = 0.7)
    plt.title(title_graphe, fontweight = "heavy", y = 1.05, fontsize = 9)
    plt.grid()
    if legend_graphe :
        plt.legend(legend_graphe, bbox_to_anchor=(0.5, -0.25), fontsize = "small", ncol = 2)
    plt.xlabel("Journée", fontsize = "small", fontstyle = "italic", labelpad = 10)
    plt.ylabel("Métrique", fontsize = "small", fontstyle = "italic", labelpad = 10)
    plt.tick_params(labelsize = 8)
    ax = plt.gca()
    ax.spines[:].set_visible(False)
    st.pyplot(fig)