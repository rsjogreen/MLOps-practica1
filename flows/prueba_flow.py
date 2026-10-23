"""Prueba de Prefect y MLflow. No usa el dataset ni entrena ningún modelo.

Pasos: sumar → registrar un experimento en MLflow

Requisitos: servicios levantados (ver services/README.md). Por defecto se conectan
en http://127.0.0.1:4200/api y http://127.0.0.1:5000; las variables de entorno
PREFECT_API_URL y MLFLOW_TRACKING_URI permiten sobrescribir esas direcciones.

Ejecución (desde la raíz del repositorio):
    poetry run python flows/prueba_flow.py
Después, el run aparece en http://localhost:4200/runs con estado Completed
y el experimento "prueba-validacion" aparece en http://localhost:5000.
"""
import os

import mlflow
from prefect import flow, task
from prefect.settings import PREFECT_API_URL, temporary_settings

os.environ.setdefault("MLFLOW_SUPPRESS_PRINTING_URL_TO_STDOUT", "true")


@task
def sumar(n: int) -> int:
    return sum(range(1, n + 1))


@flow(name="prueba", log_prints=True)
def prueba(n: int = 5) -> int:
    total = sumar(n)
    print(f"Suma de 1 a {n} = {total}")

    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI") or "http://127.0.0.1:5000")
    mlflow.set_experiment("prueba-validacion")
    with mlflow.start_run(run_name="prueba-mlflow"):
        mlflow.log_param("n", n)
        mlflow.log_metric("suma", total)
    print("Experimento registrado en MLflow")
    return total


if __name__ == "__main__":
    api_url = os.environ.get("PREFECT_API_URL") or "http://127.0.0.1:4200/api"
    with temporary_settings({PREFECT_API_URL: api_url}):
        prueba()
