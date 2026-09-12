"""
utils/style.py
CSS global + composants HTML réutilisables pour le dashboard Togo DataLab.
"""

import base64
from pathlib import Path

import streamlit as st

ASSETS_DIR = Path(__file__).parent.parent / "assets"


def _get_logo_base64() -> str:
    """Encode le logo officiel en base64 pour injection HTML."""
    logo_path = ASSETS_DIR / "tg_logo.png"
    if logo_path.exists():
        return base64.b64encode(logo_path.read_bytes()).decode()
    return ""


# ─────────────────────────────────────────────
# CSS PRINCIPAL
# ─────────────────────────────────────────────

MAIN_CSS = """
<style>
/* ── Google Fonts & Material Symbols ─────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=DM+Sans:wght@500;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0');

/* ── Variables ───────────────────────────── */
:root {
  --green-main:   #118C4F;
  --green-dark:   #0B6B3A;
  --green-pale:   #E8F5EE;
  --yellow:       #D4AC0D;
  --blue:         #1D4ED8;
  --blue-hover:   #1E40AF;
  --red:          #DC2626;
  --orange:       #EA580C;
  --gray-sidebar: #2B303A;
  --gray-topbar:  #2B303A;
  --gray-light:   #F8FAFC;
  --border:       #E2E8F0;
  --text-dark:    #0F172A;
  --text-mid:     #475569;
  --text-light:   #94A3B8;
  --shadow:       0 1px 4px rgba(0,0,0,0.06), 0 2px 8px rgba(0,0,0,0.04);
  --shadow-lg:    0 4px 16px rgba(0,0,0,0.1);
  --radius:       8px;
  --radius-sm:    6px;
}

/* ── Reset & Scroll Naturel ───────────────── */
* { box-sizing: border-box; }

html, body {
  height: 100% !important;
  overflow-x: hidden !important;
  overflow-y: auto !important;
  margin: 0 !important;
  padding: 0 !important;
  background: #FFFFFF !important;
}

.stApp {
  font-family: 'Inter', sans-serif;
  background: #FFFFFF !important;
  min-height: 100vh !important;
  height: auto !important;
  overflow-y: visible !important;
}

[data-testid="stAppViewContainer"] {
  min-height: 100vh !important;
  height: auto !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  background: #FFFFFF !important;
}

/* ── Suppression de TOUT espace Streamlit en haut et à gauche ── */
.stApp > header { display: none !important; }
#root > div:first-child { padding-top: 0 !important; }

.block-container,
[data-testid="stMainBlockContainer"],
[data-testid="stAppViewBlockContainer"] {
  padding-top: 0 !important;
  padding-left: 0 !important;
  padding-right: 0 !important;
  padding-bottom: 2.5rem !important;
  max-width: 100% !important;
}

/* ── SIDEBAR GRIS (#2B303A) ──────────────── */
[data-testid="stSidebar"] {
  background: #2B303A !important;
  min-width: 275px !important;
  max-width: 275px !important;
  border-right: 1px solid rgba(255,255,255,0.08) !important;
  box-shadow: none !important;
  opacity: 1 !important;
  backdrop-filter: none !important;
}

[data-testid="stSidebar"] > div:first-child {
  background: #2B303A !important;
  padding-top: 0 !important;
  padding-left: 0 !important;
  padding-right: 0 !important;
  opacity: 1 !important;
}

[data-testid="stSidebar"] * {
  color: #E2E8F0 !important;
}

/* Logo & Emblème haut-gauche */
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 18px;
  background: rgba(0, 0, 0, 0.25);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.sidebar-brand img {
  width: 40px;
  height: 40px;
  object-fit: contain;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.12);
  padding: 3px;
}

.sidebar-brand-text .line1 {
  font-family: 'DM Sans', sans-serif;
  font-size: 1.02rem;
  font-weight: 800;
  color: #FFFFFF;
  letter-spacing: 0.08em;
  line-height: 1.15;
}

.sidebar-brand-text .line2 {
  font-family: 'DM Sans', sans-serif;
  font-size: 1.02rem;
  font-weight: 800;
  color: var(--green-main);
  letter-spacing: 0.08em;
  line-height: 1.15;
}

/* Titre de section sidebar */
.sidebar-menu-title {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.72rem;
  font-weight: 700;
  color: #94A3B8;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  padding: 20px 18px 8px 18px;
}

/* Liens de page dans la sidebar */
[data-testid="stSidebar"] a {
  color: #E2E8F0 !important;
  border-radius: var(--radius-sm) !important;
  padding: 9px 14px !important;
  margin: 3px 12px !important;
  font-size: 0.88rem !important;
  font-weight: 500 !important;
  display: flex !important;
  align-items: center !important;
  transition: all 0.15s ease !important;
}

[data-testid="stSidebar"] a:hover {
  background: rgba(255, 255, 255, 0.12) !important;
  color: #FFFFFF !important;
}

[data-testid="stSidebar"] a[aria-selected="true"] {
  background: var(--green-main) !important;
  color: #FFFFFF !important;
  font-weight: 600 !important;
}

[data-testid="stSidebar"] hr {
  border-color: rgba(255, 255, 255, 0.1) !important;
  margin: 12px 16px !important;
}

/* ── TOPBAR GRIS (#2B303A) COLLÉE SANS ESPACE ─ */
.topbar {
  background: var(--gray-topbar);
  padding: 0 28px 0 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0 !important;
  width: 100% !important;
  border-bottom: none !important;
  box-sizing: border-box;
  min-height: 58px;
  position: relative;
  left: 0;
  right: 0;
  border-top: none !important;
}

[data-testid="stSidebar"] {
  margin-left: 0 !important;
  padding-left: 0 !important;
}

main[data-testid="stMain"] {
  padding-top: 0 !important;
  padding-left: 0.5rem !important;
}

[data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"] {
  padding-top: 0 !important;
  margin-top: 0 !important;
}

section[data-testid="stMain"] > div {
  padding-left: 0.35rem !important;
  padding-right: 0.3rem !important;
}

.topbar-title {
  font-family: 'DM Sans', sans-serif;
  font-size: 1.15rem;
  font-weight: 700;
  color: #FFFFFF;
  letter-spacing: 0.01em;
}

.topbar-subtitle {
  font-size: 0.8rem;
  color: #CBD5E1;
  margin-top: 2px;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.topbar-badge {
  background: var(--green-main);
  color: white;
  padding: 5px 14px;
  border-radius: 20px;
  font-size: 0.74rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

/* ── BANDEAU DE FILTRES SOUS LE TOPBAR ────── */
.filter-strip {
  background: #F8FAFC;
  border-bottom: 1px solid #E2E8F0;
  padding: 12px 28px 10px 28px;
  margin-bottom: 22px;
  width: 100%;
}

.filter-strip [data-testid="stSelectbox"] label {
  font-size: 0.74rem !important;
  font-weight: 600 !important;
  color: #475569 !important;
  margin-bottom: 3px !important;
  text-transform: uppercase !important;
  letter-spacing: 0.04em !important;
}

/* Selectbox styling */
[data-testid="stSelectbox"] > div > div {
  border-radius: var(--radius-sm) !important;
  font-size: 0.84rem !important;
  background-color: #FFFFFF !important;
  border: 1px solid #CBD5E1 !important;
}

/* Bouton Réinitialiser corporate */
div[data-testid="stButton"] button {
  background: var(--blue) !important;
  color: #FFFFFF !important;
  font-weight: 600 !important;
  font-size: 0.82rem !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  padding: 7px 16px !important;
  transition: background 0.15s ease !important;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
}

div[data-testid="stButton"] button:hover {
  background: var(--blue-hover) !important;
}

/* ── PADDING DU CONTENU PRINCIPAL ─────────── */
.page-container {
  padding: 0 22px 0 18px !important;
}

/* ── KPI Cards rectangulaires, bordures complètes et alignées ───────────────────────────── */
.kpi-row {
  display: flex;
  gap: 14px;
  margin-bottom: 22px;
  flex-wrap: wrap;
  align-items: stretch;
}

.kpi-card {
  background: #FFFFFF !important;
  border: 1px solid #D9E2EC !important;
  border-left: 4px solid var(--green-main) !important;
  border-radius: 0 !important;
  box-shadow: var(--shadow) !important;
  padding: 14px 16px 12px 16px !important;
  min-height: 120px !important;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  margin-bottom: 0 !important;
}

.kpi-card.green { border-color: var(--green-main) !important; }
.kpi-card.yellow { border-color: var(--yellow) !important; border-left-color: var(--yellow) !important; }
.kpi-card.blue { border-color: var(--blue) !important; border-left-color: var(--blue) !important; }
.kpi-card.red { border-color: var(--red) !important; border-left-color: var(--red) !important; }
.kpi-card.orange { border-color: var(--orange) !important; border-left-color: var(--orange) !important; }

.kpi-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.material-icon {
  font-family: 'Material Symbols Outlined';
  font-size: 1.1rem;
  line-height: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: #F8FAFC;
  border: 1px solid rgba(15, 23, 42, 0.08);
  color: var(--green-main);
}

.kpi-label {
  font-size: 0.72rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.04em !important;
  text-transform: uppercase !important;
  color: var(--text-mid) !important;
}

.kpi-value {
  font-family: 'DM Sans', sans-serif !important;
  font-size: 1.6rem !important;
  font-weight: 700 !important;
  color: var(--text-dark) !important;
  line-height: 1.1 !important;
  margin-top: 8px !important;
}

.kpi-card .kpi-value.small {
  font-size: 1.3rem !important;
}

.kpi-extra {
  font-size: 0.7rem;
  color: var(--text-light);
  font-weight: 600;
  margin-top: 6px;
}

.kpi-card-yellow  { border-left-color: var(--yellow) !important; }
.kpi-card-blue    { border-left-color: var(--blue) !important; }
.kpi-card-red     { border-left-color: var(--red) !important; }
.kpi-card-orange  { border-left-color: var(--orange) !important; }

/* ── Section titles ──────────────────────── */
.section-title {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-dark);
  margin: 0 0 12px 0;
  padding-bottom: 6px;
  border-bottom: 2px solid var(--green-pale);
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ── Content card ────────────────────────── */
.content-card {
  background: #FFFFFF;
  border-radius: var(--radius);
  padding: 18px 20px;
  box-shadow: var(--shadow);
  border: 1px solid #E2E8F0;
  margin-bottom: 18px;
}

.full-width-panel {
  width: 100% !important;
  margin-top: 0 !important;
  margin-bottom: 18px !important;
  padding: 18px 20px !important;
  border: 1px solid #E2E8F0 !important;
  border-radius: var(--radius) !important;
  background: #FFFFFF !important;
  box-shadow: var(--shadow) !important;
}

.page-container > .content-card:first-of-type,
.page-container .kpi-row + div > .content-card:first-of-type,
.page-container .kpi-row + div > div > .content-card:first-of-type,
.page-container .kpi-row + div[data-testid="stHorizontalBlock"] > div:first-child > .content-card,
.page-container .kpi-row + div[data-testid="stVerticalBlock"] > .content-card:first-of-type {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
  margin-top: 0 !important;
  margin-bottom: 14px !important;
}

/* ── Recommandation cards ────────────────── */
.reco-card {
  background: #FFFFFF;
  border-radius: 0;
  padding: 20px 24px;
  box-shadow: none;
  border: 1px solid #E2E8F0;
  margin-bottom: 16px;
  border-left: none;
  min-height: 100%;
}
.reco-card.yellow { border-left: none; }
.reco-card.orange { border-left: none; }
.reco-card.blue   { border-left: none; }
.reco-card.red    { border-left: none; }

.reco-num {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--green-main);
  margin-bottom: 4px;
}
.reco-card.yellow .reco-num { color: var(--yellow); }
.reco-card.orange .reco-num { color: var(--orange); }
.reco-card.blue   .reco-num { color: var(--blue); }
.reco-card.red    .reco-num { color: var(--red); }

.reco-title {
  font-family: 'DM Sans', sans-serif;
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-dark);
  margin-bottom: 10px;
}

.reco-body {
  font-size: 0.85rem;
  color: var(--text-mid);
  line-height: 1.65;
}

.reco-stat {
  display: inline-block;
  background: var(--green-pale);
  color: var(--green-main);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.76rem;
  font-weight: 600;
  margin-top: 12px;
}

/* ── Zone badge ──────────────────────────── */
.zone-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.74rem;
  font-weight: 600;
}
.zone-bien    { background: #D1FAE5; color: #065F46; }
.zone-surveil { background: #FEF3C7; color: #92400E; }
.zone-prio    { background: #FEE2E2; color: #991B1B; }

/* ── Download button ─────────────────────── */
.stDownloadButton > button {
  background: #2563EB !important;
  color: white !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  font-weight: 600 !important;
}

[data-testid="stPlotlyChart"] {
  border-radius: var(--radius) !important;
  overflow: visible !important;
}

.content-card {
  overflow: visible !important;
}

/* ── Scrollbar fine ──────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #94A3B8; }
</style>
"""


