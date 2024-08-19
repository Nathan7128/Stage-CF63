import pandas as pd

import sqlite3

connect = sqlite3.connect("database.db")

df_final = pd.DataFrame()

liste_dico = [{"match_drop" : [1550555, 1546206],
                "ranking" : ["AJ Auxerre", "Angers SCO", "AS Saint-Étienne", "Rodez Aveyron", "Paris FC", "SM Caen", "Stade Lavallois Mayenne FC",
           "Amiens Sporting Club", "En Avant de Guingamp", "Pau FC", "Grenoble Foot 38", "Girondins de Bordeaux", "SC Bastia",
           "FC Annecy", "AC Ajaccio", "Dunkerque", "ES Troyes AC", "US Quevilly-Rouen", "US Concarneau", "Valenciennes FC"],
           "saison" : "2023_2024"},
           {"match_drop" : [],
                "ranking" : ["Le Havre AC", "FC Metz", "Girondins de Bordeaux", "SC Bastia", "SM Caen", "En Avant de Guingamp", "Paris FC",
           "AS Saint-Étienne", "FC Sochaux-Montbéliard", "Grenoble Foot 38", "US Quevilly-Rouen", "Amiens Sporting Club", "Pau FC",
           "Rodez Aveyron", "Stade Lavallois Mayenne FC", "Valenciennes FC", "FC Annecy", "Dijon FCO", "Nîmes Olympique", "Chamois Niortais FC"],
           "saison" : "2022_2023"},
           {"match_drop" : [129364, 128946],
                "ranking" : ["Toulouse FC", "AC Ajaccio", "AJ Auxerre", "Paris FC", "FC Sochaux-Montbéliard", "En Avant de Guingamp",
                             "SM Caen", "Le Havre AC", "Nîmes Olympique", "Pau FC", "Dijon FCO", "SC Bastia", "Chamois Niortais FC", 
                             "Amiens Sporting Club", "Grenoble Foot 38", "Valenciennes FC", "Rodez Aveyron", "US Quevilly-Rouen",
                             "Dunkerque", "AS Nancy-Lorraine"],
           "saison" : "2021_2022"}
           ]

for dico in liste_dico :
     data_import = pd.read_excel(f"Data_file/Métriques Team sur une Saison Ligue 2 SB + SK/{dico["saison"]}/Skill Corner/data_pressure.xlsx", index_col = 0)
     data = data_import[~(data_import.match_id.isin(dico["match_drop"]))]
     data = data[data.quality_check == True]
     data.fillna(0, inplace = True)

     drop = ["quality_check", "player_id", "player_name", "short_name", "player_birthdate", "match_name", "match_date", "team_id",
          "competition_id", "competition_name", "season_id", "season_name", "competition_edition_id", "position", "group", "venue",
          "third", "channel", "adjusted_min_tip_per_match"]
     data.drop(drop, inplace = True, axis = 1)
     sample = data.columns[["sample" in i for i in data.columns]]
     data.drop(sample, inplace = True, axis = 1)

     # AJOUT NUMÉRO DE JOURNÉE AU DATAFRAME
     match_round = pd.read_excel(f"Data_file/Métriques Team sur une Saison Ligue 2 SB + SK/{dico["saison"]}/Skill Corner/match_round.xlsx",
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
     data[data.columns.drop("result")] = data[data.columns.drop("result")].multiply(900/nb_minute_match, axis = 0)

     data = data.reindex(dico["ranking"], axis = 0, level = 1)

     data.loc[["win" in i for i in data.result], "result"] = "win"
     data.loc[["lose" in i for i in data.result], "result"] = "lose"
     data.loc[["draw" in i for i in data.result], "result"] = "draw"

     data["result"].to_excel(f"Info matchs/Skill Corner/result_{dico["saison"]}.xlsx")
     data["Saison"] = dico["saison"]

     df_final = pd.concat([df_final, data], axis = 0)

df_final["Compet"] = "Ligue 2"

df_final.to_sql(name = "Pressure", con = connect, if_exists = "replace")

connect.close()