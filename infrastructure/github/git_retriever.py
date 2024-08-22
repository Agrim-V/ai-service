from github3 import login

class GithubRetriever:
    def __init__(self, github_token, owner, repo_name, pr_number):
        self.gh = login(token=github_token)
        self.repo = self.gh.repository(owner, repo_name)
        self.pull_request = self.repo.pull_request(pr_number)
        self.commented_lines = set()

    def get_pr_details(self):
        files_changed = [file for file in self.pull_request.files()]
        commit_messages = [commit.message for commit in self.pull_request.commits()]
        pr_comments = [comment.body for comment in self.pull_request.issue_comments()]
        return {
            "description": self.pull_request.body,
            "files_changed": files_changed,
            "commit_messages": commit_messages,
            "pr_comments": pr_comments
        }
    
    def add_commented_line(self, file_path, line_number):
        self.commented_lines.add((file_path, line_number))