import pandas as pd

import sqlite3

connect = sqlite3.connect("raw-database.db")
cursor = connect.cursor()

match_drop = [1550555, 1546206, 129364, 128946]

req = cursor.execute("SELECT * FROM raw_data_passes")
res = req.fetchall()
desc = req.description
df = pd.DataFrame(res)
df.columns = [i[0] for i in desc]

drop = ['player_name_per_match', "player_id", 'short_name_per_match', 'player_birthdate_per_match', 'match_name_per_match',
     'match_date_per_match', 'team_id_per_match', 'competition_id_per_match', 'season_id_per_match',
     'competition_edition_id_per_match', 'position_per_match', 'group_per_match', 'venue_per_match', 'third_per_match',
     'adjusted_min_tip_per_match_per_match', 'quality_check_per_match'] + df.columns[["sample" in i for i in df.columns]].tolist()
rename = {'team_name_per_match' : "team_name", 'competition_name_per_match' : "Compet", 'season_name_per_match' : "Saison",
          'result_per_match' : "result", 'minutes_played_per_match_per_match' : "minutes_played_per_match"}
df = df[(df.quality_check_per_match == True) & (~df.match_id.isin(match_drop))].drop(drop, axis = 1).rename(rename, axis = 1).fillna(0)

col_ratio_init = df.columns[["ratio" in i for i in df.columns]]
col_ratio = [i.replace("_per_match", "") for i in col_ratio_init]
rename_ratio = dict(zip(col_ratio_init, col_ratio))
df.rename(rename_ratio, axis = 1, inplace = True)

col_met = [i for i in df.columns[5:] if i not in col_ratio + ["minutes_played_per_match"]]

agg_dict = {col : lambda x: x.head(1) for col in df.columns[:5]}
agg_dict.update({col : "mean" for col in col_ratio})
agg_dict.update({col : "sum" for col in col_met + ["minutes_played_per_match"]})
df = df.groupby(["match_id", "team_name"], as_index = False, sort = False).agg(agg_dict)

nb_minute_match = df.pop("minutes_played_per_match")
df[col_met] = df[col_met].apply(lambda x : 900*x/nb_minute_match, axis = 0)

req = cursor.execute("SELECT * from match_round_SK")
match_round = pd.DataFrame(req.fetchall(), columns = ["match_id", "Journée"])

df = pd.merge(match_round, df, on = "match_id")

connect.close()


connect = sqlite3.connect("database.db")

df.to_sql(name = "Passes", con = connect, if_exists = "replace", index = False)

connect.close()