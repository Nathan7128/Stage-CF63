import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("Évolution des métriques au cours des saisons")

dico_met = {
    "Physiques" : ["physical", {"30 min. tip" : "_per30tip", "30 min. otip" : "_per30otip",
        "Match all possession" : "_per_Match"}],
    "Courses sans ballon avec la possession" : ["running", {"Match" : "per_match",
        "100 runs" : "per_100_runs", "30 min. tip" : "per_30_min_tip"}, ["runs_in_behind", "runs_ahead_of_the_ball",
        "support_runs", "pulling_wide_runs", "coming_short_runs", "underlap_runs", "overlap_runs", "dropping_off_runs",
        "pulling_half_space_runs", "cross_receiver_runs"]],
    "Action sous pression" : ["pressure", {"Match" : "per_match",
        "100 pressures" : "per_100_pressures", "30 min. tip" : "per_30_min_tip"}, ["low", "medium", "high"]],
    "Passes à un coéquipier effectuant une course" : ["passes", {"Match" : "per_match",
        "100 passes opportunities" : "_per_100_pass_opportunities", "30 min. tip" : "per_30_min_tip"}, ["runs_in_behind",
        "runs_ahead_of_the_ball", "support_runs", "pulling_wide_runs", "coming_short_runs", "underlap_runs", "overlap_runs",
        "dropping_off_runs", "pulling_half_space_runs", "cross_receiver_runs"]]
    }

columns = st.columns([1, 2, 1, 2], gap = "large")

with columns[0] :
    choix_data = st.radio("Fournisseur data", options = ["Skill Corner", "Stats Bomb"])

if choix_data == "Skill Corner" :
    with columns[1] :
        cat_met = st.radio("Catégorie de métrique", dico_met.keys(), horizontal = True)

    df = pd.read_excel(f"Métriques discriminantes/Tableau métriques/Evolutions métriques/Par saison/evo_{dico_met[cat_met][0]}.xlsx", index_col = [0, 1])

    with columns[2] :
        moy_met = st.multiselect("Moyenne de la métrique", list(dico_met[cat_met][1].keys()), default = list(dico_met[cat_met][1].keys()))

    col_keep = [False]*len(df)
    for cat_type in moy_met :
            cat_type = dico_met[cat_met][1][cat_type]
            col_keep = np.logical_or(col_keep, [(cat_type in i) or ("ratio" in i) for i in df.index.get_level_values(0)])
    df = df.iloc[col_keep, :]

    if cat_met != "Physiques" :
        with columns[3] :
            type_met = st.multiselect("Type de la métrique", dico_met[cat_met][2], default = dico_met[cat_met][2])
            col_keep = [False]*len(df)
            for cat_type in type_met :
                col_keep = np.logical_or(col_keep, [(cat_type in i) or ("ratio" in i and cat_type in i) for i in df.index.get_level_values(0)])
            df = df.iloc[col_keep]

else :
    df = pd.read_excel("Métriques discriminantes/Tableau métriques/Evolutions métriques/Par saison/evo_SB.xlsx", index_col = [0, 1])

st.divider()

def couleur_bg_df(col) :
    if col.name == "Évolution en %" :
        color = []
        for met in df.index :
            if df.loc[met, "2023/2024"] >= df.loc[met, "2022/2023"] and df.loc[met, "2022/2023"] >= df.loc[met, "2021/2022"] :
                color.append("background-color: rgba(0, 255, 0, 0.3)")
            elif df.loc[met, "2023/2024"] >= df.loc[met, "2022/2023"] and df.loc[met, "2022/2023"] < df.loc[met, "2021/2022"] :
                color.append("background-color: rgba(255, 255, 0, 0.3)")
            elif df.loc[met, "2023/2024"] < df.loc[met, "2022/2023"] and df.loc[met, "2022/2023"] >= df.loc[met, "2021/2022"] :
                color.append("background-color: rgba(255, 130, 0, 0.5)")
            else :
                color.append("background-color: rgba(255, 0, 0, 0.3)")
        return color
                    
    else :
        return ['']*len(df)

