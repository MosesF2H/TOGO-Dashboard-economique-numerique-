"""
utils/data_loader.py
Chargement, nettoyage, normalisation et filtrage de toutes les données.
"""

import ast
import json
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import streamlit as st

# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────
_local_data = Path(__file__).parent.parent / "data"
_parent_data = Path(__file__).parent.parent.parent / "data"
DATA_DIR = _local_data if _local_data.exists() else _parent_data
ASSETS_DIR = Path(__file__).parent.parent / "assets"

TOGO_CENTER = {"lat": 8.7, "lon": 1.0}
TOGO_ZOOM = 6.0

REGION_NORMALIZE = {
    "GRAND LOME": "Maritime",
    "GRAND LOMÉ": "Maritime",
    "Grand Lomé": "Maritime",
    "Grand Lome": "Maritime",
    "GRAND_LOME": "Maritime",
    "MARITIME": "Maritime",
    "Maritime": "Maritime",
    "PLATEAUX": "Plateaux",
    "Plateaux": "Plateaux",
    "CENTRALE": "Centrale",
    "Centrale": "Centrale",
    "KARA": "Kara",
    "Kara": "Kara",
    "SAVANES": "Savanes",
    "Savanes": "Savanes",
}

REGIONS_ORDER = ["Maritime", "Plateaux", "Centrale", "Kara", "Savanes"]

OPERATOR_COLORS = {
    "Togocom": "#118C4F",
    "Moov": "#F5CE37",
    "Mixte": "#3498DB",
    "Inconnu": "#95A5A6",
    "Tous": "#0F172A",
}

INFRA_COLORS = {
    "Agences": "#118C4F",
    "Datacenters": "#3498DB",
    "Mobile Money": "#F5CE37",
}

# ─────────────────────────────────────────────
# UTILITAIRES DE NORMALISATION
# ─────────────────────────────────────────────

def strip_accents(text: str) -> str:
    """Supprime les accents et met en minuscule."""
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text.strip().lower()


