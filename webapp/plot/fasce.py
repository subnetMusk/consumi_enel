import matplotlib.pyplot as plt
import pandas as pd
from .base import plot_to_base64
import holidays

def assegna_fascia_enel(row):
    ora = row["ora"]
    giorno = row["data"].weekday()
    is_festivo = row["data"].date() in holidays.Italy()
    if giorno == 6 or is_festivo:
        return "F3"
    if giorno in range(0, 5):
        if 8 <= ora < 19:
            return "F1"
        elif (7 <= ora < 8) or (19 <= ora < 23):
            return "F2"
        else:
            return "F3"
    if giorno == 5:
        if 7 <= ora < 23:
            return "F2"
        else:
            return "F3"
    return "F3"

def add_labels_to_horizontal_bars(ax, bars):
    for bar in bars:
        width = bar.get_width()
        ax.text(width - width * 0.02, bar.get_y() + bar.get_height() / 2,
                f"{width:.1f} kWh", va='center', ha='right',
                color='white', fontsize=8, fontweight='bold')

def genera_grafici_fasce(df_orari, data_inizio=None, data_fine=None):
    grafici = {}
    colori = {"F1": "red", "F2": "gold", "F3": "green"}
    fasce = ["F1", "F2", "F3"]

    df = df_orari.copy()
    df["data"] = pd.to_datetime(df["data"])
    df["ora"] = df["fascia"].str.extract(r"H(\d{1,2})")[0]
    df["ora"] = pd.to_numeric(df["ora"], errors="coerce")
    df = df[df["ora"].notna()]
    df["ora"] = df["ora"].astype(int)
    df["fascia_enel"] = df.apply(assegna_fascia_enel, axis=1)

    media_oraria = df.groupby("ora")["valore_kwh"].mean()
    fig1, ax1 = plt.subplots(figsize=(10, 3.5))
    ax1.plot(media_oraria.index, media_oraria.values, marker='o')
    ax1.set_title("Consumo Medio Giornaliero per Ora (Storico)")
    ax1.set_xlabel("Ora del giorno")
    ax1.set_ylabel("Consumo medio (kWh)")
    ax1.set_xticks(range(1, 25))
    grafici["storico_orario"] = plot_to_base64(fig1, dpi=300)

    if data_inizio and data_fine:
        periodo_corr = df[(df["data"] >= data_inizio) & (df["data"] <= data_fine)]
        media_periodo = periodo_corr.groupby("ora")["valore_kwh"].mean()
        fig2, ax2 = plt.subplots(figsize=(6, 3))
        ax2.plot(media_periodo.index, media_periodo.values, marker='o', color="orange")
        ax2.set_title(f"Media Oraria - Periodo Corrente ({data_inizio.date()} → {data_fine.date()})")
        ax2.set_xlabel("Ora del giorno")
        ax2.set_ylabel("Consumo medio (kWh)")
        ax2.set_xticks(range(1, 25))
        grafici["media_periodo"] = plot_to_base64(fig2, dpi=300)

    max_data = df["data"].max()
    settimana_df = df[df["data"] >= max_data - pd.Timedelta(days=7)]
    media_settimana = settimana_df.groupby("ora")["valore_kwh"].mean()
    fig3, ax3 = plt.subplots(figsize=(6, 3))
    ax3.plot(media_settimana.index, media_settimana.values, marker='o', color="green")
    ax3.set_title("Media Oraria - Ultima Settimana")
    ax3.set_xlabel("Ora del giorno")
    ax3.set_ylabel("Consumo medio (kWh)")
    ax3.set_xticks(range(1, 25))
    grafici["media_settimana"] = plot_to_base64(fig3, dpi=300)

    somma_fasce_enel = df.groupby("fascia_enel")["valore_kwh"].sum()
    valori = [somma_fasce_enel.get(f, 0) for f in fasce]

    fig4, ax4 = plt.subplots(figsize=(5, 2.5))
    bars4 = ax4.barh(fasce[::-1], valori[::-1], color=[colori[f] for f in fasce][::-1])
    add_labels_to_horizontal_bars(ax4, bars4)
    ax4.set_title("Totale Storico per Fascia Oraria (ENEL)")
    ax4.set_xlabel("Consumo (kWh)")
    grafici["fasce_enel_storico"] = plot_to_base64(fig4, dpi=300)

    fig4b, ax4b = plt.subplots(figsize=(5, 2.5))
    ax4b.pie(
        valori,
        labels=fasce,
        colors=[colori[f] for f in fasce],
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 9}
    )
    ax4b.set_title("Percentuale Storico", fontsize=8, pad=2)
    ax4b.axis("equal")
    plt.tight_layout(pad=0.1)
    grafici["pie_fasce_enel_storico"] = plot_to_base64(fig4b, dpi=300)

    if data_inizio and data_fine:
        df_periodo = df[(df["data"] >= data_inizio) & (df["data"] <= data_fine)]
        somma_fasce_periodo = df_periodo.groupby("fascia_enel")["valore_kwh"].sum()
        valori_periodo = [somma_fasce_periodo.get(f, 0) for f in fasce]

        fig5, ax5 = plt.subplots(figsize=(5, 2.5))
        bars5 = ax5.barh(fasce[::-1], valori_periodo[::-1], color=[colori[f] for f in fasce][::-1])
        add_labels_to_horizontal_bars(ax5, bars5)
        ax5.set_title(f"Totale Fasce Orarie - Periodo Corrente\n({data_inizio.date()} → {data_fine.date()})")
        ax5.set_xlabel("Consumo (kWh)")
        grafici["fasce_enel_periodo"] = plot_to_base64(fig5, dpi=300)

        fig5b, ax5b = plt.subplots(figsize=(5, 2.5))
        ax5b.pie(
            valori_periodo,
            labels=fasce,
            colors=[colori[f] for f in fasce],
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 9}
        )
        ax5b.set_title("Percentuale Corrente", fontsize=8, pad=2)
        ax5b.axis("equal")
        plt.tight_layout(pad=0.1)
        grafici["pie_fasce_enel_periodo"] = plot_to_base64(fig5b, dpi=300)

    return grafici
