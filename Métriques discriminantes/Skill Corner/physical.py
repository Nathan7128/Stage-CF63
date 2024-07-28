import pandas as pd

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

def rename_col(col) :
    if "full_all" in col :
        return col.replace("full_all", "per_Match")
    elif "full_otip_p30otip" in col :
        return col.replace("full_otip_p30otip", "per30otip")
    elif "full_tip_p30tip" in col :
        return col.replace("full_tip_p30tip", "per30tip")
    else :
        return col

for dico in liste_dico :
    data_import = pd.read_excel(f"Data_file/Métriques Team sur une Saison Ligue 2 SB + SK/{dico["saison"]}/Skill Corner/data_physical.xlsx", index_col = 0)
    data = data_import[~(data_import.match_id.isin(dico["match_drop"]))]
    data.fillna(0, inplace = True)

    drop = ["player_name", "player_short_name", "psv99", "player_id", "player_birthdate", "team_id", "match_name", "match_date", "competition_name", "competition_id", "season_name",
            "season_id", "competition_edition_id", "position", "position_group", "minutes_full_tip", "minutes_full_otip", "physical_check_passed"]

    data.drop(drop, inplace = True, axis = 1)
    sample = data.columns[["sample" in i for i in data.columns]]
    data.drop(sample, inplace = True, axis = 1)

    data.rename(columns = rename_col, inplace = True)

    # AJOUT NUMÉRO DE JOURNÉE AU DATAFRAME
    match_round = pd.read_excel(f"Data_file/Métriques Team sur une Saison Ligue 2 SB + SK/{dico["saison"]}/Skill Corner/match_round.xlsx",
                                index_col = 0)
    match_round.drop(index = dico["match_drop"], inplace = True)
    data = data.merge(match_round, right_on = "id", left_on = "match_id").drop("match_id", axis = 1)
    data = data.groupby(["Journée", "team_name"], as_index = True)
    nb_joueur_match = data.apply(len)
    data = data.sum()
    data = data.divide(nb_joueur_match, axis = 0)

    nb_minute_match = data.pop("minutes_per_Match")
    data = data.multiply(900/nb_minute_match, axis = 0).reindex(dico["ranking"], axis = 0, level = 1)

    info_result = pd.read_excel(f"Info matchs/Skill Corner/result_{dico["saison"]}.xlsx", index_col = [0, 1])

    data = pd.merge(info_result, data, on = ["Journée", "team_name"])

    data.to_excel(f"Métriques discriminantes/Tableau métriques/{dico["saison"]}/Skill Corner/physical.xlsx")