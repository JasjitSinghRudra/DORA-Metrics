"""
Author: Jasjit Rudra
Date: 03 May 2023
Description: (Mean Time to Recover) Time it takes for a service to bounce back from failure.
Note: JQL Query can be edited to find any ticket (not just bugfixes) details.
"""

import json
import requests
from datetime import datetime
import matplotlib.pyplot as plt

jira_server = "https://jira.xxx.com"
jira_url = "https://jira.xxx.com/rest/api/3/issue/"
jira_token = "YOUR JIRA TOKEN HERE"

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {jira_token}"
}


def cycle_time(jira_project, start_date, end_date):
    jql_query = f"(issuetype = Bug OR issuetype = Defect) AND status in (Accepted, Completed, Closed, Verified) AND resolved >= '{start_date}' AND resolved <= '{end_date}' and project = '{jira_project}'"
    response = requests.get(
        url=f"{jira_server}/rest/api/latest/search",
        headers=headers,
        params={
            'jql': jql_query,
            'expand': 'changelog'
        }
    )

    response_json = json.loads(response.text)
    issues = response_json["issues"]
    if not issues:
        return "There are no bugs resolved within the given time frame"

    total_time = 0
    x_axis = []
    y_axis = []
    for issue in reversed(issues):
        created_date_str = issue["fields"]["created"]
        resolved_date_str = issue["fields"]["resolutiondate"]

        created_date = datetime.strptime(created_date_str[:19], "%Y-%m-%dT%H:%M:%S")
        x_axis.append(f"{created_date.month} / {created_date.day}")
        resolved_date = datetime.strptime(resolved_date_str[:19], "%Y-%m-%dT%H:%M:%S")
        diff_days = (resolved_date - created_date).days
        y_axis.append(diff_days)
        print(f"Issue {issue['key']} resolved in {diff_days} days.")
        total_time += diff_days

    # Calculate the average time taken to resolve an issue
    num_issues = len(issues)
    if num_issues > 0:
        avg_time = total_time / num_issues
        plt.switch_backend('Agg')
        plt.plot(x_axis, y_axis)
        plt.title(f"Mean time to Recover = {round(avg_time)} days")
        plt.xlabel("Timeline (of issues discovered)", fontsize=10)
        plt.ylabel("Days Taken to Resolve", fontsize=10)
        plt.rc('axes', labelsize=5)

        plt.savefig(fname='static/images/mean_time_to_recover.png')
        print(f"Average time to resolve an issue: {avg_time} days.")
        return f"Average time taken to resolve defect: {avg_time} days"
