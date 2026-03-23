# Sénégal Analytics Platform

> Dashboard multi-secteurs d'analyse financière des données BCEAO, SENELEC et CIMA.  
> Projet Big Data, Master 2 ISM Par Pascale Nancy Alia AKPO

---

## Description

Application web interactive développée avec **Flask + Dash + Python**, permettant l'analyse dynamique des indicateurs financiers du secteur bancaire sénégalais.

Les données proviennent :
- de la base Excel `BASE_SENEGAL2.xlsx` (24 banques, 2015-2020)
- des rapports PDF officiels de la **BCEAO** (Bilans 2022)
- d'un module de scraping qui récupère les liens des nouveaux rapports BCEAO

---

## Structure du Projet

```
banking_dash_project/
│
├── app.py                        # Point d'entrée Flask — orchestre les 3 dashboards
│
├── apps/
│   ├── banking/
│   │   ├── app.py                # Layout Dash du secteur bancaire
│   │   └── callbacks.py          # Callbacks : filtres, graphiques, ratios, PDF
│   ├── energie/
│   │   └── app.py                # Dashboard Énergie (stub — en développement)
│   └── assurance/
│       └── app.py                # Dashboard Assurance (stub — en développement)
│
├── utils/
│   ├── data_loader.py            # Chargement données (MongoDB → Excel → Backup)
│   ├── data_ingestion.py         # Extraction PDF (pdfplumber) + OCR + MongoDB
│   ├── map_utils.py              # Carte Plotly Sénégal (Scattermapbox)
│   ├── scraper.py                # Scraping liens PDF depuis bceao.int
│   └── ocr_processor.py         # Module OCR (pytesseract)
│
├── data_raw/
│   ├── BASE_SENEGAL2.xlsx        # Base principale (24 banques, 2015-2020)
│   └── real_bceao_data_2022.csv  # Export CSV 2022
│
├── assets/
│   └── style.css                 # CSS Premium (glassmorphism, animations, typography)
│
├── tests/
│   └── test_data_loader.py       # Tests unitaires pytest
│
├── requirements.txt              # Dépendances Python
└── README.md                     # Ce fichier
```

---

## Prérequis

- Python **3.10+**
- (Optionnel) MongoDB **5.0+** — une connexion locale sur `localhost:27017`
- (Optionnel) Tesseract OCR — pour le module `ocr_processor.py`

---

## Installation & Lancement

```bash
# 1. Cloner le dépôt
# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer l'application
python app.py
```
Ouvrir ensuite **http://localhost:5000** dans le navigateur.

| URL | Description |
|---|---|
| `http://localhost:5000/` | Page d'accueil — navigation multi-secteurs |
| `http://localhost:5000/banking/` | Dashboard Bancaire complet |
| `http://localhost:5000/energie/` | Dashboard Énergie (stub) |
| `http://localhost:5000/assurance/` | Dashboard Assurance (stub) |

---

## Fonctionnalités — Secteur Bancaire

| Fonctionnalité | Description |
|---|---|
| **Filtres interactifs** | Par Institution, par Année, par Indicateur |
| **KPI Stratégiques** | Bilan, Emplois/Crédits, Ressources, Résultat Net |
| **Ratios Prudentiels** | Solvabilité, ROE, ROA, Liquidité (normes BCEAO) |
| **Top 10 Benchmark** | Comparaison interbancaire dynamique |
| **Market Share** | Camembert de part de marché (actif total) |
| **Carte Sénégal** | Localisation géographique des banques (Dakar) |
| **Export PDF** | Rapport d'analyse téléchargeable — individuel ou consolidé |

---

## Sources de Données et Extraction PDF

### Base principale
Le fichier `BASE_SENEGAL2.xlsx` contient les données historiques de 24 banques sur la période 2015-2020, issues des déclarations BCEAO.

### Rapports PDFs BCEAO 2022
Les PDF officiels sont disponibles sur [bceao.int](https://www.bceao.int/fr/publications/bilans-et-comptes-de-resultats-des-banques-et-etablissements-financiers-de-lumoa).

Le module `data_ingestion.py` :
1. Utilise `scraper.py` pour récupérer les liens PDF
2. Extrait les tableaux financiers avec `pdfplumber`
3. Applique l'OCR via `pytesseract` sur les pages scannées
4. Stocke le résultat dans MongoDB (`banking_data.historical_data`)

---

## Lancer les Tests

```bash
# Depuis le dossier racine du projet
python -m pytest tests/ -v
```

---

## Technologies Utilisées

| Catégorie | Technologie |
|---|---|
| Backend | Flask 3.1 |
| Dashboard | Dash 3.3 + Dash Bootstrap Components |
| Visualisation | Plotly 6.5 |
| Données | Pandas, MongoDB (pymongo) |
| PDF | pdfplumber (extraction), fpdf2 (génération), pytesseract (OCR) |
| Web Scraping | requests, BeautifulSoup4 |
| Tests | pytest |

---

## Auteure

Projet réalisé dans le cadre du **Master 2 Big Data** Par Pascale Nancy Alia AKPO   
