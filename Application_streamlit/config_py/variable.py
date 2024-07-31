dico_type = {
    "Physiques" : ["physical.xlsx",
        {"30 min. tip" : "_per30tip", "30 min. otip" : "_per30otip", "Match all possession" : "_per_Match"}],
    
    "Courses sans ballon avec la possession" : ["running.xlsx",
        {"Match" : "per_match", "100 runs" : "per_100_runs", "30 min. tip" : "per_30_min_tip"},
        "Type de course",
        {"Runs in behind" : "runs_in_behind", "Runs ahead of the ball" : "runs_ahead_of_the_ball", "Support runs" : "support_runs",
        "Pulling wide runs" : "pulling_wide_runs", "Coming short runs" : "coming_short_runs", "Underlap runs" : "underlap_runs",
        "Overlap runs" : "overlap_runs", "Dropping off runs" : "dropping_off_runs",
        "Pulling half space runs" : "pulling_half_space_runs", "Cross receiver runs" : "cross_receiver_runs"},
        {"Leading to goal" : "leading_to_goal", "Leading to shot" : "leading_to_shot", "Received" : "received", "Threat" : "threat",
        "Targeted" : "targeted", "Dangerous" : "dangerous"}],

    "Action sous pression" : ["pressure.xlsx",
        {"Match" : "per_match", "100 pressures" : "per_100_pressures", "30 min. tip" : "per_30_min_tip"},
        "Intensité de pression",
        {"Low" : "low", "Medium" : "medium", "High" : "high"}],
    
    "Passes à un coéquipier effectuant une course" : ["passes.xlsx",
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

dico_cat_run = {"Dangerous" : "dangerous",
                                "Leading to shot" : "leading_to_shot",
                                "Leading to goal" : "leading_to_goal"}

dico_cat_met_pressure = {"Passes" : "pass", "Conservation du ballon" : "ball_retention", "Perte de balle" : "forced_losses",
                                        "Pression reçue" : "received_per"}

dico_type_passe = {"Attempts" : "attempt", "Completed" : "completed", "Opportunities" : "opportunities"}
