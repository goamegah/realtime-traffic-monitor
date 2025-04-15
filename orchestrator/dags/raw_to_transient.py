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
TRANSIENT_DIR = "/opt/airflow/data/transient"

import subprocess

def fetch_data_via_scala():
    try:
        subprocess.run(
            ["sbt", "run"],
            cwd="/opt/airflow/scripts",
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Erreur pendant l'exécution du script Scala : {e}")

# Définition du DAG Airflow
with DAG(
    dag_id='realtime_traffic_monitor_raw_to_transient',
    default_args=default_args,
    description="Ingestion des données de trafic et stockage en local",
    schedule_interval='*/3 * * * *',  # Exécuter toutes les 3 minutes
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
    """ingestion_task = PythonOperator(
        task_id='fetch_and_store_data',
        python_callable=fetch_and_store_data
    )"""

    ingestion_task = PythonOperator(
    task_id='fetch_and_store_data',
    python_callable=fetch_data_via_scala 
    )


    # Définition de l'ordre d'exécution
    check_api >> ingestion_task
