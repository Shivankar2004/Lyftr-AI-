http_requests = {}
webhook_results = {}

def inc_http(path, status):
    http_requests[(path, status)] = http_requests.get((path, status), 0) + 1

def inc_webhook(result):
    webhook_results[result] = webhook_results.get(result, 0) + 1

def render_metrics():
    lines = []
    for (p, s), v in http_requests.items():
        lines.append(f'http_requests_total{{path="{p}",status="{s}"}} {v}')
    for r, v in webhook_results.items():
        lines.append(f'webhook_requests_total{{result="{r}"}} {v}')
    return "\n".join(lines)
