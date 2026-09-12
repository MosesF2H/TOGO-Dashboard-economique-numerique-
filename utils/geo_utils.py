"""
utils/geo_utils.py
Calculs géographiques : score proxy zones blanches, distances.
"""

import numpy as np
import pandas as pd


# ─────────────────────────────────────────────
# SCORE DE PRIORITÉ (proxy zones blanches)
# ─────────────────────────────────────────────

def compute_priority_score(
    comm_df: pd.DataFrame,
    w1: float = 0.30,  # Poids : désert d'agences
    w2: float = 0.40,  # Poids : sous-dotation mobile money
    w3: float = 0.30,  # Poids : densité démographique non couverte
) -> pd.DataFrame:
    """
    Calcule le score de priorité pour chaque commune (0 à 100).
    """
    df = comm_df.copy()

    # Normalisation des poids
    total_w = w1 + w2 + w3
    if total_w == 0:
        w1, w2, w3 = 0.33, 0.34, 0.33
    else:
        w1, w2, w3 = w1 / total_w, w2 / total_w, w3 / total_w

    # C1 — Désert d'agences [0-1]
    max_ag = max(df["nb_agences"].max(), 1)
    df["C1"] = 1.0 - (df["nb_agences"] / max_ag).clip(0, 1)

    # C2 — Sous-dotation Mobile Money [0-1]
    df["ratio_mm_10k"] = (df["nb_mm"] / df["population"].clip(lower=1)) * 10_000
    median_ratio = df["ratio_mm_10k"].median()
    if median_ratio > 0:
        df["C2"] = (1.0 - (df["ratio_mm_10k"] / (median_ratio * 2))).clip(0, 1)
    else:
        df["C2"] = (df["nb_mm"] == 0).astype(float)

    # C3 — Densité démographique non couverte [0-1]
    max_pop = max(df["population"].max(), 1)
    df["pop_norm"] = df["population"] / max_pop
    df["has_infra"] = (df["nb_agences"] + df["nb_mm"] > 0).astype(float)
    df["C3"] = df["pop_norm"] * (1.0 - df["has_infra"])

    # Score global [0-100]
    df["score_priorite"] = (w1 * df["C1"] + w2 * df["C2"] + w3 * df["C3"]) * 100
    df["score_priorite"] = df["score_priorite"].clip(0, 100).round(1)

    # Classification
    df["classe_zone"] = df["score_priorite"].apply(classify_zone)

    return df


def classify_zone(score: float) -> str:
    """Classifie le score de priorité en 3 niveaux d'intervention."""
    if score < 35:
        return "Bien couverte"
    elif score < 65:
        return "Sous surveillance"
    else:
        return "Zone prioritaire"


ZONE_COLORS = {
    "Bien couverte":      "#10B981",
    "Bien desservie":     "#10B981",
    "Sous surveillance":  "#F59E0B",
    "Zone à surveiller":  "#F59E0B",
    "Zone prioritaire":   "#EF4444",
}

ZONE_CSS_CLASSES = {
    "Bien couverte":      "zone-bien",
    "Bien desservie":     "zone-bien",
    "Sous surveillance":  "zone-surveil",
    "Zone à surveiller":  "zone-surveil",
    "Zone prioritaire":   "zone-prio",
}


def zone_badge(zone: str) -> str:
    cls = ZONE_CSS_CLASSES.get(zone, "")
    return f'<span class="zone-badge {cls}">{zone}</span>'


# ─────────────────────────────────────────────
# DISTANCE HAVERSINE
# ─────────────────────────────────────────────

def haversine_km(lat1, lon1, lat2, lon2) -> float:
    """Distance en km entre deux points GPS."""
    R = 6371.0
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlam = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlam / 2) ** 2
    return R * 2 * np.arcsin(np.sqrt(a))


def nearest_infra_distance(point_lat: float, point_lon: float, df_infra: pd.DataFrame) -> float:
    """
    Distance (km) du point au datacenter/agence le plus proche.
    """
    if df_infra.empty:
        return 9999.0
    dists = df_infra.apply(
        lambda row: haversine_km(point_lat, point_lon, row["lat"], row["lon"]),
        axis=1,
    )
    return float(dists.min())
