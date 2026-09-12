"""
streamlit_app.py — Point d'entrée principal du dashboard Togo DataLab.
Navigation multipage, sidebar stylisée avec marque officielle et onglets professionnels.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

# ─────────────────────────────────────────────
# CONFIG PAGE (premier appel Streamlit)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Togo DataLab - Dashboard Économie Numérique",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.style import inject_css, render_sidebar_brand

# Injection CSS globale (couleurs, scroll, zéro espace topbar/sidebar)
inject_css()

# ─────────────────────────────────────────────
# PAGES DU DASHBOARD (icônes professionnelles Material Symbols, aucun emoji)
# ─────────────────────────────────────────────
pages = [
    st.Page("pages/0_Vue_densemble.py",             title="Vue d'ensemble",                icon=":material/dashboard:", default=True),
    st.Page("pages/1_Mobile_Agences.py",            title="Mobile & Agences",              icon=":material/cell_tower:"),
    st.Page("pages/2_Infrastructures_Demo.py",       title="Infrastructures & Démographie", icon=":material/domain:"),
    st.Page("pages/3_Couverture_Zones_Blanches.py",  title="Couverture & Zones Blanches",   icon=":material/map:"),
    st.Page("pages/4_Recommandations.py",           title="Recommandations",               icon=":material/insights:"),
]

# Masquer la navigation par défaut de Streamlit pour un contrôle exact
pg = st.navigation(pages, position="hidden")

# ─────────────────────────────────────────────
# SIDEBAR : Emblème + Nom en haut à gauche → Titre → Onglets
# ─────────────────────────────────────────────
with st.sidebar:
    # 1. Emblème officiel suivi du nom TOGO DATA LAB dans le coin supérieur gauche
    render_sidebar_brand()

    # 2. Titre Tableau de Bord
    st.markdown('<div class="sidebar-menu-title">Tableau de Bord</div>', unsafe_allow_html=True)

    # 3. Onglets de navigation avec icônes professionnelles
    for p in pages:
        st.page_link(p, label=p.title, icon=p.icon)

# Exécution de la page sélectionnée
pg.run()
