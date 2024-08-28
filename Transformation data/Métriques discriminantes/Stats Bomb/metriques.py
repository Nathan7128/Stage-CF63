import pandas as pd

import sqlite3

connect = sqlite3.connect("raw-database.db")
cursor = connect.cursor()

req = cursor.execute("SELECT * FROM raw_data_met_SB")
res = req.fetchall()
desc = req.description

df = pd.DataFrame(res, columns = [i[0] for i in desc])

drop = ["account_id", "team_id", "competition_id", "season_id", "team_female", "team_season_matches", "team_season_minutes"]

df = df.drop(drop, axis = 1).rename({"season_name" : "Saison", "competition_name" : "Compet"}, axis = 1)

connect.close()


connect = sqlite3.connect("database.db")

df.to_sql(name = "Métriques_SB", con = connect, if_exists = "replace", index = False)

connect.close()