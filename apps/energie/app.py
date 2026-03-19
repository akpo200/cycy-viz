from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px

def init_energie_app(flask_server):
    """
    Dashboard Dash — Secteur Énergétique (Sénégal).
    Stub préparé pour intégration future des données SENELEC / PETROSEN.
    Monté sur /energie/ via Flask.
    """
    dash_app = Dash(
        __name__,
        server=flask_server,
        url_base_pathname='/energie/',
        title="Energy Intelligence Platform",
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://use.fontawesome.com/releases/v5.15.4/css/all.css"
        ],
        suppress_callback_exceptions=True
    )

    # Graphique placeholder "en développement"
    fig_placeholder = px.bar(
        x=["SENELEC", "PETROSEN", "SAR", "ORYX", "TOTAL ENERGIE"],
        y=[450, 280, 190, 120, 95],
        title="Production & Distribution Énergétique (données illustratives)",
        color_discrete_sequence=["#f59e0b"]
    )
    fig_placeholder.update_layout(
        template="plotly_white",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Plus Jakarta Sans'},
        xaxis={'title': ''},
        yaxis={'title': 'GWh / M FCFA'}
    )

    dash_app.layout = html.Div([

        # Header
        html.Div([
            dbc.Container([
                html.Div([
                    html.H1("Energy Intelligence Platform", className="text-center",
                            style={"fontFamily": "Outfit, sans-serif", "fontWeight": "800",
                                   "fontSize": "2.5rem", "color": "white"}),
                    html.P("Analyse du Secteur Énergétique au Sénégal",
                           className="text-center mb-0",
                           style={"color": "#fcd34d", "fontWeight": "500"}),
                ])
            ])
        ], style={
            "background": "radial-gradient(circle at top left, #78350f 0%, #451a03 100%)",
            "padding": "4rem 0", "marginBottom": "-3rem"
        }),

        dbc.Container([

            # KPI Cards placeholder
            html.Div([
                html.H4("Indicateurs Clés — Secteur Énergie",
                        style={"fontFamily": "Outfit", "fontWeight": "700",
                               "marginTop": "4rem", "marginBottom": "2rem",
                               "color": "#451a03"}),
                dbc.Row([
                    dbc.Col(dbc.Card([dbc.CardBody([
                        html.H5("Production (GWh)", style={"fontSize": "0.75rem",
                                                            "textTransform": "uppercase",
                                                            "color": "#64748b"}),
                        html.H3("4 382 GWh", style={"fontWeight": "800", "color": "#451a03"})
                    ])], style={"borderRadius": "20px", "border": "none",
                                "boxShadow": "0 10px 25px rgba(0,0,0,0.05)",
                                "textAlign": "center", "padding": "1rem"}),
                        lg=3, md=6, className="mb-4"),

                    dbc.Col(dbc.Card([dbc.CardBody([
                        html.H5("Capacité Installée (MW)", style={"fontSize": "0.75rem",
                                                                    "textTransform": "uppercase",
                                                                    "color": "#64748b"}),
                        html.H3("1 247 MW", style={"fontWeight": "800", "color": "#451a03"})
                    ])], style={"borderRadius": "20px", "border": "none",
                                "boxShadow": "0 10px 25px rgba(0,0,0,0.05)",
                                "textAlign": "center", "padding": "1rem"}),
                        lg=3, md=6, className="mb-4"),

                    dbc.Col(dbc.Card([dbc.CardBody([
                        html.H5("Taux d'Électrification (%)", style={"fontSize": "0.75rem",
                                                                       "textTransform": "uppercase",
                                                                       "color": "#64748b"}),
                        html.H3("74.2 %", style={"fontWeight": "800", "color": "#f59e0b"})
                    ])], style={"borderRadius": "20px", "border": "none",
                                "boxShadow": "0 10px 25px rgba(0,0,0,0.05)",
                                "textAlign": "center", "padding": "1rem"}),
                        lg=3, md=6, className="mb-4"),

                    dbc.Col(dbc.Card([dbc.CardBody([
                        html.H5("Investissements (M FCFA)", style={"fontSize": "0.75rem",
                                                                    "textTransform": "uppercase",
                                                                    "color": "#64748b"}),
                        html.H3("285 000 M", style={"fontWeight": "800", "color": "#10b981"})
                    ])], style={"borderRadius": "20px", "border": "none",
                                "boxShadow": "0 10px 25px rgba(0,0,0,0.05)",
                                "textAlign": "center", "padding": "1rem"}),
                        lg=3, md=6, className="mb-4"),
                ]),
            ]),

            # Graphique placeholder
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=fig_placeholder, config={'displayModeBar': False})
                ])
            ], style={"borderRadius": "24px", "border": "none",
                      "boxShadow": "0 10px 25px rgba(0,0,0,0.05)", "marginBottom": "3rem"}),

            # Badge "En développement"
            dbc.Alert([
                html.I(className="fas fa-tools mr-2"),
                " Module en cours de développement — Intégration des données SENELEC, PETROSEN et CRSE prévue."
            ], color="warning", className="text-center mb-5")

        ], fluid=False)
    ], style={"fontFamily": "Plus Jakarta Sans, sans-serif", "backgroundColor": "#fffbeb"})

    return dash_app
