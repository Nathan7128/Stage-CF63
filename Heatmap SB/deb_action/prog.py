import pandas as pd

liste_saison = ["2023_2024", "2022_2023", "2021_2022", "2020_2021"]


for saison in liste_saison :

    event = pd.read_json(f"Data_file/Heatmap SB/{saison}.json")
    
    event = event[~event.location.isna()]

    event.sort_values(by = ["match_id", "index"], inplace = True)

    event.set_index(["match_id", "period", "possession"], inplace = True)

    shot = event[(event.type == "Shot")]

    deb_action = event.groupby(level = [0, 1, 2]).head(1).loc[shot.index]

    deb_action["type_action"] = deb_action.pass_type.fillna(deb_action.shot_type).fillna(deb_action.type)

    loc_deb_action = pd.DataFrame(deb_action.location.tolist(), index = deb_action.index)

    df = pd.concat([loc_deb_action, shot[["team", "minute"]], deb_action.type_action, shot.shot_outcome == "Goal"], axis = 1)

    df = df.reset_index().drop([2, "period", "possession"], axis = 1)

    df.replace(to_replace = ['Interception', 'Ball Recovery', 'Duel', 'Recovery', 'Pass', 'Goal Keeper', '50/50'], value = "Open play", inplace = True)

    df.columns = ["match_id", "x", "y", "Équipe", "minute", "type_action", "But"]

    df.drop_duplicates(inplace = True)

    df.to_excel(f"Heatmap SB/deb_action/Tableaux/{saison}.xlsx")