from statsbombpy import sb

import os

import pandas as pd

import warnings
warnings.filterwarnings("ignore")

email = "nathan.talbot@etu.uca.fr"
password = os.environ["mdp_statsbomb"]
creds = {"user" : email, "passwd" : password}

import sqlite3

connect = sqlite3.connect("raw-database.db")

dico_saison = {
    "2023_2024" : 281,
    "2022_2023" : 235,
    "2021_2022" : 108,
    "2020_2021" : 90
}
ligue2_id = 8


df = pd.concat([sb.matches(ligue2_id, dico_saison[saison], creds = creds) for saison in dico_saison.keys()])
df.loc[df["away_score"] > df["home_score"], "Résultat"] = df.loc[df["away_score"] > df["home_score"], "away_team"]
df.loc[df["home_score"] > df["away_score"], "Résultat"] = df.loc[df["home_score"] > df["away_score"], "home_team"]

colonnes = ['match_id', 'match_date', 'competition', 'season', 'home_team', 'away_team', 'Résultat', "match_week"]
rename = {'match_date' : "Date", 'competition' : "Compet", 'season' : "Saison", 'home_team' : "Domicile", 'away_team' : "Extérieur",
          "match_week" : "Journée"}
df = df[colonnes].rename(rename, axis = 1)
df.Compet = df.Compet.apply(lambda x : x.replace("France - ", ""))

df.to_sql(name = "Info_matchs_SB", con = connect, if_exists = "replace", index = False)

connect.close()