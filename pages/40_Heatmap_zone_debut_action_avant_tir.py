import streamlit as st

import matplotlib.patheffects as path_effects

import pandas as pd

from mplsoccer import Pitch, VerticalPitch

import matplotlib.pyplot as plt

import cmasher as cmr

st.set_page_config(layout="wide")


if 'Type_action' not in st.session_state :
    st.session_state['Type_action'] = ["Open play"]

st.title("Heatmap des zones de début d'actions menant à un tir")


#----------------------------------------------- DÉFINITION FONCTIONS ------------------------------------------------------------------------------------

@st.cache_data
def import_df(saison_df) :
    return pd.read_excel(f"Heatmap SB/deb_action/Tableaux/{saison_df}.xlsx", index_col = 0)


def select_type_action():
    st.session_state['Type_action'] = st.session_state.multiselect


#----------------------------------------------- CRÉATION DATAFRAME ------------------------------------------------------------------------------------


dico_rank = {
     "2023_2024" : ["Auxerre", "Angers", "Saint-Étienne", "Rodez", "Paris FC", "Caen", "Laval", "Amiens", "Guingamp", "Pau",
          "Grenoble Foot", "Bordeaux", "Bastia", "FC Annecy", "AC Ajaccio", "Dunkerque", "Troyes", "Quevilly Rouen", "Concarneau",
          "Valenciennes"],
     "2022_2023" : ["Le Havre", "Metz", "Bordeaux", "Bastia", "Caen", "Guingamp", "Paris FC", "Saint-Étienne", "Sochaux", "Grenoble Foot",
          "Quevilly Rouen", "Amiens", "Pau", "Rodez", "Laval", "Valenciennes", "FC Annecy", "Dijon", "Nîmes", "Chamois Niortais"],
     "2021_2022" : ["Toulouse", "AC Ajaccio", "Auxerre", "Paris FC", "Sochaux", "Guingamp", "Caen", "Le Havre", "Nîmes", "Pau", "Dijon",
          "Bastia", "Chamois Niortais", "Amiens", "Grenoble Foot", "Valenciennes", "Rodez",  "Quevilly Rouen", "Dunkerque", "Nancy"],
     "2020_2021" : ["Troyes", "Clermont Foot", "Toulouse", "Grenoble Foot", "Paris FC", "Auxerre", "Sochaux", "Nancy", "Guingamp",
          "Amiens", "Valenciennes", "Le Havre", "AC Ajaccio", "Pau", "Rodez", "Dunkerque", "Caen",  "Chamois Niortais", "Chambly",
          "Châteauroux"]
}

dico_df_saison = {}

liste_équipe = []


#----------------------------------------------- FILTRAGE DES DATAS ------------------------------------------------------------------------------------


columns = st.columns(2, gap = "large")

with columns[0] :
    saison_choice = st.multiselect("Choisir saison", options = ["2023/2024", "2022/2023", "2021/2022", "2020/2021"])
    saison_choice.sort()
    liste_saison = [i.replace("/", "_") for i in saison_choice]

with columns[1] :
    choix_groupe = st.radio("Choix groupe", ["Choisir Top/Middle/Bottom", "Choisir équipe"], label_visibility = "hidden")

for saison in liste_saison :
    df_import = import_df(saison)
    dico_df_saison[saison] = df_import
    liste_équipe += df_import.Équipe.unique().tolist()

liste_équipe = list(set(liste_équipe))


#----------------------------------------------- CHOIX GROUPE ------------------------------------------------------------------------------------

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
        groupe_plot = st.radio("Groupe à afficher", groupe_non_vide.tolist()*(df_groupe.loc["Top", "Taille"] != 20) + ["Global"],
                               horizontal = True)

else :
    choix_équipe = st.multiselect("Choisir équipe", sorted(liste_équipe))

st.divider()


#----------------------------------------------- FILTRAGE DF ------------------------------------------------------------------------------------

df = pd.DataFrame()

if choix_groupe == "Choisir Top/Middle/Bottom" :
    
    for saison in dico_df_saison.keys() :
        df_saison = dico_df_saison[saison]
    
        if groupe_plot == "Top" :
            df_saison = df_saison[df_saison.Équipe.isin(dico_rank[saison][:df_groupe.loc["Top", "Taille"]])]

        elif groupe_plot == "Middle" :
            df_saison = df_saison[df_saison.Équipe.isin(dico_rank[saison][df_groupe.loc["Top", "Taille"]:df_groupe.loc["Top", "Taille"] + df_groupe.loc["Middle", "Taille"]])]

        elif groupe_plot == "Bottom" :  
            df_saison = df_saison[df_saison.Équipe.isin(dico_rank[saison][df_groupe.loc["Top", "Taille"] + df_groupe.loc["Middle", "Taille"]:])]
        df = pd.concat([df, df_saison[['x', 'y', 'type_action', 'But']]], axis = 0)

    
