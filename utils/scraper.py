import requests
from bs4 import BeautifulSoup
import os

def scrape_bceao_pdf_links():
    """
    Scrape le site de la BCEAO pour trouver les rapports financiers.
    Comment fait-on ?
    1. On définit l'URL cible des publications.
    2. On utilise 'requests' avec un 'User-Agent' pour simuler un humain.
    3. On utilise 'BeautifulSoup' pour extraire tous les liens <a> se terminant par .pdf
    """
    url = "https://www.bceao.int/fr/publications/bilans-et-comptes-de-resultats-des-banques-et-etablissements-financiers-de-lumoa"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [a['href'] for a in soup.find_all('a', href=True) if '.pdf' in a['href']]
        return links
    except Exception as e:
        return f"Erreur : {e}"
