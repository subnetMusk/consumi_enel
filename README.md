
# Dashboard Consumi Enel

Questa è una dashboard web sviluppata con Flask per **monitorare, analizzare e prevedere** il consumo elettrico, a partire dai dati raccolti dal sito Enel e salvati su un database PostgreSQL.  
Il sistema supporta:

- Analisi dinamiche dei consumi nel tempo;
- Stime del costo della bolletta futura;
- Grafici con **colorazione graduale** per evidenziare trend di consumo;
- Tabella statistica con confronti storici;
- Esecuzione manuale di query SQL dal browser.

---

## Anteprima della Dashboard

<details>
  <summary>Clicca per visualizzare lo screenshot completo della dashboard</summary>

  <p align="center">
    <img src=".image/dashboard_agg.png" alt="Dashboard Consumi Enel" width="800"/>
  </p>
</details>

---

## Funzionalità

- **Grafico a linea** del consumo giornaliero sull’intero storico
- **Grafici affiancati** per il periodo corrente (dall’ultima bolletta alla prossima stimata):
  - Consumo medio settimanale
  - Consumo medio mensile
  - Media per giorno della settimana
  - Consumo aggregato nel periodo
  - Consumo diviso per fasce orarie (F1, F2, F3)
- **Stima del consumo e della spesa prevista**:
  - Consumo previsto
  - Spesa prevista
  - Voci dettagliate sotto ciascun valore
- **Statistiche integrative**:
  - Massimo e minimo consumo assoluto e recenti
  - Prezzo medio per kWh per ogni anno
  - Storico e variazioni percentuali rispetto all’anno precedente
- Interfaccia SQL manuale

---

## Requisiti

Non è necessaria alcuna installazione manuale dei pacchetti Python.

Il progetto è già contenuto in un ambiente **Docker multicomponente**, che installa automaticamente tutti i servizi necessari:

- PostgreSQL (con schema predefinito)
- Web app Flask
- Script automatici per l’inserimento dei dati

Assicurarsi solo di avere Docker e Docker Compose installati sul sistema host.

---

## Variabili `.env` richieste

La dashboard e gli script di scraping richiedono alcune variabili di ambiente da definire nel file `.env` nella root del progetto:

### Database PostgreSQL

| Variabile       | Descrizione                         |
|-----------------|-------------------------------------|
| `DB_HOST`       | Host del database (es. `localhost` o `db`) |
| `DB_PORT`       | Porta (es. `5432`)          |
| `DB_NAME`       | Nome del database (es. `enel`)      |
| `DB_USER`       | Nome utente per la connessione      |
| `DB_PASSWORD`   | Password dell’utente del database   |

### Credenziali Enel per scraping

| Variabile         | Descrizione                                |
|-------------------|--------------------------------------------|
| `ENEL_USERNAME`   | Email o username per login area clienti    |
| `ENEL_PASSWORD`   | Password dell’account Enel                 |
| `ENEL_POD`        | Codice POD (identificatore punto di fornitura) |
| `ENEL_USER_NUMBER`| Codice utente associato al contratto       |
| `ENEL_CF`         | Codice fiscale del titolare del contratto  |
| `ENEL_BP`         | Business Partner (BP) code |
| `ENEL_CC`         | Codice contratto Enel                      |

---

## Avvio

Per lanciare tutti i servizi:

```bash
chmod +x reset_all.sh
./reseset_all.sh
```
### ATTENZIONE
Al primo avvio è necessario assicurarsi della corretta terminazione dello script `scripts/fetch_bollette.py` (ossia verificare la presenza dell'output corretto dei dati in `scripts/data/bollette_raw.json`).
Se dopo un minuto circa dall'avvio dei container il file di output non risulta su disco significa che il fetch delle bollette non è avvenuto correttamente ed è sufficiente riavviare lo script, anche manualmente tramite  
```python
  python3 fetch_bollette.py
```
[!] Se non esistono nel database dati relativi alle bollette l'applicativo di Flask darà errore all'apertura fintanto che essi non sono presenti.

---

## Autore

Progetto fatto abbastanza randomicamente by subnetMusk ⚡️

Per informazioni legali e condizioni d’uso, fare riferimento al [DISCLAIMER.md](./DISCLAIMER.md).