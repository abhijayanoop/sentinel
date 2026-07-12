import httpx
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings

class Deploy(BaseModel):
    sha: str
    message: str
    author: str
    timestamp: str

class DeployResult(BaseModel):
    deploys: list[Deploy]

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
def get_recent_deploys(repo: str = "your-username/your-demo-repo", limit: int = 5) -> DeployResult:
    url = f"https://api.github.com/repos/{repo}/commits"
    headers = {"Accept": "application/vnd.github+json"}
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"

    res = httpx.get(url, headers=headers, params={"per_page": limit}, timeout=10)
    res.raise_for_status()

    deploys = [
        Deploy(
            sha=c["sha"][:7],
            message=c["commit"]["message"].splitlines()[0],
            author=c["commit"]["author"]["name"],
            timestamp=c["commit"]["author"]["date"],
        )
        for c in res.json()
    ]

    return DeployResult(deploys=deploys)