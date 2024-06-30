import streamlit as st
import pandas as pd

col1, col2 = st.columns(2)

with col1 :
    annee = st.radio("Choisir année", options = ["2021_2022", "2022_2023", "2023_2024"])

with col2 :
    if annee != "2021_2022" :
        choix_data = st.radio("Fournisseur data", options = ["Skill Corner", "Stats Bomb"])
    else :
        choix_data = st.radio("Fournisseur data", options = ["Skill Corner"])
    if choix_data == "Skill Corner" :
        path_student = ["student_physical.xlsx", "student_running.xlsx", "student_pressure.xlsx", "student_passe.xlsx"]
        path_metrique = ["metrique_physical.xlsx", "metrique_running.xlsx", "metrique_pressure.xlsx", "metrique_passe.xlsx"]
        liste_cat_met = ["Physiques", "Courses sans ballon avec la possession",
                    "Action sous pression", "Passes à un coéquipier effectuant une course"]
        cat_met = st.radio("Catégorie de métrique", liste_cat_met)
        index_cat = liste_cat_met.index(cat_met)
        file_student = path_student[index_cat]
        file_metrique = path_metrique[index_cat]
    else :
        file_student = "student.xlsx"
        file_metrique = "metrique.xlsx"
    
st.divider()

student = pd.read_excel(f"Tableau métriques/student/{annee}/{choix_data}/{file_student}")
student.rename({student.columns[0] : "Métriques"}, axis = 1, inplace = True)
pvalue = st.number_input("Valeur max pvalue", min_value=0.0, max_value=1.0, step = 0.001, format="%.3f")
student_sort = student[student.pvalue < pvalue]
st.write(f"Nombre de métriques gardées : {student_sort.shape[0]}")

st.divider()

st.markdown("<p style='text-align: center;'>Résultats des tests de student pour chaque métrique : plus la p-value est petite, plus la métrique différencie le top 5 des autres équipes de Ligue 2</p>", unsafe_allow_html=True)
st.dataframe(student_sort, width = 500, hide_index=True)

st.divider()



metrique_student = pd.read_excel(f"Tableau métriques/Valeurs par équipes/{annee}/{choix_data}/{file_metrique}", index_col=0)
metrique_student_sort = metrique_student[student[student.pvalue < pvalue]["Métriques"].tolist()]
st.markdown(f"<p style='text-align: center;'>Tableau des métriques (avec pvalue < {pvalue}) par équipes, en moyenne par match</p>", unsafe_allow_html=True)
st.dataframe(metrique_student_sort)