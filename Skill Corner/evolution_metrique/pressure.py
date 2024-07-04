import pandas as pd

liste_annees = ["2021_2022", "2022_2023", "2023_2024"]
top_5_df_mean = pd.DataFrame()
top_15_df_mean = pd.DataFrame()

for i in liste_annees :
    data_import = pd.read_excel(f"Tableau métriques/moyenne/{i}/Skill Corner/metrique_pressure.xlsx", index_col = 0)
    top_5_df_mean[i] = data_import.loc[data_import.index[:5]].mean(axis = 0)
    top_15_df_mean[i] = data_import.loc[data_import.index[5:]].mean(axis = 0)

top_5_df_mean["Évolution en %"] = 100*(top_5_df_mean["2023_2024"] - top_5_df_mean["2021_2022"])/abs(top_5_df_mean["2021_2022"])
top_5_df_mean = top_5_df_mean.reindex(abs(top_5_df_mean).sort_values(by = "Évolution en %", ascending = False).index)
multi = [top_5_df_mean.index, ["Top 5", "Top 15"]]
multi = pd.MultiIndex.from_product(multi, names = ["Métriques", "Top"])
df = pd.DataFrame(columns = liste_annees, index = multi)

for i in top_5_df_mean.index :
    df.loc[i, "Top 5"] = top_5_df_mean.loc[i].drop(["Évolution en %"])
    df.loc[i, "Top 15"] = top_15_df_mean.loc[i]

df["Évolution en %"] = 100*(df["2023_2024"] - df["2021_2022"])/abs(df["2021_2022"])

df["Évolution en %"] = df["Évolution en %"].round(2)


df.to_excel("Tableau métriques/Evolutions métriques/evo_pressure.xlsx", index = True, header = True)