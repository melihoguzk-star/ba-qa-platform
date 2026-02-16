"""
Google Drive Client - Direct API access with token from n8n webhook

Similar to BA/TC evaluation flow:
1. Get OAuth token from n8n webhook
2. Use token to make direct Google Drive API calls
3. Download document content
"""
import requests
from typing import Dict, Optional, Tuple


class GoogleDriveClient:
    """Client for accessing Google Drive with OAuth token from n8n"""

    def __init__(self, n8n_docs_webhook: str, n8n_sheets_webhook: str):
        """
        Initialize Google Drive client with n8n webhook URLs

        Args:
            n8n_docs_webhook: n8n webhook URL for Google Docs token
            n8n_sheets_webhook: n8n webhook URL for Google Sheets token
        """
        self.docs_webhook = n8n_docs_webhook
        self.sheets_webhook = n8n_sheets_webhook

    def get_oauth_token(self, webhook_url: str) -> str:
        """
        Get OAuth access token from n8n webhook

        Args:
            webhook_url: n8n webhook URL that returns OAuth token

        Returns:
            OAuth access token

        Raises:
            Exception: If token retrieval fails
        """
        try:
            response = requests.post(
                webhook_url,
                json={},
                timeout=10
            )
            response.raise_for_status()
            result = response.json()

            # Expected response: {"token": "ya29.a0AfH6..."}
            token = result.get('token') or result.get('access_token')
            if not token:
                raise ValueError(f"No token in response: {result}")

            return token

        except requests.RequestException as e:
            raise Exception(f"Failed to get OAuth token from n8n: {str(e)}")

    def download_google_doc(self, document_id: str, export_format: str = 'text/plain') -> str:
        """
        Download a Google Doc using OAuth token

        Args:
            document_id: Google Docs document ID
            export_format: Export MIME type (default: text/plain)
                Options: text/plain, text/html, application/pdf

        Returns:
            Document content as text

        Raises:
            Exception: If download fails
        """
        # Get token from n8n
        token = self.get_oauth_token(self.docs_webhook)

        # Use Google Docs API to export document
        export_url = f"https://docs.google.com/document/d/{document_id}/export"

        try:
            response = requests.get(
                export_url,
                headers={
                    'Authorization': f'Bearer {token}',
                },
                params={
                    'format': export_format.split('/')[-1]  # 'plain', 'html', 'pdf'
                },
                timeout=30
            )
            response.raise_for_status()

            # Check if we got HTML error page
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' in content_type and export_format != 'text/html':
                raise Exception(
                    "Received HTML instead of document content. "
                    "Check document permissions and OAuth scopes."
                )

            return response.text

        except requests.RequestException as e:
            raise Exception(f"Failed to download Google Doc: {str(e)}")

    def download_google_sheet(self, spreadsheet_id: str, sheet_name: Optional[str] = None) -> Dict:
        """
        Download a Google Sheet using OAuth token

        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            sheet_name: Optional sheet name (default: first sheet)

        Returns:
            Sheet data as dictionary with values

        Raises:
            Exception: If download fails
        """
        # Get token from n8n
        token = self.get_oauth_token(self.sheets_webhook)

        # Use Google Sheets API
        base_url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}"

        try:
            # Get spreadsheet metadata to find sheet names
            metadata_response = requests.get(
                base_url,
                headers={'Authorization': f'Bearer {token}'},
                params={'fields': 'sheets.properties.title'},
                timeout=10
            )
            metadata_response.raise_for_status()
            metadata = metadata_response.json()

            # Get first sheet name if not specified
            if not sheet_name:
                sheets = metadata.get('sheets', [])
                if not sheets:
                    raise ValueError("No sheets found in spreadsheet")
                sheet_name = sheets[0]['properties']['title']

            # Get sheet values
            values_url = f"{base_url}/values/{sheet_name}"
            values_response = requests.get(
                values_url,
                headers={'Authorization': f'Bearer {token}'},
                timeout=30
            )
            values_response.raise_for_status()
            values_data = values_response.json()

            return {
                'spreadsheet_id': spreadsheet_id,
                'sheet_name': sheet_name,
                'values': values_data.get('values', []),
                'range': values_data.get('range', '')
            }

        except requests.RequestException as e:
            raise Exception(f"Failed to download Google Sheet: {str(e)}")

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
            sheet_data = self.download_google_sheet(doc_id)

            # Convert sheet to text format
            values = sheet_data['values']
            text_lines = []
            for row in values:
                text_lines.append('\t'.join(str(cell) for cell in row))
            content = '\n'.join(text_lines)

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
