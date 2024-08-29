import pandas as pd
import sqlite3

connect = sqlite3.connect("raw-database.db")
cursor = connect.cursor()

colonnes = ["match_id", "period", "possession", "type", "shot_type", "team", "minute", "shot_outcome", "pass_type"]
colonnes = ", ".join(colonnes)
req = cursor.execute(f"SELECT {colonnes} FROM raw_data_heatmap")
res = req.fetchall()
desc = req.description
df = pd.DataFrame(res)
df.columns = [i[0] for i in desc]

req = cursor.execute("SELECT Saison, Compet, match_id FROM Info_matchs_SB")
res = req.fetchall()
desc = req.description
df_infos = pd.DataFrame(res)
df_infos.columns = [i[0] for i in desc]

df.set_index(["match_id", "period", "possession"], inplace = True)

goal = df[(df.shot_type == "Open Play") & ((df.shot_outcome == "Goal") | (df.type == "Own Goal For"))]

df = df.loc[goal.index]

deb_action = df.groupby(level = [0, 1, 2], sort = False).head(1)
deb_action["type_action"] = deb_action.pass_type.fillna(deb_action.shot_type).fillna(deb_action.type)

count_passe = df[df.type == "Pass"].groupby(["match_id", "period", "possession"], sort = False, as_index = True).size()

df = pd.concat([goal, count_passe, deb_action.type_action], axis = 1)
df.rename({0 : "Passe"}, axis = 1, inplace = True)
df.replace(to_replace = ['Interception', 'Ball Recovery', 'Duel', 'Recovery', 'Pass', 'Goal Keeper', '50/50'], value = "Open play",
           inplace = True)

df = pd.merge(df, df_infos, on = "match_id")[["team", "Passe", "type_action", "Saison", "Compet"]]

connect.close()


connect = sqlite3.connect("database.db")

df.to_sql(name = "Passes_avant_un_but", con = connect, if_exists = "replace")

connect.close()