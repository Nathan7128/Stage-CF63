import pandas as pd


liste_annee = ["2023_2024", "2022_2023", "2021_2022", "2020_2021"]

for annee in liste_annee :
    df = pd.read_json(f"Data_file/Heatmap SB/{annee}.json")
    df.set_index(["match_id", "period", "possession"], inplace = True)
    goal = df[(df.shot_type == "Open Play") & ((df.shot_outcome == "Goal") | (df.type == "Own Goal Against"))]
    df_goal = df.loc[goal.index]
    deb_action = df_goal.groupby(level = [0, 1, 2], sort = False).head(1)
    deb_action["type_action"] = deb_action.pass_type.fillna(deb_action.shot_type).fillna(deb_action.type)
    count_passe = df_goal[df_goal.type == "Pass"].groupby(["match_id", "period", "possession"],sort = False, as_index = True).size()
    goal = pd.concat([goal, count_passe, deb_action.type_action], axis = 1)
    goal.rename({0 : "Passe"}, axis = 1, inplace = True)
    goal.replace(to_replace = ['Interception', 'Ball Recovery', 'Duel', 'Recovery', 'Pass', 'Goal Keeper', '50/50'], value = "Open play", inplace = True)
    goal = goal.reset_index()[["team", "Passe", "type_action"]]
    goal.to_excel(f"Passes avant un but/{annee}.xlsx")