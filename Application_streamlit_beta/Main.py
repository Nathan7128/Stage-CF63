import streamlit as st

dico_session_state = {
    "choix_data" : "Skill Corner",
    "cat_met" : "Physiques",
    'Type_action_deb_action' : ["Open play"],
    'Type_action_passes' : ["Open play"]
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

