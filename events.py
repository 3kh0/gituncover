import requests
from colorama import Fore

def l1(username, pages=5):
    events = []
    for page in range(1, pages + 1):
        url = f"https://api.github.com/users/{username}/events/public?per_page=100&page={page}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            page_events = response.json()
            if not page_events:
                break
            events.extend(page_events)
        except requests.exceptions.HTTPError as e:
            if response.status_code == 422: 
                print(Fore.RED + f"warning: api rejected the request on page {page}, results may be limited.")
                break
            else:
                raise e
    return events

def l2(events, max_commits=5):
    email_data = {}
    truncated = {}

    for event in events:
        if event['type'] == "PushEvent":
            repo_name = event['repo']['name']
            commits = event['payload'].get('commits', [])
            for commit in commits:
                email = commit['author'].get('email')
                commit_hash = commit['sha']
                commit_url = commit['url']
                is_merge = "[merge]" if "Merge" in commit.get('message', '') else ""
                if email:
                    if email not in email_data:
                        email_data[email] = []
                    email_data[email].append({
                        "repo": repo_name,
                        "hash": commit_hash,
                        "url": commit_url,
                        "is_merge": is_merge
                    })

    for email in email_data:
        repo_commits = {}
        truncated[email] = {}
        for commit in email_data[email]:
            repo = commit['repo']
            if repo not in repo_commits:
                repo_commits[repo] = []
            repo_commits[repo].append(commit)

        for repo, commits in repo_commits.items():
            if len(commits) > max_commits:
                truncated[email][repo] = len(commits) - max_commits
            repo_commits[repo] = commits[:max_commits]

        email_data[email] = [commit for commits in repo_commits.values() for commit in commits]

    return email_data, truncated