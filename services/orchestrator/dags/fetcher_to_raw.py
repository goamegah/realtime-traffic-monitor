import os
import json
import requests
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.sensors.http import HttpSensor

# Définition des arguments par défaut du DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 3, 9),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=3),
}

# Définition du répertoire de stockage local (monté dans Docker)
TRANSIENT_DIR = "/opt/airflow/data/raw"

def fetch_and_store_data():
    """
    Récupère les données de l'API et les stocke dans un répertoire local sous forme de fichier JSON.
    """
    alt_api_endpoint = "https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/etat-du-trafic-en-temps-reel/records?select=*&limit=100&lang=fr"
    api_endpoint = os.getenv("API_ENDPOINT", alt_api_endpoint)

    # Vérifier si le répertoire existe, sinon le créer
    os.makedirs(TRANSIENT_DIR, exist_ok=True)

    try:
        response = requests.get(api_endpoint, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data:
            print("Aucune donnée reçue de l'API")
            return
        
        # Générer un nom de fichier avec timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        filename = f"{TRANSIENT_DIR}/{timestamp}.json"

        # Enregistrer les données en local
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        print(f"Données enregistrées dans : {filename}")

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête API : {e}")

# Définition du DAG Airflow
with DAG(
    dag_id='realtime_traffic_monitor_fetcher_to_raw',
    default_args=default_args,
    description="Ingestion des données de trafic et stockage en local",
    schedule_interval='*/1 * * * *',  # Exécuter toutes les 1 minutes
    catchup=False
) as dag:

    # Vérifie si l'API est accessible avant l'ingestion
    check_api = HttpSensor(
        task_id="check_api_availability",
        http_conn_id="traffic_api",  # Configuré dans Admin > Connections
        endpoint="api/explore/v2.1/catalog/datasets/etat-du-trafic-en-temps-reel/records?limit=100",
        timeout=10,
        poke_interval=30,
        mode="poke"
    )

    # Tâche pour récupérer et stocker les données
    ingestion_task = PythonOperator(
        task_id='fetch_and_store_data',
        python_callable=fetch_and_store_data
    )

    # Définition de l'ordre d'exécution
    check_api >> ingestion_task
