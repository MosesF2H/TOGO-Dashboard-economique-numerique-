"""
Page 0 — Vue d'ensemble
Diagnostic Télécoms & Inclusion Numérique au Togo
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.style import inject_css, render_topbar, render_kpi_row, section_title
from utils.filters import render_filter_bar
from utils.data_loader import (
    load_agences, load_mobile_money, load_population, load_datacenters,
    load_geojson, apply_filters, REGIONS_ORDER, OPERATOR_COLORS, normalize_name
)

# Injection CSS
inject_css()

# 1. Topbar collée au haut et au sidebar (gris #2B303A)
render_topbar("Vue d'ensemble - Diagnostic Télécoms & Inclusion Numérique")

# 2. Bandeau de filtres globaux persistants avec bouton Réinitialiser
filters = render_filter_bar()

# 3. Conteneur principal avec padding
st.markdown('<div class="page-container">', unsafe_allow_html=True)

# ── Chargement et application des filtres ──
df_ag_all = load_agences()
df_mm_all = load_mobile_money()
df_pop_all = load_population()
dc_geo_all, dc_all = load_datacenters()

df_ag = apply_filters(df_ag_all, filters)
df_mm = apply_filters(df_mm_all, filters)

# Population filtrée
df_pop = df_pop_all.copy()
if filters["region"] != "Toutes":
    df_pop = df_pop[df_pop["region_norm"] == filters["region"]]
if filters["prefecture"] != "Toutes":
    df_pop = df_pop[df_pop["prefecture_norm"] == normalize_name(filters["prefecture"])]
if filters["commune"] != "Toutes":
    df_pop = df_pop[df_pop["commune_norm"] == normalize_name(filters["commune"])]

total_agences = len(df_ag)
total_mm = len(df_mm)
total_dc = len(dc_all)
total_pop = int(df_pop["population"].sum())

# Communes couvertes
comm_ag = set(df_ag["commune_norm"].dropna().unique())
comm_mm = set(df_mm["commune_norm"].dropna().unique())
comm_couvertes = comm_ag.union(comm_mm)
total_communes = max(df_pop["commune_norm"].nunique(), 1)
pct_couv = min(100.0, len(comm_couvertes) / total_communes * 100)

# ── KPIs Globaux ───────────────────────────
render_kpi_row([
    {"value": f"{total_agences:,}".replace(",", " "), "label": "Agences Télécom",     "color": ""},
    {"value": f"{total_mm:,}".replace(",", " "),      "label": "Agents Mobile Money", "color": "blue"},
    {"value": str(total_dc),                           "label": "Datacenters",          "color": "orange"},
    {"value": f"{total_pop:,}".replace(",", " "),     "label": "Population",           "color": ""},
    {"value": f"{pct_couv:.0f}%",                     "label": "Communes couvertes",   "color": ""},
])

# ── Ligne 1 : Agences & Mobile Money par Région (un seul grand bloc) ──
# Données régionales / préfectorales dynamiques
if filters["region"] == "Toutes":
    ag_group = df_ag.groupby("region_norm").size().reindex(REGIONS_ORDER, fill_value=0).reset_index()
    ag_group.columns = ["label", "value"]
    ag_group["group"] = "Région"
    mm_group = df_mm.groupby("region_norm").size().reindex(REGIONS_ORDER, fill_value=0).reset_index()
    mm_group.columns = ["label", "value"]
    mm_group["group"] = "Région"
else:
    ag_group = df_ag.groupby("prefecture_label").size().reset_index(name="value")
    ag_group.columns = ["label", "value"]
    ag_group["group"] = "Préfecture"
    mm_group = df_mm.groupby("prefecture_label").size().reset_index(name="value")
    mm_group.columns = ["label", "value"]
    mm_group["group"] = "Préfecture"

st.markdown('<div class="content-card full-width-panel">', unsafe_allow_html=True)
section_title("Agences Télécom & Agents Mobile Money")
col1, col2 = st.columns(2, gap="medium")

with col1:
    section_title("Agences Télécom par région") if filters["region"] == "Toutes" else section_title(f"Agences Télécom par préfecture — {filters['region']}")

    fig1 = px.bar(
        ag_group,
        x="label", y="value",
        color_discrete_sequence=["#118C4F"],
        labels={"label": "Région" if filters["region"] == "Toutes" else "Préfecture", "value": "Agences"},
        text="value",
    )
    fig1.update_traces(textposition="outside", textfont_size=11)
    fig1.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font_family="Inter", margin=dict(l=0, r=0, t=10, b=0),
        showlegend=False, height=270,
        xaxis=dict(gridcolor="#F1F5F9", title=""),
        yaxis=dict(gridcolor="#F1F5F9", title=""),
    )
    st.plotly_chart(fig1, width="stretch", config={"scrollZoom": True, "displayModeBar": True})

with col2:
    section_title("Agents Mobile Money par région") if filters["region"] == "Toutes" else section_title(f"Agents Mobile Money par préfecture — {filters['region']}")

    fig2 = px.bar(
        mm_group,
        x="label", y="value",
        color_discrete_sequence=["#1D4ED8"],
        labels={"label": "Région" if filters["region"] == "Toutes" else "Préfecture", "value": "Agents MM"},
        text="value",
    )
    fig2.update_traces(textposition="outside", textfont_size=11)
    fig2.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font_family="Inter", margin=dict(l=0, r=0, t=10, b=0),
        showlegend=False, height=270,
        xaxis=dict(gridcolor="#F1F5F9", title=""),
        yaxis=dict(gridcolor="#F1F5F9", title=""),
    )
    st.plotly_chart(fig2, width="stretch", config={"scrollZoom": True, "displayModeBar": True})

st.markdown("</div>", unsafe_allow_html=True)

# ── Ligne 2 : Carte Mapbox Togo + Répartition Opérateurs ──
col3, col4 = st.columns([3, 2], gap="medium")

with col3:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    section_title("Carte Mapbox Togo — Répartition des infrastructures")

    # Agrégation par préfecture pour la carte
    pref_pop = df_pop_all.groupby(["prefecture_norm", "prefecture_label", "region_norm"])["population"].sum().reset_index()
    pref_ag = df_ag.groupby("prefecture_norm").size().reset_index(name="nb_agences")
    pref_mm = df_mm.groupby("prefecture_norm").size().reset_index(name="nb_mm")

    pref_map = pref_pop.merge(pref_ag, on="prefecture_norm", how="left")
    pref_map = pref_map.merge(pref_mm, on="prefecture_norm", how="left")
    pref_map["nb_agences"] = pref_map["nb_agences"].fillna(0).astype(int)
    pref_map["nb_mm"] = pref_map["nb_mm"].fillna(0).astype(int)
    pref_map["total_infra"] = pref_map["nb_agences"] + pref_map["nb_mm"]

    # Choroplèthe des préfectures centrée sur le Togo (fond de carte libre, sans clé API)
    map_rendered = False
    try:
        geojson = load_geojson("prefectures")
        if geojson and geojson.get("features"):
            fig_map = px.choropleth_map(
                pref_map,
                geojson=geojson,
                locations="prefecture_norm",
                featureidkey="properties.name_norm",
                color="total_infra",
                hover_name="prefecture_label",
                hover_data={"prefecture_norm": False, "total_infra": True, "nb_agences": True, "nb_mm": True, "population": True},
                color_continuous_scale=[[0, "#E8F5EE"], [0.4, "#34D399"], [1, "#118C4F"]],
                center={"lat": 8.6195, "lon": 0.8248},
                zoom=6.1,
                map_style="carto-positron",
                labels={"total_infra": "Total Infras", "nb_agences": "Agences", "nb_mm": "Agents MM", "population": "Population"},
            )
            fig_map.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor="white",
                font_family="Inter",
                height=350,
                coloraxis_colorbar=dict(
                    title="Infras",
                    thickness=12,
                    len=0.7,
                ),
            )
            st.plotly_chart(fig_map, width="stretch", config={"scrollZoom": True, "displayModeBar": True})
            map_rendered = True
    except Exception:
        map_rendered = False

    # Repli en carte de points si la couche préfectures est indisponible
    if not map_rendered:
        ag_geo = df_ag.dropna(subset=["lat", "lon"])
        if not ag_geo.empty:
            fig_scat = px.scatter_map(
                ag_geo.head(1000),
                lat="lat", lon="lon",
                color="operateur_norm",
                color_discrete_map=OPERATOR_COLORS,
                hover_name="nom_label",
                center={"lat": 8.6195, "lon": 0.8248},
                zoom=6.1,
                map_style="carto-positron",
                height=350,
            )
            fig_scat.update_layout(margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig_scat, width="stretch", config={"scrollZoom": True, "displayModeBar": True})
        else:
            st.info("Données cartographiques non disponibles avec ces filtres.")

    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    section_title("Agences par opérateur")

    ag_op = df_ag.groupby("operateur_norm").size().reset_index(name="count")
    if not ag_op.empty:
        fig_pie1 = px.pie(
            ag_op, values="count", names="operateur_norm",
            color="operateur_norm",
            color_discrete_map=OPERATOR_COLORS,
            hole=0.45,
        )
        fig_pie1.update_traces(textposition="outside", textinfo="label+percent", textfont_size=10)
        fig_pie1.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            font_family="Inter",
            margin=dict(l=10, r=10, t=10, b=10),
            height=160,
            showlegend=False,
        )
        st.plotly_chart(fig_pie1, width="stretch", config={"scrollZoom": True, "displayModeBar": True})

    section_title("Agents MM par opérateur")
    mm_op = df_mm.groupby("operateur_norm").size().reset_index(name="count")
    if not mm_op.empty:
        fig_pie2 = px.pie(
            mm_op, values="count", names="operateur_norm",
            color="operateur_norm",
            color_discrete_map=OPERATOR_COLORS,
            hole=0.45,
        )
        fig_pie2.update_traces(textposition="outside", textinfo="label+percent", textfont_size=10)
        fig_pie2.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            font_family="Inter",
            margin=dict(l=10, r=10, t=10, b=10),
            height=160,
            showlegend=False,
        )
        st.plotly_chart(fig_pie2, width="stretch", config={"scrollZoom": True, "displayModeBar": True})

    st.markdown("</div>", unsafe_allow_html=True)

# ── Ligne 3 : Évolution temporelle ─────────
ag_year = (
    df_ag.dropna(subset=["annee_creation"])
    .groupby("annee_creation")
    .size()
    .reset_index(name="count")
)
if not ag_year.empty:
    ag_year["annee_creation"] = ag_year["annee_creation"].astype(int)
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    section_title("Évolution annuelle de création des agences")

    fig_year = px.bar(
        ag_year.sort_values("annee_creation"),
        x="annee_creation", y="count",
        color_discrete_sequence=["#118C4F"],
        labels={"annee_creation": "Année", "count": "Agences créées"},
        text="count",
    )
    fig_year.update_traces(textposition="outside", textfont_size=10)
    fig_year.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font_family="Inter",
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=False, height=220,
        xaxis=dict(gridcolor="#F1F5F9", type="category", title=""),
        yaxis=dict(gridcolor="#F1F5F9", title=""),
    )
    st.plotly_chart(fig_year, width="stretch", config={"scrollZoom": True, "displayModeBar": True})
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
