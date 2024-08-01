import streamlit as st

import numpy as np

from mplsoccer import Pitch

import pandas as pd

def func_change(key1, key2) :
    st.session_state[key1] = st.session_state[key2]

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

def best_zone(data, taille_min_centre, taille_max_centre, taille_min_recep, taille_max_recep, pas_centre, pas_recep) :
    pitch = Pitch(pitch_type = "statsbomb")
    df = pd.DataFrame(columns = ["bins_centre_h", "bins_centre_v", "bins_h_max", "bins_v_max", "% de but"])
    # tailles en mètres
    for taille_vert_centre in np.arange (taille_min_centre, taille_max_centre, pas_centre) :
        bins_centre_v = int((105/taille_vert_centre)/2)
        for taille_hor_centre in np.arange (taille_min_centre, taille_max_centre, pas_centre) :
            st.write(bins_centre_v)
            bins_centre_h = int(68/taille_hor_centre)
            st.write(bins_centre_h)
            bin_statistic = pitch.bin_statistic(data.x, data.y, values = None, statistic='count', bins=(bins_centre_v*2, bins_centre_h))["statistic"]
            bin_statistic_but = pitch.bin_statistic(data[data.But == 1].x, data[data.But == 1].y, values = None, statistic='count',
                                    bins=(bins_centre_v*2, bins_centre_h))["statistic"]
            bin_statistic = np.nan_to_num(bin_statistic_but/bin_statistic, 0)
            st.write(np.unravel_index(np.argmax(bin_statistic), bin_statistic.shape))
            st.write(bin_statistic)
            st.write(bin_statistic.ravel())
            st.write(pd.DataFrame(pd.MultiIndex.from_product([range(1, bins_centre_h + 1), range(1, bins_centre_v + 1)])))
            return df
    # return df