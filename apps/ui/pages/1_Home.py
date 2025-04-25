# apps/ui/pages/1_Home.py

import streamlit as st
import pandas as pd
import altair as alt
from streamlit_autorefresh import st_autorefresh
from dataloader.db_utils import run_query

st.set_page_config(page_title="🏠 Home - Traffic Overview", layout="wide")
st.title("🏠 Traffic Monitoring Dashboard")

st_autorefresh(interval=60 * 1000, key="home_refresh")

@st.cache_data(ttl=30)
def load_home_data():
    query = """
        SELECT period, road_name, traffic_status, road_category
        FROM road_traffic_feats_map
        WHERE period = (SELECT MAX(period) FROM road_traffic_feats_map)
    """
    return run_query(query)

df = load_home_data()

if df.empty:
    st.warning("⚠️ Aucune donnée disponible pour l'instant.")
    st.stop()

# KPIs
nb_segments = len(df)
nb_routes = df["road_name"].nunique()
status_dominant = df["traffic_status"].mode()[0]

st.markdown("## 📈 Statistiques globales")
col1, col2, col3 = st.columns(3)
col1.metric("🧩 Tronçons total", nb_segments)
col2.metric("🛣️ Routes différentes", nb_routes)
col3.metric("🚦 Statut dominant", status_dominant)

st.markdown("## 🚦 Répartition des statuts de trafic")
status_counts = df["traffic_status"].value_counts().reset_index()
status_counts.columns = ["traffic_status", "count"]

chart = alt.Chart(status_counts).mark_bar().encode(
    x=alt.X("traffic_status", sort="-y", title="Statut de trafic"),
    y=alt.Y("count", title="Nombre de tronçons"),
    color=alt.Color("traffic_status", legend=None)
).properties(
    width="container",
    height=400,
    title="🚦 Nombre de tronçons par statut de trafic"
)

st.altair_chart(chart, use_container_width=True)

with st.expander("🔍 Voir les données brutes"):
    st.dataframe(df, use_container_width=True)
