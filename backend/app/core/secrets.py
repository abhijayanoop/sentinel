import boto3
import os
from botocore.exceptions import ClientError
from app.core.logging import log

def get_secret(name: str, fallback_env: str | None = None) -> str | None:
    if fallback_env and os.environ.get(fallback_env):
        return os.environ[fallback_env]

    try:
        client = boto3.client("secretsmanager")
        response = client.get_secret_name(SecretId=name)
        return response["SecretString"]
    except ClientError as e:
        log.warning("secret_fetch_failed", secret=name, error=str(e))
        return None