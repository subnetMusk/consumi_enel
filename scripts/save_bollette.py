import os
import json
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DB_PARAMS = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

RAW_BOLLETTE_FILE = "data/bollette_raw.json"

def save_bollette(data, conn):
    fatture = data.get("data", {}).get("results", [])
    count = 0

    with conn.cursor() as cur:
        for contratto in fatture:
            for bolletta in contratto.get("fatture", []):
                try:
                    numero = bolletta["Numerodocumento"]
                    scadenza = datetime.strptime(bolletta["Datascadenza"], "%Y-%m-%d").date()
                    importo = float(bolletta["Importofattura"].replace(",", "."))
                    stato = bolletta.get("Statopagabilita", "SCONOSCIUTO")
                    voce_json = json.dumps(bolletta, ensure_ascii=False)

                    cur.execute("""
                        INSERT INTO bollette (numero, scadenza, importo, stato_pagamento, voce_dettaglio)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (numero) DO NOTHING;
                    """, (numero, scadenza, importo, stato, voce_json))
                    count += 1
                except Exception as e:
                    print(f"Errore con bolletta {bolletta.get('Numerodocumento')}: {e}")

    conn.commit()
    print(f" Inserite {count} bollette")

if __name__ == "__main__":
    print(f"Caricamento da {RAW_BOLLETTE_FILE}")
    with open(RAW_BOLLETTE_FILE, "r") as f:
        raw = json.load(f)

    with psycopg2.connect(**DB_PARAMS) as conn:
        save_bollette(raw, conn)
