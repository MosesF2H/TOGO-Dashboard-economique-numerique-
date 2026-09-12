"""
Page 2 — Infrastructures & Démographie
Croisement population, équipements et datacenters au Togo
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
    get_aggregates, load_datacenters, REGIONS_ORDER, normalize_name
)

# Injection CSS
inject_css()

# 1. Topbar collée au haut et au sidebar (gris #2B303A)
render_topbar("Infrastructures & Densité Démographique")

# 2. Bandeau de filtres globaux persistants avec bouton Réinitialiser
filters = render_filter_bar()

# 3. Conteneur principal avec padding
st.markdown('<div class="page-container">', unsafe_allow_html=True)

agg = get_aggregates()
pref_df = agg["pref_df"].copy()

# Filtrage
if filters["region"] != "Toutes":
    pref_df = pref_df[pref_df["region_norm"] == filters["region"]]
if filters["prefecture"] != "Toutes":
    pref_df = pref_df[pref_df["prefecture_norm"] == normalize_name(filters["prefecture"])]

dc_geo, dc_all = load_datacenters()

# ── KPIs ──────────────────────────────────
total_pop_f = int(pref_df["population"].sum())
tot_ag = int(pref_df["nb_agences"].sum())
tot_mm = int(pref_df["nb_mm"].sum())
tot_infra = tot_ag + tot_mm
ratio_hab = int(total_pop_f / max(tot_infra, 1))
n_dc = len(dc_all)

render_kpi_row([
    {"value": f"{total_pop_f:,}".replace(",", " "), "label": "Population",        "color": ""},
    {"value": f"{tot_ag:,}".replace(",", " "),       "label": "Agences Télécom",   "color": ""},
    {"value": f"{tot_mm:,}".replace(",", " "),       "label": "Agents MM",         "color": "blue"},
    {"value": f"{ratio_hab:,}".replace(",", " "),    "label": "Habitants / infra", "color": "orange"},
    {"value": str(n_dc),                             "label": "Datacenters",       "color": ""},
])

# ── Ligne 1 : Bubble chart & Top sous-dotées (un seul grand bloc) ──
st.markdown('<div class="content-card full-width-panel">', unsafe_allow_html=True)
section_title("Population vs infrastructures et sous-dotation")
col1, col2 = st.columns([3, 2], gap="medium")

with col1:
    section_title("Population vs Total Infrastructures par préfecture")

    if not pref_df.empty:
        pref_plot = pref_df.copy()
        pref_plot["total_infra"] = pref_plot["nb_agences"] + pref_plot["nb_mm"]
        fig_bubble = px.scatter(
            pref_plot,
            x="population",
            y="total_infra",
            size="population",
            color="region_norm",
            hover_name="prefecture_label",
            hover_data={
                "population": True,
                "nb_agences": True,
                "nb_mm": True,
                "region_norm": False,
            },
            labels={
                "population": "Population",
                "total_infra": "Total Infrastructures",
                "region_norm": "Région",
                "nb_agences": "Agences",
                "nb_mm": "Agents MM",
            },
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_bubble.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            font_family="Inter",
            margin=dict(l=0, r=0, t=10, b=0),
            height=340,
            legend=dict(title="", font_size=11, orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            xaxis=dict(gridcolor="#F1F5F9", title="Population"),
            yaxis=dict(gridcolor="#F1F5F9", title="Total Infrastructures"),
        )
        st.plotly_chart(fig_bubble, width="stretch", config={"scrollZoom": True, "displayModeBar": True})
    else:
        st.info("Aucune donnée disponible avec ces filtres.")

with col2:
    section_title("Top 10 préfectures les plus sous-dotées")

    if not pref_df.empty:
        worst = pref_df.nlargest(10, "ratio_hab_infra")[
            ["prefecture_label", "ratio_hab_infra", "region_norm"]
        ].copy()
        fig_worst = px.bar(
            worst,
            x="ratio_hab_infra", y="prefecture_label",
            orientation="h",
            color="region_norm",
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={"prefecture_label": "", "ratio_hab_infra": "Habitants par infra", "region_norm": "Région"},
            text="ratio_hab_infra",
        )
        fig_worst.update_traces(textposition="outside", textfont_size=10)
        fig_worst.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            font_family="Inter",
            margin=dict(l=0, r=0, t=10, b=0),
            height=340,
            showlegend=False,
            yaxis=dict(autorange="reversed", gridcolor="#F1F5F9", title=""),
            xaxis=dict(gridcolor="#F1F5F9", title="Habitants / infra"),
        )
        st.plotly_chart(fig_worst, width="stretch", config={"scrollZoom": True, "displayModeBar": True})
    else:
        st.info("Aucune donnée.")

st.markdown("</div>", unsafe_allow_html=True)

# ── Ligne 2 : Ratio MM par région + Datacenters Mapbox ──
col3, col4 = st.columns([2, 3], gap="medium")

with col3:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    section_title("Agents MM pour 10 000 hab. par région")

    # Groupby standard sécurisé sans apply déprécié
    reg_mm = (
        pref_df.groupby("region_norm", as_index=False)[["population", "nb_mm"]]
        .sum()
    )
    reg_mm["ratio_mm_10k"] = (
        reg_mm["nb_mm"] / reg_mm["population"].clip(lower=1) * 10_000
    ).round(1)
    reg_mm = reg_mm[reg_mm["region_norm"].isin(REGIONS_ORDER)]
    reg_mm["region_norm"] = pd.Categorical(reg_mm["region_norm"], categories=REGIONS_ORDER, ordered=True)
    reg_mm = reg_mm.sort_values("region_norm")

    if not reg_mm.empty:
        fig_ratio = px.bar(
            reg_mm,
            x="region_norm", y="ratio_mm_10k",
            color_discrete_sequence=["#1D4ED8"],
            labels={"region_norm": "Région", "ratio_mm_10k": "MM / 10k hab."},
            text=reg_mm["ratio_mm_10k"].apply(lambda x: f"{x:.1f}"),
        )
        fig_ratio.update_traces(textposition="outside")
        fig_ratio.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            font_family="Inter",
            margin=dict(l=0, r=0, t=10, b=0),
            height=280, showlegend=False,
            xaxis=dict(gridcolor="#F1F5F9", title=""),
            yaxis=dict(gridcolor="#F1F5F9", title=""),
        )
        st.plotly_chart(fig_ratio, width="stretch", config={"scrollZoom": True, "displayModeBar": True})

    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    section_title("Datacenters & Établissements stratégiques (Mapbox)")

    if not dc_geo.empty:
        fig_dc = px.scatter_map(
            dc_geo,
            lat="lat", lon="lon",
            hover_name="nom_label",
            hover_data={
                "lat": False, "lon": False,
                "prefecture_label": True,
                "region_norm": True,
            },
            zoom=6.1,
            center={"lat": 8.6195, "lon": 0.8248},
            map_style="carto-positron",
            color_discrete_sequence=["#DC2626"],
        )
        fig_dc.update_traces(marker=dict(size=12, opacity=0.9))
        fig_dc.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="white",
            font_family="Inter",
            height=280,
        )
        st.plotly_chart(fig_dc, width="stretch", config={"scrollZoom": True, "displayModeBar": True})
    else:
        st.info("Aucun datacenter géolocalisé.")

    st.markdown("</div>", unsafe_allow_html=True)

# ── Ligne 3 : Tableau croisé préfectures ──
st.markdown('<div class="content-card">', unsafe_allow_html=True)
section_title("Tableau de synthèse par préfecture")

disp = pref_df[[
    "prefecture_label", "region_norm", "population",
    "nb_agences", "nb_mm", "ratio_mm_10k", "ratio_hab_infra"
]].copy()
disp.columns = [
    "Préfecture", "Région", "Population",
    "Agences", "Agents MM", "MM / 10k hab.", "Hab. / infra"
]
disp["Population"] = disp["Population"].apply(lambda x: f"{x:,}".replace(",", " "))
disp = disp.sort_values("Agents MM", ascending=False)

st.dataframe(
    disp,
    width="stretch",
    hide_index=True,
    height=min(450, 42 + len(disp) * 36),
)

col_dl, _ = st.columns([1, 5])
with col_dl:
    st.download_button(
        "Télécharger CSV",
        data=pref_df.to_csv(index=False).encode("utf-8"),
        file_name="prefectures_infrastructures.csv",
        mime="text/csv",
    )

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
