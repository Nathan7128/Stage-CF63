from statsbombpy import sb

import os

import pandas as pd

import warnings
warnings.filterwarnings("ignore")

email = "nathan.talbot@etu.uca.fr"
password = os.environ["mdp_statsbomb"]
creds = {"user" : email, "passwd" : password}

import sqlite3

connect = sqlite3.connect("database.db")

dico_saison = {
    "2023_2024" : 281,
    "2022_2023" : 235,
    "2021_2022" : 108,
    "2020_2021" : 90
}
ligue2_id = 8

df_final = pd.DataFrame()

for saison in dico_saison.keys() :
    df = sb.matches(ligue2_id, dico_saison[saison], creds = creds)
    df.loc[df["away_score"] > df["home_score"], "Résultat"] = df.loc[df["away_score"] > df["home_score"], "away_team"]
    df.loc[df["home_score"] > df["away_score"], "Résultat"] = df.loc[df["home_score"] > df["away_score"], "home_team"]
    
    df["Saison"] = saison

    df_final = pd.concat([df_final, df], axis = 0)

df_final["Compet"] = "Ligue 2"

df_final.to_sql(name = "Info_matchs_SB", con = connect, if_exists = "replace")

connect.close()

    