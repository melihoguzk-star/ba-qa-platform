"""
Document Chunking Strategy for Semantic Search

Splits documents into semantic chunks optimized for embedding and search.
Document-type specific strategies to preserve meaningful context.

Author: BA-QA Platform
Date: 2026-02-16
"""
import logging
from typing import Dict, List, Any
import json

logger = logging.getLogger(__name__)


class DocumentChunker:
    """Split documents into semantic chunks for vector search."""

    # Token limits (approximate, 1 token ~= 4 characters)
    TARGET_CHUNK_SIZE = 512  # tokens
    MAX_CHUNK_SIZE = 1024    # tokens

    def chunk_document(self, doc_id: int, doc_type: str, content_json: dict,
                       metadata: dict = None) -> List[Dict[str, Any]]:
        """
        Chunk a document based on its type.

        Args:
            doc_id: Document ID from database
            doc_type: Document type ('ba', 'ta', 'tc')
            content_json: Parsed document content
            metadata: Additional metadata (tags, jira_keys, etc.)

        Returns:
            List of chunks with text and metadata
        """
        metadata = metadata or {}

        # Check if using new generic format (sections array)
        if 'sections' in content_json:
            return self._chunk_generic_document(doc_id, doc_type, content_json, metadata)

        # Otherwise use legacy BRD Pipeline format
        if doc_type == 'ba':
            return self._chunk_ba_document(doc_id, content_json, metadata)
        elif doc_type == 'ta':
            return self._chunk_ta_document(doc_id, content_json, metadata)
        elif doc_type == 'tc':
            return self._chunk_tc_document(doc_id, content_json, metadata)
        else:
            raise ValueError(f"Unsupported document type: {doc_type}")

    def _chunk_ba_document(self, doc_id: int, content: dict, metadata: dict) -> List[Dict]:
        """
        Chunk BA documents by screens (ekranlar) and backend operations.

        Each screen becomes a chunk with:
        - Screen name
        - Description
        - UI elements list
        """
        chunks = []
        chunk_index = 0

        # Chunk screens (ekranlar)
        ekranlar = content.get('ekranlar', [])
        for ekran in ekranlar:
            ekran_adi = ekran.get('ekran_adi', 'Unnamed Screen')
            aciklama = ekran.get('aciklama', '')
            ui_elements = ekran.get('ui_elementleri', [])

            # Build chunk text
            text_parts = [
                f"Screen: {ekran_adi}",
                f"Description: {aciklama}" if aciklama else "",
            ]

            if ui_elements:
                text_parts.append(f"UI Elements: {', '.join(ui_elements)}")

            chunk_text = '\n'.join(filter(None, text_parts))

            # Check size
            if self._estimate_tokens(chunk_text) > self.MAX_CHUNK_SIZE:
                logger.warning(f"BA screen chunk exceeds max size: {ekran_adi}")
                chunk_text = self._truncate_text(chunk_text, self.MAX_CHUNK_SIZE)

            chunks.append({
                'document_id': doc_id,
                'chunk_index': chunk_index,
                'chunk_type': 'ekran',
                'chunk_text': chunk_text,
                'metadata': {
                    **metadata,
                    'ekran_adi': ekran_adi,
                    'has_ui_elements': len(ui_elements) > 0
                }
            })
            chunk_index += 1

        # Chunk backend operations (backend_islemler)
        backend_islemler = content.get('backend_islemler', [])
        for islem in backend_islemler:
            islem_adi = islem.get('islem_adi', 'Unnamed Operation')
            endpoint = islem.get('endpoint', '')
            method = islem.get('method', '')

            text_parts = [
                f"Backend Operation: {islem_adi}",
            ]

            if endpoint:
                text_parts.append(f"Endpoint: {method} {endpoint}")

            chunk_text = '\n'.join(text_parts)

            chunks.append({
                'document_id': doc_id,
                'chunk_index': chunk_index,
                'chunk_type': 'backend_operation',
                'chunk_text': chunk_text,
                'metadata': {
                    **metadata,
                    'islem_adi': islem_adi,
                    'endpoint': endpoint,
                    'method': method
                }
            })
            chunk_index += 1

        return chunks

    def _chunk_ta_document(self, doc_id: int, content: dict, metadata: dict) -> List[Dict]:
        """
        Chunk TA documents by API endpoints and data entities.

        Each endpoint becomes a chunk with:
        - Service name
        - Endpoint path + method
        - Description
        """
        chunks = []
        chunk_index = 0

        # Chunk services and their endpoints
        servisler = content.get('servisler', [])
        for servis in servisler:
            servis_adi = servis.get('servis_adi', 'Unnamed Service')
            servis_aciklama = servis.get('aciklama', '')
            teknolojiler = servis.get('teknolojiler', [])
            endpoints = servis.get('endpoints', [])

            # Each endpoint gets its own chunk
            for endpoint in endpoints:
                path = endpoint.get('path', '')
                method = endpoint.get('method', 'GET')
                aciklama = endpoint.get('aciklama', '')

                text_parts = [
                    f"Service: {servis_adi}",
                    f"Service Description: {servis_aciklama}" if servis_aciklama else "",
                    f"API Endpoint: {method} {path}",
                    f"Description: {aciklama}" if aciklama else "",
                ]

                if teknolojiler:
                    text_parts.append(f"Technologies: {', '.join(teknolojiler)}")

                chunk_text = '\n'.join(filter(None, text_parts))

                if self._estimate_tokens(chunk_text) > self.MAX_CHUNK_SIZE:
                    logger.warning(f"TA endpoint chunk exceeds max size: {path}")
                    chunk_text = self._truncate_text(chunk_text, self.MAX_CHUNK_SIZE)

                chunks.append({
                    'document_id': doc_id,
                    'chunk_index': chunk_index,
                    'chunk_type': 'endpoint',
                    'chunk_text': chunk_text,
                    'metadata': {
                        **metadata,
                        'servis_adi': servis_adi,
                        'endpoint': path,
                        'method': method,
                        'teknolojiler': teknolojiler
                    }
                })
                chunk_index += 1

        # Chunk data models
        veri_modeli = content.get('veri_modeli', [])
        for entity in veri_modeli:
            entity_name = entity.get('entity', 'Unnamed Entity')
            fields = entity.get('fields', [])

            text_parts = [
                f"Data Entity: {entity_name}",
                f"Fields: {len(fields)} fields"
            ]

            # Add field details
            field_details = []
            for field in fields[:10]:  # Limit to first 10 fields
                name = field.get('name', '')
                field_type = field.get('type', '')
                required = field.get('required', False)
                req_str = " (required)" if required else ""
                field_details.append(f"{name}: {field_type}{req_str}")

            if field_details:
                text_parts.append('\n'.join(field_details))

            chunk_text = '\n'.join(filter(None, text_parts))

            if self._estimate_tokens(chunk_text) > self.MAX_CHUNK_SIZE:
                chunk_text = self._truncate_text(chunk_text, self.MAX_CHUNK_SIZE)

            chunks.append({
                'document_id': doc_id,
                'chunk_index': chunk_index,
                'chunk_type': 'data_entity',
                'chunk_text': chunk_text,
                'metadata': {
                    **metadata,
                    'entity_name': entity_name,
                    'field_count': len(fields)
                }
            })
            chunk_index += 1

        return chunks

    def _chunk_tc_document(self, doc_id: int, content: dict, metadata: dict) -> List[Dict]:
        """
        Chunk TC documents by test cases/scenarios.

        Each test case becomes a chunk with:
        - Test ID and name
        - Description
        - Test steps
        - Expected results
        """
        chunks = []
        chunk_index = 0

        # Support both 'test_cases' and 'test_scenarios' keys
        test_cases = content.get('test_cases', []) or content.get('test_scenarios', [])

        for test_case in test_cases:
            # Extract test case fields (flexible keys)
            test_id = test_case.get('test_id') or test_case.get('scenario_id', 'TC-Unknown')
            test_name = test_case.get('test_name') or test_case.get('title', 'Unnamed Test')
            description = test_case.get('description', '')
            priority = test_case.get('priority', '')
            steps = test_case.get('steps', [])
            expected = test_case.get('expected_result', '')

            # Build chunk text
            text_parts = [
                f"Test Case: {test_id}",
                f"Name: {test_name}",
            ]

            if description:
                text_parts.append(f"Description: {description}")

            if priority:
                text_parts.append(f"Priority: {priority}")

            # Add steps
            if steps:
                text_parts.append("Steps:")
                if isinstance(steps, list):
                    for i, step in enumerate(steps, 1):
                        if isinstance(step, dict):
                            action = step.get('action', step.get('step', ''))
                            step_expected = step.get('expected', '')
                            text_parts.append(f"  {i}. {action}")
                            if step_expected:
                                text_parts.append(f"     Expected: {step_expected}")
                        else:
                            text_parts.append(f"  {i}. {step}")

            if expected:
                text_parts.append(f"Expected Result: {expected}")

            chunk_text = '\n'.join(filter(None, text_parts))

            if self._estimate_tokens(chunk_text) > self.MAX_CHUNK_SIZE:
                logger.warning(f"TC test case chunk exceeds max size: {test_id}")
                chunk_text = self._truncate_text(chunk_text, self.MAX_CHUNK_SIZE)

            chunks.append({
                'document_id': doc_id,
                'chunk_index': chunk_index,
                'chunk_type': 'test_case',
                'chunk_text': chunk_text,
                'metadata': {
                    **metadata,
                    'test_id': test_id,
                    'test_name': test_name,
                    'priority': priority,
                    'step_count': len(steps) if steps else 0
                }
            })
            chunk_index += 1

        return chunks

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation: 1 token ~= 4 chars)."""
        return len(text) // 4

    def _truncate_text(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within max tokens."""
        max_chars = max_tokens * 4
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + "..."

    def _chunk_generic_document(self, doc_id: int, doc_type: str, content: dict,
                                 metadata: dict) -> List[Dict]:
        """
        Chunk generic document format (sections array).

        Used for Document Repository Phase 1/2/3 documents that use
        the generic sections format instead of BRD Pipeline format.

        Args:
            doc_id: Document ID
            doc_type: Document type
            content: Content with 'sections' array
            metadata: Additional metadata

        Returns:
            List of chunks
        """
        chunks = []
        chunk_index = 0

        sections = content.get('sections', [])

        for section in sections:
            section_title = section.get('section_title', 'Untitled Section')
            section_type = section.get('section_type', 'general')

            # Get section content (might be JSON string or dict)
            section_content = section.get('content_json', '{}')
            if isinstance(section_content, str):
                try:
                    section_data = json.loads(section_content)
                except:
                    section_data = {}
            else:
                section_data = section_content

            # Build chunk text
            text_parts = [f"Section: {section_title}"]

            # Add description
            if 'description' in section_data:
                text_parts.append(f"\nDescription: {section_data['description']}")

            # Add requirements
            if 'requirements' in section_data:
                text_parts.append("\n\nRequirements:")
                for req in section_data.get('requirements', []):
                    text_parts.append(f"- {req}")

            # Add security items
            if 'security' in section_data:
                text_parts.append("\n\nSecurity:")
                for sec in section_data.get('security', []):
                    text_parts.append(f"- {sec}")

            # Add components
            if 'components' in section_data:
                text_parts.append("\n\nComponents:")
                for comp in section_data.get('components', []):
                    text_parts.append(f"- {comp}")

            # Add APIs
            if 'apis' in section_data:
                text_parts.append("\n\nAPIs:")
                for api in section_data.get('apis', []):
                    text_parts.append(f"- {api}")

            # Add test cases
            if 'test_cases' in section_data:
                text_parts.append("\n\nTest Cases:")
                for tc in section_data.get('test_cases', []):
                    tc_id = tc.get('id', '')
                    tc_title = tc.get('title', '')
                    text_parts.append(f"\n{tc_id}: {tc_title}")

                    if 'steps' in tc:
                        text_parts.append("Steps:")
                        for step in tc['steps']:
                            text_parts.append(f"  - {step}")

                    if 'expected' in tc:
                        text_parts.append(f"Expected: {tc['expected']}")

            chunk_text = '\n'.join(text_parts)

            # Check size
            if self._estimate_tokens(chunk_text) > self.MAX_CHUNK_SIZE:
                logger.warning(f"Generic section chunk exceeds max size: {section_title}")
                chunk_text = self._truncate_text(chunk_text, self.MAX_CHUNK_SIZE)

            chunks.append({
                'document_id': doc_id,
                'chunk_index': chunk_index,
                'chunk_type': section_type,
                'chunk_text': chunk_text,
                'metadata': {
                    **metadata,
                    'section_title': section_title,
                    'section_type': section_type,
                    'doc_type': doc_type
                }
            })
            chunk_index += 1

        logger.info(f"Generated {len(chunks)} chunks for generic document {doc_id}")
        return chunks


# Singleton instance
_chunker = None

def get_chunker() -> DocumentChunker:
    """Get singleton chunker instance."""
    global _chunker
    if _chunker is None:
        _chunker = DocumentChunker()
    return _chunker
