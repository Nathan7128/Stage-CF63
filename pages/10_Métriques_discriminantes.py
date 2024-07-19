import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

st.title("Métriques discriminantes d'une compétition")


#----------------------------------------------- DÉFINITIONS DES DICTIONNAIRES ------------------------------------------------------------------------------------


dico_type = {
    "Physiques" : ["metrique_physical.xlsx",
        {"30 min. tip" : "_per30tip", "30 min. otip" : "_per30otip", "Match all possession" : "_per_Match"}],
    
    "Courses sans ballon avec la possession" : ["metrique_running.xlsx",
        {"Match" : "per_match", "100 runs" : "per_100_runs", "30 min. tip" : "per_30_min_tip"},
        "Type de course",
        {"Runs in behind" : "runs_in_behind", "Runs ahead of the ball" : "runs_ahead_of_the_ball", "Support runs" : "support_runs",
        "Pulling wide runs" : "pulling_wide_runs", "Coming short runs" : "coming_short_runs", "Underlap runs" : "underlap_runs",
        "Overlap runs" : "overlap_runs", "Dropping off runs" : "dropping_off_runs",
        "Pulling half space runs" : "pulling_half_space_runs", "Cross receiver runs" : "cross_receiver_runs"},
        {"Leading to goal" : "leading_to_goal", "Leading to shot" : "leading_to_shot", "Received" : "received", "Threat" : "threat",
        "Targeted" : "targeted", "Dangerous" : "dangerous"}],

    "Action sous pression" : ["metrique_pressure.xlsx",
        {"Match" : "per_match", "100 pressures" : "per_100_pressures", "30 min. tip" : "per_30_min_tip"},
        "Intensité de pression",
        {"Low" : "low", "Medium" : "medium", "High" : "high"}],
    
    "Passes à un coéquipier effectuant une course" : ["metrique_passes.xlsx",
        {"Match" : "per_match", "100 passes opportunities" : "per_100_pass_opportunities", "30 min. tip" : "per_30_min_tip"},
        "Type de course",
        {"Runs in behind" : "runs_in_behind", "Runs ahead of the ball" : "runs_ahead_of_the_ball", "Support runs" : "support_runs",
        "Pulling wide runs" : "pulling_wide_runs", "Coming short runs" : "coming_short_runs", "Underlap runs" : "underlap_runs",
        "Overlap runs" : "overlap_runs", "Dropping off runs" : "dropping_off_runs",
        "Pulling half space runs" : "pulling_half_space_runs", "Cross receiver runs" : "cross_receiver_runs"}]
}


#----------------------------------------------- CHOIX ANNÉE + FOURNISSEUR ------------------------------------------------------------------------------------


col1, col2 = st.columns([1, 3], gap = "large")

with col1 :
    choix_data = st.radio("Fournisseur data", options = ["Skill Corner", "Stats Bomb"], horizontal = True)
    if choix_data == "Skill Corner" :
        annee = st.radio("Choisir saison", options = ["2023/2024", "2022/2023", "2021/2022"], horizontal = True)
    else :
        annee = st.radio("Choisir saison", options = ["2023/2024", "2022/2023", "2021/2022", "2020/2021"], horizontal = True)
    annee = annee.replace("/", "_")



#----------------------------------------------- CHOIX TAILLE GROUPES ------------------------------------------------------------------------------------


columns = st.columns(3, gap = "large", vertical_alignment = "center")
with columns[0] :
    nb_top = st.slider("Nombre d'équipe dans le Top", min_value = 1, max_value = 20, value = 5)
with columns[1] :
    if nb_top == 20 :
        nb_bottom = 20 - nb_top
        st.write(f"Nombre d'équipe dans le Bottom : {nb_bottom}")
    else :
        nb_bottom = st.slider("Nombre d'équipe dans le Bottom", min_value = 0, max_value = 20 - nb_top)
with columns[2] :
    nb_middle = 20 - nb_top - nb_bottom
    st.write(f"Nombre d'équipe dans le Middle : {nb_middle}")



#----------------------------------------------- IMPORTATION DATAFRAME ------------------------------------------------------------------------------------



if choix_data == "Skill Corner" :
    with col2 :
        cat_met = st.radio("Catégorie de métrique", dico_type.keys(), horizontal = True)

        cat_moy = st.radio("Moyenne de la métrique", dico_type[cat_met][1].keys(), horizontal = True)

    file_metrique = dico_type[cat_met][0]
    metrique_moyenne = pd.read_excel(f"Métriques discriminantes/Tableau métriques/moyenne/{annee}/{choix_data}/{file_metrique}",
                                         index_col=0)

else :
    file_metrique = "metriques.xlsx"

    metrique_moyenne = pd.read_excel(f"Métriques discriminantes/Tableau métriques/moyenne/{annee}/{choix_data}/{file_metrique}",
                                        index_col=0)
    metrique_moyenne




# ------------------------------------------------ CRÉATION DATAFRAME MOYENNE -------------------------------------------------------------


