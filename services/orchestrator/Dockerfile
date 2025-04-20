FROM apache/airflow:2.6.0

# Copie des DAGs dans le dossier dédié de l'image
COPY dags/ /opt/airflow/dags/

# Installation des dépendances supplémentaires
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
