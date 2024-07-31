import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from config_py.variable import dico_rank_SB

st.set_page_config(layout="wide")

st.title("Moyenne du nombre de passes avant un but d'une compétition")


def func_change(key1, key2) :
    st.session_state[key1] = st.session_state[key2]


liste_équipe = []

liste_type_action = []

dico_df = {}


#----------------------------------------------- CHOIX GROUPES ------------------------------------------------------------------------------------


st.divider()
df_groupe = pd.DataFrame(0, index = ["Top", "Middle", "Bottom"], columns = ["Taille", "Slider"])
df_groupe["Slider"] = "Nombre d'équipe dans le " + df_groupe.index

columns = st.columns(3, gap = "large", vertical_alignment = "center")
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

groupe_non_vide = df_groupe[df_groupe.Taille > 0].index



#----------------------------------------------- IMPORTATION ET AFFICHAGE DATAFRAME ------------------------------------------------------------------------------------


for saison in dico_rank_SB.keys() :
    df = pd.read_excel(f"Passes avant un but/{saison}.xlsx", index_col = 0)
    dico_df[saison] = df
    liste_équipe += df.team.unique().tolist()
    liste_type_action += df.type_action.unique().tolist()

liste_équipe = list(set(liste_équipe))
liste_type_action = list(set(liste_type_action))

st.divider()

st.session_state["select_Type_action_passes"] = [i for i in st.session_state["Type_action_passes"] if i in liste_type_action]
type_action = st.multiselect("Choisir le type de début d'action", options = df.type_action.unique(), on_change = func_change,
                key = "select_Type_action_passes", args = ("Type_action_passes", "select_Type_action_passes"))

if len(type_action) > 0 :


    for saison in dico_rank_SB.keys() :
        df = dico_df[saison]
        df = df[df.type_action.isin(type_action)][["team", 'Passe']].groupby("team")
        nb_but = df.size()
        df = df.sum()
        df = df.divide(nb_but, axis = 0).reindex(dico_rank_SB[saison])
        dico_df[saison] = df

    st.divider()

    columns = st.columns([2, 1, 2], vertical_alignment = "center", gap = "large")
    with columns[1] :
        choix_groupe = st.multiselect("Groupe à afficher", groupe_non_vide, default = groupe_non_vide.tolist())

    with columns[2] :
        choix_équipe = st.multiselect("Équipe à afficher", sorted(liste_équipe))


    df_final = pd.DataFrame(index = dico_rank_SB.keys())

    for saison in dico_rank_SB.keys() :
        df = dico_df[saison]
        df_final.loc[saison, "Top"] = df.iloc[:df_groupe.loc["Top", "Taille"]].mean(axis = 0).iloc[0].round(2)
        df_final.loc[saison, "Middle"] = df.iloc[df_groupe.loc["Top", "Taille"]:df_groupe.loc["Top", "Taille"] + df_groupe.loc["Middle", "Taille"]].mean(axis = 0).iloc[0].round(2)
        df_final.loc[saison, "Bottom"] = df.iloc[df_groupe.loc["Top", "Taille"] + df_groupe.loc["Middle", "Taille"]:].mean(axis = 0).iloc[0].round(2)
        df_final.loc[saison, "Global"] = df.mean(axis = 0).iloc[0].round(2)
        for équipe in choix_équipe :
            if équipe in df.index :
                df_final.loc[saison, équipe] = df.loc[équipe].mean(axis = 0).round(2)

    df_final = df_final.dropna(axis = 1, how = "all")

    with columns[0] :
        df_final.index = ["2023/2024", "2022/2023", "2021/2022", "2020/2021"]
        select_df = st.dataframe(df_final[groupe_non_vide], on_select = "rerun", selection_mode = ["multi-row"])



    #----------------------------------------------- AFFICHAGE GRAPHIQUE ------------------------------------------------------------------------------------


    df_plot = df_final.reindex(df_final.index[::-1])[choix_groupe + choix_équipe]

    if df_plot.shape[1] > 0 :

        st.divider()
        
        fig = plt.figure()
        plt.plot(df_plot, marker = "+", linewidth = 1)
        plt.grid()

        bool_len_grp = len(df_plot.columns) > 1
        grp_title = []
        grp_title.append(f'{df_plot.columns[0]}')
        grp_title.append(f'{", ".join(df_plot.columns[:-1])} et {df_plot.columns[-1]}')
        plt.title(f"Graphe du nombre de passes avant un but\npour{' le'*(len(choix_groupe) > 0)} {grp_title[bool_len_grp]}",
                    fontweight = "heavy", y = 1.05, fontsize = 9)

        plt.legend(df_plot.columns, bbox_to_anchor=(0.75, -0.25), fontsize = "small", ncol = 3)
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


    if len(select_df.selection.rows) > 0 :
        st.divider()
        st.markdown(f"<p style='text-align: center;'>Tableau du nombre de passes avant un but lors de la saison</p>", unsafe_allow_html=True)
        ""
        columns = st.columns(len(select_df.selection.rows))

        compt = 0

        for saison in df_final.index[select_df.selection.rows] :
            with columns[compt] :
                if compt < len(select_df.selection.rows) - 1 :
                    columns2 = st.columns([10, 1], vertical_alignment = "center", gap = "medium")
                    with columns2[0] :
                        st.write(f"{saison}")
                        st.markdown('<div class="centered">', unsafe_allow_html=True)
                        st.dataframe(dico_df[saison.replace("/", "_")].round(2), height = 738)
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
                    st.write(f"{saison}")
                    st.markdown('<div class="centered">', unsafe_allow_html=True)
                    st.dataframe(dico_df[saison.replace("/", "_")].round(2), height = 738)
                    st.markdown('</div>', unsafe_allow_html=True)

            compt += 1