with col2 :

    moyenne = pd.DataFrame(index = metrique_moyenne.columns)

    df_top = metrique_moyenne.iloc[:nb_top]
    df_middle = metrique_moyenne.iloc[nb_top:nb_top + nb_middle]
    df_bottom = metrique_moyenne.iloc[nb_top + nb_middle:]

    moyenne["Moyenne Top"] = df_top.mean(axis = 0)
    if nb_top > 1 :
        moyenne["Ecart type Top"] = df_top.std(axis = 0)
        moyenne["Min Top"] = df_top.min(axis = 0)
        moyenne["Max Top"] = df_top.max(axis = 0)

    if nb_middle > 0 :
        moyenne["Moyenne Middle"] = df_middle.mean(axis = 0)
        if nb_middle > 1 :
            moyenne["Ecart type Middle"] = df_middle.std(axis = 0)
            moyenne["Min Middle"] = df_middle.std(axis = 0)
            moyenne["Max Middle"] = df_middle.std(axis = 0)
        moyenne["Diff. Top avec Middle en %"] = (100*(moyenne["Moyenne Top"] - moyenne["Moyenne Middle"])/abs(moyenne["Moyenne Middle"])).round(2)
        moyenne = moyenne.reindex(abs(moyenne).sort_values(by = "Diff. Top avec Middle en %", ascending = False).index)
    if nb_bottom > 0 :
        moyenne["Moyenne Bottom"] = df_bottom.mean(axis = 0)
        if nb_bottom > 1 :
            moyenne["Ecart type Bottom"] = df_bottom.std(axis = 0)
            moyenne["Min Bottom"] = df_bottom.min(axis = 0)
            moyenne["Max Bottom"] = df_bottom.max(axis = 0)
        moyenne["Diff. Top avec Bottom en %"] = (100*(moyenne["Moyenne Top"] - moyenne["Moyenne Bottom"])/abs(moyenne["Moyenne Bottom"])).round(2)
        moyenne = moyenne.reindex(abs(moyenne).sort_values(by = "Diff. Top avec Bottom en %", ascending = False).index)

    if nb_bottom > 0 and nb_middle > 0 :
        moyenne["Diff. Middle avec Bottom en %"] = (100*(moyenne["Moyenne Middle"] - moyenne["Moyenne Bottom"])/abs(moyenne["Moyenne Bottom"])).round(2)



    




#----------------------------------------------- FILTRAGE MÉTRIQUES SKILLCORNER ------------------------------------------------------------------------------------



if choix_data == "Skill Corner" :
    cat_type = dico_type[cat_met][1][cat_moy]
    col_keep = [(cat_type in i) or ("ratio" in i) for i in moyenne.index]
    moyenne = moyenne.iloc[col_keep]

    if cat_met != "Physiques" :
        col_keep = [False]*len(moyenne)
        liste_cat_type1 = st.multiselect(dico_type[cat_met][2], dico_type[cat_met][3].keys(), default = dico_type[cat_met][3].keys())
        for cat_type in liste_cat_type1 :
            cat_type = dico_type[cat_met][3][cat_type]
            col_keep = np.logical_or(col_keep, [(cat_type in i) or ("ratio" in i and cat_type in i) for i in moyenne.index])
        moyenne = moyenne.iloc[col_keep]

st.divider()


if len(moyenne) > 0 :
    nb_metrique = st.slider("Nombre de métriques gardées", min_value=0, max_value = moyenne.shape[0], value = moyenne.shape[0])
    moyenne_sort = moyenne.loc[moyenne.index[:nb_metrique]]

    col_df = st.multiselect("Données des métriques à afficher", moyenne.columns, moyenne.columns.tolist())

    moyenne_sort = moyenne_sort[col_df]

    if len(col_df) > 0 :



#----------------------------------------------- STYLE ET AFFICHAGE DATAFRAME --------------------------------------------------------------------------


        if "Diff. Top 5 avec Bottom 15 en %" in col_df :

            @st.cache_data
            def couleur_df(val) :
                color = 'background-color : rgba(0, 255, 0, 0.3)' if val >= 0 else 'background-color : rgba(255, 0, 0, 0.3)'
                return color

            moyenne_sort = moyenne_sort.style.applymap(couleur_df, subset = ["Diff. Top 5 avec Bottom 15 en %"])


        st.divider()

        st.markdown("<p style='text-align: center;'>Tableau des métriques trier par rapport à la différence entre la moyenne du Top 5 et du Bottom 15</p>", unsafe_allow_html=True)


        moyenne_sort_df = st.dataframe(moyenne_sort, on_select = "rerun", selection_mode = "multi-row")

        metrique_moyenne_sort = metrique_moyenne[moyenne.index[moyenne_sort_df.selection.rows]]
        st.markdown(f"<p style='text-align: center;'>Tableau des métriques retenues, par équipes, en moyenne par match</p>",
                    unsafe_allow_html=True)
        st.dataframe(metrique_moyenne_sort)