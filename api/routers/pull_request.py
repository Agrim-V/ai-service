from typing import Annotated
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Path

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
    owner: str, repo: str, github_token: str,
    pr_service: PullRequestService = Depends(Provide[Container.pr_service]),
):
    return pr_service.review_code(owner, repo, pr_number, github_token)
