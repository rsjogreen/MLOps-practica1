"""Genera un dataset sintético con el mismo esquema que el de churn.

Sirve para probar la pipeline sin descargar el dataset real. Con la misma semilla y los
mismos parámetros, el CSV es idéntico en cada ejecución. `Complain` se genera independiente
de `Exited`, así que no reproduce la fuga de datos del dataset real.

Ejecución (desde la raíz de actividad-1):
    poetry run python scripts/generate_data.py

Para cambiar los parámetros, edita los valores en `main()`. No sobrescribe un CSV que ya exista.
"""
from pathlib import Path

import numpy as np
import pandas as pd

APELLIDOS = ["Smith", "Johnson", "Garcia", "Martin", "Rossi", "Mueller", "Silva", "Kim"]
GEOGRAFIA = ["France", "Spain", "Germany"]
TIPOS_TARJETA = ["DIAMOND", "GOLD", "SILVER", "PLATINUM"]


def generar_datos(filas, proporcion_objetivo, semilla):
    """Devuelve un DataFrame con las columnas del dataset de churn.

    `proporcion_objetivo` es la fracción de clientes con `Exited = 1`. Los clientes con
    mayor puntuación de abandono son los que se marcan, así que la proporción sale exacta.
    """
    if filas < 2:
        raise ValueError("Se necesitan al menos 2 filas.")
    if not 0 < proporcion_objetivo < 1:
        raise ValueError("La proporción de la clase objetivo debe estar entre 0 y 1.")

    rng = np.random.default_rng(semilla)
    n = filas

    edad = rng.integers(18, 93, n)
    activo = rng.integers(0, 2, n)
    geografia = rng.choice(GEOGRAFIA, n, p=[0.5, 0.25, 0.25])
    # Un 36 % de clientes sin saldo, como en el dataset real.
    saldo = np.where(rng.random(n) < 0.36, 0.0, rng.normal(120_000, 30_000, n).clip(0))

    # Puntuación de abandono: edad, actividad, geografía y saldo, más ruido.
    puntuacion = (
        0.04 * (edad - 45)
        - 0.8 * activo
        + 0.5 * (geografia == "Germany")
        + 0.000004 * (saldo - 120_000)
        + rng.normal(0, 1, n)
    )
    exited = np.zeros(n, dtype=int)
    exited[np.argsort(-puntuacion)[: max(1, round(n * proporcion_objetivo))]] = 1

    return pd.DataFrame(
        {
            "RowNumber": np.arange(1, n + 1),
            "CustomerId": 15_600_000 + np.arange(n),
            "Surname": rng.choice(APELLIDOS, n),
            "CreditScore": rng.integers(350, 851, n),
            "Geography": geografia,
            "Gender": rng.choice(["Female", "Male"], n),
            "Age": edad,
            "Tenure": rng.integers(0, 11, n),
            "Balance": np.round(saldo, 2),
            "NumOfProducts": rng.choice([1, 2, 3, 4], n, p=[0.5, 0.46, 0.02, 0.02]),
            "HasCrCard": rng.integers(0, 2, n),
            "IsActiveMember": activo,
            "EstimatedSalary": np.round(rng.uniform(11, 200_000, n), 2),
            "Complain": (rng.random(n) < 0.2).astype(int),
            "Satisfaction Score": rng.integers(1, 6, n),
            "Card Type": rng.choice(TIPOS_TARJETA, n),
            "Point Earned": rng.integers(120, 1001, n),
            "Exited": exited,
        }
    )


def main():
    filas = 10000
    proporcion_objetivo = 0.2
    semilla = 42
    ruta = Path("data") / "churn_sintetico.csv"

    if ruta.exists():
        raise SystemExit(f"Ya existe {ruta}. Bórralo si quieres regenerarlo.")

    df = generar_datos(filas, proporcion_objetivo, semilla)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False)
    print(f"Generado {ruta}")
    print(f"  filas: {len(df)}  columnas: {df.shape[1]}  semilla: {semilla}")
    print(f"  proporción de Exited = 1: {df['Exited'].mean():.3f}")


if __name__ == "__main__":
    main()
