FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
ENV TZ=UTC
WORKDIR /app

# Install cron + tzdata
RUN apt-get update && apt-get install -y cron tzdata && rm -rf /var/lib/apt/lists/*

# Copy Python deps from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Setup directories used by your cron script
RUN mkdir -p /data /cron && chmod 755 /data /cron \
    && touch /cron/last_code.txt

# Install cron job file
COPY cron/2fa-cron /etc/cron.d/2fa-cron
RUN sed -i 's/\r$//' /etc/cron.d/2fa-cron
RUN chmod 0644 /etc/cron.d/2fa-cron

# Expose API port
EXPOSE 8080

# Start cron in the background, then start your FastAPI app
CMD cron && uvicorn main:app --host 0.0.0.0 --port 8080