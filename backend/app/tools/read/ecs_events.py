import boto3
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

_ecs = boto3.client("ecs", region_name="ap-south-1")


class ServiceEvent(BaseModel):
    timestamp: str
    message: str


class EcsEventsResult(BaseModel):
    events: list[ServiceEvent]


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
def get_ecs_service_events(cluster: str, service: str, limit: int = 10) -> EcsEventsResult:
    resp = _ecs.describe_services(cluster=cluster, services=[service])
    if not resp["services"]:
        return EcsEventsResult(events=[])
    raw = resp["services"][0].get("events", [])[:limit]
    events = [
        ServiceEvent(timestamp=e["createdAt"].isoformat(), message=e["message"])
        for e in raw
    ]
    return EcsEventsResult(events=events)