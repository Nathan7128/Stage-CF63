import os
import pandas as pd
from statsbombpy import sb
import sqlite3

connect = sqlite3.connect("raw-database.db")

email = "nathan.talbot@etu.uca.fr"
password = os.environ["mdp_statsbomb"]
creds = {"user" : email, "passwd" : password}

df_compet = sb.competitions(creds = creds)

df_compet.to_sql("compet_SB", con = connect, if_exists = "replace", index = False)

connect.close()