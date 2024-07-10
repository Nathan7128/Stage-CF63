import pandas as pd


dico_annee = {"2023_2024" : ["Auxerre", "Angers", "Saint-Étienne", "Rodez", "Paris FC"],
              "2022_2023" : ["Le Havre", "Metz", "Bordeaux", "Bastia", "Caen"],
              "2021_2022" : ["Toulouse", "AC Ajaccio", "Auxerre", "Paris FC", "Sochaux"],
              "2020_2021" : ["Troyes", "Clermont Foot", "Toulouse", "Grenoble Foot", "Paris FC"]}


for annee in dico_annee.keys() :

    event = pd.read_json(f"Data/Heatmap SB/{annee}.json")

    event = event[~event.location.isna()]

    event.sort_values(by = ["match_id", "index"], inplace = True)

    goal = event[(event.shot_type != "Penalty") & ((event.shot_outcome == "Goal") | (event.type == "Own Goal Against"))]

    deb_action = event.groupby(["match_id", "period", "possession"], sort = False).head(1).set_index(["match_id", "period", "possession"]).loc[list(zip(goal.match_id, goal.period, goal.possession))]

    loc_deb_action = pd.DataFrame(deb_action.location.tolist())

    df = pd.concat([loc_deb_action, pd.Series(goal.team.tolist()), pd.Series(goal.match_id.tolist())], axis = 1)

    df.drop(2, axis = 1, inplace = True)

    df.columns = ["x", "y", "Équipe", "match_id"]

    df["Top 5"] = df["Équipe"].isin(dico_annee[annee])

    df.to_excel(f"Heatmap SB/deb_action/Avant un but/Tableaux/{annee}.xlsx")