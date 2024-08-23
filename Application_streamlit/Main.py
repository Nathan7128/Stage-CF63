import streamlit as st

dico_session_state = {
    "provider" : "Skill Corner",
    "cat_met" : "Physiques",
    "nb_top_met" : 3,
    "nb_bottom_met" : 3,
    "threat_run" : True,
    "result_passe_pressure" : ["Attempts", "Completed"],
    "ratio_passe_pressure" : True,
    "ratio_conserv_pressure" : True,
    "threat_passe" : True,
    "ratio_passe" : True,
    "nb_top_nb_passe" : 3,
    "nb_bottom_nb_passe" : 3,
    'type_action_nb_passe' : ["Open play"],
    "nb_top_heatmap" : 3,
    "nb_bottom_heatmap" : 3,
    'type_action_heatmap' : ["Open play"],
    "partie_corps" : "All"
}

for key in dico_session_state.keys() :
    if key not in st.session_state :
        st.session_state[key] = dico_session_state[key]

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