"""
Page 4 — Recommandations Stratégiques
Feuille de Route pour l'Accélération de l'Inclusion Numérique au Togo
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px

from utils.style import inject_css, render_topbar, render_kpi_row, section_title
from utils.filters import render_filter_bar
from utils.data_loader import get_aggregates, REGIONS_ORDER
from utils.geo_utils import compute_priority_score

# Injection CSS
inject_css()

# 1. Topbar collée au haut et au sidebar (gris #2B303A)
render_topbar("Recommandations Stratégiques - Feuille de Route d'Inclusion")

# 2. Bandeau de filtres globaux persistants avec bouton Réinitialiser
filters = render_filter_bar()

# 3. Conteneur principal avec padding
st.markdown('<div class="page-container">', unsafe_allow_html=True)

agg = get_aggregates()
pref_df = agg["pref_df"].copy()
comm_df = agg["comm_df"].copy()

# Calcul des zones prioritaires
scored = compute_priority_score(comm_df)
n_prio = int((scored["classe_zone"] == "Zone prioritaire").sum())
pop_prio = int(scored[scored["classe_zone"] == "Zone prioritaire"]["population"].sum())
total_pop = int(comm_df["population"].sum())
pct_prio = pop_prio / max(total_pop, 1) * 100

top_prio_reg = (
    scored[scored["classe_zone"] == "Zone prioritaire"]
    .groupby("region_norm", as_index=False)["population"].sum()
    .sort_values("population", ascending=False)
)
top_prio_region = top_prio_reg.iloc[0]["region_norm"] if not top_prio_reg.empty else "Savanes"

worst_pref = pref_df.nlargest(1, "ratio_hab_infra")
worst_pref_name = worst_pref.iloc[0]["prefecture_label"] if not worst_pref.empty else "inconnue"
worst_ratio = int(worst_pref.iloc[0]["ratio_hab_infra"]) if not worst_pref.empty else 0

# Groupby standardisé sécurisé
mm_region = (
    pref_df.groupby("region_norm", as_index=False)[["nb_mm", "population"]]
    .sum()
)
mm_region["ratio_mm_10k"] = mm_region["nb_mm"] / mm_region["population"].clip(lower=1) * 10_000
worst_mm_reg_row = mm_region.nsmallest(1, "ratio_mm_10k")
worst_mm_reg = worst_mm_reg_row.iloc[0]["region_norm"] if not worst_mm_reg_row.empty else "Centrale"
worst_mm_val = float(worst_mm_reg_row.iloc[0]["ratio_mm_10k"]) if not worst_mm_reg_row.empty else 0

dc_count = agg["total_dc"]

# ── KPIs Stratégiques ──────────────────────
render_kpi_row([
    {"value": str(n_prio),           "label": "Communes prioritaires", "color": "red"},
    {"value": f"{pct_prio:.1f}%",    "label": "Pop. en zone critique",  "color": "red"},
    {"value": worst_pref_name,       "label": "Préf. la moins dotée",   "color": "orange"},
    {"value": f"{worst_mm_val:.1f}", "label": f"MM/10k ({worst_mm_reg})", "color": "blue"},
    {"value": str(dc_count),         "label": "Datacenters au Togo",    "color": ""},
])

# ── Recommandations Actionnables ───────────
section_title("Feuille de Route Stratégique")

RECOS = [
    {
        "num": "01",
        "color": "red",
        "titre": "Déploiement ciblé et prioritaire dans les zones blanches critiques",
        "corps": f"""
<b>Constat :</b> {n_prio} communes ({pct_prio:.1f}% de la population, soit {pop_prio:,} habitants) sont dépourvues de réseau suffisant d'agences et d'agents Mobile Money. La région {top_prio_region} concentre l'essentiel de cette population sous-desservie.

<b>Actions concrètes recommandées :</b>
• Mettre en place un plan d'urgence de déploiement d'agents de proximité dans les communes prioritaires de plus de 5 000 habitants.
• Déployer des relais télécoms mutualisés entre Togocom et Moov pour réduire le coût d'investissement dans les localités isolées.
• Expérimenter des caravanes d'inclusion numérique mobiles pour apporter services administratifs et financiers dans les cantons ruraux.
        """.strip(),
        "stat": f"{n_prio} communes prioritaires identifiées ({pop_prio:,} hab.)",
    },
    {
        "num": "02",
        "color": "orange",
        "titre": "Réduction des disparités régionales d'accès aux services financiers mobiles",
        "corps": f"""
<b>Constat :</b> La région {worst_mm_reg} enregistre le ratio le plus faible avec seulement {worst_mm_val:.1f} agents MM pour 10 000 habitants, contre une moyenne bien plus élevée dans la région Maritime / Grand Lomé.

