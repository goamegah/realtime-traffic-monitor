import os
import json
import requests
import boto3
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

# Fonction pour récupérer les données et les envoyer à AWS S3
def fetch_and_store_data_to_s3():
    """
    Récupère les données d'une API et les stocke sur AWS S3 en format JSON.
    """

    # URL de l'API
    alt_api_endpoint = "https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/etat-du-trafic-en-temps-reel/records?select=*&limit=100&lang=fr"
    api_endpoint = os.getenv("API_ENDPOINT", alt_api_endpoint)

    # Configuration AWS S3
    s3_bucket = os.getenv("AWS_S3_BUCKET_NAME", "traffic-monitor-bucket")  # Nom du bucket
    s3_prefix = os.getenv("AWS_S3_PREFIX", "raw/")  # Dossier dans S3 (ex: raw/)
    aws_region = os.getenv("AWS_REGION", "eu-west-1")
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    # Connexion au client S3
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
    except Exception as e:
        print(f"Erreur de connexion à S3 : {e}")
        return

    # Récupération des données de l'API
    try:
        response = requests.get(api_endpoint, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data:
            print("Aucune donnée reçue de l'API")
            return

        # Générer un nom de fichier basé sur la date et l'heure
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        file_name = f"{s3_prefix}traffic_data_{timestamp}.json"  # Exemple : raw/traffic_data_20250309123045.json

        # Conversion en JSON et envoi à S3
        s3_client.put_object(
            Bucket=s3_bucket,
            Key=file_name,
            Body=json.dumps(data, indent=2).encode('utf-8'),
            ContentType="application/json"
        )

        print(f"Données enregistrées sur S3 : s3://{s3_bucket}/{file_name}")

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête API : {e}")

    except boto3.exceptions.Boto3Error as e:
        print(f"Erreur avec AWS S3 : {e}")

# Définition du DAG Airflow
with DAG(
    dag_id='realtime_traffic_monitor_raw_to_s3',
    default_args=default_args,
    description="Ingestion des données de trafic en temps réel vers AWS S3",
    schedule_interval='*/3 * * * *',  # Exécuter toutes les 3 minutes
    catchup=False
) as dag:

    # Vérifie si l'API est accessible avant d'exécuter l'ingestion
    check_api = HttpSensor(
        task_id="check_api_availability",
        http_conn_id="traffic_api",
        endpoint='api/explore/v2.1/catalog/datasets/etat-du-trafic-en-temps-reel/records?limit=100',
        timeout=10,
        poke_interval=30,
        mode="poke"
    )

    # Tâche d'ingestion des données vers S3
    ingestion_task = PythonOperator(
        task_id='fetch_and_store_data_to_s3',
        python_callable=fetch_and_store_data_to_s3
    )

    # Définition de l'ordre d'exécution
    check_api >> ingestion_task
