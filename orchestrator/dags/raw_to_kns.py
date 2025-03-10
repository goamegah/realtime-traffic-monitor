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

# Fonction pour récupérer les données et les envoyer à AWS Kinesis
def fetch_and_send_data_to_kinesis():
    """
    Récupère les données d'une API et les envoie à AWS Kinesis avec un timestamp comme clé de partition.
    """

    # Récupération des paramètres depuis les variables d'environnement
    alt_api_endpoint = "https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/etat-du-trafic-en-temps-reel/records?select=*&limit=100&lang=fr"
    api_endpoint = os.getenv("API_ENDPOINT", alt_api_endpoint)
    stream_name = os.getenv("AWS_KINESIS_STREAM_NAME", "taffic-stream")
    aws_region = os.getenv("AWS_REGION", "eu-west-1")
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    # Connexion au client Kinesis
    try:
        kinesis_client = boto3.client(
            'kinesis',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
    except Exception as e:
        print(f"Erreur de connexion à Kinesis : {e}")
        return

    # Récupération des données de l'API
    try:
        response = requests.get(api_endpoint, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data:
            print("Aucune donnée reçue de l'API")
            return

        # Générer un timestamp unique pour la clé de partition
        partition_key = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")

        # Envoi des données à Kinesis
        kinesis_response = kinesis_client.put_record(
            StreamName=stream_name,
            Data=json.dumps(data).encode('utf-8'),
            PartitionKey=partition_key
        )
        print(f"Données envoyées à Kinesis (PartitionKey: {partition_key}): {kinesis_response}")

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête API : {e}")

    except boto3.exceptions.Boto3Error as e:
        print(f"Erreur avec AWS Kinesis : {e}")

# Définition du DAG Airflow
with DAG(
    dag_id='traffic_data_ingestion',
    default_args=default_args,
    description="Ingestion des données de trafic en temps réel vers AWS Kinesis",
    schedule_interval='*/3 * * * *',  # Exécuter toutes les 3 minutes
    catchup=False
) as dag:

    alt_api_url = "https://data.rennesmetropole.fr/api"
    api_url = os.getenv("API_URL", alt_api_url)
    print(f"API URL: {api_url}")

    # Vérifie si l'API est accessible avant d'exécuter l'ingestion
    check_api = HttpSensor(
        task_id="check_api_availability",
        http_conn_id="traffic_api",
        endpoint='api/explore/v2.1/catalog/datasets/etat-du-trafic-en-temps-reel/records?limit=100',
        timeout=10,
        poke_interval=30,
        mode="poke"
    )

    # Tâche d'ingestion des données
    ingestion_task = PythonOperator(
        task_id='fetch_and_send_data_to_kinesis',
        python_callable=fetch_and_send_data_to_kinesis
    )

    # Définition de l'ordre d'exécution
    check_api >> ingestion_task
