from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from .callbacks import register_callbacks
from utils.data_loader import get_banking_data

def init_banking_app(flask_server):
    """
    Initialise le dashboard Dash Bancaire (Mode Clair) avec :
    - Sidebar fixe à gauche
    - 2 onglets principaux : Vue Macro / Analyse Micro
    - Footer avec Copyright
    """
    df_init = get_banking_data()

    # --- Chargement Options dropdowns ---
    bank_options = [{'label': 'Toutes les banques', 'value': 'TOUTES'}]
    if not df_init.empty and 'Sigle' in df_init.columns:
        banks = sorted(df_init['Sigle'].dropna().unique())
        bank_options += [{'label': b, 'value': b} for b in banks]

    year_options = [{'label': 'Toutes les années', 'value': 'TOUTES'}]
    if not df_init.empty and 'ANNEE' in df_init.columns:
        years = sorted(df_init['ANNEE'].dropna().unique(), reverse=True)
        year_options += [{'label': int(y), 'value': int(y)} for y in years]

    group_options = [{'label': 'Tous les groupes', 'value': 'TOUS'}]
    if not df_init.empty and 'Goupe_Bancaire' in df_init.columns:
        groups = sorted(df_init['Goupe_Bancaire'].dropna().unique())
        group_options += [{'label': g, 'value': g} for g in groups]

    focus_default = bank_options[1]['value'] if len(bank_options) > 1 else 'TOUTES'

    dash_app = Dash(
        __name__,
        server=flask_server,
        url_base_pathname='/banking/',
        title="Banking Intelligence",
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://use.fontawesome.com/releases/v5.15.4/css/all.css"
        ],
        suppress_callback_exceptions=True
    )

    dash_app.layout = html.Div([

        dcc.Download(id="download-pdf-report"),

        # --- HEADER ---
        html.Header([
            html.Div([
                html.Div(html.I(className="fas fa-university"), className="header-icon"),
                html.Div([
                    html.H1("Banking Intelligence Platform"),
                    html.P("Performance & Solidité — Données Bancaires Sénégal"),
                ]),
            ], className="header-content")
        ], className="main-header"),

        # --- BODY WRAPPER ---
        html.Div([

            # --- SIDEBAR FIXE À GAUCHE ---
            html.Aside([
                html.Div([
                    html.Div(html.I(className="fas fa-layer-group"), className="sidebar-logo"),
                    html.H3("BCEAO INSIGHT", className="sidebar-title"),
                    html.P("Données Officielles", className="sidebar-subtitle"),
                ], className="sidebar-brand"),

                html.Label("Exercice d'Analyse", className="sidebar-label"),
                dcc.Dropdown(id='year-filter', options=year_options, value='TOUTES', clearable=False, className="sidebar-dropdown"),

                html.Label("Groupe Bancaire", className="sidebar-label"),
                dcc.Dropdown(id='group-filter', options=group_options, value='TOUS', clearable=False, className="sidebar-dropdown"),

                html.Label("Focus Établissement", className="sidebar-label"),
                dcc.Dropdown(id='bank-filter', options=[o for o in bank_options if o['value'] != 'TOUTES'], value=focus_default, clearable=False, className="sidebar-dropdown"),

                html.Div([
                    dcc.Loading(id="loading-pdf", type="circle", color="#4f46e5", children=[
                        dbc.Button([html.I(className="fas fa-file-pdf mr-2"), "Générer Rapport PDF"], id="btn-export-pdf", className="btn-sidebar-pdf w-100"),
                    ]),
                    html.Div(id="report-status", className="text-center mt-3", style={"fontSize": "0.7rem"})
                ], className="sidebar-pdf-block"),

            ], className="sidebar"),

            # --- CONTENU PRINCIPAL ---
            html.Main([
                
                # Navigation Onglets
                html.Div([
                    html.Button("VUE MACRO",     id="tab-macro",  n_clicks=0, className="tab-btn active"),
                    html.Button("ANALYSE MICRO", id="tab-micro",  n_clicks=0, className="tab-btn"),
                ], className="tab-bar"),

                dcc.Store(id='active-tab', data='macro'),

                # --- ONGLET 1: MACRO ---
                html.Div([
                    html.Div([
                        html.H2("Vue Macro du Secteur", className="section-heading"),
                        html.P(id="macro-subtitle", className="section-subheading"),
                    ], className="tab-header"),

                    dbc.Row([
                        dbc.Col(html.Div([html.Span("Bilan Total", className="kpi-label"), html.H3(id="kpi-bilan", className="kpi-value"), html.Span(id="kpi-bilan-growth", className="kpi-badge")], className="kpi-card"), md=3),
                        dbc.Col(html.Div([html.Span("Fonds Propres", className="kpi-label"), html.H3(id="kpi-fp", className="kpi-value")], className="kpi-card"), md=3),
                        dbc.Col(html.Div([html.Span("Ressources", className="kpi-label"), html.H3(id="kpi-ressources", className="kpi-value")], className="kpi-card"), md=3),
                        dbc.Col(html.Div([html.Span("Nb Banques", className="kpi-label"), html.H3(id="kpi-nb-banques", className="kpi-value")], className="kpi-card"), md=3),
                    ], className="g-3 mb-3"),

                    dbc.Row([
                        dbc.Col(html.Div([html.H5("Évolution du Bilan vs Ressources", className="graph-title"), dcc.Graph(id='fig-line-evolution', config={'displayModeBar': False})], className="graph-card"), md=8),
                        dbc.Col(html.Div([html.H5("Parts de Marché", className="graph-title"), dcc.Graph(id='fig-donut-marche', config={'displayModeBar': False})], className="graph-card"), md=4),
                    ], className="g-3 mb-3"),

                    dbc.Row([
                        dbc.Col(html.Div([html.H5("Positionnement (Bilan)", className="graph-title"), dcc.Graph(id='fig-scatter-bilan', config={'displayModeBar': False}, style={'height': '350px'})], className="graph-card"), md=4),
                        dbc.Col(html.Div([html.H5("Positionnement (Emplois)", className="graph-title"), dcc.Graph(id='fig-scatter-emploi', config={'displayModeBar': False}, style={'height': '350px'})], className="graph-card"), md=4),
                        dbc.Col(html.Div([html.H5("Positionnement (Ressources)", className="graph-title"), dcc.Graph(id='fig-scatter-ressources', config={'displayModeBar': False}, style={'height': '350px'})], className="graph-card"), md=4),
                    ], className="g-3 mb-3"),
                    
                    dbc.Row([
                        dbc.Col(html.Div([html.H5("Classement des Banques (Bilan)", className="graph-title"), dcc.Graph(id='fig-bar-classement', config={'displayModeBar': False}, style={'height': '400px'})], className="graph-card"), md=12),
                    ], className="g-3"),

                ], id="tab-content-macro", className="tab-content"),

                # --- ONGLET 2: MICRO ---
                html.Div([
                    html.Div([
                        html.H2(id="micro-title", className="section-heading"),
                        html.P("Analyse granulaire par banque individuelle", className="section-subheading"),
                    ], className="tab-header"),

                    dbc.Row([
                        dbc.Col(html.Div([html.Span("Bilan", className="kpi-label"), html.H3(id="micro-kpi-bilan", className="kpi-value")], className="kpi-card"), md=3),
                        dbc.Col(html.Div([html.Span("Résultat Net", className="kpi-label"), html.H3(id="micro-kpi-resultat", className="kpi-value")], className="kpi-card"), md=3),
                        dbc.Col(html.Div([html.Span("Fonds Propres", className="kpi-label"), html.H3(id="micro-kpi-fp", className="kpi-value")], className="kpi-card"), md=3),
                        dbc.Col(html.Div([html.Span("Ressources", className="kpi-label"), html.H3(id="micro-kpi-ressources", className="kpi-value")], className="kpi-card"), md=3),
                    ], className="g-3 mb-3"),

                    dbc.Row([
                        dbc.Col(html.Div([html.H5("Diagnostic de Solidité", className="graph-title"), html.Div(id="micro-ratios-bars")], className="graph-card"), md=5),
                        dbc.Col(html.Div([html.H5(id="micro-combo-title", className="graph-title"), dcc.Graph(id='fig-combo-historique', config={'displayModeBar': False}, style={'height': '350px'})], className="graph-card"), md=7),
                    ], className="g-3 mb-3"),

                    dbc.Row([
                        dbc.Col(html.Div([html.H5("Radar de Performance", className="graph-title"), dcc.Graph(id='fig-radar-diagnostic', config={'displayModeBar': False}, style={'height': '400px'})], className="graph-card"), md=7),
                        dbc.Col(html.Div([html.H5("Informations Clés", className="graph-title"), html.Div(id="micro-infos-complementaires"), html.Hr(), dcc.Graph(id='fig-gauge-pdm', config={'displayModeBar': False}, style={'height': '220px'})], className="graph-card"), md=5),
                    ], className="g-3")
                ], id="tab-content-micro", className="tab-content", style={"display": "none"}),

            ], className="main-content")
        ], className="dashboard-body"),

        # --- FOOTER ---
        html.Footer([
            html.P("Copyright © 2026 — Tous droits réservés. Créé par Nancy AKPO"),
        ], className="dashboard-footer")

    ], className="dashboard-wrapper")

    register_callbacks(dash_app)
    return dash_app
