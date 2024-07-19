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
           {"comp_id" : 90,
                "ranking" : ["Troyes", "Clermont Foot", "Toulouse", "Grenoble Foot", "Paris FC", "Auxerre", "Sochaux", "Nancy",
                             "Guingamp", "Amiens", "Valenciennes", "Le Havre", "AC Ajaccio", "Pau", "Rodez", "Dunkerque", "Caen", 
                             "Chamois Niortais", "Chambly", "Châteauroux"],
           "annee" : "2020_2021"}
           ]

for i in range(4) :

     dico = liste_dico[i]

     data_import = pd.read_excel(f"Data_file/Métriques Team sur une Saison Ligue 2 SB + SK/{dico["annee"]}/Stats Bomb/data.xlsx", index_col = 0)

     data = data_import.set_index("team_name")

     nb_matchs = data.team_season_matches

     drop = ["account_id", "team_id", "competition_id", "competition_name", "season_id", "season_name", "team_female", "team_season_matches", "team_season_minutes"]
     data.drop(drop, inplace = True, axis = 1)

     data = data.reindex(dico["ranking"])

     data.to_excel(f"Métriques discriminantes/Tableau métriques\\moyenne\\{dico["annee"]}\\Stats Bomb\\metriques.xlsx")