from github3 import login
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models.base import BaseChatModel
from langchain.chat_models import ChatOpenAI
from functools import lru_cache
from dotenv import load_dotenv
import os, re

from infrastructure.github.git_retriever import GithubRetriever

load_dotenv('/Users/qoala/Desktop/services/ai-service/.env')

class PRSummaryChain:
    def __init__(self, code_summary_llm, pr_summary_llm):
        self.code_summary_llm = code_summary_llm
        self.pr_summary_llm = pr_summary_llm

    def run(self, pr_details):
        code_summaries = []
        for file in pr_details['files_changed']:
            summary = LLMChain(
                llm=self.code_summary_llm,
                prompt=PromptTemplate.from_template("Summarize the following code changes:\n{code_diff}")
            ).run(code_diff=file.patch)
            code_summaries.append(summary)
        
        pr_summary = LLMChain(
            llm=self.pr_summary_llm,
            prompt=PromptTemplate.from_template("Summarize this pull request:\n{description}")
        ).run(description=pr_details['description'])

        return {
            "pr_summary": pr_summary,
            "code_summaries": code_summaries
        }

class CodeReviewChain:
    def __init__(self, llm):
        self.llm = llm

    def run(self, pr_details):
        code_reviews = []
        for file in pr_details['files_changed']:
            review = LLMChain(
                llm=self.llm,
                prompt=PromptTemplate.from_template(
                    """Your task is to review pull requests. Instructions:
                    - Do not give positive comments or compliments.
                    - Provide comments and suggestions ONLY if there is something to improve, otherwise return an empty array.
                    - Provide conceptual knowledge in the comments if necessary.
                    - Ensure endpoints follow RESTful architecture.
                    - Write the comment in GitHub Markdown format.
                    - For each comment, include the specific line number in the code diff that the comment applies to in the format `Line <line_number>: <comment>`.

                    Here's the code diff:
                    {code_diff}
                    """)
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

class PullRequestReporter:
    def __init__(self, pr_summary, code_summaries, pull_request, code_reviews):
        self.pr_summary = pr_summary
        self.code_summaries = code_summaries
        self.pull_request = pull_request
        self.code_reviews = code_reviews

    def report(self):
        report = f"### Pull Request Summary\n\n{self.pr_summary}\n\n"
        report += "### Code Summaries\n\n"
        for summary in self.code_summaries:
            report += f"{summary}\n\n"
        report += "### Code Reviews\n\n"
        print(self.code_reviews)
        for review in self.code_reviews:
            for comment in review['comments']:
                line_number = comment['line_number']
                comment_text = comment['comment']
                report += f"Line number: {line_number}\nComment: {comment_text}\n\n"
        return report

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
        pr_summary_chain = PRSummaryChain(
            code_summary_llm=load_gpt_llm(), 
            pr_summary_llm=load_gpt_llm()
        )
        summary = pr_summary_chain.run(pr_details)
        print(summary)

        # Initialize and run the code review chain
        code_review_chain = CodeReviewChain(llm=load_gpt_llm())
        reviews = code_review_chain.run(pr_details)
        print(reviews)
        # Generate the final report
        reporter = PullRequestReporter(
            pr_summary=summary["pr_summary"],
            code_summaries=summary["code_summaries"],
            pull_request=retriever.pull_request,
            code_reviews=reviews["code_reviews"]
        )
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
        return reporter.report()

@lru_cache(maxsize=1)
def load_gpt_llm() -> BaseChatModel:
    llm = ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-3.5-turbo",
    )
    return llm

@lru_cache(maxsize=1)
def load_gpt4_llm():
    llm = ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4",
    )
    return llm
