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
    index = []
    [index.extend(centre.index + i) for i in range (6)]

    centre = pd.DataFrame({"attacking_team" : [i for i in centre.team for _ in range (6)],
                        "centre_id" : ["centre " + str(i) for i in range (1, len(centre) + 1) for _ in range (6)]},
                        index = [j + i for j in centre.index for i in range(6)])

    df = pd.concat([event.loc[centre.index], centre], axis = 1).set_index(["centre_id", "attacking_team"])

    df["But"] = 0

    df_shot = df[(df.type == "Shot") & (df.index.get_level_values(1) == df.team)]

    df_shot_player = df_shot.groupby(level = [0, 1]).player.transform(lambda x: ', '.join(x))
    df_shot_player = df_shot_player.reset_index().drop_duplicates().set_index(["centre_id", "attacking_team"]).player

    df_goal = df[((df.shot_outcome == "Goal") | (df.type == "Own Goal For"))
                        & (df.index.get_level_values(1) == df.team)]

    df_shot_player.name = "Tireur"
    df = pd.merge(df, df_shot_player, left_index = True, right_index = True, how = "left")

    df.loc[df_goal.index, "But"] = 1
    df.loc[df_goal.index, "Buteur"] = df_goal.player

    df = df.reset_index(level = 1)


    mask_centre = df.pass_cross == 1

    df_loc_centre = pd.DataFrame(df.loc[mask_centre, "location"].tolist(),
        index = df.loc[mask_centre].index)
    df.loc[mask_centre, "x"] = df_loc_centre[0]
    df.loc[mask_centre, "y"] = df_loc_centre[1]

    df_loc_centre_end = pd.DataFrame(df.loc[mask_centre, "pass_end_location"].tolist(),
        index = df.loc[mask_centre].index)
    df.loc[mask_centre, "x_end"] = df_loc_centre_end[0]
    df.loc[mask_centre, "y_end"] = df_loc_centre_end[1]


    mask_shot = (df.attacking_team == df.team) & (df.type == "Shot")

    df_loc_shot = pd.DataFrame(df.loc[mask_shot, "location"].tolist(),
        index = df.loc[mask_shot].index)
    df.loc[mask_shot, "x"] = df_loc_shot[0]
    df.loc[mask_shot, "y"] = df_loc_shot[1]

    df_loc_shot_end = pd.DataFrame(df.loc[mask_shot, "shot_end_location"].tolist(),
        index = df.loc[mask_shot].index)
    df.loc[mask_shot, "x_end"] = df_loc_shot_end[0]
    df.loc[mask_shot, "y_end"] = df_loc_shot_end[1]

    df = df[["match_id", "attacking_team", "But", "Tireur", "Buteur", "player", "minute", "pass_body_part", "x", "y", "x_end", "y_end"]]
    df.rename(axis = 1, mapper = {"attacking_team" : "Équipe attaquante", "player" : "Centreur", "pass_body_part" : "Partie du corps"}, inplace = True)

    df.to_excel(f"Heatmap SB/centre/Tableaux/{saison}.xlsx")