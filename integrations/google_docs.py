"""
BA&QA Intelligence Platform — Google Docs & Sheets Integration
n8n webhook proxy ve doğrudan export desteği
"""
import re
import requests
import logging

logger = logging.getLogger(__name__)

N8N_DOCS_PROXY = "https://sh0tdie.app.n8n.cloud/webhook/google-docs-proxy"
N8N_SHEETS_PROXY = "https://sh0tdie.app.n8n.cloud/webhook/google-sheets-proxy"


# ─────────────────────────────────────────────
# n8n PROXY (QA Agent Team tarafından kullanılır)
# ─────────────────────────────────────────────

def fetch_google_doc_via_proxy(doc_id: str) -> str:
    """n8n webhook proxy üzerinden Google Docs çeker"""
    resp = requests.get(N8N_DOCS_PROXY, params={"doc_id": doc_id}, timeout=120)
    resp.raise_for_status()
    return resp.text


def fetch_google_sheets_as_text(spreadsheet_id: str) -> str:
    """n8n webhook proxy üzerinden Google Sheets çeker"""
    resp = requests.get(N8N_SHEETS_PROXY, params={"spreadsheet_id": spreadsheet_id}, timeout=120)
    resp.raise_for_status()
    return resp.text


# ─────────────────────────────────────────────
# DIRECT EXPORT (Design Compliance tarafından kullanılır)
# ─────────────────────────────────────────────

def extract_google_doc_id(url: str) -> str | None:
    patterns = [
        r'/document/d/([a-zA-Z0-9_-]+)',
        r'docs\.google\.com/d/([a-zA-Z0-9_-]+)',
        r'^([a-zA-Z0-9_-]{20,})$',
    ]
    for pattern in patterns:
        match = re.search(pattern, url.strip())
        if match:
            return match.group(1)
    return None


def fetch_google_doc_direct(url: str) -> str | None:
    """Google Docs'u doğrudan export endpoint ile çeker (public paylaşım gerekli)"""
    doc_id = extract_google_doc_id(url)
    if not doc_id:
        return None
    export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
    try:
        resp = requests.get(export_url, timeout=30)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        return resp.text
    except Exception as e:
        logger.error(f"Google Docs fetch error: {e}")
        return None


# ─────────────────────────────────────────────
# URL PARSERS (JIRA description'dan link çıkarma)
# ─────────────────────────────────────────────

def extract_urls_from_adf(node) -> list:
    """Atlassian Document Format'tan tüm URL'leri çıkarır"""
    urls = []
    if not node:
        return urls
    if isinstance(node, str):
        return re.findall(r"https?://[^\s\"'<>]+", node)
    if isinstance(node, dict):
        if node.get("type") in ("inlineCard", "blockCard") and node.get("attrs", {}).get("url"):
            urls.append(node["attrs"]["url"])
        for mark in node.get("marks", []):
            if mark.get("type") == "link" and mark.get("attrs", {}).get("href"):
                urls.append(mark["attrs"]["href"])
        if node.get("text"):
            urls.extend(re.findall(r"https?://[^\s\"'<>]+", node["text"]))
        for child in node.get("content", []):
            urls.extend(extract_urls_from_adf(child))
    return urls


def extract_doc_id(description) -> tuple:
    """JIRA description'dan Google Docs/Drive ID çıkarır"""
    urls = extract_urls_from_adf(description)
    for url in urls:
        m = re.search(r"docs\.google\.com/document/d/([a-zA-Z0-9_-]+)", url)
        if m:
            return m.group(1), url
        m = re.search(r"docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]+)", url)
        if m:
            return m.group(1), url
        m = re.search(r"drive\.google\.com/file/d/([a-zA-Z0-9_-]+)", url)
        if m:
            return m.group(1), url
    return None, None


def extract_spreadsheet_id(description) -> tuple:
    """JIRA description'dan Google Spreadsheet ID çıkarır"""
    urls = extract_urls_from_adf(description)
    for url in urls:
        m = re.search(r"docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]+)", url)
        if m:
            return m.group(1), url
    return None, None


def find_linked_ba_key(issue: dict) -> str | None:
    """Issue links'ten BA task key'ini bulur"""
    for link in issue.get("fields", {}).get("issuelinks", []):
        inward = link.get("inwardIssue", {})
        outward = link.get("outwardIssue", {})
        for linked in [inward, outward]:
            key = linked.get("key", "")
            if key:
                return key
    return None
