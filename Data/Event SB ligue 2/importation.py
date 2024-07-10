from statsbombpy import sb

import os

import pandas as pd

import warnings
warnings.filterwarnings("ignore")

email = "nathan.talbot@etu.uca.fr"
password = os.environ["mdp_statsbomb"]
creds = {"user" : email, "passwd" : password}

liste_annee = ["2023_2024", "2022_2023", "2021_2022", "2020_2021"]

for annee in liste_annee : 
    liste_match = pd.read_excel(f"Data/Event SB ligue 2/{annee}/liste_match.xlsx", index_col=0).dropna().squeeze()
    for match_id1 in liste_match.iloc[62:] :
        event = sb.events(match_id = match_id1, creds = creds)
        event = event[["type", "possession", "shot_outcome", "possession_team", "location", "shot_type", "period"]]
        event.to_excel(f"Data/Event SB ligue 2/{annee}/{match_id1}.xlsx")