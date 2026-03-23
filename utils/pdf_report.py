"""
utils/pdf_report.py
-------------------
Génération du rapport PDF "notebook" style avec matplotlib.
Chaque section contient du texte + un graphique matplotlib exporté en image.
Utilise fpdf2 pour assembler le document final.
"""

import io
import time
import tempfile
import os

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Pas de fenêtre graphique — mode serveur
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from fpdf import FPDF


# ============================================================
# Palette de couleurs Premium (Mode Clair)
COLORS = {
    'primary': '#0f172a',
    'accent': '#4f46e5',
    'violet': '#8b5cf6',
    'gold': '#d97706',
    'success': '#10b981',
    'danger': '#ef4444',
    'palette': ['#4f46e5', '#d97706', '#10b981', '#ef4444',
                '#8b5cf6', '#06b6d4', '#f59e0b', '#3b82f6'],
    'bg': '#ffffff',
    'text': '#0f172a',
    'muted': '#64748b'
}


def _fmt(v):
    """Formate un nombre en M FCFA lisible. Unité source: Millions."""
    if abs(v) >= 1_000:
        return f"{v/1_000:.1f} Md"
    return f"{v:,.0f} M"


def _fig_to_png_bytes(fig) -> bytes:
    """Convertit une figure matplotlib en bytes PNG."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=130,
                bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def _tmp_png(png_bytes: bytes) -> str:
    """Sauvegarde bytes PNG dans un fichier temporaire, retourne le chemin."""
    f = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    f.write(png_bytes)
    f.close()
    return f.name


# ============================================================
# Graphiques matplotlib
# ============================================================

def make_evolution_chart(df: pd.DataFrame) -> bytes:
    """Ligne : Évolution du Total Bilan + Ressources par année."""
    plt.style.use('default')
    if 'ANNEE' not in df.columns:
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.text(0.5, 0.5, 'Données annuelles non disponibles',
                ha='center', va='center', color='white')
        return _fig_to_png_bytes(fig)

    evolution = (df.groupby('ANNEE')[['BILAN', 'RESSOURCES']]
                   .sum().reset_index().sort_values('ANNEE'))
    evolution['BILAN_B'] = evolution['BILAN'] / 1_000
    evolution['RESS_B'] = evolution['RESSOURCES'] / 1_000

    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor(COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])

    ax.plot(evolution['ANNEE'], evolution['BILAN_B'],
            'o-', color=COLORS['gold'], linewidth=2.5, markersize=7,
            label='Bilan Total')
    ax.plot(evolution['ANNEE'], evolution['RESS_B'],
            's--', color='#06b6d4', linewidth=2.5, markersize=7,
            label='Ressources')
    ax.fill_between(evolution['ANNEE'], evolution['BILAN_B'],
                    alpha=0.15, color=COLORS['gold'])

    ax.set_title('Évolution du Total Bilan du Secteur Bancaire Sénégalais',
                 color='white', fontsize=13, pad=12)
    ax.set_xlabel('Année', color='#94a3b8')
    ax.set_ylabel('Milliards FCFA', color='#94a3b8')
    ax.tick_params(colors='#94a3b8')
    ax.spines[['top', 'right']].set_visible(False)
    for spine in ['bottom', 'left']:
        ax.spines[spine].set_color('#334155')
    ax.grid(color='#334155', linestyle='--', linewidth=0.8, alpha=0.6)
    ax.xticks = evolution['ANNEE'].astype(int)
    ax.set_xticks(evolution['ANNEE'].astype(int))
    ax.legend(facecolor='#1e293b', edgecolor='#334155',
              labelcolor='white', fontsize=9)
    plt.tight_layout()
    return _fig_to_png_bytes(fig)


def make_classement_chart(df: pd.DataFrame, year) -> bytes:
    """Bar horizontal : classement des banques par Bilan."""
    plt.style.use('default')
    df_y = df.copy()
    if year and year != 'TOUTES' and 'ANNEE' in df.columns:
        df_y = df[df['ANNEE'] == int(year)]

    ranking = (df_y.groupby('Sigle')['BILAN']
                   .sum().sort_values(ascending=True).tail(15))

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor(COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])

    colors_bar = [COLORS['accent']] * len(ranking)
    if len(colors_bar) >= 1:
        colors_bar[-1] = COLORS['gold']

    bars = ax.barh(ranking.index, ranking.values / 1_000,
                   color=colors_bar, edgecolor='none', height=0.6)

    for bar in bars:
        w = bar.get_width()
        ax.text(w + w*0.01, bar.get_y() + bar.get_height()/2,
                f'{w:,.0f} K', va='center', color='#94a3b8', fontsize=8)

    ax.set_title('Classement des Banques par Total Bilan', color='white', fontsize=13)
    ax.set_xlabel('Total Bilan (Milliards FCFA)', color='#94a3b8')
    ax.tick_params(colors='#94a3b8')
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.spines['bottom'].set_color('#334155')
    ax.grid(axis='x', color='#334155', linestyle='--', linewidth=0.8, alpha=0.5)
    plt.tight_layout()
    return _fig_to_png_bytes(fig)


def make_radar_chart(df: pd.DataFrame, bank: str) -> bytes:
    """Radar : Solvabilité, ROE, ROA de la banque vs secteur."""
    plt.style.use('default')

    def _compute_ratios(d):
        bilan = pd.to_numeric(d['BILAN'], errors='coerce').fillna(0).sum()
        fp = pd.to_numeric(d.get('FONDS.PROPRE', pd.Series([0])), errors='coerce').fillna(0).sum() if 'FONDS.PROPRE' in d.columns else 0
        res = pd.to_numeric(d['RESULTAT.NET'], errors='coerce').fillna(0).sum()
        app_col = 'EMPLOI' if 'EMPLOI' in d.columns else 'RESSOURCES'
        emploi = pd.to_numeric(d[app_col], errors='coerce').fillna(0).sum()
        solv = (fp / bilan * 100) if bilan > 0 else 0
        roe  = (res / fp * 100) if fp > 0 else 0
        roa  = (res / bilan * 100) if bilan > 0 else 0
        levier = (bilan / fp) if fp > 0 else 0
        return [min(solv, 30), min(roe, 30), min(abs(roa)*10, 30), min(levier, 30)]

    bank_df = df[df['Sigle'] == bank]
    bank_ratios = _compute_ratios(bank_df)
    sector_ratios = _compute_ratios(df)

    categories = ['Solvabilité', 'ROE (Rentabilité)', 'ROA (Rendement)', 'Levier']
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    bank_vals = bank_ratios + bank_ratios[:1]
    sect_vals = sector_ratios + sector_ratios[:1]

    ax.plot(angles, bank_vals, 'o-', linewidth=2, color=COLORS['gold'], label=bank)
    ax.fill(angles, bank_vals, alpha=0.25, color=COLORS['gold'])
    ax.plot(angles, sect_vals, 'o--', linewidth=1.5, color='#94a3b8', label='Moy. Secteur')
    ax.fill(angles, sect_vals, alpha=0.1, color='#94a3b8')

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, color='#334155', fontsize=9)
    ax.set_yticklabels([])
    ax.spines['polar'].set_color('#e2e8f0')
    ax.grid(color='#e2e8f0', linewidth=0.8)
    ax.set_title(f'Diagnostic vs Secteur', color='white', fontsize=12, pad=15)
    ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.1),
              facecolor='#1e293b', edgecolor='#334155', labelcolor='white', fontsize=8)
    plt.tight_layout()
    return _fig_to_png_bytes(fig)


def make_historique_chart(df: pd.DataFrame, bank: str) -> bytes:
    """Combo Barre (Bilan) + Ligne (Résultat Net) pour une banque."""
    plt.style.use('default')
    df_bank = df[df['Sigle'] == bank].copy()

    if 'ANNEE' not in df_bank.columns or df_bank.empty:
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.set_facecolor(COLORS['bg'])
        fig.patch.set_facecolor(COLORS['bg'])
        ax.text(0.5, 0.5, 'Historique non disponible', ha='center', va='center', color='white')
        return _fig_to_png_bytes(fig)

    hist = (df_bank.groupby('ANNEE')[['BILAN', 'RESULTAT.NET']]
                   .sum().reset_index().sort_values('ANNEE'))
    hist['BILAN_B'] = hist['BILAN'] / 1_000
    hist['RN_M'] = hist['RESULTAT.NET']

    fig, ax1 = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor(COLORS['bg'])
    ax1.set_facecolor(COLORS['bg'])

    # Barres pour le Bilan
    x = range(len(hist))
    ax1.bar(x, hist['BILAN_B'], color=COLORS['accent'], alpha=0.75, label='Bilan (Md FCFA)')
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(hist['ANNEE'].astype(int).tolist(), color='#94a3b8')
    ax1.set_ylabel('Bilan (Md FCFA)', color='#64748b')
    ax1.tick_params(axis='y', colors='#64748b')
    ax1.spines[['top', 'right']].set_visible(False)
    for spine in ['bottom', 'left']:
        ax1.spines[spine].set_color('#e2e8f0')
    ax1.grid(color='#f1f5f9', linestyle='--', linewidth=0.6, alpha=0.8)

    # Ligne pour Résultat Net
    ax2 = ax1.twinx()
    ax2.plot(list(x), hist['RN_M'], 'o-', color=COLORS['gold'],
             linewidth=2.5, markersize=7, label='Resultat Net (M FCFA)')
    ax2.set_ylabel('Resultat Net (M FCFA)', color=COLORS['gold'])
    ax2.tick_params(axis='y', colors=COLORS['gold'])
    ax2.spines[['top', 'bottom', 'left']].set_visible(False)
    ax2.spines['right'].set_color('#334155')
    ax2.set_facecolor('none')

    ax1.set_title(f'Croissance Historique | {bank}', color='white', fontsize=13)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               facecolor='#1e293b', edgecolor='#334155',
               labelcolor='white', fontsize=8, loc='upper left')
    plt.tight_layout()
    return _fig_to_png_bytes(fig)


def make_marche_chart(df: pd.DataFrame, year) -> bytes:
    """Camembert : parts de marché des banques."""
    plt.style.use('default')
    df_y = df.copy()
    if year and year != 'TOUTES' and 'ANNEE' in df.columns:
        df_y = df[df['ANNEE'] == int(year)]

    pdm = df_y.groupby('Sigle')['BILAN'].sum()
    total = pdm.sum()
    if total == 0:
        pdm = pd.Series({'N/A': 1})

    # Regrouper les petites parts
    threshold = total * 0.03
    small = pdm[pdm < threshold].sum()
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    wedges, texts, autotexts = ax.pie(
        pdm.values,
        labels=pdm.index,
        colors=COLORS['palette'],
        autopct='%1.1f%%',
        startangle=90,
        pctdistance=0.85,
        wedgeprops=dict(width=0.45, edgecolor='white', linewidth=1)
    )
    for t in texts:
        t.set_color('#334155')
        t.set_fontsize(7)
    for at in autotexts:
        at.set_color('#334155')
        at.set_fontsize(6)

    ax.set_title('Répartition du Marché par Banque', color='#334155', fontsize=13)
    plt.tight_layout()
    return _fig_to_png_bytes(fig)


# ============================================================
# Assemblage PDF final
# ============================================================

def generate_full_report(df: pd.DataFrame, bank: str, year) -> bytes:
    """
    Génère un rapport PDF complet style notebook avec :
    - Page de garde
    - Section Macro : évolution + classement + marché
    - Section Micro : historique banque + radar diagnostique + tableau ratios
    """

    # --- Calculs pour la section micro ---
    df_bank = df[df['Sigle'] == bank] if bank and bank != 'TOUTES' else df
    if 'ANNEE' in df.columns and year and year != 'TOUTES':
        df_year = df[df['ANNEE'] == int(year)]
        df_bank_year = df_bank[df_bank['ANNEE'] == int(year)]
    else:
        df_year = df
        df_bank_year = df_bank

    bilan_s = pd.to_numeric(df_year['BILAN'], errors='coerce').fillna(0).sum()
    fp_b = (pd.to_numeric(df_bank_year.get('FONDS.PROPRE', pd.Series([0])), errors='coerce').fillna(0).sum()
            if 'FONDS.PROPRE' in df_bank_year.columns else 0)
    res_b = pd.to_numeric(df_bank_year['RESULTAT.NET'], errors='coerce').fillna(0).sum() if 'RESULTAT.NET' in df_bank_year.columns else 0
    bilan_b = pd.to_numeric(df_bank_year['BILAN'], errors='coerce').fillna(0).sum()
    ress_b = pd.to_numeric(df_bank_year['RESSOURCES'], errors='coerce').fillna(0).sum() if 'RESSOURCES' in df_bank_year.columns else 0

    solv = (fp_b / bilan_b * 100) if bilan_b > 0 else 0
    roe  = (res_b / fp_b * 100)    if fp_b > 0 else 0
    roa  = (res_b / bilan_b * 100) if bilan_b > 0 else 0
    pdm  = (bilan_b / bilan_s * 100) if bilan_s > 0 else 0
    year_label = str(int(year)) if year and year != 'TOUTES' else 'Toutes années'

    # --- Génération des graphiques ---
    img_evolution = make_evolution_chart(df)
    img_classement = make_classement_chart(df, year)
    img_marche = make_marche_chart(df, year)
    img_historique = make_historique_chart(df, bank) if bank and bank != 'TOUTES' else None
    img_radar = make_radar_chart(df, bank) if bank and bank != 'TOUTES' else None

    # Sauvegarder en fichiers temp
    tmp_ev  = _tmp_png(img_evolution)
    tmp_cl  = _tmp_png(img_classement)
    tmp_mk  = _tmp_png(img_marche)
    tmp_hi  = _tmp_png(img_historique) if img_historique else None
    tmp_rd  = _tmp_png(img_radar) if img_radar else None

    # --- Construction PDF ---
    pdf = FPDF()
    try:
        pdf.add_font("Arial", "",  "C:/Windows/Fonts/arial.ttf")
        pdf.add_font("Arial", "B", "C:/Windows/Fonts/arialbd.ttf")
        pdf.add_font("Arial", "I", "C:/Windows/Fonts/ariali.ttf")
        FONT = "Arial"
    except Exception:
        FONT = "helvetica"

    # ---- Page 1 : Page de garde ----
    pdf.add_page()
    pdf.set_fill_color(248, 250, 252) # Slate 50
    pdf.rect(0, 0, 210, 297, 'F')

    pdf.set_y(90)
    pdf.set_text_color(79, 70, 229) # Indigo
    pdf.set_font(FONT, 'B', 10)
    pdf.cell(0, 8, "BCEAO INSIGHT | BANKING INTELLIGENCE PLATFORM",
             new_x="LMARGIN", new_y="NEXT", align='C')

    pdf.set_text_color(15, 23, 42) # Noir
    pdf.set_font(FONT, 'B', 28)
    pdf.multi_cell(0, 14, "Rapport d'Analyses\nApprofondies", align='C')
    pdf.set_font(FONT, '', 16)
    pdf.cell(0, 10, "Secteur Bancaire Senegalais", new_x="LMARGIN", new_y="NEXT", align='C')

    pdf.ln(12)
    pdf.set_draw_color(99, 102, 241)
    pdf.set_line_width(1.5)
    pdf.line(30, pdf.get_y(), 180, pdf.get_y())
    pdf.ln(10)

    if bank and bank != 'TOUTES':
        pdf.set_text_color(245, 158, 11)
        pdf.set_font(FONT, 'B', 14)
        pdf.cell(0, 10, f"Positionnement strategique : {bank}",
                 new_x="LMARGIN", new_y="NEXT", align='C')

    pdf.ln(5)
    pdf.set_text_color(148, 163, 184)
    pdf.set_font(FONT, '', 10)
    pdf.cell(0, 8, f"Exercice : {year_label} | Source : BCEAO",
             new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.cell(0, 8, f"Genere le {time.strftime('%d/%m/%Y a %Hh%M')}",
             new_x="LMARGIN", new_y="NEXT", align='C')

    # ---- Page 2 : Macro — Objectif ----
    pdf.add_page()
    _section_header(pdf, FONT, "1. VUE D'ENSEMBLE DU SECTEUR BANCAIRE")

    pdf.set_text_color(245, 245, 245)
    pdf.set_font(FONT, 'B', 11)
    pdf.cell(0, 8, "Objectif", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(FONT, '', 10)
    pdf.set_text_color(200, 200, 200)
    pdf.multi_cell(0, 6,
        f"Ce rapport analyse la structure et la performance du secteur "
        f"bancaire senegalais a partir des donnees financieres BCEAO. "
        f"L'objectif est d'evaluer la competitivite des etablissements "
        f"de credit et le positionnement de {bank} par rapport au marche."
    )
    pdf.ln(5)
    pdf.image(tmp_ev, x=10, w=190)
    pdf.ln(5)
    pdf.image(tmp_cl, x=10, w=190)

    # ---- Page 3 : Répartition du marché ----
    pdf.add_page()
    _section_header(pdf, FONT, "2. REPARTITION DU MARCHE")
    pdf.image(tmp_mk, x=25, w=160)
    pdf.ln(8)

    # Tableau résumé macro
    _table_macro(pdf, FONT, df_year)

    # ---- Page 4 : Analyse Micro (si banque sélectionnée) ----
    if bank and bank != 'TOUTES' and tmp_hi and tmp_rd:
        pdf.add_page()
        _section_header(pdf, FONT, f"3. ANALYSE MICRO — {bank.upper()}")

        pdf.set_font(FONT, '', 10)
        pdf.set_text_color(200, 200, 200)
        pdf.multi_cell(0, 6,
            f"Diagnostic detaille de la banque {bank}. "
            f"Les indicateurs cles sont compares aux moyennes sectorielles."
        )
        pdf.ln(5)
        pdf.image(tmp_hi, x=10, w=190)
        pdf.ln(5)

        # Ratios
        _table_ratios(pdf, FONT, bank, solv, roe, roa, pdm, bilan_b, ress_b, fp_b, res_b)

        # ---- Page 5 : Radar ----
        pdf.add_page()
        _section_header(pdf, FONT, f"4. DIAGNOSTIQUE STRATEGIQUE — {bank.upper()}")
        pdf.image(tmp_rd, x=30, w=150)

    # ---- Nettoyage fichiers temp ----
    for f in [tmp_ev, tmp_cl, tmp_mk, tmp_hi, tmp_rd]:
        if f and os.path.exists(f):
            try:
                os.unlink(f)
            except Exception:
                pass

    # Retourne les bytes (fpdf2 output returns bytearray)
    return bytes(pdf.output())


def _section_header(pdf, FONT, title):
    """Ajoute un bloc titre de section."""
    pdf.set_y(pdf.get_y() + 2)
    pdf.set_fill_color(15, 23, 42)
    pdf.set_text_color(99, 102, 241)
    pdf.set_font(FONT, 'B', 14)
    pdf.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT", fill=False)
    pdf.set_draw_color(99, 102, 241)
    pdf.set_line_width(0.8)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    pdf.set_text_color(220, 220, 220)


def _table_macro(pdf, FONT, df_y):
    """Tableau des indicateurs macro consolidés."""
    pdf.set_font(FONT, 'B', 11)
    pdf.set_text_color(245, 158, 11)
    pdf.cell(0, 10, "Indicateurs Consolides du Secteur", new_x="LMARGIN", new_y="NEXT")

    metrics = {
        'Total Bilan': pd.to_numeric(df_y['BILAN'], errors='coerce').fillna(0).sum(),
        'Total Ressources': pd.to_numeric(df_y['RESSOURCES'], errors='coerce').fillna(0).sum(),
        'Total Emplois': pd.to_numeric(df_y['EMPLOI'], errors='coerce').fillna(0).sum(),
        'Nb Banques': df_y['Sigle'].nunique(),
    }
    for label, val in metrics.items():
        pdf.set_font(FONT, 'B', 10)
        pdf.set_text_color(200, 200, 200)
        pdf.cell(90, 8, f"  {label} :", border=0)
        pdf.set_font(FONT, '', 10)
        v_str = _fmt(val) + " M FCFA" if label != 'Nb Banques' else str(int(val))
        pdf.cell(90, 8, v_str, border=0, new_x="LMARGIN", new_y="NEXT")


def _table_ratios(pdf, FONT, bank, solv, roe, roa, pdm, bilan, ress, fp, res):
    """Tableau des ratios prudentiels pour la micro."""
    pdf.set_font(FONT, 'B', 11)
    pdf.set_text_color(245, 158, 11)
    pdf.cell(0, 10, "Ratios Prudentiels & Indicateurs Cles", new_x="LMARGIN", new_y="NEXT")

    rows = [
        ("Total Bilan",       _fmt(bilan) + " M FCFA"),
        ("Ressources",        _fmt(ress)  + " M FCFA"),
        ("Fonds Propres",     _fmt(fp)    + " M FCFA"),
        ("Resultat Net",      _fmt(res)   + " M FCFA"),
        ("Solvabilite",       f"{solv:.1f}% (norme BCEAO > 8%)"),
        ("ROE (Rentabilite)", f"{roe:.1f}%"),
        ("ROA (Rendement)",   f"{roa:.2f}%"),
        ("Part de Marche",    f"{pdm:.1f}%"),
    ]
    for label, val in rows:
        pdf.set_font(FONT, 'B', 10)
        pdf.set_text_color(200, 200, 200)
        pdf.cell(90, 8, f"  {label} :", border=0)
        pdf.set_font(FONT, '', 10)
        pdf.cell(90, 8, val, border=0, new_x="LMARGIN", new_y="NEXT")
