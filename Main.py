# PIPELINE ETL — ANÁLISIS GLOBAL DE RETAIL
# Programación para el Procesamiento de Datos
# Fuentes: MariaDB, MongoDB, Web Scraping, CSV, XLSX, API

#imports
import os
import sys

import pandas as pd
#SE EXTRAE TODOOOO DEL config.py
from config import CSV_CLIENTES, XLSX_KPIS
from extraccion import (
    extraer_mariadb,
    extraer_mongodb,
    extraer_scraping,
    extraer_csv,
    extraer_xlsx,
    extraer_api,
)
#SE EXTRAE TODOOOO DEL limpieza.py

from limpieza import (
    reporte_calidad,
    limpiar_ventas,
    limpiar_perfiles,
    limpiar_clientes,
    normalizar,
)
#SE EXTRAE TODOOOO DEL transformacion.py

from transformacion import (
    enriquecer,
    segmentar,
    agregar_monedas,
    aplicar_pca,
    aplicar_kmeans,
)
#SE EXTRAE TODOOOO DEL visualizacion.py
from visualizacion import generar_dashboard


# PASO 1 - EXTRACCIÓN
print("\n" + "-" * 55)
print("  PASO 1 - EXTRACCIÓN")
print("-" * 55)

try:
    df_ventas = extraer_mariadb()
except Exception as e:
    print(e)
    sys.exit(1)

try:
    df_perfiles = extraer_mongodb()
except Exception as e:
    print(e)
    sys.exit(1)

try:
    df_scraping = extraer_scraping()
except Exception as e:
    print(f"{e}  Se continúa sin datos de scraping")
    df_scraping = pd.DataFrame()

try:
    df_clientes = extraer_csv(CSV_CLIENTES)
except FileNotFoundError as e:
    print(e)
    sys.exit(1)
except Exception as e:
    print(e)
    sys.exit(1)

try:
    df_kpis = extraer_xlsx(XLSX_KPIS)
except FileNotFoundError as e:
    print(e)
    sys.exit(1)
except Exception as e:
    print(e)
    sys.exit(1)

tipos_cambio = extraer_api()



# PASO 2 — CALIDAD (estado sucio)
print("\n" + "-" * 55)
print("  PASO 2 — REPORTE DE CALIDAD (antes de limpiar)")
print("-" * 55)

reporte_calidad(df_ventas,   "MariaDB  — ventas_chingonas")
reporte_calidad(df_perfiles, "MongoDB  — perfiles")
reporte_calidad(df_clientes, "CSV      — clientes sucios")
if not df_scraping.empty:
    reporte_calidad(df_scraping, "Scraping — localhost:3000")
reporte_calidad(df_kpis,     "XLSX     — KPIs")


# PASO 3 - LIMPIEZA
print("\n" + "-" * 55)
print("  PASO 3 - LIMPIEZA")
print("-" * 55)

try:
    df_ventas   = limpiar_ventas(df_ventas)
    df_perfiles = limpiar_perfiles(df_perfiles)
    df_clientes = limpiar_clientes(df_clientes)
    df_clientes = normalizar(df_clientes)
except (ValueError, KeyError) as e:
    print(e)
    sys.exit(1)


# PASO 4 - TRANSFORMACIÓN
print("\n" + "-" * 55)
print("  PASO 4 — TRANSFORMACIÓN")
print("-" * 55)

try:
    df_master = enriquecer(df_ventas, df_perfiles, df_clientes)
    df_master = segmentar(df_master)
    df_master = agregar_monedas(df_master, tipos_cambio)
    df_master, pca_obj, varianza, feats_pca = aplicar_pca(df_master)
    df_master = aplicar_kmeans(df_master)
except (ValueError, KeyError) as e:
    print(e)
    sys.exit(1)


# PASO 5 — VISUALIZACIÓN
print("\n" + "-" * 55)
print("  PASO 5 - DASHBOARD")
print("-" * 55)

try:
    generar_dashboard(df_master, df_kpis, pca_obj, varianza, feats_pca)
except (KeyError, ValueError) as e:
    print(f"Advertencia en el Dashboard: No se pudo generar: {e}")


# PASO 6 - EXPORTAR ARCHIVO MAESTRO
print("\n" + "-" * 55)
print("  PASO 6 — EXPORTACIÓN")
print("-" * 55)

try:
    df_master.to_csv("data_master_clean.csv", index=False, encoding="utf-8-sig")
    df_master.to_parquet("data_master_clean.parquet", index=False)
    print(
        f"data_master_clean.csv     "
        f"({os.path.getsize('data_master_clean.csv') / 1024:.0f} KB)"
    )
    print(
        f" data_master_clean.parquet "
        f"({os.path.getsize('data_master_clean.parquet') / 1024:.0f} KB)"
    )
except Exception as e:
    print(f"Erro de exportación: Error al guardar archivos: {e}")


# PASO 7 — RESUMEN EJECUTIVO
print(f"""
{"-" * 58}
  RESUMEN EJECUTIVO — PIPELINE ETL
{"-" * 58}
  Fuentes        : MariaDB · MongoDB · Scraping · CSV · XLSX · API
  Registros      : {len(df_master):,}
  Columnas       : {df_master.shape[1]}
  Varianza PCA   : {sum(varianza) * 100:.1f}% (3 componentes)
  Segmentos      : {df_master["segmento_cliente"].nunique()}
  Clusters       : {df_master["cluster"].nunique()}
  Monto total    : ${df_master["monto"].sum():,.0f} USD
{"-" * 58}
""")
