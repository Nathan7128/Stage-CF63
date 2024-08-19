import pandas as pd

import sqlite3

connect = sqlite3.connect("database.db")

df_final = pd.DataFrame()

liste_saison = ["2023_2024", "2022_2023", "2021_2022", "2020_2021"]

for saison in liste_saison :

    event = pd.read_json(f"Data_file/Heatmap SB/{saison}.json")

    shot = event[(event.type == "Shot") & (event.shot_type != "Penalty")]

    df = pd.concat([pd.DataFrame(shot.location.tolist(), index = shot.index), shot[["team", "match_id", "player", "minute"]]], axis = 1)

    df.drop(2, axis = 1, inplace = True)

    df.columns = ["x", "y", "Équipe", "match_id", "joueur", "minute"]

    df["Saison"] = saison

    df_final = pd.concat([df_final, df], axis = 0)

df_final["Compet"] = "Ligue 2"

df_final.to_sql(name = "Zone_tir", con = connect, if_exists = "replace")

connect.close()