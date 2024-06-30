from skillcorner.client import SkillcornerClient

import pandas as pd

import numpy as np

import os

secret_password = os.getenv("mdp_skillcorner")
client = SkillcornerClient(username = "Nathan.talbot@etu.uca.fr", password = secret_password)

from scipy.stats import ttest_ind


liste_dico = [{"comp_id" : 549,
                "ranking" : ["AJ Auxerre", "Angers SCO", "AS Saint-Étienne", "Rodez Aveyron", "Paris FC", "SM Caen", "Stade Lavallois Mayenne FC",
           "Amiens Sporting Club", "En Avant de Guingamp", "Pau FC", "Grenoble Foot 38", "Girondins de Bordeaux", "SC Bastia",
           "FC Annecy", "AC Ajaccio", "Dunkerque", "ES Troyes AC", "US Quevilly-Rouen", "US Concarneau", "Valenciennes FC"],
           "annee" : "2023_2024"},
           {"comp_id" : 393,
                "ranking" : ["Le Havre AC", "FC Metz", "Girondins de Bordeaux", "SC Bastia", "SM Caen", "En Avant de Guingamp", "Paris FC",
           "AS Saint-Étienne", "FC Sochaux-Montbéliard", "Grenoble Foot 38", "US Quevilly-Rouen", "Amiens Sporting Club", "Pau FC",
           "Rodez Aveyron", "Stade Lavallois Mayenne FC", "Valenciennes FC", "FC Annecy", "Dijon FCO", "Nîmes Olympique", "Chamois Niortais FC"],
           "annee" : "2022_2023"},
           {"comp_id" : 243,
                "ranking" : ["Toulouse FC", "AC Ajaccio", "AJ Auxerre", "Paris FC", "FC Sochaux-Montbéliard", "En Avant de Guingamp",
                             "SM Caen", "Le Havre AC", "Nîmes Olympique", "Pau FC", "Dijon FCO", "SC Bastia", "Chamois Niortais FC", 
                             "Amiens Sporting Club", "Grenoble Foot 38", "Valenciennes FC", "Rodez Aveyron", "US Quevilly-Rouen",
                             "Dunkerque", "AS Nancy-Lorraine"],
           "annee" : "2021_2022"}
           ]

for i in range(3) :
     dico = liste_dico[i]
     pressure_data_json = client.get_in_possession_on_ball_pressures(params = {'competition_edition': dico["comp_id"], "group_by" : "team",
                                                                      "pressure_intensity" : ["low", "medium", "high"]})
     pressure_data = pd.DataFrame(pressure_data_json).set_index("team_name")
     pressure_data.drop(["team_id", "third", "channel", "minutes_played_per_match", "adjusted_min_tip_per_match",
                         "count_match", "count_match_failed", "count_low_pressures_received_in_sample"], inplace = True, axis = 1)
     pressure_data = pressure_data.reindex(dico["ranking"])
     pressure_data.to_excel(f"Tableau métriques\\Valeurs par équipes\\{dico["annee"]}\\Skill Corner\\metrique_pressure.xlsx", header = True, index = True)
     
     top5 = dico["ranking"][:5]
     top15 = dico["ranking"][5:]
     top5_df = pressure_data.loc[top5]
     top15_df = pressure_data.loc[top15]
     
     dic_pvalue = {}
     for i in pressure_data.columns :
          ttest, pvalue = ttest_ind(top5_df[i], top15_df[i])
          dic_pvalue[i] = pvalue
     
     tri = pd.DataFrame(pd.Series(dic_pvalue), columns=["pvalue"]).sort_values(by="pvalue")
     tri.to_excel(f"Tableau métriques\\student\\{dico["annee"]}\\Skill Corner\\student_pressure.xlsx")