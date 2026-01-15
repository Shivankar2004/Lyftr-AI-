from fastapi import FastAPI, Request, Header, HTTPException
from pydantic import BaseModel, constr
import hmac, hashlib, time

from app.config import DATABASE_URL, WEBHOOK_SECRET
from app.models import init_db
from app.storage import insert_message
from app.metrics import inc_webhook, render_metrics

app = FastAPI()
conn = init_db(DATABASE_URL.replace("sqlite:///", ""))

# =========================
# RESPONSE MODELS
# =========================

class HealthResponse(BaseModel):
    status: str


class WebhookResponse(BaseModel):
    status: str


class MessagesResponse(BaseModel):
    data: list
    total: int
    limit: int
    offset: int


class StatsResponse(BaseModel):
    total_messages: int
    senders_count: int
    messages_per_sender: list
    first_message_ts: str | None
    last_message_ts: str | None


# =========================
# REQUEST MODEL
# =========================

class WebhookMessage(BaseModel):
    message_id: constr(min_length=1)
    from_: constr(regex=r"^\+\d+$")
    to: constr(regex=r"^\+\d+$")
    ts: constr(regex=r".+Z$")
    text: constr(max_length=4096) | None = None


# =========================
# ENDPOINTS
# =========================

@app.post("/webhook", response_model=WebhookResponse)
async def webhook(request: Request, x_signature: str = Header(...)):
    raw = await request.body()

    expected = hmac.new(
        WEBHOOK_SECRET.encode(), raw, hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, x_signature):
        inc_webhook("invalid_signature")
        raise HTTPException(status_code=401, detail="invalid signature")

    body = await request.json()
    result = insert_message(conn, {
        "message_id": body["message_id"],
        "from": body["from"],
        "to": body["to"],
        "ts": body["ts"],
        "text": body.get("text")
    })

    inc_webhook(result)
    return {"status": "ok"}


@app.get("/messages", response_model=MessagesResponse)
def messages(limit: int = 50, offset: int = 0):
    cur = conn.cursor()
    total = cur.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    rows = cur.execute(
        "SELECT message_id, from_msisdn, to_msisdn, ts, text FROM messages "
        "ORDER BY ts ASC, message_id ASC LIMIT ? OFFSET ?",
        (limit, offset)
    ).fetchall()

    data = [
        {"message_id": r[0], "from": r[1], "to": r[2], "ts": r[3], "text": r[4]}
        for r in rows
    ]

    return {"data": data, "total": total, "limit": limit, "offset": offset}


@app.get("/stats", response_model=StatsResponse)
def stats():
    cur = conn.cursor()
    total = cur.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    senders = cur.execute(
        "SELECT from_msisdn, COUNT(*) FROM messages GROUP BY from_msisdn "
        "ORDER BY COUNT(*) DESC LIMIT 10"
    ).fetchall()

    first = cur.execute("SELECT MIN(ts) FROM messages").fetchone()[0]
    last = cur.execute("SELECT MAX(ts) FROM messages").fetchone()[0]

    return {
        "total_messages": total,
        "senders_count": len(senders),
        "messages_per_sender": [{"from": s[0], "count": s[1]} for s in senders],
        "first_message_ts": first,
        "last_message_ts": last
    }


@app.get("/health/live", response_model=HealthResponse)
def live():
    return {"status": "alive"}


@app.get("/health/ready", response_model=HealthResponse)
def ready():
    try:
        conn.execute("SELECT 1")
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="not ready")


@app.get("/metrics")
def metrics():
    return render_metrics()
