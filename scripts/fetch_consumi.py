import json
import requests
from datetime import datetime, timedelta, date
import os
from dotenv import load_dotenv
from pathlib import Path
import psycopg2

# === Caricamento configurazione ===
load_dotenv()

POD = os.getenv("ENEL_POD")
USER_NUMBER = os.getenv("ENEL_USER_NUMBER")
COOKIE_PATH = "cookies/cookies_enel_post_login.json"
RAW_DUMP_FILE = "data/consumi_raw.json"

DB_PARAMS = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

# === Recupera ultima data registrata nel DB ===
def get_last_date():
    with psycopg2.connect(**DB_PARAMS) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT MAX(data) FROM consumi_giornalieri;")
            result = cur.fetchone()
            return result[0] or datetime.strptime("2023-09-01", "%Y-%m-%d").date()

# === Carica i cookie salvati ===
def load_cookies():
    with open(COOKIE_PATH, "r") as f:
        cookie_list = json.load(f)
    return {cookie['name']: cookie['value'] for cookie in cookie_list}

# === Esegue richiesta consumi ===
def fetch_data(pod, user_number, date_from, date_to, cookies):
    url = "https://www.enel.it/bin/areaclienti/auth/aggregateConsumption"
    params = {
        "pod": pod,
        "userNumber": user_number,
        "validityFrom": date_from.strftime("%d%m%Y"),
        "validityTo": date_to.strftime("%d%m%Y"),
        "_": int(datetime.now().timestamp() * 1000)
    }
    headers = {
        "Referer": "https://www.enel.it/it-it/login",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0"
    }
    print(f"Richiesta consumi da {params['validityFrom']} a {params['validityTo']}")
    resp = requests.get(url, headers=headers, cookies=cookies, params=params)
    print("Status:", resp.status_code)
    if resp.status_code == 200:
        print(" Dati ricevuti")
        return resp.json()
    else:
        print("Errore nella richiesta")
        print(resp.text)
        return None

if __name__ == "__main__":
    last_date = get_last_date()
    print("Ultimo giorno registrato:", last_date)

    start_date = last_date + timedelta(days=1)
    end_date = date.today()

    if start_date > end_date:
        print("Nessun nuovo giorno da scaricare.")
        exit(0)

    cookies = load_cookies()
    data = fetch_data(POD, USER_NUMBER, start_date, end_date, cookies)

    if data:
        Path(os.path.dirname(RAW_DUMP_FILE)).mkdir(parents=True, exist_ok=True)
        with open(RAW_DUMP_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print(f"JSON raw salvato in: {RAW_DUMP_FILE}")
