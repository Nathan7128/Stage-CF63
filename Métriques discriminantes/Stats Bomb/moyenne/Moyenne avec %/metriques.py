import pandas as pd


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
           "annee" : "2021_2022"},
           {"comp_id" : 108,
                "ranking" : ["Troyes", "Clermont Foot", "Toulouse", "Grenoble Foot", "Paris FC", "Auxerre", "Sochaux", "Nancy",
                             "Guingamp", "Amiens", "Valenciennes", "Le Havre", "AC Ajaccio", "Pau", "Rodez", "Dunkerque", "Caen", 
                             "Chamois Niortais", "Chambly", "Châteauroux"],
           "annee" : "2020_2021"}
           ]

for i in range(4) :

     dico = liste_dico[i]

     data_import = pd.read_excel(f"Métriques discriminantes/data/{dico["annee"]}/Stats Bomb/data.xlsx", index_col = 0)

     data = data_import.set_index("team_name")

     nb_matchs = data.team_season_matches

     drop = ["account_id", "team_id", "competition_id", "competition_name", "season_id", "season_name", "team_female", "team_season_matches", "team_season_minutes"]
     data.drop(drop, inplace = True, axis = 1)

     data = data.reindex(dico["ranking"])

     top5 = dico["ranking"][:5]
     top15 = dico["ranking"][5:]
     top5_df = data.loc[top5]
     top15_df = data.loc[top15]

     df_final = pd.DataFrame(index = top5_df.columns)

     df_final["Moyenne Top 5"] = top5_df.mean(axis = 0)
     df_final["Moyenne Bottom 15"] = top15_df.mean(axis = 0)

     df_final["Diff. Top 5 avec Bottom 15 en %"] = (100*(df_final["Moyenne Top 5"] - df_final["Moyenne Bottom 15"])/abs(df_final["Moyenne Bottom 15"])).round(2)

     df_final["Ecart type Top 5"] = top5_df.std(axis = 0)
     df_final["Ecart type Bottom 15"] = top15_df.std(axis = 0)

     df_final["Min Top 5"] = top5_df.min(axis = 0)
     df_final["Min Bottom 15"] = top15_df.min(axis = 0)

     df_final["Max Top 5"] = top5_df.max(axis = 0)
     df_final["Max Bottom 15"] = top15_df.max(axis = 0)

     df_final = df_final.reindex(abs(df_final).sort_values(by = "Diff. Top 5 avec Bottom 15 en %", ascending = False).index)

     df_final.to_excel(f"Métriques discriminantes/Tableau métriques\\moyenne\\{dico["annee"]}\\Stats Bomb\\moyenne_metriques.xlsx")

     data.to_excel(f"Métriques discriminantes/Tableau métriques\\moyenne\\{dico["annee"]}\\Stats Bomb\\metriques.xlsx")