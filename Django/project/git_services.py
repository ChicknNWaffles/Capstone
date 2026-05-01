import os
# import git
from pathlib import Path
from git import Repo, Actor, GitCommandError
from django.conf import settings
from django.utils.timezone import now

class ProjectGitService:
    # initial repo setup
    def __init__(self, project):
        self.project = project
        self.repo_path = project.repo_link 
        self.repo = Repo(self.repo_path)

        print(self.repo)

        # establishes and writes a gitignore for us
        gitignore_path = self.repo_link / ".gitignore"
        gitignore_path.write_text("\n__pycache__/\n*.pyc\n.DS_Store\n")
        self.repo.index.add([str(gitignore_path)])
        self.repo.index.commit("Initial commit")

    def commit(self, message: str, user):
        self.repo.index.add(["."])                     

        author = Actor(user)

        commit = self.repo.index.commit(
            message,
            author=author,
            committer=author
        )
        return {
            "hash": commit.hexsha,
            "message": commit.message,
            "author": commit.author.name,
            "date": commit.committed_datetime
        }

    def create_branch(self, name: str):
        new_branch = self.repo.create_head(name)
        return {"branch": new_branch.name, "commit": new_branch.commit.hexsha}

    def switch_branch(self, name: str):
        branch = self.repo.heads[name]
        branch.checkout()

        self.project.current_branch = name
        self.project.save()

        return {"branch": name, "commit": branch.commit.hexsha}

    def merge_branch(self, source_branch_name: str):
        current_branch = self.repo.active_branch
        source_branch = self.repo.heads[source_branch_name]

        # Find merge base for 3-way merge
        merge_base = self.repo.merge_base(source_branch, current_branch)

        try:
            # Perform the merge into the index (tutorial pattern)
            self.repo.index.merge_tree(source_branch, base=merge_base)

            # Create merge commit with two parents
            merge_commit = self.repo.index.commit(
                f"Merge branch '{source_branch_name}' into {current_branch.name}",
                parent_commits=(current_branch.commit, source_branch.commit),
                author=Actor("System Merge", "system@ide.local"),
                committer=Actor("System Merge", "system@ide.local")
            )

            return {
                "merged": True,
                "into": current_branch.name,
                "from": source_branch_name,
                "merge_commit": merge_commit.hexsha
            }

        except GitCommandError as e:
            raise ValueError(f"Merge conflict occurred: {str(e)}") from e

    def push(self):
        if not self.project.remote_url:
            raise ValueError("No remote URL configured for this project")

        # Create or get origin remote
        if "origin" not in [r.name for r in self.repo.remotes]:
            origin = self.repo.create_remote("origin", self.project.remote_url)
        else:
            origin = self.repo.remotes.origin

        # Push with error raising (recommended in tutorial)
        push_info = origin.push(self.repo.active_branch.name).raise_if_error()

        return {"pushed": True, "branch": self.repo.active_branch.name}

    def pull(self):
        if not self.project.remote_url:
            raise ValueError("No remote URL configured")

        if "origin" not in [r.name for r in self.repo.remotes]:
            self.repo.create_remote("origin", self.project.remote_url)

        origin = self.repo.remotes.origin
        fetch_info = origin.pull()   # pulls + merges

        return {"pulled": True, "branch": self.repo.active_branch.name}

    def history(self, max_count=20):
        commits = list(self.repo.iter_commits(self.repo.active_branch.name, max_count=max_count))
        return [{
            "hash": c.hexsha,
            "message": c.message.strip(),
            "author": c.author.name,
            "date": c.committed_datetime.isoformat()
        } for c in commits]