"""
FastAPI Configuration — Pydantic Settings
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # API Configuration
    api_title: str = "BA&QA Intelligence Platform API"
    api_version: str = "1.0.0"
    api_prefix: str = "/api/v1"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # CORS
    cors_origins: list[str] = ["http://localhost:5173"]

    # Database
    database_url: str = "sqlite:///data/baqa.db?mode=wal"

    # AI Models
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    default_claude_model: str = "claude-sonnet-4-20250514"
    default_gemini_model: str = "gemini-2.5-flash"

    # Jira Integration
    jira_base_url: str = "https://loodos.atlassian.net"
    jira_email: str = ""
    jira_api_token: str = ""

    # N8N Webhooks
    n8n_docs_proxy: str = "https://sh0tdie.app.n8n.cloud/webhook/google-docs-proxy"
    n8n_sheets_proxy: str = "https://sh0tdie.app.n8n.cloud/webhook/google-sheets-proxy"

    # Pipeline Configuration
    max_revisions: int = 3
    ba_pass_threshold: int = 60
    ta_pass_threshold: int = 60
    tc_pass_threshold: int = 60
    checkpoint_ttl_hours: int = 24
    chunk_output_token_limit: int = 16000
    qa_output_token_limit: int = 8000

    # Embedding
    embedding_model: str = "intfloat/multilingual-e5-base"
    vector_db_path: str = "data/chroma_db"

    # File Upload
    max_upload_size_mb: int = 50
    allowed_extensions: list[str] = [".pdf", ".docx", ".doc", ".txt"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields from .env that aren't defined in model


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()
