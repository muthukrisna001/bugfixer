"""
Git Integration Module
Handles repository operations, branch creation, and PR management
"""
import os
import shutil
import tempfile
from typing import Optional, Dict, Any
from git import Repo, GitCommandError
import httpx
from decouple import config
from ..models.schemas import FixSuggestion, BugReport

class GitManager:
    """Manages Git operations and GitHub integration"""
    
    def __init__(self):
        self.github_token = config("GITHUB_TOKEN", default="")
        self.github_username = config("GITHUB_USERNAME", default="")
        self.git_user_name = config("GIT_USER_NAME", default="Bugfixer Bot")
        self.git_user_email = config("GIT_USER_EMAIL", default="bugfixer@example.com")
        self.temp_dir = tempfile.mkdtemp(prefix="bugfixer_")
    
    async def clone_repository(self, repo_url: str, branch: str = "main") -> str:
        """
        Clone a repository to a temporary directory
        """
        try:
            # Create a unique directory for this repo
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            repo_path = os.path.join(self.temp_dir, repo_name)
            
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)
            
            # Clone the repository
            repo = Repo.clone_from(repo_url, repo_path)
            
            # Configure git user
            with repo.config_writer() as git_config:
                git_config.set_value("user", "name", self.git_user_name)
                git_config.set_value("user", "email", self.git_user_email)
            
            return repo_path
            
        except GitCommandError as e:
            print(f"Git clone failed: {e}")
            raise
        except Exception as e:
            print(f"Repository clone failed: {e}")
            raise
    
    async def create_fix_branch(self, repo_path: str, bug_report: BugReport) -> str:
        """
        Create a new branch for the bug fix
        """
        try:
            repo = Repo(repo_path)
            
            # Create branch name based on bug info
            branch_name = f"bugfix/{bug_report.error_info.error_type.value.lower()}-{bug_report.id[:8]}"
            
            # Create and checkout new branch
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
            
            return branch_name
            
        except GitCommandError as e:
            print(f"Branch creation failed: {e}")
            raise
        except Exception as e:
            print(f"Failed to create branch: {e}")
            raise
    
    async def apply_fix(self, repo_path: str, bug_report: BugReport, fix_suggestion: FixSuggestion) -> bool:
        """
        Apply the fix to the code
        """
        try:
            file_path = bug_report.code_location.file_path
            
            # Read the current file
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Apply the fix (simplified approach)
            # In a real implementation, we'd need more sophisticated code replacement
            fixed_content = self._apply_code_fix(content, bug_report, fix_suggestion)
            
            # Write the fixed content back
            with open(file_path, 'w') as f:
                f.write(fixed_content)
            
            return True
            
        except Exception as e:
            print(f"Failed to apply fix: {e}")
            return False
    
    def _apply_code_fix(self, content: str, bug_report: BugReport, fix_suggestion: FixSuggestion) -> str:
        """
        Apply the code fix to the content
        This is a simplified implementation - in practice, you'd want more sophisticated parsing
        """
        lines = content.split('\n')
        line_num = bug_report.code_location.line_number - 1  # Convert to 0-based index
        
        # Get the fix lines
        fix_lines = fix_suggestion.fixed_code.split('\n')
        
        # Find the original problematic line and replace the section
        # This is a very basic implementation
        if line_num < len(lines):
            # Replace the problematic section with the fix
            # For now, we'll replace a few lines around the problematic line
            start_idx = max(0, line_num - 2)
            end_idx = min(len(lines), line_num + 3)
            
            # Replace the section
            new_lines = lines[:start_idx] + fix_lines + lines[end_idx:]
            return '\n'.join(new_lines)
        
        return content
    
    async def commit_fix(self, repo_path: str, bug_report: BugReport, fix_suggestion: FixSuggestion) -> str:
        """
        Commit the fix to the repository
        """
        try:
            repo = Repo(repo_path)
            
            # Add the changed file
            repo.git.add(bug_report.code_location.file_path)
            
            # Create commit message
            commit_message = f"Fix {bug_report.error_info.error_type.value}: {fix_suggestion.description}\n\n" \
                           f"- {fix_suggestion.explanation}\n" \
                           f"- Confidence: {fix_suggestion.confidence:.1%}\n" \
                           f"- Bug ID: {bug_report.id}"
            
            # Commit the changes
            commit = repo.index.commit(commit_message)
            
            return commit.hexsha
            
        except GitCommandError as e:
            print(f"Commit failed: {e}")
            raise
        except Exception as e:
            print(f"Failed to commit: {e}")
            raise
    
    async def push_branch(self, repo_path: str, branch_name: str) -> bool:
        """
        Push the branch to the remote repository
        """
        try:
            repo = Repo(repo_path)
            
            # Push the branch
            origin = repo.remote('origin')
            origin.push(branch_name)
            
            return True
            
        except GitCommandError as e:
            print(f"Push failed: {e}")
            return False
        except Exception as e:
            print(f"Failed to push branch: {e}")
            return False
    
    async def create_pull_request(self, repo_owner: str, repo_name: str, branch_name: str, 
                                bug_report: BugReport, fix_suggestion: FixSuggestion) -> Optional[str]:
        """
        Create a pull request on GitHub
        """
        if not self.github_token:
            print("GitHub token not configured")
            return None
        
        try:
            # Prepare PR data
            pr_title = f"Fix {bug_report.error_info.error_type.value}: {fix_suggestion.description}"
            pr_body = f"""## Bug Fix

**Error Type:** {bug_report.error_info.error_type.value}
**File:** {bug_report.code_location.file_path}
**Line:** {bug_report.code_location.line_number}
**Function:** {bug_report.code_location.function_name or 'Unknown'}

### Description
{fix_suggestion.explanation}

### Changes Made
- {fix_suggestion.description}

### Confidence Level
{fix_suggestion.confidence:.1%}

### Original Error
```
{bug_report.error_info.error_message}
```

### Code Changes
```python
# Before
{fix_suggestion.original_code}

# After
{fix_suggestion.fixed_code}
```

---
*This PR was automatically generated by Bugfixer Bot*
"""
            
            # GitHub API request
            url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            data = {
                "title": pr_title,
                "body": pr_body,
                "head": branch_name,
                "base": "main"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, headers=headers)
                
                if response.status_code == 201:
                    pr_data = response.json()
                    return pr_data["html_url"]
                else:
                    print(f"PR creation failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            print(f"Failed to create PR: {e}")
            return None
    
    async def cleanup_temp_directory(self):
        """
        Clean up temporary directories
        """
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Failed to cleanup temp directory: {e}")
    
    def __del__(self):
        """
        Cleanup on destruction
        """
        try:
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except:
            pass