def inject_css():
    """Injecte le CSS global dans la page Streamlit."""
    st.markdown(MAIN_CSS, unsafe_allow_html=True)


def render_sidebar_brand():
    """
    Affiche l'emblème suivi du nom TOGO DATA LAB
    dans le coin supérieur gauche du sidebar.
    """
    logo_b64 = _get_logo_base64()
    if logo_b64:
        img_tag = f'<img src="data:image/png;base64,{logo_b64}" alt="Logo Togo DataLab">'
    else:
        img_tag = '<div style="width:40px;height:40px;background:rgba(255,255,255,0.2);border-radius:6px;"></div>'

    st.sidebar.markdown(f"""
    <div class="sidebar-brand">
      {img_tag}
      <div class="sidebar-brand-text">
        <div class="line1">TOGO</div>
        <div class="line2">DATA LAB</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_topbar(subtitle: str = "Diagnostic Télécoms & Inclusion Numérique"):
    """
    Affiche la barre de titre en haut de chaque page,
    collée directement au sidebar sans aucun espace vertical ou horizontal.
    """
    st.markdown(f"""
    <div class="topbar">
      <div>
        <div class="topbar-title">Dashboard Économie Numérique du Togo</div>
        <div class="topbar-subtitle">{subtitle}</div>
      </div>
      <div class="topbar-right">
        <span class="topbar-badge">Togo DataLab 2026</span>
      </div>
    </div>
    """, unsafe_allow_html=True)


def kpi_card(icon: str, value: str, label: str, delta: str = "", color: str = "") -> str:
    """Génère le HTML d'une KPI card."""
    delta_html = ""
    if delta:
        neg = "neg" if delta.startswith("-") else ""
        delta_html = f'<div class="kpi-delta {neg}">{delta}</div>'
    color_cls = f" {color}" if color else ""
    return f"""
    <div class="kpi-card{color_cls}">
      <div class="kpi-value">{value}</div>
      <div class="kpi-label">{label}</div>
      {delta_html}
    </div>
    """


def render_kpi_row(cards: list):
    """Affiche une rangée de KPI cards avec icône, bordure complète et alignement propre."""
    if not cards:
        return

    icon_map = {
        "Agences Télécom": "business",
        "Agents Mobile Money": "payments",
        "Datacenters": "dns",
        "Population": "groups",
        "Communes couvertes": "location_on",
        "Communes analysées": "analytics",
        "Bien couvertes": "check_circle",
        "Sous surveillance": "warning",
        "Zones prioritaires": "priority_high",
        "Population prioritaire": "people",
        "Préfectures avec agences": "map",
        "Préfectures avec MM": "cell_tower",
        "Préf. la moins dotée": "trending_down",
        "Communes prioritaires": "target",
        "Pop. en zone critique": "pin_drop",
    }

    cols = st.columns(len(cards))
    for col, card in zip(cols, cards):
        with col:
            label = card.get("label", "")
            value = card.get("value", "–")
            color = card.get("color", "")
            safe_color = color if color in {"green", "yellow", "blue", "red", "orange"} else "green"
            icon = icon_map.get(label, "•")
            value_class = " small" if len(str(value)) > 12 else ""
            st.markdown(
                f"""
                <div class="kpi-card {safe_color}">
                  <div class="kpi-card-header">
                    <span class="material-icon">{icon}</span>
                    <span class="kpi-label">{label}</span>
                  </div>
                  <div class="kpi-value{value_class}">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def section_title(title: str, icon: str = ""):
    """Affiche un titre de section stylisé sans emojis."""
    st.markdown(
        f'<div class="section-title">{title}</div>',
        unsafe_allow_html=True,
    )
