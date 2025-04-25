# apps/ui/pages/3_Map.py

import streamlit as st
import pandas as pd
import folium
from datetime import datetime
from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh
from data.data_loader import get_db_engine

st.set_page_config(page_title="🗺️ Traffic Map", layout="wide")
st.title("🗺️ Real-Time Traffic Map")

# 🔄 Rafraîchissement automatique toutes les 60 secondes
st_autorefresh(interval=60 * 1000, key="map_refresh")

engine = get_db_engine()

@st.cache_data(ttl=30)
def load_map_data():
    query = """
        SELECT period, location_id, road_name, road_category, traffic_status, geometry_linestring
        FROM road_traffic_feats_map
        WHERE geometry_linestring IS NOT NULL
        AND period = (SELECT MAX(period) FROM road_traffic_feats_map)
    """
    return pd.read_sql(query, engine)

df = load_map_data()

if df.empty:
    st.warning("⚠️ Aucune donnée géographique disponible.")
    st.stop()

# 📌 Filtres
with st.sidebar:
    st.header("🔎 Filtres")
    road_names = sorted(df["road_name"].dropna().unique())
    traffic_statuses = sorted(df["traffic_status"].dropna().unique())

    selected_road_names = st.multiselect("🛣️ Road(s)", road_names, default=road_names)
    selected_statuses = st.multiselect("🚦 Statut(s) de trafic", traffic_statuses, default=traffic_statuses)

# 📌 Filtrage
filtered_df = df[
    (df["road_name"].isin(selected_road_names)) &
    (df["traffic_status"].isin(selected_statuses))
]

# 📌 Résumé au-dessus de la carte
latest_period = df["period"].max()
st.markdown(f"""
### 🛰️ Mise à jour : `{latest_period.strftime('%Y-%m-%d %H:%M')}`  
**🚗 Tronçons affichés :** {len(filtered_df)} / {len(df)}  
""")

# 📌 Couleurs par statut
STATUS_COLORS = {
    "freeFlow": "green",
    "heavy": "red",
    "trafficJam": "darkred",
    "slow": "orange",
    "unknown": "gray",
    "roadClosed": "black"
}

def get_color(status):
    return STATUS_COLORS.get(status, "blue")

# 🗺️ Création de la carte
m = folium.Map(location=[48.1147, -1.6794], zoom_start=12, control_scale=True)

for _, row in filtered_df.iterrows():
    try:
        geometry = eval(row["geometry_linestring"])
        coords = geometry["coordinates"]
        coords = [(lat, lon) for lon, lat in coords]
        folium.PolyLine(
            locations=coords,
            color=get_color(row["traffic_status"]),
            weight=5,
            tooltip=f"{row['road_name']} ({row['traffic_status']})"
        ).add_to(m)
    except Exception as e:
        st.error(f"Erreur sur la ligne {row['location_id']}: {e}")

# 📌 Légende manuelle
legend_html = """
<div style='position: fixed; bottom: 60px; left: 60px; z-index: 1000; background: white; padding: 10px; border: 1px solid gray; border-radius: 5px;'>
<b>🚦 Légende Trafic</b><br>
<span style='color:green;'>⬤</span> Free Flow<br>
<span style='color:orange;'>⬤</span> Slow<br>
<span style='color:red;'>⬤</span> Heavy<br>
<span style='color:darkred;'>⬤</span> Traffic Jam<br>
<span style='color:black;'>⬤</span> Road Closed<br>
<span style='color:gray;'>⬤</span> Unknown
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# 📌 Affichage de la carte
st.markdown("## 🧭 Carte des tronçons surveillés")
st_folium(m, width=1000, height=600)

# 🗃️ Données tabulaires optionnelles
with st.expander("🔍 Voir les données géographiques"):
    st.dataframe(filtered_df, use_container_width=True)
