\connect enel;

CREATE TABLE IF NOT EXISTS consumi_orari (
    data DATE NOT NULL,
    fascia TEXT NOT NULL,
    valore_kwh REAL NOT NULL,
    tipo_misura TEXT,
    PRIMARY KEY (data, fascia)
);

CREATE TABLE IF NOT EXISTS consumi_giornalieri (
    data DATE PRIMARY KEY,
    valore_kwh REAL NOT NULL,
    tipo_misura TEXT
);

CREATE TABLE IF NOT EXISTS bollette (
    numero TEXT PRIMARY KEY,
    scadenza DATE NOT NULL,
    importo REAL NOT NULL,
    stato_pagamento TEXT NOT NULL,
    voce_dettaglio JSONB,
    ricevuta_il TIMESTAMP DEFAULT NOW()
);