# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Importation des librairies


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from functools import partial

from fonction import execute_SQL, load_session_state, key_widg, init_session_state, filtre_session_state, push_session_state, get_session_state
from variable import dico_rank_SB, df_taille_groupe

# Index slicer pour la sélection de donnée sur les dataframes avec multi-index
idx = pd.IndexSlice


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Connection BDD


connect = sqlite3.connect("database.db")
cursor = connect.cursor()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Mise en page de la page


st.set_page_config(layout="wide")

st.title("Moyenne du nombre de passe avant un but d'une compétition")

st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Définition des fonctions de mofication du session state


load_session_state = partial(load_session_state, suffixe = "_nb_passe")
key_widg = partial(key_widg, suffixe = "_nb_passe")
get_session_state = partial(get_session_state, suffixe = "_nb_passe")
init_session_state = partial(init_session_state, suffixe = "_nb_passe")
push_session_state = partial(push_session_state, suffixe = "_nb_passe")
filtre_session_state = partial(filtre_session_state, suffixe = "_nb_passe")


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Choix de la compétition et de la ou des saisons


columns = st.columns([1, 2], vertical_alignment = "center", gap = "large")

params = []
stat = f"SELECT DISTINCT Compet FROM Passes_avant_un_but"
liste_compet, desc = execute_SQL(cursor, stat, params)
liste_compet = [i[0] for i in liste_compet]
    
with columns[0] :
    load_session_state("compet")
    choix_compet = st.selectbox("Choisir compétition", options = liste_compet, **key_widg("compet"))

params = [choix_compet]
stat = f"SELECT DISTINCT Saison FROM Passes_avant_un_but WHERE Compet = ?"
liste_saison, desc = execute_SQL(cursor, stat, params)
liste_saison = [i[0] for i in liste_saison]

with columns[1] :
    init_session_state("saison", [max(liste_saison)])
    load_session_state("saison")
    choix_saison = st.multiselect("Choisir saison", liste_saison, **key_widg("saison"))

if len(choix_saison) == 0 :
    st.stop()

st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Importation du dataframe après avoir effectuer les choix pour le filtrage des données


params = [choix_compet] + choix_saison
stat = f"SELECT * FROM Passes_avant_un_but WHERE Compet = ? and Saison IN ({', '.join('?' * len(choix_saison))})"
res, desc = execute_SQL(cursor, stat, params)

df = pd.DataFrame(res)
df.columns = [i[0] for i in desc]
df = df.drop(["Compet", "index"], axis = 1).set_index(["Saison", "team"])


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Choix de la taille des groupes à étudier


df_nb_team = df.reset_index()[["Saison", "team"]].drop_duplicates().groupby("Saison").apply(len)

max_nb_team = min(df_nb_team)

columns = st.columns(2, gap = "large", vertical_alignment = "center")

with columns[0] :
    load_session_state("nb_top")
    df_taille_groupe.loc["Top", "Taille"] = st.slider(df_taille_groupe.loc["Top", "Slider"], min_value = 1, max_value = max_nb_team,
                                                      **key_widg("nb_top"))
    
with columns[1] :
    if df_taille_groupe.loc["Top", "Taille"] == max_nb_team :
        push_session_state("nb_bottom", max_nb_team - df_taille_groupe.loc["Top", "Taille"])

    else :
        push_session_state("nb_bottom", min(max_nb_team - df_taille_groupe.loc["Top", "Taille"], get_session_state("nb_bottom")))
        load_session_state("nb_bottom")
        st.slider(df_taille_groupe.loc["Bottom", "Slider"], min_value = 0,
                max_value = max_nb_team - df_taille_groupe.loc["Top", "Taille"], **key_widg("nb_bottom"))
        
    df_taille_groupe.loc["Bottom", "Taille"] = get_session_state("nb_bottom")
        
df_taille_groupe.loc["Middle", "Taille"] = max_nb_team - df_taille_groupe.loc["Top", "Taille"] - df_taille_groupe.loc["Bottom", "Taille"]

groupe_non_vide = df_taille_groupe[df_taille_groupe.Taille > 0].index.tolist()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Filtre des types de début d'action souhaités


st.divider()

liste_type_action = df.type_action.unique().tolist()

filtre_session_state("type_action", liste_type_action)
load_session_state("type_action")
type_action = st.multiselect("Choisir le type de début d'action", options = liste_type_action, **key_widg("type_action"))

if len(type_action) == 0 :
    st.stop()

df = df[df.type_action.isin(type_action)][['Passe']].groupby(level = [0, 1], sort = False)

nb_but = df.size()
df = df.sum().divide(nb_but, axis = 0)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Attribution des groupes d'équipes au dataframe