def normalize_name(text) -> str:
    """Normalise un nom géographique pour les jointures."""
    if pd.isna(text) or text is None:
        return ""
    s = strip_accents(str(text))
    s = re.sub(r"[-_/]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def normalize_region(raw) -> str:
    """Mappe n'importe quelle variante vers les 5 régions standard."""
    if pd.isna(raw) or raw is None:
        return "Inconnu"
    raw_s = str(raw).strip()
    # Essai direct
    if raw_s in REGION_NORMALIZE:
        return REGION_NORMALIZE[raw_s]
    # Essai strip_accents
    stripped = strip_accents(raw_s)
    for key, val in REGION_NORMALIZE.items():
        if strip_accents(key) == stripped:
            return val
    # Essai partiel
    for key, val in REGION_NORMALIZE.items():
        if strip_accents(key) in stripped or stripped in strip_accents(key):
            return val
    return raw_s.title()


# ─────────────────────────────────────────────
# PARSING DES COORDONNÉES
# ─────────────────────────────────────────────

def parse_coords(val):
    """
    Parse la colonne 'coordonnees' qui contient soit:
    - "[lon, lat]" (string)
    - une liste Python
    Retourne (lon, lat) ou (None, None) si invalide.
    Les coordonnées de Togo : lat ∈ [6.0, 11.5], lon ∈ [-0.2, 1.8]
    """
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return None, None
    try:
        s = str(val).strip()
        # Nettoyage : remplacer les apostrophes/crochets alternatifs
        s = s.replace("(", "[").replace(")", "]")
        coords = ast.literal_eval(s)
        if isinstance(coords, (list, tuple)) and len(coords) >= 2:
            lon, lat = float(coords[0]), float(coords[1])
            # Validation des bornes Togo
            if -0.5 <= lon <= 2.0 and 5.5 <= lat <= 12.0:
                return lon, lat
            # Parfois lat/lon inversés
            if -0.5 <= lat <= 2.0 and 5.5 <= lon <= 12.0:
                return lat, lon
    except Exception:
        pass
    # Essai regex pour format "lat,lon" ou "lon lat"
    try:
        nums = re.findall(r"[-+]?\d+\.?\d*", str(val))
        if len(nums) >= 2:
            a, b = float(nums[0]), float(nums[1])
            if -0.5 <= a <= 2.0 and 5.5 <= b <= 12.0:
                return a, b
            if -0.5 <= b <= 2.0 and 5.5 <= a <= 12.0:
                return b, a
    except Exception:
        pass
    return None, None


# ─────────────────────────────────────────────
# CHARGEMENT DES DONNÉES
# ─────────────────────────────────────────────

@st.cache_data(show_spinner="Chargement des agences télécom…")
def load_agences() -> pd.DataFrame:
    """Charge agences_telecom.xlsx — source unique des agences."""
    path = DATA_DIR / "agences_telecom.xlsx"
    df = pd.read_excel(path, engine="openpyxl")
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Trouver la colonne de coordonnées
    coord_col = next((c for c in df.columns if "coord" in c), None)
    if coord_col:
        df[["lon", "lat"]] = pd.DataFrame(
            df[coord_col].apply(parse_coords).tolist(), index=df.index
        )

    # Normaliser la région
    reg_col = next((c for c in df.columns if "region" in c or "région" in c.lower()), None)
    if reg_col:
        df["region_norm"] = df[reg_col].apply(normalize_region)
    else:
        df["region_norm"] = "Inconnu"

    # Préfecture
    pref_col = next((c for c in df.columns if "prefecture" in c or "préfecture" in c.lower()), None)
    if pref_col:
        df["prefecture_norm"] = df[pref_col].apply(normalize_name)
        df["prefecture_label"] = df[pref_col].apply(lambda x: str(x).title() if pd.notna(x) else "")
    else:
        df["prefecture_norm"] = ""
        df["prefecture_label"] = ""

    # Commune
    com_col = next((c for c in df.columns if "commune" in c), None)
    if com_col:
        df["commune_norm"] = df[com_col].apply(normalize_name)
        df["commune_label"] = df[com_col].apply(lambda x: str(x).title() if pd.notna(x) else "")
    else:
        df["commune_norm"] = ""
        df["commune_label"] = ""

    # Opérateur
    # NB : agences_telecom.xlsx (export agrégé Moov + Togocom) ne contient
    # aucune colonne nommée "operateur" — l'opérateur n'est identifiable
    # qu'à travers le texte de la catégorie d'activité ou le nom de l'agence
    # (ex. "Agence Togocom Sotouboua"). On détecte donc en cascade.
    op_col = next((c for c in df.columns if "operateur" in c or "opérateur" in c.lower() or "operator" in c), None)
    if op_col:
        df["operateur_norm"] = df[op_col].apply(_normalize_operator)
    else:
        text_col = next((c for c in df.columns if "categorie" in c or "catégorie" in c.lower()), None)
        if not text_col:
            text_col = next((c for c in df.columns if "nom" in c), None)
        df["operateur_norm"] = df[text_col].apply(_normalize_operator) if text_col else "Inconnu"

    # Année de création
    date_cols = [c for c in df.columns if "date" in c or "annee" in c or "année" in c.lower()]
    if date_cols:
        try:
            df["annee_creation"] = pd.to_datetime(df[date_cols[0]], errors="coerce").dt.year
        except Exception:
            df["annee_creation"] = np.nan
    else:
        df["annee_creation"] = np.nan

    # Nom de l'agence
    nom_col = next((c for c in df.columns if "nom" in c and "agence" in c), None)
    if not nom_col:
        nom_col = next((c for c in df.columns if "nom" in c), None)
    df["nom_label"] = df[nom_col].fillna("Agence") if nom_col else "Agence"

    # Supprimer les lignes sans coordonnées valides
    df = df.dropna(subset=["lon", "lat"]).copy()
    df["type_infra"] = "Agences"
    return df.reset_index(drop=True)


@st.cache_data(show_spinner="Chargement des agents Mobile Money…")
def load_mobile_money() -> pd.DataFrame:
    """Charge agents_mobile_money.xlsx."""
    path = DATA_DIR / "agents_mobile_money.xlsx"
    df = pd.read_excel(path, engine="openpyxl")
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    coord_col = next((c for c in df.columns if "coord" in c), None)
    if coord_col:
        df[["lon", "lat"]] = pd.DataFrame(
            df[coord_col].apply(parse_coords).tolist(), index=df.index
        )

    reg_col = next((c for c in df.columns if "region" in c or "région" in c.lower()), None)
    df["region_norm"] = df[reg_col].apply(normalize_region) if reg_col else "Inconnu"

    pref_col = next((c for c in df.columns if "prefecture" in c or "préfecture" in c.lower()), None)
    if pref_col:
        df["prefecture_norm"] = df[pref_col].apply(normalize_name)
        df["prefecture_label"] = df[pref_col].apply(lambda x: str(x).title() if pd.notna(x) else "")
    else:
        df["prefecture_norm"] = ""
        df["prefecture_label"] = ""

    com_col = next((c for c in df.columns if "commune" in c), None)
    if com_col:
        df["commune_norm"] = df[com_col].apply(normalize_name)
        df["commune_label"] = df[com_col].apply(lambda x: str(x).title() if pd.notna(x) else "")
    else:
        df["commune_norm"] = ""
        df["commune_label"] = ""

    canton_col = next((c for c in df.columns if "canton" in c), None)
    if canton_col:
        df["canton_norm"] = df[canton_col].apply(normalize_name)
    else:
        df["canton_norm"] = ""

    op_col = next((c for c in df.columns if "operateur" in c or "opérateur" in c.lower() or "operator" in c), None)
    if op_col:
        df["operateur_norm"] = df[op_col].apply(_normalize_operator)
    else:
        df["operateur_norm"] = "Inconnu"

    # Étiquette d'affichage (le jeu de données ne fournit pas de nom d'agent
    # individuel : on construit un libellé lisible pour les info-bulles carte).
    df["nom_label"] = "Agent Mobile Money — " + df["operateur_norm"].astype(str)

    df = df.dropna(subset=["lon", "lat"]).copy()
    df["type_infra"] = "Mobile Money"
    return df.reset_index(drop=True)


@st.cache_data(show_spinner="Chargement des datacenters…")
def load_datacenters() -> pd.DataFrame:
    """Charge datacenter_etablissements.xlsx."""
    path = DATA_DIR / "datacenter_etablissements.xlsx"
    df = pd.read_excel(path, engine="openpyxl")
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    coord_col = next((c for c in df.columns if "coord" in c), None)
    if coord_col:
        df[["lon", "lat"]] = pd.DataFrame(
            df[coord_col].apply(parse_coords).tolist(), index=df.index
        )

    reg_col = next((c for c in df.columns if "region" in c or "région" in c.lower()), None)
    df["region_norm"] = df[reg_col].apply(normalize_region) if reg_col else "Maritime"

    pref_col = next((c for c in df.columns if "prefecture" in c or "préfecture" in c.lower()), None)
    if pref_col:
        df["prefecture_norm"] = df[pref_col].apply(normalize_name)
        df["prefecture_label"] = df[pref_col].apply(lambda x: str(x).title() if pd.notna(x) else "")
    else:
        df["prefecture_norm"] = ""
        df["prefecture_label"] = ""

    com_col = next((c for c in df.columns if "commune" in c), None)
    if com_col:
        df["commune_norm"] = df[com_col].apply(normalize_name)
        df["commune_label"] = df[com_col].apply(lambda x: str(x).title() if pd.notna(x) else "")
    else:
        df["commune_norm"] = ""
        df["commune_label"] = ""

    nom_col = next((c for c in df.columns if "nom" in c), None)
    df["nom_label"] = df[nom_col] if nom_col else "Datacenter"

    df["operateur_norm"] = "Inconnu"
    df["type_infra"] = "Datacenters"

    # Garder toutes lignes (même sans coord pour les stats)
    df_geo = df.dropna(subset=["lon", "lat"]).copy()
    return df_geo.reset_index(drop=True), df.reset_index(drop=True)


@st.cache_data(show_spinner="Chargement de la démographie…")
def load_population() -> pd.DataFrame:
    """Charge repartit_pop_rgph5_tg.xlsx avec normalisation."""
    path = DATA_DIR / "repartit_pop_rgph5_tg.xlsx"
    df = pd.read_excel(path, engine="openpyxl")
    df.columns = df.columns.str.strip().str.lower()

    # Colonnes standardisées
    col_map = {}
    for c in df.columns:
        cn = strip_accents(c)
        if "region" in cn:
            col_map[c] = "region_raw"
        elif "prefecture" in cn:
            col_map[c] = "prefecture_raw"
        elif "commune" in cn:
            col_map[c] = "commune_raw"
        elif "canton" in cn:
            col_map[c] = "canton_raw"
        elif "population" in cn or "pop" == cn or cn.startswith("pop"):
            col_map[c] = "population"

    df = df.rename(columns=col_map)

    for col in ["region_raw", "prefecture_raw", "commune_raw", "canton_raw", "population"]:
        if col not in df.columns:
            df[col] = np.nan if col == "population" else ""

    df["region_norm"] = df["region_raw"].apply(normalize_region)
    df["prefecture_norm"] = df["prefecture_raw"].apply(normalize_name)
    df["commune_norm"] = df["commune_raw"].apply(normalize_name)
    df["canton_norm"] = df["canton_raw"].apply(normalize_name)

    df["prefecture_label"] = df["prefecture_raw"].apply(lambda x: str(x).title() if pd.notna(x) and str(x).strip() else "")
    df["commune_label"] = df["commune_raw"].apply(lambda x: str(x).title() if pd.notna(x) and str(x).strip() else "")
    df["canton_label"] = df["canton_raw"].apply(lambda x: str(x).title() if pd.notna(x) and str(x).strip() else "")

    df["population"] = pd.to_numeric(df["population"], errors="coerce").fillna(0).astype(int)

    return df.reset_index(drop=True)


def _normalize_operator(val) -> str:
    if pd.isna(val) or val is None:
        return "Inconnu"
    s = strip_accents(str(val)).lower()
    if s in ("nsp", "non specifie", "n/a", "na", ""):
        return "Inconnu"
    has_togocom = "togocom" in s or "togo com" in s or "telecom" in s
    has_moov = "moov" in s
    # IMPORTANT : les agents Mobile Money partagés (ex. "Moov, Togocom")
    # doivent être classés "Mixte" — vérifier la double présence AVANT
    # les tests individuels, sinon ils retombent tous sur "Togocom".
    if (has_togocom and has_moov) or "mixte" in s or "both" in s or "tous" in s:
        return "Mixte"
    if has_togocom:
        return "Togocom"
    if has_moov:
        return "Moov"
    return str(val).strip().title()


# ─────────────────────────────────────────────
# GÉOJSON TOGO (GADM)
# ─────────────────────────────────────────────

GADM_URLS = {
    "regions": "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_TGO_1.json",
    "prefectures": "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_TGO_2.json",
}

# Le fond de carte GADM (limites administratives) et le fichier RGPH-5
# (population) n'utilisent pas exactement le même découpage / la même
# orthographe des préfectures. Sans cette table de correspondance, les
# polygones concernés restent gris/vides sur la carte (aucune valeur
# ne leur est associée), ce qui ressemble à une "carte cassée".
#   - bimah / tandjouare / tchaudjo → variantes orthographiques GADM
#     du RGPH-5 (binah / tandjoare / tchaoudjo).
#   - naki ouest → ancien découpage GADM correspondant à la préfecture
#     récente de Kpendjal-Ouest.
#   - lome → ancienne préfecture GADM absorbée par "Golfe" dans le
#     découpage administratif actuel (agglomération du Grand Lomé) ;
#     rattachée à Golfe pour l'affichage.
PREFECTURE_NAME_ALIASES = {
    "bimah": "binah",
    "tandjouare": "tandjoare",
    "tchaudjo": "tchaoudjo",
    "naki ouest": "kpendjal ouest",
    "lome": "golfe",
}


@st.cache_data(show_spinner="Téléchargement des limites géographiques du Togo…", ttl=86400)
def load_geojson(level: str = "prefectures") -> dict:
    """
    Charge le GeoJSON Togo niveau 'regions' ou 'prefectures'.
    Ajoute une colonne normalisée pour les jointures.
    """
    fname = f"togo_{level}.geojson"
    fpath = ASSETS_DIR / fname

    if not fpath.exists():
        try:
            resp = requests.get(GADM_URLS[level], timeout=90)
            resp.raise_for_status()
            fpath.write_bytes(resp.content)
        except Exception as e:
            st.error(f"Impossible de télécharger le GeoJSON {level} : {e}")
            return {"type": "FeatureCollection", "features": []}

    with open(fpath, encoding="utf-8") as f:
        geojson = json.load(f)

    # Ajouter propriété normalisée pour jointure
    for feat in geojson.get("features", []):
        props = feat.get("properties", {})
        if level == "regions":
            name = props.get("NAME_1", "")
            props["name_norm"] = normalize_region(name)
        else:
            name = props.get("NAME_2", "")
            norm = normalize_name(name)
            props["name_norm"] = PREFECTURE_NAME_ALIASES.get(norm, norm)
            props["region_norm"] = normalize_region(props.get("NAME_1", ""))
        feat["properties"] = props

    return geojson


# ─────────────────────────────────────────────
# OPTIONS DE FILTRES (cascades)
# ─────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def get_filter_options():
    """
    Retourne les options disponibles pour les filtres en cascade.
    Basé sur la population (source de vérité géographique).
    """
    df_pop = load_population()

    regions = sorted([r for r in df_pop["region_norm"].unique() if r and r != "Inconnu"],
                     key=lambda x: REGIONS_ORDER.index(x) if x in REGIONS_ORDER else 99)

    # Dictionnaire région → préfectures
    reg_to_pref = {}
    for reg in regions:
        prefs = df_pop[df_pop["region_norm"] == reg]["prefecture_label"].dropna().unique()
        reg_to_pref[reg] = sorted({p.strip() for p in prefs if str(p).strip()})

    # Dictionnaire région → communes (utile pour la cascade lorsqu'aucune préfecture n'est choisie)
    reg_to_comm = {}
    for reg in regions:
        comms = df_pop[df_pop["region_norm"] == reg]["commune_label"].dropna().unique()
        reg_to_comm[reg] = sorted({str(c).strip() for c in comms if str(c).strip()})

    # Dictionnaire préfecture_norm → communes
    pref_to_comm = {}
    for _, row in df_pop.iterrows():
        pref_n = row["prefecture_norm"]
        comm_l = row["commune_label"]
        if pref_n and comm_l:
            pref_to_comm.setdefault(pref_n, set()).add(str(comm_l).strip())
    pref_to_comm = {k: sorted(v) for k, v in pref_to_comm.items()}

    return {
        "regions": regions,
        "reg_to_pref": reg_to_pref,
        "reg_to_comm": reg_to_comm,
        "pref_to_comm": pref_to_comm,
    }


# ─────────────────────────────────────────────
# APPLICATION DES FILTRES
# ─────────────────────────────────────────────

def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Applique les filtres session sur un DataFrame qui doit avoir:
    region_norm, prefecture_norm, commune_norm, operateur_norm, type_infra
    """
    out = df.copy()

    if filters.get("region") and filters["region"] != "Toutes":
        out = out[out["region_norm"] == filters["region"]]

    if filters.get("prefecture") and filters["prefecture"] != "Toutes":
        pref_n = normalize_name(filters["prefecture"])
        out = out[out["prefecture_norm"] == pref_n]

    if filters.get("commune") and filters["commune"] != "Toutes":
        com_n = normalize_name(filters["commune"])
        out = out[out["commune_norm"] == com_n]

    if filters.get("operateur") and filters["operateur"] != "Tous":
        out = out[out["operateur_norm"] == filters["operateur"]]

    if filters.get("type_infra") and filters["type_infra"] != "Tous":
        out = out[out["type_infra"] == filters["type_infra"]]

    return out.reset_index(drop=True)


def get_active_filters() -> dict:
    """Lit les filtres depuis st.session_state."""
    return {
        "region": st.session_state.get("f_region", "Toutes"),
        "prefecture": st.session_state.get("f_prefecture", "Toutes"),
        "commune": st.session_state.get("f_commune", "Toutes"),
        "operateur": st.session_state.get("f_operateur", "Tous"),
        "type_infra": st.session_state.get("f_type_infra", "Tous"),
    }


# ─────────────────────────────────────────────
# AGRÉGATS PRÉ-CALCULÉS
# ─────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def get_aggregates():
    """
    Calcule tous les agrégats utiles une seule fois.
    Retourne un dictionnaire d'agrégats.
    """
    df_ag = load_agences()
    df_mm = load_mobile_money()
    _, df_dc_all = load_datacenters()
    df_pop = load_population()

    # Population par région
    pop_region = (
        df_pop.groupby("region_norm")["population"]
        .sum()
        .reindex(REGIONS_ORDER, fill_value=0)
        .reset_index()
    )
    pop_region.columns = ["region", "population"]

    # Agences par région
    ag_region = df_ag.groupby("region_norm").size().reset_index(name="nb_agences")
    ag_region.columns = ["region", "nb_agences"]

    # MM par région
    mm_region = df_mm.groupby("region_norm").size().reset_index(name="nb_mm")
    mm_region.columns = ["region", "nb_mm"]

    # MM par opérateur
    mm_op = df_mm.groupby("operateur_norm").size().reset_index(name="count")
    mm_op.columns = ["operateur", "count"]

    # Agences par opérateur
    ag_op = df_ag.groupby("operateur_norm").size().reset_index(name="count")
    ag_op.columns = ["operateur", "count"]

    # Agences par préfecture
    ag_pref = df_ag.groupby(["prefecture_norm", "prefecture_label", "region_norm"]).size().reset_index(name="nb_agences")

    # MM par préfecture
    mm_pref = df_mm.groupby(["prefecture_norm", "prefecture_label", "region_norm"]).size().reset_index(name="nb_mm")

    # Pop par préfecture (agréger les communes)
    pop_pref = df_pop.groupby(["prefecture_norm", "prefecture_label", "region_norm"])["population"].sum().reset_index()

    # Jointure préfecture
    pref_df = pop_pref.merge(ag_pref[["prefecture_norm", "nb_agences"]], on="prefecture_norm", how="left")
    pref_df = pref_df.merge(mm_pref[["prefecture_norm", "nb_mm"]], on="prefecture_norm", how="left")
    pref_df["nb_agences"] = pref_df["nb_agences"].fillna(0).astype(int)
    pref_df["nb_mm"] = pref_df["nb_mm"].fillna(0).astype(int)
    pref_df["ratio_mm_10k"] = (pref_df["nb_mm"] / pref_df["population"].clip(lower=1) * 10000).round(1)
    pref_df["total_infra"] = pref_df["nb_agences"] + pref_df["nb_mm"]
    pref_df["ratio_hab_infra"] = (pref_df["population"] / pref_df["total_infra"].clip(lower=1)).round(0).astype(int)

    # Agences par année
    ag_year = (
        df_ag.dropna(subset=["annee_creation"])
        .groupby("annee_creation")
        .size()
        .reset_index(name="count")
    )
    ag_year["annee_creation"] = ag_year["annee_creation"].astype(int)

    # Agences par commune
    ag_comm = df_ag.groupby(["commune_norm", "commune_label", "prefecture_norm", "region_norm"]).size().reset_index(name="nb_agences")
    mm_comm = df_mm.groupby(["commune_norm", "commune_label", "prefecture_norm", "region_norm"]).size().reset_index(name="nb_mm")
    pop_comm = df_pop.groupby(["commune_norm", "commune_label", "prefecture_norm", "region_norm"])["population"].sum().reset_index()

    # Ajouter prefecture_label depuis df_pop (première occurrence par prefecture_norm)
    pref_label_map = (
        df_pop.dropna(subset=["prefecture_norm", "prefecture_label"])
        .drop_duplicates(subset=["prefecture_norm"])[["prefecture_norm", "prefecture_label"]]
    )
    pop_comm = pop_comm.merge(pref_label_map, on="prefecture_norm", how="left")
    pop_comm["prefecture_label"] = pop_comm["prefecture_label"].fillna("").str.strip()

    comm_df = pop_comm.merge(ag_comm[["commune_norm", "nb_agences"]], on="commune_norm", how="left")
    comm_df = comm_df.merge(mm_comm[["commune_norm", "nb_mm"]], on="commune_norm", how="left")
    comm_df["nb_agences"] = comm_df["nb_agences"].fillna(0).astype(int)
    comm_df["nb_mm"] = comm_df["nb_mm"].fillna(0).astype(int)
    comm_df["ratio_mm_10k"] = (comm_df["nb_mm"] / comm_df["population"].clip(lower=1) * 10000).round(1)
    comm_df["total_infra"] = comm_df["nb_agences"] + comm_df["nb_mm"]
    comm_df["ratio_hab_infra"] = (comm_df["population"] / comm_df["total_infra"].clip(lower=1)).round(0).astype(int)

    return {
        "pop_region": pop_region,
        "ag_region": ag_region,
        "mm_region": mm_region,
        "mm_op": mm_op,
        "ag_op": ag_op,
        "pref_df": pref_df,
        "comm_df": comm_df,
        "ag_year": ag_year,
        "total_agences": len(df_ag),
        "total_mm": len(df_mm),
        "total_dc": len(df_dc_all),
        "total_pop": df_pop["population"].sum(),
        "nb_communes_couvertes": int((comm_df["total_infra"] > 0).sum()),
        "nb_communes_total": len(comm_df),
    }
