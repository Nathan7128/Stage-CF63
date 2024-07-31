import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout = "wide")

idx = pd.IndexSlice

st.title("Évolutions des métriques au cours des journées")
st.divider()

#----------------------------------------------- DÉFINITIONS DES DICTIONNAIRES ------------------------------------------------------------------------------------

def func_change(key1, key2) :
    st.session_state[key1] = st.session_state[key2]

groupe_plot = []

groupe_non_vide = []

choix_équipe = []

dico_met = {
    "Physiques" : ["physical.xlsx",
        {"30 min. tip" : "_per30tip", "30 min. otip" : "_per30otip", "Match all possession" : "_per_Match"}],

    "Courses sans ballon avec la possession" : ["running.xlsx",
        {"Match" : "per_match", "100 runs" : "per_100_runs", "30 min. tip" : "per_30_min_tip"},
        ["runs_in_behind", "runs_ahead_of_the_ball", "support_runs", "pulling_wide_runs", "coming_short_runs", "underlap_runs",
        "overlap_runs", "dropping_off_runs", "pulling_half_space_runs", "cross_receiver_runs"],
        "Type de course"],

    "Action sous pression" : ["pressure.xlsx",
        {"Match" : "per_match", "100 pressures" : "per_100_pressures", "30 min. tip" : "per_30_min_tip"},
        ["low", "medium", "high"],
        "Intensité de pression"],

    "Passes à un coéquipier effectuant une course" : ["passes.xlsx",
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
    saison = st.radio("Choisir saison", options = ["2023/2024", "2022/2023", "2021/2022"], horizontal = True)
    saison = saison.replace("/", "_")
    liste_équipe = dico_rank[saison]

with columns[1] :
    func_change("select_cat_met", "cat_met")
    cat_met = st.radio("Catégorie de métrique", dico_met.keys(), horizontal = True, key = 'select_cat_met',
                        on_change = func_change, args = ("cat_met", "select_cat_met"))

with columns[2] :
    moy_met = st.radio("Moyenne de la métrique", dico_met[cat_met][1].keys())

with columns[3] :
    ""
    choix_groupe_équipe = st.checkbox("Sélectionner équipe", value = False)
    choix_groupe_top = st.checkbox("Sélectionner Top/Middle/Bottom", value = False)
    win_met = st.checkbox("Métriques pour les équipes qui gagnent les matchs")


#----------------------------------------------- IMPORTATION DATAFRAME ------------------------------------------------------------------------------------

@st.cache_data
def import_df(saison_df, cat_met_df) :
    return pd.read_excel(f"Métriques discriminantes/Tableau métriques/{saison_df}/Skill Corner/{dico_met[cat_met_df][0]}", index_col = [0, 1])

df = import_df(saison, cat_met)

df

if win_met :
    df = df[df.result == "win"]

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

df = df[choix_metrique]


#----------------------------------------------- CHOIX GROUPES ------------------------------------------------------------------------------------

if choix_groupe_top :
    st.divider()
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

if choix_groupe_équipe :
    st.divider()
    choix_équipe = st.multiselect("Choisir équipe", liste_équipe)


#----------------------------------------------- FILTRAGE DATAFRAME GROUPE ------------------------------------------------------------------------------------


df_final = pd.DataFrame(index = df.index.levels[0])

if "Top" in groupe_plot :
    df_final["Top"] = df.loc[:, liste_équipe[:df_groupe.loc["Top", "Taille"]], :].groupby("Journée").mean()
if "Middle" in groupe_plot :
    df_final["Middle"] = df.loc[:, liste_équipe[df_groupe.loc["Top", "Taille"]:df_groupe.loc["Top", "Taille"] + df_groupe.loc["Middle", "Taille"]], :].groupby("Journée").mean()
if "Bottom" in groupe_plot :
    df_final["Bottom"] = df.loc[:, liste_équipe[df_groupe.loc["Top", "Taille"] + df_groupe.loc["Middle", "Taille"]:], :].groupby("Journée").mean()

for équipe in choix_équipe :
    df_final[équipe] = df.loc[:, équipe, :]


#----------------------------------------------- AFFICHAGE GRAPHIQUE ------------------------------------------------------------------------------------

if len(groupe_plot) + len(choix_équipe) > 0 :

    st.divider()

    fig = plt.figure(figsize = (8, 4))

    plt.plot(df_final, marker = "o", markersize = 3, linewidth = 0.7)

    bool_len_grp = len(df_final.columns) > 1
    grp_title = []
    grp_title.append(f'{df_final.columns[0]}')
    grp_title.append(f'{", ".join(df_final.columns[:-1])} et {df_final.columns[-1]}')
    plt.title(f"Graphe de la métrique {choix_metrique}\npour{' le'*(len(groupe_plot) > 0)} {grp_title[bool_len_grp]} \nau cours des journées de la saison {saison.replace('_', '/')}",
                fontweight = "heavy", y = 1.05, fontsize = 9)
    plt.legend(df_final.columns, bbox_to_anchor=(0.5, -0.25), fontsize = "small", ncol = 2)

    plt.grid()

    plt.xlabel("Journée", fontsize = "small", fontstyle = "italic", labelpad = 10)
    plt.ylabel(choix_metrique, fontsize = "small", fontstyle = "italic", labelpad = 10)
    plt.xticks(np.arange(1, df.index.levels[0][-1], 3))

    plt.tick_params(labelsize = 8)
    ax = plt.gca()
    ax.spines[:].set_visible(False)

    st.pyplot(fig)