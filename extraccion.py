# EXTRACCIÓN
# Fuentes: MariaDB, MongoDB, web Scraping, archivo CSV, archivo XLSX, API

# imports
import mysql.connector
import pandas as pd
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# variables necesarias para que funcione, esto se toma del config.py
from config import (
    API_BASE_CURRENCY,
    API_FALLBACK,
    MARIADB,
    MONGODB_DB,
    MONGODB_URI,
    SCRAPING_URL,
)


# funcion para extrar de Mysql/MariaDB
def extraer_mariadb() -> pd.DataFrame:
    # conectar a MySQL/MariaDB a la base de datos ventas con la tabla ventas_chingonas
    # Base: ventas | Tabla: ventas_chingonas
    # Columnas: id_transaccion, id_cliente, monto, fecha, id_tienda

    try:
        conn = mysql.connector.connect(**MARIADB)
        df = pd.read_sql("SELECT * FROM ventas_chingonas", conn)
        conn.close()
        print(f"{len(df):,} registros extraídos de ventas_chingonas")
        return df

    except mysql.connector.Error as e:
        raise ConnectionError(f"Error de conexión en MariaDB/MySQL: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Error inesperado en MariaDB/MySQL: {e}") from e


# Funcion para extrer de MongoDB
def extraer_mongodb() -> pd.DataFrame:
    # Conectar a MongoDB base de datos admin y coleccion perfiles_usuarios
    # Conexión a MongoDB (puerto 27017).
    # Base: admin | Colección: perfiles_usuarios
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
        print(f"{len(df):,} perfiles extraídos")
        return df
    except Exception as e:
        raise ConnectionError(f"Error de conexión en MongoDB: {e}") from e


# Funcion para extraer de la WEB
def extraer_scraping(url: str = SCRAPING_URL) -> pd.DataFrame:

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()

    except requests.exceptions.ConnectionError:
        raise ConnectionError(f"No se pudo conectar a: {url}")

    except requests.exceptions.Timeout:
        raise TimeoutError(f"Timeout al conectar con: {url}")

    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"HTTP error: {e}") from e

    data = resp.json()

    df = pd.DataFrame(data)

    df = df.rename(
        columns={
            "id_transaccion": "Id_transaccion",
            "id_clientes": "Id_Cliente",
            "monto": "Monto",
            "fecha": "Fecha",
            "id_tienda": "Id_Tienda",
        }
    )

    # Conversión de tipos
    df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce")

    df["Id_transaccion"] = pd.to_numeric(df["Id_transaccion"], errors="coerce")

    df["Id_Cliente"] = pd.to_numeric(df["Id_Cliente"], errors="coerce")

    df["Id_Tienda"] = pd.to_numeric(df["Id_Tienda"], errors="coerce")

    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

    print(f"{len(df):,} registros extraídos desde API")

    return df


# funcion para extraer el CSV
def extraer_csv(ruta: str) -> pd.DataFrame:
    # Lee el CSV de clientes con datos sucios:
    # nulos 10%, duplicados 5%, fechas inconsistentes, países mal escritos.
    try:
        df = pd.read_csv(ruta)
    except FileNotFoundError:
        raise FileNotFoundError(f"Erroe en el CSV: Archivo no encontrado: {ruta}")
    except Exception as e:
        raise RuntimeError(f"Error en el CSV: Error al leer archivo: {e}") from e

    print(f"{len(df):,} Los registros fueron cargados")
    print(f"   Nulos:\n{df.isnull().sum().to_string()}")
    return df


# Funcion para extraer el XLSX, excel pues.
def extraer_xlsx(ruta: str) -> pd.DataFrame:
    """Lee los KPIs de negocio por región desde Excel."""
    try:
        df = pd.read_excel(ruta, sheet_name="KPIs", engine="openpyxl")
    except FileNotFoundError:
        raise FileNotFoundError(f"Error del excel: Archivo no encontrado: {ruta}")
    except Exception as e:
        raise RuntimeError(f"Error del excel: Error al leer archivo: {e}") from e

    print(f"{len(df):,} Los KPIs regionales cargados")
    return df


# funcion para extraer la API de las monedas y reglas del negocio
def extraer_api(base: str = API_BASE_CURRENCY) -> dict:
    # """Consume exchangerate-api para tipos de cambio. Fallback si no hay internet."""
    try:
        resp = requests.get(
            f"https://api.exchangerate-api.com/v4/latest/{base}", timeout=8
        )
        if resp.status_code == 200:
            rates = resp.json()["rates"]
            print(f"Tipos de cambio obtenidos — MXN={rates['MXN']} EUR={rates['EUR']}")
            return rates
    except requests.exceptions.RequestException as e:
        print(f"Error de red ({e}), usando fallback")
    except Exception as e:
        print(f"Error inesperado ({e}), usando fallback")

    print("Sin conexión, usando fallback")
    return API_FALLBACK
