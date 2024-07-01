from statsbombpy import sb

import os

import pandas as pd

import numpy as np

from scipy.stats import ttest_ind

import warnings
warnings.filterwarnings("ignore")

email = "nathan.talbot@etu.uca.fr"
password = os.environ["mdp_statsbomb"]
creds = {"user" : email, "passwd" : password}

ligue2_id = 8

liste_dico = [{"comp_id" : 281,
                "ranking" : ["Auxerre", "Angers", "Saint-Étienne", "Rodez", "Paris FC", "Caen", "Laval",
           "Amiens", "Guingamp", "Pau", "Grenoble Foot", "Bordeaux", "Bastia",
           "FC Annecy", "AC Ajaccio", "Dunkerque", "Troyes", "Quevilly Rouen", "Concarneau", "Valenciennes"],
           "annee" : "2023_2024"},
           {"comp_id" : 235,
                "ranking" : ["Le Havre", "Metz", "Bordeaux", "Bastia", "Caen", "Guingamp", "Paris FC",
           "Saint-Étienne", "Sochaux", "Grenoble Foot", "Quevilly Rouen", "Amiens", "Pau",
           "Rodez", "Laval", "Valenciennes", "FC Annecy", "Dijon", "Nîmes", "Chamois Niortais"],
           "annee" : "2022_2023"},
           {"comp_id" : 108,
                "ranking" : ["Toulouse", "AC Ajaccio", "Auxerre", "Paris FC", "Sochaux", "Guingamp", "Caen", "Le Havre", "Nîmes",
                             "Pau", "Dijon", "Bastia", "Chamois Niortais", "Amiens", "Grenoble Foot", "Valenciennes", "Rodez", 
                             "Quevilly Rouen", "Dunkerque", "Nancy"],
           "annee" : "2021_2022"}]

for i in range(3) :

    dico = liste_dico[i]

    team_stat_import = sb.team_season_stats(ligue2_id, dico["comp_id"], creds = creds)
    team_stat = team_stat_import.set_index("team_name").drop(["account_id", "team_id", "competition_id", "competition_name",
                                        "season_id", "season_name", "team_female", "team_season_minutes"], axis = 1)
    team_stat = team_stat.reindex(dico["ranking"])

    top5 = dico["ranking"][:5]
    top15 = dico["ranking"][5:]
    top5_df = team_stat.loc[top5]
    top15_df = team_stat.loc[top15]

    df_final = pd.DataFrame(index = top5_df.columns)

    df_final["Moyenne Top 5"] = top5_df.mean(axis = 0)
    df_final["Moyenne Bottom 15"] = top15_df.mean(axis = 0)

    df_final["Ratio Moyennes"] = df_final["Moyenne Top 5"]/df_final["Moyenne Bottom 15"]
    df_final.loc[df_final["Ratio Moyennes"] < 1, "Ratio Moyennes"] **= -1

    df_final["Ecart type Top 5"] = top5_df.std(axis = 0)
    df_final["Ecart type Bottom 15"] = top15_df.std(axis = 0)

    df_final["Min Top 5"] = top5_df.min(axis = 0)
    df_final["Min Bottom 15"] = top15_df.min(axis = 0)

    df_final["Max Top 5"] = top5_df.max(axis = 0)
    df_final["Max Bottom 15"] = top15_df.max(axis = 0)

    df_final.replace([np.inf, -np.inf], 0, inplace=True)
    df_final.fillna(0, inplace = True)
    df_final.sort_values(by = "Ratio Moyennes", inplace = True, ascending = False)

    df_final.to_excel(f"Tableau métriques\\moyenne\\{dico["annee"]}\\Stats Bomb\\moyenne_metriques.xlsx")