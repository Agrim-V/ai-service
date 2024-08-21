from dependency_injector import containers, providers
from services.pull_requests import PullRequestService, load_gpt_llm, load_gpt4_llm

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["api.routers"])

    # LLM Providers
    code_summary_llm = providers.Singleton(load_gpt_llm)
    pr_summary_llm = providers.Singleton(load_gpt_llm)
    review_llm = providers.Singleton(load_gpt4_llm)

    # Services
    pr_service = providers.Factory(
        PullRequestService,
        owner="some_owner",
        repo="some_repo",
        pr_number=1,
        github_token="some_token",
        code_summary_llm=code_summary_llm,
        pr_summary_llm=pr_summary_llm,
        review_llm=review_llm
    )
