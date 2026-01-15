# Lyftr AI – Backend Assignment  
Containerized Webhook API

This repository implements the Lyftr AI Backend Assignment: a production-style FastAPI service for securely ingesting WhatsApp-like messages exactly once, with observability, metrics, and analytics.

---

##  Features
- HMAC-SHA256 protected `/webhook`
- Exactly-once message ingestion (idempotent)
- SQLite persistence under Docker volume
- Pagination & filters on `/messages`
- Analytics via `/stats`
- Liveness & readiness probes
- Prometheus-style `/metrics`
- Structured JSON logs
- 12-factor configuration
- Docker & Docker Compose ready

---

##  Configuration (Environment Variables)

The system requires:

```bash
export WEBHOOK_SECRET="testsecret"
export DATABASE_URL="sqlite:////data/app.db"
export LOG_LEVEL="INFO"
