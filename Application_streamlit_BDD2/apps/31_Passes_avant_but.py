import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

from fonction import func_change, execute_SQL, replace_saison1, replace_saison2
from variable import dico_rank_SB

idx = pd.IndexSlice

st.set_page_config(layout="wide")

st.title("Moyenne du nombre de passe avant un but d'une compétition")
st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Connection BDD


connect = sqlite3.connect("database.db")
cursor = connect.cursor()


#----------------------------------------------- CHOIX COMPET + SAISON ------------------------------------------------------------------------------------


columns = st.columns([1, 2], vertical_alignment = "center", gap = "large")

# Choix Compet
params = []
stat = f"SELECT DISTINCT Compet FROM Passes_avant_un_but"
liste_compet = execute_SQL(cursor, stat, params).fetchall()
liste_compet = [i[0] for i in liste_compet]
    
with columns[0] :
    choix_compet = st.selectbox("Choisir compétition", options = liste_compet, index = 0)

# Choix d'une ou plusieurs saisons sur laquelle/lesquelles on va étudier les métriques pour Skill Corner
params = [choix_compet]
stat = f"SELECT DISTINCT Saison FROM Passes_avant_un_but WHERE Compet = ?"
liste_saison = execute_SQL(cursor, stat, params).fetchall()
liste_saison = [i[0] for i in liste_saison]

with columns[1] :
    choix_saison = st.multiselect("Choisir saison", replace_saison2(liste_saison), default = replace_saison2(liste_saison))
choix_saison = replace_saison1(choix_saison)

# On regarde si au moins une saison est choisie
if len(choix_saison) == 0 :
    st.stop()

st.divider()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Création du dataframe en choisissant le type de métrique qu'on souhaite étudier


params = [choix_compet] + choix_saison
stat = f"SELECT * FROM Passes_avant_un_but WHERE Compet = ? and Saison IN ({', '.join('?' * len(choix_saison))})"
res = execute_SQL(cursor, stat, params)

df = pd.DataFrame(res.fetchall())
df.columns = [i[0] for i in res.description]
df = df.drop(["Compet", "index"], axis = 1).set_index(["Saison", "team"])


#----------------------------------------------- CHOIX GROUPES ------------------------------------------------------------------------------------


df_nb_team = df.reset_index()[["Saison", "team"]].drop_duplicates().groupby("Saison").apply(len)
max_team = min(df_nb_team)

df_groupe = pd.DataFrame(0, index = ["Top", "Middle", "Bottom"], columns = ["Taille", "Slider"])
df_groupe["Slider"] = "Nombre d'équipe dans le " + df_groupe.index

columns = st.columns(2, gap = "large", vertical_alignment = "center")
with columns[0] :
    df_groupe.loc["Top", "Taille"] = st.slider(df_groupe.loc["Top", "Slider"], min_value = 1, max_value = 20, value = 5)
with columns[1] :
    if df_groupe.loc["Top", "Taille"] == 20 :
        df_groupe.loc["Bottom", "Taille"] = 20 - df_groupe.loc["Top", "Taille"]
        st.write(f"Nombre d'équipe dans le Bottom : {df_groupe.loc['Bottom', 'Taille']}")
    else :
        df_groupe.loc["Bottom", "Taille"] = st.slider(df_groupe.loc["Bottom", "Slider"], min_value = 0,
                                                        max_value = 20 - df_groupe.loc["Top", "Taille"])

nb_middle = df_nb_team - df_groupe.loc["Top", "Taille"] - df_groupe.loc["Bottom", "Taille"]
df_groupe.loc["Middle", "Taille"] = max(nb_middle)

groupe_non_vide = df_groupe[df_groupe.Taille > 0].index



#----------------------------------------------- IMPORTATION ET AFFICHAGE DATAFRAME ------------------------------------------------------------------------------------


liste_équipe = df.index.levels[1]
liste_type_action = df.type_action.unique().tolist()

st.divider()

st.session_state["select_Type_action_passes"] = [i for i in st.session_state["Type_action_passes"] if i in liste_type_action]
type_action = st.multiselect("Choisir le type de début d'action", options = df.type_action.unique(), on_change = func_change,
                key = "select_Type_action_passes", args = ("Type_action_passes", "select_Type_action_passes"))

if len(type_action) == 0 :
    st.stop()

