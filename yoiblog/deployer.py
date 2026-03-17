"""GitHub Pages deployment for YoiBlog.

Supports two authentication methods:
1. HTTPS + Personal Access Token (recommended)
2. SSH Key

Uses a standalone temporary git repo for deployment, so the blog
directory itself does NOT need to be a git repository.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .config import Config
from .generator import generate


class DeployError(Exception):
    """Raised when deployment fails."""
    pass


def deploy(config: Config, message: str | None = None, skip_generate: bool = False) -> str:
    """Deploy the site to GitHub Pages.

    Returns a log string of what happened.
    """
    log_lines: list[str] = []

    def log(msg: str) -> None:
        log_lines.append(msg)
        print(msg)

    # Validate config
    _validate_deploy_config(config)

    # Generate first
    if not skip_generate:
        log("📦 Generating site...")
        generate(config, quiet=True)
        log("✅ Site generated")

    if not config.public_dir.exists() or not any(config.public_dir.iterdir()):
        raise DeployError("public/ directory is empty. Generation may have failed.")

    branch = config.deploy.branch
    if message is None:
        message = "Deploy site"

    remote_url = _build_remote_url(config)
    env = _build_git_env(config)

    log(f"🚀 Deploying to {_safe_repo_display(config)} (branch: {branch})...")

    # Write CNAME if configured
    if config.deploy.cname:
        (config.public_dir / "CNAME").write_text(config.deploy.cname, encoding="utf-8")

    # Deploy via a temporary git repo
    _push_directory(config.public_dir, remote_url, branch, message, env)

    log("✅ Deploy complete!")
    if config.site.url:
        log(f"🌐 Site: {config.site.url}")

    return "\n".join(log_lines)


def test_connection(config: Config) -> str:
    """Test git connectivity without actually deploying.

    Returns a success message or raises DeployError.
    """
    _validate_deploy_config(config)

    remote_url = _build_remote_url(config)
    env = _build_git_env(config)

    try:
        result = subprocess.run(
            ["git", "ls-remote", "--heads", remote_url],
            capture_output=True, text=True, env=env, timeout=30,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()
            if "Permission denied" in stderr or "publickey" in stderr:
                method = config.deploy.auth_method
                if method == "ssh":
                    raise DeployError(f"SSH authentication failed. Check your SSH key.\n{stderr}")
                else:
                    raise DeployError(f"Token authentication failed. Check your GitHub token.\n{stderr}")
            if "not found" in stderr.lower() or "not exist" in stderr.lower():
                raise DeployError(
                    f"Repository not found. It will be created on first deploy if you have permission.\n{stderr}"
                )
            raise DeployError(f"Cannot connect to repository:\n{stderr}")

        return "✅ Connection successful! Repository is accessible."

    except subprocess.TimeoutExpired:
        raise DeployError("Connection timed out. Check your network and repository URL.")
    except FileNotFoundError:
        raise DeployError("Git is not installed. Please install Git first.")


def _validate_deploy_config(config: Config) -> None:
    """Validate deploy configuration, raise DeployError if invalid."""
    if not config.deploy.repo:
        raise DeployError(
            "No deploy repo configured.\n"
            "Set deploy.repo in _config.yml or WebUI Settings."
        )

    method = config.deploy.auth_method

    if method == "token" and not config.deploy.github_token:
        raise DeployError(
            "GitHub token not configured.\n"
            "Go to Settings → Deploy Settings to set your Personal Access Token."
        )

    if method == "ssh" and config.deploy.ssh_key_path:
        key_path = Path(config.deploy.ssh_key_path)
        if not key_path.exists():
            raise DeployError(f"SSH key not found at: {key_path}")


def _push_directory(
    source_dir: Path,
    remote_url: str,
    branch: str,
    message: str,
    env: dict,
) -> None:
    """Create a temporary git repo from source_dir contents and force-push to remote/branch.

    This is completely independent of any existing git repo — the blog
    directory does NOT need to be a git repository.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # 1. Copy all public files into the temp directory
        for item in source_dir.iterdir():
            dest = tmp / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

        # 2. Init a fresh git repo
        _run_git(["init"], cwd=tmp, env=env)
        _run_git(["checkout", "--orphan", branch], cwd=tmp, env=env)

        # 3. Stage everything
        _run_git(["add", "-A"], cwd=tmp, env=env)

        # 4. Commit
        _run_git(
            ["commit", "-m", message, "--author", "YoiBlog <yoiblog@deploy>"],
            cwd=tmp, env=env,
        )

        # 5. Force-push to remote
        result = subprocess.run(
            ["git", "push", "--force", remote_url, f"HEAD:{branch}"],
            cwd=tmp, env=env,
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()
            if "Permission denied" in stderr or "publickey" in stderr:
                raise DeployError(f"Authentication failed during push:\n{stderr}")
            if "could not read" in stderr.lower() or "fatal" in stderr.lower():
                raise DeployError(f"Push failed:\n{stderr}")
            raise DeployError(f"Push failed (exit {result.returncode}):\n{stderr}")


def _run_git(args: list[str], cwd: Path, env: dict) -> subprocess.CompletedProcess:
    """Run a git command, raising DeployError on failure."""
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd, env=env,
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise DeployError(f"git {' '.join(args)} failed:\n{result.stderr.strip()}")
    return result


def _build_remote_url(config: Config) -> str:
    """Build the git remote URL with embedded credentials if using token auth."""
    repo = config.deploy.repo

    if config.deploy.auth_method == "token" and config.deploy.github_token:
        token = config.deploy.github_token
        # Normalize to HTTPS with token
        if repo.startswith("git@github.com:"):
            path = repo.replace("git@github.com:", "")
            return f"https://x-access-token:{token}@github.com/{path}"
        elif repo.startswith("https://github.com/"):
            path = repo.replace("https://github.com/", "")
            return f"https://x-access-token:{token}@github.com/{path}"
        elif "github.com" in repo:
            path = repo.split("github.com")[-1].lstrip(":/")
            return f"https://x-access-token:{token}@github.com/{path}"
        else:
            return repo
    else:
        return repo


def _safe_repo_display(config: Config) -> str:
    """Return a display-safe version of the repo URL (no tokens)."""
    return config.deploy.repo or "(not configured)"


def _build_git_env(config: Config) -> dict:
    """Build environment variables for git commands."""
    env = os.environ.copy()

    if config.deploy.auth_method == "ssh" and config.deploy.ssh_key_path:
        key_path = config.deploy.ssh_key_path
        env["GIT_SSH_COMMAND"] = f'ssh -i "{key_path}" -o StrictHostKeyChecking=accept-new'

    return env
