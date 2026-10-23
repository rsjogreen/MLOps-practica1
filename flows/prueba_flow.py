"""Prueba de Prefect y MLflow. No usa el dataset ni entrena ningún modelo.

Pasos: sumar → registrar un experimento en MLflow

Requisitos: servicios levantados (ver services/README.md) y las variables:
    PREFECT_API_URL=http://localhost:4200/api
    MLFLOW_TRACKING_URI=http://localhost:5000

Ejecución (desde la raíz de actividad-1):
    poetry run python flows/prueba_flow.py
Después, el run aparece en http://localhost:4200/runs con estado Completed
y el experimento "prueba-validacion" aparece en http://localhost:5000.
"""
import mlflow
from prefect import flow, task


@task
def sumar(n: int) -> int:
    return sum(range(1, n + 1))


@flow(name="prueba", log_prints=True)
def prueba(n: int = 5) -> int:
    total = sumar(n)
    print(f"Suma de 1 a {n} = {total}")

    mlflow.set_experiment("prueba-validacion")
    with mlflow.start_run(run_name="prueba-mlflow"):
        mlflow.log_param("n", n)
        mlflow.log_metric("suma", total)
    print("Experimento registrado en MLflow")
    return total


if __name__ == "__main__":
    prueba()
