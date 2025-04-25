# dataloader/db_utils.py

import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Unique instance de l'engine (réutilisable partout)
_engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)

def get_engine():
    return _engine

def run_query(query: str, params: dict = None) -> pd.DataFrame:
    """
    Exécute une requête SQL avec SQLAlchemy et pandas.
    Utilise le moteur central `_engine`.

    :param query: Requête SQL avec placeholders `:param`
    :param params: Dictionnaire des paramètres
    :return: DataFrame pandas
    """
    return pd.read_sql(text(query), con=_engine, params=params)
