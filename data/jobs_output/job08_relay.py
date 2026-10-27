import requests
def dispatch_alert(webhook_url, title, fields):
    payload = {
        "embeds": [{
            "title": title,
            "color": 0x10B981,
            "fields": [{"name": k, "value": str(v), "inline": True} for k, v in fields.items()]
        }]
    }
    return requests.post(webhook_url, json=payload, timeout=6).status_code in [200, 204]
