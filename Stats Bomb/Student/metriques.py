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

    nb_matches = team_stat.pop("team_season_matches")
    team_stat.to_excel(f"Tableau métriques\\Valeurs par équipes\\{dico["annee"]}\\Stats Bomb\\metrique.xlsx",
                       header = True,index = True)

    top5 = dico["ranking"][:5]
    top15 = dico["ranking"][5:]
    top5_df = team_stat.loc[top5]
    top15_df = team_stat.loc[top15]

    dic_pvalue = {}
    for i in team_stat.columns :
        ttest, pvalue = ttest_ind(top5_df[i], top15_df[i])
        dic_pvalue[i] = pvalue

    tri = pd.DataFrame(pd.Series(dic_pvalue), columns=["pvalue"]).sort_values(by="pvalue")
    tri.to_excel(f"Tableau métriques\\student\\{dico["annee"]}\\Stats Bomb\\student.xlsx")