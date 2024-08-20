import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from config_py.fonction import func_change
from config_py.variable import dico_type, dico_rank_SK


st.set_page_config(layout = "wide")

idx = pd.IndexSlice

st.title("Évolution des métriques au cours des journées")
st.divider()

groupe_plot = []

groupe_non_vide = []

choix_équipe = []

#----------------------------------------------- CHOIX SAISON ET MÉTRIQUE ------------------------------------------------------------------------------------


columns = st.columns([2, 4, 2, 3])

with columns[0] :
    saison = st.radio("Choisir saison", options = ["2023/2024", "2022/2023", "2021/2022"], horizontal = True)
    saison = saison.replace("/", "_")
    liste_équipe = dico_rank_SK[saison]

with columns[1] :
    func_change("select_cat_met", "cat_met")
    cat_met = st.radio("Catégorie de métrique", dico_type.keys(), horizontal = True, key = 'select_cat_met',
                        on_change = func_change, args = ("cat_met", "select_cat_met"))

with columns[2] :
    moy_met = st.radio("Moyenne de la métrique", dico_type[cat_met][1].keys())

with columns[3] :
    ""
    choix_groupe_équipe = st.checkbox("Sélectionner équipe", value = False)
    choix_groupe_top = st.checkbox("Sélectionner Top/Middle/Bottom", value = False)
    win_met = st.checkbox("Métriques pour les équipes qui gagnent les matchs")


#----------------------------------------------- IMPORTATION DATAFRAME ------------------------------------------------------------------------------------

@st.cache_data
def import_df(saison_df, cat_met_df) :
    return pd.read_excel(f"Métriques discriminantes/Tableau métriques/{saison_df}/Skill Corner/{dico_type[cat_met_df][0]}", index_col = [0, 1])

df = import_df(saison, cat_met)

if win_met :
    df = df[df.result == "win"]

df = df[df.columns[[(dico_type[cat_met][1][moy_met] in i) or ("ratio" in i) for i in df.columns]]]

#----------------------------------------------- CHOIX MÉTRIQUE ------------------------------------------------------------------------------------


st.divider()

if cat_met != "Physiques" :
    columns = st.columns([1, 2])

    with columns[0] :
        type_met = st.selectbox(dico_type[cat_met][2], dico_type[cat_met][3])
        type_met = dico_type[cat_met][3][type_met]
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