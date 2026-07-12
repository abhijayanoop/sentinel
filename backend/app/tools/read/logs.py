import time

import boto3
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

_logs = boto3.client("logs", region_name="ap-south-1")


class LogLine(BaseModel):
    timestamp: str
    message: str


class LogsResult(BaseModel):
    lines: list[LogLine]


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
def get_cloudwatch_logs(log_group: str, minutes: int = 15, limit: int = 20) -> LogsResult:
    query = f"fields @timestamp, @message | sort @timestamp desc | limit {limit}"
    start_result = _logs.start_query(
        logGroupName=log_group,
        startTime=int(time.time()) - minutes * 60,
        endTime=int(time.time()),
        queryString=query,
    )
    query_id = start_result["queryId"]

    for _ in range(15):
        result = _logs.get_query_results(queryId=query_id)
        if result["status"] == "Complete":
            break
        time.sleep(1)

    lines = []
    for row in result.get("results", []):
        fields = {f["field"]: f["value"] for f in row}
        lines.append(LogLine(timestamp=fields.get("@timestamp", ""), message=fields.get("@message", "")))
    return LogsResult(lines=lines)