import streamlit as st

import numpy as np

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