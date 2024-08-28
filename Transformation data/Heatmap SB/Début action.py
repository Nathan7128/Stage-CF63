import pandas as pd
import sqlite3

connect = sqlite3.connect("raw-database.db")
cursor = connect.cursor()

colonnes = ["x_loc", "y_loc", "match_id", "period", "possession", "type", "shot_type", "team", "minute", "shot_outcome", "pass_type"]
colonnes = ", ".join(colonnes)
req = cursor.execute(f"SELECT {colonnes} FROM raw_data_heatmap")
res = req.fetchall()
desc = req.description
df = pd.DataFrame(res)
df.columns = [i[0] for i in desc]

colonnes = ["Date", "Journée", "Domicile", "Extérieur", "Saison", "Compet", "match_id"]
colonnes = ", ".join(colonnes)
req = cursor.execute(f"SELECT {colonnes} FROM Info_matchs_SB")
res = req.fetchall()
desc = req.description
df_infos = pd.DataFrame(res)
df_infos.columns = [i[0] for i in desc]


df.set_index(["match_id", "period", "possession"], inplace = True)

shot = df[(df.type == "Shot")]

deb_action = df.groupby(level = [0, 1, 2]).head(1).loc[shot.index]
deb_action["type_action"] = deb_action.pass_type.fillna(deb_action.shot_type).fillna(deb_action.type)

df = pd.concat([shot[["team", "minute"]], deb_action[["x_loc", "y_loc", "type_action"]], shot.shot_outcome == "Goal"], axis = 1)

df.replace(to_replace = ['Interception', 'Ball Recovery', 'Duel', 'Recovery', 'Pass', 'Goal Keeper', '50/50'], value = "Open play", inplace = True)

rename = {"team" : "Équipe", "minute" : "Minute", "shot_outcome" : "But"}
df = pd.merge(df, df_infos, on = "match_id").rename(rename, axis = 1)
df.drop_duplicates(inplace = True)

connect.close()


connect = sqlite3.connect("database.db")

df.to_sql(name = "Debut_action", con = connect, if_exists = "replace")

connect.close()