#!/bin/bash

set -e

echo "Arresto e rimozione dei container e dei volumi..."
docker compose down --volumes --remove-orphans

echo "Pulizia directory locali temporanee..."
rm -rf scripts/data scripts/cookies scripts/screenshots scripts/cronlog
mkdir -p scripts/data scripts/cookies scripts/screenshots scripts/cronlog

echo "Ricostruzione delle immagini Docker (senza cache)..."
docker compose build --no-cache

echo "Avvio dei container..."
docker compose up -d --force-recreate --build

echo " Tutti i container sono stati avviati."
echo "Il container 'scraper' eseguirà lo script 'run_all.sh' ogni 6 ore tramite cron."