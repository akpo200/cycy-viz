import sys
import os

# Ajout du dossier racine au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pandas as pd
from utils.data_loader import get_banking_data


# ============================================================
# Fixtures
# ============================================================
@pytest.fixture(scope="module")
def df():
    """Charge les données une seule fois pour tous les tests."""
    return get_banking_data()


# ============================================================
# Tests d'intégrité des données
# ============================================================

def test_get_banking_data_not_empty(df):
    """Vérifie que le DataFrame retourné n'est pas vide."""
    assert not df.empty, "get_banking_data() ne doit pas retourner un DataFrame vide"


def test_required_columns_present(df):
    """Vérifie que toutes les colonnes critiques sont présentes."""
    required = ['Sigle', 'BILAN', 'EMPLOI', 'RESSOURCES', 'RESULTAT.NET']
    for col in required:
        assert col in df.columns, f"Colonne manquante : '{col}'"


def test_no_negative_bilan(df):
    """Vérifie que le BILAN est toujours positif (> 0 après nettoyage)."""
    bilan_series = pd.to_numeric(df['BILAN'], errors='coerce').fillna(0)
    assert (bilan_series > 0).all(), "Certaines valeurs de BILAN sont nulles ou négatives"


def test_sigle_not_null(df):
    """Vérifie qu'aucun Sigle n'est nul ou vide."""
    assert df['Sigle'].notna().all(), "Des valeurs nulles existent dans la colonne Sigle"
    assert (df['Sigle'].astype(str).str.strip() != '').all(), "Des Sigles vides existent"


def test_minimum_banks(df):
    """Vérifie qu'on a au minimum 5 banques distinctes."""
    nb = df['Sigle'].nunique()
    assert nb >= 5, f"Seulement {nb} banques trouvées — attendu au moins 5"


def test_resultat_net_is_numeric(df):
    """Vérifie que RESULTAT.NET est bien numérique."""
    series = pd.to_numeric(df['RESULTAT.NET'], errors='coerce')
    assert series.notna().sum() > 0, "RESULTAT.NET ne contient aucune valeur numérique"


def test_fonds_propres_present(df):
    """Vérifie que la colonne FONDS.PROPRE est présente (nécessaire pour les ratios)."""
    assert 'FONDS.PROPRE' in df.columns, "Colonne FONDS.PROPRE manquante — ratios impossibles"
