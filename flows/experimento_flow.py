"""Actividad 1: primer flow de Prefect con tracking en MLflow.

Pasos: cargar datos → entrenar y registrar en MLflow → resumen (artefacto de Prefect)

Requisitos: servicios levantados (ver services/README.md) y las variables de entorno:
    PREFECT_API_URL=http://localhost:4200/api
    MLFLOW_TRACKING_URI=http://localhost:5000

Ejecución (desde la raíz de actividad-1):
    poetry run python flows/experimento_flow.py
"""
import os

import mlflow
import yaml
from mlflow.models import infer_signature
from prefect import flow, task
from prefect.artifacts import create_markdown_artifact
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from scripts.load_data import cargar_datos as leer_datos

CONFIG = "configs/config.yaml"

# Variables del modelo. Los identificadores (RowNumber, CustomerId, Surname) no se usan.
NUMERICAS = [
    "CreditScore",
    "Age",
    "Tenure",
    "Balance",
    "NumOfProducts",
    "HasCrCard",
    "IsActiveMember",
    "EstimatedSalary",
    "Complain",
    "Satisfaction Score",
    "Point Earned",
]
CATEGORICAS = ["Geography", "Gender", "Card Type"]
OBJETIVO = "Exited"


@task
def cargar_datos(ruta):
    """Carga el CSV con scripts/load_data.py y valida sus columnas."""
    return leer_datos(ruta)


@task
def entrenar_y_registrar(df, cfg):
    """Entrena el modelo, calcula sus métricas y lo registra en MLflow. Devuelve (run_id, métricas)."""
    # 1. Partir los datos en entrenamiento y prueba.
    division = cfg["division"]
    train_df, test_df = train_test_split(
        df,
        test_size=division["test_size"],
        random_state=division["random_state"],
        stratify=df[OBJETIVO],
    )
    X_train, y_train = train_df[NUMERICAS + CATEGORICAS], train_df[OBJETIVO]
    X_test, y_test = test_df[NUMERICAS + CATEGORICAS], test_df[OBJETIVO]

    # 2. Crear el modelo: preprocesado (escalar y one-hot) + estimador.
    tipo = cfg["modelo"]["tipo"]
    parametros = cfg["modelo"].get("parametros") or {}
    if tipo == "logistic_regression":
        estimador = LogisticRegression(**parametros)
    elif tipo == "gradient_boosting":
        estimador = GradientBoostingClassifier(**parametros)
    else:
        raise ValueError(f"modelo '{tipo}' no soportado")

    preprocesado = ColumnTransformer(
        [
            ("num", StandardScaler(), NUMERICAS),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAS),
        ]
    )
    modelo = Pipeline([("preprocesado", preprocesado), ("modelo", estimador)])
    modelo.fit(X_train, y_train)

    # 3. Calcular las métricas sobre el conjunto de prueba.
    umbral = cfg["metricas"]["umbral"]
    proba = modelo.predict_proba(X_test)[:, 1]
    pred = (proba >= umbral).astype(int)
    metricas = {
        "auc": float(roc_auc_score(y_test, proba)),
        "accuracy": float(accuracy_score(y_test, pred)),
        "precision": float(precision_score(y_test, pred, zero_division=0)),
        "recall": float(recall_score(y_test, pred, zero_division=0)),
        "f1": float(f1_score(y_test, pred, zero_division=0)),
    }

    # 4. Registrar el run en MLflow. MLFLOW_TRACKING_URI, si existe, tiene prioridad sobre el YAML.
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", cfg["mlflow"]["tracking_uri"]))
    mlflow.set_experiment(cfg["mlflow"]["experimento"])
    with mlflow.start_run(run_name=cfg["mlflow"]["nombre_run"]) as run:
        mlflow.log_params({"modelo": tipo, **parametros, "semilla": division["random_state"], "umbral": umbral})
        mlflow.log_metrics(metricas)
        mlflow.sklearn.log_model(
            modelo,
            name="model",
            signature=infer_signature(X_test, proba),
            input_example=X_test.head(3),
        )
        run_id = run.info.run_id

    return run_id, metricas


@flow(name="churn-training-v1", log_prints=True)
def churn_training():
    with open(CONFIG, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    df = cargar_datos(cfg["datos"]["ruta"])
    run_id, metricas = entrenar_y_registrar(df, cfg)

    create_markdown_artifact(
        key="churn-training-v1",
        markdown=(
            "## Churn Training V1\n\n"
            f"- Modelo: `{cfg['modelo']['tipo']}`\n"
            f"- Filas: {len(df)}\n"
            f"- AUC: **{metricas['auc']:.4f}**\n"
            f"- Recall: {metricas['recall']:.4f}\n"
            f"- Run de MLflow: `{run_id}`"
        ),
    )
    print(f"Run de MLflow: {run_id} | AUC = {metricas['auc']:.4f}")
    return run_id


if __name__ == "__main__":
    churn_training()
