import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import pandas as pd

# Charger les variables d'environnement (.env à la racine du projet)
load_dotenv()

def get_db_engine():
    db_url = (
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/"
        f"{os.getenv('POSTGRES_DB')}"
    )
    return create_engine(db_url)

def read_sql_file(filename: str) -> str:
    """Lis un fichier SQL depuis data/queries/"""
    path = os.path.join(os.path.dirname(__file__), "queries", filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# Fonctions de requêtes
def get_available_road_names(engine, resolution: str):
    query = read_sql_file("get_available_road_names.sql")
    df = pd.read_sql(query.format(table=f"road_traffic_stats_{resolution}"), con=engine)
    return df["road_name"].tolist()

def get_period_bounds_query(resolution: str) -> str:
    return read_sql_file("get_period_bounds.sql").format(table=f"road_traffic_stats_{resolution}")

def get_traffic_history_query(resolution: str) -> str:
    return read_sql_file("get_traffic_history.sql").format(table=f"road_traffic_stats_{resolution}")
