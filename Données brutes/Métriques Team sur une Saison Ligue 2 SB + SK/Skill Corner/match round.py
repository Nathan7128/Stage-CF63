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
    liste_matches = pd.DataFrame(client.get_matches(params = {"competition_edition" : dico_saison[saison]}))
    match_round = pd.Series(index = liste_matches["id"], name = "Journée")
    for match in match_round.index :
        match_round.loc[match] = client.get_match(match_id = match)["competition_round"]["round_number"]
    df_final = pd.concat([df_final, match_round])

df_final.to_sql(name = "match_round_SK", con = connect, if_exists = "replace")

connect.close()