df = df[df.type_action.isin(type_action)][['Passe']].groupby(level = [0, 1], sort = False)
nb_but = df.size()
df = df.sum()
df = df.divide(nb_but, axis = 0)

for saison in choix_saison :

    liste_rank = dico_rank_SB[saison]

    df.loc[idx[saison, liste_rank[:df_groupe.loc["Top", "Taille"]]], "Groupe"] = "Top"
    df.loc[idx[saison, liste_rank[df_groupe.loc["Top", "Taille"]:df_groupe.loc["Top", "Taille"] + nb_middle.loc[saison]]], "Groupe"] = "Middle"
    df.loc[idx[saison, liste_rank[df_groupe.loc["Top", "Taille"] + nb_middle.loc[saison]:]], "Groupe"] = "Bottom"


st.divider()

columns = st.columns([1, 2], vertical_alignment = "center", gap = "large")

with columns[0] :
    choix_groupe = st.multiselect("Groupe à afficher", groupe_non_vide, default = groupe_non_vide.tolist())

with columns[1] :
    choix_équipe = st.multiselect("Équipe à afficher", sorted(liste_équipe))

df = df.set_index("Groupe", append = True)

df_final_groupe = df["Passe"].groupby(level = [0, 2]).mean().unstack().round(2)
df_final_équipe = df["Passe"].groupby(level = [0, 1]).mean().unstack().round(2)

df_final = pd.concat([df_final_groupe, df_final_équipe], axis = 1)[choix_groupe + choix_équipe]
df_final.index = replace_saison2(df_final_groupe.index.tolist())

if df_final.shape[1] == 0 :
    st.stop()

st.divider()

st.markdown(f"<p style='text-align: center;'>Tableau du nombre de passe avant un but</p>", unsafe_allow_html=True)

select_df = st.dataframe(df_final.fillna("x"), on_select = "rerun", selection_mode = ["multi-row"])


#----------------------------------------------- AFFICHAGE GRAPHIQUE ------------------------------------------------------------------------------------


st.divider()

fig = plt.figure()
plt.plot(df_final, marker = "+", linewidth = 1)
plt.grid()

bool_len_grp = df_final.shape[1] > 1
grp_title = []
grp_title.append(f'{df_final.columns[0]}')
grp_title.append(f'{", ".join(df_final.columns[:-1])} et {df_final.columns[-1]}')
plt.title(f"Graphe du nombre de passe avant un but\npour{' le'*(len(choix_groupe) > 0)} {grp_title[bool_len_grp]}",
            fontweight = "heavy", y = 1.05, fontsize = 9)

plt.legend(df_final.columns, bbox_to_anchor=(0.75, -0.25), fontsize = "small", ncol = 3)
plt.xlabel("Saison", fontsize = "small", fontstyle = "italic", labelpad = 10)
plt.ylabel("Passes", fontsize = "small", fontstyle = "italic", labelpad = 10)
plt.tick_params(labelsize = 8)
ax = plt.gca()
ax.spines[:].set_visible(False)

st.pyplot(fig)



#----------------------------------------------- AFFICHAGE TABLEAU ÉQUIPES ------------------------------------------------------------------------------------


st.markdown(
    """
    <style>
    .centered {
        display: flex;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)


nb_saison_select = len(select_df.selection.rows)

if nb_saison_select == 0 :
    st.stop()

df.reset_index(level = 2, drop = True, inplace = True)

st.divider()
st.markdown(f"<p style='text-align: center;'>Tableau du nombre de passes avant un but lors de la saison</p>", unsafe_allow_html=True)
""
columns = st.columns(nb_saison_select)
select_saison = replace_saison1(df_final.index[select_df.selection.rows].tolist())

compt = 0

for saison in select_saison :
    with columns[compt] :
        if compt < nb_saison_select - 1 :
            columns2 = st.columns([10, 1], vertical_alignment = "center", gap = "medium")
            with columns2[0] :
                st.write(f"{replace_saison2(saison)}")
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
            st.write(f"{replace_saison2(saison)}")
            st.markdown('<div class="centered">', unsafe_allow_html=True)
            st.dataframe(df.loc[saison, :].round(2).reindex(dico_rank_SB[saison]), height = 738)
            st.markdown('</div>', unsafe_allow_html=True)

    compt += 1