"""
Google Drive Client - n8n webhook proxy for Google Drive access

Uses n8n webhooks (same as BA/TC evaluation):
1. Call n8n webhook with document ID
2. n8n handles OAuth and downloads document
3. Returns document content directly
"""
import requests
from typing import Dict, Optional, Tuple


class GoogleDriveClient:
    """Client for accessing Google Drive via n8n webhook proxy"""

    def __init__(self, n8n_docs_webhook: str, n8n_sheets_webhook: str):
        """
        Initialize Google Drive client with n8n webhook URLs

        Args:
            n8n_docs_webhook: n8n webhook URL for Google Docs proxy
            n8n_sheets_webhook: n8n webhook URL for Google Sheets proxy
        """
        self.docs_webhook = n8n_docs_webhook
        self.sheets_webhook = n8n_sheets_webhook

    def fetch_document_content(self, webhook_url: str, doc_id: str) -> str:
        """
        Fetch document content via n8n webhook proxy

        Args:
            webhook_url: n8n webhook URL
            doc_id: Google document ID

        Returns:
            Document content as text

        Raises:
            Exception: If fetch fails
        """
        try:
            response = requests.get(
                webhook_url,
                params={"doc_id": doc_id},
                timeout=120
            )
            response.raise_for_status()
            return response.text
            if not token:
                raise Exception(f"Webhook request failed: {response.status_code} - {response.text}")

        except requests.RequestException as e:
            raise Exception(f"Failed to fetch document from n8n webhook: {str(e)}")

    def download_google_doc(self, document_id: str) -> str:
        """
        Download a Google Doc via n8n webhook proxy

        Args:
            document_id: Google Docs document ID

        Returns:
            Document content as text

        Raises:
            Exception: If download fails
        """
        return self.fetch_document_content(self.docs_webhook, document_id)

    def download_google_sheet(self, spreadsheet_id: str) -> str:
        """
        Download a Google Sheet via n8n webhook proxy

        Args:
            spreadsheet_id: Google Sheets spreadsheet ID

        Returns:
            Sheet content as text

        Raises:
            Exception: If download fails
        """
        return self.fetch_document_content(self.sheets_webhook, spreadsheet_id)

    def read_document_from_url(self, url: str, doc_type: str = 'auto') -> Tuple[str, str]:
        """
        Read document from Google Drive URL (Docs or Sheets)

        Args:
            url: Google Docs or Sheets URL
            doc_type: 'auto', 'docs', or 'sheets'

        Returns:
            Tuple of (content, document_type)

        Raises:
            Exception: If read fails
        """
        from pipeline.document_reader import extract_google_drive_file_id

        # Extract document ID
        doc_id = extract_google_drive_file_id(url)
        if not doc_id:
            raise ValueError(f"Could not extract document ID from URL: {url}")

        # Auto-detect document type from URL
        if doc_type == 'auto':
            if 'docs.google.com/document' in url:
                doc_type = 'docs'
            elif 'docs.google.com/spreadsheets' in url:
                doc_type = 'sheets'
            else:
                # Try docs first
                doc_type = 'docs'

        # Download based on type
        if doc_type == 'docs':
            content = self.download_google_doc(doc_id)
            return content, 'docs'
        elif doc_type == 'sheets':
            content = self.download_google_sheet(doc_id)
            return content, 'sheets'
        else:
            raise ValueError(f"Unknown document type: {doc_type}")


def create_client_from_env() -> GoogleDriveClient:
    """
    Create GoogleDriveClient from environment variables

    Environment variables:
        N8N_GOOGLE_DOCS_WEBHOOK: Webhook URL for Google Docs token
        N8N_GOOGLE_SHEETS_WEBHOOK: Webhook URL for Google Sheets token

    Returns:
        Configured GoogleDriveClient

    Raises:
        ValueError: If required environment variables are not set
    """
    import os

    docs_webhook = os.environ.get('N8N_GOOGLE_DOCS_WEBHOOK')
    sheets_webhook = os.environ.get('N8N_GOOGLE_SHEETS_WEBHOOK')

    if not docs_webhook:
        raise ValueError("N8N_GOOGLE_DOCS_WEBHOOK environment variable not set")
    if not sheets_webhook:
        raise ValueError("N8N_GOOGLE_SHEETS_WEBHOOK environment variable not set")

    return GoogleDriveClient(docs_webhook, sheets_webhook)
