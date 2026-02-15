"""
Unit tests for Document Repository functions (Phase 1).

Tests cover:
- Project CRUD operations
- Document CRUD operations
- Version management
- Document sections
- Statistics
"""
import pytest
import json
from datetime import datetime


# ─────────────────────────────────────────────
# Project Tests
# ─────────────────────────────────────────────

@pytest.mark.unit
@pytest.mark.db
class TestProjectOperations:
    """Test project CRUD operations."""

    def test_create_project(self, db_connection, sample_project):
        """Test creating a new project."""
        from data.database import create_project

        # Create project
        project_id = create_project(
            name=sample_project["name"],
            description=sample_project["description"],
            jira_project_key=sample_project["jira_project_key"],
            tags=sample_project["tags"]
        )

        # Verify
        assert project_id > 0

        # Check database
        row = db_connection.execute(
            "SELECT * FROM projects WHERE id = ?", (project_id,)
        ).fetchone()

        assert row is not None
        assert row["name"] == sample_project["name"]
        assert row["description"] == sample_project["description"]
        assert row["jira_project_key"] == sample_project["jira_project_key"]

        tags = json.loads(row["tags"])
        assert tags == sample_project["tags"]

    def test_create_project_duplicate_name(self, db_connection, sample_project):
        """Test creating project with duplicate name fails."""
        from data.database import create_project

        # Create first project
        create_project(name=sample_project["name"])

        # Try to create duplicate - should fail (UNIQUE constraint)
        with pytest.raises(Exception):
            create_project(name=sample_project["name"])

    def test_get_projects(self, db_connection, sample_project):
        """Test retrieving all projects."""
        from data.database import create_project, get_projects

        # Create multiple projects
        create_project(name="Project A", tags=["mobile"])
        create_project(name="Project B", tags=["web"])
        create_project(name="Project C", tags=["api"])

        # Get all projects
        projects = get_projects()

        assert len(projects) == 3
        assert all("tags" in p for p in projects)
        assert all(isinstance(p["tags"], list) for p in projects)

    def test_get_projects_with_search(self, db_connection):
        """Test searching projects by name/description."""
        from data.database import create_project, get_projects

        create_project(name="Mobile Banking App", description="iOS application")
        create_project(name="Web Portal", description="Customer portal")

        # Search by name
        results = get_projects(search="Mobile")
        assert len(results) == 1
        assert results[0]["name"] == "Mobile Banking App"

        # Search by description
        results = get_projects(search="portal")
        assert len(results) == 1
        assert results[0]["name"] == "Web Portal"

    def test_get_project_by_id(self, db_connection, sample_project):
        """Test retrieving a specific project."""
        from data.database import create_project, get_project_by_id

        # Create project
        project_id = create_project(**sample_project)

        # Retrieve
        project = get_project_by_id(project_id)

        assert project is not None
        assert project["id"] == project_id
        assert project["name"] == sample_project["name"]
        assert project["tags"] == sample_project["tags"]

    def test_get_project_by_id_not_found(self, db_connection):
        """Test retrieving non-existent project returns None."""
        from data.database import get_project_by_id

        result = get_project_by_id(99999)
        assert result is None


# ─────────────────────────────────────────────
# Document Tests
# ─────────────────────────────────────────────

@pytest.mark.unit
@pytest.mark.db
class TestDocumentOperations:
    """Test document CRUD operations."""

    def test_create_document(self, db_connection, sample_project, sample_ba_document):
        """Test creating a new document."""
        from data.database import create_project, create_document

        # Create project first
        project_id = create_project(**sample_project)

        # Create document
        doc_id = create_document(
            project_id=project_id,
            doc_type="ba",
            title="User Authentication Flow",
            content_json=sample_ba_document,
            description="BA for login feature",
            tags=["auth", "security"],
            jira_keys=["TMA-101"],
            created_by="test_user"
        )

        assert doc_id > 0

        # Verify in database
        row = db_connection.execute(
            "SELECT * FROM documents WHERE id = ?", (doc_id,)
        ).fetchone()

        assert row is not None
        assert row["project_id"] == project_id
        assert row["doc_type"] == "ba"
        assert row["title"] == "User Authentication Flow"
        assert row["current_version"] == 1
        assert row["status"] == "active"

    def test_create_document_creates_initial_version(self, db_connection, sample_project, sample_ba_document):
        """Test that creating document also creates version 1."""
        from data.database import create_project, create_document

        project_id = create_project(**sample_project)
        doc_id = create_document(
            project_id=project_id,
            doc_type="ba",
            title="Test Doc",
            content_json=sample_ba_document
        )

        # Check version was created
        version_row = db_connection.execute(
            "SELECT * FROM document_versions WHERE document_id = ? AND version_number = 1",
            (doc_id,)
        ).fetchone()

        assert version_row is not None
        assert version_row["change_summary"] == "Initial version"

    def test_get_documents_by_project(self, db_connection, sample_project, sample_ba_document):
        """Test filtering documents by project."""
        from data.database import create_project, create_document, get_documents

        # Create two projects
        project1 = create_project(name="Project 1")
        project2 = create_project(name="Project 2")

        # Create documents in each
        create_document(project1, "ba", "Doc 1", sample_ba_document)
        create_document(project1, "tc", "Doc 2", sample_ba_document)
        create_document(project2, "ba", "Doc 3", sample_ba_document)

        # Filter by project
        docs_p1 = get_documents(project_id=project1)
        docs_p2 = get_documents(project_id=project2)

        assert len(docs_p1) == 2
        assert len(docs_p2) == 1

    def test_get_documents_by_type(self, db_connection, sample_project, sample_ba_document, sample_tc_document):
        """Test filtering documents by type."""
        from data.database import create_project, create_document, get_documents

        project_id = create_project(**sample_project)

        create_document(project_id, "ba", "BA Doc 1", sample_ba_document)
        create_document(project_id, "ba", "BA Doc 2", sample_ba_document)
        create_document(project_id, "tc", "TC Doc 1", sample_tc_document)

        # Filter by type
        ba_docs = get_documents(doc_type="ba")
        tc_docs = get_documents(doc_type="tc")

        assert len(ba_docs) == 2
        assert len(tc_docs) == 1
        assert all(d["doc_type"] == "ba" for d in ba_docs)

    def test_get_documents_with_search(self, db_connection, sample_project, sample_ba_document):
        """Test searching documents by title/description."""
        from data.database import create_project, create_document, get_documents

        project_id = create_project(**sample_project)

        create_document(project_id, "ba", "Login Feature", sample_ba_document, description="User authentication")
        create_document(project_id, "ba", "Dashboard", sample_ba_document, description="Main screen")

        # Search by title
        results = get_documents(search="Login")
        assert len(results) == 1
        assert results[0]["title"] == "Login Feature"

        # Search by description
        results = get_documents(search="authentication")
        assert len(results) == 1

    def test_update_document(self, db_connection, sample_project, sample_ba_document):
        """Test updating document metadata."""
        from data.database import create_project, create_document, update_document, get_document_by_id

        project_id = create_project(**sample_project)
        doc_id = create_document(project_id, "ba", "Original Title", sample_ba_document)

        # Update
        update_document(
            doc_id,
            title="Updated Title",
            description="New description",
            tags=["new", "tags"],
            status="archived"
        )

        # Verify
        doc = get_document_by_id(doc_id)
        assert doc["title"] == "Updated Title"
        assert doc["description"] == "New description"
        assert doc["tags"] == ["new", "tags"]
        assert doc["status"] == "archived"


