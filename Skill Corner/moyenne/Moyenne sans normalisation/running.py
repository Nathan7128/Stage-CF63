from skillcorner.client import SkillcornerClient

import pandas as pd

import numpy as np

import os

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

     running_data_json = client.get_in_possession_off_ball_runs(params = {'competition_edition': dico["comp_id"], "group_by" : "team",
               "run_type" : ["run_in_behind", "run_ahead_of_the_ball", "support_run", "pulling_wide_run", "coming_short_run", "underlap_run",
                              "overlap_run", "dropping_off_run", "pulling_half_space_run", "cross_receiver_run"]})
     running_data = pd.DataFrame(running_data_json).set_index("team_name")
     running_data.drop(["team_id", "third", "channel", "minutes_played_per_match", "adjusted_min_tip_per_match",
                    "count_match", "count_match_failed", "count_runs_in_behind_in_sample"], inplace = True, axis = 1)
     running_data = running_data.reindex(dico["ranking"])

     top5 = dico["ranking"][:5]
     top15 = dico["ranking"][5:]
     top5_df = running_data.loc[top5]
     top15_df = running_data.loc[top15]

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

     df_final.to_excel(f"Tableau métriques\\moyenne\\{dico["annee"]}\\Skill Corner\\moyenne_running.xlsx")