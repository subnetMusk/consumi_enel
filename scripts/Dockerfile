FROM python:3.11-slim

# Installa dipendenze
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libx11-xcb1 \
    cron \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Crea cartella lavoro
WORKDIR /app
COPY . .

# Installa dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

RUN [ -f /usr/bin/google-chrome ] || ln -s /usr/bin/chromium /usr/bin/google-chrome && \
    [ -f /usr/bin/chromedriver ] || ln -s /usr/lib/chromium/chromedriver /usr/bin/chromedriver

# Crea cron job ogni 6 ore per run_all.sh
RUN echo "0 */6 * * * root bash /app/run_all.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/enel

# Imposta permessi corretti
RUN chmod 0644 /etc/cron.d/enel && crontab /etc/cron.d/enel && touch /var/log/cron.log

# Avvia cron in foreground
CMD bash -c "bash /app/run_all.sh >> /var/log/cron.log 2>&1 && cron -f"
