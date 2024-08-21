import streamlit as st

import pandas as pd

from mplsoccer import VerticalPitch

import matplotlib.patches as patches

import numpy as np

import sqlite3

from config_py.variable import path_effect_1, dico_rank_SB, colormapblue, colormapred

from config_py.fonction import label_heatmap, execute_SQL, replace_saison1, replace_saison2, func_change

idx = pd.IndexSlice

st.set_page_config(layout="wide")

st.title("Heatmap des zones de début d'action menant à un tir")
st.divider()


#----------------------------------------------- DÉFINITION DES DICOS ------------------------------------------------------------------------------------


dico_label = {"Choisir Top/Middle/Bottom" : ["du"], "Choisir équipe" : ["de"]}


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Connection BDD


connect = sqlite3.connect("database.db")
cursor = connect.cursor()


#----------------------------------------------- FILTRAGE DES DATAS ------------------------------------------------------------------------------------


columns = st.columns([2, 4, 3], vertical_alignment = "center", gap = "large")

# Choix Compet
params = []
stat = f"SELECT DISTINCT Compet FROM Debut_action"
liste_compet = execute_SQL(cursor, stat, params).fetchall()
liste_compet = [i[0] for i in liste_compet]
    
with columns[0] :
    choix_compet = st.selectbox("Choisir compétition", options = liste_compet, index = 0)

# Choix d'une ou plusieurs saisons sur laquelle/lesquelles on va étudier les métriques pour Skill Corner
params = [choix_compet]
stat = f"SELECT DISTINCT Saison FROM Debut_action WHERE Compet = ?"
liste_saison = execute_SQL(cursor, stat, params).fetchall()
liste_saison = [i[0] for i in liste_saison]

with columns[1] :
    choix_saison = st.multiselect("Choisir saison", replace_saison2(liste_saison), default = replace_saison2(liste_saison))
choix_saison = replace_saison1(choix_saison)

with columns[2] :
    choix_groupe = st.radio("Choix groupe", ["Choisir Top/Middle/Bottom", "Choisir équipe"], label_visibility = "hidden")

# On regarde si au moins une saison est choisie
if len(choix_saison) == 0 :
    st.stop()

st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Création du dataframe en choisissant le type de métrique qu'on souhaite étudier


params = [choix_compet] + choix_saison
stat = f"SELECT * FROM Debut_action WHERE Compet = ? and Saison IN ({', '.join('?' * len(choix_saison))})"
res = execute_SQL(cursor, stat, params)

df = pd.DataFrame(res.fetchall())
df.columns = [i[0] for i in res.description]

df = df.drop(["Compet", "index"], axis = 1).set_index(["Saison", "Équipe"])


#----------------------------------------------- CHOIX GROUPE ------------------------------------------------------------------------------------


liste_équipe = df.index.levels[1]

if choix_groupe == "Choisir Top/Middle/Bottom" :

    df_nb_team = df.reset_index()[["Saison", "Équipe"]].drop_duplicates().groupby("Saison").apply(len)
    max_team = min(df_nb_team)

    df_groupe = pd.DataFrame(0, index = ["Top", "Middle", "Bottom"], columns = ["Taille", "Slider"])
    df_groupe["Slider"] = "Nombre d'équipe dans le " + df_groupe.index

    columns = st.columns(3, gap = "large", vertical_alignment = "center")
    with columns[0] :
        df_groupe.loc["Top", "Taille"] = st.slider(df_groupe.loc["Top", "Slider"], min_value = 1, max_value = max_team, value = 5)
    with columns[1] :
        if df_groupe.loc["Top", "Taille"] == max_team :
            df_groupe.loc["Bottom", "Taille"] = max_team - df_groupe.loc["Top", "Taille"]
            st.write(f"Nombre d'équipe dans le Bottom : {df_groupe.loc['Bottom', 'Taille']}")
        else :
            df_groupe.loc["Bottom", "Taille"] = st.slider(df_groupe.loc["Bottom", "Slider"], min_value = 0,
                                                          max_value = max_team - df_groupe.loc["Top", "Taille"])
    
    nb_middle = df_nb_team - df_groupe.loc["Top", "Taille"] - df_groupe.loc["Bottom", "Taille"]
    df_groupe.loc["Middle", "Taille"] = max(nb_middle)

    with columns[2] :
        groupe_non_vide = df_groupe[df_groupe.Taille > 0].index
        groupe_plot = st.radio("Groupe à afficher", groupe_non_vide.tolist()*(df_groupe.loc["Top", "Taille"] != max_team) + ["Global"],
                               horizontal = True)

