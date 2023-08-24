import json
import requests
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime

JIRA_SERVER = "https://jira.xxx.com"
jira_url = "https://jira.xxx.com/rest/api/3/issue/"
JIRA_TOKEN = "YOUR JIRA TOKEN HERE"

STATE = "Completed"  # The state is where Pull Request is raised

JIRA_HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {JIRA_TOKEN}"
}

TOTAL_PULL_REQUEST = []


def deployment_freq(project_key, start_date, end_date):
    jira_tickets = get_jira_issues_within_date(project_key, start_date, end_date)

    all_pull_request = []

    for ticket in jira_tickets:
        pull_request = get_pull_requests(ticket['id'])
        for pr in pull_request:
            all_pull_request.append(pr)

    if len(all_pull_request) != 0:
        newlist = sorted(all_pull_request, key=lambda d: d['lastUpdate'])
        all_pull_request = newlist
        dates = [datetime.strptime(d["lastUpdate"], "%Y-%m-%dT%H:%M:%S.%f%z").date() for d in all_pull_request]
        date_freq = Counter(dates)
        x_values, y_values = zip(*date_freq.items())

        plt.switch_backend('Agg')
        plt.plot(x_values, y_values, marker='o', color='gold')
        plt.xlabel('Date')
        plt.ylabel('Frequency')
        plt.title('Deployment Frequency')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(fname='static/images/deployment_frequency.png')

        return len(all_pull_request)
    else:
        plt.switch_backend('Agg')
        plt.plot(0, 0)
        plt.title("No deployment was done in given timeframe")
        plt.savefig(fname='static/images/deployment_frequency.png')
        return "Cannot determine Deployment Frequency as no deployment was ever done in given timeframe"


def get_jira_issues_within_date(jira_project_key, since_date, until_date):
    print(since_date)
    print(until_date)
    response = requests.get(
        url=f"{JIRA_SERVER}/rest/api/latest/search",
        headers=JIRA_HEADERS,
        params={
            'jql': 'project="{}" and status CHANGED TO {} DURING ("{}","{}") ORDER BY createdDate asc'.format(
                jira_project_key, STATE, since_date, until_date),
            'fields': 'key',
            'maxResults': 1000
        }
    )
    data = json.loads(response.text)
    return data['issues']


def get_pull_requests(issue_id):
    attached_pull_request_url = 'https://jira.xxx.com/rest/dev-status/latest/issue/detail?issueId=' + issue_id + '&applicationType=stash&dataType=pullrequest'
    get_attached_pull_requests = requests.get(attached_pull_request_url, headers=JIRA_HEADERS)
    get_attached_pull_requests = json.loads(get_attached_pull_requests.text)
    if not get_attached_pull_requests['detail'][0]['pullRequests']:
        return []

    pull_request_list = []

    for pull_request in get_attached_pull_requests['detail'][0]['pullRequests']:
        if pull_request['status'] == "MERGED":
            pull_request_list.append(pull_request)
    return pull_request_list
