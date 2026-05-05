# ============================================================
# VISUALIZACIÓN — Dashboard de 12 gráficas
# ============================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from config import COLORES, BG, AX, GR, WH


def _sty(ax, titulo: str) -> None:
    """Aplica estilo oscuro uniforme a un subplot."""
    ax.set_facecolor(AX)
    ax.set_title(titulo, color=WH, fontsize=10, pad=7)
    ax.tick_params(colors=WH)
    ax.xaxis.label.set_color(WH)
    ax.yaxis.label.set_color(WH)
    for sp in ax.spines.values():
        sp.set_edgecolor(GR)
    ax.grid(color=GR, linewidth=0.4)


def generar_dashboard(
    df_master: pd.DataFrame,
    df_kpis: pd.DataFrame,
    pca_obj,
    varianza,
    feats_pca: list,
    ruta_salida: str = "dashboard_etl.png",
) -> None:
    """
    Genera y guarda el dashboard con 12 visualizaciones.
    Parámetros:
        df_master   : DataFrame maestro enriquecido y segmentado
        df_kpis     : DataFrame con KPIs regionales (XLSX)
        pca_obj     : Objeto PCA entrenado (sklearn)
        varianza    : Array de varianza explicada por componente
        feats_pca   : Lista de features usadas en PCA
        ruta_salida : Ruta del PNG de salida
    """
    _validar_columnas(df_master)

    fig = plt.figure(figsize=(20, 22), facecolor=BG)
    fig.suptitle(
        "DASHBOARD ETL — ANÁLISIS GLOBAL DE RETAIL\n"
        "MariaDB · MongoDB · Web Scraping · CSV · XLSX · API",
        fontsize=16, fontweight="bold", color=WH, y=0.99,
    )

    # 1. Boxplot montos por segmento
    ax1 = fig.add_subplot(4, 3, 1)
    data_bp = [
        df_master.loc[df_master["segmento_cliente"] == s, "monto"].dropna()
        for s in COLORES
    ]
    bp = ax1.boxplot(
        data_bp, patch_artist=True,
        medianprops=dict(color="yellow", linewidth=2),
    )
    for p, c in zip(bp["boxes"], COLORES.values()):
        p.set_facecolor(c)
        p.set_alpha(0.8)
    ax1.set_xticklabels(
        [s.replace(" ", "\n") for s in COLORES], fontsize=7, color=WH
    )
    _sty(ax1, "📦 Boxplot: Montos por Segmento")
    ax1.set_ylabel("Monto USD")

    # 2. Scatter PCA PC1 vs PC2
    ax2 = fig.add_subplot(4, 3, 2)
    m = df_master["PC1"].notna()
    sc = ax2.scatter(
        df_master.loc[m, "PC1"], df_master.loc[m, "PC2"],
        c=df_master.loc[m, "cluster"], cmap="plasma", alpha=0.5, s=8,
    )
    plt.colorbar(sc, ax=ax2, label="Cluster")
    _sty(ax2, "🔬 PCA: PC1 vs PC2 (Clusters)")
    ax2.set_xlabel("PC1")
    ax2.set_ylabel("PC2")

    # 3. Varianza PCA
    ax3 = fig.add_subplot(4, 3, 3)
    lpc = [f"PC{i + 1}" for i in range(len(varianza))]
    bars = ax3.bar(
        lpc, varianza * 100,
        color=["#e74c3c", "#3498db", "#2ecc71"], alpha=0.85, edgecolor=WH,
    )
    ax3.plot(
        lpc, np.cumsum(varianza) * 100, "o--",
        color="yellow", linewidth=2, markersize=7, label="Acumulado",
    )
    for b, v in zip(bars, varianza):
        ax3.text(
            b.get_x() + b.get_width() / 2, b.get_height() + 0.5,
            f"{v * 100:.1f}%", ha="center", color=WH, fontsize=9,
        )
    ax3.legend(facecolor=AX, labelcolor=WH)
    _sty(ax3, "📊 PCA: Varianza Explicada")
    ax3.set_ylabel("% Varianza")

    # 4. Histograma edades
    ax4 = fig.add_subplot(4, 3, 4)
    ax4.hist(
        df_master["edad"].dropna(), bins=30,
        color="#3498db", edgecolor=WH, alpha=0.8,
    )
    _sty(ax4, "👤 Distribución de Edades")
    ax4.set_xlabel("Edad")
    ax4.set_ylabel("Frecuencia")

    # 5. Ventas totales por segmento
    ax5 = fig.add_subplot(4, 3, 5)
    vs = df_master.groupby("segmento_cliente")["monto"].sum().sort_values()
    ax5.barh(
        vs.index, vs.values / 1e6,
        color=[COLORES.get(s, "#888") for s in vs.index],
        alpha=0.85, edgecolor=WH,
    )
    _sty(ax5, "💰 Ventas Totales por Segmento (M USD)")
    ax5.set_xlabel("Millones USD")

    # 6. Heatmap correlaciones
    ax6 = fig.add_subplot(4, 3, 6)
    cols_c = ["monto", "edad", "ingresos", "gastos_mensuales", "puntos_lealtad"]
    cols_c = [c for c in cols_c if c in df_master.columns]
    corr = df_master[cols_c].dropna().corr()
    n = len(cols_c)
    im = ax6.imshow(corr.values, cmap="RdYlGn", vmin=-1, vmax=1)
    ax6.set_xticks(range(n))
    ax6.set_yticks(range(n))
    ax6.set_xticklabels([c[:8] for c in cols_c], rotation=30, color=WH, fontsize=7)
    ax6.set_yticklabels([c[:8] for c in cols_c], color=WH, fontsize=7)
    for i in range(n):
        for j in range(n):
            ax6.text(
                j, i, f"{corr.values[i, j]:.2f}",
                ha="center", va="center",
                color="black", fontsize=7, fontweight="bold",
            )
    ax6.set_facecolor(AX)
    ax6.set_title("🔥 Heatmap Correlaciones", color=WH, fontsize=10, pad=7)

    # 7. Pie segmentos
    ax7 = fig.add_subplot(4, 3, 7)
    sc2 = df_master["segmento_cliente"].value_counts()
    wedges, texts, at = ax7.pie(
        sc2, labels=sc2.index,
        colors=[COLORES.get(s, "#888") for s in sc2.index],
        autopct="%1.1f%%", startangle=90,
        textprops={"color": WH, "fontsize": 8},
    )
    for a in at:
        a.set_color(WH)
    ax7.set_facecolor(AX)
    ax7.set_title("🎯 Distribución Segmentos", color=WH, fontsize=10, pad=7)

    # 8. Evolución ventas por año
    ax8 = fig.add_subplot(4, 3, 8)
    tmp = df_master.dropna(subset=["fecha"]).copy()
    tmp["año"] = tmp["fecha"].dt.year
    va = tmp.groupby("año")["monto"].sum()
    ax8.plot(va.index, va.values / 1e6, "-o", color="#2ecc71", linewidth=2, markersize=4)
    ax8.fill_between(va.index, va.values / 1e6, alpha=0.2, color="#2ecc71")
    _sty(ax8, "📈 Ventas por Año (M USD)")
    ax8.set_xlabel("Año")
    ax8.set_ylabel("Millones USD")

    # 9. Scatter PC1 vs PC3 por segmento
    ax9 = fig.add_subplot(4, 3, 9)
    for seg, color in COLORES.items():
        m2 = (df_master["segmento_cliente"] == seg) & df_master["PC1"].notna()
        ax9.scatter(
            df_master.loc[m2, "PC1"], df_master.loc[m2, "PC3"],
            c=color, alpha=0.4, s=8, label=seg,
        )
    ax9.legend(fontsize=6, facecolor=AX, labelcolor=WH, markerscale=2)
    _sty(ax9, "🔵 PCA: PC1 vs PC3 por Segmento")
    ax9.set_xlabel("PC1")
    ax9.set_ylabel("PC3")

    # 10. KPIs por región (XLSX)
    ax10 = fig.add_subplot(4, 3, 10)
    if not df_kpis.empty and "Ventas_Anuales_USD" in df_kpis.columns:
        top = df_kpis.nlargest(10, "Ventas_Anuales_USD")
        ax10.bar(
            range(len(top)), top["Ventas_Anuales_USD"] / 1e3,
            color=plt.cm.viridis(np.linspace(0.2, 0.9, len(top))),
            edgecolor=WH,
        )
        ax10.set_xticks(range(len(top)))
        ax10.set_xticklabels(
            top["País"], rotation=45, ha="right", fontsize=7, color=WH
        )
    else:
        ax10.text(0.5, 0.5, "Sin datos KPI", ha="center", va="center", color=WH)
    _sty(ax10, "🌍 Top 10 Regiones — KPIs XLSX")
    ax10.set_ylabel("K USD")

    # 11. Sankey simplificado: Segmentos → Clusters
    ax11 = fig.add_subplot(4, 3, 11)
    ax11.set_facecolor(AX)
    segs = list(COLORES.keys())
    clus = [f"Cluster {i}" for i in range(KMEANS_N_CLUSTERS if hasattr(_sty, '__module__') else 4)]
    try:
        n_clusters = df_master["cluster"].nunique()
        clus = [f"Cluster {i}" for i in range(n_clusters)]
        flujo = pd.crosstab(df_master["segmento_cliente"], df_master["cluster"])
        ys = np.linspace(0.1, 0.9, len(segs))
        yc = np.linspace(0.1, 0.9, len(clus))
        for i, seg in enumerate(segs):
            for j in flujo.columns:
                val = flujo.loc[seg, j] if seg in flujo.index else 0
                if val > 0:
                    ax11.plot(
                        [0, 1], [ys[i], yc[j]],
                        color=COLORES[seg],
                        alpha=min(0.9, val / flujo.max().max()),
                        linewidth=max(0.5, val / 80),
                    )
        for i, seg in enumerate(segs):
            ax11.text(
                -0.02, ys[i], seg,
                ha="right", va="center",
                color=COLORES[seg], fontsize=7, fontweight="bold",
            )
        for j, cl in enumerate(clus):
            ax11.text(1.02, yc[j], cl, ha="left", va="center", color=WH, fontsize=8)
    except Exception as e:
        ax11.text(0.5, 0.5, f"Sin datos\n{e}", ha="center", va="center", color=WH)
    ax11.set_xlim(-0.35, 1.35)
    ax11.set_ylim(0, 1)
    ax11.axis("off")
    ax11.set_title("🌊 Sankey: Segmentos → Clusters", color=WH, fontsize=10, pad=7)

    # 12. PCA Loadings
    ax12 = fig.add_subplot(4, 3, 12)
    load = pd.DataFrame(
        pca_obj.components_.T,
        columns=[f"PC{i+1}" for i in range(pca_obj.n_components_)],
        index=feats_pca,
    )
    ax12.imshow(load.values, cmap="coolwarm", aspect="auto", vmin=-1, vmax=1)
    ax12.set_xticks(range(pca_obj.n_components_))
    ax12.set_xticklabels(load.columns, color=WH)
    ax12.set_yticks(range(len(feats_pca)))
    ax12.set_yticklabels([f[:12] for f in feats_pca], color=WH, fontsize=7)
    for i in range(len(feats_pca)):
        for j in range(pca_obj.n_components_):
            ax12.text(
                j, i, f"{load.values[i, j]:.2f}",
                ha="center", va="center",
                color="black", fontsize=6,
            )
    ax12.set_facecolor(AX)
    ax12.set_title("⚙️ PCA Loadings", color=WH, fontsize=10, pad=7)

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.savefig(ruta_salida, dpi=130, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"✅ Dashboard guardado → {ruta_salida}")


def _validar_columnas(df: pd.DataFrame) -> None:
    """Valida que el DataFrame maestro tenga las columnas mínimas necesarias."""
    requeridas = {"monto", "segmento_cliente", "cluster", "PC1", "PC2", "PC3"}
    faltantes = requeridas - set(df.columns)
    if faltantes:
        raise KeyError(f"❌ [Dashboard] Columnas faltantes en df_master: {faltantes}")


# Importación diferida para evitar circularidad con config
from config import KMEANS_N_CLUSTERS  # noqa: E402 (se usa en Sankey)