<b>Actions concrètes recommandées :</b>
• Définir un seuil minimal réglementaire de densité d'agents Mobile Money (ex. minimum 25 agents pour 10 000 habitants par préfecture).
• Mettre en place un mécanisme d'incitation fiscale ou de subvention d'amorçage pour les agents s'installant dans les préfectures de l'Intérieur.
• Accélérer l'interopérabilité des plateformes de paiement mobile pour maximiser l'utilité des points de vente ruraux.
        """.strip(),
        "stat": f"Objectif cible : minimum 25 agents MM / 10k hab. dans chaque région",
    },
    {
        "num": "03",
        "color": "blue",
        "titre": "Densification des infrastructures dans les préfectures sous-dotées",
        "corps": f"""
<b>Constat :</b> La préfecture de {worst_pref_name} présente une pression extrême avec {worst_ratio:,} habitants par infrastructure physique, traduisant une saturation locale et des files d'attente importantes.

<b>Actions concrètes recommandées :</b>
• Imposer des critères de couverture minimale aux opérateurs concessionnaires lors du renouvellement des licences ARCEP.
• Faciliter l'octroi d'agréments aux établissements de microfinance et réseaux postaux (La Poste du Togo) pour agir comme tiers distributeurs télécom.
• Favoriser l'implantation de micro-datacenters et points d'échange régionaux (IXP) pour héberger localement les données publiques.
        """.strip(),
        "stat": f"Ratio actuel le plus critique : {worst_ratio:,} hab./infra ({worst_pref_name})",
    },
    {
        "num": "04",
        "color": "",
        "titre": "Gouvernance par la donnée : Observatoire National du Numérique",
        "corps": """
<b>Constat :</b> L'absence de cartographie dynamique unifiée et actualisée trimestriellement des infrastructures retarde l'identification des poches de déconnexion et la prise de décision publique.

<b>Actions concrètes recommandées :</b>
• Institutionnaliser ce tableau de bord Togo DataLab au sein du Ministère de l'Économie Numérique et de l'ARCEP.
• Obliger les opérateurs télécoms (Togocom, Moov) et acteurs Fintech à téléverser mensuellement leurs points de présence sous format standardisé ouvert.
• Établir un baromètre public annuel de l'inclusion numérique mesurant les progrès par commune et canton.
        """.strip(),
        "stat": "Recommandation de gouvernance et de régulation continue",
    },
]

card_cols = st.columns(2)
for idx, reco in enumerate(RECOS):
    color_cls = f" {reco['color']}" if reco["color"] else ""
    body_html = reco["corps"].replace("\n", "<br>")
    with card_cols[idx % 2]:
        st.markdown(f"""
        <div class="reco-card{color_cls}">
          <div class="reco-num">Recommandation {reco['num']}</div>
          <div class="reco-title">{reco['titre']}</div>
          <div class="reco-body">{body_html}</div>
          <span class="reco-stat">{reco['stat']}</span>
        </div>
        """, unsafe_allow_html=True)

# ── Plan d'action opérationnel ─────────────
st.markdown('<div class="content-card">', unsafe_allow_html=True)
section_title("Matrice de mise en œuvre des recommandations")

plan_data = pd.DataFrame([
    {
        "Recommandation": "R01 — Déploiement zones blanches",
        "Horizon": "Court terme (6-12 mois)",
        "Priorité": "Critique",
        "Acteurs responsables": "ARCEP, Opérateurs (Togocom, Moov)",
        "Indicateur cible": "0 commune > 5k hab. sans agent MM",
    },
    {
        "Recommandation": "R02 — Réduction disparités régionales",
        "Horizon": "Moyen terme (12-24 mois)",
        "Priorité": "Élevée",
        "Acteurs responsables": "Ministère TIC, Fintechs, Banques",
        "Indicateur cible": "Min. 25 agents MM / 10k hab. partout",
    },
    {
        "Recommandation": "R03 — Densification préfectures saturées",
        "Horizon": "Moyen terme (18-24 mois)",
        "Priorité": "Moyenne",
        "Acteurs responsables": "Opérateurs, La Poste, Collectivités",
        "Indicateur cible": "< 500 hab./infra dans chaque préfecture",
    },
    {
        "Recommandation": "R04 — Observatoire National Numérique",
        "Horizon": "Immédiat (3-6 mois)",
        "Priorité": "Haute",
        "Acteurs responsables": "Togo DataLab, Ministère Économie Num.",
        "Indicateur cible": "Plateforme ouverte actualisée chaque trimestre",
    },
])

st.dataframe(plan_data, width="stretch", hide_index=True)

st.download_button(
    "Télécharger la feuille de route (CSV)",
    data=plan_data.to_csv(index=False).encode("utf-8"),
    file_name="feuille_de_route_togo_numerique.csv",
    mime="text/csv",
)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
