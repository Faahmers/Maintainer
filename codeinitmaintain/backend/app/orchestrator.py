import subprocess
import os
import shutil
import requests
from dotenv import load_dotenv

CLONE_DIR = "repo"
BRANCH = "ai-update"

load_dotenv()
GITHUB_TOKEN = os.environ.get("GITHUB_TOK")
USERNAME = os.environ.get("GITHUB_USER")


# ------------------ subprocess with LIVE logs ------------------

def run(cmd, cwd=None, log_callback=None):
    process = subprocess.Popen(
        cmd,
        shell=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    output_lines = []

    for line in process.stdout:
        line = line.rstrip()
        output_lines.append(line)

        if log_callback:
            log_callback(line)  # 🔴 live log push

    process.wait()

    if process.returncode != 0:
        raise RuntimeError("\n".join(output_lines))

    return "\n".join(output_lines)


# ------------------ helpers ------------------

def normalize_repo(raw: str) -> str:
    raw = raw.strip()
    if not raw.startswith("http"):
        raw = f"https://{raw}"
    return raw


# ------------------ git operations ------------------

def fork_repo(upstream_repo: str):
    api_url = upstream_repo.replace(
        "https://github.com/", "https://api.github.com/repos/"
    )

    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    resp = requests.post(f"{api_url}/forks", headers=headers)

    if resp.status_code not in (202, 422):
        resp.raise_for_status()


def clone_repo(upstream_repo: str, log):
    if os.path.exists(CLONE_DIR):
        shutil.rmtree(CLONE_DIR)

    repo_name = upstream_repo.rstrip("/").split("/")[-1]
    fork_url = f"https://{GITHUB_TOKEN}@github.com/{USERNAME}/{repo_name}.git"

    run(f"git clone {fork_url} {CLONE_DIR}", log_callback=log)


def sync_fork(upstream_repo: str, log):
    try:
        run(f"git remote add upstream {upstream_repo}", cwd=CLONE_DIR, log_callback=log)
    except Exception:
        pass

    run("git fetch upstream", cwd=CLONE_DIR, log_callback=log)
    run("git checkout main", cwd=CLONE_DIR, log_callback=log)
    run("git merge upstream/main", cwd=CLONE_DIR, log_callback=log)
    run("git push origin main", cwd=CLONE_DIR, log_callback=log)


def checkout_branch(log):
    try:
        run(f"git checkout -b {BRANCH}", cwd=CLONE_DIR, log_callback=log)
    except Exception:
        run(f"git checkout {BRANCH}", cwd=CLONE_DIR, log_callback=log)


# ------------------ docker ------------------

def run_docker(log):
    abs_path = os.path.abspath(CLONE_DIR)
    run("docker build -t ai-sandbox .", log_callback=log)
    run(f"docker run --rm -v {abs_path}:/agent/repo ai-sandbox", log_callback=log)


# ------------------ commit & PR ------------------

def commit_and_push(log):
    run("git add .", cwd=CLONE_DIR, log_callback=log)

    try:
        run('git commit -m "AI Maintainer update"', cwd=CLONE_DIR, log_callback=log)
    except Exception:
        return False

    run(f"git push origin {BRANCH} --force", cwd=CLONE_DIR, log_callback=log)
    return True


def create_pr(upstream_repo: str):
    parts = upstream_repo.rstrip("/").split("/")
    upstream_owner, repo_name = parts[-2], parts[-1]

    api_url = f"https://api.github.com/repos/{upstream_owner}/{repo_name}/pulls"

    data = {
        "title": "AI Maintainer Update",
        "body": "Automated fixes and repository evolution by AI Agent.",
        "head": f"{USERNAME}:{BRANCH}",
        "base": "main",
    }

    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    resp = requests.post(api_url, json=data, headers=headers)

    if resp.status_code == 201:
        return {"message": "PR created successfully", "url": resp.json().get("html_url")}

    if resp.status_code == 422:
        list_url = f"{api_url}?head={USERNAME}:{BRANCH}&state=open"
        existing = requests.get(list_url, headers=headers)
        existing.raise_for_status()
        prs = existing.json()

        if prs:
            return {
                "message": "PR already exists but was force-updated",
                "url": prs[0].get("html_url"),
            }

        return {"message": "PR exists but URL not found", "url": None}

    resp.raise_for_status()


# ================== MAIN ENTRY ==================

def run_maintainer(repo_url: str, log_callback=None) -> dict:
    logs = []

    def push(line):
        logs.append(line)
        if log_callback:
            log_callback(line)

    try:
        upstream_repo = normalize_repo(repo_url)
        push(f"Normalized repo: {upstream_repo}")

        fork_repo(upstream_repo)
        push("Fork step completed")

        clone_repo(upstream_repo, push)
        push("Clone completed")

        sync_fork(upstream_repo, push)
        push("Sync completed")

        checkout_branch(push)
        push("Branch ready")

        run_docker(push)
        push("Docker execution finished")

        changed = commit_and_push(push)
        push("Commit & push done" if changed else "No changes to commit")

        pr_info = create_pr(upstream_repo)
        push(f"PR result: {pr_info}")

        return {
            "status": "completed",
            "pr_url": pr_info.get("url"),
            "message": pr_info.get("message"),
            "logs": "\n".join(logs),
        }

    except Exception as e:
        push(f"ERROR: {str(e)}")
        return {"status": "error", "pr_url": None, "message": str(e), "logs": "\n".join(logs)}
