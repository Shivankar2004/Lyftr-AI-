import json, time, uuid
from datetime import datetime

def log_request(request, response, start, extra=None):
    log = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "level": "INFO",
        "request_id": str(uuid.uuid4()),
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "latency_ms": int((time.time() - start) * 1000)
    }
    if extra:
        log.update(extra)
    print(json.dumps(log))
