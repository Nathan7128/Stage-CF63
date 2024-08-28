from skillcorner.client import SkillcornerClient
import pandas as pd
import sqlite3
import os

secret_password = os.getenv("mdp_skillcorner")
client = SkillcornerClient(username = "Nathan.talbot@etu.uca.fr", password = secret_password)

connect = sqlite3.connect("raw-database.db")

dico_saison = {
    "2023_2024" : 549,
    "2022_2023" : 393,
    "2021_2022" : 243
}

df_final = pd.DataFrame()

for saison in dico_saison.keys() :
    data_import1 = client.get_in_possession_on_ball_pressures(params = {'competition_edition': dico_saison[saison],
            "pressure_intensity" : ["low", "medium", "high"], "average_per" : "match"})
    df1 = pd.DataFrame(data_import1)

    data_import2 = client.get_in_possession_on_ball_pressures(params = {'competition_edition': dico_saison[saison],
          "pressure_intensity" : ["low", "medium", "high"], "average_per" : "100_pressures"})
    df2 = pd.DataFrame(data_import2)

    data_import3 = client.get_in_possession_on_ball_pressures(params = {'competition_edition': dico_saison[saison],
          "pressure_intensity" : ["low", "medium", "high"], "average_per" : "30_min_tip"})
    df3 = pd.DataFrame(data_import3)

    df = pd.merge(df1, df2, on = ["player_id", "match_id"], suffixes = ["_per_match", "_per_100_pressures"])
    df = pd.merge(df, df3, on = ["player_id", "match_id"], suffixes = [None, "_per_30_min_tip"])

    df_final = pd.concat([df_final, df])

df_final = df_final.T.drop_duplicates().T

df_final.to_sql(name = "raw_data_pressure", con = connect, if_exists = "replace", index = False)

connect.close()