for saison in choix_saison :
    liste_rank = dico_rank_SB[saison]

    df.loc[idx[saison, liste_rank[:df_nb_team[saison] - df_taille_groupe.loc["Middle", "Taille"] - df_taille_groupe.loc["Bottom", "Taille"]]], "Groupe"] = "Top"
    df.loc[idx[saison, liste_rank[df_nb_team[saison] - df_taille_groupe.loc["Middle", "Taille"] - df_taille_groupe.loc["Bottom", "Taille"]:df_nb_team[saison] - df_taille_groupe.loc["Bottom", "Taille"]]], "Groupe"] = "Middle"
    df.loc[idx[saison, liste_rank[df_nb_team[saison] - df_taille_groupe.loc["Bottom", "Taille"]:]], "Groupe"] = "Bottom"


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Choix des groupes/équipes à afficher


st.divider()

columns = st.columns([1, 2], vertical_alignment = "center", gap = "large")

with columns[0] :
    init_session_state("groupe", groupe_non_vide)
    filtre_session_state("groupe", groupe_non_vide)
    load_session_state("groupe")
    choix_groupe = st.multiselect("Groupe à afficher", groupe_non_vide, **key_widg("groupe"))

with columns[1] :
    liste_équipe = sorted(df.index.levels[1].tolist())

    filtre_session_state("équipe", liste_équipe)
    load_session_state("équipe")
    choix_équipe = st.multiselect("Équipe à afficher", liste_équipe, **key_widg("équipe"))


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Création et affichage du dataframe final


df.set_index("Groupe", append = True, inplace = True)

df_final_groupe = df["Passe"].groupby(level = [0, 2]).mean().unstack().round(2)
df_final_équipe = df["Passe"].groupby(level = [0, 1]).mean().unstack().round(2)

df_final = pd.concat([df_final_groupe, df_final_équipe], axis = 1)[choix_groupe + choix_équipe]

if df_final.shape[1] == 0 :
    st.stop()

st.divider()

st.markdown(f"<p style='text-align: center;'>Tableau du nombre de passe avant un but</p>", unsafe_allow_html=True)

row_select_saison = st.dataframe(df_final.fillna("x"), on_select = "rerun", selection_mode = ["multi-row"]).selection.rows


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Affichage de l'évolution du nombre de passe pour les groupes/équipes sélectionnées


if len(choix_saison) > 1 :
    st.divider()

    fig = plt.figure()

    plt.plot(df_final, marker = "+", linewidth = 1)

    plt.grid()

    bool_taille_grp = df_final.shape[1] > 1
    grp_title = []
    grp_title.append(f'{df_final.columns[0]}')
    grp_title.append(f'{", ".join(df_final.columns[:-1])} et {df_final.columns[-1]}')
    plt.title(f"Graphe du nombre de passe avant un but\npour{' le'*(len(choix_groupe) > 0)} {grp_title[bool_taille_grp]}",
                fontweight = "heavy", y = 1.05, fontsize = 9)

    plt.legend(df_final.columns, bbox_to_anchor=(0.75, -0.25), fontsize = "small", ncol = 3)

    plt.xlabel("Saison", fontsize = "small", fontstyle = "italic", labelpad = 10)
    plt.ylabel("Passes", fontsize = "small", fontstyle = "italic", labelpad = 10)
    plt.tick_params(labelsize = 8)

    ax = plt.gca()
    ax.spines[:].set_visible(False)

    st.pyplot(fig)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Affichage des nombres de passe pour chaque saison sélectionnée


nb_saison_select = len(row_select_saison)

if nb_saison_select == 0 :
    st.stop()

df.reset_index(level = 2, drop = True, inplace = True)

st.divider()

st.markdown(f"<p style='text-align: center;'>Tableau du nombre de passes avant un but lors de la saison</p>", unsafe_allow_html=True)
""

columns = st.columns(nb_saison_select)

select_saison = df_final.index[row_select_saison].tolist()

compt = 0

for saison in select_saison :
    with columns[compt] :
        if compt < nb_saison_select - 1 :
            columns2 = st.columns([10, 1], vertical_alignment = "center", gap = "medium")

            with columns2[0] :
                st.write(saison)

                st.markdown('<div class="centered">', unsafe_allow_html=True)

                st.dataframe(df.loc[saison, :].round(2).reindex(dico_rank_SB[saison]), height = 738)

                st.markdown('</div>', unsafe_allow_html=True)
            
            with columns2[1] :
                st.html(
                        '''
                            <div class="divider-vertical-line"></div>
                            <style>
                                .divider-vertical-line {
                                    border-left: 2px solid rgba(49, 51, 63, 0.2);
                                    height: 800px;
                                    margin: auto;
                                }
                            </style>
                        '''
                    )
                
        else :
            st.write(saison)

            st.markdown('<div class="centered">', unsafe_allow_html=True)

            st.dataframe(df.loc[saison, :].round(2).reindex(dico_rank_SB[saison]), height = 738)

            st.markdown('</div>', unsafe_allow_html=True)

    compt += 1