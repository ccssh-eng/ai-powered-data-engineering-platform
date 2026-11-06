"""
DAG : Customer ETL Pipeline
Orchestration du pipeline ETL JSONPlaceholder → PostgreSQL
Module 3 – Orchestration avec Airflow
Auteur : Cédric SH
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator

import sys
import os

# Ajout du répertoire racine au PYTHONPATH
sys.path.insert(0, "/opt/airflow/project")

# ── Paramètres par défaut ────────────────────────────────────
DEFAULT_ARGS = {
    "owner": "cedric-sh",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}


# ── Fonctions des tâches ─────────────────────────────────────

def task_test_connection():
    """Vérifie la connectivité PostgreSQL avant de lancer le pipeline."""
    from database.connection import test_connection
    if not test_connection():
        raise RuntimeError("PostgreSQL est inaccessible — pipeline annulé")


def task_create_tables():
    """Crée les tables si elles n'existent pas."""
    from database.connection import create_tables
    create_tables()


def task_extract(**context):
    """Extrait les données depuis JSONPlaceholder API."""
    from ingestion.extract import extract_customers
    customers = extract_customers()
    # Passage des données via XCom
    context["ti"].xcom_push(key="raw_customers", value=customers)
    return len(customers)


def task_transform(**context):
    """Nettoie et valide les données extraites."""
    from transformation.transform import transform_customers
    raw_customers = context["ti"].xcom_pull(
        task_ids="extract",
        key="raw_customers"
    )
    clean_customers = transform_customers(raw_customers)
    context["ti"].xcom_push(key="clean_customers", value=clean_customers)
    return len(clean_customers)


def task_load(**context):
    """Charge les données transformées dans PostgreSQL."""
    from database.load import load_customers
    clean_customers = context["ti"].xcom_pull(
        task_ids="transform",
        key="clean_customers"
    )
    loaded_count = load_customers(clean_customers)
    return loaded_count


# ── Définition du DAG ────────────────────────────────────────
with DAG(
    dag_id="customer_etl_pipeline",
    default_args=DEFAULT_ARGS,
    description="Pipeline ETL : JSONPlaceholder → PostgreSQL",
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["etl", "customers", "postgresql", "data-engineering"],
) as dag:

    start = EmptyOperator(task_id="start")

    check_db = PythonOperator(
        task_id="check_database",
        python_callable=task_test_connection,
    )

    create_tables = PythonOperator(
        task_id="create_tables",
        python_callable=task_create_tables,
    )

    extract = PythonOperator(
        task_id="extract",
        python_callable=task_extract,
    )

    transform = PythonOperator(
        task_id="transform",
        python_callable=task_transform,
    )

    load = PythonOperator(
        task_id="load",
        python_callable=task_load,
    )

    end = EmptyOperator(task_id="end")

    # ── Ordre d'exécution ────────────────────────────────────
    # start → check_database → create_tables → extract → transform → load → end
    start >> check_db >> create_tables >> extract >> transform >> load >> end

