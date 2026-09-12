"""
utils/charts.py
Fonctions Plotly réutilisables pour tous les graphiques.
Cartes centrées sur le Togo uniquement (fond blanc + shapefile GADM).
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ─────────────────────────────────────────────
# CONSTANTES CARTE TOGO
# ─────────────────────────────────────────────

TOGO_CENTER = dict(lat=8.7, lon=1.0)
TOGO_ZOOM = 6.2

PLOTLY_LAYOUT = dict(
    font_family="Inter, sans-serif",
    paper_bgcolor="white",
    plot_bgcolor="white",
    margin=dict(l=0, r=0, t=36, b=0),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font_size=11,
    ),
)

REGION_COLORS = {
    "Maritime": "#118C4F",
    "Plateaux": "#3498DB",
    "Centrale": "#9B59B6",
    "Kara":     "#E67E22",
    "Savanes":  "#E74C3C",
    "Inconnu":  "#95A5A6",
}

OP_COLORS = {
    "Togocom": "#118C4F",
    "Moov":    "#F5CE37",
    "Mixte":   "#3498DB",
    "Inconnu": "#95A5A6",
}

ZONE_COLORS = {
    "Bien desservie":    "#10B981",
    "Zone à surveiller": "#F59E0B",
    "Zone prioritaire":  "#EF4444",
}


def _apply_layout(fig, title: str = "", height: int = 360) -> go.Figure:
    """Applique le layout standard Plotly."""
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(
            text=title,
            font=dict(size=13, family="DM Sans, sans-serif", color="#0F172A"),
            x=0,
            xanchor="left",
            pad=dict(l=4),
        ) if title else None,
        height=height,
    )
    return fig


# ─────────────────────────────────────────────
# BARRES HORIZONTALES
# ─────────────────────────────────────────────

def bar_agences_by_region(ag_region: pd.DataFrame, highlight: str = None) -> go.Figure:
    """Barres horizontales : agences par région."""
    df = ag_region.copy()
    df = df[df["region"].notna()].sort_values("nb_agences", ascending=True)
    colors = [
        "#2ECC71" if (highlight and row["region"] == highlight) else REGION_COLORS.get(row["region"], "#118C4F")
        for _, row in df.iterrows()
    ]
    fig = go.Figure(go.Bar(
        x=df["nb_agences"],
        y=df["region"],
        orientation="h",
        marker_color=colors,
        text=df["nb_agences"],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Agences : %{x}<extra></extra>",
    ))
    _apply_layout(fig, "Agences télécom par région", height=300)
    fig.update_xaxes(showgrid=True, gridcolor="#F1F5F9", title_text="")
    fig.update_yaxes(title_text="")
    return fig


def bar_population_by_region(pop_region: pd.DataFrame) -> go.Figure:
    """Barres horizontales : population par région."""
    df = pop_region.copy()
    df = df[df["region"].notna()].sort_values("population", ascending=True)
    fig = go.Figure(go.Bar(
        x=df["population"],
        y=df["region"],
        orientation="h",
        marker_color=[REGION_COLORS.get(r, "#3498DB") for r in df["region"]],
        text=df["population"].apply(lambda x: f"{x:,.0f}".replace(",", " ")),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Population : %{x:,.0f}<extra></extra>",
    ))
    _apply_layout(fig, "Population par région (RGPH-5)", height=300)
    fig.update_xaxes(showgrid=True, gridcolor="#F1F5F9", title_text="")
    fig.update_yaxes(title_text="")
    return fig


def bar_agences_by_prefecture(ag_pref: pd.DataFrame, region_filter: str = None, top_n: int = 15) -> go.Figure:
    """Barres par préfecture (top N)."""
    df = ag_pref.copy()
    if region_filter and region_filter != "Toutes":
        df = df[df["region_norm"] == region_filter]
    df = df.nlargest(top_n, "nb_agences").sort_values("nb_agences", ascending=True)
    fig = go.Figure(go.Bar(
        x=df["nb_agences"],
        y=df["prefecture_label"],
        orientation="h",
        marker_color="#118C4F",
        text=df["nb_agences"],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Agences : %{x}<extra></extra>",
    ))
    _apply_layout(fig, f"Top {top_n} préfectures — Agences télécom", height=max(300, top_n * 24))
    return fig


# ─────────────────────────────────────────────
# CAMEMBERT / ANNEAU
# ─────────────────────────────────────────────

def donut_mm_by_operator(mm_op: pd.DataFrame) -> go.Figure:
    """Anneau : répartition MM par opérateur."""
    df = mm_op[mm_op["count"] > 0].copy()
    colors = [OP_COLORS.get(op, "#95A5A6") for op in df["operateur"]]
    fig = go.Figure(go.Pie(
        labels=df["operateur"],
        values=df["count"],
        hole=0.55,
        marker_colors=colors,
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>Agents : %{value:,}<br>Part : %{percent}<extra></extra>",
    ))
    _apply_layout(fig, "Agents Mobile Money par opérateur", height=300)
    fig.update_layout(showlegend=False)
    return fig


def donut_agences_by_operator(ag_op: pd.DataFrame) -> go.Figure:
    """Anneau : répartition agences par opérateur."""
    df = ag_op[ag_op["count"] > 0].copy()
    colors = [OP_COLORS.get(op, "#95A5A6") for op in df["operateur"]]
    fig = go.Figure(go.Pie(
        labels=df["operateur"],
        values=df["count"],
        hole=0.55,
        marker_colors=colors,
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>Agences : %{value:,}<br>Part : %{percent}<extra></extra>",
    ))
    _apply_layout(fig, "Agences télécom par opérateur", height=300)
    fig.update_layout(showlegend=False)
    return fig


# ─────────────────────────────────────────────
# ÉVOLUTION TEMPORELLE
# ─────────────────────────────────────────────

def line_agences_evolution(ag_year: pd.DataFrame) -> go.Figure:
    """Ligne : évolution du nombre d'agences créées par an."""
    df = ag_year.sort_values("annee_creation")
    df["cumul"] = df["count"].cumsum()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["annee_creation"],
        y=df["count"],
        name="Nouvelles agences",
        marker_color="#118C4F",
        opacity=0.7,
        hovertemplate="%{x} : %{y} agences<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["annee_creation"],
        y=df["cumul"],
        name="Cumul",
        line=dict(color="#F5CE37", width=2.5),
        yaxis="y2",
        hovertemplate="Cumul %{x} : %{y}<extra></extra>",
    ))
    _apply_layout(fig, "Évolution du déploiement des agences", height=300)
    fig.update_layout(
        yaxis2=dict(overlaying="y", side="right", showgrid=False),
        barmode="overlay",
    )
    return fig


