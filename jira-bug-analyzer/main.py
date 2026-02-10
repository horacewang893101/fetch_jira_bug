import argparse
import os
from typing import List

import requests
import pandas as pd

try:
    from config import settings
except ImportError:
    from .config import settings

def fetch_bug_data(url, auth):
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        raise Exception(f"Failed to fetch data from {url}: {response.status_code}")

def analyze_bugs(bug_data):
    # Example analysis: Count the number of bugs by status
    status_counts = {}
    for bug in bug_data:
        status = bug.get('fields', {}).get('status', {}).get('name', 'Unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    return status_counts

def write_bug_to_md(bug, output_dir):
    bug_id = bug.get('key', 'Unknown')
    fields = bug.get('fields', {})
    title = fields.get('summary', 'No title')
    description = fields.get('description', 'No description')
    status = fields.get('status', {})
    status_name = status.get('name', 'Unknown') if status else 'Unknown'
    assignee = fields.get('assignee', {})
    assignee_name = assignee.get('displayName', 'Unassigned') if assignee else 'Unassigned'
    
    md_content = f"# {bug_id}: {title}\n\n**Status:** {status_name}\n\n**Assignee:** {assignee_name}\n\n**Description:**\n{description}\n"
    
    filename = f"{bug_id}.md"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w') as f:
        f.write(md_content)
    print(f"Written {filename}")

def load_issue_keys(file_path: str) -> List[str]:
    """Load issue keys from a text file, one per line."""
    issue_keys: List[str] = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            key = line.strip()
            if not key or key.startswith('#'):
                continue
            issue_keys.append(key)
    return issue_keys


def main(issue_keys: List[str], output_dir: str):
    # Configure authentication from .env
    email = settings.JIRA_EMAIL
    token = settings.JIRA_TOKEN
    auth = (email, token)
    
    os.makedirs(output_dir, exist_ok=True)
    
    all_bugs = []
    for issue_key in issue_keys:
        api_url = f"{settings.JIRA_DOMAIN}/rest/api/2/issue/{issue_key}"
        try:
            bug_data = fetch_bug_data(api_url, auth)
            all_bugs.append(bug_data)
            write_bug_to_md(bug_data, output_dir)
        except Exception as e:
            print(f"Could not process {issue_key}: {e}")

    if all_bugs:
        analysis_results = analyze_bugs(all_bugs)
        print("\nBug Status Summary:")
        for status, count in analysis_results.items():
            print(f"{status}: {count}")
    else:
        print("\nNo bug data processed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch Jira bugs and write markdown files")
    parser.add_argument("--issue-file", required=True, help="Path to a file containing issue keys")
    parser.add_argument("--output-dir", default="bugs_md", help="Directory to write bug markdown files")
    args = parser.parse_args()

    issue_keys = load_issue_keys(args.issue_file)
    if not issue_keys:
        raise SystemExit("No issue keys found in the provided file.")

    main(issue_keys, args.output_dir)