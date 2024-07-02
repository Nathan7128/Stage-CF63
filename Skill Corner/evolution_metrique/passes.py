from skillcorner.client import SkillcornerClient

import pandas as pd

import numpy as np

import os

secret_password = os.getenv("mdp_skillcorner")
client = SkillcornerClient(username = "Nathan.talbot@etu.uca.fr", password = secret_password)

dico_annee = {
    "2021_2022" : 549,
    "2022_2023" : 393,
    "2023_2024" : 243
}

liste_met = pd.read_excel("Tableau métriques/liste_métriques.xlsx", header = 0)
liste_met = liste_met["passes"]
liste_met.dropna(inplace = True)

df = pd.DataFrame(index = liste_met, columns = dico_annee.keys())

for i in dico_annee.keys() :
    data_import = pd.read_excel(f"data/{i}/Skill Corner/data_passes.xlsx")
    data = pd.DataFrame(data_import).set_index("team_name")
    data = data[data.quality_check == True]
    data.fillna(0, inplace = True)
    nb_matchs = pd.Series(index = data.index.unique())
    for team in nb_matchs.index :
        nb_matchs[team] = len(data.loc[team].match_id.unique())

    drop = ["quality_check", "player_id", "player_name", "short_name", "player_birthdate", "match_id", "match_name", "match_date", "team_id",
        "competition_id", "competition_name", "season_id", "season_name", "competition_edition_id", "position", "group", "result", "venue",
        "third", "channel", "minutes_played_per_match", "adjusted_min_tip_per_match"]
    data.drop(drop, inplace = True, axis = 1)

    data = data.groupby("team_name").sum()

    data = data.divide(nb_matchs, axis = 0)
    df[i] = data.mean(axis = 0)

df["Évolution en %"] = 100*(df["2023_2024"] - df["2021_2022"])/abs(df["2021_2022"])

df.sort_values(by = "Évolution en %", ascending = False, inplace = True)

df.to_excel("Tableau métriques/Evolutions métriques/evo_passes.xlsx", index = True, header = True)