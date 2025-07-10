from datetime import timedelta

def genera_tabella_integrativa(consumi_df, bollette_df):
    """
    Riceve il DataFrame dei consumi giornalieri e delle bollette,
    restituisce una lista di dizionari con etichetta e valore per la tabella HTML.
    """
    stats = []

    def add(label, value):
        stats.append({"label": label, "value": value})

    # Massimo e minimo assoluto (consumi)
    max_abs = consumi_df.loc[consumi_df["valore_kwh"].idxmax()]
    min_abs = consumi_df.loc[consumi_df["valore_kwh"].idxmin()]
    add("Massimo assoluto consumo", f"{max_abs['data'].date()} - {max_abs['valore_kwh']} kWh")
    add("Minimo assoluto consumo", f"{min_abs['data'].date()} - {min_abs['valore_kwh']} kWh")

    # Per anno (consumi)
    for year in sorted(consumi_df["data"].dt.year.unique()):
        anno = consumi_df[consumi_df["data"].dt.year == year]
        max_y = anno.loc[anno["valore_kwh"].idxmax()]
        min_y = anno.loc[anno["valore_kwh"].idxmin()]
        add(f"Massimo consumo {year}", f"{max_y['data'].date()} - {max_y['valore_kwh']} kWh")
        add(f"Minimo consumo {year}", f"{min_y['data'].date()} - {min_y['valore_kwh']} kWh")

    # Ultimi 30 giorni (consumi)
    ultimi30 = consumi_df[consumi_df["data"] >= consumi_df["data"].max() - timedelta(days=30)]
    if not ultimi30.empty:
        max30 = ultimi30.loc[ultimi30["valore_kwh"].idxmax()]
        min30 = ultimi30.loc[ultimi30["valore_kwh"].idxmin()]
        add("Massimo ultimi 30 giorni", f"{max30['data'].date()} - {max30['valore_kwh']} kWh")
        add("Minimo ultimi 30 giorni", f"{min30['data'].date()} - {min30['valore_kwh']} kWh")

    # Ultimi 7 giorni (consumi)
    ultimi7 = consumi_df[consumi_df["data"] >= consumi_df["data"].max() - timedelta(days=7)]
    if not ultimi7.empty:
        max7 = ultimi7.loc[ultimi7["valore_kwh"].idxmax()]
        min7 = ultimi7.loc[ultimi7["valore_kwh"].idxmin()]
        add("Massimo ultima settimana", f"{max7['data'].date()} - {max7['valore_kwh']} kWh")
        add("Minimo ultima settimana", f"{min7['data'].date()} - {min7['valore_kwh']} kWh")

    # Medie e confronto (consumi)
    media7 = ultimi7["valore_kwh"].mean() if not ultimi7.empty else None
    year_back = consumi_df[consumi_df["data"].between(consumi_df["data"].max() - timedelta(days=372),
                                                       consumi_df["data"].max() - timedelta(days=365))]
    media_back = year_back["valore_kwh"].mean() if not year_back.empty else None

    if media7 is not None:
        add("Media ultimi 7 giorni", f"{media7:.2f} kWh")
    if media_back is not None:
        add("Media stesso periodo anno scorso", f"{media_back:.2f} kWh")
    if media7 and media_back:
        delta = (media7 - media_back) / media_back * 100
        add("Differenza % consumi con anno scorso", f"{delta:+.2f}%")

    # Dati da bollette
    bollette_df = bollette_df[bollette_df["prezzo_medio_kwh"].notna()]
    if not bollette_df.empty:
        add("Costo massimo kWh (bollette)", f"€ {bollette_df['prezzo_medio_kwh'].max():.4f}")
        add("Costo minimo kWh (bollette)", f"€ {bollette_df['prezzo_medio_kwh'].min():.4f}")
        for anno in sorted(bollette_df["scadenza"].dt.year.unique()):
            media_annua = bollette_df[bollette_df["scadenza"].dt.year == anno]["prezzo_medio_kwh"].mean()
            add(f"Costo medio kWh {anno}", f"€ {media_annua:.4f}")
        ultimo = bollette_df.sort_values("scadenza").iloc[-1]["prezzo_medio_kwh"]
        add("Costo medio kWh ultima bolletta", f"€ {ultimo:.4f}")

    return stats
