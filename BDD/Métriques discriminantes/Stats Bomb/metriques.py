import pandas as pd


dico_rank = {
     "2023_2024" : ["Auxerre", "Angers", "Saint-Étienne", "Rodez", "Paris FC", "Caen", "Laval", "Amiens", "Guingamp", "Pau",
          "Grenoble Foot", "Bordeaux", "Bastia", "FC Annecy", "AC Ajaccio", "Dunkerque", "Troyes", "Quevilly Rouen", "Concarneau",
          "Valenciennes"],
     "2022_2023" : ["Le Havre", "Metz", "Bordeaux", "Bastia", "Caen", "Guingamp", "Paris FC", "Saint-Étienne", "Sochaux", "Grenoble Foot",
          "Quevilly Rouen", "Amiens", "Pau", "Rodez", "Laval", "Valenciennes", "FC Annecy", "Dijon", "Nîmes", "Chamois Niortais"],
     "2021_2022" : ["Toulouse", "AC Ajaccio", "Auxerre", "Paris FC", "Sochaux", "Guingamp", "Caen", "Le Havre", "Nîmes", "Pau", "Dijon",
          "Bastia", "Chamois Niortais", "Amiens", "Grenoble Foot", "Valenciennes", "Rodez",  "Quevilly Rouen", "Dunkerque", "Nancy"],
     "2020_2021" : ["Troyes", "Clermont Foot", "Toulouse", "Grenoble Foot", "Paris FC", "Auxerre", "Sochaux", "Nancy", "Guingamp",
          "Amiens", "Valenciennes", "Le Havre", "AC Ajaccio", "Pau", "Rodez", "Dunkerque", "Caen",  "Chamois Niortais", "Chambly",
          "Châteauroux"]
}

for saison in dico_rank.keys() :

     data_import = pd.read_excel(f"Data_file/Métriques Team sur une Saison Ligue 2 SB + SK/{saison}/Stats Bomb/data.xlsx", index_col = 0)

     data = data_import.set_index("team_name")

     nb_matchs = data.team_season_matches

     drop = ["account_id", "team_id", "competition_id", "competition_name", "season_id", "season_name", "team_female",
          "team_season_matches", "team_season_minutes"]
     data.drop(drop, inplace = True, axis = 1)

     data = data.reindex(dico_rank[saison])

     data.to_excel(f"Métriques discriminantes/Tableau métriques\\{saison}\\Stats Bomb\\metriques.xlsx")