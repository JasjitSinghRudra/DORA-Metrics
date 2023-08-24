"""
Author: Jasjit Rudra
Date: 17 May 2023
Description: Time that passes for a committed code to reach production.
"""

import requests
import json
import commit_id
import pr_check
from datetime import datetime
import matplotlib.pyplot as plt

jira_server = "https://jira.xxx.com"
jira_url = "https://jira.xxx.com/rest/api/3/issue/"
jira_token = "YOUR JIRA TOKEN HERE"


JIRA_HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {jira_token}"
}

BITBUCKET_TOKEN = "YOUR BITBUCKET TOKEN HERE"
BITBUCKET_SERVER = "https://git-bitbucket.aws.com:8443"
BITBUCKET_HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {BITBUCKET_TOKEN}"
}


# Obtain repository name and pull request (used same API for both)
def get_repo_pull_request_id(project_key):
    response = requests.get(
        url=f"{jira_server}/rest/dev-status/1.0/issue/detail?issueId={commit_id.get_issue_id(project_key)}&applicationType=stash&dataType=pullrequest",
        headers=JIRA_HEADERS,
        params={
            'expand': 'changelog'
        }
    )
    data_commit_id = response.json()
    repo_pr = [data_commit_id['detail'][0]['pullRequests'][0]['source']['repository']['name'],
               data_commit_id['detail'][0]['pullRequests'][0]['id'].replace("#", "")]
    return repo_pr


def lead_change_time(project_id, repo_name, pr_id):
    merged_timestamp = 0
    opened_timestamp = 0
    pull_request_url = f'https://git-bitbucket.aws.com:8443/projects/{project_id}/repos/{repo_name}/pull-requests/{pr_id}'
    response = requests.get(pull_request_url, headers=BITBUCKET_HEADERS)

    if response.status_code == 200:
        pull_request_info = response.json()
        opened_timestamp = pull_request_info['createdDate']
        activities_url = pull_request_info['links']['self'][0]['href'] + '/activities'
        activities_response = requests.get(activities_url, headers=BITBUCKET_HEADERS)

        if activities_response.status_code == 200:
            activities_info = activities_response.json()
            activities = activities_info['values']

            for activity in activities:
                if activity['action'] == 'MERGED':
                    merged_timestamp = activity['createdDate']
                    break
            milliseconds = merged_timestamp - opened_timestamp
            days = milliseconds / (1000 * 60 * 60 * 24)
            print("Lead time for changes= ", round(days, 2), "days")
            return round(days, 2)
        else:
            print("Error occurred while retrieving activities information.")
            return None
    else:
        print("Error occurred while retrieving pull request information.", response.status_code)
        return None


def cycle_time_lead(jira_project, start_date, end_date):
    jql_query = f"(issuetype = Bug OR issuetype = Defect OR issuetype = Task) AND status in (Accepted, Completed, Closed, Verified) AND resolved >= '{start_date}' AND resolved <= '{end_date}' and project = '{jira_project}'"
    response = requests.get(
        url=f"{jira_server}/rest/api/latest/search",
        headers=JIRA_HEADERS,
        params={
            'jql': jql_query,
            'expand': 'changelog'
        }
    )

    response_json = json.loads(response.text)
    issues = response_json["issues"]
    if not issues:
        return "There are no tickets resolved within the given time frame"

    x_axis = []
    y_axis = []
    for issue in reversed(issues):
        print(issue['key'])
        if pr_check.has_pull_request(issue['key']):
            y_axis.append(lead_change_time(jira_project, get_repo_pull_request_id(issue['key'])[0]
                                           , get_repo_pull_request_id(issue['key'])[1]))
            created_date_str = issue["fields"]["created"]
            created_date = datetime.strptime(created_date_str[:19], "%Y-%m-%dT%H:%M:%S")
            x_axis.append(f"{created_date.month}/{created_date.day}")

    if len(y_axis) != 0:
        print(y_axis)
        plt.switch_backend('Agg')
        plt.bar(x_axis, y_axis, color='green', width=0.4)
        plt.title(f"Lead time for Changes = {round(sum(y_axis) / len(y_axis),2)} days")
        plt.xlabel("Timeline (of issues)", fontsize=10)
        plt.ylabel("Number of Days", fontsize=10)
        plt.rc('axes', labelsize=5)
        plt.savefig(fname='static/images/lead_time_for_changes.png')
        return round(sum(y_axis) / len(y_axis),2)

    else:
        plt.plot(0, 0)
        plt.title("No changes were found in given timeframe")
        plt.savefig(fname='static/images/lead_time_for_changes.png')
        return "No changes were found in given timeframe"