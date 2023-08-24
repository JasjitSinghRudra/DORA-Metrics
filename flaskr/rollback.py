import requests

BITBUCKET_TOKEN = "YOUR BITBUCKET TOKEN"
BITBUCKET_SERVER = "https://git-bitbucket.aws.com:8443"
BITBUCKET_HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {BITBUCKET_TOKEN}"
}


def find_rollbacks(commit_id, repo_name, project_id):
    url = f'{BITBUCKET_SERVER}/rest/api/latest/projects/{project_id}/repos/{repo_name}/commits/{commit_id}/changes'
    response = requests.get(url, headers=BITBUCKET_HEADERS)

    if response.status_code == 200:
        data = response.json()
        num_rollbacks = 0
        for change in data['values']:
            if change['type'] == 'REVERT':
                num_rollbacks += 1
        return int(num_rollbacks)
    else:
        return None

