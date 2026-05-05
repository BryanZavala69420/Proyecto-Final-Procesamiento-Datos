# ============================================================
# EXTRACCIÓN — Fuentes: MariaDB | MongoDB | Scraping | CSV | XLSX | API
# ============================================================

import mysql.connector
import pandas as pd
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

from config import (
    MARIADB, MONGODB_URI, MONGODB_DB,
    SCRAPING_URL, API_BASE_CURRENCY, API_FALLBACK,
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
                "id_clientes":     doc.get("id_clientes"),
                "edad":            doc.get("edad"),
                "preferencias":    ", ".join(doc.get("preferencias") or []),
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
    Scraping de la tabla HTML en la app React (localhost:3000).
    Columnas: Id_transaccion, Id_Cliente, Monto, Fecha, Id_Tienda
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

    soup = BeautifulSoup(resp.text, "html.parser")
    tabla = soup.find("table")
    if tabla is None:
        raise ValueError(f"❌ [Scraping] No se encontró tabla HTML en {url}")

    headers = [th.get_text(strip=True) for th in tabla.find_all("th")]
    filas = [
        [td.get_text(strip=True) for td in tr.find_all("td")]
        for tr in tabla.find("tbody").find_all("tr")
        if tr.find_all("td")
    ]

    df = pd.DataFrame(filas, columns=headers)
    df["Monto"] = pd.to_numeric(
        df["Monto"].str.replace("$", "", regex=False), errors="coerce"
    )
    df["Id_transaccion"] = pd.to_numeric(df["Id_transaccion"], errors="coerce")
    df["Id_Cliente"]     = pd.to_numeric(df["Id_Cliente"],     errors="coerce")
    df["Id_Tienda"]      = pd.to_numeric(df["Id_Tienda"],      errors="coerce")
    df["Fecha"]          = pd.to_datetime(df["Fecha"], dayfirst=True, errors="coerce")

    print(f"✅ [Web Scraping] {len(df):,} registros extraídos de {url}")
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
