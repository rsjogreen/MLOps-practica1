 # Guía de ejecución

## 1. Crear el repositorio en GitHub

Un integrante crea el repositorio desde el navegador:

1. Entra en [https://github.com/new](https://github.com/new).
2. En **Repository name**, escribe `PROJECTO_DE_EQUIPO`.
3. Marca **Add a README file**.
4. En **Add .gitignore**, selecciona la plantilla **Python**.
5. Pulsa **Create repository**.

## 2. Agregar colaboradores

El mismo integrante agrega al resto del grupo:

1. En el repositorio, entra en **Settings → Collaborators** (en el menú lateral, dentro de **Access**).
2. Pulsa **Add people**, escribe el usuario de GitHub de cada compañero y selecciona **Add**.
3. Cada compañero debe aceptar la invitación por correo o desde **GitHub → Notifications** antes de poder hacer `push`.

## 3. Clonar el repositorio

El dueño del repositorio y cada colaborador clonan el proyecto desde PowerShell, en la carpeta donde guardan sus proyectos:

```powershell
git clone URL_DEL_REPOSITORIO.git
cd MY_REPO
```

Reemplaza `URL_DEL_REPOSITORIO.git` por la URL del repositorio y `MY_REPO` por el nombre de la carpeta creada al clonarlo.

## 4. Crear la estructura del proyecto

Un integrante crea la estructura de carpetas del proyecto y sube los cambios. Git no versiona carpetas vacías: agrega un archivo `__init__.py` a cada carpeta que deba versionarse como paquete de Python.

## 5. Completar `.gitignore`

Añade estas entradas al `.gitignore`, ya que la plantilla de Python no las cubre:

```gitignore
mlruns/
mlflow.db
mlflow_store/
```

## 6. Crear el entorno con Poetry

Genera `pyproject.toml` sin preguntas y fija la versión de Python del entorno:

```powershell
poetry init --no-interaction --name mi-proyecto-mlops --python ">=3.12,<3.15"
poetry env use 3.12
```

Si `poetry env use 3.12` falla, instala Python 3.12 o indica la ruta completa a su `python.exe`.

## 7. Instalar las dependencias

Añade las dependencias con versiones fijadas (`==`). Cada comando `poetry add` actualiza `pyproject.toml`, guarda las versiones resueltas en `poetry.lock` e instala los paquetes en el entorno virtual:

```powershell
poetry add "prefect==3.8.8" "mlflow==3.17.0" "scikit-learn==1.9.1" "pandas==3.0.6" "numpy==2.5.4" "pyyaml==6.0.3"
poetry add --group dev "pytest==9.1.1"
```

desde la raiz del repositorio ejecutar

$env:PREFECT_API_URL = "http://localhost:4200/api"
$env:MLFLOW_TRACKING_URI = "http://localhost:5000"
poetry run python flows/prueba_flow.py