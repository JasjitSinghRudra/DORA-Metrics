import requests
import rollback
import change_failover_rate
import pr_check

jira_server = "https://jira.xxx.com"
jira_url = "https://jira.xxx.com/rest/api/3/issue/"
jira_token = "YOUR JIRA TOKEN HERE"

JIRA_HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {jira_token}"
}


def get_issue_id(jira_key):
    if pr_check.has_pull_request(jira_key):
        url = 'https://jira.xxx.com/rest/api/latest/issue/{}'.format(jira_key)
        response = requests.get(
            url,
            headers=JIRA_HEADERS,
            params={
                'expand': 'changelog'
            }
        )

        if response.status_code == 200:
            data_get_id = response.json()
            issue_id = data_get_id['id']

            print('Jira issue ID for {}: {}'.format(jira_key, issue_id))
            return issue_id
        else:
            print('Error: failed to get Jira issue ID for {}. Status code: {}'.format(jira_key, response.status_code))
            return None


def commit_id(jira_key):
    response = requests.get(
        url=f"{jira_server}/rest/dev-status/1.0/issue/detail?issueId={get_issue_id(jira_key)}&applicationType=stash&dataType=repository",
        headers=JIRA_HEADERS,
        params={
            'expand': 'changelog'
        }
    )
    data = response.json()

    print("Repository: ",
          data["detail"][0]["repositories"][0]["name"])  # I think should be iterated if repositories are >1
    print("Commit ID: ", data["detail"][0]["repositories"][0]["commits"][0]["id"])
    print("Author Timestamp: ", data["detail"][0]["repositories"][0]["commits"][0]["authorTimestamp"])
    print("Is request merged: ", data["detail"][0]["repositories"][0]["commits"][0]["merge"])
    print("Author Name: ", data["detail"][0]["repositories"][0]["commits"][0]["author"]["name"])

    url = data["detail"][0]["repositories"][0]["url"]
    parts = url.split('/')
    index_projects = parts.index('projects')
    index_repos = parts.index('repos')
    project_id = parts[index_projects + 1:index_repos][0]
    print("PROJECT ID:", project_id)

    if (data["detail"][0]["repositories"][0]["commits"][0]["merge"]):
        response = requests.get(
            url=f"{jira_server}/rest/dev-status/1.0/issue/summary?issueId={get_issue_id(jira_key)}",
            headers=JIRA_HEADERS,
            params={
                'expand': 'changelog'
            }
        )
        data2 = response.json()
        print("Total number of PRs", data2['summary']['pullrequest']['overall']['count'])
        if data2['summary']['pullrequest']['overall']['count']:
            return change_failover_rate.change_failure(
                rollback.find_rollbacks(data["detail"][0]["repositories"][0]["commits"][0]["id"],
                                        data["detail"][0]["repositories"][0]["name"], project_id),
                int(data2['summary']['pullrequest']['overall']['count']))
        else:
            print('No PR found for ticket')
            return "None"
    else:
        print(f"Cannot calculate change failover rate for ticket {jira_key} as no PR is attached to it.")
        return "None"
