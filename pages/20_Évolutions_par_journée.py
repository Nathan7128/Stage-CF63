import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("Évolutions des métriques au cours des saisons")

dico_met = {
    "Physiques" : ["physical", {"30 min. tip" : "_per30tip", "30 min. otip" : "_per30otip",
        "Match all possession" : "_per_Match"}],
    "Courses sans ballon avec la possession" : ["running", {"Match" : "per_match",
        "100 runs" : "per_100_runs", "30 min. tip" : "per_30_min_tip"}, ["runs_in_behind", "runs_ahead_of_the_ball",
        "support_runs", "pulling_wide_runs", "coming_short_runs", "underlap_runs", "overlap_runs", "dropping_off_runs",
        "pulling_half_space_runs", "cross_receiver_runs"]],
    "Action sous pression" : ["pressure", {"Match" : "per_match",
        "100 pressures" : "per_100_pressures", "30 min. tip" : "per_30_min_tip"}, ["low", "medium", "high"]],
    "Passes à un coéquipier effectuant une course" : ["passes", {"Match" : "per_match",
        "100 passes opportunities" : "_per_100_pass_opportunities", "30 min. tip" : "per_30_min_tip"}, ["runs_in_behind",
        "runs_ahead_of_the_ball", "support_runs", "pulling_wide_runs", "coming_short_runs", "underlap_runs", "overlap_runs",
        "dropping_off_runs", "pulling_half_space_runs", "cross_receiver_runs"]]
    }


dico_top = {
    "Moyenne Top 5" : [["top5"], 0],
    "Moyenne Bottom 15" : [["bottom15"], 0],
    "Moyenne Top 5 & Bottom 15" : [["top5", "bottom15"], 0],
    "Moyenne globale" : [["top20"], 0],
    "Choisir équipe" : [["équipe"], [0, 1]]
}


columns = st.columns([1, 2, 1, 1], gap = "large")

with columns[0] :
    annee = st.radio("Choisir saison", options = ["2021_2022", "2022_2023", "2023_2024"])

with columns[1] :
    cat_met = st.radio("Catégorie de métrique", dico_met.keys(), horizontal = True)

with columns[2] :
    moy_met = st.radio("Moyenne de la métrique", dico_met[cat_met][1].keys())

with columns[3] :
    choix_top = st.radio("Groupe à afficher sur le graphe", dico_top.keys())

st.divider()


liste_df = []
for groupe_df in dico_top[choix_top][0] :
    df_import = pd.read_excel(f"Métriques discriminantes/Tableau métriques/Evolutions métriques/Par journée/{annee}/Skill Corner/{dico_met[cat_met][0]}_{groupe_df}.xlsx", index_col = dico_top[choix_top][1])
    liste_df.append(df_import)

for i in range (len(liste_df)) :
    liste_df[i] = liste_df[i][liste_df[i].columns[[(dico_met[cat_met][1][moy_met] in i) or ("ratio" in i) for i in liste_df[i].columns]]]

if cat_met != "Physiques" :
    type_met = st.radio("Type de la métrique", dico_met[cat_met][2], horizontal = True)
    for i in range (len(liste_df)) :
        liste_df[i] = liste_df[i][liste_df[i].columns[[(type_met in i) or ("ratio" in i and type_met in i) for i in liste_df[i].columns]]]

    st.divider()

choix_metrique = st.selectbox("Choisir la métrique", liste_df[0].columns)

équipe_graphe = []

if choix_top == "Choisir équipe" :
    df = liste_df[0]
    équipe_graphe = st.multiselect("Équipe à afficher sur le graphe", df.index.levels[1])
    liste_df = []
    for team in équipe_graphe :
        liste_df.append(df.loc[:, team, :])

dico_graphe = {
    "Moyenne Top 5" : [f"Graphe du Top 5 de Ligue 2 pour la métrique {choix_metrique}\nau cours des journées de la saison {annee}", 0],
    "Moyenne Bottom 15" : [f"Graphe du Bottom 15 de Ligue 2 pour la métrique {choix_metrique}\nau cours des journées de la saison {annee}", 0],
    "Moyenne Top 5 & Bottom 15" : [f"Graphe du Top 5 et Bottom 15 pour la métrique {choix_metrique}\nau cours des journées de la saison {annee}",
                                   ["Top 5", "Bottom 15"]],
    "Moyenne globale" : [f"Graphe des 20 équipes de Ligue 2 pour la métrique {choix_metrique}\nau cours des journées de la saison {annee}", 0],
    "Choisir équipe" : [f"Graphe des équipes sélectionnées pour la métrique {choix_metrique}\nau cours des journées de la saison {annee}", équipe_graphe]
}

title_graphe = dico_graphe[choix_top][0]
legend_graphe = dico_graphe[choix_top][1]

st.divider()

fig = plt.figure()
for df in liste_df :
    plt.plot(df[choix_metrique], linewidth = 0.7)
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