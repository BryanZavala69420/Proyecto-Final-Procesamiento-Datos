# ============================================================
# CONFIG — Constantes globales del pipeline ETL
# ============================================================

import warnings
import matplotlib
import seaborn as sns

matplotlib.use("Agg")
warnings.filterwarnings("ignore")
sns.set_theme(style="darkgrid")

# ── Conexiones ───────────────────────────────────────────────
MARIADB = {
    "host": "localhost",
    "user": "ernesto",
    "password": "030224",
    "database": "ventas",
}

MONGODB_URI = "mongodb://localhost:27017/"
MONGODB_DB  = "ventas"

SCRAPING_URL = "http://localhost:3000"

# ── Rutas de archivos ─────────────────────────────────────────
CSV_CLIENTES  = "datos_clientes_sucios.csv"
XLSX_KPIS     = "metas_anuales.xlsx"

# ── API ───────────────────────────────────────────────────────
API_BASE_CURRENCY = "USD"
API_FALLBACK = {"USD": 1, "MXN": 17.2, "EUR": 0.92, "ARS": 900, "BRL": 4.97}

# ── Dashboard ────────────────────────────────────────────────
COLORES = {
    "Premium Joven":   "#e74c3c",
    "Premium Senior":  "#c0392b",
    "Estándar Joven":  "#3498db",
    "Estándar Senior": "#2980b9",
    "Básico":          "#95a5a6",
}
BG = "#1a1a2e"
AX = "#16213e"
GR = "#0f3460"
WH = "white"

# ── Normalización ─────────────────────────────────────────────
COLS_NORMALIZAR = ["ingresos", "puntos_lealtad", "gastos_mensuales"]

# ── PCA ───────────────────────────────────────────────────────
PCA_N_COMPONENTES = 3
PCA_FEATURES = [
    "monto", "edad", "ingresos", "puntos_lealtad",
    "gastos_mensuales", "monto_mxn", "monto_eur",
    "ingresos_norm", "puntos_lealtad_norm", "gastos_mensuales_norm",
]

# ── K-Means ───────────────────────────────────────────────────
KMEANS_N_CLUSTERS = 4

# ── Mapa de países (normalización CSV) ───────────────────────
MAPA_PAISES = {
    "us": "Estados Unidos", "usa": "Estados Unidos",
    "mx": "México", "mex": "México", "mexico": "México", "méxico": "México",
    "arg": "Argentina", "argentina": "Argentina",
    "jap": "Japón", "japon": "Japón", "japan": "Japón", "japón": "Japón",
    "corea": "Corea del Sur", "korea": "Corea del Sur", "kr": "Corea del Sur",
    "afganistan": "Afganistán",
    "ucraia": "Ucrania", "ucrania": "Ucrania",
    "nicaragua": "Nicaragua",
    "brasil": "Brasil", "brazil": "Brasil",
    "chile": "Chile",
    "peru": "Perú", "perú": "Perú",
    "rusia": "Rusia",
    "alemania": "Alemania",
    "canada": "Canadá", "canadá": "Canadá",
    "españa": "España",
    "italia": "Italia",
    "francia": "Francia",
    "australia": "Australia",
}
