from langchain_core.prompts import PromptTemplate

CODE_REVIEW_PROMPT = PromptTemplate(
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
                                """)

CODE_SUMMARY_PROMPT = PromptTemplate(
    input_variables=["code_diff"],
    template="Summarize the following code changes:\n{code_diff}"
)

PR_SUMMARY_PROMPT = PromptTemplate(
    input_variables=["description"],
    template="Summarize this pull request:\n{description}"
)

CODE_SUMMARY = """Act as a Code Reviewer Assistant. I will give a code diff content.
And I want you to briefly summarize the content of the diff to helper reviewers understand what happened in this file
faster and more convienently.

Your summary must be totaly objective and contains no opinions or suggestions.
For example: ```This diff contains change in functions `create_database`,`delete_database`,
it add a parameter `force` to these functions.
```

Here's the diff of file {name}:
```{language}
{content}
```
"""