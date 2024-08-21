from typing import Annotated
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from api.container import Container
from services.pull_requests import PullRequestService

router = APIRouter(
    prefix="",
    tags=["PullRequest"],
)

@router.post("/pr/review")
@inject
async def review_code(
    pr_number: int,
    owner: str,
    repo: str,
    github_token: str,
    pr_service: PullRequestService = Depends(Provide[Container.pr_service]),
):
    # Update the service instance with the dynamic values if necessary
    pr_service.owner = owner
    pr_service.repo = repo
    pr_service.pr_number = pr_number
    pr_service.github_token = github_token
    return pr_service.review_code()
