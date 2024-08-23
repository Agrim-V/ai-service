from langchain_core.prompts import PromptTemplate

class CodeReviewPrompts:
    def __init__(self):
        self.CODE_REVIEW_PROMPT = PromptTemplate(
            input_variables=["code_diff"],
            template="""Your task is to review pull requests. Instructions:
                        - Do not give positive comments or compliments.
                        - Provide comments and suggestions ONLY if there is something to improve, otherwise return an empty array.
                        - Provide conceptual knowledge in the comments if necessary.
                        - Ensure endpoints follow RESTful architecture.
                        - Write the comment in GitHub Markdown format.
                        - For each comment, include the specific line number in the code diff that the comment applies to in the format `Line <line_number>: <comment>`.

                        Here's the code diff:
                        {code_diff}
                        """
        )

        self.CODE_SUMMARY_PROMPT = PromptTemplate(
            input_variables=["code_diff"],
            template="Summarize the following code changes:\n{code_diff}"
        )

        self.PR_SUMMARY_PROMPT = PromptTemplate(
            input_variables=["description"],
            template="Summarize this pull request:\n{description}"
        )
        