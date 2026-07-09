import hashlib
import hmac
import json

import pytest

from app.core.config import settings


def _sign(body: bytes) -> str:
    return hmac.new(settings.webhook_secret.encode(), body, hashlib.sha256).hexdigest()


@pytest.mark.asyncio
async def test_rejects_bad_signature(client):
    body = json.dumps({"alarmId": "x", "stateChangeTime": "t"}).encode()
    resp = await client.post(
        "/webhooks/cloudwatch",
        content=body,
        headers={"X-Signature": "wrong", "Content-Type": "application/json"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_accepts_valid_and_dedupes_duplicate(client):
    body = json.dumps({"alarmId": "abc", "stateChangeTime": "2026-07-03T10:00:00Z"}).encode()
    headers = {"X-Signature": _sign(body), "Content-Type": "application/json"}

    first = await client.post("/webhooks/cloudwatch", content=body, headers=headers)
    assert first.status_code == 200
    assert first.json()["status"] == "accepted"

    second = await client.post("/webhooks/cloudwatch", content=body, headers=headers)
    assert second.status_code == 200
    assert second.json()["status"] == "duplicate_ignored"