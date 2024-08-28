import pandas as pd
import sqlite3

connect = sqlite3.connect("raw-database.db")
cursor = connect.cursor()

colonnes = ["x_loc", "y_loc", "match_id", "type", "team", "minute", "shot_outcome", "pass_type", "pass_cross", "index_event", "x_shot", "y_shot", "z_shot", "x_pass", "y_pass", "pass_body_part", "player"]
colonnes = ", ".join(colonnes)
req = cursor.execute(f"SELECT {colonnes} FROM raw_data_heatmap")
res = req.fetchall()
desc = req.description
data = pd.DataFrame(res)
data.columns = [i[0] for i in desc]

colonnes = ["Date", "Journée", "Domicile", "Extérieur", "Saison", "Compet", "match_id"]
colonnes = ", ".join(colonnes)
req = cursor.execute(f"SELECT {colonnes} FROM Info_matchs_SB")
res = req.fetchall()
desc = req.description
df_infos = pd.DataFrame(res)
df_infos.columns = [i[0] for i in desc]

event = data.sort_values(by = ["match_id", "index_event"])
event["index_event"] = range(len(event))

centre = event[(event.pass_cross == 1) & (event.pass_type != "Corner")]
centre = pd.DataFrame({"attacking_team" : [i for i in centre.team for _ in range (6)],
                    "centre_id" : [i for i in range (1, len(centre) + 1) for _ in range (6)],
                    "match_id" : [i for i in centre.match_id for _ in range (6)],
                    "index_event" : [j + i for j in centre["index_event"] for i in range (6)]})

liste_centre_drop = centre.centre_id[centre["index_event"].duplicated()].unique() - 1
centre = centre.drop_duplicates("index_event", keep = "last")

df = pd.merge(centre, event, on = ["index_event", "match_id"])

df["But"] = "Non"
df["Tireur"] = ""

mask_shot = (df.type == "Shot") & (df.attacking_team == df.team)
df.loc[mask_shot, "Tireur"] = df.loc[mask_shot, "player"]

mask_goal = ((df.shot_outcome == "Goal") | (df.type == "Own Goal For")) & (df.attacking_team == df.team)
df.loc[(df.centre_id.isin(df.loc[mask_goal, "centre_id"])) & (df.pass_cross == 1), "But"] = "Oui"
df.loc[mask_goal, "But"] = "Oui"

df_centre_drop = df[df.centre_id.isin(liste_centre_drop)]
df.drop(df_centre_drop[df_centre_drop.But == "Non"].index, inplace = True)

df_centreur = df.groupby("centre_id").head(1)[['player', 'centre_id']]
df = pd.merge(df, df_centreur, on = "centre_id").set_index(df.index)

drop = ["shot_outcome", "team", "match_id", "player_x", "index_event", "type", "pass_type"]
rename = {"attacking_team" : "Équipe", "minute" : "Minute", "pass_cross" : "Centre", "player_y" : "Centreur",
          "pass_body_part" : "Partie du corps"}
df = pd.merge(df, df_infos, on = "match_id").drop(drop, axis = 1).rename(rename, axis = 1)

connect.close()


connect = sqlite3.connect("database.db")

df.to_sql(name = "Centre", con = connect, if_exists = "replace")

connect.close()