else :
    choix_équipe = st.multiselect("Choisir équipe", sorted(liste_équipe))

st.divider()


#----------------------------------------------- FILTRAGE DF ------------------------------------------------------------------------------------


if choix_groupe == "Choisir Top/Middle/Bottom" :
    
    for saison in choix_saison :

        liste_rank = dico_rank_SB[saison]

        df.loc[idx[saison, liste_rank[:df_groupe.loc["Top", "Taille"]]], "Groupe"] = "Top"
        df.loc[idx[saison, liste_rank[df_groupe.loc["Top", "Taille"]:df_groupe.loc["Top", "Taille"] + nb_middle.loc[saison]]], "Groupe"] = "Middle"
        df.loc[idx[saison, liste_rank[df_groupe.loc["Top", "Taille"] + nb_middle.loc[saison]:]], "Groupe"] = "Bottom"
    df = df[df.Groupe == groupe_plot]
    
else :
    df = df.loc[:, choix_équipe, :]


#----------------------------------------------- FILTRAGE HEATMAPS ------------------------------------------------------------------------------------


if len(df) == 0 :
    st.stop()

st.session_state["select_Type_action_deb_action"] = [i for i in st.session_state["Type_action_deb_action"] if i in df.type_action.unique()]
type_action = st.multiselect("Choisir le type de début d'action", options = df.type_action.unique(), on_change = func_change,
                key = "select_Type_action_deb_action", args = ("Type_action_deb_action", "select_Type_action_deb_action"))
df = df[df.type_action.isin(type_action)]

st.divider()

columns = st.columns(2, gap = "large", vertical_alignment = "bottom")

with columns[0] :
    bins_h = st.number_input("Nombre de colonne pour la Heatmap de gauche", min_value = 1, step = 1, value = 5)
    bins_v = st.number_input("Nombre de ligne pour la Heatmap de gauche", min_value = 1, step = 1, value = 10)
    
with columns[1] :
    choix_goal = st.checkbox("Sélectionner uniquement les débuts d'actions menant à un but")

    if choix_goal :
        df = df[df.But]
    
    count_type = st.selectbox("Type de comptage", ["Pourcentage", "Pourcentage sans %", "Valeur", "Aucune valeur"])

if choix_groupe == "Choisir équipe" :
    columns = st.columns(2)

    with columns[0] :
        choix_bins_v = st.number_input("Choisir une ligne", min_value = 0, step = 1, max_value = bins_v)

    with columns[1] :
        choix_bins_h = st.number_input("Choisir une colonne", min_value = 0, step = 1, max_value = bins_h)

    if (choix_bins_h != 0) & (choix_bins_v != 0) :
        df_sort = df[(df.x >= ((120/bins_v)*(choix_bins_v - 1))) &
                        (df.x <= ((120/bins_v)*(choix_bins_v))) &
                        (df.y >= (80/bins_h)*(choix_bins_h - 1)) &
                        (df.y <= (80/bins_h)*(choix_bins_h))]


#----------------------------------------------- AFFICHAGE HEATMAPS ------------------------------------------------------------------------------------


if len(type_action) == 0 :
    st.stop()
    
st.divider()

choix_saison_title = replace_saison2(choix_saison)
choix_saison_title.reverse()
bool_len_grp = (len(choix_saison) > 1)
saison_title = []
saison_title.append(f'la saison {choix_saison_title[0]}')
saison_title.append(f'les saisons {", ".join(choix_saison_title[:-1])} et {choix_saison_title[-1]}')

if choix_groupe == "Choisir Top/Middle/Bottom" :
    bool_len = 0
    grp_title = [f"{groupe_plot} de ligue 2"]
else :
    bool_len = (len(choix_équipe) > 1)
    grp_title = [f'{choix_équipe[0]}', f'{", ".join(choix_équipe[:-1])} et {choix_équipe[-1]}']

