"""Airflow DAG for ETL pipeline."""
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def extract():
    return []


def transform(data):
    return data


with DAG("etl_pipeline", start_date=datetime(2024, 1, 1), schedule="@daily") as dag:
    t1 = PythonOperator(task_id="extract", python_callable=extract)
    t2 = PythonOperator(task_id="transform", python_callable=transform)
    t1 >> t2
