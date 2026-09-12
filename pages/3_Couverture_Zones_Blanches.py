"""
Page 3 — Couverture Réseau & Zones Blanches
Diagnostic des zones blanches et score proxy d'inclusion numérique
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
    get_aggregates, load_agences, load_mobile_money, load_geojson, normalize_name
)
from utils.geo_utils import compute_priority_score, classify_zone, haversine_km, ZONE_COLORS

# Injection CSS
inject_css()

# 1. Topbar collée au haut et au sidebar (gris #2B303A)
render_topbar("Couverture Réseau & Zones Blanches - Score Proxy d'Inclusion")

# 2. Bandeau de filtres globaux persistants avec bouton Réinitialiser
filters = render_filter_bar()

# 3. Conteneur principal avec padding
st.markdown('<div class="page-container">', unsafe_allow_html=True)

agg = get_aggregates()
comm_df = agg["comm_df"].copy()

# Filtrer par région / préfecture si sélectionné
if filters["region"] != "Toutes":
    comm_df = comm_df[comm_df["region_norm"] == filters["region"]]
if filters["prefecture"] != "Toutes":
    comm_df = comm_df[comm_df["prefecture_norm"] == normalize_name(filters["prefecture"])]
if filters["commune"] != "Toutes":
    comm_df = comm_df[comm_df["commune_norm"] == normalize_name(filters["commune"])]

# Calcul du score proxy de priorité (0 à 100)
scored_df = compute_priority_score(comm_df)

n_total   = len(scored_df)
n_bien    = int((scored_df["classe_zone"] == "Bien couverte").sum())
n_surveil = int((scored_df["classe_zone"] == "Sous surveillance").sum())
n_prio    = int((scored_df["classe_zone"] == "Zone prioritaire").sum())
pop_prio  = int(scored_df[scored_df["classe_zone"] == "Zone prioritaire"]["population"].sum())

# ── KPIs ──────────────────────────────────
render_kpi_row([
    {"value": str(n_total),                                      "label": "Communes analysées",    "color": ""},
    {"value": str(n_bien),                                       "label": "Bien couvertes",         "color": ""},
    {"value": str(n_surveil),                                    "label": "Sous surveillance",      "color": "yellow"},
    {"value": str(n_prio),                                       "label": "Zones prioritaires",     "color": "red"},
    {"value": f"{pop_prio:,}".replace(",", " "),                 "label": "Population prioritaire", "color": "red"},
])

# ── Ligne 1 : Carte Mapbox Togo & Répartition par classe (un seul grand bloc) ──
st.markdown('<div class="content-card full-width-panel">', unsafe_allow_html=True)
section_title("Carte des zones blanches & statut des communes")
col_map, col_pie = st.columns([3, 2], gap="medium")

with col_map:
    section_title("Carte Mapbox — Zones prioritaires par préfecture")

    map_success = False
    try:
        geojson = load_geojson("prefectures")
        if geojson and geojson.get("features"):
            pref_scored = (
                scored_df.groupby("prefecture_norm", as_index=False)
                .agg(
                    population=("population", "sum"),
                    nb_agences=("nb_agences", "sum"),
                    nb_mm=("nb_mm", "sum"),
                    score_priorite=("score_priorite", "mean"),
                )
            )
            labels = scored_df[["prefecture_norm", "prefecture_label"]].drop_duplicates("prefecture_norm")
            pref_scored = pref_scored.merge(labels, on="prefecture_norm", how="left")
            pref_scored["prefecture_label"] = pref_scored["prefecture_label"].fillna(
                pref_scored["prefecture_norm"].str.title()
            )
            pref_scored["classe_zone"] = pref_scored["score_priorite"].apply(classify_zone)

            fig_zone = px.choropleth_map(
                pref_scored,
                geojson=geojson,
                locations="prefecture_norm",
                featureidkey="properties.name_norm",
                color="classe_zone",
                hover_name="prefecture_label",
                hover_data={
                    "prefecture_norm": False,
                    "score_priorite": ":.1f",
                    "population": True,
                    "nb_agences": True,
                    "nb_mm": True,
                },
                color_discrete_map=ZONE_COLORS,
                center={"lat": 8.6195, "lon": 0.8248},
                zoom=6.1,
                map_style="carto-positron",
                labels={"classe_zone": "Diagnostic", "score_priorite": "Score moyen"},
                category_orders={"classe_zone": ["Zone prioritaire", "Sous surveillance", "Bien couverte"]},
            )
            fig_zone.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor="white",
                font_family="Inter",
                height=360,
                legend=dict(
                    orientation="h",
                    yanchor="bottom", y=1.02,
                    xanchor="left", x=0,
                    font_size=11, title="",
                ),
            )
            st.plotly_chart(fig_zone, width="stretch", config={"scrollZoom": True, "displayModeBar": True})
            map_success = True
    except Exception:
        map_success = False

    if not map_success:
        top_prio = scored_df.nlargest(10, "score_priorite")[["commune_label", "score_priorite", "classe_zone"]]
        fig_fb = px.bar(
            top_prio, x="score_priorite", y="commune_label", orientation="h",
            color="classe_zone", color_discrete_map=ZONE_COLORS,
            labels={"score_priorite": "Score de priorité", "commune_label": "Commune"},
        )
        fig_fb.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=0, r=0, t=10, b=0), height=360,
            font_family="Inter", yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig_fb, width="stretch", config={"scrollZoom": True, "displayModeBar": True})

with col_pie:
    section_title("Répartition des communes par statut")

    zone_counts = scored_df["classe_zone"].value_counts().reset_index()
    zone_counts.columns = ["classe_zone", "count"]

    fig_donut = px.pie(
        zone_counts,
        values="count", names="classe_zone",
        color="classe_zone",
        color_discrete_map=ZONE_COLORS,
        hole=0.5,
    )
    fig_donut.update_traces(textposition="outside", textinfo="label+percent", textfont_size=11)
    fig_donut.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font_family="Inter",
        margin=dict(l=10, r=10, t=10, b=10),
        height=220, showlegend=False,
    )
    st.plotly_chart(fig_donut, width="stretch", config={"scrollZoom": True, "displayModeBar": True})

    st.markdown(f"""
    <div style="font-size: 0.82rem; color: #475569; line-height: 1.6; padding-top: 6px;">
      <b>Synthèse :</b><br>
      • <span style="color:#DC2626; font-weight:600;">{n_prio} communes</span> en zone prioritaire ({pop_prio:,} hab.)<br>
      • <span style="color:#D4AC0D; font-weight:600;">{n_surveil} communes</span> sous surveillance<br>
      • <span style="color:#118C4F; font-weight:600;">{n_bien} communes</span> bien desservies
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ── Ligne 2 : Seuil de distance & top 15 communes prioritaires ──
# Distance au point d'accès le plus proche, calculée sur les données géolocalisées du projet
# et sécurisée si certaines colonnes ne sont pas présentes dans les fichiers source.
ag_geo = load_agences().copy()
mm_geo = load_mobile_money().copy()

