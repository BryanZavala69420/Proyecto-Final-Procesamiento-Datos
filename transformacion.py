# TRANSFORMACIÓN Join, segmentación, moneda, PCA, K-Means
#Imports variables
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
#variables necesarias para que funcione, esto se toma del config.py
from config import PCA_N_COMPONENTES, PCA_FEATURES, KMEANS_N_CLUSTERS


# Join multifuente
def enriquecer(
    ventas: pd.DataFrame,
    perfiles: pd.DataFrame,
    clientes: pd.DataFrame,
) -> pd.DataFrame:
    #JOIN 1: ventas (MariaDB) ← perfiles (MongoDB) por id_cliente
    #JOIN 2: resultado ← clientes (CSV) por id_cliente = Customer_ID
    #condicional para ver si hay algo en la base de datos ventas
    if ventas.empty:
        raise ValueError("DataFrame de ventas vacío, no hay nada we.")
    #hace el merge
    df = ventas.merge(
        perfiles, left_on="id_cliente", right_on="id_clientes", how="left"
    )
    df = df.merge(
        clientes.rename(columns={"Customer_ID": "id_cliente"}),
        on="id_cliente",
        how="left",
    )
    print(
        f"DataFrame maestro: {df.shape[0]:,} filas × {df.shape[1]} columnas"
    )
    return df


# Segmentación de clientes
def segmentar(df: pd.DataFrame) -> pd.DataFrame:
    #Crea segmento_cliente con np.where:
      #Premium Joven   : monto > 7000 y edad <= 35
      #Premium Senior  : monto > 7000 y edad >  35
      #Estándar Joven  : monto 3000-7000 y edad <= 35
      #Estándar Senior : monto 3000-7000 y edad >  35
     # Básico          : monto < 3000
    if "monto" not in df.columns:
        raise KeyError("Error en la segmentación: Columna 'monto' no encontrada")
    if "edad" not in df.columns:
        raise KeyError("Error en la segmentacion: Columna 'edad' no encontrada")

    g = df["monto"]
    e = df["edad"].fillna(df["edad"].median())

    df["segmento_cliente"] = np.where(
        (g > 7000) & (e <= 35), "Premium Joven",
        np.where(
            (g > 7000) & (e > 35), "Premium Senior",
            np.where(
                g.between(3000, 7000) & (e <= 35), "Estándar Joven",
                np.where(
                    g.between(3000, 7000) & (e > 35), "Estándar Senior",
                    "Básico"
                ),
            ),
        ),
    )
    print("Segmentacion existosa, ganamos:", df["segmento_cliente"].value_counts().to_dict())
    return df


# Conversión de moneda
def agregar_monedas(df: pd.DataFrame, tipos_cambio: dict) -> pd.DataFrame:
    """Agrega columnas monto_mxn y monto_eur usando los tipos de cambio."""
    if "monto" not in df.columns:
        raise KeyError("Error: Columna 'monto' no encontrada")

    df["monto_mxn"] = (df["monto"] * tipos_cambio.get("MXN", 17.2)).round(2)
    df["monto_eur"] = (df["monto"] * tipos_cambio.get("EUR", 0.92)).round(2)
    print("Exito, tremendo ganador: monto_mxn y monto_eur agregados")
    return df


# PCA
def aplicar_pca(
    df: pd.DataFrame,
    n: int = PCA_N_COMPONENTES,
    features: list = PCA_FEATURES,
):
    
    #Estandariza con Z-score y aplica PCA sobre variables de comportamiento.
    #Retorna (df_con_PCs, objeto_pca, varianza_explicada, features_usados).
   
    feats = [c for c in features if c in df.columns]
    if not feats:
        raise ValueError("Erroe en el PCA: Ninguna feature válida encontrada en el DataFrame")
    if len(feats) < n:
        raise ValueError(
            f"Error en el PCA: Se necesitan al menos {n} features, "
            f"solo se encontraron {len(feats)}: {feats}"
        )

    sub = df[feats].dropna()
    if sub.empty:
        raise ValueError("Error en el PCA: No hay filas completas para aplicar PCA")

    idx = sub.index
    X = StandardScaler().fit_transform(sub)
    pca = PCA(n_components=n, random_state=42)
    comps = pca.fit_transform(X)
    var = pca.explained_variance_ratio_

    print(f"Exito en el PCA: Varianza explicada: {[f'{v * 100:.1f}%' for v in var]}")
    print(f"   Acumulada: {sum(var) * 100:.1f}%")

    for i in range(n):
        df.loc[idx, f"PC{i + 1}"] = comps[:, i]

    return df, pca, var, feats


# K-Means
def aplicar_kmeans(
    df: pd.DataFrame,
    n_clusters: int = KMEANS_N_CLUSTERS,
    cols_pc: list = None,
) -> pd.DataFrame:
   # """Aplica K-Means sobre las componentes principales PC1, PC2, PC3."""
    if cols_pc is None:
        cols_pc = ["PC1", "PC2", "PC3"]

    cols_faltantes = [c for c in cols_pc if c not in df.columns]
    if cols_faltantes:
        raise KeyError(f"Error en el K-Means: Columnas faltantes: {cols_faltantes}")

    mask = df[cols_pc].notna().all(axis=1)
    if mask.sum() == 0:
        raise ValueError("Error en el K-Means:  No hay filas completas en las PCs")

    km = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    df.loc[mask, "cluster"] = km.fit_predict(df.loc[mask, cols_pc])
    df["cluster"] = df["cluster"].fillna(-1).astype(int)

    print(f"Exito en el K-means: {n_clusters} clusters asignados")
    return df
