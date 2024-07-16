import matplotlib.pyplot as plt

import pandas as pd

import streamlit as st

top5_import = pd.read_excel(f"Métriques discriminantes/Tableau métriques/Evolutions métriques/Par journée/2021_2022/Skill Corner/passes_top5.xlsx", index_col = 0)
bottom15_import = pd.read_excel(f"Métriques discriminantes/Tableau métriques/Evolutions métriques/Par journée/2021_2022/Skill Corner/passes_bottom15.xlsx", index_col = 0)

top5 = top5_import[top5_import.columns[3]]
bottom15 = bottom15_import[bottom15_import.columns[3]]

fig = plt.figure()
plt.plot(top5)
plt.plot(bottom15)
plt.title(f"Graphe du Top 5 et Bottom 15 pour la métrique {top5_import.columns[3]}\nau cours des journées de la saison 2021_2022",
          fontweight = "heavy", y = 1.05, fontsize = 10)
plt.grid()
plt.legend(["Top 5", "Bottom 15"])
plt.xlabel("Journée")
plt.ylabel("Métrique")
st.pyplot(fig)