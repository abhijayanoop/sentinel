import hashlib
import hmac
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

import boto3

from app.core.config import settings

CLUSTER = "sentinel-cluster"
SERVICE = "sentinel-backend-service"
TASK_FAMILY = "sentinel-backend"
BACKEND_URL = os.environ.get("AGENT_BACKEND_URL", "http://localhost:8000")

ecs = boto3.client("ecs", region_name="ap-south-1")


def _notify_agent() -> None:
    """Trigger the agent directly instead of waiting on the CloudWatch alarm to
    fire and relay through SNS/Lambda — that path only completes once the
    service is at least partially reachable again, which defeats the point of
    signaling an outage. A real alarm still fires for the dashboard; this is
    what actually drives the demo."""
    payload = {
        "alarmId": "sentinel-backend-unhealthy",
        "stateChangeTime": datetime.now(timezone.utc).isoformat(),
        "newState": "ALARM",
        "reason": "chaos.py break: simulated crash loop",
    }
    body = json.dumps(payload).encode()
    signature = hmac.new(settings.webhook_secret.encode(), body, hashlib.sha256).hexdigest()

    req = urllib.request.Request(
        f"{BACKEND_URL}/webhooks/cloudwatch",
        data=body, method="POST",
        headers={"Content-Type": "application/json", "X-Signature": signature},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"\nNotified agent: {resp.status} {resp.read().decode()}")
    except urllib.error.URLError as e:
        print(f"\nCould not notify agent at {BACKEND_URL}: {e}")
        print("Is the backend running locally? (uv run uvicorn app.main:app --reload)")


def _current_task_def_arn() -> str:
    svc = ecs.describe_services(cluster=CLUSTER, services=[SERVICE])["services"][0]
    return svc["taskDefinition"]


def break_service() -> None:
    """Register a task definition with a command that exits immediately, causing
    a crash loop. Tasks fail to stay running -> RunningTaskCount drops -> alarm fires."""
    current_arn = _current_task_def_arn()
    print(f"Current (healthy) task definition: {current_arn}")
    print("Save this ARN — the agent should roll back to it.\n")

    td = ecs.describe_task_definition(taskDefinition=TASK_FAMILY)["taskDefinition"]

    # strip read-only fields so we can re-register
    for field in (
        "taskDefinitionArn",
        "revision",
        "status",
        "requiresAttributes",
        "compatibilities",
        "registeredAt",
        "registeredBy",
    ):
        td.pop(field, None)

    # THE BREAKAGE: override the command so the container exits immediately
    td["containerDefinitions"][0]["command"] = [
        "sh",
        "-c",
        "echo 'simulated failure'; exit 1",
    ]

    broken = ecs.register_task_definition(**td)["taskDefinition"]["taskDefinitionArn"]
    print(f"Registered BROKEN task definition: {broken}")

    ecs.update_service(cluster=CLUSTER, service=SERVICE, taskDefinition=broken)
    print(f"Deployed broken definition to {SERVICE}")

    # ECS won't cut over on its own: with minimumHealthyPercent=100 and no
    # deployment circuit breaker, a rolling deployment never removes the last
    # healthy task until a replacement passes health checks — which the broken
    # revision never will. Force the issue by stopping the currently running
    # (still-healthy) task so ECS has no choice but to replace it right now.
    task_arns = ecs.list_tasks(cluster=CLUSTER, serviceName=SERVICE)["taskArns"]
    if task_arns:
        tasks = ecs.describe_tasks(cluster=CLUSTER, tasks=task_arns)["tasks"]
        old_tasks = [t["taskArn"] for t in tasks if t["taskDefinitionArn"] != broken]
        for task_arn in old_tasks:
            ecs.stop_task(cluster=CLUSTER, task=task_arn, reason="chaos: forcing cutover to broken revision")
            print(f"Stopped old healthy task: {task_arn}")

    print("\nTasks will now crash-loop. The CloudWatch alarm will fire within ~2")
    print("minutes for the dashboard, but the agent is notified directly below.")
    _notify_agent()


def status() -> None:
    svc = ecs.describe_services(cluster=CLUSTER, services=[SERVICE])["services"][0]
    print(f"Service:          {SERVICE}")
    print(f"Task definition:  {svc['taskDefinition']}")
    print(f"Desired count:    {svc['desiredCount']}")
    print(f"Running count:    {svc['runningCount']}")
    print(f"Pending count:    {svc['pendingCount']}")
    print("\nRecent events:")
    for event in svc["events"][:5]:
        print(f"  {event['createdAt'].strftime('%H:%M:%S')}  {event['message']}")


def fix() -> None:
    """Manual restore — normally the AGENT does this via an approved rollback."""
    td_list = ecs.list_task_definitions(familyPrefix=TASK_FAMILY, sort="DESC")[
        "taskDefinitionArns"
    ]
    for arn in td_list:
        td = ecs.describe_task_definition(taskDefinition=arn)["taskDefinition"]
        cmd = td["containerDefinitions"][0].get("command")
        if not cmd or "simulated failure" not in " ".join(cmd):
            ecs.update_service(cluster=CLUSTER, service=SERVICE, taskDefinition=arn)
            print(f"Restored service to healthy task definition: {arn}")
            return
    print("Could not find a healthy task definition to restore.")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"break": break_service, "status": status, "fix": fix}.get(cmd, status)()
