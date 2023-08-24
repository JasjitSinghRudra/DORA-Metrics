import requests


def has_pull_request(ticket_number):

    jira_token = "MTMxNzAyNTE3MTk5OvrAB8eGzMcnB+mJ+cwuqzIfylGW"  # Jasjit Token
    # "OTk1NDQ0NzgzMTI3Oiy3PADJLC2RExY+hq/CLgIFoy9t"  # Mukul Token
    JIRA_HEADERS = {
        "Accept": "application/json",
        "Authorization": f"Bearer {jira_token}"
    }

    url = 'https://jira.xxx.com/rest/api/latest/issue/{}'.format(ticket_number)
    response = requests.get(
        url,
        headers=JIRA_HEADERS,
        params={
            'expand': 'changelog'
        }
    )
    if response.status_code == 200:
        data = response.json()
        issue_id = data['id']
    else:
        print('Error: failed to get Jira issue ID for {}. Status code: {}'.format(ticket_number, response.status_code))
        return "No issue ID"

    api_url = f"https://jira.xxx.com/rest/dev-status/1.0/issue/detail?issueId={issue_id}&applicationType=stash&dataType=pullrequest"
    response = requests.get(api_url, headers=JIRA_HEADERS)
    data = response.json()
    if str(data["detail"][0]['pullRequests']) == '[]':
        return False
    else:
        return True

