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
st.divider()

#----------------------------------------------- DÉFINITION FONCTIONS ------------------------------------------------------------------------------------

@st.cache_data
def import_df(saison_df) :
    return pd.read_excel(f"Heatmap SB/deb_action/Tableaux/{saison_df}.xlsx", index_col = 0)


def select_type_action():
    st.session_state['Type_action'] = st.session_state.multiselect


#----------------------------------------------- DÉFINITION DES DICOS ------------------------------------------------------------------------------------


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

dico_label = {"Choisir Top/Middle/Bottom" : ["du"], "Choisir équipe" : ["de"]}

#----------------------------------------------- FILTRAGE DES DATAS ------------------------------------------------------------------------------------


columns = st.columns(2, gap = "large")

with columns[0] :
    saison_choice = st.multiselect("Choisir saison", options = ["2023/2024", "2022/2023", "2021/2022", "2020/2021"], default = "2023/2024")
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

    st.multiselect("Choisir le type de début d'action", options = df.type_action.unique(), on_change = select_type_action,
                                        default = [i for i in st.session_state["Type_action"] if i in df.type_action.unique()], key = "multiselect")
    df = df[df.type_action.isin(st.session_state["Type_action"])]

    columns = st.columns(2, gap = "large", vertical_alignment = "center")


    with columns[0] :
        bins_h = st.number_input("Nombre de colonne pour la Heatmap de gauche", min_value = 1, step = 1, value = 5)
        bins_v = st.number_input("Nombre de ligne pour la Heatmap de gauche", min_value = 1, step = 1, value = 10)

    with columns[1] :
        choix_goal = st.checkbox("Sélectionner uniquement les débuts d'actions menant à un but")

        if choix_goal :
            df = df[df.But]
        
        count_type = st.selectbox("Type de comptage", ["Pourcentage", "Pourcentage sans %", "Valeur", "Aucune valeur"])



    #----------------------------------------------- AFFICHAGE HEATMAPS ------------------------------------------------------------------------------------

    if len(st.session_state["Type_action"]) > 0 :
        
        st.divider()
        bool_len_grp = (len(saison_choice) > 1)
        saison_title = []
        saison_title.append(f'la saison {saison_choice[0]}')
        saison_title.append(f'les saisons {", ".join(saison_choice[:-1])} et {saison_choice[-1]}')
        
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
            path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'), path_effects.Normal()]
            pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#f4edf0', line_color = "#f4edf0",
                                goal_type = "box", linewidth = 1, spot_scale = 0.002)
            fig1, ax1 = pitch.draw(constrained_layout=True, tight_layout=False)
            fig1.set_facecolor("none")
            ax1.set_facecolor((98/255, 98/255, 98/255))
            fig1.set_edgecolor("none")
            bin_statistic1 = pitch.bin_statistic(data.x, data.y, statistic='count', bins=(bins_v, bins_h),
                                                normalize = "Pourcentage" in count_type)
            pitch.heatmap(bin_statistic1, ax = ax1, cmap = cmr.nuclear, edgecolor='#FF0000')
            if count_type == "Pourcentage" :
                labels = pitch.label_heatmap(bin_statistic1, fontsize = int(50/(bins_v + bins_h)) + 2, color='#f4edf0', ax = ax1,
                                                ha='center', va='center', str_format='{:.0%}', path_effects=path_eff)
            elif count_type == "Pourcentage sans %" :
                (bin_statistic1["statistic"]) = 100*(bin_statistic1["statistic"])
                labels = pitch.label_heatmap(bin_statistic1, fontsize = int(50/(bins_v + bins_h)) + 2, color='#f4edf0', ax = ax1,
                                                ha='center', va='center', str_format='{:.0f}', path_effects=path_eff)
            elif count_type == "Valeur" :
                labels = pitch.label_heatmap(bin_statistic1, fontsize = int(50/(bins_v + bins_h)) + 2, color='#f4edf0', ax = ax1,
                                                ha='center', va='center', str_format='{:.0f}', path_effects=path_eff)
            st.pyplot(fig1)

        @st.cache_data
        def heatmap_smooth(data) :
            path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'), path_effects.Normal()]
            pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#f4edf0', line_color = "#f4edf0",
                                goal_type = "box", linewidth = 1, spot_scale = 0.002)
            fig2, ax2 = pitch.draw(constrained_layout=True, tight_layout=False)
            fig2.set_facecolor("none")
            ax2.set_facecolor((98/255, 98/255, 98/255))
            fig2.set_edgecolor("none")
            kde = pitch.kdeplot(data.x, data.y, ax = ax2, fill = True, levels = 100, thresh = 0, cmap = cmr.nuclear)
            st.pyplot(fig2)




        col1, col2 = st.columns(2, vertical_alignment = "bottom")
        with col1 :
            heatmap_percen(df, bins_h, bins_v, count_type)
        with col2 :
            heatmap_smooth(df)


    liste_goal_label = ["tirs", "buts"]
    st.markdown(f"<p style='text-align: center;'>Nombre total de {liste_goal_label[choix_goal]} : {len(df)}</p>",
                        unsafe_allow_html=True)