import plotly.graph_objects as go

def create_senegal_map(df):
    """
    Crée une carte interactive du Sénégal avec le positionnement des banques.
    """
    # Coordonnées des sièges sociaux à Dakar (Zones: Plateau, Almadies, Fann)
    locations = {
        "BOA SENEGAL": {"lat": 14.6937, "lon": -17.4441},
        "CBAO": {"lat": 14.6912, "lon": -17.4330},
        "SOCIETE GENERALE SENEGAL": {"lat": 14.6950, "lon": -17.4390},
        "SG SENEGAL": {"lat": 14.6950, "lon": -17.4390},
        "ECOBANK SENEGAL": {"lat": 14.6680, "lon": -17.4344},
        "ORABANK SENEGAL": {"lat": 14.6720, "lon": -17.4360},
        "BNDE": {"lat": 14.6750, "lon": -17.4380},
        "CORIS BANK": {"lat": 14.6810, "lon": -17.4420},
        "BIMAO": {"lat": 14.6850, "lon": -17.4450},
        "NSIA BANQUE": {"lat": 14.6880, "lon": -17.4480},
        "UBA SENEGAL": {"lat": 14.6910, "lon": -17.4510},
        "BANQUE DE L'HABITAT DU SENEGAL": {"lat": 14.6940, "lon": -17.4540},
        "CNCAS": {"lat": 14.6970, "lon": -17.4570},
        "BRM": {"lat": 14.7000, "lon": -17.4600},
        "IB BANK": {"lat": 14.7030, "lon": -17.4630},
    }
    
    lats = []
    lons = []
    names = []
    sizes = []
    
    for _, row in df.iterrows():
        bank = str(row['Sigle']).upper().strip()
        # On essaie de trouver une correspondance ou on met une position par défaut à Dakar Plateau
        loc = locations.get(bank, {"lat": 14.667 + (len(names) * 0.002), "lon": -17.435 - (len(names) * 0.001)})
        lats.append(loc['lat'])
        lons.append(loc['lon'])
        names.append(bank)
        
        # Taille proportionnelle (Bilan ou Emploi)
        size_val = float(row.get('BILAN', 0))
        sizes.append(min(max(size_val / 40000, 10), 50)) 
            
    fig = go.Figure(go.Scattermapbox(
        lat=lats,
        lon=lons,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=sizes, 
            color='#1a237e',
            opacity=0.7,
            showscale=False
        ),
        text=names,
        hoverinfo='text',
        name="Emplacement Stratégique"
    ))

    fig.update_layout(
        mapbox_style="carto-positron",
        hovermode='closest',
        mapbox=dict(
            bearing=0,
            center=go.layout.mapbox.Center(lat=14.685, lon=-17.445),
            pitch=0,
            zoom=12
        ),
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    
    return fig
