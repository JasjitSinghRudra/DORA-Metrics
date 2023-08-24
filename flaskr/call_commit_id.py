import commit_id
import json
import requests
import pr_check
from datetime import datetime
import matplotlib.pyplot as plt


def cycle_time_failover(jira_project, start_date, end_date):
    jira_server = "https://jira.xxx.com"
    jira_token = "YOUR JIRA TOKEN HERE"

    JIRA_HEADERS = {
        "Accept": "application/json",
        "Authorization": f"Bearer {jira_token}"
    }
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
        if pr_check.has_pull_request(issue['key']):
            print(commit_id.commit_id(issue['key']))
            y_axis.append(commit_id.commit_id(issue['key']))
            created_date_str = issue["fields"]["created"]
            created_date = datetime.strptime(created_date_str[:19], "%Y-%m-%dT%H:%M:%S")
            x_axis.append(f"{created_date.month}/{created_date.day}")

    print(y_axis)
    print(x_axis)
    length_y = len(y_axis)
    for i in range(0, length_y-1):
        if y_axis[i] == "None":
            y_axis.pop(i)
            x_axis.pop(i)

    if len(y_axis) != 0:
        print(y_axis)
        print(x_axis)
        plt.switch_backend('Agg')
        plt.plot(x_axis, y_axis, color='red')
        plt.title(f"Change Failover Rate = {round(sum(y_axis)/len(y_axis),2)}")
        plt.xlabel("Timeline (of issues discovered)", fontsize=10)
        plt.ylabel("Days", fontsize=10)
        plt.rc('axes', labelsize=5)
        plt.savefig(fname='static/images/change_failover_rate.png')

        return round(sum(y_axis)/len(y_axis),2)

    else:
        plt.plot(0, 0)
        plt.title("No Commits were found in given timespan")
        plt.savefig(fname='static/images/change_failover_rate.png')
        return "No Commits were found in given timespan"
