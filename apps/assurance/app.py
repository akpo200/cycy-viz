from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px

def init_assurance_app(flask_server):
    """
    Dashboard Dash — Secteur Assurance (Sénégal).
    Stub préparé pour intégration future des données CIMA / FANAF.
    Monté sur /assurance/ via Flask.
    """
    dash_app = Dash(
        __name__,
        server=flask_server,
        url_base_pathname='/assurance/',
        title="Insurance Intelligence Platform",
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://use.fontawesome.com/releases/v5.15.4/css/all.css"
        ],
        suppress_callback_exceptions=True
    )

    # Graphique placeholder
    fig_placeholder = px.bar(
        x=["SAAR", "NSIA", "SONAM", "AXA SENEGAL", "SAHAM"],
        y=[28500, 24300, 19700, 15200, 11800],
        title="Primes Émises par Compagnie d'Assurance (données illustratives, M FCFA)",
        color_discrete_sequence=["#8b5cf6"]
    )
    fig_placeholder.update_layout(
        template="plotly_white",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Plus Jakarta Sans'},
        xaxis={'title': ''},
        yaxis={'title': 'M FCFA'}
    )

    dash_app.layout = html.Div([

        # Header
        html.Div([
            dbc.Container([
                html.Div([
                    html.H1("Insurance Intelligence Platform", className="text-center",
                            style={"fontFamily": "Outfit, sans-serif", "fontWeight": "800",
                                   "fontSize": "2.5rem", "color": "white"}),
                    html.P("Analyse du Secteur Assurance au Sénégal",
                           className="text-center mb-0",
                           style={"color": "#c4b5fd", "fontWeight": "500"}),
                ])
            ])
        ], style={
            "background": "radial-gradient(circle at top left, #4c1d95 0%, #1e1b4b 100%)",
            "padding": "4rem 0", "marginBottom": "-3rem"
        }),

        dbc.Container([

            html.Div([
                html.H4("Indicateurs Clés — Secteur Assurance",
                        style={"fontFamily": "Outfit", "fontWeight": "700",
                               "marginTop": "4rem", "marginBottom": "2rem",
                               "color": "#1e1b4b"}),
                dbc.Row([
                    dbc.Col(dbc.Card([dbc.CardBody([
                        html.H5("Primes Émises (M FCFA)", style={"fontSize": "0.75rem",
                                                                   "textTransform": "uppercase",
                                                                   "color": "#64748b"}),
                        html.H3("186 420 M", style={"fontWeight": "800", "color": "#1e1b4b"})
                    ])], style={"borderRadius": "20px", "border": "none",
                                "boxShadow": "0 10px 25px rgba(0,0,0,0.05)",
                                "textAlign": "center", "padding": "1rem"}),
                        lg=3, md=6, className="mb-4"),

                    dbc.Col(dbc.Card([dbc.CardBody([
                        html.H5("Sinistres Réglés (M FCFA)", style={"fontSize": "0.75rem",
                                                                     "textTransform": "uppercase",
                                                                     "color": "#64748b"}),
                        html.H3("98 750 M", style={"fontWeight": "800", "color": "#1e1b4b"})
                    ])], style={"borderRadius": "20px", "border": "none",
                                "boxShadow": "0 10px 25px rgba(0,0,0,0.05)",
                                "textAlign": "center", "padding": "1rem"}),
                        lg=3, md=6, className="mb-4"),

                    dbc.Col(dbc.Card([dbc.CardBody([
                        html.H5("Ratio Combiné (%)", style={"fontSize": "0.75rem",
                                                             "textTransform": "uppercase",
                                                             "color": "#64748b"}),
                        html.H3("87.4 %", style={"fontWeight": "800", "color": "#8b5cf6"})
                    ])], style={"borderRadius": "20px", "border": "none",
                                "boxShadow": "0 10px 25px rgba(0,0,0,0.05)",
                                "textAlign": "center", "padding": "1rem"}),
                        lg=3, md=6, className="mb-4"),

                    dbc.Col(dbc.Card([dbc.CardBody([
                        html.H5("Capitaux Gérés (M FCFA)", style={"fontSize": "0.75rem",
                                                                    "textTransform": "uppercase",
                                                                    "color": "#64748b"}),
                        html.H3("412 600 M", style={"fontWeight": "800", "color": "#10b981"})
                    ])], style={"borderRadius": "20px", "border": "none",
                                "boxShadow": "0 10px 25px rgba(0,0,0,0.05)",
                                "textAlign": "center", "padding": "1rem"}),
                        lg=3, md=6, className="mb-4"),
                ]),
            ]),

            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=fig_placeholder, config={'displayModeBar': False})
                ])
            ], style={"borderRadius": "24px", "border": "none",
                      "boxShadow": "0 10px 25px rgba(0,0,0,0.05)", "marginBottom": "3rem"}),

            dbc.Alert([
                html.I(className="fas fa-tools mr-2"),
                " Module en cours de développement — Intégration des données CIMA / FANAF prévue."
            ], color="primary", className="text-center mb-5")

        ], fluid=False)
    ], style={"fontFamily": "Plus Jakarta Sans, sans-serif", "backgroundColor": "#f5f3ff"})

    return dash_app
