import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("Moyenne du nombre de passes avant un but d'une compétition")


#----------------------------------------------- DEFINITION DICTIONNAIRE ------------------------------------------------------------------------------------


dico_saison = {
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


for saison in dico_saison.keys() :
    df = pd.read_excel(f"Passes avant un but/{saison}.xlsx", index_col = 0)
    df = df.reindex(dico_saison[saison])
    dico_df[saison] = df
    liste_équipe += df.index.tolist()

liste_équipe = list(set(liste_équipe))

st.divider()

columns = st.columns([2, 1, 3], vertical_alignment = "center", gap = "large")
with columns[1] :
   choix_groupe = st.multiselect("Groupe à afficher", groupe_non_vide, default = groupe_non_vide.tolist())

with columns[2] :
    choix_équipe = st.multiselect("Équipe à afficher", sorted(liste_équipe))


df_final = pd.DataFrame(index = dico_saison.keys())

for saison in dico_saison.keys() :
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

if len(df_plot) > 0 :

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