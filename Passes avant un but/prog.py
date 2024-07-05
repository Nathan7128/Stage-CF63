import pandas as pd

dico = {
    "annee" : ["2023_2024", "2022_2023", "2021_2022", "2020_2021"],
    "top5" : [["Auxerre", "Angers", "Saint-Étienne", "Rodez", "Paris FC"],
                 ["Le Havre", "Metz", "Bordeaux", "Bastia", "Caen"],
                 ["Toulouse", "AC Ajaccio", "Auxerre", "Paris FC", "Sochaux"],
                 ["Troyes", "Clermont Foot", "Toulouse", "Grenoble Foot", "Paris FC"]]
}

for i in range (4) :
    df = pd.DataFrame(0.0, index = ["nb_but", "nb_passe"], columns = ["Top 5", "Bottom 15"])
    annee = dico["annee"][i]
    top5 = dico["top5"][i]
    liste_match = pd.read_excel(f"Passes avant un but/data/event_match_ligue2/2023_2024/liste_match.xlsx", index_col=0).squeeze()
    for match_id in liste_match :
        event = pd.read_excel(f"Passes avant un but/data/event_match_ligue2/{annee}/{match_id}")
        goal = event[event.shot_outcome == "Goal"]
        goal_top5 = goal[goal.possession_team.isin(top5)]
        goal_bottom15 = goal[~goal.possession_team.isin(top5)]
        df.loc["nb_but", "Top 5"] += len(goal_top5)
        df.loc["nb_but", "Bottom 15"] += len(goal_bottom15)
        for poss in goal_top5.possession :
            passe_top5 = len(event[(event.possession == poss) & (event.type == "Pass")])
            df.loc["nb_passe", "Top 5"] += len(passe_top5)
        for poss in goal_bottom15.possession :
            passe_bottom15 = len(event[(event.possession == poss) & (event.type == "Pass")])
            df.loc["nb_passe", "Bottom 15"] += len(passe_bottom15)

    df.loc["Moyenne"] = df.loc["nb_passe"]/df.loc["nb_but"]
    df.loc["Moyenne"].to_excel(f"Passes avant un but/Tableaux/moy{annee}.xlsx")
    