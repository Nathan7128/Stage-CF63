# FICHIER CONTENANT LES VARIABLES QUI SE RÉPÈTENT ENTRE PLUSIEURS PAGES


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Importation des librairies


import pandas as pd
import matplotlib.patheffects as path_effects
from matplotlib.colors import LinearSegmentedColormap


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Définitions des variables


# Dictionnaire de dictionnaire avec comme clé le nom des 4 catégories de métriques
# Chaque sous-dictionnaire contient le nom de la table correspondante et les différents niveaux d'aggrégations
# Pour les catégories autre que Physique, les sous-dictionnaires contiennent d'avantages de filtre sur les métriques comme
# le type de pression/type de course...
dico_met = {
    "Physique" : ["Physical",
        {"30 min. tip" : "_per_30_min_tip", "30 min. otip" : "_per_30_min_otip", "Match all possession" : "_per_match"}],
    
    "Course sans ballon avec la possession" : ["Running",
        {"Match" : "_per_match", "100 runs" : "_per_100_runs", "30 min. tip" : "_per_30_min_tip"},
        "Type de course",
        {"Runs in behind" : "runs_in_behind", "Runs ahead of the ball" : "runs_ahead_of_the_ball", "Support runs" : "support_runs",
        "Pulling wide runs" : "pulling_wide_runs", "Coming short runs" : "coming_short_runs", "Underlap runs" : "underlap_runs",
        "Overlap runs" : "overlap_runs", "Dropping off runs" : "dropping_off_runs",
        "Pulling half space runs" : "pulling_half_space_runs", "Cross receiver runs" : "cross_receiver_runs"},
        {"Leading to goal" : "leading_to_goal", "Leading to shot" : "leading_to_shot", "Received" : "received", "Threat" : "threat",
        "Targeted" : "targeted", "Dangerous" : "dangerous"}],

    "Action sous pression" : ["Pressure",
        {"Match" : "_per_match", "100 pressures" : "_per_100_pressures", "30 min. tip" : "_per_30_min_tip"},
        "Intensité de pression",
        {"Low" : "low", "Medium" : "medium", "High" : "high"}],
    
    "Passe à un coéquipier effectuant une course" : ["Passes",
        {"Match" : "_per_match", "100 passes opportunities" : "_per_100_pass_opportunities", "30 min. tip" : "_per_30_min_tip"},
        "Type de course",
        {"Runs in behind" : "runs_in_behind", "Runs ahead of the ball" : "runs_ahead_of_the_ball", "Support runs" : "support_runs",
        "Pulling wide runs" : "pulling_wide_runs", "Coming short runs" : "coming_short_runs", "Underlap runs" : "underlap_runs",
        "Overlap runs" : "overlap_runs", "Dropping off runs" : "dropping_off_runs",
        "Pulling half space runs" : "pulling_half_space_runs", "Cross receiver runs" : "cross_receiver_runs"}]
}


# Dictionnaire contenant pour chaque saison le classement de ligue 2 avec les noms d'équipe au format Skill Corner
dico_rank_SK = {
    "2023/2024" : ["AJ Auxerre", "Angers SCO", "AS Saint-Étienne", "Rodez Aveyron", "Paris FC", "SM Caen",
                   "Stade Lavallois Mayenne FC", "Amiens Sporting Club", "En Avant de Guingamp", "Pau FC", "Grenoble Foot 38",
                   "Girondins de Bordeaux", "SC Bastia", "FC Annecy", "AC Ajaccio", "Dunkerque", "ES Troyes AC", "US Quevilly-Rouen",
                   "US Concarneau", "Valenciennes FC"],
    "2022/2023" : ["Le Havre AC", "FC Metz", "Girondins de Bordeaux", "SC Bastia", "SM Caen", "En Avant de Guingamp", "Paris FC",
                   "AS Saint-Étienne", "FC Sochaux-Montbéliard", "Grenoble Foot 38", "US Quevilly-Rouen", "Amiens Sporting Club",
                   "Pau FC", "Rodez Aveyron", "Stade Lavallois Mayenne FC", "Valenciennes FC", "FC Annecy", "Dijon FCO",
                   "Nîmes Olympique", "Chamois Niortais FC"],
    "2021/2022" : ["Toulouse FC", "AC Ajaccio", "AJ Auxerre", "Paris FC", "FC Sochaux-Montbéliard", "En Avant de Guingamp", "SM Caen",
                   "Le Havre AC", "Nîmes Olympique", "Pau FC", "Dijon FCO", "SC Bastia", "Chamois Niortais FC", 
                   "Amiens Sporting Club", "Grenoble Foot 38", "Valenciennes FC", "Rodez Aveyron", "US Quevilly-Rouen", "Dunkerque",
                   "AS Nancy-Lorraine"]
                   }


