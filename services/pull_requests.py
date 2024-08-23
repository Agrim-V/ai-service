from github import Github
from langchain.chains import LLMChain
from langchain.chat_models.base import BaseChatModel
from dotenv import load_dotenv
import os, re, ipdb

from infrastructure.github.git_retriever import GithubRetriever
from infrastructure.repositories.llm.pr_summary import PRSummaryChainService
from infrastructure.models.prompts import CODE_REVIEW_PROMPT
from infrastructure.models.llm_gpt import GPT35Model

load_dotenv('/Users/qoala/Desktop/services/ai-service/.env')

class CodeReviewChain:
    def __init__(self, llm):
        self.llm = llm

    def run(self, pr_details):
        code_reviews = []
        for file in pr_details['files_changed']:
            review = LLMChain(
                llm=self.llm,
                prompt=CODE_REVIEW_PROMPT
            ).run(code_diff=file.patch)

            for line in review.splitlines():
                pattern = r'^- Line (\d+): (.*)$'
    
                match = re.match(pattern, line)
                if match:
                    # Extract line number and comment from the match
                    line_number = int(match.group(1))
                    comment = match.group(2)

                    comments = [{
                        "file_path": file.filename,
                        "line_number": line_number,
                        "comment": comment.strip()
                    }]
                    code_reviews.append({"file_path": file.filename, "comments": comments})
        return {"code_reviews": code_reviews}

class PullRequestService:
    def __init__(self, owner: str, repo: str, pr_number: int, github_token: str,
                 code_summary_llm: BaseChatModel, pr_summary_llm: BaseChatModel, review_llm: BaseChatModel):
        self.owner = owner
        self.repo = repo
        self.pr_number = pr_number
        self.github_token = github_token
        self.code_summary_llm = code_summary_llm
        self.pr_summary_llm = pr_summary_llm
        self.review_llm = review_llm

    def review_code(self):
        retriever = GithubRetriever(self.github_token, self.owner, self.repo, self.pr_number)
        pr_details = retriever.get_pr_details()

        print(pr_details)

        # Initialize and run the summary chain
        pr_summary_chain = PRSummaryChainService(
            code_summary_llm=GPT35Model().load_llm(), 
            pr_summary_llm=GPT35Model().load_llm()
        )
        summary = pr_summary_chain.run(pr_details)
        print(summary)

        # Initialize and run the code review chain
        code_review_chain = CodeReviewChain(GPT35Model().load_llm())
        reviews = code_review_chain.run(pr_details)
        print(reviews)
        
        # Optionally, post comments inline
        for review in reviews["code_reviews"]:
            for comment in review["comments"]:
                # Use the GitHub API to post the comment directly in the PR
                file_path = comment["file_path"]
                line_number = comment["line_number"]
                comment_text = comment["comment"]
                retriever.pull_request.create_review_comment(
                    body=comment_text,
                    commit_id=retriever.pull_request.head.sha,
                    path=file_path,
                    position=line_number
                )
                retriever.add_commented_line(file_path, line_number)
        
        return self.report(
            pr_summary=summary["pr_summary"],
            code_summaries=summary["code_summaries"],
            pull_request=retriever.pull_request,
            code_reviews=reviews["code_reviews"]
        )
        

    def report(self, pr_summary, code_summaries, pull_request, code_reviews):
        report = f"### Pull Request Summary\n\n{pr_summary}\n\n"
        report += "### Code Summaries\n\n"
        for summary in code_summaries:
            report += f"{summary}\n\n"
        report += "### Code Reviews\n\n"
        print(code_reviews)
        for review in code_reviews:
            for comment in review['comments']:
                line_number = comment['line_number']
                comment_text = comment['comment']
                report += f"Line number: {line_number}\nComment: {comment_text}\n\n"
        return report