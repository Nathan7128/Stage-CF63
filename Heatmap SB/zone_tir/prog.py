import pandas as pd


liste_saison = ["2023_2024", "2022_2023", "2021_2022", "2020_2021"]


for saison in liste_saison :

    event = pd.read_json(f"Data_file/Heatmap SB/{saison}.json")

    shot = event[(event.type == "Shot") & (event.shot_type != "Penalty")]

    df = pd.concat([pd.DataFrame(shot.location.tolist()), pd.Series(shot.team.tolist()), pd.Series(shot.match_id.tolist())], axis = 1)

    df.drop(2, axis = 1, inplace = True)

    df.columns = ["x", "y", "Équipe", "match_id"]

    df.to_excel(f"Heatmap SB/zone_tir/Tableaux/{saison}.xlsx")