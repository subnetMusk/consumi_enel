from flask import Flask, render_template, request
import pandas as pd
import psycopg2
import os
import numpy as np
from dotenv import load_dotenv
from plot.consumi import genera_grafici_consumi
from plot.bollette import genera_grafici_bollette
from plot.fasce import genera_grafici_fasce
from utils.stats import genera_tabella_integrativa
import json

load_dotenv()
app = Flask(__name__)

DB_PARAMS = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

enel_username = os.environ.get("ENEL_USERNAME", "utente@esempio.it")
enel_cf = os.environ.get("ENEL_CF", "XXXXXXXXXXXXXXX")

def estrai_data_emissione_ultima_bolletta(bollette_df):
    # Ordina dalla più recente alla più vecchia
    bollette_df = bollette_df.sort_values("scadenza", ascending=False)

    for riga in bollette_df.itertuples():
        dettaglio = riga.voce_dettaglio
        if isinstance(dettaglio, str):
            try:
                dettaglio = json.loads(dettaglio)
            except Exception:
                continue
        if isinstance(dettaglio, dict) and "Dataemissione" in dettaglio:
            try:
                return pd.to_datetime(dettaglio["Dataemissione"])
            except Exception:
                continue

    # Fallback: scadenza della bolletta più recente (modificata al giorno 10 se oltre)
    ultima = bollette_df["scadenza"].max()
    if pd.notna(ultima) and ultima.day > 10:
        return ultima.replace(day=10)
    return ultima

def get_dataframe():
    with psycopg2.connect(**DB_PARAMS) as conn:
        giornalieri = pd.read_sql("SELECT * FROM consumi_giornalieri ORDER BY data ASC;", conn)
        bollette = pd.read_sql("SELECT * FROM bollette ORDER BY scadenza ASC;", conn)
        orari = pd.read_sql("SELECT * FROM consumi_orari ORDER BY data ASC;", conn)
    giornalieri["data"] = pd.to_datetime(giornalieri["data"])
    bollette["scadenza"] = pd.to_datetime(bollette["scadenza"])
    bollette["mese"] = bollette["scadenza"].dt.to_period("M").dt.start_time
    orari["data"] = pd.to_datetime(orari["data"])
    return giornalieri, bollette, orari


def calcola_costo_corrente(giornalieri, bollette, data_inizio, data_fine):
    periodo_df = giornalieri[(giornalieri["data"] >= data_inizio) & (giornalieri["data"] <= data_fine)]
    consumo_finora = periodo_df["valore_kwh"].sum()
    if periodo_df.empty:
        return {
            "consumo_finora": 0, "media_attuale": 0, "media_storica": 0, "media_effettiva": 0,
            "consumo_previsto": 0, "prezzo_kwh": 0, "costo_accumulato": 0, "costo_previsto": 0,
            "giorni_rimanenti": (data_fine - data_inizio).days + 1
        }

    ultimo_giorno_disponibile = periodo_df["data"].max()
    giorni_passati = (ultimo_giorno_disponibile - data_inizio).days + 1
    giorni_totali = (data_fine - data_inizio).days + 1
    giorni_rimanenti = max(0, giorni_totali - giorni_passati)

    media_attuale = consumo_finora / giorni_passati if giorni_passati > 0 else 0

    storico_comparabile = []
    for year in giornalieri["data"].dt.year.unique():
        if year >= ultimo_giorno_disponibile.year:
            continue
        start = data_inizio.replace(year=year)
        end = data_fine.replace(year=year)
        periodo_anno = giornalieri[(giornalieri["data"] >= start) & (giornalieri["data"] <= end)]
        if not periodo_anno.empty:
            storico_comparabile.append(periodo_anno["valore_kwh"].sum())

    media_storica = np.mean(storico_comparabile) if storico_comparabile else media_attuale
    media_effettiva =  np.mean([media_attuale, media_storica]) if media_storica else media_attuale
    consumo_previsto_completo = round(consumo_finora + (media_attuale * giorni_rimanenti), 2)

    prezzo_ultimo = bollette["prezzo_medio_kwh"].dropna().iloc[-1] if not bollette["prezzo_medio_kwh"].dropna().empty else 0
    costo_accumulato = round(consumo_finora * prezzo_ultimo, 2)
    costo_previsto = round(consumo_previsto_completo * prezzo_ultimo, 2)

    return {
        "consumo_finora": round(consumo_finora, 2),
        "media_attuale": round(media_attuale, 2),
        "media_storica": round(media_storica, 2),
        "media_effettiva": round(media_effettiva, 2),
        "consumo_previsto": consumo_previsto_completo,
        "prezzo_kwh": round(prezzo_ultimo, 4),
        "costo_accumulato": costo_accumulato,
        "costo_previsto": costo_previsto,
        "giorni_rimanenti": giorni_rimanenti
    }

