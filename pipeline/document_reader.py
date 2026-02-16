"""
Document Reader - Extract text from Word documents and Google Drive
"""
import io
import re
import tempfile
from typing import Optional, Tuple
import requests


def read_docx(file_content: bytes) -> str:
    """
    Extract text from a Word (.docx) document

    Args:
        file_content: Binary content of the .docx file

    Returns:
        Extracted text with structure preserved
    """
    try:
        from docx import Document
    except ImportError:
        raise ImportError("python-docx library is required. Install with: pip install python-docx")

    # Load document from bytes
    doc = Document(io.BytesIO(file_content))

    # Extract text with structure
    text_parts = []

    for paragraph in doc.paragraphs:
        # Preserve heading structure
        style = paragraph.style.name.lower()
        text = paragraph.text.strip()

        if not text:
            text_parts.append("")  # Preserve empty lines
            continue

        # Detect heading levels
        if 'heading 1' in style or 'title' in style:
            text_parts.append(f"# {text}")
        elif 'heading 2' in style:
            text_parts.append(f"## {text}")
        elif 'heading 3' in style:
            text_parts.append(f"### {text}")
        else:
            # Regular paragraph
            text_parts.append(text)

    return "\n".join(text_parts)


def extract_google_drive_file_id(url: str) -> Optional[str]:
    """
    Extract file ID from Google Drive URL

    Supports formats:
    - https://drive.google.com/file/d/FILE_ID/view
    - https://drive.google.com/open?id=FILE_ID
    - https://docs.google.com/document/d/FILE_ID/edit
    - https://docs.google.com/spreadsheets/d/FILE_ID/edit

    Args:
        url: Google Drive or Google Docs URL

    Returns:
        File ID or None if not found
    """
    # Pattern 1: /d/FILE_ID/ (most common)
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)

    # Pattern 2: ?id=FILE_ID
    match = re.search(r'[?&]id=([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)

    return None


def download_from_google_drive(url: str) -> Tuple[bytes, str]:
    """
    Download document from Google Drive

    Args:
        url: Google Drive share link (must be publicly accessible or "Anyone with link")

    Returns:
        Tuple of (file_content, mime_type)

    Raises:
        ValueError: If URL is invalid or file ID cannot be extracted
        requests.RequestException: If download fails
    """
    # Extract file ID
    file_id = extract_google_drive_file_id(url)
    if not file_id:
        raise ValueError("Could not extract file ID from Google Drive URL. "
                        "Make sure it's a valid Google Drive share link.")

    # Try to download directly (works for publicly shared files)
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    try:
        response = requests.get(download_url, timeout=30)
        response.raise_for_status()

        # Check if we got a download confirmation page (for large files)
        if 'download_warning' in response.text or 'virus scan warning' in response.text.lower():
            # Extract confirm token
            confirm_match = re.search(r'confirm=([0-9A-Za-z_-]+)', response.text)
            if confirm_match:
                confirm = confirm_match.group(1)
                download_url = f"https://drive.google.com/uc?export=download&confirm={confirm}&id={file_id}"
                response = requests.get(download_url, timeout=30)
                response.raise_for_status()

        # Detect content type
        content_type = response.headers.get('content-type', 'application/octet-stream')

        # Check if we actually got file content (not HTML error page)
        if 'text/html' in content_type.lower() and len(response.content) < 10000:
            # Likely an error page or permission issue
            if 'Google Drive' in response.text and 'Access' in response.text:
                raise ValueError("Cannot access file. Make sure the Google Drive link is set to "
                               "'Anyone with the link can view' in sharing settings.")
            else:
                raise ValueError("Failed to download file. Make sure the link is a direct file link, "
                               "not a folder or restricted document.")

        return response.content, content_type

    except requests.RequestException as e:
        raise requests.RequestException(f"Failed to download from Google Drive: {str(e)}")


def read_document_from_drive(url: str) -> str:
    """
    Download and extract text from a Google Drive document

    Args:
        url: Google Drive share link

    Returns:
        Extracted text

    Raises:
        ValueError: If URL is invalid or file format is not supported
        requests.RequestException: If download fails
    """
    # Download file
    file_content, mime_type = download_from_google_drive(url)

    # Handle different file types
    if 'word' in mime_type.lower() or 'document' in mime_type.lower() or file_content.startswith(b'PK'):
        # Word document (.docx)
        return read_docx(file_content)

    elif 'text/plain' in mime_type.lower():
        # Plain text
        return file_content.decode('utf-8')

    elif 'application/pdf' in mime_type.lower():
        # PDF - would need additional library
        raise ValueError("PDF files are not yet supported. Please use Word (.docx) or text files.")

    else:
        # Try to detect by content
        if file_content.startswith(b'PK'):
            # Likely a .docx file (ZIP-based)
            return read_docx(file_content)

        # Try plain text as fallback
        try:
            return file_content.decode('utf-8')
        except UnicodeDecodeError:
            raise ValueError(f"Unsupported file format (MIME: {mime_type}). "
                           "Please use Word (.docx) or text files.")


def export_google_doc_as_text(doc_url: str) -> str:
    """
    Export a Google Docs document as plain text

    This uses Google Docs export feature for Google Docs native documents

    Args:
        doc_url: Google Docs URL (https://docs.google.com/document/d/...)

    Returns:
        Exported text content
    """
    file_id = extract_google_drive_file_id(doc_url)
    if not file_id:
        raise ValueError("Could not extract document ID from Google Docs URL")

    # Use Google Docs export API
    export_url = f"https://docs.google.com/document/d/{file_id}/export?format=txt"

    try:
        response = requests.get(export_url, timeout=30)
        response.raise_for_status()

        # Check if we got permission error
        if 'text/html' in response.headers.get('content-type', '').lower():
            raise ValueError("Cannot access document. Make sure the Google Doc is set to "
                           "'Anyone with the link can view' in sharing settings.")

        return response.text

    except requests.RequestException as e:
        # Fallback to regular download method
        return read_document_from_drive(doc_url)