def couleur_text_df(row) :
    color = ['']
    if choix_data == "Stats Bomb" :
        if row["2021/2022"] > row["2020/2021"] :
            color.append("color : green")
        else :
            color.append("color : red")
    if row["2022/2023"] > row["2021/2022"] :
        color.append("color : green")
    else :
        color.append("color : red")
    if row["2023/2024"] > row["2022/2023"] :
        color.append("color : green")
    else :
        color.append("color : red")
    color.append('')
    return color

df.rename({"2023_2024" : "2023/2024", "2022_2023" : "2022/2023", "2021_2022" : "2021/2022", "2020_2021" : "2020/2021"}, axis = 1,
          inplace = True)

df_style = df.style.apply(couleur_bg_df, axis = 0)
df_style = df_style.apply(couleur_text_df, axis = 1)


st.markdown("<p style='text-align: center;'>Tableau de l'évolution de chaque métrique entre la saison 2021/2022 et 2023/2024</p>", unsafe_allow_html=True)

met_sel = st.dataframe(df_style, width = 10000, on_select = "rerun", selection_mode = "multi-row")

st.markdown("<p style='text-align: center;'>Code couleur de l'évolution des métriques entre la saison 2021/2022 et 2023/2024 :</p>", unsafe_allow_html=True)

st.dataframe(pd.DataFrame(columns = ["salut", "ok", "daccord"]))
st.dataframe()
# st.markdown(
#     """
#     <style>
#     .highlight1 {
#         background-color: green; /* Couleur de l'arrière-plan */
#         padding: 10px;
#         border-radius: 5px;
#         font-size: 20px;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# st.markdown(
#     """
#     <style>
#     .highlight2 {
#         background-color: yellow; /* Couleur de l'arrière-plan */
#         padding: 10px;
#         border-radius: 5px;
#         font-size: 20px;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# st.markdown(
#     """
#     <style>
#     .highlight3 {
#         background-color: orange; /* Couleur de l'arrière-plan */
#         padding: 10px;
#         border-radius: 5px;
#         font-size: 20px;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# st.markdown(
#     """
#     <style>
#     .highlight4 {
#         background-color: red; /* Couleur de l'arrière-plan */
#         padding: 10px;
#         border-radius: 5px;
#         font-size: 20px;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# # Afficher le texte avec le style défini

# columns = st.columns(4)
# with columns[0] :
#     st.markdown('<div class="highlight1">augmentation constante</div>', unsafe_allow_html=True)
# with columns[1] :
#     st.markdown('<div class="highlight2">tendance haussière</div>', unsafe_allow_html=True)
# with columns[2] :
#     st.markdown('<div class="highlight3">tendance baissière</div>', unsafe_allow_html=True)
# with columns[3] :
#     st.markdown('<div class="highlight4">diminution constante</div>', unsafe_allow_html=True)

if len(met_sel.selection.rows) > 0 :

    st.divider()

    evo_graphe = df_style.data.iloc[met_sel.selection.rows].drop("Évolution en %", axis = 1)
    new_index = []
    for i in df_style.index[met_sel.selection.rows] :
        new_index.append(i[1] + " - " + i[0])
    evo_graphe = evo_graphe.reset_index()
    evo_graphe.index = new_index
    # couleur = (evo_graphe.Top == "Top 5").replace({True : "#FF0000", False : '#0000FF'})
    evo_graphe = evo_graphe.drop(["Métriques", "Top"], axis = 1).T
    fig = plt.figure()
    plt.plot(evo_graphe, linewidth = 0.7)
    plt.title("Graphique de l'évolution des métriques sélectionnées", fontweight = "heavy", y = 1.05, fontsize = 9)
    plt.grid()
    plt.legend(evo_graphe.columns, loc = "lower center", bbox_to_anchor=(0.5, -0.35 - 0.08*(int((len(evo_graphe.columns) + 1)/2) - 1)),
               fontsize = "small", ncol = 2)
    plt.xlabel("Saison", fontsize = "small", fontstyle = "italic", labelpad = 10)
    plt.ylabel("Métrique", fontsize = "small", fontstyle = "italic", labelpad = 10)
    plt.tick_params(labelsize = 8)
    ax = plt.gca()
    ax.spines[:].set_visible(False)
    st.pyplot(fig)