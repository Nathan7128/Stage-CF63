import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("Moyenne du nombre de passes avant un but d'une compétition")


#----------------------------------------------- DEFINITION DICTIONNAIRE ------------------------------------------------------------------------------------


dico_annee = {
    "2023_2024" : ["Auxerre", "Angers", "Saint-Étienne", "Rodez", "Paris FC", "Caen", "Laval",
           "Amiens", "Guingamp", "Pau", "Grenoble Foot", "Bordeaux", "Bastia",
           "FC Annecy", "AC Ajaccio", "Dunkerque", "Troyes", "Quevilly Rouen", "Concarneau", "Valenciennes"],
    "2022_2023" :["Le Havre", "Metz", "Bordeaux", "Bastia", "Caen", "Guingamp", "Paris FC",
           "Saint-Étienne", "Sochaux", "Grenoble Foot", "Quevilly Rouen", "Amiens", "Pau",
           "Rodez", "Laval", "Valenciennes", "FC Annecy", "Dijon", "Nîmes", "Chamois Niortais"],
    "2021_2022" : ["Toulouse", "AC Ajaccio", "Auxerre", "Paris FC", "Sochaux", "Guingamp", "Caen", "Le Havre", "Nîmes",
                             "Pau", "Dijon", "Bastia", "Chamois Niortais", "Amiens", "Grenoble Foot", "Valenciennes", "Rodez", 
                             "Quevilly Rouen", "Dunkerque", "Nancy"],
    "2020_2021" : ["Troyes", "Clermont Foot", "Toulouse", "Grenoble Foot", "Paris FC", "Auxerre", "Sochaux", "Nancy",
                             "Guingamp", "Amiens", "Valenciennes", "Le Havre", "AC Ajaccio", "Pau", "Rodez", "Dunkerque", "Caen", 
                             "Chamois Niortais", "Chambly", "Châteauroux"]
                             }


liste_équipe = []

dico_df = {}


#----------------------------------------------- CHOIX GROUPES ------------------------------------------------------------------------------------


st.divider()

columns = st.columns(3, gap = "large", vertical_alignment = "center")
with columns[0] :
    nb_top = st.slider("Nombre d'équipe dans le Top", min_value = 1, max_value = 20, value = 5)
with columns[1] :
    if nb_top == 20 :
        nb_bottom = 20 - nb_top
        st.write(f"Nombre d'équipe dans le Bottom : {nb_bottom}")
    else :
        nb_bottom = st.slider("Nombre d'équipe dans le Bottom", min_value = 0,
                                                        max_value = 20 - nb_top)
with columns[2] :
    nb_middle = 20 - nb_top - nb_bottom
    st.write(f"Nombre d'équipe dans le Middle : {nb_middle}")


#----------------------------------------------- IMPORTATION ET AFFICHAGE DATAFRAME ------------------------------------------------------------------------------------


df_moy = pd.DataFrame(index = dico_annee.keys(), columns = ["Top", "Middle", "Bottom", "Global"])

for i in dico_annee.keys() :
    df = pd.read_excel(f"Passes avant un but/{i}.xlsx", index_col = 0)
    df = df.reindex(dico_annee[i])
    df_moy.loc[i, "Top"] = df.iloc[:nb_top].mean(axis = 0).iloc[0].round(2)
    df_moy.loc[i, "Middle"] = df.iloc[nb_top:nb_top + nb_middle].mean(axis = 0).iloc[0].round(2)
    df_moy.loc[i, "Bottom"] = df.iloc[nb_top + nb_middle:].mean(axis = 0).iloc[0].round(2)
    df_moy.loc[i, "Global"] = df.mean(axis = 0).iloc[0].round(2)
    dico_df[i] = df
    liste_équipe += df.index.tolist()

liste_équipe = list(set(liste_équipe))

df_moy = df_moy.dropna(axis = 1, how = "all")

st.divider()

columns = st.columns([1, 4, 1, 4, 1], vertical_alignment = "center")

with columns[1] :
    df_moy.index = ["2023/2024", "2022/2023", "2021/2022", "2020/2021"]
    select_df = st.dataframe(df_moy, on_select = "rerun", selection_mode = ["multi-row"])

with columns[3] :
    type_groupe = st.radio("Groupe à afficher", ["Top", "Équipe"], horizontal = True)

    if type_groupe == "Top" :
        choix_groupe = st.multiselect("Choix groupe", df_moy.columns, default = df_moy.columns.tolist())

    else :
        choix_groupe = st.multiselect("Choix équipes", sorted(liste_équipe))

#----------------------------------------------- AFFICHAGE GRAPHIQUE ------------------------------------------------------------------------------------


if len(choix_groupe) > 0 :

    st.divider()

    if type_groupe == "Top" :
        df_plot = df_moy.reindex(df_moy.index[::-1])[choix_groupe]
  
    else :
        df_plot = pd.DataFrame(index = dico_annee.keys(), columns = choix_groupe)
        for saison in df_plot.index :
            liste_équipe_i = list(set(choix_groupe) & set(dico_df[saison].index))
            df_plot.loc[saison, :] = dico_df[saison].loc[liste_équipe_i, "Passe"]
        df_plot = df_plot.reindex(df_plot.index[::-1])
    
    fig = plt.figure()
    plt.plot(df_plot, marker = "+", linewidth = 1)
    plt.grid()
    plt.legend(df_plot.columns, fontsize = "small", ncol = 2)
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

    for saison in df_moy.index[select_df.selection.rows] :
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
