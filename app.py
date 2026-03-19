from flask import Flask, redirect, render_template_string
from apps.banking.app import init_banking_app
from apps.energie.app import init_energie_app
from apps.assurance.app import init_assurance_app

# ============================================================
# Création de l'application Flask principale
# ============================================================
app = Flask(__name__)

# ============================================================
# Montage des 3 dashboards Dash sur des routes distinctes
# ============================================================
dash_banking   = init_banking_app(app)    # /banking/
dash_energie   = init_energie_app(app)    # /energie/
dash_assurance = init_assurance_app(app)  # /assurance/

# ============================================================
# Page d'accueil HTML — Navigation entre les 3 secteurs
# ============================================================
HOME_PAGE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Sénégal Analytics Platform</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;600;800&family=Plus+Jakarta+Sans:wght@400;500;700&display=swap" rel="stylesheet">
    <link href="https://use.fontawesome.com/releases/v5.15.4/css/all.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: radial-gradient(ellipse at top, #1e293b 0%, #0f172a 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }

        .hero-title {
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            font-size: clamp(2rem, 5vw, 3.5rem);
            background: linear-gradient(135deg, #fff 0%, #94a3b8 100%);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 0.5rem;
        }

        .hero-sub {
            color: #64748b;
            font-size: 1.1rem;
            text-align: center;
            margin-bottom: 3.5rem;
            font-weight: 500;
        }

        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            max-width: 960px;
            width: 100%;
        }

        .sector-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 24px;
            padding: 2.5rem 2rem;
            text-align: center;
            text-decoration: none;
            color: white;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(12px);
            cursor: pointer;
            display: block;
        }

        .sector-card:hover {
            transform: translateY(-8px);
            border-color: rgba(255,255,255,0.3);
            background: rgba(255,255,255,0.1);
            box-shadow: 0 25px 50px rgba(0,0,0,0.4);
            text-decoration: none;
            color: white;
        }

        .sector-icon {
            font-size: 2.5rem;
            width: 80px;
            height: 80px;
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1.5rem;
        }

        .icon-banking    { background: linear-gradient(135deg, #6366f1, #8b5cf6); }
        .icon-energie    { background: linear-gradient(135deg, #f59e0b, #ef4444); }
        .icon-assurance  { background: linear-gradient(135deg, #8b5cf6, #ec4899); }

        .sector-name {
            font-family: 'Outfit', sans-serif;
            font-size: 1.4rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }

        .sector-desc {
            font-size: 0.9rem;
            color: #94a3b8;
            line-height: 1.5;
            margin-bottom: 1.5rem;
        }

        .sector-badge {
            display: inline-block;
            padding: 0.35rem 1rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }

        .badge-live   { background: rgba(16, 185, 129, 0.2); color: #10b981; }
        .badge-dev    { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }

        .footer {
            margin-top: 3rem;
            color: #334155;
            font-size: 0.8rem;
            text-align: center;
        }
    </style>
</head>
<body>

    <h1 class="hero-title">Sénégal Analytics Platform</h1>
    <p class="hero-sub">Plateforme d'Analyse Multi-Secteurs — Données BCEAO | SENELEC | CIMA</p>

    <div class="cards-grid">

        <!-- Secteur Bancaire -->
        <a href="/banking/" class="sector-card">
            <div class="sector-icon icon-banking">
                <i class="fas fa-landmark" style="color:white; font-size:1.8rem;"></i>
            </div>
            <div class="sector-name">Secteur Bancaire</div>
            <div class="sector-desc">
                Analyse des bilans, ratios prudentiels et benchmarks des établissements
                bancaires au Sénégal. Données BCEAO 2015–2022.
            </div>
            <span class="sector-badge badge-live">● En ligne</span>
        </a>

        <!-- Secteur Énergie -->
        <a href="/energie/" class="sector-card">
            <div class="sector-icon icon-energie">
                <i class="fas fa-bolt" style="color:white; font-size:1.8rem;"></i>
            </div>
            <div class="sector-name">Secteur Énergétique</div>
            <div class="sector-desc">
                Suivi de la production, distribution et investissements énergétiques.
                Données SENELEC / PETROSEN.
            </div>
            <span class="sector-badge badge-dev">⚙ En développement</span>
        </a>

        <!-- Secteur Assurance -->
        <a href="/assurance/" class="sector-card">
            <div class="sector-icon icon-assurance">
                <i class="fas fa-shield-alt" style="color:white; font-size:1.8rem;"></i>
            </div>
            <div class="sector-name">Secteur Assurance</div>
            <div class="sector-desc">
                Analyse des primes émises, sinistres et capitaux gérés par les compagnies
                d'assurance. Données CIMA / FANAF.
            </div>
            <span class="sector-badge badge-dev">⚙ En développement</span>
        </a>

    </div>

    <div class="footer">
        Projet Big Data — Master 2 | Sources : BCEAO, SENELEC, CIMA | &copy; 2022–2025
    </div>

</body>
</html>
"""

@app.route('/')
def home():
    """Page d'accueil avec navigation entre les 3 secteurs."""
    return render_template_string(HOME_PAGE)


if __name__ == '__main__':
    print("🚀 Lancement de la Sénégal Analytics Platform...")
    print("   /          → Page d'accueil Multi-secteurs")
    print("   /banking/  → Dashboard Bancaire (LIVE)")
    print("   /energie/  → Dashboard Énergie (stub)")
    print("   /assurance/→ Dashboard Assurance (stub)")
    app.run(debug=True, port=5000)
