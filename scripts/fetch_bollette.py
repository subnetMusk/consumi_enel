import os
import json
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# === Carica le credenziali da .env ===
load_dotenv()
USERNAME = os.getenv("ENEL_USERNAME")
PASSWORD = os.getenv("ENEL_PASSWORD")
CF = os.getenv("ENEL_CF")
BP = os.getenv("ENEL_BP")
CC = os.getenv("ENEL_CC")

if not USERNAME or not PASSWORD:
    raise ValueError("ENEL_USERNAME o ENEL_PASSWORD non sono definiti nel file .env")

# === Configura Chrome + driver ===
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1280,1024")
options.binary_location = "/usr/bin/chromium"

driver = webdriver.Chrome(
    service=Service("/usr/bin/chromedriver"),
    options=options
)

try:
    print("[•] Navigazione verso la pagina di login...")
    driver.get("https://www.enel.it/it-it/login")
    wait = WebDriverWait(driver, 15)

    print("[•] Compilazione del form...")
    email_input = wait.until(EC.presence_of_element_located((By.ID, "txtLoginUsername")))
    password_input = driver.find_element(By.ID, "txtLoginPassword")

    email_input.clear()
    email_input.send_keys(USERNAME)
    password_input.clear()
    password_input.send_keys(PASSWORD)

    login_button = driver.find_element(By.ID, "login-btn")
    login_button.click()

    print("[•] Attendo esito login...")
    time.sleep(5)

    # Screenshot utile per debug
    driver.save_screenshot("screenshots/post_login.png")


    # === Salva i cookie in due formati: Selenium + Requests ===
    cookies = driver.get_cookies()
    os.makedirs("cookies", exist_ok=True)

    # 1. Salvataggio in formato Selenium (lista di dict)
    with open("cookies/cookies_enel_post_login.json", "w") as f:
        json.dump(cookies, f, indent=2)

    # 2. Salvataggio in formato Requests (dict chiave/valore)
    cookie_dict = {c["name"]: c["value"] for c in cookies}
    with open("cookies/cookies_enel_requests.json", "w") as f:
        json.dump(cookie_dict, f, indent=2)

    print("Login completato. Cookie salvati in cookies/")

    try:
        # STEP 1 – Visita la pagina bollette
        print("Apro la pagina delle bollette...")
        driver.get("https://www.enel.it/it-IT/area-clienti/bollette")
        time.sleep(5)

        # STEP 2 – Estrai e salva i cookie aggiornati
        cookies_selenium = driver.get_cookies()
        cookie_dict = {c['name']: c['value'] for c in cookies_selenium}

        os.makedirs("cookies", exist_ok=True)
        with open("cookies/cookies_enel_post_login.json", "w") as f:
            json.dump(cookies_selenium, f, indent=2)
        with open("cookies/cookies_enel_requests.json", "w") as f:
            json.dump(cookie_dict, f, indent=2)
        print("Cookie salvati in cookies/")

        # STEP 3 – Esegui la POST direttamente nel browser (via JS)
        print("Invio POST a getArchivioBollette via browser...")

        post_payload = {
            "cache": True,
            "canale": "W",
            "cf": CF,
            "inputList": [
                {
                    "businessPartner": BP,
                    "contoContrattuale": [CC]
                }
            ],
            "numeroMassimoX2": 100,
            "tipologia": ""
        }

        js_code = f"""
        return fetch("https://www.enel.it/bin/areaclienti/auth/getArchivioBollette", {{
            method: "POST",
            headers: {{
                "Content-Type": "application/x-www-form-urlencoded"
            }},
            body: "pagamentiRequest=" + encodeURIComponent(JSON.stringify({json.dumps(post_payload)}))
        }})
        .then(resp => resp.text())
        .then(text => text);
        """

        response_text = driver.execute_script(js_code)
        if not response_text:
            print("Nessuna risposta dal server")
            exit(1)

        # STEP 4 – Salva i dati raw
        os.makedirs("data", exist_ok=True)
        with open("data/bollette_raw.json", "w") as f:
            f.write(response_text)

        print("Dati bollette salvati in data/bollette_raw.json")
        driver.quit()

    except Exception as e:
        print(f"Errore: {e}")
        driver.quit()

except Exception as e:
    print(f"Errore durante il login: {e}")
    driver.quit()
    exit(1)

