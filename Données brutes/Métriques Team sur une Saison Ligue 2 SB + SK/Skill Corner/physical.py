from skillcorner.client import SkillcornerClient
import pandas as pd
import sqlite3
import os

secret_password = os.getenv("mdp_skillcorner")
client = SkillcornerClient(username = "Nathan.talbot@etu.uca.fr", password = secret_password)

connect = sqlite3.connect("raw-database.db")

dico_saison = {
    "2023/2024" : 549,
    "2022/2023" : 393,
    "2021/2022" : 243
}

df_final = pd.DataFrame()

for saison in dico_saison.keys() :
    data_import1 = client.get_physical(params = {"data_version" : 3, 'competition_edition': dico_saison[saison],
                                                 "physical_check_passed" : "true"})
    df1 = pd.DataFrame(data_import1)

    data_import2 = client.get_physical(params = {"data_version" : 3, 'competition_edition': dico_saison[saison],
                        "average_per" : "p30tip", "possession" : "tip", "physical_check_passed" : "true"})
    df2 = pd.DataFrame(data_import2)

    data_import3 = client.get_physical(params = {"data_version" : 3, 'competition_edition': dico_saison[saison], 
                        "average_per" : "p30otip", "possession" : "otip", "physical_check_passed" : "true"})
    df3 = pd.DataFrame(data_import3)

    df = pd.merge(df1, df2, on = ["player_id", "match_id"])
    df = pd.merge(df, df3, on = ["player_id", "match_id"])

    df_final = pd.concat([df_final, df])

df_final = df_final.T.drop_duplicates().T

df_final.to_sql(name = "raw_data_physical", con = connect, if_exists = "replace", index = False)

connect.close()