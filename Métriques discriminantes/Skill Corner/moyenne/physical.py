import pandas as pd


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

def rename_col(col) :
    if "full_all" in col :
        return col.replace("full_all", "per_Match")
    elif "full_otip_p30otip" in col :
        return col.replace("full_otip_p30otip", "per30otip")
    elif "full_tip_p30tip" in col :
        return col.replace("full_tip_p30tip", "per30tip")
    else :
        return col

for i in range(3) :

     dico = liste_dico[i]

     data_import = pd.read_excel(f"Data_file/Métriques Team sur une Saison Ligue 2 SB + SK/{dico["annee"]}/Skill Corner/data_physical.xlsx", index_col = 0)     
     data = data_import.set_index("team_name").fillna(0)

     nb_matchs = pd.Series(index = data.index.unique())
     for team in nb_matchs.index :
          nb_matchs[team] = len(data.loc[team].match_id.unique())
     nb_matchs = nb_matchs.reindex(dico["ranking"])

     drop = ["player_name", "player_short_name", "psv99", "player_id", "player_birthdate", "team_id", "match_name", "match_date", "competition_name", "competition_id", "season_name",
          "season_id", "competition_edition_id", "position", "position_group", "minutes_full_tip", "minutes_full_otip", "physical_check_passed"]

     data.drop(drop, inplace = True, axis = 1)

     data.rename(columns = rename_col, inplace = True)

     data = data.groupby(["team_name", "match_id"]).sum()

     nb_minute_match = data.pop("minutes_per_Match")
     data = data.multiply(900/nb_minute_match, axis = 0)

     data = data.reset_index().drop("match_id", axis = 1).groupby("team_name", as_index = True).sum().reindex(dico["ranking"])

     data = data.divide(nb_matchs, axis = 0)

     data.to_excel(f"Métriques discriminantes/Tableau métriques/moyenne/{dico["annee"]}/Skill Corner/metrique_physical.xlsx")