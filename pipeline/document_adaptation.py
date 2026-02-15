"""
📝 Document Adaptation Engine — Phase 3: Reuse & Adapt Workflow

Allows users to:
1. Select an existing document as a template
2. Preview and modify content
3. Create a new document while tracking lineage
4. Get AI-powered adaptation suggestions
"""
import json
import copy
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class DocumentAdapter:
    """
    Document adaptation engine for creating new documents from templates.
    Tracks lineage and provides smart modification suggestions.
    """

    def __init__(self):
        self.modifications = []

    # ═══════════════════════════════════════════════════════════════
    # TEMPLATE LOADING
    # ═══════════════════════════════════════════════════════════════

    def load_template(self, document: Dict) -> Dict:
        """
        Load a document as a template for adaptation.

        Args:
            document: Source document with content_json

        Returns:
            Deep copy of document ready for modification
        """
        template = copy.deepcopy(document)

        # Add metadata about template origin
        template['_is_template'] = True
        template['_original_id'] = document.get('id')
        template['_original_title'] = document.get('title')
        template['_loaded_at'] = datetime.now().isoformat()

        return template

    # ═══════════════════════════════════════════════════════════════
    # CONTENT MODIFICATIONS
    # ═══════════════════════════════════════════════════════════════

    def modify_field(self, content: Dict, path: str, new_value: any) -> Dict:
        """
        Modify a specific field in the content JSON.

        Args:
            content: Document content JSON
            path: Dot-notation path (e.g., "ekranlar.0.ekran_adi")
            new_value: New value to set

        Returns:
            Modified content
        """
        modified_content = copy.deepcopy(content)
        keys = path.split('.')

        # Navigate to the parent
        current = modified_content
        for key in keys[:-1]:
            # Handle array indices
            if key.isdigit():
                current = current[int(key)]
            else:
                current = current[key]

        # Set the final value
        final_key = keys[-1]
        if final_key.isdigit():
            current[int(final_key)] = new_value
        else:
            current[final_key] = new_value

        # Track modification
        self.modifications.append({
            'path': path,
            'old_value': self._get_field(content, path),
            'new_value': new_value,
            'timestamp': datetime.now().isoformat()
        })

        return modified_content

    def add_item(self, content: Dict, path: str, item: any) -> Dict:
        """
        Add an item to an array in the content.

        Args:
            content: Document content JSON
            path: Dot-notation path to array
            item: Item to add

        Returns:
            Modified content
        """
        modified_content = copy.deepcopy(content)
        keys = path.split('.')

        # Navigate to the array
        current = modified_content
        for key in keys:
            if key.isdigit():
                current = current[int(key)]
            else:
                current = current[key]

        # Add item
        if isinstance(current, list):
            current.append(item)
            self.modifications.append({
                'action': 'add',
                'path': path,
                'item': item,
                'timestamp': datetime.now().isoformat()
            })
        else:
            raise ValueError(f"Path {path} does not point to an array")

        return modified_content

    def remove_item(self, content: Dict, path: str, index: int) -> Dict:
        """
        Remove an item from an array.

        Args:
            content: Document content JSON
            path: Dot-notation path to array
            index: Index to remove

        Returns:
            Modified content
        """
        modified_content = copy.deepcopy(content)
        keys = path.split('.')

        # Navigate to the array
        current = modified_content
        for key in keys:
            if key.isdigit():
                current = current[int(key)]
            else:
                current = current[key]

        # Remove item
        if isinstance(current, list) and 0 <= index < len(current):
            removed_item = current.pop(index)
            self.modifications.append({
                'action': 'remove',
                'path': path,
                'index': index,
                'removed_item': removed_item,
                'timestamp': datetime.now().isoformat()
            })
        else:
            raise ValueError(f"Invalid array or index at {path}[{index}]")

        return modified_content

    def _get_field(self, content: Dict, path: str) -> any:
        """Get a field value by dot-notation path"""
        keys = path.split('.')
        current = content

        for key in keys:
            if key.isdigit():
                current = current[int(key)]
            else:
                current = current.get(key)
                if current is None:
                    return None

        return current

    # ═══════════════════════════════════════════════════════════════
    # SMART SUGGESTIONS
    # ═══════════════════════════════════════════════════════════════

    def suggest_adaptations(
        self,
        template: Dict,
        new_context: Dict
    ) -> List[Dict]:
        """
        Suggest adaptations based on new context.

        Args:
            template: Source template document
            new_context: New context (project, tags, requirements)

        Returns:
            List of suggested modifications
        """
        suggestions = []

        # Suggest title change
        if new_context.get('project_name'):
            suggestions.append({
                'type': 'title',
                'suggestion': f"{template['title']} - {new_context['project_name']}",
                'reason': 'Differentiate from template with project name',
                'priority': 'high'
            })

        # Suggest tag updates
        if new_context.get('tags'):
            new_tags = set(new_context['tags']) - set(template.get('tags', []))
            if new_tags:
                suggestions.append({
                    'type': 'tags',
                    'suggestion': list(set(template.get('tags', [])) | new_tags),
                    'reason': f'Add context-specific tags: {", ".join(new_tags)}',
                    'priority': 'medium'
                })

        # Suggest JIRA key updates
        if new_context.get('jira_key'):
            suggestions.append({
                'type': 'jira_keys',
                'suggestion': [new_context['jira_key']],
                'reason': 'Link to new JIRA ticket',
                'priority': 'high'
            })

        # Suggest content adaptations
        content = template.get('content_json', {})

        # Check for placeholder values
        placeholders = self._find_placeholders(content)
        if placeholders:
            suggestions.append({
                'type': 'placeholders',
                'paths': placeholders,
                'reason': 'Found placeholder values that should be updated',
                'priority': 'high'
            })

        return suggestions

    def _find_placeholders(self, obj, path='', placeholders=None) -> List[str]:
        """Recursively find placeholder values in JSON"""
        if placeholders is None:
            placeholders = []

        placeholder_keywords = ['TODO', 'TBD', 'FIXME', 'XXX', 'placeholder', 'example']

        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                self._find_placeholders(value, new_path, placeholders)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{path}.{i}"
                self._find_placeholders(item, new_path, placeholders)
        elif isinstance(obj, str):
            if any(keyword in obj.upper() for keyword in placeholder_keywords):
                placeholders.append(path)

        return placeholders

    # ═══════════════════════════════════════════════════════════════
    # ADAPTATION SUMMARY
    # ═══════════════════════════════════════════════════════════════

    def get_adaptation_summary(self) -> Dict:
        """
        Get summary of all modifications made.

        Returns:
            Summary dict with modification counts and details
        """
        return {
            'total_modifications': len(self.modifications),
            'modifications': self.modifications,
            'modification_types': self._count_modification_types(),
            'timestamp': datetime.now().isoformat()
        }

    def _count_modification_types(self) -> Dict:
        """Count modifications by type"""
        counts = {}
        for mod in self.modifications:
            action = mod.get('action', 'modify')
            counts[action] = counts.get(action, 0) + 1
        return counts

    def get_adaptation_notes(self, summary: bool = True) -> str:
        """
        Generate human-readable adaptation notes.

        Args:
            summary: If True, return brief summary. If False, detailed notes.

        Returns:
            Adaptation notes as markdown string
        """
        if not self.modifications:
            return "No modifications made."

        if summary:
            mod_count = len(self.modifications)
            types = self._count_modification_types()
            type_str = ", ".join(f"{count} {type}" for type, count in types.items())
            return f"Adapted with {mod_count} modifications: {type_str}"

        # Detailed notes
        notes = ["# Adaptation Details\n"]

        for i, mod in enumerate(self.modifications, 1):
            action = mod.get('action', 'modify')
            path = mod.get('path', 'unknown')

            if action == 'modify':
                notes.append(f"{i}. Modified `{path}`")
                notes.append(f"   - From: {mod.get('old_value')}")
                notes.append(f"   - To: {mod.get('new_value')}")
            elif action == 'add':
                notes.append(f"{i}. Added item to `{path}`")
                notes.append(f"   - Item: {mod.get('item')}")
            elif action == 'remove':
                notes.append(f"{i}. Removed item from `{path}[{mod.get('index')}]`")
                notes.append(f"   - Item: {mod.get('removed_item')}")

            notes.append("")

        return "\n".join(notes)

    # ═══════════════════════════════════════════════════════════════
    # LINEAGE TRACKING
    # ═══════════════════════════════════════════════════════════════

    def create_lineage_metadata(self, source_doc: Dict, adapted_doc: Dict) -> Dict:
        """
        Create metadata about document lineage.

        Args:
            source_doc: Original template document
            adapted_doc: New adapted document

        Returns:
            Lineage metadata
        """
        return {
            'source_document_id': source_doc.get('id'),
            'source_title': source_doc.get('title'),
            'source_version': source_doc.get('current_version'),
            'adapted_at': datetime.now().isoformat(),
            'adaptation_notes': self.get_adaptation_notes(summary=True),
            'modification_count': len(self.modifications),
            'preserved_structure': self._calculate_structure_similarity(
                source_doc.get('content_json', {}),
                adapted_doc.get('content_json', {})
            )
        }

    def _calculate_structure_similarity(self, source: Dict, adapted: Dict) -> float:
        """Calculate how much of the original structure was preserved"""
        source_keys = self._get_all_keys(source)
        adapted_keys = self._get_all_keys(adapted)

        if not source_keys:
            return 0.0

        preserved = len(source_keys & adapted_keys)
        return preserved / len(source_keys)

    def _get_all_keys(self, obj, keys=None) -> set:
        """Recursively get all keys in nested structure"""
        if keys is None:
            keys = set()

        if isinstance(obj, dict):
            keys.update(obj.keys())
            for value in obj.values():
                self._get_all_keys(value, keys)
        elif isinstance(obj, list):
            for item in obj:
                self._get_all_keys(item, keys)

        return keys


# ═══════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def adapt_document(
    source_doc: Dict,
    new_title: str,
    modifications: List[Tuple[str, any]],
    new_context: Optional[Dict] = None
) -> Tuple[Dict, Dict]:
    """
    Convenience function to adapt a document.

    Args:
        source_doc: Source document to adapt
        new_title: Title for adapted document
        modifications: List of (path, value) tuples
        new_context: Optional context for suggestions

    Returns:
        Tuple of (adapted_document, lineage_metadata)
    """
    adapter = DocumentAdapter()

    # Load template
    template = adapter.load_template(source_doc)

    # Apply modifications
    adapted_content = template.get('content_json', {})
    for path, value in modifications:
        adapted_content = adapter.modify_field(adapted_content, path, value)

    # Create adapted document
    adapted_doc = {
        'title': new_title,
        'content_json': adapted_content,
        'project_id': template.get('project_id'),
        'doc_type': template.get('doc_type'),
        'tags': template.get('tags', []),
        'jira_keys': new_context.get('jira_keys', []) if new_context else [],
    }

    # Get lineage metadata
    adapted_doc['content_json'] = adapted_content
    lineage = adapter.create_lineage_metadata(source_doc, adapted_doc)

    return adapted_doc, lineage
