# import pandas as pd

# import sqlite3

# connect = sqlite3.connect("database.db")
# cursor = connect.cursor()

# match_drop = [1550555, 1546206, 129364, 128946]

# rename = {'team_name_x' : "team_name", 'competition_name_x' : "Compet", 'season_name_x' : "Saison"}

# def rename_col(col) :
#     if "full_all" in col :
#         return col.replace("full_all", "per_match")
#     elif "full_otip_p30otip" in col :
#         return col.replace("full_otip_p30otip", "per_30_min_otip")
#     elif "full_tip_p30tip" in col :
#         return col.replace("full_tip_p30tip", "per_30_min_tip")
#     elif col in rename.keys() :
#         return rename[col]
#     else :
#         return col

# req = cursor.execute("SELECT * FROM raw_data_physical")
# res = req.fetchall()
# desc = req.description
# df = pd.DataFrame(res)
# df.columns = [i[0] for i in desc]

# drop = ["player_name_x", "player_short_name_x", "psv99", "player_id", "player_birthdate_x", "team_id_x", "match_name_x",
#             "match_date_x", "competition_id_x", "season_id_x", "competition_edition_id_x", "position_x", "position_group_x",
#             "minutes_full_tip", "minutes_full_otip", "physical_check_passed_x", "minutes_full_all"]

# df = df[~df.match_id.isin(match_drop)].drop(drop, axis = 1).rename(columns = rename_col).fillna(0)

# agg_dict = {col : lambda x: x.head(1) for col in df.columns[:4]}
# agg_dict.update({col : "mean" for col in df.columns[4:]})
# df = df.groupby(["match_id", "team_name"], as_index = False, sort = False).agg(agg_dict)

# req = cursor.execute("SELECT match_id, Journée, result from Passes")
# match_infos = pd.DataFrame(req.fetchall(), columns = ["match_id", "Journée", "result"])
# match_infos = match_infos.groupby("match_id").head(1)
# df = pd.merge(match_infos, df, on = "match_id")

# df.to_sql(name = "Physical", con = connect, if_exists = "replace", index = False)

# connect.close()



import pandas as pd

import sqlite3

connect = sqlite3.connect("database.db")
cursor = connect.cursor()

df = pd.concat([pd.read_excel(f"Données brutes/Métriques Team sur une Saison Ligue 2 SB + SK/{saison}/data_physical.xlsx", index_col = 0)
                  for saison in ["2021_2022", "2022_2023", "2023_2024"]])

match_drop = [1550555, 1546206, 129364, 128946]

rename = {'competition_name' : "Compet", 'season_name' : "Saison"}

def rename_col(col) :
    if "full_all" in col :
        return col.replace("full_all", "per_match")
    elif "full_otip_p30otip" in col :
        return col.replace("full_otip_p30otip", "per_30_min_otip")
    elif "full_tip_p30tip" in col :
        return col.replace("full_tip_p30tip", "per_30_min_tip")
    elif col in rename.keys() :
        return rename[col]
    else :
        return col

drop = ["player_name", "player_short_name", "psv99", "player_id", "player_birthdate", "team_id", "match_name",
            "match_date", "competition_id", "season_id", "competition_edition_id", "position", "position_group",
            "minutes_full_tip", "minutes_full_otip", "physical_check_passed"]

df = df[~df.match_id.isin(match_drop)].drop(drop, axis = 1).rename(columns = rename_col).fillna(0)
df.Compet = df.Compet.apply(lambda x : x.replace("FRA - ", ""))

agg_dict = {col : lambda x: x.head(1) for col in df.columns[:4]}
agg_dict.update({col : "sum" for col in df.columns[4:]})
df = df.groupby(["match_id", "team_name"], as_index = False, sort = False).agg(agg_dict)
nb_minute_match = df.pop("minutes_per_match")
df[df.columns[4:]] = df[df.columns[4:]].apply(lambda x : 900*x/nb_minute_match, axis = 0)

req = cursor.execute("SELECT match_id, Journée, result from Passes")
match_infos = pd.DataFrame(req.fetchall(), columns = ["match_id", "Journée", "result"])
match_infos = match_infos.groupby("match_id").head(1)
df = pd.merge(df, match_infos, on = "match_id")

df.to_sql(name = "Physical", con = connect, if_exists = "replace", index = False)

connect.close()