"""
Page 1 — Mobile & Agences Télécom
Cartographie et Réseaux de Distribution au Togo
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px

from utils.style import inject_css, render_topbar, render_kpi_row, section_title
from utils.filters import render_filter_bar
from utils.data_loader import (
    load_agences, load_mobile_money, apply_filters, OPERATOR_COLORS
)

# Injection CSS
inject_css()

# 1. Topbar collée au haut et au sidebar (gris #2B303A)
render_topbar("Mobile & Agences Télécom - Cartographie et Réseaux de Distribution")

# 2. Bandeau de filtres globaux persistants avec bouton Réinitialiser
filters = render_filter_bar()

# 3. Conteneur principal avec padding
st.markdown('<div class="page-container">', unsafe_allow_html=True)

# Données filtrées
df_ag_all = load_agences()
df_mm_all = load_mobile_money()

df_ag = apply_filters(df_ag_all, filters)
df_mm = apply_filters(df_mm_all, filters)

# ── KPIs ──────────────────────────────────
n_ag = len(df_ag)
n_mm = len(df_mm)
pref_ag = df_ag["prefecture_norm"].nunique()
pref_mm = df_mm["prefecture_norm"].nunique()

render_kpi_row([
    {"value": f"{n_ag:,}".replace(",", " "),  "label": "Agences Télécom",         "color": ""},
    {"value": f"{n_mm:,}".replace(",", " "),  "label": "Agents Mobile Money",     "color": "blue"},
    {"value": str(pref_ag),                   "label": "Préfectures avec agences", "color": ""},
    {"value": str(pref_mm),                   "label": "Préfectures avec MM",      "color": "blue"},
])

# ── Ligne 1 : Cartes Mapbox Togo (un seul grand bloc) ──────────
st.markdown('<div class="content-card full-width-panel">', unsafe_allow_html=True)
section_title("Localisation des infrastructures télécom")
col_map1, col_map2 = st.columns(2, gap="medium")

with col_map1:
    section_title("Localisation des agences télécom")

    ag_geo = df_ag.dropna(subset=["lat", "lon"])
    if not ag_geo.empty:
        fig_ag = px.scatter_map(
            ag_geo.head(2000),
            lat="lat", lon="lon",
            color="operateur_norm",
            color_discrete_map=OPERATOR_COLORS,
            hover_name="nom_label",
            hover_data={
                "lat": False, "lon": False,
                "operateur_norm": True,
                "prefecture_label": True,
                "region_norm": True
            },
            zoom=6.1,
            center={"lat": 8.6195, "lon": 0.8248},
            map_style="carto-positron",
            labels={"operateur_norm": "Opérateur"},
        )
        fig_ag.update_traces(marker=dict(size=8, opacity=0.85))
        fig_ag.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="white",
            font_family="Inter",
            height=360,
            legend=dict(
                orientation="h",
                yanchor="bottom", y=1.02,
                xanchor="left", x=0,
                font_size=11,
                title="",
            ),
        )
        st.plotly_chart(fig_ag, width="stretch", config={"scrollZoom": True, "displayModeBar": True})
    else:
        st.info("Aucune agence géolocalisée avec ces filtres.")

with col_map2:
    section_title("Localisation des agents Mobile Money")

    mm_geo = df_mm.dropna(subset=["lat", "lon"])
    if not mm_geo.empty:
        fig_mm = px.scatter_map(
            mm_geo.sample(min(2500, len(mm_geo)), random_state=42),
            lat="lat", lon="lon",
            color="operateur_norm",
            color_discrete_map=OPERATOR_COLORS,
            hover_name="nom_label",
            hover_data={
                "lat": False, "lon": False,
                "operateur_norm": True,
                "prefecture_label": True,
                "region_norm": True
            },
            zoom=6.1,
            center={"lat": 8.6195, "lon": 0.8248},
            map_style="carto-positron",
            labels={"operateur_norm": "Opérateur"},
        )
        fig_mm.update_traces(marker=dict(size=5, opacity=0.7))
        fig_mm.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="white",
            font_family="Inter",
            height=360,
            legend=dict(
                orientation="h",
                yanchor="bottom", y=1.02,
                xanchor="left", x=0,
                font_size=11,
                title="",
            ),
        )
        st.plotly_chart(fig_mm, width="stretch", config={"scrollZoom": True, "displayModeBar": True})
    else:
        st.info("Aucun agent Mobile Money géolocalisé avec ces filtres.")

st.markdown("</div>", unsafe_allow_html=True)

# ── Ligne 2 : Analyse par opérateur & Top Préfectures ──
col_c1, col_c2 = st.columns(2, gap="medium")

with col_c1:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    if filters["prefecture"] == "Toutes":
        section_title("Répartition des agents MM par opérateur")
        mm_op = df_mm.groupby("operateur_norm").size().reset_index(name="nb_mm")
        if not mm_op.empty:
            fig_mm_op = px.bar(
                mm_op,
                x="nb_mm", y="operateur_norm",
                orientation="h",
                color="operateur_norm",
                color_discrete_map=OPERATOR_COLORS,
                labels={"nb_mm": "Agents MM", "operateur_norm": "Opérateur"},
                text="nb_mm",
            )
            fig_mm_op.update_traces(textposition="outside", textfont_size=10)
            fig_mm_op.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                font_family="Inter",
                margin=dict(l=0, r=0, t=10, b=0),
                height=250, showlegend=False,
                xaxis=dict(gridcolor="#F1F5F9", title=""),
                yaxis=dict(gridcolor="#F1F5F9", title=""),
            )
            st.plotly_chart(fig_mm_op, width="stretch", config={"scrollZoom": True, "displayModeBar": True})
    else:
        section_title(f"Agents MM par commune — {filters['prefecture']}")
        pref_comm = (
            df_mm[df_mm["prefecture_norm"] == filters["prefecture"].lower().replace(" ", " ")]
            if "prefecture_norm" in df_mm.columns and filters["prefecture"] != "Toutes"
            else df_mm
        )
        if filters["prefecture"] != "Toutes":
            pref_norm = df_mm["prefecture_norm"].str.normalize('NFKD').str.encode('ascii', 'ignore').str.decode('ascii').str.lower().str.replace(' ', ' ')
            selected = pref_norm == filters["prefecture"].lower().replace(' ', ' ')
            pref_comm = df_mm[selected]
        if pref_comm.empty:
            st.info("Aucune donnée disponible pour cette préfecture.")
        else:
            comm_counts = pref_comm.groupby("commune_label").size().reset_index(name="nb_mm").sort_values("nb_mm", ascending=False)
            fig_comm = px.bar(
                comm_counts,
                x="nb_mm", y="commune_label",
                orientation="h",
                color_discrete_sequence=["#1D4ED8"],
                labels={"nb_mm": "Agents MM", "commune_label": "Commune"},
                text="nb_mm",
            )
            fig_comm.update_traces(textposition="outside", textfont_size=10)
            fig_comm.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                font_family="Inter",
                margin=dict(l=0, r=0, t=10, b=0),
                height=250, showlegend=False,
                yaxis=dict(autorange="reversed", gridcolor="#F1F5F9", title=""),
                xaxis=dict(gridcolor="#F1F5F9", title=""),
            )
            st.plotly_chart(fig_comm, width="stretch", config={"scrollZoom": True, "displayModeBar": True})
    st.markdown("</div>", unsafe_allow_html=True)

with col_c2:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    section_title("Top 10 préfectures — Nombre d'agents MM")

    top_mm = (
        df_mm.groupby("prefecture_label")
        .size()
        .reset_index(name="nb_mm")
        .nlargest(10, "nb_mm")
    )
    if not top_mm.empty:
        fig_top_mm = px.bar(
            top_mm,
            x="nb_mm", y="prefecture_label",
            orientation="h",
            color_discrete_sequence=["#1D4ED8"],
            labels={"nb_mm": "Agents MM", "prefecture_label": "Préfecture"},
            text="nb_mm",
        )
        fig_top_mm.update_traces(textposition="outside", textfont_size=10)
        fig_top_mm.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            font_family="Inter",
            margin=dict(l=0, r=0, t=10, b=0),
            height=250, showlegend=False,
            yaxis=dict(autorange="reversed", gridcolor="#F1F5F9", title=""),
            xaxis=dict(gridcolor="#F1F5F9", title=""),
        )
        st.plotly_chart(fig_top_mm, width="stretch", config={"scrollZoom": True, "displayModeBar": True})
    st.markdown("</div>", unsafe_allow_html=True)

# ── Ligne 3 : Tableau de données ──────────
st.markdown('<div class="content-card">', unsafe_allow_html=True)
section_title("Explorateur des données filtrées")

tab_choice = st.radio("Afficher :", ["Agences Télécom", "Agents Mobile Money"], horizontal=True)

if tab_choice == "Agences Télécom":
    disp_cols = [c for c in ["nom_label", "operateur_norm", "region_norm", "prefecture_label", "commune_label", "statut_norm", "annee_creation"] if c in df_ag.columns]
    st.dataframe(df_ag[disp_cols].head(500), width="stretch", hide_index=True)
    st.download_button(
        "Télécharger Agences CSV",
        data=df_ag[disp_cols].to_csv(index=False).encode("utf-8"),
        file_name="agences_filtrees.csv",
        mime="text/csv",
    )
else:
    disp_cols = [c for c in ["nom_label", "operateur_norm", "region_norm", "prefecture_label", "commune_label", "statut_norm"] if c in df_mm.columns]
    st.dataframe(df_mm[disp_cols].head(500), width="stretch", hide_index=True)
    st.download_button(
        "Télécharger Mobile Money CSV",
        data=df_mm[disp_cols].to_csv(index=False).encode("utf-8"),
        file_name="mobile_money_filtre.csv",
        mime="text/csv",
    )

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