# ─────────────────────────────────────────────
# SCATTER
# ─────────────────────────────────────────────

def scatter_mm_vs_population(pref_df: pd.DataFrame) -> go.Figure:
    """
    Scatter : X = population préfecture, Y = nb agents MM.
    Droite de tendance. Points rouges = sous la tendance.
    """
    df = pref_df.dropna(subset=["population", "nb_mm"]).copy()
    if len(df) < 3:
        fig = go.Figure()
        _apply_layout(fig, "Données insuffisantes", 300)
        return fig

    # Régression
    coeffs = np.polyfit(np.log1p(df["population"]), df["nb_mm"], 1)
    df["predicted"] = np.polyval(coeffs, np.log1p(df["population"]))
    df["sous_tendance"] = df["nb_mm"] < df["predicted"]

    colors = ["#EF4444" if s else "#118C4F" for s in df["sous_tendance"]]

    fig = go.Figure()
    # Points
    fig.add_trace(go.Scatter(
        x=df["population"],
        y=df["nb_mm"],
        mode="markers+text",
        text=df["prefecture_label"],
        textposition="top center",
        textfont=dict(size=9, color="#64748B"),
        marker=dict(color=colors, size=9, line=dict(color="white", width=1)),
        hovertemplate="<b>%{text}</b><br>Pop : %{x:,}<br>Agents MM : %{y}<extra></extra>",
        name="Préfectures",
    ))
    # Droite de tendance
    x_range = np.linspace(df["population"].min(), df["population"].max(), 100)
    y_range = np.polyval(coeffs, np.log1p(x_range))
    fig.add_trace(go.Scatter(
        x=x_range, y=y_range,
        mode="lines",
        line=dict(color="#F5CE37", width=2, dash="dash"),
        name="Tendance nationale",
        hoverinfo="skip",
    ))

    _apply_layout(fig, "Population vs. Agents Mobile Money (par préfecture)", height=380)
    fig.add_annotation(
        text="🔴 Sous la tendance = sous-dotées",
        xref="paper", yref="paper", x=0.01, y=0.98,
        showarrow=False, font=dict(size=10, color="#EF4444"), bgcolor="white",
    )
    fig.update_xaxes(title_text="Population", showgrid=True, gridcolor="#F1F5F9")
    fig.update_yaxes(title_text="Agents MM", showgrid=True, gridcolor="#F1F5F9")
    return fig


# ─────────────────────────────────────────────
# CARTES TOGO (Plotly map — fond blanc ou clair)
# ─────────────────────────────────────────────

def map_choropleth_prefectures(
    geojson: dict,
    df: pd.DataFrame,
    value_col: str,
    id_col: str = "prefecture_norm",
    title: str = "",
    colorscale: str = "Greens",
    hover_data: dict = None,
    height: int = 520,
    zoom: float = TOGO_ZOOM,
) -> go.Figure:
    """
    Choroplèthe des préfectures du Togo.
    Fond blanc (white-bg) — seul le Togo est visible.
    """
    if df.empty or not geojson.get("features"):
        fig = go.Figure()
        fig.add_annotation(text="Données insuffisantes pour la carte", x=0.5, y=0.5, showarrow=False)
        _apply_layout(fig, title, height)
        return fig

    hover_cols = list(hover_data.keys()) if hover_data else []

    fig = px.choropleth_map(
        df,
        geojson=geojson,
        locations=id_col,
        featureidkey="properties.name_norm",
        color=value_col,
        color_continuous_scale=colorscale,
        center=TOGO_CENTER,
        zoom=zoom,
        map_style="white-bg",
        hover_name=df.columns[0] if len(df.columns) > 0 else id_col,
        hover_data=hover_data or {},
        opacity=0.85,
    )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=height,
        title=dict(text=title, font=dict(size=13, family="DM Sans, sans-serif")),
        coloraxis_colorbar=dict(
            len=0.5, thickness=12, tickfont=dict(size=10),
            title=dict(font=dict(size=10)),
        ),
        map=dict(style="white-bg", center=TOGO_CENTER, zoom=zoom),
    )
    return fig


