from statsbombpy import sb

import os

import pandas as pd

import warnings
warnings.filterwarnings("ignore")

email = "nathan.talbot@etu.uca.fr"
password = os.environ["mdp_statsbomb"]
creds = {"user" : email, "passwd" : password}

dico_annee = {
    "2023_2024" : 281,
    "2022_2023" : 235,
    "2021_2022" : 108,
    "2020_2021" : 90
}
ligue2_id = 8

for annee in dico_annee.keys() :
    match = sb.matches(ligue2_id, dico_annee[annee], creds = creds)
    liste_match = match[match.match_status == 'available'].match_id
    liste_match.to_excel(f"Data/Event SB ligue 2/{annee}/liste_match.xlsx")