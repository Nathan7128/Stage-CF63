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
    data_import1 = client.get_in_possession_passes(params = {'competition_edition': dico_saison[saison],
          "run_type" : ["run_in_behind", "run_ahead_of_the_ball", "support_run", "pulling_wide_run", "coming_short_run", "underlap_run",
                              "overlap_run", "dropping_off_run", "pulling_half_space_run", "cross_receiver_run"],
                              "average_per" : "match"})
    df1 = pd.DataFrame(data_import1)

    data_import2 = client.get_in_possession_passes(params = {'competition_edition': dico_saison[saison],
          "run_type" : ["run_in_behind", "run_ahead_of_the_ball", "support_run", "pulling_wide_run", "coming_short_run", "underlap_run",
                              "overlap_run", "dropping_off_run", "pulling_half_space_run", "cross_receiver_run"],
                              "average_per" : "100_pass_opportunities"})
    df2 = pd.DataFrame(data_import2)

    data_import3 = client.get_in_possession_passes(params = {'competition_edition': dico_saison[saison],
          "run_type" : ["run_in_behind", "run_ahead_of_the_ball", "support_run", "pulling_wide_run", "coming_short_run", "underlap_run",
                              "overlap_run", "dropping_off_run", "pulling_half_space_run", "cross_receiver_run"],
                              "average_per" : "30_min_tip"})
    df3 = pd.DataFrame(data_import3)

    df = pd.merge(df1, df2, on = ["player_id", "match_id"], suffixes = ["_per_match", "_per_100_pass_opportunities"])
    df = pd.merge(df, df3, on = ["player_id", "match_id"], suffixes = [None, "_per_30_min_tip"])

    df_final = pd.concat([df_final, df])

df_final = df_final.T.drop_duplicates().T

df_final.to_sql(name = "raw_data_passes", con = connect, if_exists = "replace", index = False)

connect.close()