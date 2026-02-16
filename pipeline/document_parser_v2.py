"""
Heading-based Document Parser (v2)
Converts documents to JSON based on heading hierarchy, not keyword patterns
"""
import re
from typing import Dict, List, Tuple


class HeadingBasedParser:
    """Parse documents based on heading structure (H1, H2, H3)"""

    @staticmethod
    def parse_text_to_structure(text: str) -> Dict:
        """
        Parse text into hierarchical structure based on headings

        Context-aware: After an H1, next heading is likely H2 (subsection)

        Returns:
        {
            "sections": [
                {
                    "heading": "Section Name",
                    "level": 1,
                    "content": "text content",
                    "subsections": [
                        {
                            "heading": "Subsection Name",
                            "level": 2,
                            "items": ["item1", "item2"],
                            "content": "text"
                        }
                    ]
                }
            ]
        }
        """
        lines = text.strip().split('\n')

        # Parse into structured data
        structure = {"sections": []}
        current_section = None
        current_subsection = None
        just_had_section = False  # Track if we just created a section

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect heading level
            detected_level = HeadingBasedParser._detect_heading_level(line)

            # Context-aware adjustment:
            # If we just had an H1 section and detect another "heading",
            # it's probably a subsection, not a new section
            if detected_level == 1 and just_had_section and current_section:
                # Check if this looks like a subsection
                # (has content following it or has fewer than 4 words)
                words = HeadingBasedParser._clean_heading(line).split()
                if len(words) <= 3:
                    # Treat as subsection
                    detected_level = 2

            level = detected_level

            if level == 1:
                # H1 - Main section
                current_section = {
                    "heading": HeadingBasedParser._clean_heading(line),
                    "level": 1,
                    "content": "",
                    "subsections": []
                }
                structure["sections"].append(current_section)
                current_subsection = None
                just_had_section = True  # Mark that we just created a section

            elif level == 2:
                # H2 - Subsection
                if current_section:
                    current_subsection = {
                        "heading": HeadingBasedParser._clean_heading(line),
                        "level": 2,
                        "content": "",
                        "items": []
                    }
                    current_section["subsections"].append(current_subsection)
                    just_had_section = False  # Reset flag
                else:
                    # No parent section - treat as main section
                    current_section = {
                        "heading": HeadingBasedParser._clean_heading(line),
                        "level": 1,
                        "content": "",
                        "subsections": [],
                        "items": []
                    }
                    structure["sections"].append(current_section)
                    just_had_section = True

            elif line.startswith(('-', '•', '*', '+')):
                # Bullet point - list item
                item = line.lstrip('-•*+ ').strip()
                if current_subsection:
                    current_subsection["items"].append(item)
                elif current_section:
                    # Item directly under section
                    if "items" not in current_section:
                        current_section["items"] = []
                    current_section["items"].append(item)
                just_had_section = False  # Content found

            elif re.match(r'^\d+[.)]', line):
                # Numbered item
                item = re.sub(r'^\d+[.)] *', '', line)
                if current_subsection:
                    if "steps" not in current_subsection:
                        current_subsection["steps"] = []
                    current_subsection["steps"].append(item)
                elif current_section:
                    if "steps" not in current_section:
                        current_section["steps"] = []
                    current_section["steps"].append(item)
                just_had_section = False  # Content found

            else:
                # Regular text - add to content
                if current_subsection:
                    if current_subsection["content"]:
                        current_subsection["content"] += " " + line
                    else:
                        current_subsection["content"] = line
                elif current_section:
                    if current_section["content"]:
                        current_section["content"] += " " + line
                    else:
                        current_section["content"] = line
                just_had_section = False  # Content found

        return structure

    @staticmethod
    def _detect_heading_level(line: str, context: Dict = None) -> int:
        """
        Detect if line is a heading and its level

        Returns:
            0 = regular text
            1 = H1 (main section - few words, important)
            2 = H2 (subsection - more specific)

        Logic:
        - Lines ending with ":" are headings
        - Numbered sections (e.g., "5.3. Section Name") are headings
        - Shorter headings (1-3 words) → H1
        - Longer headings (4-6 words) → H2
        - All caps → H1
        - Title case → H2
        """
        # Check for markdown-style headings
        if line.startswith('# '):
            return 1
        if line.startswith('## '):
            return 2
        if line.startswith('### '):
            return 2

        # Check for numbered sections (e.g., "5.3. Teknik Gereksinimler")
        # Pattern: digits.digits. or just digits.
        numbered_pattern = r'^\d+(\.\d+)*\.\s+'
        if re.match(numbered_pattern, line):
            # Remove the number prefix to analyze the text
            clean_line = re.sub(numbered_pattern, '', line)
            word_count = len(clean_line.split())

            # Numbered sections are usually subsections (H2)
            # unless they're very short
            if word_count <= 2:
                return 1
            return 2

        # Check for colon-ending headings (common in documents)
        if line.endswith(':'):
            # Clean and count words
            clean_line = line.rstrip(':').strip()
            # Remove number prefix if present
            clean_line = re.sub(r'^\d+(\.\d+)*\.\s*', '', clean_line)
            words = clean_line.split()
            word_count = len(words)

            if word_count == 0:
                return 0

            # Very short (1-2 words) = likely main section
            if word_count <= 2:
                return 1

            # Medium (3-4 words) = depends on case
            if word_count <= 4:
                # All caps suggests main section
                if clean_line.isupper():
                    return 1
                # Otherwise subsection
                return 2

            # Longer (5+ words) = subsection
            return 2

        # Check for ALL CAPS lines (often main headings)
        if line.isupper() and len(line.split()) <= 4:
            return 1

        return 0

    @staticmethod
    def _clean_heading(line: str) -> str:
        """Remove heading markers and clean text"""
        # Remove markdown #
        line = re.sub(r'^#+\s*', '', line)
        # Remove numbered prefixes (e.g., "5.3. " or "1. ")
        line = re.sub(r'^\d+(\.\d+)*\.\s*', '', line)
        # Remove trailing colon
        line = line.rstrip(':')
        return line.strip()

    @staticmethod
    def structure_to_ba(structure: Dict) -> Dict:
        """
        Convert hierarchical structure to BA JSON format

        Maps based on structure:
        - Sections become top-level arrays (ekranlar, backend_islemler, etc.)
        - Subsections become items in those arrays
        - Items become fields/actions
        """
        ba_doc = {
            "ekranlar": [],
            "backend_islemler": [],
            "guvenlik_gereksinimleri": [],
            "test_senaryolari": []
        }

        for section in structure.get("sections", []):
            section_heading = section["heading"].lower()

            # Map sections to BA structure based on content type
            if HeadingBasedParser._is_screen_section(section):
                # This section contains screens/UI
                if section.get("subsections"):
                    # Has subsections - each subsection is a screen
                    for subsection in section.get("subsections", []):
                        screen = {
                            "ekran_adi": subsection["heading"],
                            "aciklama": subsection.get("content", ""),
                            "fields": [],
                            "actions": []
                        }

                        # Parse items as fields
                        for item in subsection.get("items", []):
                            field = HeadingBasedParser._parse_field(item)
                            if field["type"] == "button":
                                screen["actions"].append({
                                    "button": field["name"],
                                    "action": field["description"]
                                })
                            else:
                                screen["fields"].append({
                                    "name": field["name"],
                                    "type": field["type"],
                                    "required": field["required"],
                                    "description": field["description"]
                                })

                        ba_doc["ekranlar"].append(screen)
                else:
                    # No subsections - section itself is a screen
                    items = section.get("items", [])
                    if items:
                        screen = {
                            "ekran_adi": section["heading"],
                            "aciklama": section.get("content", ""),
                            "fields": [],
                            "actions": []
                        }

                        for item in items:
                            field = HeadingBasedParser._parse_field(item)
                            if field["type"] == "button":
                                screen["actions"].append({
                                    "button": field["name"],
                                    "action": field["description"]
                                })
                            else:
                                screen["fields"].append({
                                    "name": field["name"],
                                    "type": field["type"],
                                    "required": field["required"],
                                    "description": field["description"]
                                })

                        ba_doc["ekranlar"].append(screen)

            elif HeadingBasedParser._is_backend_section(section):
                # This section contains backend/API operations
                if section.get("subsections"):
                    for subsection in section.get("subsections", []):
                        # Look for API endpoint in content
                        endpoint_info = HeadingBasedParser._extract_api_info(
                            subsection.get("content", "")
                        )

                        ba_doc["backend_islemler"].append({
                            "islem": subsection["heading"],
                            "aciklama": subsection.get("content", ""),
                            "endpoint": endpoint_info.get("endpoint", "/api/endpoint"),
                            "method": endpoint_info.get("method", "POST")
                        })
                else:
                    # No subsections - treat section itself as backend operation
                    content = section.get("content", "")
                    items = section.get("items", [])
                    if items:
                        content += "\n" + "\n".join(f"• {item}" for item in items)

                    endpoint_info = HeadingBasedParser._extract_api_info(content)

                    ba_doc["backend_islemler"].append({
                        "islem": section["heading"],
                        "aciklama": content.strip(),
                        "endpoint": endpoint_info.get("endpoint", "/api/endpoint"),
                        "method": endpoint_info.get("method", "POST")
                    })

            elif HeadingBasedParser._is_security_section(section):
                # Security requirements
                if section.get("subsections"):
                    # Has subsections - process each
                    for subsection in section.get("subsections", []):
                        ba_doc["guvenlik_gereksinimleri"].append({
                            "gereksinim": subsection["heading"],
                            "aciklama": subsection.get("content", "")
                        })
                else:
                    # No subsections - treat section itself as a requirement
                    items = section.get("items", [])
                    if items:
                        # Create requirement from section with its items
                        aciklama = section.get("content", "")
                        if items:
                            aciklama += "\n" + "\n".join(f"• {item}" for item in items)
                        ba_doc["guvenlik_gereksinimleri"].append({
                            "gereksinim": section["heading"],
                            "aciklama": aciklama.strip()
                        })
                    elif section.get("content"):
                        # Just content, no items
                        ba_doc["guvenlik_gereksinimleri"].append({
                            "gereksinim": section["heading"],
                            "aciklama": section.get("content", "")
                        })

            elif HeadingBasedParser._is_test_section(section):
                # Test scenarios
                if section.get("subsections"):
                    for subsection in section.get("subsections", []):
                        ba_doc["test_senaryolari"].append({
                            "senaryo": subsection["heading"],
                            "adimlar": subsection.get("steps", [])
                        })
                else:
                    # No subsections - treat section itself as a test scenario
                    steps = section.get("steps", [])
                    items = section.get("items", [])
                    if steps or items:
                        ba_doc["test_senaryolari"].append({
                            "senaryo": section["heading"],
                            "adimlar": steps if steps else items
                        })

            else:
                # Unmatched section - treat as general requirement
                # (fallback for sections that don't fit other categories)
                items = section.get("items", [])
                content = section.get("content", "")

                if items or content:
                    aciklama = content
                    if items:
                        if aciklama:
                            aciklama += "\n"
                        aciklama += "\n".join(f"• {item}" for item in items)

                    ba_doc["guvenlik_gereksinimleri"].append({
                        "gereksinim": section["heading"],
                        "aciklama": aciklama.strip()
                    })

        return ba_doc

    @staticmethod
    def _is_screen_section(section: Dict) -> bool:
        """Check if section contains UI/screen content"""
        heading = section["heading"].lower()
        keywords = [
            "ekran", "screen", "ui", "interface", "page", "view", "form",
            "arayüz", "sayfa", "görünüm", "kullanıcı arayüz", "user interface"
        ]

        # Check heading
        if any(kw in heading for kw in keywords):
            return True

        # Also check subsection headings and content
        for subsection in section.get("subsections", []):
            sub_heading = subsection["heading"].lower()
            if any(kw in sub_heading for kw in keywords):
                return True

        # Check if items look like UI fields (contain field descriptors)
        items = section.get("items", [])
        if items:
            field_indicators = ["field", "button", "input", "checkbox", "alanı", "butonu"]
            item_text = " ".join(items).lower()
            if any(indicator in item_text for indicator in field_indicators):
                return True

        return False

    @staticmethod
    def _is_backend_section(section: Dict) -> bool:
        """Check if section contains backend/API content"""
        heading = section["heading"].lower()
        keywords = ["backend", "api", "endpoint", "servis", "service", "işlem", "operation"]

        # Check heading
        if any(kw in heading for kw in keywords):
            return True

        # Check content for API patterns (GET, POST, etc.)
        content = section.get("content", "")
        if re.search(r'\b(GET|POST|PUT|DELETE|PATCH)\s+/', content):
            return True

        # Check items for API patterns
        items = section.get("items", [])
        if items:
            item_text = " ".join(items)
            if re.search(r'\b(GET|POST|PUT|DELETE|PATCH)\s+/', item_text):
                return True

        # Check subsections
        for subsection in section.get("subsections", []):
            sub_content = subsection.get("content", "")
            if re.search(r'\b(GET|POST|PUT|DELETE|PATCH)\s+/', sub_content):
                return True

        return False

    @staticmethod
    def _is_security_section(section: Dict) -> bool:
        """Check if section contains security requirements"""
        heading = section["heading"].lower()
        keywords = ["güvenlik", "security", "auth", "permission", "access", "teknik", "technical", "gereksinim", "requirement"]

        # Check heading
        if any(kw in heading for kw in keywords):
            return True

        # Security indicators list (used for items and subsections)
        security_indicators = ["güvenlik", "security", "encryption", "hash", "token", "authentication", "şifreleme"]

        # Check items content for security-related terms
        items = section.get("items", [])
        if items:
            item_text = " ".join(items).lower()
            if any(indicator in item_text for indicator in security_indicators):
                return True

        # Check subsections
        for subsection in section.get("subsections", []):
            sub_heading = subsection["heading"].lower()
            if any(kw in sub_heading for kw in keywords):
                return True
            sub_items = subsection.get("items", [])
            if sub_items:
                sub_text = " ".join(sub_items).lower()
                if any(indicator in sub_text for indicator in security_indicators):
                    return True

        return False

    @staticmethod
    def _is_test_section(section: Dict) -> bool:
        """Check if section contains test scenarios"""
        heading = section["heading"].lower()
        keywords = ["test", "senaryo", "scenario", "case"]
        return any(kw in heading for kw in keywords)

    @staticmethod
    def _parse_field(item: str) -> Dict:
        """Parse a field from item text"""
        field = {
            "name": "",
            "type": "text",
            "required": False,
            "description": ""
        }

        # Try to split by colon
        if ':' in item or '：' in item:
            parts = re.split('[：:]', item, 1)
            field["name"] = parts[0].strip()
            field["description"] = parts[1].strip() if len(parts) > 1 else ""
        else:
            field["name"] = item
            field["description"] = ""

        # Detect field type
        combined = (field["name"] + " " + field["description"]).lower()

        if "email" in combined or "e-mail" in combined:
            field["type"] = "email"
        elif "password" in combined or "şifre" in combined or "parola" in combined:
            field["type"] = "password"
        elif "checkbox" in combined or "onay" in combined:
            field["type"] = "checkbox"
        elif "button" in combined or "buton" in combined:
            field["type"] = "button"
        elif "text" in combined or "input" in combined:
            field["type"] = "text"

        # Detect required
        if "required" in combined or "zorunlu" in combined or "gerekli" in combined:
            field["required"] = True
        elif "optional" in combined or "opsiyonel" in combined:
            field["required"] = False

        return field

    @staticmethod
    def _extract_api_info(text: str) -> Dict:
        """Extract API endpoint and method from text"""
        info = {
            "method": "POST",
            "endpoint": "/api/endpoint"
        }

        # Look for HTTP method + endpoint pattern
        pattern = r'\b(GET|POST|PUT|DELETE|PATCH)\s+(/[\w/:\-{}]+)'
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            info["method"] = match.group(1).upper()
            info["endpoint"] = match.group(2)

        return info


def parse_text_to_json(text: str, doc_type: str = 'ba') -> Dict:
    """
    Main function: Parse text to JSON based on heading structure

    Args:
        text: Document text with headings
        doc_type: 'ba', 'ta', or 'tc'

    Returns:
        Parsed JSON dictionary
    """
    parser = HeadingBasedParser()

    # Step 1: Parse into hierarchical structure
    structure = parser.parse_text_to_structure(text)

    # Step 2: Convert to specific format
    if doc_type == 'ba':
        return parser.structure_to_ba(structure)
    elif doc_type == 'ta':
        # TA parsing can be added similarly
        return {
            "servisler": [],
            "veri_modeli": [],
            "teknolojik_gereksinimler": []
        }
    elif doc_type == 'tc':
        # TC parsing can be added similarly
        return {
            "test_cases": [],
            "test_senaryolari": []
        }
    else:
        return structure