if not ag_geo.empty and not mm_geo.empty:
    pref_summary = scored_df[["prefecture_norm", "prefecture_label"]].drop_duplicates().copy()

    def nearest_distance_by_pref(df, infra_name):
        rows = []
        for _, row in pref_summary.iterrows():
            pref_norm = row["prefecture_norm"]
            pref_points = df[df["prefecture_norm"] == pref_norm]
            if pref_points.empty:
                rows.append({"prefecture_norm": pref_norm, "prefecture_label": row["prefecture_label"], f"distance_km_{infra_name}": 9999.0})
                continue

            n_points = pref_points[["lat", "lon"]].dropna()
            if n_points.empty:
                rows.append({"prefecture_norm": pref_norm, "prefecture_label": row["prefecture_label"], f"distance_km_{infra_name}": 9999.0})
                continue

            centroid_lat = float(n_points["lat"].mean())
            centroid_lon = float(n_points["lon"].mean())
            all_points = df[["lat", "lon"]].dropna()
            if all_points.empty:
                dist = 9999.0
            else:
                dist = float(
                    all_points.apply(
                        lambda p: haversine_km(centroid_lat, centroid_lon, float(p["lat"]), float(p["lon"])),
                        axis=1,
                    ).min()
                )
            rows.append({"prefecture_norm": pref_norm, "prefecture_label": row["prefecture_label"], f"distance_km_{infra_name}": dist})
        return pd.DataFrame(rows)

    pref_dist_ag = nearest_distance_by_pref(ag_geo, "ag")
    pref_dist_mm = nearest_distance_by_pref(mm_geo, "mm")
    dist_df = pref_summary.merge(pref_dist_ag, on=["prefecture_norm", "prefecture_label"], how="left")
    dist_df = dist_df.merge(pref_dist_mm, on=["prefecture_norm", "prefecture_label"], how="left")
    dist_df["distance_km_ag"] = dist_df["distance_km_ag"].fillna(9999.0)
    dist_df["distance_km_mm"] = dist_df["distance_km_mm"].fillna(9999.0)

    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    section_title("Distance au point d'accès le plus proche par préfecture")
    sel = st.selectbox("Type de distance", ["Agence télécom", "Agent Mobile Money"], index=0, key="dist_type")
    metric_col = "distance_km_ag" if sel == "Agence télécom" else "distance_km_mm"
    fig_dist = px.bar(
        dist_df.sort_values(metric_col, ascending=False).head(15),
        x=metric_col,
        y="prefecture_label",
        orientation="h",
        color_discrete_sequence=["#118C4F" if sel == "Agence télécom" else "#1D4ED8"],
        labels={"prefecture_label": "Préfecture", metric_col: "Distance (km)"},
        text=metric_col,
    )
    fig_dist.add_vline(x=20 if sel == "Agence télécom" else 25, line_dash="dash", line_color="#DC2626", annotation_text="Seuil")
    fig_dist.update_traces(texttemplate='%{text:.1f} km', textposition='outside')
    fig_dist.update_layout(plot_bgcolor='white', paper_bgcolor='white', margin=dict(l=0, r=0, t=10, b=0), height=320, yaxis=dict(autorange='reversed'))
    st.plotly_chart(fig_dist, width="stretch", config={"scrollZoom": True, "displayModeBar": True})
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    section_title("Dégradation de couverture à partir du seuil de distance")
    dist_long = dist_df[["prefecture_label", "distance_km_ag", "distance_km_mm"]].copy()
    dist_long = dist_long.melt(id_vars=['prefecture_label'], var_name='type', value_name='distance_km')
    dist_long['type'] = dist_long['type'].map({"distance_km_ag": "Agence télécom", "distance_km_mm": "Agent Mobile Money"})
    fig_seuil = px.box(dist_long, x='type', y='distance_km', color='type', color_discrete_map={"Agence télécom": "#118C4F", "Agent Mobile Money": "#1D4ED8"})
    fig_seuil.add_hline(y=20, line_dash='dash', line_color='#DC2626', annotation_text='Seuil 20 km')
    fig_seuil.update_layout(plot_bgcolor='white', paper_bgcolor='white', margin=dict(l=0, r=0, t=10, b=0), height=260, showlegend=False)
    st.plotly_chart(fig_seuil, width="stretch", config={"scrollZoom": True, "displayModeBar": True})
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="content-card">', unsafe_allow_html=True)
section_title("Top 15 des communes prioritaires pour l'extension du réseau")

