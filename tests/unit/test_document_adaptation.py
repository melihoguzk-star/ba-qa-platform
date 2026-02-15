"""
Tests for Document Adaptation Engine (Phase 3)
Tests template loading, content modification, and lineage tracking.
"""
import pytest
from pipeline.document_adaptation import DocumentAdapter, adapt_document


class TestTemplateLoading:
    """Test loading documents as templates"""

    def test_load_template_creates_copy(self):
        """Should create a deep copy of the document"""
        adapter = DocumentAdapter()

        source_doc = {
            'id': 1,
            'title': 'Original Document',
            'content_json': {'key': 'value'}
        }

        template = adapter.load_template(source_doc)

        # Should have template metadata
        assert template['_is_template'] is True
        assert template['_original_id'] == 1
        assert template['_original_title'] == 'Original Document'

        # Should be a copy
        template['title'] = 'Modified'
        assert source_doc['title'] == 'Original Document'

    def test_load_template_deep_copy_content(self):
        """Should deep copy nested content"""
        adapter = DocumentAdapter()

        source_doc = {
            'id': 1,
            'content_json': {'nested': {'data': 'value'}}
        }

        template = adapter.load_template(source_doc)

        # Modify template content
        template['content_json']['nested']['data'] = 'modified'

        # Original should be unchanged
        assert source_doc['content_json']['nested']['data'] == 'value'


class TestContentModifications:
    """Test modifying template content"""

    def test_modify_field_simple(self):
        """Should modify a simple field"""
        adapter = DocumentAdapter()

        content = {'title': 'Original Title'}
        modified = adapter.modify_field(content, 'title', 'New Title')

        assert modified['title'] == 'New Title'
        assert content['title'] == 'Original Title'  # Original unchanged

    def test_modify_field_nested(self):
        """Should modify nested fields"""
        adapter = DocumentAdapter()

        content = {'data': {'nested': {'value': 'old'}}}
        modified = adapter.modify_field(content, 'data.nested.value', 'new')

        assert modified['data']['nested']['value'] == 'new'

    def test_modify_field_array_index(self):
        """Should modify array elements by index"""
        adapter = DocumentAdapter()

        content = {'items': ['a', 'b', 'c']}
        modified = adapter.modify_field(content, 'items.1', 'modified')

        assert modified['items'][1] == 'modified'
        assert modified['items'][0] == 'a'
        assert modified['items'][2] == 'c'

    def test_modify_field_tracks_changes(self):
        """Should track modifications"""
        adapter = DocumentAdapter()

        content = {'key': 'value'}
        adapter.modify_field(content, 'key', 'new_value')

        assert len(adapter.modifications) == 1
        assert adapter.modifications[0]['path'] == 'key'
        assert adapter.modifications[0]['old_value'] == 'value'
        assert adapter.modifications[0]['new_value'] == 'new_value'

    def test_add_item_to_array(self):
        """Should add item to array"""
        adapter = DocumentAdapter()

        content = {'items': ['a', 'b']}
        modified = adapter.add_item(content, 'items', 'c')

        assert modified['items'] == ['a', 'b', 'c']
        assert len(adapter.modifications) == 1
        assert adapter.modifications[0]['action'] == 'add'

    def test_add_item_to_non_array_fails(self):
        """Should raise error when adding to non-array"""
        adapter = DocumentAdapter()

        content = {'value': 'not_array'}

        with pytest.raises(ValueError):
            adapter.add_item(content, 'value', 'item')

    def test_remove_item_from_array(self):
        """Should remove item from array"""
        adapter = DocumentAdapter()

        content = {'items': ['a', 'b', 'c']}
        modified = adapter.remove_item(content, 'items', 1)

        assert modified['items'] == ['a', 'c']
        assert len(adapter.modifications) == 1
        assert adapter.modifications[0]['action'] == 'remove'
        assert adapter.modifications[0]['removed_item'] == 'b'

    def test_remove_item_invalid_index(self):
        """Should raise error for invalid index"""
        adapter = DocumentAdapter()

        content = {'items': ['a', 'b']}

        with pytest.raises(ValueError):
            adapter.remove_item(content, 'items', 5)


class TestSmartSuggestions:
    """Test adaptation suggestions"""

    def test_suggest_title_change(self):
        """Should suggest title with project name"""
        adapter = DocumentAdapter()

        template = {'title': 'User Login', 'tags': []}
        context = {'project_name': 'E-Commerce'}

        suggestions = adapter.suggest_adaptations(template, context)

        title_suggestions = [s for s in suggestions if s['type'] == 'title']
        assert len(title_suggestions) == 1
        assert 'E-Commerce' in title_suggestions[0]['suggestion']

    def test_suggest_tag_additions(self):
        """Should suggest adding new tags"""
        adapter = DocumentAdapter()

        template = {'title': 'Doc', 'tags': ['auth']}
        context = {'tags': ['auth', 'security', 'login']}

        suggestions = adapter.suggest_adaptations(template, context)

        tag_suggestions = [s for s in suggestions if s['type'] == 'tags']
        assert len(tag_suggestions) == 1
        suggested_tags = tag_suggestions[0]['suggestion']
        assert 'security' in suggested_tags
        assert 'login' in suggested_tags

    def test_suggest_jira_key_update(self):
        """Should suggest JIRA key update"""
        adapter = DocumentAdapter()

        template = {'title': 'Doc', 'tags': []}
        context = {'jira_key': 'PROJ-123'}

        suggestions = adapter.suggest_adaptations(template, context)

        jira_suggestions = [s for s in suggestions if s['type'] == 'jira_keys']
        assert len(jira_suggestions) == 1
        assert jira_suggestions[0]['suggestion'] == ['PROJ-123']

    def test_find_placeholders(self):
        """Should find placeholder values"""
        adapter = DocumentAdapter()

        template = {
            'title': 'Doc',
            'tags': [],
            'content_json': {
                'description': 'TODO: Add description',
                'value': 'This is a placeholder text'
            }
        }

        suggestions = adapter.suggest_adaptations(template, {})

        placeholder_suggestions = [s for s in suggestions if s['type'] == 'placeholders']
        assert len(placeholder_suggestions) == 1
        assert len(placeholder_suggestions[0]['paths']) >= 1


