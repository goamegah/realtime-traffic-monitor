import streamlit as st
import pandas as pd
import altair as alt
from streamlit_autorefresh import st_autorefresh
from dataloader.data_loader import get_db_engine
import datetime

st.set_page_config(page_title="🏠 Home - Traffic Overview", layout="wide")
st.title("🏠 Traffic Monitoring Dashboard")

# Auto-refresh every 60 seconds
st_autorefresh(interval=60 * 1000, key="home_refresh")

engine = get_db_engine()

# Load latest map features (only latest period)
@st.cache_data(ttl=30)
def load_home_data():
    query = """
        SELECT period, road_name, traffic_status, road_category
        FROM road_traffic_feats_map
        WHERE period = (SELECT MAX(period) FROM road_traffic_feats_map)
    """
    return pd.read_sql(query, engine)

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

# Répartition par statut de trafic
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

# Données tabulaires optionnelles
with st.expander("🔍 Voir les données brutes"):
    st.dataframe(df, use_container_width=True)


# Load speed data for boxplots
@st.cache_data(ttl=30)
def load_speed_data():
    # Use a simpler query without NOW() function
    query = """
        SELECT traffic_status, average_speed
        FROM traffic_status_avg_status
    """
    return pd.read_sql(query, engine)


# Try to load speed data, but handle any errors
try:
    speed_df = load_speed_data()
    has_speed_data = not speed_df.empty
except Exception as e:
    st.error(f"Erreur lors du chargement des données de vitesse: {str(e)}")
    has_speed_data = False
    speed_df = pd.DataFrame()

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

# Répartition par statut de trafic
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

# Boxplots de vitesse moyenne par statut de trafic
if has_speed_data:
    st.markdown("## 🚗 Distributions des vitesses par statut de trafic")

    # Create boxplot with Altair
    boxplot = alt.Chart(speed_df).mark_boxplot().encode(
        x=alt.X('traffic_status:N', title='Statut de trafic'),
        y=alt.Y('average_speed:Q', title='Vitesse moyenne (km/h)'),
        color='traffic_status:N'
    ).properties(
        width='container',
        height=400,
        title="🚗 Distribution des vitesses par statut de trafic"
    )

    st.altair_chart(boxplot, use_container_width=True)

    # Add summary statistics for each traffic status
    st.markdown("### 📊 Statistiques des vitesses par statut")

    stats_df = speed_df.groupby('traffic_status')['average_speed'].agg([
        ('Moyenne', 'mean'),
        ('Médiane', 'median'),
        ('Min', 'min'),
        ('Max', 'max'),
        ('Écart-type', 'std')
    ]).reset_index()

    # Round the statistics to 2 decimal places
    for col in stats_df.columns:
        if col != 'traffic_status':
            stats_df[col] = stats_df[col].round(2)

    st.dataframe(stats_df, use_container_width=True)
else:
    st.warning("⚠️ Pas de données de vitesse disponibles pour créer les boxplots.")

# Données tabulaires optionnelles
with st.expander("🔍 Voir les données brutes"):
    st.dataframe(df, use_container_width=True)
