#!/bin/bash
set -e

echo "Login Enel..."
python fetch_login.py

echo "Prelievo consumi..."
python fetch_consumi.py

echo "Salvataggio consumi..."
python save_consumi.py

echo "Prelievo bollette..."
python fetch_bollette.py

echo "Salvataggio bollette..."
python save_bollette.py

echo "Scraping completato."
