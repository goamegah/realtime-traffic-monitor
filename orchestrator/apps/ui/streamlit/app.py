import streamlit as st
import plotly.express as px
import pandas as pd

st.title("Dashboard Traffic en Temps Réel")

# Exemple de data (tu peux le connecter à ton dossier `./data` plus tard)
df = pd.DataFrame({
    "Heure": ["10:00", "10:05", "10:10", "10:15"],
    "Volume de trafic": [120, 150, 90, 170]
})

fig = px.line(df, x="Heure", y="Volume de trafic", title="Évolution du trafic")
st.plotly_chart(fig)
