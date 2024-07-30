import streamlit as st
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patheffects as path_effects

liste_page = []
liste_page.append(st.Page("apps/10_Métriques_discriminantes.py", title = "Métriques discriminantes"))
liste_page.append(st.Page("apps/20_Évolutions_par_journée.py", title = "Évolution des métriques par journée"))
liste_page.append(st.Page("apps/30_Évolution_par_saison.py", title = "Évolution des métriques par saison"))
liste_page.append(st.Page("apps/31_Passes_avant_but.py", title = "Nombre de passe avant un but"))
liste_page.append(st.Page("apps/40_Heatmap_zone_debut_action_avant_tir.py", title = "Heatmap des zones de début d'action avant un but"))
liste_page.append(st.Page("apps/60_Heatmap_zone_de_tir.py", title = "Heatmap des zones de tir"))
liste_page.append(st.Page("apps/70_Heatmap_zone_de_centre_et_réception.py", title = "Heatmap des zones de centres"))

pg = st.navigation(liste_page)

pg.run()

dico_session_state = {
    "colormapblue" : LinearSegmentedColormap.from_list('custom_cmap', [(1, 1, 1), (0, 47/255, 103/255)]),
    "colormapred" : LinearSegmentedColormap.from_list('custom_cmap', [(1, 1, 1), (195/255, 1/255, 64/255)]),
    "path_eff_heatmap" : [path_effects.Stroke(linewidth=1.5, foreground='black'), path_effects.Normal()],
}

for key in dico_session_state.keys() :
    if key not in st.session_state :
        st.session_state[key] = dico_session_state[key]