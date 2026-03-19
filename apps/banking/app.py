from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from .callbacks import register_callbacks
from utils.data_loader import get_banking_data

def init_banking_app(flask_server):
    """
    Initialise le dashboard Dash Bancaire, monté sur /banking/ via Flask.
    Construit le layout complet avec filtres, KPIs, ratios, graphiques, carte et export PDF.
    """
    # --- Chargement initial pour alimenter les dropdowns ---
    df_init = get_banking_data()

    # Options dropdown : Institutions (banques)
    bank_options = [{'label': 'Toutes les banques', 'value': 'Toutes les banques'}]
    if not df_init.empty and 'Sigle' in df_init.columns:
        banks = sorted(df_init['Sigle'].unique())
        bank_options += [{'label': b, 'value': b} for b in banks]

    # Options dropdown : Années disponibles dans les données
    year_options = [{'label': 'Toutes les années', 'value': 'Toutes'}]
    if not df_init.empty and 'ANNEE' in df_init.columns:
        years = sorted(df_init['ANNEE'].dropna().unique(), reverse=True)
        year_options += [{'label': int(y), 'value': int(y)} for y in years]

    dash_app = Dash(
        __name__,
        server=flask_server,
        url_base_pathname='/banking/',
        title="Banking Intelligence Platform",
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://use.fontawesome.com/releases/v5.15.4/css/all.css"
        ],
        suppress_callback_exceptions=True
    )

    dash_app.layout = html.Div([

        # ===================================================================
        # HEADER — Titre principal
        # ===================================================================
        html.Div([
            dbc.Container([
                html.Div([
                    html.H1("Banking Intelligence Platform", className="text-center"),
                    html.P("Analyse Dynamique du Secteur Bancaire au Sénégal",
                           className="text-center mb-0"),
                ], className="header-content")
            ])
        ], className="main-header"),

        dbc.Container([

            # ===================================================================
            # SECTION FILTRES — 3 dropdowns : Institution, Année, Indicateur
            # ===================================================================
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([

                                # Filtre 1 : Institution (banque)
                                dbc.Col([
                                    html.Div([
                                        html.I(className="fas fa-university mr-2 text-primary"),
                                        html.Label("Institution",
                                                   className="text-muted small font-weight-bold uppercase")
                                    ]),
                                    dcc.Dropdown(
                                        id='bank-filter',
                                        options=bank_options,
                                        value='Toutes les banques',
                                        clearable=False,
                                        className="custom-dropdown"
                                    )
                                ], md=4, className="px-3"),

                                # Filtre 2 : Année (NOUVEAU)
                                dbc.Col([
                                    html.Div([
                                        html.I(className="fas fa-calendar-alt mr-2 text-primary"),
                                        html.Label("Année",
                                                   className="text-muted small font-weight-bold uppercase")
                                    ]),
                                    dcc.Dropdown(
                                        id='year-filter',
                                        options=year_options,
                                        value='Toutes',
                                        clearable=False,
                                        className="custom-dropdown"
                                    )
                                ], md=4, className="px-3 border-left"),

                                # Filtre 3 : Indicateur Maître
                                dbc.Col([
                                    html.Div([
                                        html.I(className="fas fa-chart-line mr-2 text-primary"),
                                        html.Label("Indicateur Maître",
                                                   className="text-muted small font-weight-bold uppercase")
                                    ]),
                                    dcc.Dropdown(
                                        id='kpi-filter',
                                        options=[
                                            {'label': 'Puissance du Bilan',       'value': 'BILAN'},
                                            {'label': 'Engagement Crédits',        'value': 'EMPLOI'},
                                            {'label': 'Capture des Dépôts',        'value': 'RESSOURCES'},
                                            {'label': 'Performance (Résultat Net)', 'value': 'RESULTAT.NET'},
                                        ],
                                        value='BILAN',
                                        clearable=False,
                                        className="custom-dropdown"
                                    )
                                ], md=4, className="px-3 border-left"),

                            ])
                        ])
                    ], className="filter-card shadow-lg")
                ], width=12)
            ], className="mt-n5"),

            # ===================================================================
            # KPIs — 4 indicateurs stratégiques
            # ===================================================================
            html.Div([
                html.H4("Indicateurs Stratégiques (M FCFA)", className="section-title"),
                dbc.Row([
                    dbc.Col(dbc.Card([dbc.CardBody([
                        html.H5("Actif Total"),
                        html.H3(id="kpi-actif")
                    ])], className="kpi-card"), lg=3, md=6, className="mb-4"),
                    dbc.Col(dbc.Card([dbc.CardBody([
                        html.H5("Prêts Clientèle"),
                        html.H3(id="kpi-credits")
                    ])], className="kpi-card"), lg=3, md=6, className="mb-4"),
                    dbc.Col(dbc.Card([dbc.CardBody([
                        html.H5("Ressources"),
                        html.H3(id="kpi-depots")
                    ])], className="kpi-card"), lg=3, md=6, className="mb-4"),
                    dbc.Col(dbc.Card([dbc.CardBody([
                        html.H5("Résultat Net"),
                        html.H3(id="kpi-resultat")
                    ])], className="kpi-card"), lg=3, md=6, className="mb-4"),
                ]),
            ], className="mb-5"),

            # Composant Dash pour déclencher le téléchargement PDF
            dcc.Download(id="download-pdf-report"),

            # ===================================================================
            # RATIOS — Expertise & indicateurs Bâlois
            # ===================================================================
            html.Div([
                html.H4("Expertise & Ratios Prudentiels", className="section-title"),
                dbc.Row([
                    dbc.Col(dbc.Card([dbc.CardBody([
                        html.H5("Solvabilité (FP/Bilan)"),
                        html.H4(id="ratio-solvabilite")
                    ])], className="kpi-card"), lg=3, md=6, className="mb-4"),
                    dbc.Col(dbc.Card([dbc.CardBody([
                        html.H5("Rentabilité (ROE)"),
                        html.H4(id="ratio-roe")
                    ])], className="kpi-card"), lg=3, md=6, className="mb-4"),
                    dbc.Col(dbc.Card([dbc.CardBody([
                        html.H5("Rendement (ROA)"),
                        html.H4(id="ratio-roa")
                    ])], className="kpi-card"), lg=3, md=6, className="mb-4"),
                    dbc.Col(dbc.Card([dbc.CardBody([
                        html.H5("Liquidité"),
                        html.H4(id="ratio-liquidite")
                    ])], className="kpi-card"), lg=3, md=6, className="mb-4"),
                ]),
            ], className="mb-5"),

            # ===================================================================
            # GRAPHIQUES — Benchmarks interbancaires
            # ===================================================================
            html.Div([
                html.H4("Benchmarks Interbancaires", className="section-title"),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-trophy mr-2"),
                                "Top 10 : Performance de l'Année"
                            ]),
                            dbc.CardBody([
                                dcc.Graph(id='main-trend-graph',
                                          config={'displayModeBar': False})
                            ])
                        ], className="graph-card")
                    ], lg=7, md=12),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.I(className="fas fa-chart-pie mr-2"),
                                "Market Share %"
                            ]),
                            dbc.CardBody([
                                dcc.Graph(id='market-share-pie',
                                          config={'displayModeBar': False})
                            ])
                        ], className="graph-card")
                    ], lg=5, md=12),
                ]),
            ], className="mb-4"),

            # ===================================================================
            # CARTE INTERACTIVE — Positionnement géographique (NOUVEAU)
            # ===================================================================
            html.Div([
                html.H4("Carte Interactive — Positionnement des Banques au Sénégal",
                        className="section-title"),
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-map-marker-alt mr-2"),
                        "Localisation des Sièges Sociaux à Dakar"
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id='map-senegal',
                                  config={'displayModeBar': True},
                                  style={'height': '480px'})
                    ])
                ], className="graph-card")
            ], className="mb-5"),

            # ===================================================================
            # EXPORT PDF — Bouton de téléchargement
            # ===================================================================
            dbc.Row([
                dbc.Col([
                    dcc.Loading(
                        id="loading-1",
                        type="default",
                        children=[
                            dbc.Button([
                                html.I(className="fas fa-file-pdf mr-3"),
                                "Générer le Rapport d'Analyse (PDF)"
                            ], color="dark", id="btn-export-pdf",
                               className="btn-premium w-100 py-3"),
                            html.Div(
                                "Sélectionnez une banque pour un rapport individuel, "
                                "ou laissez « Toutes les banques » pour un rapport consolidé du secteur.",
                                id="report-status",
                                className="text-center small text-muted mt-3"
                            )
                        ]
                    )
                ], lg={"size": 6, "offset": 3}, md=12, className="pb-5")
            ])

        ], fluid=False)
    ])

    register_callbacks(dash_app)
    return dash_app
