"""Send a signed test webhook. Usage: WEBHOOK_SECRET=... uv run python -m scripts.send_test_webhook"""
import hashlib
import hmac
import json
import os

import httpx

secret = os.environ["WEBHOOK_SECRET"]
body = json.dumps({"alarmId": "abc123", "stateChangeTime": "2026-07-03T10:00:00Z"}).encode()
signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

resp = httpx.post(
    "http://localhost:8000/webhooks/cloudwatch",
    data=body,
    headers={"X-Signature": signature, "Content-Type": "application/json"},
)
print(resp.status_code, resp.json())