from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from infrastructure.models.prompts import PR_SUMMARY_PROMPT, CODE_SUMMARY_PROMPT

class PRSummaryChainService:
    def __init__(self, code_summary_llm, pr_summary_llm):
        self.code_summary_llm = code_summary_llm
        self.pr_summary_llm = pr_summary_llm

    def run(self, pr_details):
        code_summaries = []
        for file in pr_details['files_changed']:
            summary = LLMChain(
                llm=self.code_summary_llm,
                prompt=CODE_SUMMARY_PROMPT
            ).run(code_diff=file.patch)
            code_summaries.append(summary)
        
        pr_summary = LLMChain(
            llm=self.pr_summary_llm,
            prompt=PR_SUMMARY_PROMPT
        ).run(description=pr_details['description'])

        return {
            "pr_summary": pr_summary,
            "code_summaries": code_summaries
        }