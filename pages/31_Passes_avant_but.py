import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("Moyenne du nombre de passes avant un but d'une compétition")

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




dico_df = {}

df_moy = pd.DataFrame(index = dico_annee.keys(), columns = ["Top 5", "Bottom 15", "Global"])

for i in dico_annee.keys() :
    df = pd.read_excel(f"Passes avant un but/{i}.xlsx", index_col = 0)
    df = df.reindex(dico_annee[i])
    df_moy.loc[i, "Top 5"] = df.loc[df["Top 5"] == 1, "Passe"].mean()
    df_moy.loc[i, "Bottom 15"] = df.loc[df["Top 5"] == 0, "Passe"].mean()
    df_moy.loc[i, "Global"] = df["Passe"].mean()
    dico_df[i] = df

st.divider()

with st.columns([1, 1, 3, 2])[2] :
    df_moy.index = ["2023/2024", "2022/2023", "2021/2022", "2020/2021"]
    annee_select = st.dataframe(df_moy, on_select = "rerun", selection_mode = "single-row")


df_moy = df_moy.reindex(df_moy.index[::-1])
fig = plt.figure()
plt.plot(df_moy, linewidth = 1)
plt.grid()
plt.legend(df_moy.columns, fontsize = "small", ncol = 2)
plt.xlabel("Saison", fontsize = "small", fontstyle = "italic", labelpad = 10)
plt.ylabel("Passes", fontsize = "small", fontstyle = "italic", labelpad = 10)
plt.tick_params(labelsize = 8)
ax = plt.gca()
ax.spines[:].set_visible(False)

st.pyplot(fig)


st.markdown("<p style='text-align: center;'>Choisir une saison</p>", unsafe_allow_html=True)

# if len(annee_select.selection.rows) == 1 :
#     annee = df_moy.index[annee_select.selection.rows][0]
#     with col1 :
#         st.dataframe(dico_df[annee.replace("/", "_")].drop("Top 5", axis = 1), height = 733)