from skillcorner.client import SkillcornerClient
import pandas as pd
import sqlite3
import os

connect = sqlite3.connect("raw-database.db")

secret_password = os.getenv("mdp_skillcorner")
client = SkillcornerClient(username = "Nathan.talbot@etu.uca.fr", password = secret_password)

df_compet = pd.DataFrame(client.get_competitions(params = {"component_permission_for" : "physical"}))

df_compet.to_sql("compet_SK", con = connect, if_exists = "replace", index = False)

connect.close()