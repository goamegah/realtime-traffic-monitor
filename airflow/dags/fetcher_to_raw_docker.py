from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.http.sensors.http import HttpSensor
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 4, 6),
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="realtime_traffic_monitor_fetcher_to_raw_docker",
    default_args=default_args,
    schedule_interval="*/5 * * * *",
    catchup=False,
    description="Lancer le job Scala FetcherToRaw depuis un conteneur Docker",
) as dag:

    check_api = HttpSensor(
        task_id="check_api",
        http_conn_id="traffic_api",  # Configuré dans Admin > Connections
        endpoint="api/explore/v2.1/catalog/datasets/etat-du-trafic-en-temps-reel/records?limit=100",
        timeout=10,
        poke_interval=30,
        mode="poke",
    )

    run_fetcher_scala = DockerOperator(
        task_id="run_scala_fetcher_job",
        image="scala-fetcher-runner",
        api_version="auto",
        auto_remove=True,
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        command='sbt "runMain com.goamegah.trafficmonitor.job.FetcherToRaw"',
        working_dir="/app",
        mount_tmp_dir=False,
        mounts=[
            "/home/goamegah/Documents/workspace/develop/esgi/4a/s2/spark-streaming/realtime-traffic-monitor/src/main/data:/app/src/main/data"
        ],
    )

    check_api >> run_fetcher_scala
