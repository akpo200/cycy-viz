"""
apps/hospitalier/callbacks.py
--------------------------
Tous les callbacks pour le dashboard bancaire :
1. switch_tab           : Basculer entre Vue Macro et Analyse Micro
2. update_macro         : KPIs + 5 graphiques Macro
3. update_micro         : KPIs + 4 graphiques Micro
4. generate_pdf_report  : Rapport PDF avec graphiques matplotlib
"""

from dash import Input, Output, State, dcc, html, callback_context, no_update
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.data_loader import get_hospitalier_data
from utils.map_utils import create_senegal_map
from utils.pdf_report import generate_full_report
import traceback
import base64

# Chargement unique des données au démarrage
df_full = get_hospitalier_data()

# Palette Premium Étendue (pour inclure de nombreuses Hôpitals)
PALETTE = ['#0f766e', '#10b981', '#10b981', '#ef4444',
           '#8b5cf6', '#06b6d4', '#f59e0b', '#3b82f6',
           '#a855f7', '#84cc16', '#eab308', '#14b8a6',
           '#fb923c', '#38bdf8', '#6366f1', '#ec4899',
           '#f43f5e', '#2dd4bf', '#a78bfa', '#fb7185']

# Styles de base Plotly (Thème Clair Premium)
# ON NE MET PAS 'font', 'legend' ou 'margin' ICI pour éviter les conflits Python "multiple values for keyword"
BASE_LAYOUT = dict(
    template="plotly_white",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
)

# Styles partagés Optionnels (à déstructurer explicitement si besoin)
_FONT = dict(family='Plus Jakarta Sans, Outfit, sans-serif', color='#334155', size=11)
_LEGEND = dict(bgcolor='rgba(0,0,0,0)', font=dict(size=10, color='#334155'))
_AXES = dict(
    xaxis=dict(gridcolor='#f1f5f9', showgrid=True, zeroline=False),
    yaxis=dict(gridcolor='#f1f5f9', showgrid=True, zeroline=False),
)
_MARGIN = dict(t=40, b=40, l=40, r=20)



def _filter_df(bank=None, year=None, group=None, focus=None):
    """
    Retourne une copie filtrée du DataFrame global.
    focus = Hôpital spécifique (pour Analyse Micro)
    """
    df = df_full.copy()

    # Filtre Groupe Bancaire
    if group and group != 'TOUS' and 'Goupe_Bancaire' in df.columns:
        df = df[df['Goupe_Bancaire'] == group]

    # Filtre Année
    if year and year != 'TOUTES' and 'ANNEE' in df.columns:
        df = df[df['ANNEE'] == int(year)]

    print(f"DEBUG FILTER: after year/group filters, len(df)={len(df)}")

    # Filtre Focus Hôpital (Analyse Micro uniquement)
    if focus and focus != 'TOUTES' and focus != 'TOUS':
        df_bank = df_full[df_full['Sigle'].str.upper() == str(focus).upper()]
        # Optionnel: on peut aussi filtrer df_bank par année si on veut restreindre l'historique
        return df, df_bank

    return df, df


def _fmt(v, force_millions=False):
    """Formatage M FCFA lisible. Unité source: Millions."""
    if force_millions:
        return f"{v:,.0f} M".replace(',', ' ')
    if abs(v) >= 1_000:
        return f"{v / 1_000:.1f} Md CFA"
    return f"{v:,.0f} M".replace(',', ' ')


def _calc_ratios(d):
    """Calcule les ratios prudentiels depuis un DataFrame."""
    bilan = pd.to_numeric(d['Bilan'], errors='coerce').fillna(0).sum()
    emploi = pd.to_numeric(d['Emploi'], errors='coerce').fillna(0).sum() if 'Emploi' in d.columns else 0
    ress = pd.to_numeric(d['Ressources'], errors='coerce').fillna(0).sum() if 'Ressources' in d.columns else 0
    res = pd.to_numeric(d['Resultat'], errors='coerce').fillna(0).sum() if 'Resultat' in d.columns else 0
    fp = pd.to_numeric(d['Fonds Propres'], errors='coerce').fillna(0).sum() if 'Fonds Propres' in d.columns else 0
    solv = (fp / bilan * 100) if bilan > 0 else 0
    roe = (res / fp * 100) if fp > 0 else 0
    roa = (res / bilan * 100) if bilan > 0 else 0
    lev = (bilan / fp) if fp > 0 else 0
    return dict(bilan=bilan, emploi=emploi, ress=ress, res=res,
                fp=fp, solv=solv, roe=roe, roa=roa, lev=lev)