st.markdown(f"<p style='text-align: center;'>Heatmap {dico_label[choix_groupe][0]} {grp_title[bool_len]} sur {saison_title[bool_len_grp]}</p>",
                unsafe_allow_html=True)



@st.cache_data
def heatmap_percen(data, bins_h, bins_v, count_type) :
    pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color=None, line_color = "green", axis = True,
        label = True, tick = True, goal_type = "box", linewidth = 1, spot_scale = 0.002)
    fig, ax = pitch.draw(constrained_layout=True, tight_layout=False)
    ax.set_xticks(np.arange(80/(2*bins_h), 80 - 80/(2*bins_h) + 1, 80/bins_h), labels = np.arange(1, bins_h + 1, dtype = int))
    ax.set_yticks(np.arange(120/(2*bins_v), 120 - 120/(2*bins_v) + 1, 120/bins_v),
                labels = np.arange(1, bins_v + 1, dtype = int))
    ax.tick_params(axis = "y", right = False, labelright = False, labelsize = "xx-small")
    ax.spines[:].set_visible(False)
    ax.tick_params(axis = "x", top = False, labeltop = False, labelsize = "xx-small")
    ax.set_xlim(0, 80)
    ax.set_ylim(0, 125)
    fig.set_facecolor("none")
    ax.set_facecolor((1, 1, 1))
    fig.set_edgecolor("none")


    bin_statistic1 = pitch.bin_statistic(data.x, data.y, statistic='count', bins=(bins_v, bins_h),
                                        normalize = "Pourcentage" in count_type)
    
    pitch.heatmap(bin_statistic1, ax = ax, cmap = colormapred, edgecolor='#000000', linewidth = 0.2)

    if count_type != "Aucune valeur" :
        dico_label_heatmap = label_heatmap(bin_statistic1["statistic"])
        dico_label_heatmap = dico_label_heatmap[count_type]
        bin_statistic1["statistic"] = dico_label_heatmap["statistique"]
        str_format = dico_label_heatmap["str_format"]
        pitch.label_heatmap(bin_statistic1, exclude_zeros = True, fontsize = int(50/(bins_v + bins_h)) + 2, color='#f4edf0',
                            ax = ax, ha='center', va='center', str_format=str_format, path_effects=path_effect_1)

    return fig, ax

@st.cache_data
def heatmap_smooth(data) :
    pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color=None, line_color = "green",
                        goal_type = "box", linewidth = 1, spot_scale = 0.002)
    fig, ax = pitch.draw(constrained_layout=True, tight_layout=False)
    fig.set_facecolor("none")
    ax.set_xlim([0, 87])
    ax.set_ylim([0, 125])
    ax.set_facecolor((1, 1, 1))
    fig.set_edgecolor("none")
    pitch.kdeplot(data.x, data.y, ax = ax, fill = True, levels = 100, thresh = 0, cmap = colormapblue)
    return fig, ax




col1, col2 = st.columns(2)
with col1 :
    fig1, ax1 = heatmap_percen(df, bins_h, bins_v, count_type)
    if choix_groupe == "Choisir équipe" and (choix_bins_h != 0) & (choix_bins_v != 0) :
        rect = patches.Rectangle(((80/bins_h)*(choix_bins_h - 1), (120/bins_v)*(choix_bins_v - 1)),
                                80/bins_h, 120/bins_v, linewidth=4, edgecolor='r', facecolor='r', alpha=0.8)
        ax1.add_patch(rect)            
    st.pyplot(fig1)
with col2 :
    fig2, ax2 = heatmap_smooth(df)
    st.pyplot(fig2)


liste_goal_label = ["tirs", "buts"]
st.markdown(f"<p style='text-align: center;'>Nombre total de {liste_goal_label[choix_goal]} : {len(df)}</p>",
                unsafe_allow_html=True)

if choix_groupe == "Choisir équipe" and choix_bins_h > 0 and choix_bins_v > 0 and len(df_sort) > 0  :
    df_sort.reset_index(inplace = True)

    df_sort[["match_date", "match_week", "home_team", "away_team", "minute", "Équipe"]]
    st.dataframe(df_sort.reset_index()[["match_date", "match_week", "home_team", "away_team", "minute", "Équipe"]],
                    hide_index = True)