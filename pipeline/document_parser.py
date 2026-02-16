"""
Rule-based Document Parser
Converts structured Word documents to BA/TA/TC JSON format without AI
"""
import re
from typing import Dict, List, Optional, Tuple
from docx import Document
from docx.text.paragraph import Paragraph


class DocumentParser:
    """Parse structured Word documents into JSON format based on headings"""

    # Heading patterns for BA (Business Analysis)
    BA_PATTERNS = {
        'ekranlar': [
            r'ekranlar',
            r'screens?',
            r'ui\s*screens?',
            r'user\s*interface',
            r'pages?',
            r'views?'
        ],
        'backend_islemler': [
            r'backend',
            r'api',
            r'endpoints?',
            r'servisler',
            r'services?',
            r'işlemler',
            r'operations?'
        ],
        'guvenlik_gereksinimleri': [
            r'güvenlik',
            r'security',
            r'authentication',
            r'authorization'
        ],
        'test_senaryolari': [
            r'test',
            r'scenarios?',
            r'senaryolar'
        ]
    }

    # Heading patterns for TA (Technical Analysis)
    TA_PATTERNS = {
        'servisler': [
            r'servisler',
            r'services?',
            r'microservices?',
            r'components?'
        ],
        'veri_modeli': [
            r'veri\s*model',
            r'data\s*model',
            r'database',
            r'entities',
            r'schema'
        ],
        'teknolojik_gereksinimler': [
            r'teknoloj',
            r'technolog',
            r'tech\s*stack',
            r'requirements?',
            r'dependencies'
        ]
    }

    # Heading patterns for TC (Test Cases)
    TC_PATTERNS = {
        'test_cases': [
            r'test\s*cases?',
            r'test\s*scenarios?',
            r'test\s*suite'
        ],
        'test_senaryolari': [
            r'senaryolar',
            r'scenarios?',
            r'test\s*plans?'
        ]
    }

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for pattern matching"""
        return text.lower().strip()

    @staticmethod
    def matches_pattern(text: str, patterns: List[str]) -> bool:
        """Check if text matches any pattern"""
        normalized = DocumentParser.normalize_text(text)
        for pattern in patterns:
            if re.search(pattern, normalized):
                return True
        return False

    @staticmethod
    def extract_from_docx(file_path: str) -> Dict:
        """Extract structured content from Word document"""
        doc = Document(file_path)

        # Extract paragraphs with their styles
        content = []
        for para in doc.paragraphs:
            if para.text.strip():
                content.append({
                    'text': para.text.strip(),
                    'style': para.style.name,
                    'level': DocumentParser._get_heading_level(para)
                })

        return {'paragraphs': content}

    @staticmethod
    def _get_heading_level(para: Paragraph) -> int:
        """Get heading level (0 = normal text, 1-9 = heading levels)"""
        style_name = para.style.name.lower()

        if 'heading' in style_name:
            # Extract number from "Heading 1", "Heading 2", etc.
            match = re.search(r'heading\s*(\d+)', style_name)
            if match:
                return int(match.group(1))
            return 1  # Default heading level

        return 0  # Normal text

    @staticmethod
    def parse_to_ba(content: Dict) -> Dict:
        """Parse content to BA (Business Analysis) format"""
        ba_doc = {
            'ekranlar': [],
            'backend_islemler': [],
            'guvenlik_gereksinimleri': [],
            'test_senaryolari': []
        }

        current_section = None
        current_item = None
        current_subsection = None

        for para in content['paragraphs']:
            text = para['text']
            level = para['level']

            # Check if this is a main section heading
            if level == 1 or level == 2:
                # Determine which section this is
                section_found = False
                for section_key, patterns in DocumentParser.BA_PATTERNS.items():
                    if DocumentParser.matches_pattern(text, patterns):
                        current_section = section_key
                        section_found = True
                        break

                if not section_found:
                    # If not a recognized section, treat as item heading
                    if current_section and level == 2:
                        current_item = {'name': text}
                        current_subsection = None

            # Check if this is a subsection (Heading 3)
            elif level == 3:
                if current_item:
                    current_subsection = text

            # Normal text - add to current item
            elif level == 0 and current_section and text:
                if current_section == 'ekranlar':
                    ba_doc['ekranlar'] = DocumentParser._parse_screens(
                        text, ba_doc['ekranlar'], current_item, current_subsection
                    )

                elif current_section == 'backend_islemler':
                    ba_doc['backend_islemler'] = DocumentParser._parse_backend(
                        text, ba_doc['backend_islemler'], current_item
                    )

                elif current_section == 'guvenlik_gereksinimleri':
                    ba_doc['guvenlik_gereksinimleri'].append({
                        'gereksinim': current_item.get('name', 'Security Requirement') if current_item else 'Requirement',
                        'aciklama': text
                    })

                elif current_section == 'test_senaryolari':
                    ba_doc['test_senaryolari'] = DocumentParser._parse_test_scenarios(
                        text, ba_doc['test_senaryolari'], current_item
                    )

        return ba_doc

    @staticmethod
    def _parse_screens(text: str, screens: List, current_item: Optional[Dict], subsection: Optional[str]) -> List:
        """Parse screen information"""
        # Look for bullet-point field definitions
        if text.startswith(('-', '•', '*', '+')):
            # Extract field name and description
            text = text.lstrip('-•*+ ').strip()

            # Try to split by : or colon
            if ':' in text or '：' in text:
                parts = re.split('[：:]', text, 1)
                field_name = parts[0].strip()
                field_info = parts[1].strip() if len(parts) > 1 else ''
            else:
                # No colon, just take the text as is
                field_name = text
                field_info = ''

            # Ensure we have a current screen item
            if current_item and 'ekran_adi' not in current_item:
                current_item['ekran_adi'] = current_item.get('name', 'Screen')
                current_item['aciklama'] = ''
                current_item['fields'] = []
                current_item['actions'] = []
                screens.append(current_item)

            if current_item:
                # Determine field type
                field_type = 'text'
                required = False

                # Type detection
                normalized = (field_name + ' ' + field_info).lower()
                if 'email' in normalized:
                    field_type = 'email'
                elif 'password' in normalized or 'şifre' in normalized:
                    field_type = 'password'
                elif 'checkbox' in normalized or 'onay' in normalized:
                    field_type = 'checkbox'
                elif 'button' in normalized or 'buton' in normalized or 'link' in normalized:
                    # This is an action
                    current_item['actions'].append({
                        'button': field_name,
                        'action': field_info or 'action'
                    })
                    return screens

                # Required detection
                if 'required' in normalized or 'zorunlu' in normalized or 'gerekli' in normalized:
                    required = True
                if 'optional' in normalized or 'opsiyonel' in normalized:
                    required = False

                current_item['fields'].append({
                    'name': field_name,
                    'type': field_type,
                    'required': required,
                    'description': field_info
                })

        return screens

    @staticmethod
    def _parse_backend(text: str, backend_ops: List, current_item: Optional[Dict]) -> List:
        """Parse backend operation information"""
        # Look for API endpoint patterns
        api_pattern = r'\b(GET|POST|PUT|DELETE|PATCH)\s+(/[\w/:\-{}]+)'
        match = re.search(api_pattern, text, re.IGNORECASE)

        if match and current_item:
            method = match.group(1).upper()
            endpoint = match.group(2)

            # Get description (rest of the text after the endpoint)
            desc_text = text[match.end():].strip()
            if not desc_text:
                desc_text = current_item.get('name', '')

            backend_ops.append({
                'islem': current_item.get('name', 'API Operation'),
                'aciklama': desc_text or 'API endpoint',
                'endpoint': endpoint,
                'method': method
            })
        elif current_item and 'api' in text.lower():
            # Fallback: if text mentions "api" but no pattern found
            backend_ops.append({
                'islem': current_item.get('name', 'API Operation'),
                'aciklama': text,
                'endpoint': '/api/endpoint',
                'method': 'POST'
            })

        return backend_ops

    @staticmethod
    def _parse_test_scenarios(text: str, scenarios: List, current_item: Optional[Dict]) -> List:
        """Parse test scenario information"""
        # Look for numbered steps
        step_pattern = r'(\d+)[.)]\s*(.+)'
        matches = re.findall(step_pattern, text)

        if matches and current_item:
            steps = [match[1].strip() for match in matches]

            scenarios.append({
                'senaryo': current_item.get('name', 'Test Scenario'),
                'adimlar': steps
            })

        return scenarios

    @staticmethod
    def parse_to_ta(content: Dict) -> Dict:
        """Parse content to TA (Technical Analysis) format"""
        ta_doc = {
            'servisler': [],
            'veri_modeli': [],
            'teknolojik_gereksinimler': []
        }

        current_section = None
        current_item = None

        for para in content['paragraphs']:
            text = para['text']
            level = para['level']

            # Check section headings
            if level == 1 or level == 2:
                section_found = False
                for section_key, patterns in DocumentParser.TA_PATTERNS.items():
                    if DocumentParser.matches_pattern(text, patterns):
                        current_section = section_key
                        section_found = True
                        break

                if not section_found and level == 2:
                    current_item = {'name': text}

            elif level == 0 and current_section and text:
                if current_section == 'servisler' and current_item:
                    ta_doc['servisler'].append({
                        'servis_adi': current_item.get('name', 'Service'),
                        'aciklama': text,
                        'teknolojiler': [],
                        'endpoints': []
                    })

                elif current_section == 'veri_modeli' and current_item:
                    ta_doc['veri_modeli'].append({
                        'entity': current_item.get('name', 'Entity'),
                        'fields': []
                    })

                elif current_section == 'teknolojik_gereksinimler':
                    ta_doc['teknolojik_gereksinimler'].append({
                        'kategori': current_item.get('name', 'Requirement') if current_item else 'General',
                        'gereksinim': text,
                        'aciklama': ''
                    })

        return ta_doc

    @staticmethod
    def parse_to_tc(content: Dict) -> Dict:
        """Parse content to TC (Test Cases) format"""
        tc_doc = {
            'test_cases': [],
            'test_senaryolari': []
        }

        current_section = None
        current_item = None
        test_case_counter = 1

        for para in content['paragraphs']:
            text = para['text']
            level = para['level']

            if level == 1 or level == 2:
                section_found = False
                for section_key, patterns in DocumentParser.TC_PATTERNS.items():
                    if DocumentParser.matches_pattern(text, patterns):
                        current_section = section_key
                        section_found = True
                        break

                if not section_found and level == 2:
                    current_item = {'name': text}

            elif level == 0 and current_section and text:
                if current_section == 'test_cases' and current_item:
                    # Parse test steps
                    step_pattern = r'(\d+)[.)]\s*(.+)'
                    matches = re.findall(step_pattern, text)

                    if matches:
                        steps = []
                        for i, match in enumerate(matches, 1):
                            steps.append({
                                'step': i,
                                'action': match[1].strip(),
                                'expected': ''
                            })

                        tc_doc['test_cases'].append({
                            'test_id': f'TC-{test_case_counter:03d}',
                            'test_name': current_item.get('name', 'Test Case'),
                            'description': text,
                            'priority': 'Medium',
                            'steps': steps,
                            'test_data': {},
                            'prerequisites': []
                        })
                        test_case_counter += 1

        return tc_doc

    @staticmethod
    def parse_text(text: str, doc_type: str = 'ba') -> Dict:
        """Parse plain text to JSON (simplified version without .docx)"""
        # Split text into lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # Create pseudo-content structure with better heuristics
        content = {'paragraphs': []}

        for i, line in enumerate(lines):
            # Determine heading level based on multiple heuristics
            level = 0

            # Section headers (likely Heading 1/2)
            if line.endswith(':'):
                # Check if it matches known section patterns
                is_main_section = False
                all_patterns = []

                if doc_type == 'ba':
                    all_patterns = [p for patterns in DocumentParser.BA_PATTERNS.values() for p in patterns]
                elif doc_type == 'ta':
                    all_patterns = [p for patterns in DocumentParser.TA_PATTERNS.values() for p in patterns]
                elif doc_type == 'tc':
                    all_patterns = [p for patterns in DocumentParser.TC_PATTERNS.values() for p in patterns]

                for pattern in all_patterns:
                    if re.search(pattern, DocumentParser.normalize_text(line)):
                        is_main_section = True
                        break

                if is_main_section:
                    level = 1  # Main section
                else:
                    level = 2  # Subsection

            # Bullet points and list items
            elif line.startswith(('-', '•', '*', '+')):
                level = 0  # Normal text (list item)

            # Numbered items
            elif re.match(r'^\d+[.)]', line):
                level = 0  # Normal text (numbered item)

            # Short lines (likely titles but not sections)
            elif len(line.split()) <= 6 and not line.startswith(('-', '•')):
                # Could be a subsection title
                level = 2

            content['paragraphs'].append({
                'text': line,
                'style': f'Heading {level}' if level > 0 else 'Normal',
                'level': level
            })

        # Parse based on document type
        if doc_type == 'ba':
            return DocumentParser.parse_to_ba(content)
        elif doc_type == 'ta':
            return DocumentParser.parse_to_ta(content)
        elif doc_type == 'tc':
            return DocumentParser.parse_to_tc(content)
        else:
            return {}


def parse_document(file_path: str, doc_type: str = 'ba') -> Dict:
    """
    Main function to parse Word document to JSON

    Args:
        file_path: Path to .docx file
        doc_type: 'ba', 'ta', or 'tc'

    Returns:
        Parsed JSON dictionary
    """
    parser = DocumentParser()

    # Extract content from Word document
    content = parser.extract_from_docx(file_path)

    # Parse to appropriate format
    if doc_type == 'ba':
        return parser.parse_to_ba(content)
    elif doc_type == 'ta':
        return parser.parse_to_ta(content)
    elif doc_type == 'tc':
        return parser.parse_to_tc(content)
    else:
        raise ValueError(f"Unknown document type: {doc_type}")


def parse_text_to_json(text: str, doc_type: str = 'ba') -> Dict:
    """
    Parse plain text to JSON (without Word file)

    Args:
        text: Plain text content
        doc_type: 'ba', 'ta', or 'tc'

    Returns:
        Parsed JSON dictionary
    """
    return DocumentParser.parse_text(text, doc_type)