def register_callbacks(dash_app):
    """Enregistre tous les callbacks du dashboard."""

    # ==========================================================================
    # CALLBACK 0 — Switcher d'onglets
    # ==========================================================================
    @dash_app.callback(
        [Output('tab-content-macro', 'style'),
         Output('tab-content-micro', 'style'),
         Output('tab-macro', 'className'),
         Output('tab-micro', 'className'),
         Output('active-tab', 'data')],
        [Input('tab-macro', 'n_clicks'),
         Input('tab-micro', 'n_clicks')]
    )
    def switch_tab(n_macro, n_micro):
        """Affiche/masque les contenus selon l'onglet cliqué."""
        ctx = callback_context
        if not ctx.triggered:
            return {'display': 'block'}, {'display': 'none'}, 'tab-btn active', 'tab-btn', 'macro'
        btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if btn_id == 'tab-macro':
            return {'display': 'block'}, {'display': 'none'}, 'tab-btn active', 'tab-btn', 'macro'
        else:
            return {'display': 'none'}, {'display': 'block'}, 'tab-btn', 'tab-btn active', 'micro'

    # ==========================================================================
    # CALLBACK 1 — VUE MACRO : KPIs + 5 Graphiques
    # ==========================================================================
    @dash_app.callback(
        [Output('kpi-bilan',          'children'),
         Output('kpi-bilan-growth',   'children'),
         Output('kpi-fp',             'children'),
         Output('kpi-ressources',     'children'),
         Output('kpi-nb-Hôpitals',     'children'),
         Output('macro-subtitle',     'children'),
         Output('fig-line-evolution', 'figure'),
         Output('fig-donut-marche',   'figure'),
         Output('fig-scatter-bilan',  'figure'),
         Output('fig-scatter-emploi', 'figure'),
         Output('fig-scatter-ressources', 'figure'),
         Output('fig-bar-classement', 'figure')],
        [Input('year-filter',  'value'),
         Input('group-filter', 'value')]
    )
    def update_macro(year, group):
        """Recalcule tous les éléments de la Vue Macro."""
        try:
            df, _ = _filter_df(year=year, group=group)
            year_label = str(int(year)) if year and year != 'TOUTES' else 'Toutes années'
            subtitle = f"Analyse consolidée du marché pour l'exercice {year_label}"

            if df.empty:
                ef = go.Figure().update_layout(**BASE_LAYOUT, font=_FONT)
                return ["N/A"] * 5 + [subtitle] + [ef] * 6

            r = _calc_ratios(df)
            nb_Hôpitals = df['Sigle'].nunique()

            # --- Croissance Lits Disponibles (vs année précédente) ---
            growth_txt = ""
            if 'ANNEE' in df_full.columns and year and year != 'TOUTES':
                prev_year = int(year) - 1
                df_prev = df_full[df_full['ANNEE'] == prev_year]
                if not df_prev.empty:
                    prev_bilan = pd.to_numeric(df_prev['Bilan'], errors='coerce').fillna(0).sum()
                    if prev_bilan > 0:
                        g = (r['bilan'] - prev_bilan) / prev_bilan * 100
                        growth_txt = f"+{g:.1f}%" if g >= 0 else f"{g:.1f}%"

            # ----------------------------------------------------------------
            # FIG 1 — Ligne Évolution sectorielle
            # ----------------------------------------------------------------
            fig_line = go.Figure()
            if 'ANNEE' in df_full.columns:
                grp = df_full.copy()
                if group and group != 'TOUS' and 'Goupe_Bancaire' in grp.columns:
                    grp = grp[grp['Goupe_Bancaire'] == group]
                evo = grp.groupby('ANNEE')[['Bilan', 'Ressources']].sum().reset_index().sort_values('ANNEE')
                fig_line.add_trace(go.Scatter(
                    x=evo['ANNEE'], y=evo['Bilan'] / 1_000,
                    name='Lits Disponibles Total', mode='lines+markers',
                    line=dict(color='#10b981', width=3),
                    marker=dict(size=8),
                    fill='tozeroy', fillcolor='rgba(217,119,6,0.05)'
                ))
                if 'Ressources' in evo.columns:
                    fig_line.add_trace(go.Scatter(
                        x=evo['ANNEE'], y=evo['Ressources'] / 1_000,
                        name='Budget', mode='lines+markers',
                        line=dict(color='#0f766e', width=2.5, dash='dot'),
                        marker=dict(size=7)
                    ))
            fig_line.update_layout(**BASE_LAYOUT, font=_FONT, **_AXES,
                yaxis_title='Milliards FCFA',
                margin=dict(t=30, b=40, l=50, r=20),
                title=dict(text='', font=dict(size=14))
            )
            fig_line.update_xaxes(tickmode='linear', dtick=1)

            # ----------------------------------------------------------------
            # FIG 2 — Donut parts de marché (groupés par Goupe_Bancaire si dispo)
            # ----------------------------------------------------------------
            group_col = 'Sigle' # On force le sigle pour voir toutes les Hôpitals individuellement
            pdm_df = df.groupby(group_col)['Bilan'].sum().reset_index()
            pdm_df.columns = ['Label', 'Bilan']
            pdm_df = pdm_df.sort_values('Bilan', ascending=False)
            
            fig_donut = go.Figure(go.Pie(
                labels=pdm_df['Label'],
                values=pdm_df['Bilan'],
                hole=0.6,
                marker=dict(colors=PALETTE,
                            line=dict(color='#ffffff', width=2)),
                textinfo='percent',
                textfont=dict(size=10),
                hovertemplate='<b>%{label}</b><br>Lits Disponibles : %{value:,.0f} M<br>Part : %{percent}<extra></extra>'
            ))
            fig_donut.add_annotation(
                text='MARCHÉ', showarrow=False,
                font=dict(size=12, family='Outfit', color='#64748b')
            )
            fig_donut.update_layout(**BASE_LAYOUT, font=_FONT, showlegend=True,
                legend=dict(orientation='v', x=1.0, y=0.5,
                            bgcolor='rgba(0,0,0,0)', font=dict(size=9)),
                margin=dict(t=20, b=20, l=10, r=80))

            # ----------------------------------------------------------------
            # TCAM helper (taux de croissance annuel moyen)
            # ----------------------------------------------------------------
            def compute_tcam(col):
                """Calcule le TCAM et la part de marché finale pour chaque Hôpital."""
                if 'ANNEE' not in df_full.columns or col not in df_full.columns:
                    return pd.DataFrame(columns=['Sigle', 'PDM', 'TCAM'])
                g = (df_full.groupby(['Sigle', 'ANNEE'])[col]
                     .sum().reset_index().sort_values(['Sigle', 'ANNEE']))
                result = []
                for bank_name, d in g.groupby('Sigle'):
                    d = d.sort_values('ANNEE')
                    if len(d) >= 2:
                        v0, v1 = d[col].iloc[0], d[col].iloc[-1]
                        n = d['ANNEE'].iloc[-1] - d['ANNEE'].iloc[0]
                        tcam = ((v1 / v0) ** (1 / n) - 1) * 100 if v0 > 0 and n > 0 else 0
                    else:
                        tcam = 0
                    result.append({'Sigle': bank_name, 'Val': d[col].sum(), 'TCAM': tcam})
                res_df = pd.DataFrame(result)
                res_df['PDM'] = res_df['Val'] / res_df['Val'].sum() * 100
                return res_df

            def scatter_tcam(col, title_col):
                """Scatter TCAM vs PDM style Premium."""
                tcam_df = compute_tcam(col)
                if tcam_df.empty:
                    return go.Figure().update_layout(**BASE_LAYOUT, font=_FONT)
                fig_s = go.Figure()
                # Zone de croissance (quadrant haut-droit)
                fig_s.add_hrect(y0=0, y1=tcam_df['TCAM'].max()*1.1 or 5,
                                fillcolor='rgba(16,185,129,0.04)', line_width=0)
                fig_s.add_vrect(x0=tcam_df['PDM'].median(), x1=tcam_df['PDM'].max()*1.1,
                                fillcolor='rgba(16,185,129,0.04)', line_width=0)
                # Lignes de référence
                fig_s.add_hline(y=0, line_color='rgba(148,163,184,0.4)', line_dash='dot')
                fig_s.add_vline(x=tcam_df['PDM'].median(),
                                line_color='rgba(148,163,184,0.4)', line_dash='dot')
                # Points
                for _, row in tcam_df.iterrows():
                    col_pt = '#10b981' if row['TCAM'] > 0 and row['PDM'] > tcam_df['PDM'].median() else '#0f766e'
                    fig_s.add_trace(go.Scatter(
                        x=[row['PDM']], y=[row['TCAM']],
                        mode='markers+text',
                        marker=dict(size=max(6, min(row['PDM'] * 2.5, 22)),
                                    color=col_pt, opacity=0.8,
                                    line=dict(color='white', width=1)),
                        text=[row['Sigle']],
                        textposition='top center',
                        textfont=dict(size=8, color='#64748b'),
                        hovertemplate=f"<b>{row['Sigle']}</b><br>PDM : {row['PDM']:.1f}%<br>TCAM : {row['TCAM']:.1f}%<extra></extra>",
                        showlegend=False
                    ))
                fig_s.update_layout(**BASE_LAYOUT, font=_FONT, **_AXES,
                    xaxis_title='Part de marché (%)',
                    yaxis_title='TCAM 2015-2022 (%)',
                    margin=dict(t=20, b=40, l=50, r=20)
                )
                return fig_s

            fig_sc_bilan     = scatter_tcam('Bilan',     'Lits Disponibles')
            fig_sc_emploi    = scatter_tcam('Emploi',    'Patients Admis')
            fig_sc_ressources = scatter_tcam('Ressources', 'Budget')

            # --- Classement horizontal ---
            rank = (df.groupby('Sigle')['Bilan']
                      .sum().sort_values(ascending=True).tail(12))
            fig_rank = go.Figure(go.Bar(
                x=rank.values / 1_000,
                y=rank.index,
                orientation='h',
                marker=dict(
                    color=rank.values,
                    colorscale=[[0, '#0f766e'], [1, '#10b981']],
                    line=dict(width=0)
                ),
                hovertemplate='<b>%{y}</b><br>%{x:,.0f} K FCFA<extra></extra>'
            ))
            fig_rank.update_layout(**BASE_LAYOUT, font=_FONT, **_AXES,
                xaxis_title='Total Lits Disponibles (Milliards FCFA)',
                margin=dict(t=20, b=40, l=80, r=20)
            )

            return (
                _fmt(r['bilan']), growth_txt,
                _fmt(r['fp']), _fmt(r['ress']),
                str(nb_Hôpitals), subtitle,
                fig_line, fig_donut,
                fig_sc_bilan, fig_sc_emploi, fig_sc_ressources,
                fig_rank
            )

        except Exception as e:
            traceback.print_exc()
            ef = go.Figure().update_layout(**BASE_LAYOUT,
                title=dict(text=f"Erreur : {str(e)[:60]}", font=dict(color='#f43f5e')))
            return ["Err"] * 5 + ["Erreur de chargement"] + [ef] * 6

    # ==========================================================================
    # CALLBACK 2 — ANALYSE MICRO
    # ==========================================================================
    @dash_app.callback(
        [Output('micro-title',              'children'),
         Output('micro-combo-title',        'children'),
         Output('micro-kpi-bilan',          'children'),
         Output('micro-kpi-resultat',       'children'),
         Output('micro-kpi-fp',             'children'),
         Output('micro-kpi-ressources',     'children'),
         Output('micro-ratios-bars',        'children'),
         Output('micro-infos-complementaires', 'children'),
         Output('fig-combo-historique',     'figure'),
         Output('fig-radar-diagnostic',     'figure'),
         Output('fig-gauge-pdm',            'figure')],
        [Input('bank-filter',  'value'),
         Input('year-filter',  'value'),
         Input('group-filter', 'value')]
    )
    def update_micro(bank, year, group):
        """Recalcule tous les éléments de l'Analyse Micro pour la Hôpital choisie."""
        try:
            df, _ = _filter_df(year=year, group=group, focus=None) # df for sector calculation
            print(f"DEBUG MICRO: bank={bank}, year={year}, group={group}")

            # On prend TOUTE l'histoire de la Hôpital pour les graphiques,
            # mais on filtre l'année pour les KPIs
            df_bank_all = df_full[df_full['Sigle'].str.upper() == str(bank).upper()]
            
            if df_bank_all.empty:
                print(f"⚠ Analyse Micro : Aucune donnée trouvée pour {bank}")
                ef = go.Figure().update_layout(**BASE_LAYOUT, font=_FONT)
                return ["ANALYSE MICRO", "Aucune donnée", "N/A", "N/A", "N/A", "N/A", [], "Hôpital inconnue", ef, ef, ef]

            # Filtrage de l'année pour les KPIs
            df_bank_year = df_bank_all.copy()
            if year and year != 'TOUTES':
                df_bank_year = df_bank_all[df_bank_all['ANNEE'] == int(year)]
            
            # Si vide pour cette année, on prend le plus récent
            if df_bank_year.empty:
                df_bank_year = df_bank_all.sort_values('ANNEE').tail(1)
            
            r_bank = _calc_ratios(df_bank_year)
            # Utilisation du DataFrame filtré pour le calcul du secteur
            r_sect = _calc_ratios(df) 
            title = f"ANALYSE MICRO — FOCUS SUR {str(bank).upper()}"
            combo_title = f"Historique des Capacités | {str(bank)}"

            # --- KPIs (Unité: Md CFA pour Lits Disponibles, M CFA pour Résultat) ---
            bilan_val = _fmt(r_bank['bilan'])
            res_val = _fmt(r_bank['res'], force_millions=True)
            fp_val = _fmt(r_bank['fp'])
            ress_val = _fmt(r_bank['ress'])

            # Infos complémentaires (Groupe, Effectif…)
            bank_row = df_bank_year.iloc[-1] if not df_bank_year.empty else pd.Series()
            group_val = bank_row.get('Goupe_Bancaire', 'N/A')
            effectif_val = bank_row.get('EFFECTIF', 'N/A')
            try:
                effectif_val = str(int(effectif_val)) if effectif_val != 'N/A' else 'N/A'
            except Exception:
                effectif_val = str(effectif_val)

            infos = html.Div([
                html.Table([
                    html.Tr([html.Td("Groupe :", className="info-label"),
                             html.Td(str(group_val), className="info-value")]),
                    html.Tr([html.Td("Effectif :", className="info-label"),
                             html.Td(effectif_val, className="info-value")]),
                    html.Tr([html.Td("Siège :", className="info-label"),
                             html.Td("Dakar, Sénégal", className="info-value")]),
                    html.Tr([html.Td("Part de Marché :", className="info-label"),
                             html.Td(f"{r_bank['bilan']/r_sect['bilan']*100:.1f}% du Lits Disponibles" if r_sect['bilan'] > 0 else "N/A",
                                     className="info-value kpi-gold")]),
                ], className="info-table")
            ])

            # Barres de ratios
            def ratio_bar(label, value, avg, unit='%', color=None):
                pct = min(abs(value) * 3, 100) # Échelle augmentée pour visibilité
                return html.Div([
                    html.Div([
                        html.Span(label, className="ratio-name"),
                        html.Span(f"{value:.1f}{unit}", className="ratio-val")
                    ], className="ratio-label-group"),
                    html.Div([
                        html.Div(style={"width": f"{pct}%"}, className="ratio-bar-fill")
                    ], className="ratio-bar-bg"),
                    html.Div(f"Moyenne secteur : {avg:.1f}{unit}", className="ratio-avg")
                ], className="ratio-container")

            ratios_ui = html.Div([
                ratio_bar("SOLVABILITÉ", r_bank['solv'], r_sect['solv'], '%'),
                ratio_bar("ROE (RENTABILITÉ)", r_bank['roe'], r_sect['roe'], '%'),
                ratio_bar("LEVIER FINANCIER", r_bank['lev'], r_sect['lev'], 'x'),
            ], style={"padding": "0.5rem"})

            # ----------------------------------------------------------------
            # FIG Combo Historique (Barre Lits Disponibles + Ligne Résultat Net)
            # ----------------------------------------------------------------
            df_hist = df_bank_all.copy()
            fig_combo = go.Figure()
            if 'ANNEE' in df_hist.columns:
                hist = (df_hist.groupby('ANNEE')[['Bilan', 'Resultat']]
                        .sum().reset_index().sort_values('ANNEE'))
                # Barres Lits Disponibles
                fig_combo.add_trace(go.Bar(
                    x=hist['ANNEE'].astype(int),
                    y=hist['Bilan'] / 1_000,
                    name='Lits Disponibles (Md)',
                    marker=dict(color='#0f766e', opacity=0.8, line=dict(width=0))
                ))
                # Ligne Résultat Net (axe secondaire)
                fig_combo.add_trace(go.Scatter(
                    x=hist['ANNEE'].astype(int),
                    y=hist['Resultat'], # On garde en Millions pour plus de détail
                    name='Résultat Net (M)',
                    yaxis='y2',
                    mode='lines+markers',
                    line=dict(color='#10b981', width=2.5),
                    marker=dict(size=8)
                ))
            fig_combo.update_layout(
                **BASE_LAYOUT, font=_FONT,
                yaxis=dict(title='Lits Disponibles (Milliards FCFA)', gridcolor='#f1f5f9',
                           zeroline=False),
                yaxis2=dict(title='Résultat Net (Millions FCFA)', overlaying='y', side='right',
                             gridcolor='rgba(0,0,0,0)', zeroline=False),
                xaxis=dict(title='Année', tickmode='linear',
                           gridcolor='#f1f5f9', zeroline=False),
                barmode='group',
                margin=dict(t=30, b=40, l=50, r=50),
                legend=dict(orientation='h', y=1.1, x=0.5, xanchor='center')
            )

            # ----------------------------------------------------------------
            # FIG Radar diagnostic (Solvabilité, ROE, ROA, Levier)
            # ----------------------------------------------------------------
            categories_radar = ['Solvabilité', 'ROE', 'ROA×10', 'Levier÷10']

            def norm(val, scale=1):
                return min(abs(val) * scale, 100)

            bank_vals = [norm(r_bank['solv'], 3), norm(r_bank['roe'], 2),
                         norm(r_bank['roa'], 20), norm(r_bank['lev'], 5)]
            sect_vals = [norm(r_sect['solv'], 3), norm(r_sect['roe'], 2),
                         norm(r_sect['roa'], 20), norm(r_sect['lev'], 5)]
            bank_vals += bank_vals[:1]
            sect_vals += sect_vals[:1]
            cats_closed = categories_radar + [categories_radar[0]]

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=bank_vals, theta=cats_closed, fill='toself',
                name=bank, line=dict(color='#f59e0b', width=2.5),
                marker=dict(size=8),
                fillcolor='rgba(245,158,11,0.15)'
            ))
            fig_radar.add_trace(go.Scatterpolar(
                r=sect_vals, theta=cats_closed, fill='toself',
                name='Moy. Secteur', line=dict(color='#94a3b8', width=1.5, dash='dot'),
                fillcolor='rgba(148,163,184,0.08)'
            ))
            fig_radar.update_layout(
                **BASE_LAYOUT, font=_FONT,
                polar=dict(
                    bgcolor='rgba(0,0,0,0)',
                    radialaxis=dict(visible=True, range=[0, 100],
                                   gridcolor='#e2e8f0',
                                   tickfont=dict(size=8, color='#64748b')),
                    angularaxis=dict(gridcolor='#e2e8f0',
                                     tickfont=dict(size=10, color='#334155'))
                ),
                legend=dict(orientation='h', y=-0.15, x=0.5, xanchor='center',
                            bgcolor='rgba(0,0,0,0)', font=dict(size=10, color='#334155')),
                margin=dict(t=30, b=60, l=30, r=30)
            )

            # ----------------------------------------------------------------
            # FIG Gauge Part de marché
            # ----------------------------------------------------------------
            pdm_val = r_bank['bilan'] / r_sect['bilan'] * 100 if r_sect['bilan'] > 0 else 0
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=pdm_val,
                number=dict(suffix="%", font=dict(size=28, color='#10b981')),
                gauge=dict(
                    axis=dict(range=[0, 30], tickcolor='#94a3b8',
                              tickfont=dict(size=8, color='#64748b')),
                    bar=dict(color='#10b981', thickness=0.4),
                    bgcolor='rgba(0,0,0,0)',
                    bordercolor='#e2e8f0',
                    steps=[
                        dict(range=[0, 5], color='#f8fafc'),
                        dict(range=[5, 15], color='#f1f5f9'),
                        dict(range=[15, 30], color='#e2e8f0'),
                    ]
                ),
                title=dict(text='Emprise Commerciale', font=dict(size=11, color='#64748b'))
            ))
            fig_gauge.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Plus Jakarta Sans', color='#334155'),
                margin=dict(t=30, b=10, l=20, r=20)
            )

            return (
                title, combo_title,
                _fmt(r_bank['bilan']), _fmt(r_bank['res']),
                _fmt(r_bank['fp']), _fmt(r_bank['ress']),
                ratios_ui, infos,
                fig_combo, fig_radar, fig_gauge
            )

        except Exception as e:
            traceback.print_exc()
            ef = go.Figure().update_layout(**BASE_LAYOUT,
                title=dict(text=f"Erreur Micro : {str(e)[:60]}", font=dict(color='#f43f5e')))
            return ["ERREUR", "—", "N/A", "N/A", "N/A", "N/A", [], [], ef, ef, ef]

    # ==========================================================================
    # CALLBACK 3 — Génération rapport PDF (via matplotlib)
    # ==========================================================================
    @dash_app.callback(
        [Output("download-pdf-report", "data"),
         Output("report-status",       "children")],
        [Input("btn-export-pdf",       "n_clicks")],
        [State("bank-filter",          "value"),
         State("year-filter",          "value")],
        prevent_initial_call=True
    )
    def generate_pdf_report(n_clicks, bank, year):
        """Génère le rapport PDF complet avec graphiques matplotlib."""
        try:
            df = df_full.copy()
            safe_bank = bank if bank and bank != 'TOUTES' else 'Secteur'
            safe_name = "".join([c if c.isalnum() else "_" for c in safe_bank])
            year_str = str(int(year)) if year and year != 'TOUTES' else "Toutes_annees"

            print(f"✅ Génération PDF pour : {safe_bank} | {year_str}")
            pdf_bytes = generate_full_report(df, bank, year)
            filename = f"Rapport_HOSPITALIER_{safe_name}_{year_str}.pdf"
            # Encodage Base64 manuel pour assurer la compatibilité totale
            content_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # Retourne le dictionnaire de téléchargement Dash
            return (
                dict(content=content_b64, filename=filename, base64=True, type='application/pdf'),
                f"✓ Rapport prêt : {filename}"
            )

        except Exception as e:
            traceback.print_exc()
            return None, f"⚠ Erreur : {str(e)[:80]}"
