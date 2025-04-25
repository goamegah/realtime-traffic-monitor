import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from dataloader.data_loader import (
    get_db_engine,
    get_available_road_names,
    get_period_bounds,
    load_traffic_data
)

st.set_page_config(page_title="📊 Traffic History", layout="wide")
st.title("📊 Traffic Evolution History")

# 🔄 Rafraîchissement automatique toutes les 60 secondes
st_autorefresh(interval=60 * 1000, key="history_refresh")

# 📌 Connexion base de données
engine = get_db_engine()

# 📌 Choix de la résolution temporelle
resolution = st.radio("⏱️ Temporal Resolution", ["minute", "hour"], horizontal=True)

# 📌 Chargement des routes disponibles
with st.spinner("Chargement des routes disponibles..."):
    road_names = get_available_road_names(engine, resolution)

# 📌 Sélection persistante du nom de route
if "selected_road" not in st.session_state:
    st.session_state.selected_road = road_names[0]

road_name = st.selectbox(
    "🛣️ Road Name",
    road_names,
    index=road_names.index(st.session_state.selected_road),
    key="selected_road"
)

# 📌 Bornes temporelles pour les sliders
with st.spinner("Chargement des bornes temporelles..."):
    min_period, max_period = get_period_bounds(engine, resolution, road_name)

if min_period == max_period:
    st.warning("⚠️ Pas assez de données pour cette route et cette résolution.")
    st.stop()

# 📅 Sélection de la période
col_start, col_end = st.columns(2)
with col_start:
    start_date = st.slider("📅 Start", min_value=min_period, max_value=max_period, value=min_period, format="YYYY-MM-DD HH:mm")
with col_end:
    end_date = st.slider("📅 End", min_value=min_period, max_value=max_period, value=max_period, format="YYYY-MM-DD HH:mm")

# 📌 Chargement de l'évolution du trafic
with st.spinner("Chargement des données de trafic..."):
    df = load_traffic_data(engine, resolution, road_name, start_date, end_date)

if df.empty:
    st.warning("⚠️ Aucune donnée disponible pour les filtres choisis.")
    st.stop()

# 📊 KPI
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

# 📈 Graphiques Altair
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

# 🗃️ Données brutes
with st.expander("🔍 Voir les données brutes"):
    st.dataframe(df, use_container_width=True)
