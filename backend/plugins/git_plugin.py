"""
Git Plugin for ArbiterAI
Version control operations with state management.

Phase 1: Local State Management
- git init, status, add, commit, log
- Repository state tracking

Phase 2: Remote Operations
- git clone, push, pull, fetch
- Remote repository management
"""

import subprocess
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import json

sys.path.append(str(Path(__file__).parent.parent))

from plugin_interface import (
    ArbiterPlugin,
    PluginMetadata,
    PluginResult,
    PluginPermission
)


class GitPlugin(ArbiterPlugin):
    """
    Git version control plugin.
    
    Features:
    - Initialize repositories
    - Track repository state
    - Stage and commit changes
    - View commit history
    - Clone remote repositories
    - Push/pull to/from remotes
    - Manage remote connections
    """
    
    def __init__(self):
        self.repo_path = None
        self.workspace_path = None
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="git",
            version="1.0.0",
            author="ArbiterAI",
            description="Git version control operations and state management",
            dependencies=["git"],
            permissions=[
                PluginPermission.FILESYSTEM,
                PluginPermission.SHELL
            ]
        )
    
    def initialize(self, workspace: str) -> bool:
        """Initialize plugin with workspace."""
        self.workspace_path = Path(workspace)
        self.repo_path = self.workspace_path
        
        # Configure git user if not set
        self._configure_git_user()
        
        return True
    
    def _configure_git_user(self):
        """Configure git user name and email."""
        user_name = os.getenv("GIT_USER_NAME", "ArbiterAI")
        user_email = os.getenv("GIT_USER_EMAIL", "arbiter@ai.local")
        
        try:
            subprocess.run(
                ["git", "config", "--global", "user.name", user_name],
                capture_output=True
            )
            subprocess.run(
                ["git", "config", "--global", "user.email", user_email],
                capture_output=True
            )
        except Exception:
            pass  # Git config is optional
    
    def execute(self, action: str, **kwargs) -> PluginResult:
        """
        Execute git action.
        
        Args:
            action: Git action (init, status, add, commit, log, etc.)
            **kwargs: Action-specific parameters
            
        Returns:
            PluginResult with operation outcome
        """
        actions = {
            "init": self._git_init,
            "status": self._git_status,
            "add": self._git_add,
            "commit": self._git_commit,
            "log": self._git_log,
            "diff": self._git_diff,
            "branch": self._git_branch,
            "checkout": self._git_checkout,
            "clone": self._git_clone,
            "push": self._git_push,
            "pull": self._git_pull,
            "fetch": self._git_fetch,
            "remote": self._git_remote
        }
        
        if action not in actions:
            return PluginResult(
                success=False,
                error=f"Unknown git action: {action}"
            )
        
        try:
            return actions[action](**kwargs)
        except Exception as e:
            return PluginResult(
                success=False,
                error=f"Git {action} failed: {str(e)}"
            )
    
    def _git_init(self, **kwargs) -> PluginResult:
        """Initialize git repository."""
        try:
            result = subprocess.run(
                ["git", "init"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return PluginResult(
                    success=True,
                    output=f"✅ Initialized git repository at {self.repo_path}"
                )
            else:
                return PluginResult(
                    success=False,
                    error=result.stderr
                )
        except Exception as e:
            return PluginResult(
                success=False,
                error=f"Failed to initialize repository: {str(e)}"
            )
    
    def _git_status(self, **kwargs) -> PluginResult:
        """Get repository status."""
        try:
            # Check if git repo exists
            if not (self.repo_path / ".git").exists():
                return PluginResult(
                    success=False,
                    error="Not a git repository. Run 'git init' first."
                )
            
            # Get status
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            # Parse status
            state = self._parse_status(result.stdout)
            
            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            state["branch"] = branch_result.stdout.strip() or "main"
            
            # Format output
            output = self._format_status(state)
            
            return PluginResult(
                success=True,
                output=output,
                data=state
            )
        except Exception as e:
            return PluginResult(
                success=False,
                error=f"Failed to get status: {str(e)}"
            )
    
    def _parse_status(self, status_output: str) -> Dict[str, List[str]]:
        """Parse git status --porcelain output."""
        staged = []
        unstaged = []
        untracked = []
        
        for line in status_output.split('\n'):
            if not line:
                continue
            
            status_code = line[:2]
            filename = line[3:]
            
            if status_code[0] in ['A', 'M', 'D', 'R', 'C']:
                staged.append(filename)
            if status_code[1] in ['M', 'D']:
                unstaged.append(filename)
            if status_code == '??':
                untracked.append(filename)
        
        return {
            "staged": staged,
            "unstaged": unstaged,
            "untracked": untracked
        }
    
    def _format_status(self, state: Dict) -> str:
        """Format status for display."""
        lines = []
        lines.append(f"📍 Branch: {state.get('branch', 'unknown')}")
        
        if state["staged"]:
            lines.append(f"\n✅ Staged files ({len(state['staged'])}):")
            for f in state["staged"]:
                lines.append(f"  + {f}")
        
        if state["unstaged"]:
            lines.append(f"\n⚠️ Unstaged changes ({len(state['unstaged'])}):")
            for f in state["unstaged"]:
                lines.append(f"  M {f}")
        
        if state["untracked"]:
            lines.append(f"\n❓ Untracked files ({len(state['untracked'])}):")
            for f in state["untracked"][:5]:  # Limit to 5
                lines.append(f"  ? {f}")
            if len(state["untracked"]) > 5:
                lines.append(f"  ... and {len(state['untracked']) - 5} more")
        
        if not (state["staged"] or state["unstaged"] or state["untracked"]):
            lines.append("\n✨ Working tree clean")
        
        return "\n".join(lines)
    
    def _git_add(self, files: str = ".", **kwargs) -> PluginResult:
        """Stage files for commit."""
        try:
            result = subprocess.run(
                ["git", "add", files],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return PluginResult(
                    success=True,
                    output=f"✅ Staged: {files}"
                )
            else:
                return PluginResult(
                    success=False,
                    error=result.stderr
                )
        except Exception as e:
            return PluginResult(
                success=False,
                error=f"Failed to stage files: {str(e)}"
            )
    
    def _git_commit(self, message: str, **kwargs) -> PluginResult:
        """Create commit with message."""
        if not message:
            return PluginResult(
                success=False,
                error="Commit message is required"
            )
        
        try:
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Extract commit hash
                hash_result = subprocess.run(
                    ["git", "rev-parse", "--short", "HEAD"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                commit_hash = hash_result.stdout.strip()
                
                return PluginResult(
                    success=True,
                    output=f"✅ Commit created: {commit_hash}\n{message}",
                    data={"commit_hash": commit_hash}
                )
            else:
                return PluginResult(
                    success=False,
                    error=result.stderr
                )
        except Exception as e:
            return PluginResult(
                success=False,
                error=f"Failed to commit: {str(e)}"
            )
    
    def _git_log(self, count: int = 5, **kwargs) -> PluginResult:
        """View commit history."""
        try:
            result = subprocess.run(
                ["git", "log", f"-{count}", "--oneline", "--decorate"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                if result.stdout.strip():
                    output = f"📜 Recent commits:\n{result.stdout}"
                else:
                    output = "No commits yet"
                
                return PluginResult(
                    success=True,
                    output=output
                )
            else:
                return PluginResult(
                    success=False,
                    error=result.stderr
                )
        except Exception as e:
            return PluginResult(
                success=False,
                error=f"Failed to get log: {str(e)}"
            )
    
    def _git_diff(self, **kwargs) -> PluginResult:
        """Show diff of unstaged changes."""
        try:
            result = subprocess.run(
                ["git", "diff"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                output = f"📝 Changes:\n{result.stdout[:1000]}"  # Limit output
                if len(result.stdout) > 1000:
                    output += "\n... (truncated)"
            else:
                output = "No changes to show"
            
            return PluginResult(
                success=True,
                output=output,
                data={"diff": result.stdout}
            )
        except Exception as e:
            return PluginResult(
                success=False,
                error=f"Failed to get diff: {str(e)}"
            )
    
    def _git_branch(self, name: str = None, **kwargs) -> PluginResult:
        """List or create branches."""
        try:
            if name:
                # Create branch
                result = subprocess.run(
                    ["git", "branch", name],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    return PluginResult(
                        success=True,
                        output=f"✅ Created branch: {name}"
                    )
                else:
                    return PluginResult(
                        success=False,
                        error=result.stderr
                    )
            else:
                # List branches
                result = subprocess.run(
                    ["git", "branch"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                
                return PluginResult(
                    success=True,
                    output=f"🌿 Branches:\n{result.stdout}"
                )
        except Exception as e:
            return PluginResult(
                success=False,
                error=f"Failed to manage branches: {str(e)}"
            )
    
    def _git_checkout(self, branch: str, create: bool = False, **kwargs) -> PluginResult:
        """Switch branches."""
        try:
            cmd = ["git", "checkout"]
            if create:
                cmd.append("-b")
            cmd.append(branch)
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                action = "Created and switched to" if create else "Switched to"
                return PluginResult(
                    success=True,
                    output=f"✅ {action} branch: {branch}"
                )
            else:
                return PluginResult(
                    success=False,
                    error=result.stderr
                )
        except Exception as e:
            return PluginResult(
                success=False,
                error=f"Failed to checkout: {str(e)}"
            )
    
    def _git_clone(self, url: str, directory: str = None, **kwargs) -> PluginResult:
        """Clone remote repository."""
        if not url:
            return PluginResult(
                success=False,
                error="Repository URL is required"
            )
        
        try:
            target = directory or self.workspace_path
            
            result = subprocess.run(
                ["git", "clone", url, str(target)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout for large repos
            )
            
            if result.returncode == 0:
                # Update repo path if cloned to workspace
                if not directory:
                    self.repo_path = Path(target)
                
                return PluginResult(
                    success=True,
                    output=f"✅ Cloned repository from {url}"
                )
            else:
                return PluginResult(
                    success=False,
                    error=result.stderr
                )
        except subprocess.TimeoutExpired:
            return PluginResult(
                success=False,
                error="Clone operation timed out (>5 minutes)"
            )
        except Exception as e:
            return PluginResult(
                success=False,
                error=f"Failed to clone: {str(e)}"
            )
    
    def _git_push(self, remote: str = "origin", branch: str = None, **kwargs) -> PluginResult:
        """Push commits to remote."""
        try:
            # Get current branch if not specified
            if not branch:
                branch_result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                branch = branch_result.stdout.strip()
            
            if not branch:
                return PluginResult(
                    success=False,
                    error="No branch specified and could not detect current branch"
                )
            
            result = subprocess.run(
                ["git", "push", remote, branch],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return PluginResult(
                    success=True,
                    output=f"✅ Pushed to {remote}/{branch}\n{result.stdout}"
                )
            else:
                return PluginResult(
                    success=False,
                    error=result.stderr
                )
        except subprocess.TimeoutExpired:
            return PluginResult(
                success=False,
                error="Push operation timed out (>5 minutes)"
            )
        except Exception as e:
            return PluginResult(
                success=False,
                error=f"Failed to push: {str(e)}"
            )
    
    def _git_pull(self, remote: str = "origin", branch: str = None, **kwargs) -> PluginResult:
        """Pull changes from remote."""
        try:
            # Get current branch if not specified
            if not branch:
                branch_result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                branch = branch_result.stdout.strip()
            
            if not branch:
                return PluginResult(
                    success=False,
                    error="No branch specified and could not detect current branch"
                )
            
            result = subprocess.run(
                ["git", "pull", remote, branch],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return PluginResult(
                    success=True,
                    output=f"✅ Pulled from {remote}/{branch}\n{result.stdout}"
                )
            else:
                return PluginResult(
                    success=False,
                    error=result.stderr
                )
        except subprocess.TimeoutExpired:
            return PluginResult(
                success=False,
                error="Pull operation timed out (>5 minutes)"
            )
        except Exception as e:
            return PluginResult(
                success=False,
                error=f"Failed to pull: {str(e)}"
            )
    
    def _git_fetch(self, remote: str = "origin", **kwargs) -> PluginResult:
        """Fetch updates from remote."""
        try:
            result = subprocess.run(
                ["git", "fetch", remote],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return PluginResult(
                    success=True,
                    output=f"✅ Fetched from {remote}\n{result.stdout or 'Up to date'}"
                )
            else:
                return PluginResult(
                    success=False,
                    error=result.stderr
                )
        except subprocess.TimeoutExpired:
            return PluginResult(
                success=False,
                error="Fetch operation timed out (>5 minutes)"
            )
        except Exception as e:
            return PluginResult(
                success=False,
                error=f"Failed to fetch: {str(e)}"
            )
    
    def _git_remote(self, action: str = "list", name: str = None, url: str = None, **kwargs) -> PluginResult:
        """Manage remote repositories."""
        try:
            if action == "list":
                # List remotes
                result = subprocess.run(
                    ["git", "remote", "-v"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                
                if result.stdout.strip():
                    output = f"🌐 Remotes:\n{result.stdout}"
                else:
                    output = "No remotes configured"
                
                return PluginResult(
                    success=True,
                    output=output
                )
            
            elif action == "add":
                # Add remote
                if not name or not url:
                    return PluginResult(
                        success=False,
                        error="Both 'name' and 'url' are required to add remote"
                    )
                
                result = subprocess.run(
                    ["git", "remote", "add", name, url],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    return PluginResult(
                        success=True,
                        output=f"✅ Added remote '{name}': {url}"
                    )
                else:
                    return PluginResult(
                        success=False,
                        error=result.stderr
                    )
            
            elif action == "remove":
                # Remove remote
                if not name:
                    return PluginResult(
                        success=False,
                        error="Remote 'name' is required to remove"
                    )
                
                result = subprocess.run(
                    ["git", "remote", "remove", name],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    return PluginResult(
                        success=True,
                        output=f"✅ Removed remote: {name}"
                    )
                else:
                    return PluginResult(
                        success=False,
                        error=result.stderr
                    )
            
            else:
                return PluginResult(
                    success=False,
                    error=f"Unknown remote action: {action}. Use 'list', 'add', or 'remove'"
                )
        
        except Exception as e:
            return PluginResult(
                success=False,
                error=f"Failed to manage remotes: {str(e)}"
            )
    
    def validate_input(self, **kwargs) -> tuple[bool, str]:
        """Validate git operation input."""
        action = kwargs.get("action")
        
        if not action:
            return False, "Parameter 'action' is required"
        
        # Validate commit message
        if action == "commit" and not kwargs.get("message"):
            return False, "Commit message is required"
        
        # Validate checkout
        if action == "checkout" and not kwargs.get("branch"):
            return False, "Branch name is required for checkout"
        
        return True, ""
    
    def describe(self) -> Dict[str, Any]:
        return {
            "name": "git",
            "description": "Git version control operations for repository management",
            "parameters": {
                "action": "Git action (init, status, add, commit, log, diff, branch, checkout, clone, push, pull, fetch, remote)",
                "message": "Commit message (for commit action)",
                "files": "Files to stage (for add action, default: '.')",
                "count": "Number of commits to show (for log action, default: 5)",
                "branch": "Branch name (for branch/checkout/push/pull actions)",
                "create": "Create new branch (for checkout action)",
                "url": "Repository URL (for clone/remote actions)",
                "remote": "Remote name (for push/pull/fetch actions, default: 'origin')",
                "directory": "Target directory (for clone action)"
            },
            "examples": [
                "Initialize repository: action='init'",
                "Check status: action='status'",
                "Stage all files: action='add', files='.'",
                "Commit changes: action='commit', message='feat: add feature'",
                "View history: action='log', count=10",
                "Show changes: action='diff'",
                "Create branch: action='branch', name='feature/new'",
                "Switch branch: action='checkout', branch='main'",
                "Clone repository: action='clone', url='https://github.com/user/repo'",
                "Push to remote: action='push', remote='origin', branch='main'",
                "Pull from remote: action='pull', remote='origin', branch='main'",
                "Fetch updates: action='fetch', remote='origin'",
                "List remotes: action='remote'",
                "Add remote: action='remote', action='add', name='origin', url='https://...'"
            ]
        }


# Test the plugin
if __name__ == "__main__":
    import tempfile
    import shutil
    
    # Create temp workspace
    workspace = tempfile.mkdtemp()
    
    try:
        plugin = GitPlugin()
        plugin.initialize(workspace)
        
        print("=== Git Plugin Test ===\n")
        
        # Test 1: Initialize
        print("Test 1: Initialize repository")
        result = plugin.execute("init")
        print(f"Success: {result.success}")
        print(f"Output: {result.output}\n")
        
        # Test 2: Status (empty repo)
        print("Test 2: Status (empty)")
        result = plugin.execute("status")
        print(f"Success: {result.success}")
        print(f"Output:\n{result.output}\n")
        
        # Test 3: Create file and check status
        print("Test 3: Create file and check status")
        (Path(workspace) / "test.txt").write_text("Hello Git!")
        result = plugin.execute("status")
        print(f"Output:\n{result.output}\n")
        
        # Test 4: Stage files
        print("Test 4: Stage files")
        result = plugin.execute("add", files=".")
        print(f"Success: {result.success}")
        print(f"Output: {result.output}\n")
        
        # Test 5: Commit
        print("Test 5: Commit")
        result = plugin.execute("commit", message="feat: initial commit")
        print(f"Success: {result.success}")
        print(f"Output: {result.output}\n")
        
        # Test 6: Log
        print("Test 6: View log")
        result = plugin.execute("log")
        print(f"Success: {result.success}")
        print(f"Output:\n{result.output}\n")
        
    finally:
        # Cleanup
        shutil.rmtree(workspace)
        print("Workspace cleaned up")
