import pandas as pd


dico_annee = {"2023_2024" : ["Auxerre", "Angers", "Saint-Étienne", "Rodez", "Paris FC"],
              "2022_2023" : ["Le Havre", "Metz", "Bordeaux", "Bastia", "Caen"],
              "2021_2022" : ["Toulouse", "AC Ajaccio", "Auxerre", "Paris FC", "Sochaux"],
              "2020_2021" : ["Troyes", "Clermont Foot", "Toulouse", "Grenoble Foot", "Paris FC"]}


for annee in dico_annee.keys() :

    event = pd.read_json(f"Data_file/Heatmap SB/{annee}.json")
    
    event = event[~event.location.isna()]

    event.sort_values(by = ["match_id", "index"], inplace = True)

    event.set_index(["match_id", "period", "possession"], inplace = True)

    shot = event[(event.type == "Shot")]

    deb_action = event.groupby(level = [0, 1, 2]).head(1).loc[shot.index]

    deb_action["type_action"] = deb_action.pass_type.fillna(deb_action.shot_type).fillna(deb_action.type)

    loc_deb_action = pd.DataFrame(deb_action.location.tolist(), index = deb_action.index)

    df = pd.concat([loc_deb_action, shot.team, deb_action.type_action, shot.shot_outcome == "Goal"], axis = 1)

    df = df.reset_index().drop([2, "period", "possession"], axis = 1)

    df.replace(to_replace = ['Interception', 'Ball Recovery', 'Duel', 'Recovery', 'Pass', 'Goal Keeper', '50/50'], value = "Open play", inplace = True)

    df.columns = ["match_id", "x", "y", "Équipe", "type_action", "But"]

    df["Top 5"] = df["Équipe"].isin(dico_annee[annee])

    df.to_excel(f"Heatmap SB/deb_action/Avant un tir/Tableaux/{annee}.xlsx")