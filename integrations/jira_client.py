"""
BA&QA Intelligence Platform — JIRA Integration
"""
import base64
import requests

JIRA_BASE_URL = "https://loodos.atlassian.net"


def jira_headers(email: str, token: str) -> dict:
    cred = base64.b64encode(f"{email}:{token}".encode()).decode()
    return {"Authorization": f"Basic {cred}", "Content-Type": "application/json"}


def jira_search(email: str, token: str, jql: str,
                fields: str = "summary,description,status,labels,assignee,updated,issuelinks",
                max_results: int = 20) -> list:
    url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
    params = {"jql": jql, "maxResults": max_results, "fields": fields}
    resp = requests.get(url, headers=jira_headers(email, token), params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("issues", [])


def jira_get_issue(email: str, token: str, key: str, fields: str = "description") -> dict:
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{key}"
    params = {"fields": fields}
    resp = requests.get(url, headers=jira_headers(email, token), params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def jira_add_label(email: str, token: str, key: str, label: str):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{key}"
    body = {"update": {"labels": [{"add": label}]}}
    resp = requests.put(url, headers=jira_headers(email, token), json=body, timeout=10)
    return resp.status_code


def jira_update_labels(email: str, token: str, key: str, remove_labels: list, add_labels: list):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{key}"
    ops = [{"remove": l} for l in remove_labels] + [{"add": l} for l in add_labels]
    body = {"update": {"labels": ops}}
    resp = requests.put(url, headers=jira_headers(email, token), json=body, timeout=10)
    return resp.status_code


def jira_add_comment(email: str, token: str, key: str, text: str):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{key}/comment"
    body = {
        "body": {
            "type": "doc", "version": 1,
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": text}]}]
        }
    }
    resp = requests.post(url, headers=jira_headers(email, token), json=body, timeout=30)
    return resp.status_code
