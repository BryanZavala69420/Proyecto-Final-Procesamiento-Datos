# ============================================================
# LIMPIEZA — Transformación y calidad de datos
# ============================================================

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from config import MAPA_PAISES, COLS_NORMALIZAR

# Reporte de calidad
def reporte_calidad(df: pd.DataFrame, nombre: str) -> None:
    """Imprime un resumen de nulos, duplicados y forma del DataFrame."""
    print(f"\n{'-' * 55}")
    print(f"  CALIDAD: {nombre}")
    print(
        f"  Filas: {len(df):,} | Columnas: {df.shape[1]} "
        f"| Duplicados: {df.duplicated().sum():,}"
    )
    nulos = df.isnull().sum()
    for col, n in nulos.items():
        pct = n / len(df) * 100
        bar = "█" * int(pct / 5)
        print(f"    {col:<28} {n:>5} ({pct:5.1f}%) {bar}")


# Limpieza por fuente
def limpiar_ventas(df: pd.DataFrame) -> pd.DataFrame:
    """
    MariaDB — ventas_chingonas:
    - Elimina duplicados por id_transaccion
    - Imputa monto nulo con mediana
    - Convierte fecha a datetime64
    - Elimina filas sin id_cliente (llave de join)
    - Imputa id_tienda con moda
    """
    if df.empty:
        raise ValueError("Error de limpieza en MariaDB: DataFrame vacío")

    n0 = len(df)
    df = df.drop_duplicates(subset="id_transaccion")
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["monto"] = df["monto"].fillna(df["monto"].median())
    df = df.dropna(subset=["id_cliente"])
    df["id_cliente"] = df["id_cliente"].astype(int)
    moda_tienda = df["id_tienda"].mode()
    if moda_tienda.empty:
        raise ValueError("Error de limpieza en MariaDB: No se pudo calcular moda de id_tienda")
    df["id_tienda"] = df["id_tienda"].fillna(moda_tienda[0]).astype(int)

    print(f"Exito en limpieza de MariaDB:  {n0:,} → {len(df):,} filas")
    return df.reset_index(drop=True)


def limpiar_perfiles(df: pd.DataFrame) -> pd.DataFrame:
    """
    MongoDB — perfiles:
    - Normaliza edades fuera de rango (1-110) con mediana
    - Rellena geolocalización nula con 'Desconocida'
    """
    if df.empty:
        raise ValueError("Error de limpieza en MongoDB: DataFrame vacío")

    df["edad"] = pd.to_numeric(df["edad"], errors="coerce")
    med = df.loc[df["edad"].between(1, 110), "edad"].median()

    if pd.isna(med):
        print("Advertencia: No hay edades válidas para calcular mediana en MongoDB")
        med = 30  # valor por defecto razonable

    df.loc[~df["edad"].between(1, 110), "edad"] = np.nan
    df["edad"] = df["edad"].fillna(med).astype(int)
    df["geolocalizacion"] = df["geolocalizacion"].fillna("Desconocida")

    print(f"Limpieza de MongoDB exitosa: {len(df):,} perfiles listos")
    return df


def limpiar_clientes(df: pd.DataFrame) -> pd.DataFrame:
    """
    CSV — clientes sucios:
    - Elimina duplicados por Customer_ID
    - Normaliza nombres de países
    - Convierte Timestamp DD/MM/YYYY a datetime64
    - Imputa numéricos con mediana
    """
    if df.empty:
        raise ValueError("Limpieza del dataFrame vacío")

    n0 = len(df)
    df = df.drop_duplicates(subset="Customer_ID")
    df["pais"] = (
        df["pais"].str.lower().str.strip().map(MAPA_PAISES).fillna("Desconocido")
    )
    df["Timestamp"] = pd.to_datetime(
        df["Timestamp"], format="%d/%m/%Y", errors="coerce"
    )
    for col in ["ingresos", "puntos_lealtad", "gastos_mensuales"]:
        if col not in df.columns:
            print(f"Advertencia en la Limpieza del CSV: Columna '{col}' no encontrada, se omite")
            continue
        df[col] = df[col].fillna(df[col].median())

    print(f"Limpieza CSV exitosa: {n0:,} → {len(df):,} filas")
    return df.reset_index(drop=True)


# Normalización
def normalizar(df: pd.DataFrame, cols: list = COLS_NORMALIZAR) -> pd.DataFrame:
    """Aplica MinMaxScaler y agrega columnas _norm al DataFrame."""
    cols_presentes = [c for c in cols if c in df.columns]
    cols_faltantes  = [c for c in cols if c not in df.columns]

    if cols_faltantes:
        print(f"Advertencia:  Min-Max Columnas no encontradas (se omiten): {cols_faltantes}")
    if not cols_presentes:
        raise ValueError("Error en el Min-Max: ninguna columna válida para normalizar")

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df[cols_presentes])
    for i, col in enumerate(cols_presentes):
        df[f"{col}_norm"] = scaled[:, i]

    print(f"Exito en el Min-Max Normalizado: {cols_presentes}")
    return df