def map_points(
    df_points: pd.DataFrame,
    color_col: str = "type_infra",
    color_map: dict = None,
    title: str = "",
    size: int = 8,
    height: int = 520,
    geojson_outline: dict = None,
) -> go.Figure:
    """
    Carte de points GPS sur fond blanc du Togo.
    """
    if df_points.empty:
        fig = go.Figure()
        _apply_layout(fig, title, height)
        return fig

    cmap = color_map or {
        "Agences": "#118C4F",
        "Mobile Money": "#F5CE37",
        "Datacenters": "#3498DB",
    }

    fig = go.Figure()

    # Ajouter contour Togo si fourni
    if geojson_outline:
        fig.add_trace(go.Scattermap(
            lon=[], lat=[], mode="lines",
            line=dict(color="#334155", width=1),
            hoverinfo="skip", showlegend=False,
        ))

    for cat, group in df_points.groupby(color_col):
        hover_name = group.get("nom_label", group.get("operateur_norm", pd.Series([""] * len(group))))
        fig.add_trace(go.Scattermap(
            lon=group["lon"],
            lat=group["lat"],
            mode="markers",
            name=str(cat),
            marker=dict(
                size=size,
                color=cmap.get(str(cat), "#118C4F"),
                opacity=0.8,
                allowoverlap=True,
            ),
            text=hover_name if hasattr(hover_name, "values") else "",
            hovertemplate=f"<b>%{{text}}</b><br>Lon: %{{lon:.4f}}<br>Lat: %{{lat:.4f}}<extra>{cat}</extra>",
        ))

    fig.update_layout(
        map=dict(style="white-bg", center=TOGO_CENTER, zoom=TOGO_ZOOM),
        **PLOTLY_LAYOUT,
        height=height,
        title=dict(text=title, font=dict(size=13, family="DM Sans")),
        showlegend=True,
    )
    return fig


def map_choropleth_zone(
    geojson: dict,
    df: pd.DataFrame,
    zone_col: str = "classe_zone",
    id_col: str = "prefecture_norm",
    score_col: str = "score_priorite",
    title: str = "Carte des zones prioritaires",
    height: int = 560,
) -> go.Figure:
    """
    Choroplèthe des 3 classes de zones (Bien / Surveiller / Prioritaire).
    """
    if df.empty or not geojson.get("features"):
        fig = go.Figure()
        _apply_layout(fig, title, height)
        return fig

    color_map_discrete = {
        "Bien desservie": "#10B981",
        "Zone à surveiller": "#F59E0B",
        "Zone prioritaire": "#EF4444",
    }

    fig = px.choropleth_map(
        df,
        geojson=geojson,
        locations=id_col,
        featureidkey="properties.name_norm",
        color=zone_col,
        color_discrete_map=color_map_discrete,
        center=TOGO_CENTER,
        zoom=TOGO_ZOOM,
        map_style="white-bg",
        hover_data={score_col: True, "population": True, "nb_agences": True, "nb_mm": True},
        opacity=0.88,
        category_orders={zone_col: ["Bien desservie", "Zone à surveiller", "Zone prioritaire"]},
    )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=height,
        title=dict(text=title, font=dict(size=13, family="DM Sans")),
        legend=dict(
            title=dict(text="Classe de zone"),
            orientation="v",
            x=0.01,
            y=0.98,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#E2E8F0",
            borderwidth=1,
        ),
    )
    return fig


# ─────────────────────────────────────────────
# TABLEAU FORMATÉ PLOTLY
# ─────────────────────────────────────────────

def table_top_communes(df: pd.DataFrame, cols_display: list, title: str = "") -> go.Figure:
    """Table Plotly élégante pour les classements."""
    disp = df[cols_display].head(20).copy()
    fig = go.Figure(go.Table(
        header=dict(
            values=[f"<b>{c}</b>" for c in cols_display],
            fill_color="#0D3321",
            font=dict(color="white", size=12, family="DM Sans"),
            align="left",
            height=36,
        ),
        cells=dict(
            values=[disp[c].tolist() for c in cols_display],
            fill_color=[["#F8FAFC", "white"] * (len(disp) // 2 + 1)],
            font=dict(color="#0F172A", size=11),
            align="left",
            height=30,
        ),
    ))
    _apply_layout(fig, title, height=min(600, 80 + len(disp) * 32))
    fig.update_layout(margin=dict(l=0, r=0, t=36, b=0))
    return fig
