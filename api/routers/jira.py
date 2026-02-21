"""
JIRA Integration Router
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import base64
import requests

from ..config import get_settings

router = APIRouter(prefix="/jira", tags=["jira"])

settings = get_settings()


class JIRACredentials(BaseModel):
    email: str
    token: str


def get_jira_credentials() -> JIRACredentials:
    """Get JIRA credentials from settings"""
    if not settings.jira_email or not settings.jira_api_token:
        raise HTTPException(
            status_code=500,
            detail="JIRA credentials not configured. Set JIRA_EMAIL and JIRA_API_TOKEN in .env"
        )
    return JIRACredentials(
        email=settings.jira_email,
        token=settings.jira_api_token
    )


def jira_headers(creds: JIRACredentials) -> dict:
    """Create JIRA authentication headers"""
    auth_str = f"{creds.email}:{creds.token}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    return {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/json"
    }


@router.post("/search")
async def search_jira_issues(
    jql: str,
    credentials: JIRACredentials,
    fields: str = "summary,description,status,labels,assignee,updated,issuelinks",
    max_results: int = 20
):
    """
    Search JIRA issues with JQL
    """
    url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
    params = {
        "jql": jql,
        "maxResults": max_results,
        "fields": fields
    }
    
    try:
        resp = requests.get(
            url,
            headers=jira_headers(credentials),
            params=params,
            timeout=30
        )
        resp.raise_for_status()
        return resp.json().get("issues", [])
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"JIRA API error: {str(e)}")


@router.get("/status")
async def get_jira_status():
    """
    Check if JIRA credentials are configured
    """
    return {
        "configured": bool(settings.jira_email and settings.jira_api_token),
        "jira_base_url": settings.jira_base_url,
        "jira_email": settings.jira_email if settings.jira_email else None
    }


@router.get("/projects")
async def get_jira_projects():
    """
    Get all JIRA projects accessible to the user
    Uses credentials from environment variables
    """
    creds = get_jira_credentials()
    url = f"{settings.jira_base_url}/rest/api/3/project"
    
    try:
        resp = requests.get(
            url,
            headers=jira_headers(creds),
            timeout=30
        )
        resp.raise_for_status()
        projects = resp.json()
        
        # Return simplified project list
        return [
            {
                "key": p["key"],
                "name": p["name"],
                "id": p["id"]
            }
            for p in projects
        ]
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"JIRA API error: {str(e)}")


@router.get("/tasks")
async def get_jira_tasks(
    project_key: str,
    doc_type: Optional[str] = None
):
    """
    Get tasks from a JIRA project
    Filters for tasks that have Google Doc links
    Uses credentials from environment variables
    """
    creds = get_jira_credentials()
    
    # Build JQL based on doc_type
    # Note: We filter out completed tasks in code (lines 168-171) since JIRA JQL label negation is complex
    if doc_type == "ba":
        jql = f'project = {project_key} AND status NOT IN (Cancelled,Done) AND created >= startOfYear() ORDER BY updated DESC'
    elif doc_type == "tc":
        # TC tasks have component = Test
        jql = f'project = {project_key} AND component = Test AND status NOT IN (Cancelled,Done) AND created >= startOfYear() ORDER BY updated DESC'
    else:
        jql = f'project = {project_key} AND status NOT IN (Cancelled,Done) ORDER BY updated DESC'

    url = f"{settings.jira_base_url}/rest/api/3/search/jql"
    params = {
        "jql": jql,
        "maxResults": 50,
        "fields": "summary,description,status,labels,assignee,updated,issuelinks"  # Added issuelinks for TC
    }
    
    try:
        resp = requests.get(
            url,
            headers=jira_headers(creds),
            params=params,
            timeout=30
        )
        resp.raise_for_status()
        issues = resp.json().get("issues", [])
        
        # Filter and extract doc links
        tasks = []
        for issue in issues:
            fields = issue.get("fields", {})
            desc = fields.get("description", "")
            labels = fields.get("labels", [])
            
            # Skip test/dummy tasks (only for BA, not for TC since TC tasks ARE test tasks)
            summary = fields.get("summary", "")
            if doc_type == "ba" and ("test" in labels or "test-task" in labels or "TEST TEST" in summary or summary.endswith("(Test)")):
                continue

            # Skip already completed tasks
            if doc_type == "ba" and ("qa-tamamlandi" in labels or "qa-devam-ediyor" in labels):
                continue
            if doc_type == "tc" and ("tc-qa-tamamlandi" in labels or "tc-qa-devam-ediyor" in labels):
                continue
            
            # Extract Google Doc/Sheets ID (prefer Sheets for TC, Docs for BA)
            prefer_sheets = (doc_type == "tc")
            doc_id, doc_url = extract_doc_id_from_desc(desc, prefer_sheets=prefer_sheets)

            if doc_id:
                task_data = {
                    "key": issue["key"],
                    "summary": summary,
                    "assignee": (fields.get("assignee") or {}).get("displayName", ""),
                    "doc_id": doc_id,
                    "doc_url": doc_url,
                    "status": fields.get("status", {}).get("name", ""),
                    "labels": labels
                }

                # For TC tasks, extract linked BA
                if doc_type == "tc":
                    linked_ba = find_linked_ba_key(issue)
                    task_data["linked_ba_key"] = linked_ba if linked_ba else None

                tasks.append(task_data)
        
        return tasks
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"JIRA API error: {str(e)}")


@router.get("/tasks/{task_key}/document")
async def get_task_document(task_key: str):
    """
    Get the Google Doc linked to a JIRA task
    Uses credentials from environment variables
    """
    creds = get_jira_credentials()

    # Get task details
    url = f"{settings.jira_base_url}/rest/api/3/issue/{task_key}"
    params = {"fields": "description"}
    
    try:
        resp = requests.get(
            url,
            headers=jira_headers(creds),
            params=params,
            timeout=30
        )
        resp.raise_for_status()
        issue = resp.json()
        
        desc = issue.get("fields", {}).get("description", "")
        doc_id, doc_url = extract_doc_id_from_desc(desc)
        
        if not doc_id:
            raise HTTPException(status_code=404, detail="No Google Doc link found in task description")
        
        return {
            "doc_id": doc_id,
            "doc_url": doc_url
        }
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"JIRA API error: {str(e)}")


def extract_doc_id_from_desc(description: str, prefer_sheets: bool = False) -> tuple[str, str]:
    """
    Extract Google Doc/Sheets ID from JIRA description
    Returns: (doc_id, doc_url)

    Args:
        description: JIRA description field
        prefer_sheets: If True, look for Sheets first (for TC tasks), else Docs first (for BA tasks)
    """
    import re

    if not description:
        return "", ""

    # Convert description to plain text (it's in Atlassian Document Format)
    # For simplicity, we'll search the raw JSON string
    desc_str = str(description)

    # Define pattern sets
    sheets_patterns = [
        r'docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]+)',
    ]

    docs_patterns = [
        r'docs\.google\.com/document/d/([a-zA-Z0-9_-]+)',
        r'https://docs\.google\.com/.*?/d/([a-zA-Z0-9_-]+)'
    ]

    # Try patterns based on preference
    pattern_order = [sheets_patterns, docs_patterns] if prefer_sheets else [docs_patterns, sheets_patterns]

    for pattern_set in pattern_order:
        for pattern in pattern_set:
            match = re.search(pattern, desc_str)
            if match:
                doc_id = match.group(1)
                # Determine if it's a sheet or doc based on pattern
                if 'spreadsheet' in pattern:
                    doc_url = f"https://docs.google.com/spreadsheets/d/{doc_id}/edit"
                else:
                    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
                return doc_id, doc_url

    return "", ""


def find_linked_ba_key(issue: dict) -> str:
    """
    Extract linked BA task key from issue links
    Returns the first linked issue key found
    """
    issuelinks = issue.get("fields", {}).get("issuelinks", [])
    for link in issuelinks:
        # Check both inward and outward links
        inward = link.get("inwardIssue", {})
        outward = link.get("outwardIssue", {})
        for linked in [inward, outward]:
            key = linked.get("key", "")
            if key:
                return key
    return ""
