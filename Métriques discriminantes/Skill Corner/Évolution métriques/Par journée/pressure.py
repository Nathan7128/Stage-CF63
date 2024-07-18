import pandas as pd

liste_dico = [{"match_drop" : [1550555, 1546206],
                "ranking" : ["AJ Auxerre", "Angers SCO", "AS Saint-Étienne", "Rodez Aveyron", "Paris FC"],
           "annee" : "2023_2024"},
           {"match_drop" : [],
                "ranking" : ["Le Havre AC", "FC Metz", "Girondins de Bordeaux", "SC Bastia", "SM Caen"],
           "annee" : "2022_2023"},
           {"match_drop" : [129364, 128946],
                "ranking" : ["Toulouse FC", "AC Ajaccio", "AJ Auxerre", "Paris FC", "FC Sochaux-Montbéliard"],
           "annee" : "2021_2022"}
           ]

for dico in liste_dico :
     data_import = pd.read_excel(f"Data_file/Métriques Team sur une Saison Ligue 2 SB + SK/{dico["annee"]}/Skill Corner/data_pressure.xlsx", index_col = 0)
     data = data_import[~(data_import.match_id.isin(dico["match_drop"]))]
     data = data[data.quality_check == True]
     data.fillna(0, inplace = True)

     drop = ["quality_check", "player_id", "player_name", "short_name", "player_birthdate", "match_name", "match_date", "team_id",
          "competition_id", "competition_name", "season_id", "season_name", "competition_edition_id", "position", "group", "result", "venue",
          "third", "channel", "adjusted_min_tip_per_match"]
     data.drop(drop, inplace = True, axis = 1)
     sample = data.columns[["sample" in i for i in data.columns]]
     data.drop(sample, inplace = True, axis = 1)

     # AJOUT NUMÉRO DE JOURNÉE AU DATAFRAME
     match_round = pd.read_excel(f"Data_file/Métriques Team sur une Saison Ligue 2 SB + SK/{dico["annee"]}/Skill Corner/match_round.xlsx",
                                   index_col = 0)
     match_round.drop(index = dico["match_drop"], inplace = True)
     data = data.merge(match_round, right_on = "id", left_on = "match_id").drop("match_id", axis = 1)

     # modif métriques ratios

     col_ratio_rep = data.columns[[("ratio" in i) and ("per_100_pressures" in i or "per_match" in i) for i in data.columns]]
     data.drop(col_ratio_rep, inplace = True, axis = 1)

     met_ratio = data.columns[["ratio" in i for i in data.columns]]
     data = data.groupby(["Journée", "team_name"], as_index = True)
     nb_joueur_match = data.apply(len)
     data = data.sum()
     data[met_ratio] = data[met_ratio].divide(nb_joueur_match, axis = 0)

     nb_minute_match = data.pop("minutes_played_per_match")
     data = data.multiply(900/nb_minute_match, axis = 0)

     moyenne_top20 = data.groupby("Journée").mean()
     moyenne_top5 = data[data.index.get_level_values("team_name").isin(dico["ranking"])].groupby("Journée").mean()
     moyenne_bottom15 = data[~data.index.get_level_values("team_name").isin(dico["ranking"])].groupby("Journée").mean()

     data.to_excel(f"Métriques discriminantes/Tableau métriques/Evolutions métriques/Par journée/{dico["annee"]}/Skill Corner/pressure_équipe.xlsx")
     moyenne_top20.to_excel(f"Métriques discriminantes/Tableau métriques/Evolutions métriques/Par journée/{dico["annee"]}/Skill Corner/pressure_top20.xlsx")
     moyenne_top5.to_excel(f"Métriques discriminantes/Tableau métriques/Evolutions métriques/Par journée/{dico["annee"]}/Skill Corner/pressure_top5.xlsx")
     moyenne_bottom15.to_excel(f"Métriques discriminantes/Tableau métriques/Evolutions métriques/Par journée/{dico["annee"]}/Skill Corner/pressure_bottom15.xlsx")