# Dictionnaire contenant pour chaque saison le classement de ligue 2 avec les noms d'équipe au format Stats Bomb
dico_rank_SB = {
    "2023/2024" : ["Auxerre", "Angers", "Saint-Étienne", "Rodez", "Paris FC", "Caen", "Laval", "Amiens", "Guingamp", "Pau",
                   "Grenoble Foot", "Bordeaux", "Bastia", "FC Annecy", "AC Ajaccio", "Dunkerque", "Troyes", "Quevilly Rouen",
                   "Concarneau", "Valenciennes"],
    "2022/2023" :["Le Havre", "Metz", "Bordeaux", "Bastia", "Caen", "Guingamp", "Paris FC", "Saint-Étienne", "Sochaux",
                  "Grenoble Foot", "Quevilly Rouen", "Amiens", "Pau", "Rodez", "Laval", "Valenciennes", "FC Annecy", "Dijon", "Nîmes",
                  "Chamois Niortais"],
    "2021/2022" : ["Toulouse", "AC Ajaccio", "Auxerre", "Paris FC", "Sochaux", "Guingamp", "Caen", "Le Havre", "Nîmes", "Pau",
                   "Dijon", "Bastia", "Chamois Niortais", "Amiens", "Grenoble Foot", "Valenciennes", "Rodez",  "Quevilly Rouen",
                   "Dunkerque", "Nancy"],
    "2020/2021" : ["Troyes", "Clermont Foot", "Toulouse", "Grenoble Foot", "Paris FC", "Auxerre", "Sochaux", "Nancy", "Guingamp",
                   "Amiens", "Valenciennes", "Le Havre", "AC Ajaccio", "Pau", "Rodez", "Dunkerque", "Caen",  "Chamois Niortais",
                   "Chambly", "Châteauroux"]
                   }


# Dictionnaire contenant les différentes catégories de métriques pour la catégorie Running, et leur correspondance au vu des noms
# des métriques dans le dataframe
dico_cat_run = {"Dangerous" : "dangerous", "Leading to shot" : "leading_to_shot", "Leading to goal" : "leading_to_goal"}


# Liste contenant les différentes catégories de métriques pour la catégorie Running, avec aussi "All" qui correspond aux autres
# métriques qui n'appartiennent pas à une catégorie spécifique
liste_cat_run = ["All"] + list(dico_cat_run.keys())


# Dictionnaire contenant les différents types de réception de passe pour la catégorie Running
liste_type_passe_run = ["Targeted", "Received"]


# Dictionnaire contenant les différentes catégories de métriques pour la catégorie Pressure comme clé, et leur correspondance
# au vu des noms des métriques dans le dataframe
dico_cat_pressure = {"Passes" : "pass", "Conservation du ballon" : "ball_retention", "Perte de balle" : "forced_losses",
                     "Pression reçue" : "received_per"}


# Liste contenant les différentes catégories de métriques pour la catégorie Pressure 
liste_cat_pressure = list(dico_cat_pressure.keys())


# Liste contenant les différentes catégories de passes effectuées sous pression pour la catégorie Pressure 
liste_cat_passe_pressure = ["All", "Dangerous", "Difficult"]


# Dictionnaire contenant les différentes catégories de passes pour la catégorie Passes, et leur correspondance au vu des noms des
# métriques dans le dataframe
dico_cat_passe = {"Attempts" : "attempt", "Completed" : "completed", "Opportunities" : "opportunities"}


# Dictionnaire contenant les différentes catégories de passes pour la catégorie Passes
liste_type_passe = list(dico_cat_passe.keys())


# Dataframe permettant le choix de la taille des différents groupes d'équipes
df_taille_groupe = pd.DataFrame(0, index = ["Top", "Middle", "Bottom"], columns = ["Taille", "Slider"])
df_taille_groupe["Slider"] = "Nombre d'équipe dans le " + df_taille_groupe.index


# Mise en forme du texte des heatmaps des les zones de début d'action
path_effect_1 = [path_effects.Stroke(linewidth=1, foreground='black'), path_effects.Normal()]

# Mise en forme du texte des heatmaps pour les zones de tir et de centre
path_effect_2 = [path_effects.Stroke(linewidth=1.5, foreground='black'), path_effects.Normal()]

# Colormap des heatmaps de gauche
colormapred = LinearSegmentedColormap.from_list('custom_cmap', [(1, 1, 1), (198/255, 11/255, 70/255)])

# Colormap des heatmaps de droite
colormapblue = LinearSegmentedColormap.from_list('custom_cmap', [(1, 1, 1), (0, 45/255, 106/255)])

# Dictionnaire pour l'affichage des titres des heatmaps
dico_label = {"Choisir Top/Middle/Bottom" : ["du"], "Choisir équipe" : ["de"]}