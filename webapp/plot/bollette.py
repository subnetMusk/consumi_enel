import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
from .base import plot_to_base64, gradient_line

def genera_grafici_bollette(df, consumo_mensile=None, data_inizio=None, data_fine=None):
    """
    Riceve il DataFrame delle bollette e opzionalmente:
    - i consumi mensili
    - il periodo corrente da usare per alcuni grafici
    Restituisce:
    - importi bollette nel tempo (linea)
    - costo medio per kWh (linea con gradiente)
    - spesa totale per anno (bar chart con label)
    """
    grafici = {}

    df_sorted = df.sort_values("scadenza").copy()
    df_sorted = df_sorted[df_sorted["importo"].notna()]
    df_sorted["scadenza"] = pd.to_datetime(df_sorted["scadenza"])
    df_sorted["mese"] = df_sorted["scadenza"].dt.to_period("M").dt.start_time

    # Grafico 1: Importi Bollette (lineare)
    fig1, ax1 = plt.subplots(figsize=(12, 4))
    ax1.plot(df_sorted["scadenza"], df_sorted["importo"], marker='o')
    ax1.set_title("Importi Bollette (€ nel tempo)")
    ax1.set_ylabel("Importo (€)")
    ax1.set_xlabel("Data scadenza")
    ax1.tick_params(axis='x', rotation=45)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig1.autofmt_xdate()
    grafici["importi_bollette"] = plot_to_base64(fig1, dpi=300)

    # Grafico 2: Costo medio per kWh (linea con gradiente)
    if consumo_mensile is not None:
        df_sorted["kwh_mese"] = df_sorted["mese"].map(consumo_mensile)
        df_sorted["costo_medio_kwh"] = (
            df_sorted["importo"] / df_sorted["kwh_mese"]
        ).replace([np.inf, -np.inf], np.nan)
    elif "prezzo_medio_kwh" in df_sorted.columns:
        df_sorted["costo_medio_kwh"] = df_sorted["prezzo_medio_kwh"]
    else:
        df_sorted["costo_medio_kwh"] = np.nan

    df_val = df_sorted.dropna(subset=["costo_medio_kwh"])

    fig2, ax2 = plt.subplots(figsize=(6, 3))
    if not df_val.empty:
        x = df_val["scadenza"]
        y = df_val["costo_medio_kwh"]
        gradient_line(ax2, x, y, cmap="RdYlGn_r")
        titolo = (
            f"Costo medio per kWh - periodo {data_inizio.date()} → {data_fine.date()}"
            if data_inizio and data_fine else "Costo medio per kWh (storico)"
        )
        ax2.set_title(titolo)
        ax2.set_ylabel("€/kWh")
        ax2.set_xlabel("Data scadenza")
        ax2.tick_params(axis='x', rotation=45)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax2.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig2.autofmt_xdate()
    else:
        ax2.text(0.5, 0.5, "Dati insufficienti", ha='center', va='center')
    grafici["costo_medio"] = plot_to_base64(fig2, dpi=300)

    # Grafico 3: Spesa Totale per Anno (bar chart)
    df_sorted["anno"] = df_sorted["scadenza"].dt.year
    spesa_per_anno = df_sorted.groupby("anno")["importo"].sum()

    fig3, ax3 = plt.subplots(figsize=(6, 3))
    bars = ax3.bar(spesa_per_anno.index.astype(str), spesa_per_anno.values)
    ax3.bar_label(bars, fmt="€%.0f", fontsize=9)
    ax3.set_title("Spesa Totale Bollette per Anno (€)")
    ax3.set_ylabel("Totale annuale (€)")
    ax3.set_xlabel("Anno")
    grafici["totale_anno"] = plot_to_base64(fig3, dpi=300)

    return grafici