def prepara_dati():
    giornalieri, bollette, orari = get_dataframe()
    consumo_per_mese = giornalieri.groupby(giornalieri["data"].dt.to_period("M").dt.start_time)["valore_kwh"].sum()
    bollette["importo"] = pd.to_numeric(bollette["importo"], errors="coerce")
    bollette["kwh_mese"] = bollette["mese"].map(consumo_per_mese)
    bollette["kwh_mese"] = pd.to_numeric(bollette["kwh_mese"], errors="coerce")
    bollette["prezzo_medio_kwh"] = pd.to_numeric(bollette["importo"] / bollette["kwh_mese"], errors="coerce").round(4)

    data_inizio = estrai_data_emissione_ultima_bolletta(bollette)
    data_fine = (data_inizio + pd.DateOffset(months=2)).replace(day=10)
    stima = calcola_costo_corrente(giornalieri, bollette, data_inizio, data_fine)
    grafici_fasce = genera_grafici_fasce(orari.copy(), data_inizio, data_fine)

    return {
        "giornalieri": giornalieri,
        "bollette": bollette,
        "orari": orari,
        "consumo_per_mese": consumo_per_mese,
        "data_inizio": data_inizio,
        "data_fine": data_fine,
        "stima": stima,
        "grafici_fasce": grafici_fasce
    }


@app.route("/")
def index():
    dati = prepara_dati()
    giornalieri = dati["giornalieri"]
    bollette = dati["bollette"]
    stima = dati["stima"]

    grafici_consumi = genera_grafici_consumi(giornalieri.copy(), dati["data_inizio"], dati["data_fine"])
    grafici_bollette = genera_grafici_bollette(bollette.copy(), dati["consumo_per_mese"], dati["data_inizio"], dati["data_fine"])
    bollette_card = bollette.sort_values("scadenza", ascending=False).to_dict(orient="records")
    tabella = genera_tabella_integrativa(giornalieri.copy(), bollette.copy())

    consumo_dal_ultimo = giornalieri[giornalieri["data"] > bollette["scadenza"].max()]["valore_kwh"].sum()

    return render_template("dashboard.html",
        utente=enel_username,
        cf_utente=enel_cf,
        grafici_consumi=grafici_consumi,
        grafici_bollette=grafici_bollette,
        grafici_fasce=dati["grafici_fasce"],
        consumo_dal_ultimo=round(consumo_dal_ultimo, 2),
        previsione_consumo=stima["consumo_previsto"],
        costo_accumulato=stima["costo_accumulato"],
        stima=stima,
        bollette_card=bollette_card,
        tabella=tabella,
        periodo_corrente=(dati["data_inizio"].date(), dati["data_fine"].date()),
        data_inizio_storico=giornalieri["data"].min().date(),
        data_fine_storico=giornalieri["data"].max().date(),
        query_result=None
    )

@app.route("/query", methods=["POST"])
def query_sql():
    sql = request.form.get("sql", "").strip()

    sql_upper = sql.upper()
    if not sql_upper.startswith("SELECT") or any(forbidden in sql_upper for forbidden in ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE"]):
        html = "<p style='color:red;'>Errore: sono permesse solo query SELECT di lettura.</p>"
    else:
        try:
            with psycopg2.connect(**DB_PARAMS) as conn:
                df = pd.read_sql(sql, conn)
            html = df.to_html(index=False, classes="data")
        except Exception as e:
            html = f"<p style='color:red;'>Errore nell'esecuzione della query: {e}</p>"

    dati = prepara_dati()
    giornalieri = dati["giornalieri"]
    bollette = dati["bollette"]
    stima = dati["stima"]

    grafici_consumi = genera_grafici_consumi(giornalieri.copy(), dati["data_inizio"], dati["data_fine"])
    grafici_bollette = genera_grafici_bollette(bollette.copy(), dati["consumo_per_mese"], dati["data_inizio"], dati["data_fine"])
    tabella = genera_tabella_integrativa(giornalieri.copy(), bollette.copy())
    consumo_dal_ultimo = giornalieri[giornalieri["data"] > bollette["scadenza"].max()]["valore_kwh"].sum()

    return render_template("dashboard.html",
        utente=enel_username,
        cf_utente=enel_cf,
        grafici_consumi=grafici_consumi,
        grafici_bollette=grafici_bollette,
        grafici_fasce=dati["grafici_fasce"],
        consumo_dal_ultimo=round(consumo_dal_ultimo, 2),
        previsione_consumo=stima["consumo_previsto"],
        costo_accumulato=stima["costo_accumulato"],
        stima=stima,
        tabella=tabella,
        query_result=html,
        bollette_card=bollette.sort_values("scadenza", ascending=False).to_dict(orient="records"),
        periodo_corrente=(dati["data_inizio"].date(), dati["data_fine"].date()),
        data_inizio_storico=giornalieri["data"].min().date(),
        data_fine_storico=giornalieri["data"].max().date()
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
