# Togo DataLab — Dashboard Économie Numérique & Télécoms

Tableau de bord interactif d'aide à la décision pour le diagnostic des télécommunications, de l'inclusion financière et la résorption des zones blanches au Togo.

## 🇹🇬 Fonctionnalités Principales

- **Page 0 : Vue d'ensemble** : Indicateurs macroéconomiques, couverture des 117 communes, répartition régionale, carte interactive Mapbox du Togo.
- **Page 1 : Mobile & Agences** : Cartographie des agences télécoms et des agents Mobile Money (Togocom, Moov, Telecom).
- **Page 2 : Infrastructures & Démographie** : Croisement de la population RGPH-5 et de l'accès aux infrastructures, identification des préfectures sous-dotées, localisation des datacenters.
- **Page 3 : Couverture Réseau & Zones Blanches** : Calcul du score proxy de priorité (0 à 100) pour prioriser les investissements sur les communes non couvertes.
- **Page 4 : Recommandations Stratégiques** : 4 axes d'action chiffrés et feuille de route opérationnelle exportable.

## 🚀 Exécution Locale

```bash
# 1. Installation des dépendances
pip install -r requirements.txt

# 2. Lancement du dashboard
streamlit run streamlit_app.py
```

L'application s'ouvre automatiquement à l'adresse : `http://localhost:8501`.

## 🌐 Déploiement en Ligne (Streamlit Community Cloud)

1. Publiez ce dossier sur votre compte **GitHub** (dépôt public ou privé).
2. Rendez-vous sur [share.streamlit.io](https://share.streamlit.io).
3. Connectez votre compte GitHub et sélectionnez le dépôt.
4. Spécifiez le fichier principal : `streamlit_app.py` (ou `togo_dashboard/streamlit_app.py`).
5. Cliquez sur **Deploy** ! Vous obtiendrez un lien public direct (ex. `https://togo-datalab-dashboard.streamlit.app`) accessible à tous les membres du jury et évaluateurs.
