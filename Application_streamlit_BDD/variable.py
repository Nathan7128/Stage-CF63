
import matplotlib.patheffects as path_effects
from matplotlib.colors import LinearSegmentedColormap

path_effect_1 = [path_effects.Stroke(linewidth=1, foreground='black'), path_effects.Normal()]
path_effect_2 = [path_effects.Stroke(linewidth=1.5, foreground='black'), path_effects.Normal()]

colormapblue = LinearSegmentedColormap.from_list('custom_cmap', [(1, 1, 1), (0, 45/255, 106/255)])
colormapred = LinearSegmentedColormap.from_list('custom_cmap', [(1, 1, 1), (198/255, 11/255, 70/255)])

dico_label = {"Choisir Top/Middle/Bottom" : ["du"], "Choisir équipe" : ["de"]}

dico_met = {
    "Physiques" : ["Physical",
        {"30 min. tip" : "_per30tip", "30 min. otip" : "_per30otip", "Match all possession" : "_per_Match"}],
    
    "Courses sans ballon avec la possession" : ["Running",
        {"Match" : "per_match", "100 runs" : "per_100_runs", "30 min. tip" : "per_30_min_tip"},
        "Type de course",
        {"Runs in behind" : "runs_in_behind", "Runs ahead of the ball" : "runs_ahead_of_the_ball", "Support runs" : "support_runs",
        "Pulling wide runs" : "pulling_wide_runs", "Coming short runs" : "coming_short_runs", "Underlap runs" : "underlap_runs",
        "Overlap runs" : "overlap_runs", "Dropping off runs" : "dropping_off_runs",
        "Pulling half space runs" : "pulling_half_space_runs", "Cross receiver runs" : "cross_receiver_runs"},
        {"Leading to goal" : "leading_to_goal", "Leading to shot" : "leading_to_shot", "Received" : "received", "Threat" : "threat",
        "Targeted" : "targeted", "Dangerous" : "dangerous"}],

    "Action sous pression" : ["Pressure",
        {"Match" : "per_match", "100 pressures" : "per_100_pressures", "30 min. tip" : "per_30_min_tip"},
        "Intensité de pression",
        {"Low" : "low", "Medium" : "medium", "High" : "high"}],
    
    "Passes à un coéquipier effectuant une course" : ["Passes",
        {"Match" : "per_match", "100 passes opportunities" : "per_100_pass_opportunities", "30 min. tip" : "per_30_min_tip"},
        "Type de course",
        {"Runs in behind" : "runs_in_behind", "Runs ahead of the ball" : "runs_ahead_of_the_ball", "Support runs" : "support_runs",
        "Pulling wide runs" : "pulling_wide_runs", "Coming short runs" : "coming_short_runs", "Underlap runs" : "underlap_runs",
        "Overlap runs" : "overlap_runs", "Dropping off runs" : "dropping_off_runs",
        "Pulling half space runs" : "pulling_half_space_runs", "Cross receiver runs" : "cross_receiver_runs"}]
}


dico_rank_SK = {"2023_2024" : ["AJ Auxerre", "Angers SCO", "AS Saint-Étienne", "Rodez Aveyron", "Paris FC", "SM Caen", "Stade Lavallois Mayenne FC",
           "Amiens Sporting Club", "En Avant de Guingamp", "Pau FC", "Grenoble Foot 38", "Girondins de Bordeaux", "SC Bastia",
           "FC Annecy", "AC Ajaccio", "Dunkerque", "ES Troyes AC", "US Quevilly-Rouen", "US Concarneau", "Valenciennes FC"],
           "2022_2023" : ["Le Havre AC", "FC Metz", "Girondins de Bordeaux", "SC Bastia", "SM Caen", "En Avant de Guingamp", "Paris FC",
           "AS Saint-Étienne", "FC Sochaux-Montbéliard", "Grenoble Foot 38", "US Quevilly-Rouen", "Amiens Sporting Club", "Pau FC",
           "Rodez Aveyron", "Stade Lavallois Mayenne FC", "Valenciennes FC", "FC Annecy", "Dijon FCO", "Nîmes Olympique", "Chamois Niortais FC"],
           "2021_2022" : ["Toulouse FC", "AC Ajaccio", "AJ Auxerre", "Paris FC", "FC Sochaux-Montbéliard", "En Avant de Guingamp",
                             "SM Caen", "Le Havre AC", "Nîmes Olympique", "Pau FC", "Dijon FCO", "SC Bastia", "Chamois Niortais FC", 
                             "Amiens Sporting Club", "Grenoble Foot 38", "Valenciennes FC", "Rodez Aveyron", "US Quevilly-Rouen",
                             "Dunkerque", "AS Nancy-Lorraine"]}


dico_rank_SB = {
    "2023_2024" : ["Auxerre", "Angers", "Saint-Étienne", "Rodez", "Paris FC", "Caen", "Laval",
           "Amiens", "Guingamp", "Pau", "Grenoble Foot", "Bordeaux", "Bastia",
           "FC Annecy", "AC Ajaccio", "Dunkerque", "Troyes", "Quevilly Rouen", "Concarneau", "Valenciennes"],
    "2022_2023" :["Le Havre", "Metz", "Bordeaux", "Bastia", "Caen", "Guingamp", "Paris FC",
           "Saint-Étienne", "Sochaux", "Grenoble Foot", "Quevilly Rouen", "Amiens", "Pau",
           "Rodez", "Laval", "Valenciennes", "FC Annecy", "Dijon", "Nîmes", "Chamois Niortais"],
    "2021_2022" : ["Toulouse", "AC Ajaccio", "Auxerre", "Paris FC", "Sochaux", "Guingamp", "Caen", "Le Havre", "Nîmes",
                             "Pau", "Dijon", "Bastia", "Chamois Niortais", "Amiens", "Grenoble Foot", "Valenciennes", "Rodez", 
                             "Quevilly Rouen", "Dunkerque", "Nancy"],
    "2020_2021" : ["Troyes", "Clermont Foot", "Toulouse", "Grenoble Foot", "Paris FC", "Auxerre", "Sochaux", "Nancy",
                             "Guingamp", "Amiens", "Valenciennes", "Le Havre", "AC Ajaccio", "Pau", "Rodez", "Dunkerque", "Caen", 
                             "Chamois Niortais", "Chambly", "Châteauroux"]
                             }

dico_cat_run = {"Dangerous" : "dangerous",
                                "Leading to shot" : "leading_to_shot",
                                "Leading to goal" : "leading_to_goal"}

dico_cat_pressure = {"Passes" : "pass", "Conservation du ballon" : "ball_retention", "Perte de balle" : "forced_losses",
                                        "Pression reçue" : "received_per"}

dico_cat_passe = {"Attempts" : "attempt", "Completed" : "completed", "Opportunities" : "opportunities"}
