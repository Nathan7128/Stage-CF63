import pandas as pd

import sqlite3

connect = sqlite3.connect("database.db")

df_final = pd.DataFrame()

liste_saison = ["2023_2024", "2022_2023", "2021_2022", "2020_2021"]


for saison in liste_saison :

    event = pd.read_json(f"Data_file/Heatmap SB/{saison}.json")

    event = event[~event.location.isna()]

    event = event.sort_values(by = ["match_id", "index"])
    event["index"] = range(len(event))

    centre = event[(event.pass_cross == 1) & (event.pass_type != "Corner")]

    centre = pd.DataFrame({"attacking_team" : [i for i in centre.team for _ in range (6)],
                        "centre_id" : [i for i in range (1, len(centre) + 1) for _ in range (6)],
                        "match_id" : [i for i in centre.match_id for _ in range (6)],
                        "index" : [j + i for j in centre["index"] for i in range (6)]})

    liste_centre_drop = centre.centre_id[centre["index"].duplicated()].unique() - 1
    centre = centre.drop_duplicates("index", keep = "last")

    df = pd.merge(centre, event, on = ["index", "match_id"])

    df["But"] = "Non"
    df["Tireur"] = ""

    mask_shot = (df.type == "Shot") & (df.attacking_team == df.team)

    df_shot = df[mask_shot]
    df_loc_shot = pd.DataFrame(df_shot.location.tolist(), index = df_shot.index)[[0, 1]]
    df_loc_shot_end = pd.DataFrame(df_shot.shot_end_location.tolist(), index = df_shot.index)

    df.loc[df_shot.index, "Tireur"] = df_shot.player

    df.loc[mask_shot, "x"] = df_loc_shot[0]
    df.loc[mask_shot, "y"] = df_loc_shot[1]

    df.loc[mask_shot, "x_end"] = df_loc_shot_end[0]
    df.loc[mask_shot, "y_end"] = df_loc_shot_end[1]
    df.loc[mask_shot, "z_end"] = df_loc_shot_end[2]

    df_goal = df[((df.shot_outcome == "Goal") | (df.type == "Own Goal For")) & (df.attacking_team == df.team)]

    df.loc[(df.centre_id.isin(df_goal.centre_id)) & (df.pass_cross == 1), "But"] = "Oui"
    df.loc[df_goal.index, "But"] = "Oui"
    df.loc[df_goal.index, "Tireur"] = df_goal.player

    mask_centre = df.pass_cross == 1

    df_loc_centre = pd.DataFrame(df.loc[mask_centre, "location"].tolist(), index = df.loc[mask_centre].index)
    df.loc[mask_centre, "x"] = df_loc_centre[0]
    df.loc[mask_centre, "y"] = df_loc_centre[1]

    df_loc_centre_end = pd.DataFrame(df.loc[mask_centre, "pass_end_location"].tolist(),
        index = df.loc[mask_centre].index)
    df.loc[mask_centre, "x_end"] = df_loc_centre_end[0]
    df.loc[mask_centre, "y_end"] = df_loc_centre_end[1]

    df_centre_drop = df[df.centre_id.isin(liste_centre_drop)]
    df.drop(df_centre_drop[df_centre_drop.But == "Non"].index, inplace = True)

    df_centreur = df.groupby("centre_id").head(1)[['player', 'centre_id']]
    df = pd.merge(df, df_centreur, on = "centre_id").set_index(df.index)

    df = df[["pass_cross", "match_id", "attacking_team", "shot_outcome", "But", "Tireur", "player_y", "minute", "pass_body_part", "x", "y", "x_end", "centre_id",
             "y_end", "z_end"]]
    df.rename(axis = 1, mapper = {"pass_cross" : "Centre", "attacking_team" : "Équipe attaquante", "player_y" : "Centreur",
                                  "pass_body_part" : "Partie du corps"}, inplace = True)
    
    df["Saison"] = saison

    df_final = pd.concat([df_final, df], axis = 0)

df_final["Compet"] = "Ligue 2"

df_final.to_sql(name = "Centre", con = connect, if_exists = "replace")

connect.close()