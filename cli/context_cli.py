import requests
import sys

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
    """Display commits with related workflow status."""
    print(f"\nContext Timeline for: {repo}\n{'-'*60}")
    commits = get_recent_commits(repo)
    workflows = get_workflow_status(repo)

    if not commits:
        print("No commits found.")
        return

    for c in commits:
        sha = c["sha"]
        date = c["date"]
        author = c["author"]
        msg = c["message"]
        status = workflows.get(sha, "NO_WORKFLOW")
        print(f"[{date}] {author} - {msg} ({sha}) [{status}]")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cli/context_cli.py <owner/repo>")
        sys.exit(1)
    repo = sys.argv[1]
    show_context(repo)
