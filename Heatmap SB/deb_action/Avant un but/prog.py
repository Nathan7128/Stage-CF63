from statsbombpy import sb

import pandas as pd

import numpy as np

import os

import warnings
warnings.filterwarnings("ignore")

import ast

email = "nathan.talbot@etu.uca.fr"
password = os.environ["mdp_statsbomb"]
creds = {"user" : email, "passwd" : password}


dico_annee = {"2023_2024" : ["Auxerre", "Angers", "Saint-Étienne", "Rodez", "Paris FC"],
              "2022_2023" : ["Le Havre", "Metz", "Bordeaux", "Bastia", "Caen"],
              "2021_2022" : ["Toulouse", "AC Ajaccio", "Auxerre", "Paris FC", "Sochaux"],
              "2020_2021" : ["Troyes", "Clermont Foot", "Toulouse", "Grenoble Foot", "Paris FC"]}


for annee in dico_annee.keys() :

    df_annee = pd.DataFrame()

    liste_match = pd.read_excel(f"Data/Event SB ligue 2/{annee}/liste_match.xlsx", index_col = 0).squeeze()

    serie_match = []

    for match in liste_match :

        df = pd.DataFrame()

        event = pd.read_excel(f"Data/Event SB ligue 2/{annee}/{match}.xlsx", index_col = 0)
        event.location = event.location.fillna("[60, 40]").apply(ast.literal_eval)

        goal = event[(event.shot_outcome == "Goal") & (event.shot_type != "Penalty")]

        if len(goal) > 0 :

            pos_change_side = goal[pd.DataFrame(goal.location.tolist(), index = goal.index)[0] > 60].possession

            deb_action = pd.DataFrame(columns = event.columns)

            for ind in goal.index :
                deb_action.loc[ind] = event[(event.possession == goal.loc[ind, "possession"]) & (event.period == goal.loc[ind, "period"])].iloc[0]
            
            loc_deb_action = pd.DataFrame(deb_action.location.tolist(), index = deb_action.index)
            df = pd.concat([df, pd.concat([loc_deb_action, deb_action.possession, deb_action.possession_team], axis = 1)], axis = 0)

            df.loc[df.possession.isin(pos_change_side), [0, 1]] = [120, 80] - df[df.possession.isin(pos_change_side)][[0, 1]]
        
            df_annee = pd.concat([df_annee, df], axis = 0, ignore_index = True)

            serie_match += [f"{match}"]*len(df)

    df_annee["match_id"] = serie_match

    df_annee.drop([2, "possession"], axis = 1, inplace = True)

    df_annee.columns = ["x", "y", "Équipe", "match_id"]

    df_annee["Top 5"] = df_annee["Équipe"].isin(dico_annee[annee])

    df_annee.to_excel(f"Heatmap SB/deb_action/Avant un but/Tableaux/{annee}/loc_deb_action.xlsx")