else :
    for saison in dico_df_saison.keys() :
        df_saison = dico_df_saison[saison]
        df_saison = df_saison[df_saison.Équipe.isin(choix_équipe)]
        df = pd.concat([df, df_saison[['x', 'y', 'type_action', 'But']]], axis = 0)



#----------------------------------------------- FILTRAGE HEATMAPS ------------------------------------------------------------------------------------

if len(df) > 0 :

    columns = st.columns(2, gap = "large")


    with columns[0] :
        bins_h = st.number_input("Nombre de colonne pour la Heatmap de gauche", min_value = 1, step = 1, value = 5)
        bins_v = st.number_input("Nombre de ligne pour la Heatmap de gauche", min_value = 1, step = 1, value = 10)

    with columns[1] :
        choix_goal = st.checkbox("Sélectionner uniquement les débuts d'actions menant à un but")

        if choix_goal :
            df = df[df.But]
        
        st.multiselect("Choisir le type de début d'action", options = df.type_action.unique(), on_change = select_type_action,
                                            default = st.session_state["Type_action"], key = "multiselect")
        df = df[df.type_action.isin(st.session_state["Type_action"])]

    st.divider()

    col1, col2 = st.columns(2, vertical_alignment = "bottom")
    with col1 :
        choix_percent = st.checkbox("Cacher les '%' des zones")
    with col2 :
        choix_line = st.checkbox("Cacher les lignes du terrain")


    #----------------------------------------------- AFFICHAGE HEATMAPS ------------------------------------------------------------------------------------

    if len(st.session_state["Type_action"]) > 0 :
        
        st.divider()

        # if groupe != "Équipe" :
        #     st.markdown(f"<p style='text-align: center;'>Heatmap pour le {groupe} de Ligue 2 sur la saison {annee_choice}</p>", unsafe_allow_html=True)

        # else :
        #     st.markdown(f"<p style='text-align: center;'>Heatmap pour les équipes sélectionnées de Ligue 2 sur la saison {annee_choice}</p>", unsafe_allow_html=True)



        @st.cache_data
        def heatmap_percen(data, bins_h, bins_v, choix_percent, choix_line) :
            path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'), path_effects.Normal()]
            pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#f4edf0', line_color = "#f4edf0",
                                goal_type = "box", linewidth = 1*(1 - choix_line), spot_scale = 0.002*(1 - choix_line))
            fig1, ax1 = pitch.draw(constrained_layout=True, tight_layout=False)
            fig1.set_facecolor("none")
            ax1.set_facecolor((98/255, 98/255, 98/255))
            fig1.set_edgecolor("none")
            bin_statistic1 = pitch.bin_statistic(data.x, data.y, statistic='count', bins=(bins_v, bins_h), normalize=True)
            pitch.heatmap(bin_statistic1, ax = ax1, cmap = cmr.nuclear, edgecolor='#FF0000')
            if not(choix_percent) :
                labels = pitch.label_heatmap(bin_statistic1, fontsize = int(50/(bins_v + bins_h)) + 2, color='#f4edf0', ax = ax1,
                                                ha='center', va='center', str_format='{:.0%}', path_effects=path_eff)
            st.pyplot(fig1)

        @st.cache_data
        def heatmap_smooth(data, choix_line) :
            path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'), path_effects.Normal()]
            pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#f4edf0', line_color = "#f4edf0",
                                goal_type = "box", linewidth = 1*(1 - choix_line), spot_scale = 0.002*(1 - choix_line))
            fig2, ax2 = pitch.draw(constrained_layout=True, tight_layout=False)
            fig2.set_facecolor("none")
            ax2.set_facecolor((98/255, 98/255, 98/255))
            fig2.set_edgecolor("none")
            kde = pitch.kdeplot(data.x, data.y, ax = ax2, fill = True, levels = 100, thresh = 0, cmap = cmr.nuclear)
            st.pyplot(fig2)




        col1, col2 = st.columns(2, vertical_alignment = "bottom")
        with col1 :
            heatmap_percen(df, bins_h, bins_v, choix_percent, choix_line)
        with col2 :
            heatmap_smooth(df, choix_line)