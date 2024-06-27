import streamlit as st
import pandas as pd

def centered_text(text):
    return (f'<div style="text-align: center">{text}</div>')

liste_cat_met = ["Physiques", "Courses sans ballon avec la possession", "Action sous pression",
                 "Passes à un coéquipier effectuant une course"]
path_student = ["student_physical.xlsx", "student_running.xlsx", "student_pressure.xlsx", "student_passe.xlsx"]
path_metrique = ["metrique_physical.xlsx", "metrique_running.xlsx", "metrique_pressure.xlsx", "metrique_passe.xlsx"]

cat_met = st.radio("Catégorie de métrique", liste_cat_met)

st.divider()

index_cat = liste_cat_met.index(cat_met)
student = pd.DataFrame(pd.read_excel(path_student[index_cat]))
student.rename({student.columns[0] : "Métriques"}, axis = 1, inplace = True)
pvalue = st.number_input("Valeur max pvalue", min_value=0.0, max_value=1.0, step = 0.001, format="%.3f")
student_sort = student[student.pvalue < pvalue]
st.write(f"Nombre de métriques gardées : {student_sort.shape[0]}")

st.divider()

st.markdown("<p style='text-align: center;'>Résultats des tests de student pour chaque métrique : plus la p-value est petite, plus la métrique différencie le top 5 des autres équipes de Ligue 2</p>", unsafe_allow_html=True)
st.dataframe(student_sort, hide_index=True)

st.divider()

metrique = pd.DataFrame(pd.read_excel(path_metrique[index_cat], index_col=0))
metrique_sort = metrique[student[student.pvalue < pvalue]["Métriques"].tolist()]
st.markdown(f"<p style='text-align: center;'>Tableau des métriques (avec pvalue < {pvalue}) par équipes, en moyenne par match</p>", unsafe_allow_html=True)
st.dataframe(metrique_sort)