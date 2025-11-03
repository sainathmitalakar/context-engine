import requests
import sys
from core.memory import load_memory, save_memory


def get_recent_commits(repo, limit=5):
    """Fetch recent commits from a GitHub repository."""
    url = f"https://api.github.com/repos/{repo}/commits"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch commits:", response.status_code)
        return []
    commits = response.json()
    return [
        {
            "sha": c["sha"][:7],
            "author": c["commit"]["author"]["name"],
            "message": c["commit"]["message"].split("\n")[0],
            "date": c["commit"]["author"]["date"]
        }
        for c in commits[:limit]
    ]

def get_workflow_status(repo):
    """Fetch recent GitHub Actions runs and map head sha -> conclusion."""
    url = f"https://api.github.com/repos/{repo}/actions/runs?per_page=10"
    response = requests.get(url)
    if response.status_code != 200:
        # do not fail the whole program for missing workflows
        return {}
    runs = response.json().get("workflow_runs", [])
    return {run["head_sha"][:7]: (run.get("conclusion") or "IN_PROGRESS") for run in runs}

def show_context(repo):
    print(f"\nContext Timeline for: {repo}\n{'-'*60}")
    commits = get_recent_commits(repo)
    workflows = get_workflow_status(repo)

    memory = load_memory()
    new_data = {}

    for c in commits:
        sha = c["sha"]
        date = c["date"]
        author = c["author"]
        msg = c["message"]
        status = workflows.get(sha, "NO_WORKFLOW")
        print(f"[{date}] {author} - {msg} ({sha}) [{status}]")
        new_data[sha] = {"author": author, "message": msg, "status": status}

    added, updated = detect_changes(memory, new_data)

    if added or updated:
        print("\nChanges since last check:")
        for sha in added:
            print(f" + New commit: {new_data[sha]['message']} ({sha})")
        for sha in updated:
            print(f" * Updated workflow: {new_data[sha]['message']} ({sha}) [{new_data[sha]['status']}]")
        save_memory(new_data)
    else:
        print("\nNo new changes. Everything is up-to-date.")
