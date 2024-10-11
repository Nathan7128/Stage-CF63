import streamlit as st
from variable import liste_cat_run, liste_type_passe_run, liste_cat_pressure, liste_cat_passe_pressure, liste_cat_run, liste_type_passe

dico_session_state = {
    "provider" : "Skill Corner",
    "cat_met" : "Physique",
    "nb_top" : 3,
    "nb_bottom" : 3,
    "cat_run" : liste_cat_run,
    "type_passe_run" : liste_type_passe_run,
    "cat_pressure" : liste_cat_pressure,
    "cat_passe_pressure" : liste_cat_passe_pressure,
    "cat_run_passe" : liste_cat_run,
    "type_passe" : liste_type_passe,
    "threat_run" : True,
    "result_passe_pressure" : ["Attempts", "Completed"],
    "ratio_passe_pressure" : True,
    "ratio_conserv_pressure" : True,
    "threat_passe" : True,
    "ratio_passe" : True,
    'type_action' : ["Open play"],
    "partie_corps" : "All",
    "nb_col" : 5,
    "choix_col" : 0,
    "choix_ligne" : 0,
    "nb_col_gauche" : 5,
    "nb_col_droite" : 5,
    "choix_col_gauche" : 0,
    "choix_ligne_gauche" : 0,
    "choix_col_droite" : 0,
    "choix_ligne_droite" : 0    
}

for key in dico_session_state.keys() :
    if key not in st.session_state :
        st.session_state[key] = dico_session_state[key]

liste_page_app = []
liste_page_app.append(st.Page("apps/10_Métriques_discriminantes.py", title = "Métriques discriminantes"))
liste_page_app.append(st.Page("apps/20_Évolutions_par_journée.py", title = "Évolution des métriques par journée"))
liste_page_app.append(st.Page("apps/30_Évolution_par_saison.py", title = "Évolution des métriques par saison"))
liste_page_app.append(st.Page("apps/40_Passes_avant_but.py", title = "Nombre de passe avant un but"))
liste_page_app.append(st.Page("apps/50_Heatmap_zone_debut_action_avant_tir.py", title = "Heatmap des zones de début d'action avant un but"))
liste_page_app.append(st.Page("apps/60_Heatmap_zone_de_tir.py", title = "Heatmap des zones de tir"))
liste_page_app.append(st.Page("apps/70_Heatmap_zone_de_centre_et_réception.py", title = "Heatmap des zones de centres"))

pg = st.navigation({
    "Applications" : liste_page_app
})

pg.run()