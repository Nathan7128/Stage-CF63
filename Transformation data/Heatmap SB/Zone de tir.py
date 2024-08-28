import pandas as pd
import sqlite3

connect = sqlite3.connect("raw-database.db")
cursor = connect.cursor()

colonnes = ["x_loc", "y_loc", "match_id", "type", "shot_type", "team", "minute", "player"]
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

df = df[(df.type == "Shot") & (df.shot_type != "Penalty")].drop(["type", "shot_type"], axis = 1)

rename = {"player" : "Joueur", "minute" : "Minute", "team" : "Équipe"}

df = pd.merge(df, df_infos, on = "match_id").rename(rename, axis = 1)

connect.close()


connect = sqlite3.connect("database.db")

df.to_sql(name = "Zone_tir", con = connect, if_exists = "replace")

connect.close()