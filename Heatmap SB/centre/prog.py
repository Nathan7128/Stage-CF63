import pandas as pd

import warnings
warnings.filterwarnings("ignore")

liste_saison = ["2023_2024", "2022_2023", "2021_2022", "2020_2021"]


for saison in liste_saison :

    event = pd.read_json(f"Data_file/Heatmap SB/{saison}.json")

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
    df.columns = ["match_id", "Équipe", "But", "x", "y", "x_end", "y_end"]

    df.to_excel(f"Heatmap SB/centre/Tableaux/{saison}.xlsx")