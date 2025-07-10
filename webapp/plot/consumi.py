import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from .base import plot_to_base64, gradient_line

def genera_grafici_consumi(df, data_inizio, data_fine):
    grafici = {}
    df_sorted = df.sort_values("data")

    # === 1. Grafico grande: consumo giornaliero completo ===
    fig1, ax1 = plt.subplots(figsize=(12, 4))
    x = df_sorted["data"]
    y = df_sorted["valore_kwh"].to_numpy()
    gradient_line(ax1, x, y)
    ax1.set_title(f"Consumo Giornaliero - {x.min().date()} → {x.max().date()}")
    ax1.set_xlabel("Data")
    ax1.set_ylabel("Consumo (kWh)")
    ax1.xaxis.set_major_locator(mdates.MonthLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax1.tick_params(axis='x', rotation=45)
    grafici["giornaliero"] = plot_to_base64(fig1, dpi=300)

    # === 2. Media settimanale sulla prima settimana completa precedente ===
    max_data = df_sorted["data"].max()
    ultima_lun = max_data - pd.Timedelta(days=max_data.weekday() + 7)
    settimana_prec = df_sorted[(df_sorted["data"] >= ultima_lun) & (df_sorted["data"] < ultima_lun + pd.Timedelta(days=7))]
    media_sett = settimana_prec.groupby("data")["valore_kwh"].mean()
    fig2, ax2 = plt.subplots(figsize=(6, 3))
    if not media_sett.empty:
        gradient_line(ax2, media_sett.index, media_sett.values)
        ax2.set_title(f"Media Settimanale - {ultima_lun.date()} → {(ultima_lun + pd.Timedelta(days=6)).date()}")
        ax2.set_xlabel("Data")
        ax2.set_ylabel("Consumo medio (kWh)")
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%a %d'))
        ax2.tick_params(axis='x', rotation=45)
    else:
        ax2.text(0.5, 0.5, "Dati insufficienti", ha="center", va="center")
        ax2.set_title("Media Settimanale - dati non disponibili")
    grafici["media_settimanale"] = plot_to_base64(fig2, dpi=300)

    # === 3. Media giornaliera sul periodo corrente ===
    periodo_df = df_sorted[(df_sorted["data"] >= data_inizio) & (df_sorted["data"] <= data_fine)]
    media_mensile = periodo_df.groupby("data")["valore_kwh"].mean()
    fig3, ax3 = plt.subplots(figsize=(6, 3))
    if not media_mensile.empty:
        gradient_line(ax3, media_mensile.index, media_mensile.values)
        ax3.set_title(f"Media Giornaliera - Periodo corrente: {data_inizio.date()} → {data_fine.date()}")
        ax3.set_xlabel("Data")
        ax3.set_ylabel("Consumo medio (kWh)")
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        ax3.tick_params(axis='x', rotation=45)
    else:
        ax3.text(0.5, 0.5, "Dati insufficienti", ha="center", va="center")
        ax3.set_title("Media Giornaliera - dati non disponibili")
    grafici["media_mensile"] = plot_to_base64(fig3, dpi=300)

    # === 4. Bar chart consumo per periodo corrente ===
    fig4, ax4 = plt.subplots(figsize=(6, 3))
    if not periodo_df.empty:
        ax4.bar(periodo_df["data"], periodo_df["valore_kwh"])
        ax4.set_title(f"Consumo Giornaliero - Periodo: {data_inizio.date()} → {data_fine.date()}")
        ax4.set_xlabel("Data")
        ax4.set_ylabel("Consumo (kWh)")
        ax4.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
        ax4.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        ax4.tick_params(axis='x', rotation=45)
    else:
        ax4.text(0.5, 0.5, "Dati insufficienti", ha="center", va="center")
        ax4.set_title("Consumo Giornaliero - dati non disponibili")
    grafici["ultimi_30"] = plot_to_base64(fig4, dpi=300)

    # === 5. Media per giorno della settimana (storica) ===
    df_sorted["giorno_settimana"] = df_sorted["data"].dt.dayofweek
    giorni = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]
    media_giorni = df_sorted.groupby("giorno_settimana")["valore_kwh"].mean()
    fig5, ax5 = plt.subplots(figsize=(6, 3))
    ax5.bar(giorni, media_giorni.values)
    for i, v in enumerate(media_giorni.values):
        ax5.text(i, v + 0.1, f"{v:.1f}", ha="center", fontsize=9)
    ax5.set_title("Media storica per Giorno della Settimana")
    ax5.set_ylabel("Consumo medio (kWh)")
    grafici["per_fascia"] = plot_to_base64(fig5, dpi=300)

    # === 6. Media mensile storica ===
    df_sorted["mese"] = df_sorted["data"].dt.month
    media_mesi = df_sorted.groupby("mese")["valore_kwh"].mean()
    mesi = ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"]
    fig6, ax6 = plt.subplots(figsize=(6, 3))
    ax6.bar(mesi, [media_mesi.get(i+1, 0) for i in range(12)])
    for i in range(12):
        val = media_mesi.get(i+1, 0)
        ax6.text(i, val + 0.1, f"{val:.1f}", ha="center", fontsize=9)
    ax6.set_title("Consumo Medio Storico per Mese")
    ax6.set_ylabel("Consumo medio (kWh)")
    grafici["media_mese"] = plot_to_base64(fig6, dpi=300)

    return grafici
