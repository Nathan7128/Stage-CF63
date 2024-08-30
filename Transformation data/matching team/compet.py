import pandas as pd
import sqlite3
from Levenshtein import distance

connect = sqlite3.connect("raw-database.db")
cursor = connect.cursor()

req = cursor.execute("SELECT id, area, name from compet_SK WHERE gender = 'male' AND age_group = 'adult'")
res = req.fetchall()
desc = req.description
df_compet_SK = pd.DataFrame(res)
df_compet_SK.columns = [i[0] for i in desc]

df_compet_SK = df_compet_SK[[("Play" not in i or "play" not in i) and ("Off" not in i or "off" not in i) for i in df_compet_SK.name]]
df_compet_SK.set_index("id", inplace = True)
df_compet_SK = pd.DataFrame(df_compet_SK.area + " - " + df_compet_SK.name, columns = ["compet_SK"]).reset_index()

req = cursor.execute("SELECT DISTINCT competition_id, country_name, competition_name from compet_SB WHERE competition_youth = False AND competition_youth = False")
res = req.fetchall()
desc = req.description
df_compet_SB = pd.DataFrame(res)
df_compet_SB.columns = [i[0] for i in desc]

connect.close()

df_compet_SB = df_compet_SB[["Play-offs" not in i for i in df_compet_SB.competition_name]]
df_compet_SB.set_index("competition_id", inplace = True)
df_compet_SB = pd.DataFrame(df_compet_SB.country_name + " - " + df_compet_SB.competition_name, columns = ["compet_SB"]).reset_index()

liste_compet_SK = df_compet_SK.compet_SK
df_distance = pd.DataFrame(index = liste_compet_SK)
for compet_SB in df_compet_SB.compet_SB :
    df_distance[compet_SB] = [distance(compet_SB, i, weights = (1, 1, 5)) for i in liste_compet_SK]
dico = {}
min_distance = df_distance.min().sort_values()
min_distance = min_distance[min_distance < 20].index
df_distance = df_distance[min_distance]
i = 0
while min(df_distance.shape) != 0 :
    compet_SB = min_distance[i]
    compet_SK = df_distance[compet_SB].idxmin()
    dico[compet_SB] = compet_SK
    df_distance.drop(compet_SK, axis = 0, inplace = True)
    df_distance.drop(compet_SB, axis = 1, inplace = True)
    i += 1

df_final = pd.DataFrame(dico.items(), columns = ["compet_SB", "compet_SK"])
df_final = pd.merge(df_final, df_compet_SB, on = "compet_SB")
df_final = pd.merge(df_final, df_compet_SK, on = "compet_SK")
df_final = pd.concat([df_final, df_compet_SK[~df_compet_SK.compet_SK.isin(df_final.compet_SK)]])
df_final = pd.concat([df_final, df_compet_SB[~df_compet_SB.compet_SB.isin(df_final.compet_SB)]])

connect = sqlite3.connect("database.db")

df_final.to_sql("compet", con = connect, if_exists = "replace", index = False)
df_final.to_sql("compet_modif", con = connect, if_exists = "replace", index = False)

connect.close()