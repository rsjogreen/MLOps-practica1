# CLAUDE.md — carpeta `services/`

Guía para trabajar en esta carpeta. Léela antes de cambiar algo aquí.

## Qué es

Los servicios que usan las actividades del curso: **MLflow** (tracking y UI) y **Prefect** (orquestación de flows y su UI). Hay dos opciones de arranque: Docker Compose (`docker-compose.yml`) y sin Docker (`requirements.txt` + comandos del README). La carpeta es autocontenida: lo que se levanta aquí no debe depender de archivos dentro de `actividades/`.

## Estado actual

- **MLflow 3.17.0:** imagen oficial `ghcr.io/mlflow/mlflow:v3.17.0` (opción A) o `pip` (opción B). Verificado con ambas: `/health` responde 200.
- **Prefect 3.8.8:** imagen oficial `prefecthq/prefect:3.8.8-python3.12` (opción A) o `pip` (opción B). Verificado con ambas: `/api/health` responde `true`, y un flow de `prefect-prueba/` termina en `Completed`.

## Reglas

- **No añadir `build:` a `docker-compose.yml`.** Las imágenes son oficiales y se fijan por versión.
- **Versiones fijadas y sincronizadas.** MLflow `3.17.0` debe coincidir en `docker-compose.yml`, `requirements.txt` y `actividades/actividad-1/pyproject.toml`. Prefect `3.8.8` debe coincidir en `docker-compose.yml` y `requirements.txt`. Si cambias una, cámbiala en todos esos sitios.
- **No desactivar la verificación TLS** para saltar errores de certificado.
- **No versionar datos.** `mlflow_store/` y el volumen `prefect_data` no van a git.
- **No usar dos opciones a la vez.** Las dos usan los puertos 5000 y 4200.
- **No cambiar los puertos sin actualizar la documentación:** 5000 (MLflow) y 4200 (Prefect).
- **La documentación de esta carpeta es `README.md`.** Si cambias el comportamiento, actualízalo en el mismo cambio.

## Comandos

```bash
# Opción A
docker compose up -d                  # MLflow (5000) y Prefect (4200)
docker compose down                   # para los servicios (conserva los volúmenes)
curl http://localhost:5000/health
curl http://localhost:4200/api/health

# Opción B (desde services/, con el entorno activado)
pip install -r requirements.txt
mlflow server --host 127.0.0.1 --port 5000 --backend-store-uri sqlite:///mlflow_store/mlflow.db --artifacts-destination mlflow_store/artifacts --serve-artifacts
prefect server start --host 127.0.0.1 --port 4200
```

## Qué no hacer sin preguntar

- No borrar `mlflow_store/`: contiene los runs del curso.
- No ejecutar `docker compose down -v`: borra el volumen `prefect_data` con los runs de Prefect.
- No cambiar la versión de MLflow o Prefect sin revisar `actividad-1`.
- No añadir servicios nuevos sin acordarlo: hoy todo corre en local.
