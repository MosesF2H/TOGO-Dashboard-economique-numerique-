"""
utils/filters.py
Barre de filtres globaux persistants (session_state) sous le topbar.
Cascade : Région → Préfecture → Commune → Opérateur → Type d'infra
Bouton Réinitialiser avec callback sécurisé.
"""

import streamlit as st
from utils.data_loader import get_filter_options, normalize_name


def _on_region_change():
    """Réinitialise la préfecture et commune quand la région change."""
    st.session_state["f_prefecture"] = "Toutes"
    st.session_state["f_commune"] = "Toutes"


def _on_prefecture_change():
    """Réinitialise la commune quand la préfecture change."""
    st.session_state["f_commune"] = "Toutes"


def _on_reset():
    """Réinitialise tous les filtres globaux sans erreur de widget."""
    st.session_state["f_region"] = "Toutes"
    st.session_state["f_prefecture"] = "Toutes"
    st.session_state["f_commune"] = "Toutes"
    st.session_state["f_operateur"] = "Tous"
    st.session_state["f_type_infra"] = "Tous"


def render_filter_bar() -> dict:
    """
    Affiche la rangée de filtres globaux sous le topbar avec le bouton Réinitialiser.
    Retourne le dictionnaire des filtres actifs.
    """
    # Initialisation session_state
    if "f_region" not in st.session_state:
        st.session_state["f_region"] = "Toutes"
    if "f_prefecture" not in st.session_state:
        st.session_state["f_prefecture"] = "Toutes"
    if "f_commune" not in st.session_state:
        st.session_state["f_commune"] = "Toutes"
    if "f_operateur" not in st.session_state:
        st.session_state["f_operateur"] = "Tous"
    if "f_type_infra" not in st.session_state:
        st.session_state["f_type_infra"] = "Tous"

    opts = get_filter_options()

    # 1. Région
    region_choices = ["Toutes"] + opts["regions"]
    current_reg = st.session_state.get("f_region", "Toutes")
    if current_reg not in region_choices:
        current_reg = "Toutes"
        st.session_state["f_region"] = "Toutes"

    # 2. Préfecture (cascade)
    if current_reg != "Toutes":
        pref_choices = ["Toutes"] + opts["reg_to_pref"].get(current_reg, [])
    else:
        all_prefs = []
        for prefs in opts["reg_to_pref"].values():
            all_prefs.extend(prefs)
        pref_choices = ["Toutes"] + sorted(set(all_prefs))

    current_pref = st.session_state.get("f_prefecture", "Toutes")
    if current_pref not in pref_choices:
        current_pref = "Toutes"
        st.session_state["f_prefecture"] = "Toutes"

    # 3. Commune (cascade)
    if current_pref != "Toutes":
        pref_norm = normalize_name(current_pref)
        comm_choices = ["Toutes"] + opts["pref_to_comm"].get(pref_norm, [])
    elif current_reg != "Toutes":
        comm_choices = ["Toutes"] + opts["reg_to_comm"].get(current_reg, [])
    else:
        all_comms = []
        for comms in opts.get("reg_to_comm", {}).values():
            all_comms.extend(comms)
        comm_choices = ["Toutes"] + sorted(set(all_comms))

    current_comm = st.session_state.get("f_commune", "Toutes")
    if current_comm not in comm_choices:
        current_comm = "Toutes"
        st.session_state["f_commune"] = "Toutes"

    # 4. Opérateur & 5. Type Infra
    # Valeurs alignées sur celles réellement produites par _normalize_operator
    # (data_loader.py) : "Telecom" n'existe pas après normalisation, le
    # filtre ne retournait donc jamais aucune ligne avec ce choix.
    op_choices = ["Tous", "Togocom", "Moov", "Mixte", "Inconnu"]
    current_op = st.session_state.get("f_operateur", "Tous")
    if current_op not in op_choices:
        current_op = "Tous"
        st.session_state["f_operateur"] = "Tous"

    infra_choices = ["Tous", "Agences", "Datacenters", "Mobile Money"]
    current_infra = st.session_state.get("f_type_infra", "Tous")
    if current_infra not in infra_choices:
        current_infra = "Tous"
        st.session_state["f_type_infra"] = "Tous"

    # Conteneur HTML stylisé sous le topbar
    st.markdown('<div class="filter-strip">', unsafe_allow_html=True)
    col1, col2, col3, col4, col5, col6 = st.columns([1.15, 1.15, 1.15, 1.0, 1.05, 0.75], gap="small")

    with col1:
        st.selectbox(
            "Région",
            region_choices,
            key="f_region",
            on_change=_on_region_change,
        )
    with col2:
        st.selectbox(
            "Préfecture",
            pref_choices,
            key="f_prefecture",
            on_change=_on_prefecture_change,
        )
    with col3:
        st.selectbox(
            "Commune",
            comm_choices,
            key="f_commune",
        )
    with col4:
        st.selectbox(
            "Opérateur",
            op_choices,
            key="f_operateur",
        )
    with col5:
        st.selectbox(
            "Type d'infra",
            infra_choices,
            key="f_type_infra",
        )
    with col6:
        st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
        st.button(
            "Réinitialiser",
            key="btn_reset_filters",
            on_click=_on_reset,
            use_container_width=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)

    return get_active_filters()


def get_active_filters() -> dict:
    """Lit les filtres depuis st.session_state."""
    return {
        "region":     st.session_state.get("f_region",     "Toutes"),
        "prefecture": st.session_state.get("f_prefecture", "Toutes"),
        "commune":    st.session_state.get("f_commune",    "Toutes"),
        "operateur":  st.session_state.get("f_operateur",  "Tous"),
        "type_infra": st.session_state.get("f_type_infra", "Tous"),
    }
