import pandas as pd

import numpy as np

dico_annee = {
    "2021_2022" : 549,
    "2022_2023" : 393,
    "2023_2024" : 243
}

df = pd.DataFrame()

for i in dico_annee.keys() :
    data_import = pd.read_excel(f"Tableau métriques/moyenne/{i}/Stats Bomb/metriques.xlsx", index_col = 0)
    df[i] = data_import.mean(axis = 0)

df["Évolution en %"] = 100*(df["2023_2024"] - df["2021_2022"])/abs(df["2021_2022"])

df = df.reindex(abs(df).sort_values(by = "Évolution en %", ascending = False).index)

df["Évolution en %"] = df["Évolution en %"].round(2)

df.to_excel("Tableau métriques/Evolutions métriques/evo_SB.xlsx", index = True, header = True)