top15 = scored_df.sort_values("score_priorite", ascending=False).head(15)[
    ["commune_label", "prefecture_label", "region_norm", "population",
     "nb_agences", "nb_mm", "ratio_mm_10k", "score_priorite", "classe_zone"]
].copy()

top15.columns = [
    "Commune", "Préfecture", "Région", "Population",
    "Agences", "Agents MM", "MM / 10k hab.", "Score (0-100)", "Statut"
]
top15["Population"] = top15["Population"].apply(lambda x: f"{x:,}".replace(",", " "))
top15["Score (0-100)"] = top15["Score (0-100)"].round(1)

st.dataframe(
    top15,
    width="stretch",
    hide_index=True,
    height=min(450, 42 + len(top15) * 35),
)

col_dl, _ = st.columns([1, 5])
with col_dl:
    st.download_button(
        "Télécharger les scores (CSV)",
        data=scored_df.to_csv(index=False).encode("utf-8"),
        file_name="zones_prioritaires_togo.csv",
        mime="text/csv",
    )

st.markdown("</div>", unsafe_allow_html=True)

# ── Méthodologie ───────────────────────────
st.markdown("""
<div class="method-box">
<b>Méthodologie du score proxy de priorité :</b>
En l'absence de données directes de signaux radio 3G/4G, le score proxy d'inclusion numérique (0 à 100) combine :
1. <b>Absence d'infrastructures physiques</b> (50 points) : 30 pts si aucune agence + 20 pts si aucun agent Mobile Money.
2. <b>Faiblesse du ratio d'inclusion financière</b> (30 points) : calculé en fonction du nombre d'agents MM pour 10 000 habitants.
3. <b>Poids démographique de la commune</b> (20 points) : priorité accordée aux bassins de population les plus peuplés non couverts.
• <b>Score ≥ 65</b> : Zone prioritaire (urgence de déploiement)
• <b>Score 35–64</b> : Zone sous surveillance (couverture fragile)
• <b>Score < 35</b> : Bien couverte (desserte satisfaisante)
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
