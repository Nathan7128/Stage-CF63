from statsbombpy import sb
import os
import pandas as pd
import sqlite3
import warnings

warnings.filterwarnings("ignore")

connect = sqlite3.connect("raw-database.db")

email = "nathan.talbot@etu.uca.fr"
password = os.environ["mdp_statsbomb"]
creds = {"user" : email, "passwd" : password}

dico_saison = {
    "2023/2024" : 281,
    "2022/2023" : 235,
    "2021/2022" : 108,
    "2020/2021" : 90
}
ligue2_id = 8

df = pd.DataFrame()
for saison in dico_saison.keys() :
    data_import = sb.team_season_stats(ligue2_id, dico_saison[saison], creds = creds)

    df = pd.concat([df, data_import], axis = 0)

df.to_sql(name = "raw_data_met_SB", con = connect, if_exists = "replace", index = False)

connect.close()