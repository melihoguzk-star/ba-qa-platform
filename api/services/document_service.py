"""
Document Service — Document parsing, embedding, chunking
"""
from typing import Dict, Any
import os


async def parse_uploaded_file(
    file_content: bytes,
    filename: str,
    file_extension: str
) -> Dict[str, Any]:
    """
    Parse uploaded file and extract content.

    Uses utils/text_extractor.py for parsing.
    """
    try:
        from utils.text_extractor import extract_text_from_bytes

        # Extract text
        extracted_text = extract_text_from_bytes(file_content, file_extension)

        # Attempt structured parsing for DOCX
        if file_extension in ['.docx', '.doc']:
            try:
                # Try to use document_reader for structured parsing
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as tmp:
                    tmp.write(file_content)
                    tmp_path = tmp.name

                # Attempt structured parsing
                try:
                    from utils.document_reader import parse_docx_to_json
                    structured_content = parse_docx_to_json(tmp_path)

                    return {
                        'content': structured_content,
                        'raw_text': extracted_text,
                        'metadata': {
                            'title': filename,
                            'filename': filename,
                            'file_type': file_extension,
                            'size_bytes': len(file_content),
                            'parsing_method': 'structured'
                        },
                        'confidence_score': 0.9,
                        'warnings': []
                    }
                finally:
                    os.unlink(tmp_path)

            except Exception as e:
                # Fall back to plain text
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Structured parsing failed, using plain text: {e}")

        # Plain text fallback
        return {
            'content': {'text': extracted_text},
            'raw_text': extracted_text,
            'metadata': {
                'title': filename,
                'filename': filename,
                'file_type': file_extension,
                'size_bytes': len(file_content),
                'parsing_method': 'plain_text'
            },
            'confidence_score': 0.7,
            'warnings': ['Plain text extraction used - structured parsing not available']
        }

    except Exception as e:
        raise Exception(f"Failed to parse file: {str(e)}")
