import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("Évolutions des métriques au cours des journées")


#----------------------------------------------- DÉFINITIONS DES DICTIONNAIRES ------------------------------------------------------------------------------------


dico_met = {
    "Physiques" : ["physical",
        {"30 min. tip" : "_per30tip", "30 min. otip" : "_per30otip", "Match all possession" : "_per_Match"}],

    "Courses sans ballon avec la possession" : ["running",
        {"Match" : "per_match", "100 runs" : "per_100_runs", "30 min. tip" : "per_30_min_tip"},
        ["runs_in_behind", "runs_ahead_of_the_ball", "support_runs", "pulling_wide_runs", "coming_short_runs", "underlap_runs",
        "overlap_runs", "dropping_off_runs", "pulling_half_space_runs", "cross_receiver_runs"],
        "Type de course"],

    "Action sous pression" : ["pressure",
        {"Match" : "per_match", "100 pressures" : "per_100_pressures", "30 min. tip" : "per_30_min_tip"},
        ["low", "medium", "high"],
        "Intensité de pression"],

    "Passes à un coéquipier effectuant une course" : ["passes",
        {"Match" : "per_match", "100 passes opportunities" : "_per_100_pass_opportunities", "30 min. tip" : "per_30_min_tip"},
        ["runs_in_behind", "runs_ahead_of_the_ball", "support_runs", "pulling_wide_runs", "coming_short_runs", "underlap_runs",
        "overlap_runs", "dropping_off_runs", "pulling_half_space_runs", "cross_receiver_runs"],
        "Type de course"]
    }

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



columns = st.columns([2, 4, 2, 3])

with columns[0] :
    annee = st.radio("Choisir saison", options = ["2023/2024", "2022/2023", "2021/2022"], horizontal = True)
    annee = annee.replace("/", "_")
    liste_équipe = dico_rank[annee]

with columns[1] :
    cat_met = st.radio("Catégorie de métrique", dico_met.keys(), horizontal = True)

with columns[2] :
    moy_met = st.radio("Moyenne de la métrique", dico_met[cat_met][1].keys())

with columns[3] :
    choix_groupe = st.radio("Choix groupe", ["Choisir Top/Middle/Bottom", "Choisir équipe"], label_visibility = "hidden")


#----------------------------------------------- IMPORTATION DATAFRAME ------------------------------------------------------------------------------------

@st.cache_data
def import_df(annee_df, cat_met_df) :
    return pd.read_excel(f"Métriques discriminantes/Tableau métriques/Evolutions métriques/Par journée/{annee_df}/Skill Corner/{dico_met[cat_met_df][0]}_équipe.xlsx", index_col = [0, 1])

df = import_df(annee, cat_met)
df = df[df.columns[[(dico_met[cat_met][1][moy_met] in i) or ("ratio" in i) for i in df.columns]]]

#----------------------------------------------- CHOIX MÉTRIQUE ------------------------------------------------------------------------------------


st.divider()

if cat_met != "Physiques" :
    columns = st.columns([1, 2])

    with columns[0] :
        type_met = st.selectbox(dico_met[cat_met][3], dico_met[cat_met][2])
        df = df[df.columns[[type_met in i for i in df.columns]]]
    with columns[1] :
        choix_metrique = st.selectbox("Choisir la métrique", df.columns)

else :
    choix_metrique = st.selectbox("Choisir la métrique", df.columns)


#----------------------------------------------- CHOIX GROUPES ------------------------------------------------------------------------------------


st.divider()

if choix_groupe == "Choisir Top/Middle/Bottom" :

    df_groupe = pd.DataFrame(0, index = ["Top", "Middle", "Bottom"], columns = ["Taille", "Slider"])
    df_groupe["Slider"] = "Nombre d'équipe dans le " + df_groupe.index

    columns = st.columns(4, gap = "large", vertical_alignment = "center")
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

    with columns[3] :
        groupe_non_vide = df_groupe[df_groupe.Taille > 0].index
        groupe_plot = st.multiselect("Groupe à afficher", groupe_non_vide)
 
    dico_df_groupe = {}
    dico_df_groupe["Top"] = df.loc[:, liste_équipe[:df_groupe.loc["Top", "Taille"]], :].groupby("Journée").mean()
    if df_groupe.loc["Middle", "Taille"] > 0 :
        dico_df_groupe["Middle"] = df.loc[:, liste_équipe[df_groupe.loc["Top", "Taille"]:df_groupe.loc["Top", "Taille"] + df_groupe.loc["Middle", "Taille"]], :].groupby("Journée").mean()
    if df_groupe.loc["Bottom", "Taille"] > 0 :
        dico_df_groupe["Bottom"] = df.loc[:, liste_équipe[df_groupe.loc["Top", "Taille"] + df_groupe.loc["Middle", "Taille"]:], :].groupby("Journée").mean()

else :
    choix_équipe = st.multiselect("Choisir équipe", liste_équipe)
    df = df.loc[:, choix_équipe, :]
    df = df.reset_index().pivot(index = "Journée", columns = "team_name", values = choix_metrique)



#----------------------------------------------- AFFICHAGE GRAPHIQUE ------------------------------------------------------------------------------------


st.divider()

fig = plt.figure(figsize = (8, 4))



if choix_groupe == "Choisir équipe" :

    plt.plot(df, marker = "o", markersize = 3, linewidth = 0.7)

    plt.title(f"Graphe des équipes sélectionnées pour la métrique {choix_metrique}\nau cours des journées de la saison {annee.replace("_", "/")}",
            fontweight = "heavy", y = 1.05, fontsize = 9)
    plt.legend(choix_équipe, bbox_to_anchor=(0.5, -0.25), fontsize = "small", ncol = 2)


else :
    for groupe in groupe_plot :
        plt.plot(dico_df_groupe[groupe][choix_metrique], marker = "o", markersize = 3, linewidth = 0.7)
    plt.title(f"Graphe des groupes sélectionnés pour la métrique {choix_metrique}\nau cours des journées de la saison {annee.replace("_", "/")}",
            fontweight = "heavy", y = 1.05, fontsize = 9)
    plt.legend(groupe_plot, bbox_to_anchor=(0.5, -0.25), fontsize = "small", ncol = 2)


plt.grid()

plt.xlabel("Journée", fontsize = "small", fontstyle = "italic", labelpad = 10)
plt.ylabel("Métrique", fontsize = "small", fontstyle = "italic", labelpad = 10)

plt.tick_params(labelsize = 8)
ax = plt.gca()
ax.spines[:].set_visible(False)

st.pyplot(fig)