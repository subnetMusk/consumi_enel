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

RAW_FILE = "data/consumi_raw.json"

def parse_date(ddmmyyyy):
    return datetime.strptime(ddmmyyyy, "%d%m%Y").date()

def save_orari_e_giornalieri(data, conn):
    aggregations = data["data"]["aggregationResult"]["aggregations"]
    count_orari = 0
    count_giornalieri = 0

    with conn.cursor() as cur:
        for agg in aggregations:
            for result in agg.get("results", []):
                giorno = parse_date(result["date"])
                tipo = result.get("measureType", "N/A")
                totale = 0.0

                for entry in result.get("binValues", []):
                    fascia = entry["name"]
                    valore = entry["value"]
                    totale += valore
                    cur.execute("""
                        INSERT INTO consumi_orari (data, fascia, valore_kwh, tipo_misura)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (data, fascia) DO NOTHING;
                    """, (giorno, fascia, valore, tipo))
                    count_orari += 1

                cur.execute("""
                    INSERT INTO consumi_giornalieri (data, valore_kwh, tipo_misura)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (data) DO NOTHING;
                """, (giorno, round(totale, 3), tipo))
                count_giornalieri += 1

    conn.commit()
    print(f" Inserite {count_orari} righe in consumi_orari")
    print(f" Inseriti {count_giornalieri} record in consumi_giornalieri")

if __name__ == "__main__":
    print(f"Caricamento da {RAW_FILE}")
    with open(RAW_FILE, "r") as f:
        raw = json.load(f)

    with psycopg2.connect(**DB_PARAMS) as conn:
        save_orari_e_giornalieri(raw, conn)
