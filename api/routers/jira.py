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
    if doc_type == "ba":
        jql = f'project = {project_key} AND labels != qa-tamamlandi AND labels != qa-devam-ediyor AND status NOT IN (Cancelled,Done) AND created >= startOfYear() ORDER BY updated DESC'
    elif doc_type == "tc":
        jql = f'project = {project_key} AND labels != tc-qa-tamamlandi AND labels != tc-qa-devam-ediyor AND status NOT IN (Cancelled,Done) AND created >= startOfYear() ORDER BY updated DESC'
    else:
        jql = f'project = {project_key} AND status NOT IN (Cancelled,Done) ORDER BY updated DESC'

    url = f"{settings.jira_base_url}/rest/api/3/search/jql"
    params = {
        "jql": jql,
        "maxResults": 50,
        "fields": "summary,description,status,labels,assignee,updated"
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
            
            # Skip test tasks
            summary = fields.get("summary", "")
            if "test" in labels or "TEST TEST" in summary or summary.endswith("(Test)"):
                continue
                
            # Skip already completed tasks
            if doc_type == "ba" and ("qa-tamamlandi" in labels or "qa-devam-ediyor" in labels):
                continue
            if doc_type == "tc" and ("tc-qa-tamamlandi" in labels or "tc-qa-devam-ediyor" in labels):
                continue
            
            # Extract Google Doc ID
            doc_id, doc_url = extract_doc_id_from_desc(desc)
            
            if doc_id:
                tasks.append({
                    "key": issue["key"],
                    "summary": summary,
                    "assignee": (fields.get("assignee") or {}).get("displayName", ""),
                    "doc_id": doc_id,
                    "doc_url": doc_url,
                    "status": fields.get("status", {}).get("name", ""),
                    "labels": labels
                })
        
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


def extract_doc_id_from_desc(description: str) -> tuple[str, str]:
    """
    Extract Google Doc ID from JIRA description
    Returns: (doc_id, doc_url)
    """
    import re
    
    if not description:
        return "", ""
    
    # Convert description to plain text (it's in Atlassian Document Format)
    # For simplicity, we'll search the raw JSON string
    desc_str = str(description)
    
    # Look for Google Docs URL patterns
    patterns = [
        r'docs\.google\.com/document/d/([a-zA-Z0-9_-]+)',
        r'https://docs\.google\.com/.*?/d/([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, desc_str)
        if match:
            doc_id = match.group(1)
            doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
            return doc_id, doc_url
    
    return "", ""
