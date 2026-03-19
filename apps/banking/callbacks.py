from dash import Input, Output, State, dcc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import get_banking_data
from utils.map_utils import create_senegal_map
from fpdf import FPDF
import time

def register_callbacks(dash_app):
    """
    Enregistre tous les callbacks du Dashboard Bancaire :
    1. update_dashboard : KPIs, ratios, graphiques — réagit aux 3 filtres (banque, année, indicateur)
    2. update_map       : Carte Sénégal — réagit au filtre banque
    3. generate_report  : Génération et téléchargement du rapport PDF
    """

    # Chargement unique des données au démarrage de l'app
    df_full = get_banking_data()

    # Palette de couleurs premium
    COLORS = {
        'primary':  '#0f172a',
        'accent':   '#6366f1',
        'success':  '#10b981',
        'palette':  ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e',
                     '#f59e0b', '#10b981', '#06b6d4', '#3b82f6']
    }

    # ===========================================================================
    # CALLBACK 1 — KPIs, Ratios & Graphiques
    # Réagit aux 3 filtres : banque, année, indicateur maître
    # ===========================================================================
    @dash_app.callback(
        [Output('kpi-actif',         'children'),
         Output('kpi-credits',       'children'),
         Output('kpi-depots',        'children'),
         Output('kpi-resultat',      'children'),
         Output('ratio-solvabilite', 'children'),
         Output('ratio-roe',         'children'),
         Output('ratio-roa',         'children'),
         Output('ratio-liquidite',   'children'),
         Output('main-trend-graph',  'figure'),
         Output('market-share-pie',  'figure')],
        [Input('bank-filter', 'value'),
         Input('year-filter', 'value'),     # NOUVEAU filtre année
         Input('kpi-filter',  'value')]
    )
    def update_dashboard(bank, year, kpi_type):
        """
        Recalcule KPIs, ratios et graphiques selon les 3 filtres sélectionnés.
        L'année filtre les données historiques de l'Excel (2015-2020) + backup 2022.
        """
        try:
            df = df_full.copy()

            if df.empty:
                empty_fig = px.scatter(title="Base de données vide")
                return ["---"] * 8 + [empty_fig, empty_fig]

            # --- Application des filtres ---
            # Filtre par banque
            if bank and bank != "Toutes les banques":
                df = df[df['Sigle'] == bank]

            # Filtre par année
            if year and year != "Toutes" and 'ANNEE' in df.columns:
                df = df[df['ANNEE'] == int(year)]

            if df.empty:
                empty_fig = px.scatter(title="Aucune donnée pour cette sélection")
                return ["N/A"] * 8 + [empty_fig, empty_fig]

            # --- Calcul des agrégats ---
            bilan      = pd.to_numeric(df['BILAN'],        errors='coerce').fillna(0).sum()
            emploi     = pd.to_numeric(df['EMPLOI'],       errors='coerce').fillna(0).sum()
            ressources = pd.to_numeric(df['RESSOURCES'],   errors='coerce').fillna(0).sum()
            resultat   = pd.to_numeric(df['RESULTAT.NET'], errors='coerce').fillna(0).sum()

            if 'FONDS.PROPRE' in df.columns:
                fp = pd.to_numeric(df['FONDS.PROPRE'], errors='coerce').fillna(0).sum()
            else:
                fp = 0

            # --- Ratios prudentiels ---
            solv = (fp / bilan * 100)       if bilan > 0  else 0
            roe  = (resultat / fp * 100)    if fp > 0     else 0
            roa  = (resultat / bilan * 100) if bilan > 0  else 0
            liq  = (ressources / emploi)    if emploi > 0 else 0

            # --- Graphique barres — Top 10 (sur données complètes non filtrées par banque) ---
            # On prend df_full filtré uniquement par année pour garder le benchmark global
            df_bench = df_full.copy()
            if year and year != "Toutes" and 'ANNEE' in df_bench.columns:
                df_bench = df_bench[df_bench['ANNEE'] == int(year)]

            kpi_col = kpi_type if kpi_type in df_bench.columns else 'BILAN'
            df_bar = (
                df_bench.groupby('Sigle')[kpi_col]
                .sum()
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
            )

            # Label de l'année dans le titre
            year_label = f"— Année {year}" if (year and year != "Toutes") else "— Toutes années"
            fig_bar = px.bar(
                df_bar, x='Sigle', y=kpi_col,
                title=f"Top 10 — {kpi_col.replace('.', ' ')} {year_label}",
                color_discrete_sequence=[COLORS['accent']]
            )
            fig_bar.update_traces(marker_line_color='white', marker_line_width=2, opacity=0.9)
            fig_bar.update_layout(
                height=450, template="plotly_white",
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font={'family': 'Plus Jakarta Sans'},
                margin=dict(t=80, b=40, l=40, r=40),
                xaxis={'title': '', 'tickangle': -30},
                yaxis={'title': 'M FCFA', 'gridcolor': '#f1f5f9'},
                title={'font': {'size': 17, 'color': COLORS['primary']}}
            )

            # --- Camembert — Market share global (par année si filtrée) ---
            df_pie = df_bench.groupby('Sigle')['BILAN'].sum().reset_index()
            total = df_pie['BILAN'].sum()
            df_pie['Pct'] = (df_pie['BILAN'] / total * 100).round(2) if total > 0 else 0

            threshold = 3.0
            main_bk = df_pie[df_pie['Pct'] >= threshold].copy()
            others  = df_pie[df_pie['Pct'] < threshold]['BILAN'].sum()
            if others > 0:
                main_bk = pd.concat([main_bk, pd.DataFrame([{
                    'Sigle': f'Autres ({len(df_pie) - len(main_bk)} banques)',
                    'BILAN': others,
                    'Pct':   round(others / total * 100, 2)
                }])], ignore_index=True)

            fig_pie = px.pie(
                main_bk, names='Sigle', values='BILAN',
                title=f"Structure de l'Actif Bancaire {year_label}",
                hole=0.55, color_discrete_sequence=COLORS['palette']
            )
            fig_pie.update_traces(
                textposition='outside', textinfo='percent+label',
                pull=[0.05 if 'Autres' in str(s) else 0 for s in main_bk['Sigle']],
                marker=dict(line=dict(color='white', width=3))
            )
            fig_pie.update_layout(
                height=450, showlegend=False, template="plotly_white",
                font={'family': 'Plus Jakarta Sans'},
                margin=dict(t=80, b=40, l=40, r=40),
                title={'font': {'size': 17, 'color': COLORS['primary']}}
            )

            # Formatage milliers avec espace
            def fmt(v): return f"{v:,.0f} M".replace(',', ' ')

            return (
                fmt(bilan), fmt(emploi), fmt(ressources), fmt(resultat),
                f"{solv:.1f}%", f"{roe:.1f}%", f"{roa:.1f}%", f"{liq:.2f}",
                fig_bar, fig_pie
            )

        except Exception as e:
            print(f"ERREUR update_dashboard : {e}")
            import traceback; traceback.print_exc()
            err_fig = px.scatter(title=f"Erreur : {str(e)[:80]}")
            return ["Erreur"] * 8 + [err_fig, err_fig]

    # ===========================================================================
    # CALLBACK 2 — Carte interactive Sénégal (NOUVEAU)
    # Réaffiche la carte quand le filtre banque change
    # ===========================================================================
    @dash_app.callback(
        Output('map-senegal', 'figure'),
        [Input('bank-filter', 'value')]
    )
    def update_map(bank):
        """
        Génère la carte Plotly Scattermapbox du Sénégal.
        Si une banque est sélectionnée, met en surbrillance son emplacement.
        """
        try:
            df = df_full.copy()

            # On agrège par Sigle pour avoir une ligne par banque (le plus récent)
            if 'ANNEE' in df.columns:
                df_latest = (
                    df.sort_values('ANNEE', ascending=False)
                    .groupby('Sigle')
                    .first()
                    .reset_index()
                )
            else:
                df_latest = df.groupby('Sigle').first().reset_index()

            fig = create_senegal_map(df_latest)
            return fig

        except Exception as e:
            print(f"ERREUR update_map : {e}")
            return px.scatter(title=f"Carte indisponible : {e}")

    # ===========================================================================
    # CALLBACK 3 — Génération du rapport PDF
    # ===========================================================================
    @dash_app.callback(
        [Output("download-pdf-report", "data"),
         Output("report-status",        "children")],
        [Input("btn-export-pdf",        "n_clicks")],
        [State("bank-filter",           "value"),
         State("year-filter",           "value")],   # Inclure l'année dans le rapport
        prevent_initial_call=True
    )
    def generate_report(n_clicks, bank, year):
        """
        Génère un rapport PDF (banque individuelle ou secteur consolidé).
        Utilise la police Arial TTF (Unicode complet) pour tous les accents français.
        """
        try:
            df = df_full.copy()

            # --- Filtrage selon la sélection ---
            if bank and bank != "Toutes les banques":
                df = df[df['Sigle'] == bank]
                titre_rapport = bank
            else:
                titre_rapport = "Secteur Bancaire Senegalais - Consolide"

            if year and year != "Toutes" and 'ANNEE' in df.columns:
                df = df[df['ANNEE'] == int(year)]
                titre_rapport += f" ({int(year)})"

            if df.empty:
                return None, f"Aucune donnée pour la sélection actuelle."

            # --- Calcul des indicateurs ---
            bilan      = pd.to_numeric(df['BILAN'],        errors='coerce').fillna(0).sum()
            emploi     = pd.to_numeric(df['EMPLOI'],       errors='coerce').fillna(0).sum()
            ressources = pd.to_numeric(df['RESSOURCES'],   errors='coerce').fillna(0).sum()
            resultat   = pd.to_numeric(df['RESULTAT.NET'], errors='coerce').fillna(0).sum()
            fp = pd.to_numeric(df.get('FONDS.PROPRE', pd.Series([0])), errors='coerce').fillna(0).sum() \
                 if 'FONDS.PROPRE' in df.columns else 0

            solv = (fp / bilan * 100)       if bilan > 0  else 0
            roe  = (resultat / fp * 100)    if fp > 0     else 0
            roa  = (resultat / bilan * 100) if bilan > 0  else 0
            liq  = (ressources / emploi)    if emploi > 0 else 0

            # --- Nombre de banques dans la sélection ---
            nb_banques = df['Sigle'].nunique() if 'Sigle' in df.columns else 1

            # =================================================================
            # Construction PDF avec fpdf2 + police Arial Unicode
            # =================================================================
            pdf = FPDF()
            try:
                pdf.add_font("Arial",  "",  "C:/Windows/Fonts/arial.ttf")
                pdf.add_font("Arial",  "B", "C:/Windows/Fonts/arialbd.ttf")
                pdf.add_font("Arial",  "I", "C:/Windows/Fonts/ariali.ttf")
                FONT = "Arial"
            except Exception:
                FONT = "helvetica"

            pdf.add_page()

            # En-tête ardoise
            pdf.set_fill_color(15, 23, 42)
            pdf.rect(0, 0, 210, 55, 'F')
            pdf.set_text_color(255, 255, 255)
            pdf.set_font(FONT, 'B', 20)
            pdf.set_y(13)
            pdf.cell(0, 10, "RAPPORT D'EXPERTISE BANCAIRE",
                     new_x="LMARGIN", new_y="NEXT", align='C')
            pdf.set_font(FONT, '', 10)
            pdf.cell(0, 7, f"Source : BCEAO | Genere le {time.strftime('%d/%m/%Y a %H:%M')}",
                     new_x="LMARGIN", new_y="NEXT", align='C')
            pdf.set_font(FONT, 'B', 13)
            pdf.set_text_color(163, 190, 221)
            pdf.cell(0, 9, titre_rapport.upper(),
                     new_x="LMARGIN", new_y="NEXT", align='C')
            pdf.ln(20)

            # Contexte
            pdf.set_text_color(100, 116, 139)
            pdf.set_font(FONT, 'I', 10)
            if nb_banques > 1:
                pdf.cell(0, 8, f"Analyse consolidee de {nb_banques} etablissements bancaires",
                         new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)

            # Section 1 : Indicateurs financiers
            pdf.set_font(FONT, 'B', 14)
            pdf.set_text_color(99, 102, 241)
            pdf.cell(0, 10, "1. INDICATEURS FINANCIERS CLES",
                     new_x="LMARGIN", new_y="NEXT")
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)
            pdf.set_text_color(15, 23, 42)

            for label, valeur in [
                ("Total du Bilan",         f"{bilan:,.0f} M FCFA".replace(',', ' ')),
                ("Credits a la Clientele", f"{emploi:,.0f} M FCFA".replace(',', ' ')),
                ("Ressources / Depots",    f"{ressources:,.0f} M FCFA".replace(',', ' ')),
                ("Fonds Propres",          f"{fp:,.0f} M FCFA".replace(',', ' ')),
                ("Resultat Net",           f"{resultat:,.0f} M FCFA".replace(',', ' ')),
            ]:
                pdf.set_font(FONT, 'B', 11)
                pdf.cell(100, 9, f"  {label} :", border=0)
                pdf.set_font(FONT, '', 11)
                pdf.cell(80, 9, valeur, border=0, new_x="LMARGIN", new_y="NEXT")

            pdf.ln(8)

            # Section 2 : Ratios prudentiels
            pdf.set_font(FONT, 'B', 14)
            pdf.set_text_color(99, 102, 241)
            pdf.cell(0, 10, "2. RATIOS PRUDENTIELS (BALE II/III)",
                     new_x="LMARGIN", new_y="NEXT")
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)
            pdf.set_text_color(15, 23, 42)

            for label, valeur, note in [
                ("Solvabilite (FP / Actif Total)",      f"{solv:.2f}%", "Norme BCEAO : > 8%"),
                ("Rentabilite des Fonds Propres (ROE)", f"{roe:.2f}%",  "Resultat Net / Fonds Propres"),
                ("Rendement des Actifs (ROA)",          f"{roa:.2f}%",  "Resultat Net / Total Bilan"),
                ("Coefficient de Liquidite",            f"{liq:.3f}",   "Ressources / Credits accordes"),
            ]:
                pdf.set_font(FONT, 'B', 11)
                pdf.cell(110, 9, f"  {label} :", border=0)
                pdf.set_font(FONT, '', 11)
                pdf.cell(25, 9, valeur, border=0)
                pdf.set_font(FONT, 'I', 9)
                pdf.set_text_color(100, 116, 139)
                pdf.cell(0, 9, f"  ({note})", border=0, new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(15, 23, 42)

            pdf.ln(15)

            # Pied de page
            pdf.set_font(FONT, 'I', 8)
            pdf.set_text_color(148, 163, 184)
            pdf.multi_cell(0, 5,
                "Ce document presente une analyse automatique basee sur les donnees "
                "declaratives BCEAO (Rapport Annuel 2022). Il ne constitue pas un "
                "conseil en investissement. Toute reproduction est soumise a autorisation.")

            safe_name = "".join([c if c.isalnum() else "_" for c in titre_rapport])
            pdf_bytes = bytes(pdf.output())

            print(f"PDF genere : {len(pdf_bytes)} octets pour '{titre_rapport}'")
            return (
                dcc.send_bytes(pdf_bytes, f"Rapport_BCEAO_{safe_name}.pdf"),
                f"Rapport genere avec succes : {titre_rapport}"
            )

        except Exception as e:
            print(f"Erreur PDF : {e}")
            import traceback; traceback.print_exc()
            return None, f"Erreur technique : {str(e)}"
