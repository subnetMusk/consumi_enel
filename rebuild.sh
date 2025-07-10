#!/bin/bash

set -e

echo "Arresto e rimozione dei container (ma NON dei volumi)..."
docker compose down --remove-orphans

echo "Pulizia directory temporanee (senza toccare i volumi persistenti)..."
rm -rf scripts/data scripts/cookies scripts/screenshots
mkdir -p scripts/data scripts/cookies scripts/screenshots

echo "Ricostruzione leggera delle immagini Docker (con cache)..."
docker compose build

echo "Avvio dei container..."
docker compose up -d --force-recreate

echo " Tutti i container sono stati aggiornati e avviati."