class TestAdaptationSummary:
    """Test adaptation tracking and summaries"""

    def test_get_adaptation_summary(self):
        """Should return summary of modifications"""
        adapter = DocumentAdapter()

        content = {'a': 1, 'b': 2}
        adapter.modify_field(content, 'a', 10)
        adapter.modify_field(content, 'b', 20)

        summary = adapter.get_adaptation_summary()

        assert summary['total_modifications'] == 2
        assert len(summary['modifications']) == 2

    def test_count_modification_types(self):
        """Should count modifications by type"""
        adapter = DocumentAdapter()

        content = {'items': ['a'], 'value': 1}
        adapter.modify_field(content, 'value', 2)
        adapter.add_item(content, 'items', 'b')
        adapter.remove_item(adapter.add_item(content, 'items', 'c'), 'items', 0)

        summary = adapter.get_adaptation_summary()
        types = summary['modification_types']

        assert 'modify' in types
        assert 'add' in types
        assert 'remove' in types

    def test_get_adaptation_notes_summary(self):
        """Should generate brief summary notes"""
        adapter = DocumentAdapter()

        content = {'key': 'value'}
        adapter.modify_field(content, 'key', 'new')

        notes = adapter.get_adaptation_notes(summary=True)

        assert '1 modifications' in notes.lower() or '1 modification' in notes.lower()
        assert 'modify' in notes.lower()

    def test_get_adaptation_notes_detailed(self):
        """Should generate detailed notes"""
        adapter = DocumentAdapter()

        content = {'key': 'value'}
        adapter.modify_field(content, 'key', 'new_value')

        notes = adapter.get_adaptation_notes(summary=False)

        assert 'Modified `key`' in notes
        assert 'From: value' in notes
        assert 'To: new_value' in notes

    def test_empty_modifications_notes(self):
        """Should handle no modifications"""
        adapter = DocumentAdapter()

        notes = adapter.get_adaptation_notes()
        assert 'No modifications' in notes


class TestLineageTracking:
    """Test document lineage metadata"""

    def test_create_lineage_metadata(self):
        """Should create lineage metadata"""
        adapter = DocumentAdapter()

        source_doc = {
            'id': 1,
            'title': 'Source Doc',
            'current_version': 2,
            'content_json': {'key': 'value'}
        }

        adapted_doc = {
            'title': 'Adapted Doc',
            'content_json': {'key': 'modified'}
        }

        adapter.modify_field(source_doc['content_json'], 'key', 'modified')

        lineage = adapter.create_lineage_metadata(source_doc, adapted_doc)

        assert lineage['source_document_id'] == 1
        assert lineage['source_title'] == 'Source Doc'
        assert lineage['source_version'] == 2
        assert lineage['modification_count'] == 1

    def test_calculate_structure_similarity(self):
        """Should calculate structure preservation"""
        adapter = DocumentAdapter()

        source = {'a': 1, 'b': 2, 'c': 3}
        adapted_full = {'a': 10, 'b': 20, 'c': 30}  # All keys preserved
        adapted_partial = {'a': 10, 'b': 20}  # One key removed

        # Dummy docs for metadata
        source_doc = {'content_json': source}
        adapted_full_doc = {'content_json': adapted_full}
        adapted_partial_doc = {'content_json': adapted_partial}

        lineage_full = adapter.create_lineage_metadata(source_doc, adapted_full_doc)
        lineage_partial = adapter.create_lineage_metadata(source_doc, adapted_partial_doc)

        assert lineage_full['preserved_structure'] == 1.0
        assert lineage_partial['preserved_structure'] == pytest.approx(2/3, abs=0.01)


class TestConvenienceFunction:
    """Test the convenience wrapper function"""

    def test_adapt_document_wrapper(self):
        """Should adapt document with convenience function"""
        source_doc = {
            'id': 1,
            'title': 'Source',
            'content_json': {'value': 'original'},
            'project_id': 1,
            'doc_type': 'ba',
            'tags': ['auth']
        }

        modifications = [('value', 'modified')]
        new_context = {'jira_keys': ['PROJ-123']}

        adapted, lineage = adapt_document(
            source_doc,
            'Adapted Document',
            modifications,
            new_context
        )

        assert adapted['title'] == 'Adapted Document'
        assert adapted['content_json']['value'] == 'modified'
        assert adapted['jira_keys'] == ['PROJ-123']
        assert lineage['source_document_id'] == 1

    def test_adapt_document_preserves_metadata(self):
        """Should preserve source metadata"""
        source_doc = {
            'id': 1,
            'title': 'Source',
            'content_json': {},
            'project_id': 5,
            'doc_type': 'tc',
            'tags': ['test', 'qa']
        }

        adapted, lineage = adapt_document(source_doc, 'New Doc', [])

        assert adapted['project_id'] == 5
        assert adapted['doc_type'] == 'tc'
        assert adapted['tags'] == ['test', 'qa']
