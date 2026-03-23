from flask import Flask, redirect, render_template_string
from apps.banking.app import init_banking_app
from apps.energie.app import init_energie_app
from apps.assurance.app import init_assurance_app
from apps.hospitalier.app import init_hospitalier_app

app = Flask(__name__)

dash_banking   = init_banking_app(app)
dash_energie   = init_energie_app(app)
dash_assurance = init_assurance_app(app)
dash_hospitalier = init_hospitalier_app(app)

HOME_PAGE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Cycy Viz — Projets de Data Visualisation</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;600;800&family=Plus+Jakarta+Sans:wght@400;500;700&display=swap" rel="stylesheet">
    <link href="https://use.fontawesome.com/releases/v5.15.4/css/all.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 4rem 2rem;
            background-image: radial-gradient(circle at 50% 0%, #1e293b 0%, transparent 70%);
        }
        .hero-title { font-family: 'Outfit', sans-serif; font-size: 3.5rem; font-weight: 800; margin-bottom: 0.5rem; text-align: center; background: linear-gradient(to right, #f8fafc, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .hero-sub { color: #64748b; font-size: 1.2rem; margin-bottom: 2rem; text-align: center; font-weight: 500; }
        .tech-stack { display: flex; gap: 1rem; margin-bottom: 5rem; flex-wrap: wrap; justify-content: center; }
        .tech-pill { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 0.5rem 1.2rem; border-radius: 99px; font-size: 0.85rem; color: #cbd5e1; display: flex; align-items: center; gap: 0.6rem; }
        .tech-pill i { color: #f59e0b; }
        .cards-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem; max-width: 1400px; width: 100%; margin-bottom: 6rem; }
        .sector-card {
            border-radius: 20px; padding: 2rem; text-decoration: none; color: inherit;
            display: flex; flex-direction: column; position: relative; overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .sector-card:hover { transform: translateY(-8px); box-shadow: 0 20px 40px rgba(0,0,0,0.4); }
        .card-hospitalier { background: #064e3b; border: 1px solid #047857; }
        .card-assurance { background: #2e1065; border: 1px solid #4c1d95; }
        .card-bancaire { background: #451a03; border: 1px solid #78350f; }
        .card-energie { background: #422006; border: 1px solid #78350f; }
        .sector-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
        .sector-icon {
            width: 50px; height: 50px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem;
        }
        .icon-hosp { background: #ecfdf5; color: #10b981; }
        .icon-assur { background: #f5f3ff; color: #8b5cf6; }
        .icon-bank { background: #fefce8; color: #eab308; }
        .icon-energ { background: #fff7ed; color: #f97316; }
        .sector-tag { font-size: 0.75rem; padding: 0.3rem 0.8rem; border-radius: 20px; font-weight: 600; opacity: 0.8; }
        .tag-hosp { background: rgba(16, 185, 129, 0.2); color: #34d399; }
        .tag-assur { background: rgba(139, 92, 246, 0.2); color: #a78bfa; }
        .tag-bank { background: rgba(234, 179, 8, 0.2); color: #fdd835; }
        .tag-energ { background: rgba(249, 115, 22, 0.2); color: #fdba74; }
        .sector-name { font-family: 'Outfit', sans-serif; font-size: 1.8rem; font-weight: 800; margin-bottom: 1rem; }
        .sector-desc { font-size: 0.9rem; color: #cbd5e1; line-height: 1.5; margin-bottom: 1.5rem; flex-grow: 1; }
        .pills { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 2rem; }
        .pill { font-size: 0.75rem; padding: 0.3rem 0.8rem; border-radius: 20px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); }
        .btn { padding: 0.8rem 1.5rem; border-radius: 30px; font-weight: 700; text-align: center; border: none; cursor: pointer; display: flex; justify-content: space-between; align-items: center; width: 100%; transition: opacity 0.3s; }
        .btn:hover { opacity: 0.9; }
        .btn-hosp { background: linear-gradient(135deg, #10b981, #059669); color: white; }
        .btn-assur { background: linear-gradient(135deg, #8b5cf6, #6d28d9); color: white; }
        .btn-bank { background: linear-gradient(135deg, #eab308, #ca8a04); color: white; }
        .btn-energ { background: linear-gradient(135deg, #f59e0b, #d97706); color: white; }
        .footer {
            color: #64748b;
            font-size: 0.9rem;
            text-align: center;
            padding: 4rem 0;
            border-top: 1px solid rgba(255,255,255,0.05);
            width: 100%;
        }
    </style>
</head>
<body>
    <h1 class="hero-title">Cycy Viz</h1>
    <p class="hero-sub">Projet de Data visualisation Master 2 Big Data et stratégie</p>
    
    <div class="tech-stack">
        <span class="tech-pill"><i class="fas fa-server"></i> Flask/Python</span>
        <span class="tech-pill"><i class="fas fa-chart-line"></i> Plotly Dash</span>
        <span class="tech-pill"><i class="fas fa-database"></i> MongoDB / Excel</span>
        <span class="tech-pill"><i class="fas fa-file-pdf"></i> PDF Export (FPDF2)</span>
    </div>

    <div class="cards-grid">
        <a href="/hospitalier/" class="sector-card card-hospitalier">
            <div class="sector-header">
                <div class="sector-icon icon-hosp"><i class="fas fa-hospital"></i></div>
                <div class="sector-tag tag-hosp">Healthcare Analytics</div>
            </div>
            <div class="sector-name">Hospitalier</div>
            <div class="sector-desc">Analyse des performances hospitalières : durée de séjour, pathologies, efficacité des départements et profils patients.</div>
            <div class="pills">
                <span class="pill">Durée de séjour</span><span class="pill">Taux de réadmission</span>
                <span class="pill">Pathologies</span><span class="pill">Inefficiencies</span>
            </div>
            <button class="btn btn-hosp">Ouvrir le dashboard <i class="fas fa-arrow-right"></i></button>
        </a>
        <a href="/assurance/" class="sector-card card-assurance">
            <div class="sector-header">
                <div class="sector-icon icon-assur"><i class="fas fa-shield-alt"></i></div>
                <div class="sector-tag tag-assur">Risk & Portfolio Analytics</div>
            </div>
            <div class="sector-name">Assurance</div>
            <div class="sector-desc">Pilotage du portefeuille assurance : fréquence/sévérité des sinistres, segmentation du risque, bonus-malus et rentabilité.</div>
            <div class="pills">
                <span class="pill">Loss Ratio</span><span class="pill">Charge Sinistres</span>
                <span class="pill">Segmentation Risque</span><span class="pill">Primes Totales</span>
            </div>
            <button class="btn btn-assur">Ouvrir le dashboard <i class="fas fa-arrow-right"></i></button>
        </a>
        <a href="/banking/" class="sector-card card-bancaire">
            <div class="sector-header">
                <div class="sector-icon icon-bank"><i class="fas fa-landmark"></i></div>
                <div class="sector-tag tag-bank">BCEAO Insight Dashboard</div>
            </div>
            <div class="sector-name">Bancaire</div>
            <div class="sector-desc">Suivi des performances bancaires au Sénégal : bilans, PNB, ratios de solvabilité, ROE/ROA et analyse comparative.</div>
            <div class="pills">
                <span class="pill">PNB</span><span class="pill">Ratio Solvabilité</span>
                <span class="pill">ROE / ROA</span><span class="pill">Résultat Net</span>
            </div>
            <button class="btn btn-bank">Ouvrir le dashboard <i class="fas fa-arrow-right"></i></button>
        </a>
        <a href="/energie/" class="sector-card card-energie">
            <div class="sector-header">
                <div class="sector-icon icon-energ"><i class="fas fa-sun"></i></div>
                <div class="sector-tag tag-energ">Solar Park Analytics</div>
            </div>
            <div class="sector-name">Énergie Solaire</div>
            <div class="sector-desc">Monitoring de la production photovoltaïque : rendement AC/DC, détection d'anomalies, analyse environnementale.</div>
            <div class="pills">
                <span class="pill">Production AC/DC</span><span class="pill">Taux Anomalies</span>
                <span class="pill">Facteur Capacité</span><span class="pill">Irradiation Moy.</span>
            </div>
            <button class="btn btn-energ">Ouvrir le dashboard <i class="fas fa-arrow-right"></i></button>
        </a>
    </div>

    <div class="footer">
        Copyright &copy; 2026 — Tous droits réservés. Créé par Nancy AKPO
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HOME_PAGE)

# Objet server exposé pour Gunicorn (Render)
server = app

if __name__ == '__main__':
    import os
    # Port dynamique pour Render, par défaut 5000
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Cycy Viz est en ligne sur le port {port}...")
    app.run(host='0.0.0.0', port=port)
