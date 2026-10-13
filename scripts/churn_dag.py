from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os

# Ajouter le dossier parent et 'include' au chemin Python pour pouvoir importer nos scripts
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../include')))

from ingest import ingest_data
from validate import validate_data
from train import train_model

# Arguments par défaut du DAG
default_args = {
    'owner': 'wissal',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

# Définition du DAG Airflow
with DAG(
    dag_id='churn_mlops_orchestration',
    default_args=default_args,
    description='Pipeline MLOps complet : Ingestion -> Qualité (GX) -> Entraînement (MLlib & MLflow)',
    start_date=datetime(2026, 1, 1),
    schedule='@daily',
    catchup=False,
) as dag:

    # Tâche 1 : Ingestion et nettoyage des données brutes
    t1_ingest = PythonOperator(
        task_id='ingest_data_task',
        python_callable=ingest_data,
    )

    # Tâche 2 : Validation de la qualité des données avec Great Expectations
    t2_validate = PythonOperator(
        task_id='validate_data_task',
        python_callable=validate_data,
    )

    # Tâche 3 : Entraînement du modèle Spark MLlib et suivi MLflow
    t3_train = PythonOperator(
        task_id='train_model_task',
        python_callable=train_model,
    )

    # Ordonnancement des tâches du pipeline (L'opérateur >> définit le flux DAG)
    # Le modèle ne s'entraîne que si la validation réussit, elle-même exécutée après l'ingestion.
    t1_ingest >> t2_validate >> t3_train