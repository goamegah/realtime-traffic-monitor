# apps/ui/pages/2_History.py

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from dataloader.data_loader import get_db_engine
from dataloader import get_available_road_names, get_period_bounds_query, get_traffic_history_query

st.set_page_config(page_title="📊 Traffic History", layout="wide")
st.title("📊 Traffic Evolution History")

# Rafraîchissement automatique toutes les 60 secondes
st_autorefresh(interval=60 * 1000, key="history_refresh")

engine = get_db_engine()

# Choix de la résolution temporelle
resolution = st.radio("⏱️ Temporal Resolution", ["minute", "hour"], horizontal=True)

# Sélection persistante du nom de route
if "selected_road" not in st.session_state:
    st.session_state.selected_road = get_available_road_names(engine, resolution)[0]

road_name = st.selectbox(
    "🛣️ Road Name",
    get_available_road_names(engine, resolution),
    index=get_available_road_names(engine, resolution).index(st.session_state.selected_road),
    key="selected_road"
)

# Bornes temporelles pour les sliders
@st.cache_data(ttl=60)
def get_period_bounds(resolution, road_name):
    query = get_period_bounds_query(resolution)
    df = pd.read_sql(query, engine, params={"road_name": road_name})
    return df["min_period"][0].to_pydatetime(), df["max_period"][0].to_pydatetime()

min_period, max_period = get_period_bounds(resolution, road_name)

if min_period == max_period:
    st.warning("⚠️ Pas assez de données pour cette route et cette résolution.")
    st.stop()

# Sliders dans une disposition horizontale
col_start, col_end = st.columns(2)
with col_start:
    start_date = st.slider("📅 Start", min_value=min_period, max_value=max_period, value=min_period, format="YYYY-MM-DD HH:mm")
with col_end:
    end_date = st.slider("📅 End", min_value=min_period, max_value=max_period, value=max_period, format="YYYY-MM-DD HH:mm")

# hargement des données filtrées
@st.cache_data(ttl=30)
def load_traffic_data(resolution, road_name, start_date, end_date):
    query = get_traffic_history_query(resolution)
    return pd.read_sql(query, engine, params={
        "road_name": road_name,
        "start": start_date,
        "end": end_date
    })

df = load_traffic_data(resolution, road_name, start_date, end_date)

if df.empty:
    st.warning("⚠️ Aucune donnée disponible pour les filtres choisis.")
    st.stop()

# KPI
kpi_speed = df["average_speed"].mean()
kpi_travel_time = df["average_travel_time"].mean()
max_speed = df["average_speed"].max()
min_speed = df["average_speed"].min()

st.markdown("## 📈 Indicateurs clés")
col1, col2, col3, col4 = st.columns(4)
col1.metric("🚀 Vitesse moyenne", f"{kpi_speed:.2f} km/h")
col2.metric("⏱️ Temps moyen trajet", f"{kpi_travel_time:.2f} min")
col3.metric("📈 Vitesse max", f"{max_speed:.2f} km/h", delta=f"{(max_speed - kpi_speed):+.2f}")
col4.metric("📉 Vitesse min", f"{min_speed:.2f} km/h", delta=f"{(min_speed - kpi_speed):+.2f}")

# Graphiques côte à côte
st.markdown("## 📊 Évolution temporelle (vitesse & temps trajet)")
col_speed, col_travel = st.columns(2)

with col_speed:
    st.altair_chart(
        alt.Chart(df).mark_line(point=True).encode(
            x=alt.X("period:T", title="Time"),
            y=alt.Y("average_speed:Q", title="Average Speed (km/h)"),
            tooltip=["period:T", "average_speed", "average_travel_time"]
        ).properties(
            width="container",
            height=400,
            title="🚗 Speed Evolution"
        ),
        use_container_width=True
    )

with col_travel:
    st.altair_chart(
        alt.Chart(df).mark_line(point=True, color="orange").encode(
            x=alt.X("period:T", title="Time"),
            y=alt.Y("average_travel_time:Q", title="Avg Travel Time (min)"),
            tooltip=["period:T", "average_speed", "average_travel_time"]
        ).properties(
            width="container",
            height=400,
            title="⏱️ Travel Time Evolution"
        ),
        use_container_width=True
    )

# Données brutes
with st.expander("🔍 Voir les données brutes"):
    st.dataframe(df, use_container_width=True)
