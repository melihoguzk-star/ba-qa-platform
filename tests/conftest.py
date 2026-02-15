"""
Pytest configuration and shared fixtures for BA-QA Platform tests.
"""
import pytest
import sqlite3
import tempfile
import os
from pathlib import Path


# ─────────────────────────────────────────────
# Database Fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def temp_db():
    """Create a temporary test database."""
    # Create a temporary file for the database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')

    yield db_path

    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def db_connection(temp_db):
    """Create a database connection with schema initialized."""
    # Import here to avoid circular imports
    from data.database import init_db, get_db

    # Temporarily override DB_PATH
    import data.database as db_module
    original_db_path = db_module.DB_PATH
    db_module.DB_PATH = temp_db

    # Initialize database
    init_db()

    # Get connection
    conn = get_db()

    yield conn

    # Cleanup
    conn.close()
    db_module.DB_PATH = original_db_path


@pytest.fixture
def clean_db(db_connection):
    """Provide a clean database for each test."""
    yield db_connection

    # Rollback any changes after test
    db_connection.rollback()


# ─────────────────────────────────────────────
# Sample Data Fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def sample_project():
    """Sample project data."""
    return {
        "name": "Test Mobile App",
        "description": "Test project for mobile application",
        "jira_project_key": "TMA",
        "tags": ["mobile", "test", "ios"]
    }


@pytest.fixture
def sample_ba_document():
    """Sample BA document content."""
    return {
        "ekranlar": [
            {
                "ekran_adi": "Login Screen",
                "aciklama": "User authentication",
                "ui_elementleri": ["Email input", "Password input", "Login button"]
            },
            {
                "ekran_adi": "Dashboard",
                "aciklama": "Main dashboard",
                "ui_elementleri": ["Account balance", "Recent transactions"]
            }
        ],
        "backend_islemler": [
            {
                "islem_adi": "User Authentication",
                "endpoint": "/api/auth/login",
                "method": "POST"
            }
        ]
    }


@pytest.fixture
def sample_tc_document():
    """Sample TC document content."""
    return {
        "test_scenarios": [
            {
                "scenario_id": "TC001",
                "title": "Successful Login",
                "steps": [
                    "Open login page",
                    "Enter valid credentials",
                    "Click login button"
                ],
                "expected_result": "User is redirected to dashboard"
            }
        ]
    }


# ─────────────────────────────────────────────
# API Mocking Fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def mock_anthropic_response():
    """Mock Anthropic API response."""
    return {
        "json_output": {
            "ekranlar": [{"ekran_adi": "Test Screen"}],
            "backend_islemler": []
        },
        "stop_reason": "end_turn"
    }


@pytest.fixture
def mock_gemini_response():
    """Mock Gemini API response."""
    return {
        "json_output": {
            "genel_puan": 85.0,
            "gecti_mi": True,
            "eksikler": []
        },
        "stop_reason": "stop"
    }


# ─────────────────────────────────────────────
# Test Markers
# ─────────────────────────────────────────────

def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (slower, with dependencies)"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )
    config.addinivalue_line(
        "markers", "db: Tests that require database"
    )
    config.addinivalue_line(
        "markers", "api: Tests that require API calls"
    )
