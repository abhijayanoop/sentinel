import hashlib
import hmac
import json
import os
import urllib.request

import boto3

BACKEND_URL = os.environ["BACKEND_URL"]
WEBHOOK_SECRET_ARN = os.environ["WEBHOOK_SECRET_ARN"]

_secrets_client = boto3.client("secretsmanager")
_cached_secret = None


def _webhook_secret() -> str:
    global _cached_secret
    if _cached_secret is None:
        _cached_secret = _secrets_client.get_secret_value(SecretId=WEBHOOK_SECRET_ARN)["SecretString"]
    return _cached_secret


def handler(event, _context):
    for record in event["Records"]:
        message = json.loads(record["Sns"]["Message"])

        if message.get("NewStateValue") != "ALARM":
            continue

        payload = {
            "alarmId": message["AlarmName"],
            "stateChangeTime": message["StateChangeTime"],
            "newState": message["NewStateValue"],
            "reason": message.get("NewStateReason"),
        }
        body = json.dumps(payload).encode()
        signature = hmac.new(_webhook_secret().encode(), body, hashlib.sha256).hexdigest()

        req = urllib.request.Request(
            BACKEND_URL,
            data=body,
            method="POST",
            headers={"Content-Type": "application/json", "X-Signature": signature},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"forwarded alarm {message['AlarmName']}: backend responded {resp.status}")
