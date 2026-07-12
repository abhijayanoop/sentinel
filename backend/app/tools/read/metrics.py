import boto3
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings

_cw_client = boto3.client("cloudwatch", region_name=settings.aws_region if hasattr(settings, "aws_region") else "ap-south-1")

class MetricPoint(BaseModel):
    timestamp: str
    value: float


class MetricResult(BaseModel):
    metric_name: str
    points: list[MetricPoint]
    latest_value: float | None

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
def get_metric_data(
    namespace: str,
    metric_name: str,
    dimension_name: str,
    dimension_value: str,
    minutes: int = 30,
) -> MetricResult:
    end = datetime.now(timezone.utc)
    start = end - timedelta(minutes=minutes)

    resp = _cw_client.get_metric_statistics(
        Namespace=namespace,
        MetricName=metric_name,
        Dimensions=[{"Name": dimension_name, "Value": dimension_value}],
        StartTime=start,
        EndTime=end,
        Period=60,
        Statistics=["Average"],
    )

    datapoints = sorted(resp["Datapoints"], key=lambda d: d["Timestamp"])
    points = [
        MetricPoint(timestamp=p["Timestamp"].isoformat(), value=round(p["Average"], 2))
        for p in datapoints
    ]

    return MetricResult(metric_name=metric_name, points=points, latest_value=points[-1].value if points else None,)