# ─────────────────────────────────────────────
# Version Management Tests
# ─────────────────────────────────────────────

@pytest.mark.unit
@pytest.mark.db
class TestVersionManagement:
    """Test document version control."""

    def test_create_document_version(self, db_connection, sample_project, sample_ba_document):
        """Test creating a new version."""
        from data.database import create_project, create_document, create_document_version, get_document_by_id

        project_id = create_project(**sample_project)
        doc_id = create_document(project_id, "ba", "Test Doc", sample_ba_document)

        # Create version 2
        updated_content = sample_ba_document.copy()
        updated_content["ekranlar"].append({"ekran_adi": "New Screen"})

        version_id = create_document_version(
            doc_id=doc_id,
            content_json=updated_content,
            change_summary="Added new screen",
            created_by="test_user"
        )

        assert version_id > 0

        # Check document version updated
        doc = get_document_by_id(doc_id)
        assert doc["current_version"] == 2

    def test_get_document_versions(self, db_connection, sample_project, sample_ba_document):
        """Test retrieving all versions."""
        from data.database import (
            create_project, create_document, create_document_version, get_document_versions
        )

        project_id = create_project(**sample_project)
        doc_id = create_document(project_id, "ba", "Test Doc", sample_ba_document)

        # Create multiple versions
        create_document_version(doc_id, {"v": 2}, "Version 2")
        create_document_version(doc_id, {"v": 3}, "Version 3")

        # Get all versions
        versions = get_document_versions(doc_id)

        assert len(versions) == 3  # v1 (initial) + v2 + v3
        assert versions[0]["version_number"] == 3  # Most recent first
        assert versions[1]["version_number"] == 2
        assert versions[2]["version_number"] == 1

    def test_get_latest_version(self, db_connection, sample_project, sample_ba_document):
        """Test retrieving latest version."""
        from data.database import (
            create_project, create_document, create_document_version, get_latest_version
        )

        project_id = create_project(**sample_project)
        doc_id = create_document(project_id, "ba", "Test Doc", sample_ba_document)

        create_document_version(doc_id, {"v": 2}, "Version 2")
        create_document_version(doc_id, {"v": 3}, "Version 3")

        # Get latest
        latest = get_latest_version(doc_id)

        assert latest is not None
        assert latest["version_number"] == 3
        assert latest["content_json"] == {"v": 3}


# ─────────────────────────────────────────────
# Statistics Tests
# ─────────────────────────────────────────────

@pytest.mark.unit
@pytest.mark.db
class TestDocumentStats:
    """Test document repository statistics."""

    def test_get_document_stats(self, db_connection, sample_project, sample_ba_document, sample_tc_document):
        """Test retrieving document statistics."""
        from data.database import create_project, create_document, get_document_stats

        # Create test data
        p1 = create_project(name="Project 1")
        p2 = create_project(name="Project 2")

        create_document(p1, "ba", "BA Doc 1", sample_ba_document)
        create_document(p1, "ba", "BA Doc 2", sample_ba_document)
        create_document(p1, "tc", "TC Doc 1", sample_tc_document)
        create_document(p2, "ba", "BA Doc 3", sample_ba_document)

        # Get stats
        stats = get_document_stats()

        assert stats["total_projects"] == 2
        assert stats["total_documents"] == 4

        # Check by_type
        ba_count = next((s["c"] for s in stats["by_type"] if s["doc_type"] == "ba"), 0)
        tc_count = next((s["c"] for s in stats["by_type"] if s["doc_type"] == "tc"), 0)

        assert ba_count == 3
        assert tc_count == 1

    def test_get_document_stats_empty_db(self, db_connection):
        """Test stats with empty database."""
        from data.database import get_document_stats

        stats = get_document_stats()

        assert stats["total_projects"] == 0
        assert stats["total_documents"] == 0
        assert stats["by_type"] == []
