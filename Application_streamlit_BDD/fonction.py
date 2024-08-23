# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Importation des librairies


import streamlit as st

import numpy as np

from mplsoccer import Pitch

import pandas as pd

import sqlite3


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Définitions des fonctions


# Fonctions utilisées sur toutes les pages


def func_change(key1, key2) :

    """Associe à la clé d'un widget la valeur de l'élément du session state en question
    La clé du widget est toujours égale à "widg_" + la clé de l'élément du session_state
    L'association est réalisée dans l'unique cas ou la valeur de l'élément du session state a été initialisée
    Args:
        key : Clé du widget
    """

    st.session_state[key1] = st.session_state[key2]


def execute_SQL(_cursor, stat, params) :

    """Éxécute une requête sql via un curseur et des paramètres

    Args:
        cursor : Curseur lié à la base de donnée
        stat : Requête à effectuer
        params : Paramètres de la requête

    Returns:
        _type_: Résultat de la requête
    """

    return _cursor.execute(stat, params)


def replace_saison1(saison) :
    if type(saison) == list :
        return [i.replace("/", "_") for i in saison]
    else :
        return saison.replace("/", "_")

def replace_saison2(saison) :
    if type(saison) == list :
        return [i.replace("_", "/") for i in saison]

    else :
        return saison.replace("_", "/")






# 1/ Métriques discriminantes

def couleur_diff(col) :

    """Modifie la couleur des lignes(métriques) des colonnes différenciant 2 groupes d'équipe.
    Modifie en vert si la différence est positive et en rouge si elle est strictement négative
    Si la colonne ne différencie pas 2 groupes, on n'applique pas de couleur

    Args:
        col : Colonne du dataframe passée en argument par le .apply()

    Returns:
        list : liste des couleurs à appliquer à la colonne
    """

    if col.name in ["Diff. Top avec Bottom en %", "Diff. Top avec Middle en %", "Diff. Middle avec Bottom en %"] :
        color = []

        for met in col.index :
            if col.loc[met] >= 0 :
                color.append("background-color : rgba(0, 255, 0, 0.3)")
            else : 
                color.append("background-color : rgba(255, 0, 0, 0.3)")
        return color
    
    else :
        return ['']*len(col)







def label_heatmap(bin_statistic) :
    dico_label_heatmap = {
        "Pourcentage" : {"statistique" : np.round(bin_statistic, 2), "str_format" : '{:.0%}'},
        "Pourcentage sans %" : {"statistique" : 100*np.round(bin_statistic, 2), "str_format" : '{:.0f}'},
        "Valeur" : {"statistique" : bin_statistic, "str_format" : '{:.0f}'},
    }
    return dico_label_heatmap

def label_heatmap_centre(bin_statistic, bin_statistic_but) :
    dico_label_heatmap = label_heatmap(bin_statistic)
    dico_label_heatmap.update({
        "Pourcentage de but" : {"statistique" : np.round(np.nan_to_num((bin_statistic_but/bin_statistic), 0), 2),
                                "str_format" : '{:.0%}'},
        "Pourcentage de but sans %" : {"statistique" : 100*np.round(np.nan_to_num((bin_statistic_but/bin_statistic), 0), 2),
                                       "str_format" : '{:.0f}'}
    })
    return dico_label_heatmap






# def best_zone(data, taille_min_centre, taille_max_centre, nb_but_min) :
#     pitch = Pitch(pitch_type = "statsbomb")

#     columns_df = ["N° colonne", "N° ligne", "% de but", "Nombre de colonne", "Nombre de ligne", "Nombre de but"]
#     df = pd.DataFrame([np.zeros(len(columns_df))], columns = columns_df)

#     nb_zone = 10

#     for bins_centre_v in range (int((52.5/taille_max_centre)), int((52.5/taille_min_centre)) + 1) :

#         for bins_centre_h in range (int(68/taille_max_centre), int(68/taille_min_centre) + 1) :

#             bin_pitch = pitch.bin_statistic(data.x, data.y, values = None, statistic='count', bins=(bins_centre_v*2, bins_centre_h))
#             bin_statistic = bin_pitch["statistic"]
#             bin_pitch_but = pitch.bin_statistic(data[data.But == 1].x, data[data.But == 1].y, values = None, statistic='count',
#                                     bins=(bins_centre_v*2, bins_centre_h))
#             bin_statistic_but = bin_pitch_but["statistic"]
#             bin_statistic = np.nan_to_num(bin_statistic_but/bin_statistic, 0)

#             df_centre = pd.DataFrame({
#                 "N° colonne" : [j for j in range (1, bins_centre_h + 1) for i in range (1, bins_centre_v*2 + 1)],
#                 "N° ligne" : [j - bins_centre_v for i in range (1, bins_centre_h + 1) for j in range (1, bins_centre_v*2 + 1)],
#                 "% de but" : bin_statistic.ravel(),
#                 "Nombre de but" : bin_statistic_but.ravel()
#             })
#             df_centre["Nombre de colonne"] = bins_centre_h
#             df_centre["Nombre de ligne"] = bins_centre_v    

#             df_centre = df_centre[(df_centre["% de but"] > min(df["% de but"])) & (df_centre["Nombre de but"] >= nb_but_min)]

#     df = pd.concat([df, df_centre], axis = 0).sort_values(by = "% de but", ascending = False).head(nb_zone)

#     df['% de but'] = (100*df['% de but']).round(1).astype(str) + " %"

#     return df



# def best_zone(data, taille_min_centre, taille_max_centre, taille_min_recep, taille_max_recep, pas_centre, pas_recep) :
#     pitch = Pitch(pitch_type = "statsbomb")

#     df = pd.DataFrame([[0, 0, 0, 0, 0, 0, 0, 0]], columns = ["colonne", "ligne", "% de but", "taille_vert_centre", "taille_hor_centre", "bins_centre_v", "bins_centre_h", "nb_but"])

#     for taille_vert_centre in np.arange (taille_min_centre, taille_max_centre, pas_centre) :
#         bins_centre_v = int((52.5/taille_vert_centre))
#         for taille_hor_centre in np.arange (taille_min_centre, taille_max_centre, pas_centre) :
#             bins_centre_h = int(68/taille_hor_centre)
#             bin_statistic = pitch.bin_statistic(data.x, data.y, values = None, statistic='count', bins=(bins_centre_v*2, bins_centre_h))["statistic"]
#             bin_statistic_but = pitch.bin_statistic(data[data.But == 1].x, data[data.But == 1].y, values = None, statistic='count',
#                                     bins=(bins_centre_v*2, bins_centre_h))["statistic"]
#             bin_statistic = np.nan_to_num(bin_statistic_but/bin_statistic, 0)
#             df_centre = pd.DataFrame({
#                 "colonne" : [j for j in range (1, bins_centre_h + 1) for i in range (1, bins_centre_v*2 + 1)],
#                 "ligne" : [j - bins_centre_v for i in range (1, bins_centre_h + 1) for j in range (1, bins_centre_v*2 + 1)],
#                 "% de but" : bin_statistic.ravel(),
#                 "nb_but" : bin_statistic_but.ravel()
#             })
#             df_centre["taille_vert_centre"] = taille_vert_centre
#             df_centre["taille_hor_centre"] = taille_hor_centre
#             df_centre["bins_centre_v"] = bins_centre_v
#             df_centre["bins_centre_h"] = bins_centre_h
#             df = pd.concat([df, df_centre[(df_centre["% de but"] > min(df["% de but"])) & (df_centre.nb_but > 10)]], axis = 0).sort_values(by = "% de but", ascending = False).head(10)
#     st.write(df)