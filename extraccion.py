# ============================================================
# EXTRACCIÓN — Fuentes: MariaDB | MongoDB | Scraping | CSV | XLSX | API
# ============================================================

import mysql.connector
import pandas as pd
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

from config import (
    API_BASE_CURRENCY,
    API_FALLBACK,
    MARIADB,
    MONGODB_DB,
    MONGODB_URI,
    SCRAPING_URL,
)


def extraer_mariadb() -> pd.DataFrame:
    """
    Conexión a MariaDB.
    Base: ventas | Tabla: ventas_chingonas
    Columnas: id_transaccion, id_cliente, monto, fecha, id_tienda
    """
    try:
        conn = mysql.connector.connect(**MARIADB)
        df = pd.read_sql("SELECT * FROM ventas_chingonas", conn)
        conn.close()
        print(f"✅ [MariaDB] {len(df):,} registros extraídos de ventas_chingonas")
        return df
    except mysql.connector.Error as e:
        raise ConnectionError(f"❌ [MariaDB] Error de conexión: {e}") from e
    except Exception as e:
        raise RuntimeError(f"❌ [MariaDB] Error inesperado: {e}") from e


def extraer_mongodb() -> pd.DataFrame:
    """
    Conexión a MongoDB (puerto 27017).
    Base: ventas | Colección: perfiles
    """
    try:
        cliente = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        cliente.server_info()  # dispara error si no hay conexión
        db = cliente[MONGODB_DB]
        col = db["perfiles"]

        documentos = list(col.find({}, {"_id": 0}))
        cliente.close()

        registros = [
            {
                "id_clientes": doc.get("id_clientes"),
                "edad": doc.get("edad"),
                "preferencias": ", ".join(doc.get("preferencias") or []),
                "geolocalizacion": doc.get("geolocalizacoon"),  # typo en la fuente
            }
            for doc in documentos
        ]

        df = pd.DataFrame(registros)
        print(f"✅ [MongoDB] {len(df):,} perfiles extraídos")
        return df
    except Exception as e:
        raise ConnectionError(f"❌ [MongoDB] Error de conexión: {e}") from e


def extraer_scraping(url: str = SCRAPING_URL) -> pd.DataFrame:
    """
    Consume directamente el API REST que alimenta la tabla React.
    Evita el problema de renderizado JS de BeautifulSoup.
    """
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise ConnectionError(f"❌ [Scraping] No se pudo conectar a {url}")
    except requests.exceptions.Timeout:
        raise TimeoutError(f"❌ [Scraping] Timeout al conectar con {url}")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"❌ [Scraping] HTTP error: {e}") from e

    data = resp.json()
    df = pd.DataFrame(data)

    # Renombrar columnas al formato esperado
    df = df.rename(
        columns={
            "id_transaccion": "Id_transaccion",
            "id_cliente": "id_clientes",
            "monto": "Monto",
            "fecha": "Fecha",
            "id_tienda": "Id_Tienda",
        }
    )

    df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce")
    df["Id_transaccion"] = pd.to_numeric(df["Id_transaccion"], errors="coerce")
    df["id_cliente"] = pd.to_numeric(df["id_clientes"], errors="coerce")
    df["Id_Tienda"] = pd.to_numeric(df["Id_Tienda"], errors="coerce")
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    data = resp.json()
    df = pd.DataFrame(data)

    print(f"✅ [Web Scraping→API] {len(df):,} registros extraídos de {url}")
    return df


def extraer_csv(ruta: str) -> pd.DataFrame:
    """
    Lee el CSV de clientes con datos sucios:
    nulos ~10%, duplicados ~5%, fechas inconsistentes, países mal escritos.
    """
    try:
        df = pd.read_csv(ruta)
    except FileNotFoundError:
        raise FileNotFoundError(f"❌ [CSV] Archivo no encontrado: {ruta}")
    except Exception as e:
        raise RuntimeError(f"❌ [CSV] Error al leer archivo: {e}") from e

    print(f"✅ [CSV] {len(df):,} registros cargados")
    print(f"   Nulos:\n{df.isnull().sum().to_string()}")
    return df


def extraer_xlsx(ruta: str) -> pd.DataFrame:
    """Lee los KPIs de negocio por región desde Excel."""
    try:
        df = pd.read_excel(ruta, sheet_name="KPIs", engine="openpyxl")
    except FileNotFoundError:
        raise FileNotFoundError(f"❌ [XLSX] Archivo no encontrado: {ruta}")
    except Exception as e:
        raise RuntimeError(f"❌ [XLSX] Error al leer archivo: {e}") from e

    print(f"✅ [XLSX] {len(df):,} KPIs regionales cargados")
    return df


def extraer_api(base: str = API_BASE_CURRENCY) -> dict:
    """Consume exchangerate-api para tipos de cambio. Fallback si no hay internet."""
    try:
        resp = requests.get(
            f"https://api.exchangerate-api.com/v4/latest/{base}", timeout=8
        )
        if resp.status_code == 200:
            rates = resp.json()["rates"]
            print(
                f"✅ [API] Tipos de cambio obtenidos — "
                f"MXN={rates['MXN']} EUR={rates['EUR']}"
            )
            return rates
    except requests.exceptions.RequestException as e:
        print(f"⚠️  [API] Error de red ({e}), usando fallback")
    except Exception as e:
        print(f"⚠️  [API] Error inesperado ({e}), usando fallback")

    print("⚠️  [API] Sin conexión, usando fallback")
    return API_FALLBACK
