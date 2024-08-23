from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from infrastructure.models.prompts import CodeReviewPrompts

class PRSummaryChainService:
    def __init__(self, code_summary_llm, pr_summary_llm):
        self.code_summary_llm = code_summary_llm
        self.pr_summary_llm = pr_summary_llm

    def run(self, pr_details):
        code_summaries = []
        prompts = CodeReviewPrompts()
        for file in pr_details['files_changed']:
            summary = LLMChain(
                llm=self.code_summary_llm,
                prompt=prompts.CODE_SUMMARY_PROMPT
            ).run(code_diff=file.patch)
            code_summaries.append(summary)
        
        pr_summary = LLMChain(
            llm=self.pr_summary_llm,
            prompt=prompts.PR_SUMMARY_PROMPT
        ).run(description=pr_details['description'])

        return {
            "pr_summary": pr_summary,
            "code_summaries": code_summaries
        }