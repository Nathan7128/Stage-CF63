# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Importation des librairies


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

from fonction import execute_SQL, load_session_state, store_session_state, init_session_state, replace_saison1, replace_saison2, filtre_session_state
from variable import dico_rank_SB

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
# Choix de la compétition et de la ou des saisons


columns = st.columns([1, 2], vertical_alignment = "center", gap = "large")

params = []
stat = f"SELECT DISTINCT Compet FROM Passes_avant_un_but"
liste_compet, desc = execute_SQL(cursor, stat, params)
liste_compet = [i[0] for i in liste_compet]
    
with columns[0] :
    load_session_state("compet_nb_passe")
    choix_compet = st.selectbox("Choisir compétition", options = liste_compet, key = "widg_compet_nb_passe",
                                on_change = store_session_state, args = ["compet_nb_passe"])

params = [choix_compet]
stat = f"SELECT DISTINCT Saison FROM Passes_avant_un_but WHERE Compet = ?"
liste_saison, desc = execute_SQL(cursor, stat, params)
liste_saison = [i[0] for i in liste_saison]

with columns[1] :
    init_session_state("saison_nb_passe", [max(replace_saison1(liste_saison))])
    load_session_state("saison_nb_passe")
    choix_saison = st.multiselect("Choisir saison", replace_saison1(liste_saison), key = "widg_saison_nb_passe",
                                  on_change = store_session_state, args = ["saison_nb_passe"])

choix_saison = replace_saison2(choix_saison)

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

df_taille_groupe = pd.DataFrame(0, index = ["Top", "Middle", "Bottom"], columns = ["Taille", "Slider"])

df_taille_groupe["Slider"] = "Nombre d'équipe dans le " + df_taille_groupe.index

with columns[0] :
    load_session_state("nb_top_nb_passe")
    df_taille_groupe.loc["Top", "Taille"] = st.slider(df_taille_groupe.loc["Top", "Slider"], min_value = 1,
            max_value = max_nb_team, key = "widg_nb_top_nb_passe", on_change = store_session_state, args = ["nb_top_nb_passe"])
    
with columns[1] :
    if df_taille_groupe.loc["Top", "Taille"] == max_nb_team :
        st.session_state["nb_bottom_nb_passe"] = max_nb_team - df_taille_groupe.loc["Top", "Taille"]

    else :
        load_session_state("nb_bottom_nb_passe")
        st.slider(df_taille_groupe.loc["Bottom", "Slider"], min_value = 0,
                max_value = max_nb_team - df_taille_groupe.loc["Top", "Taille"], key = "widg_nb_bottom_nb_passe",
                on_change = store_session_state, args = ["nb_bottom_nb_passe"])
        
    df_taille_groupe.loc["Bottom", "Taille"] = st.session_state["nb_bottom_nb_passe"]
        
df_taille_groupe.loc["Middle", "Taille"] = max_nb_team - df_taille_groupe.loc["Top", "Taille"] - df_taille_groupe.loc["Bottom", "Taille"]

groupe_non_vide = df_taille_groupe[df_taille_groupe.Taille > 0].index.tolist()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Filtre des types de début d'action souhaités


st.divider()

liste_type_action = df.type_action.unique().tolist()

filtre_session_state("type_action_nb_passe", liste_type_action)
load_session_state("type_action_nb_passe")
type_action = st.multiselect("Choisir le type de début d'action", options = liste_type_action, key = "widg_type_action_nb_passe",
                             on_change = store_session_state, args = ["type_action_nb_passe"])

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
    init_session_state("groupe_nb_passe", groupe_non_vide)
    filtre_session_state("groupe_nb_passe", groupe_non_vide)
    load_session_state("groupe_nb_passe")
    choix_groupe = st.multiselect("Groupe à afficher", groupe_non_vide, key = "widg_groupe_nb_passe",
                on_change = store_session_state, args = ["groupe_nb_passe"])

with columns[1] :
    liste_équipe = sorted(df.index.levels[1].tolist())

    filtre_session_state("équipe_nb_passe", liste_équipe)
    load_session_state("équipe_nb_passe")
    choix_équipe = st.multiselect("Équipe à afficher", liste_équipe, key = "widg_équipe_nb_passe", on_change = store_session_state,
                                  args = ["équipe_nb_passe"])


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Création et affichage du dataframe final


df.set_index("Groupe", append = True, inplace = True)

df_final_groupe = df["Passe"].groupby(level = [0, 2]).mean().unstack().round(2)
df_final_équipe = df["Passe"].groupby(level = [0, 1]).mean().unstack().round(2)

df_final = pd.concat([df_final_groupe, df_final_équipe], axis = 1)[choix_groupe + choix_équipe]
df_final.index = replace_saison1(df_final_groupe.index.tolist())

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

select_saison = replace_saison2(df_final.index[row_select_saison].tolist())

compt = 0

for saison in select_saison :
    with columns[compt] :
        if compt < nb_saison_select - 1 :
            columns2 = st.columns([10, 1], vertical_alignment = "center", gap = "medium")

            with columns2[0] :
                st.write(f"{replace_saison1(saison)}")

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
            st.write(f"{replace_saison1(saison)}")

            st.markdown('<div class="centered">', unsafe_allow_html=True)

            st.dataframe(df.loc[saison, :].round(2).reindex(dico_rank_SB[saison]), height = 738)

            st.markdown('</div>', unsafe_allow_html=True)

    compt += 1