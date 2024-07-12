import pandas as pd

dico = {
    "annee" : ["2023_2024", "2022_2023", "2021_2022", "2020_2021"],
    "top5" : [["Auxerre", "Angers", "Saint-Étienne", "Rodez", "Paris FC"],
                 ["Le Havre", "Metz", "Bordeaux", "Bastia", "Caen"],
                 ["Toulouse", "AC Ajaccio", "Auxerre", "Paris FC", "Sochaux"],
                 ["Troyes", "Clermont Foot", "Toulouse", "Grenoble Foot", "Paris FC"]]
}

for i in range (4) :
    annee = dico["annee"][i]
    top5 = dico["top5"][i]
    df = pd.read_json(f"Data_file/Heatmap SB/{annee}.json")
    df.set_index(["match_id", "period", "possession"], inplace = True)
    goal = df[(df.shot_type == "Open Play") & ((df.shot_outcome == "Goal") | (df.type == "Own Goal Against"))]
    df_goal = df.loc[goal.index]
    count_passe = df_goal[df_goal.type == "Pass"].groupby(["match_id", "period", "possession"],sort = False, as_index = True).size()
    goal = pd.concat([goal, count_passe], axis = 1)
    goal.rename({0 : "Passe"}, axis = 1, inplace = True)
    goal = goal.reset_index()[["team", "Passe"]]
    nb_but = goal.groupby("team").size()
    goal = goal.groupby("team").sum()
    goal = goal.divide(nb_but, axis = 0)
    goal["Top 5"] = 0
    goal.loc[goal.index.isin(dico["top5"][i]), "Top 5"] = 1
    goal.to_excel(f"Passes avant un but/{annee}.xlsx")