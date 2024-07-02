from skillcorner.client import SkillcornerClient

import pandas as pd

import numpy as np

import os

from sklearn.preprocessing import StandardScaler

secret_password = os.getenv("mdp_skillcorner")
client = SkillcornerClient(username = "Nathan.talbot@etu.uca.fr", password = secret_password)



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

     physical_data_json = client.get_physical(params = {"data_version" : 3, 'competition_edition': dico["comp_id"], "possession" : ["tip", "otip"], "physical_check_passed" : "true"})     
     physical_data = pd.DataFrame(physical_data_json).set_index("team_name").fillna(0)

     nb_matchs = pd.Series(index = physical_data.index.unique())
     for team in nb_matchs.index :
          nb_matchs[team] = len(physical_data.loc[team].match_id.unique())
     nb_matchs.reindex(dico["ranking"])

     drop = ["player_name", "player_short_name", "player_id", "player_birthdate", "team_id", "match_name", "match_id", "match_date", "competition_name", "competition_id", "season_name",
             "season_id", "competition_edition_id", "position", "position_group", "minutes_full_tip", "minutes_full_otip", "physical_check_passed"]

     physical_data.drop(drop, inplace = True, axis = 1)

     physical_data = physical_data.groupby("team_name").sum().reindex(dico["ranking"])

     scaler = StandardScaler()
     physical_data_standard = scaler.fit_transform(physical_data)
     physical_data_standard = pd.DataFrame(physical_data_standard, index = physical_data.index, columns = physical_data.columns)

     physical_data = physical_data.divide(nb_matchs, axis = 0).reindex(dico["ranking"])

     top5 = dico["ranking"][:5]
     top15 = dico["ranking"][5:]
     top5_df = physical_data.loc[top5]
     top15_df = physical_data.loc[top15]
     top5_df_standard = physical_data_standard.loc[top5]
     top15_df_standard = physical_data_standard.loc[top15]

     df_final = pd.DataFrame(index = top5_df.columns)

     df_final["Moyenne Top 5"] = top5_df.mean(axis = 0)
     df_final["Moyenne Bottom 15"] = top15_df.mean(axis = 0)

     df_final["Diff Moyennes\n(données normalisées)"] = abs(top5_df_standard.mean(axis = 0) - top15_df_standard.mean(axis = 0))

     df_final["Ecart type Top 5"] = top5_df.std(axis = 0)
     df_final["Ecart type Bottom 15"] = top15_df.std(axis = 0)

     df_final["Min Top 5"] = top5_df.min(axis = 0)
     df_final["Min Bottom 15"] = top15_df.min(axis = 0)

     df_final["Max Top 5"] = top5_df.max(axis = 0)
     df_final["Max Bottom 15"] = top15_df.max(axis = 0)

     df_final.sort_values(by = "Diff Moyennes\n(données normalisées)", inplace = True, ascending = False)

     df_final.to_excel(f"Tableau métriques\\moyenne\\{dico["annee"]}\\Skill Corner\\moyenne_physical.xlsx")
     physical_data.to_excel(f"Tableau métriques\\moyenne\\{dico["annee"]}\\Skill Corner\\metrique_physical.xlsx", header = True, index = True)