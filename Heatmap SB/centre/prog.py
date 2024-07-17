import pandas as pd

import warnings
warnings.filterwarnings("ignore")

dico_annee = {"2023_2024" : ["Auxerre", "Angers", "Saint-Étienne", "Rodez", "Paris FC"],
              "2022_2023" : ["Le Havre", "Metz", "Bordeaux", "Bastia", "Caen"],
              "2021_2022" : ["Toulouse", "AC Ajaccio", "Auxerre", "Paris FC", "Sochaux"],
              "2020_2021" : ["Troyes", "Clermont Foot", "Toulouse", "Grenoble Foot", "Paris FC"]}


for annee in dico_annee.keys() :

    event = pd.read_json(f"Data_file/Heatmap SB/{annee}.json")

    event = event[~event.location.isna()]

    event.sort_values(by = ["match_id", "index"], inplace = True)

    event.index = range(len(event))

    centre = event[(event.pass_cross == 1) & (event.pass_type != "Corner")]

    n_event = 5
    for i in centre.index :
        team_i = centre.team
        event_i = event.loc[i + 1 : i + n_event]
        if sum(((event_i.shot_outcome == "Goal") | (event_i.type == "Own Goal Against")) & (event_i.team == centre.loc[i, "team"])) > 0 :
            centre.loc[i, "goal"] = 1
    
    df = pd.concat([centre.match_id, centre.team, centre.goal, pd.DataFrame(centre.location.tolist(), index = centre.index), pd.DataFrame(centre.pass_end_location.tolist(), index = centre.index)], axis = 1, ignore_index = True)
    df.columns = ["match_id", "Équipe", "goal", "x", "y", "x_end", "y_end"]

    df["Top 5"] = df["Équipe"].isin(dico_annee[annee])

    df.to_excel(f"Heatmap SB/centre/Tableaux/{annee}.xlsx")