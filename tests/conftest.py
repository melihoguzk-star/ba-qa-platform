"""
Pytest configuration and shared fixtures for BA-QA Platform tests.
"""
import io
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


# ─────────────────────────────────────────────
# DOCX Fixtures — Adım 5
# ─────────────────────────────────────────────

def _add_hyperlink_to_para(para, url: str, text: str):
    """python-docx ile paragraf içine hyperlink ekle."""
    from docx.oxml import OxmlElement
    part  = para.part
    r_id  = part.relate_to(
        url,
        'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',
        is_external=True,
    )
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(
        '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id', r_id
    )
    run_el = OxmlElement('w:r')
    t = OxmlElement('w:t')
    t.text = text
    run_el.append(t)
    hyperlink.append(run_el)
    para._element.append(hyperlink)


def _add_bullet_item(doc, text: str, level: int = 0) -> None:
    """Belirtilen level'da bullet list item ekle (numPr XML ile)."""
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    p = doc.add_paragraph(text)
    pPr = OxmlElement('w:pPr')
    numPr = OxmlElement('w:numPr')
    ilvl = OxmlElement('w:ilvl')
    ilvl.set(qn('w:val'), str(level))
    numId = OxmlElement('w:numId')
    numId.set(qn('w:val'), '1')
    numPr.append(ilvl)
    numPr.append(numId)
    pPr.append(numPr)
    p._element.insert(0, pPr)


@pytest.fixture(scope="session")
def sample_loodos_ba_docx() -> bytes:
    """
    Kahve Dünyası stilinde gerçekçi bir Loodos BA DOCX dosyası oluşturur.

    Yapı:
      H1: Proje Açıklaması   → platform/dil bilgisi
      H1: Proje Kapsamı      → kapsam metni
      H1: Mobil Uygulama Gereksinimleri
        H2: Splash
          H3: Açıklama        → açıklama paragrafı
          H3: Tasarım Dosyaları → Figma linki
          H3: İş Akışı        → L0/L1/L2 nested bullet + Lottie link
        H2: Login
          H3: Açıklama
          H3: İş Akışı        → L0/L1 bullet, bold run
          H3: OTP Akışı       → ayrı is_akisi

    Returns:
        bytes — .docx binary içeriği
    """
    from docx import Document

    doc = Document()

    # ── Proje Açıklaması ──────────────────────────────────────
    doc.add_heading('Proje Açıklaması', level=1)
    doc.add_paragraph('Bu projede amaç; Kahve Dünyası mobil uygulamasını geliştirmektir.')
    doc.add_paragraph('Platform Bilgisi: iOS | Android | Web')
    doc.add_paragraph('Dil Desteği: Türkçe, İngilizce')

    # ── Proje Kapsamı ─────────────────────────────────────────
    doc.add_heading('Proje Kapsamı', level=1)
    doc.add_paragraph('Mobil ve Web tarafında yapılan geliştirmeler kapsam dahilindedir.')

    # ── Mobil Uygulama Gereksinimleri ─────────────────────────
    doc.add_heading('Mobil Uygulama Gereksinimleri', level=1)

    # ── Splash ekranı ────────────────────────────────────────
    doc.add_heading('Splash', level=2)

    doc.add_heading('Açıklama', level=3)
    doc.add_paragraph('Uygulama başlangıç ekranıdır.')

    doc.add_heading('Tasarım Dosyaları', level=3)
    figma_url = 'https://figma.com/file/splash-design/KahveDunyasi'
    para = doc.add_paragraph('Figma: ')
    _add_hyperlink_to_para(para, figma_url, 'Splash Tasarımı')

    doc.add_heading('İş Akışı', level=3)
    lottie_url = 'https://app.lottiefiles.com/share/splash-animation'
    _add_bullet_item(doc, 'Kullanıcı uygulamayı açar; splash ekranı görüntülenir.', level=0)
    _add_bullet_item(doc, 'Kahve Dünyası logosu ve animasyon gösterilir.', level=1)
    para_lottie = doc.add_paragraph()
    para_lottie_content = 'Lottie animasyon dosyası: '
    _add_hyperlink_to_para(para_lottie, lottie_url, 'Lottie Linki')
    _add_bullet_item(doc, 'Al götür logosu gösterilir.', level=1)
    _add_bullet_item(doc, '2 saniye beklenir, ardından Login ekranına geçilir.', level=0)

    # ── Login ekranı ─────────────────────────────────────────
    doc.add_heading('Login', level=2)

    doc.add_heading('Açıklama', level=3)
    doc.add_paragraph('Kullanıcı telefon numarası ile sisteme giriş yapar.')

    doc.add_heading('İş Akışı', level=3)
    _add_bullet_item(doc, 'Kullanıcı telefon numarasını girer.', level=0)
    # Bold run ekle
    p_bold = doc.add_paragraph()
    run_norm = p_bold.add_run('Giriş Yap ')
    run_bold = p_bold.add_run('butonuna')
    run_bold.bold = True
    run_norm2 = p_bold.add_run(' tıklar.')
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    pPr = OxmlElement('w:pPr')
    numPr = OxmlElement('w:numPr')
    ilvl = OxmlElement('w:ilvl'); ilvl.set(qn('w:val'), '1')
    numId = OxmlElement('w:numId'); numId.set(qn('w:val'), '1')
    numPr.append(ilvl); numPr.append(numId); pPr.append(numPr)
    p_bold._element.insert(0, pPr)
    _add_bullet_item(doc, 'OTP doğrulama ekranına yönlendirilir.', level=0)

    doc.add_heading('OTP Akışı', level=3)
    _add_bullet_item(doc, 'Kullanıcıya 6 haneli OTP kodu SMS ile gönderilir.', level=0)
    _add_bullet_item(doc, 'Kod 3 dakika geçerlidir.', level=1)
    _add_bullet_item(doc, 'Hatalı giriş 3 kez yapılırsa hesap kilitlenir.', level=1)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


@pytest.fixture(scope="session")
def sample_loodos_ba_elements(sample_loodos_ba_docx) -> list:
    """
    sample_loodos_ba_docx'ten read_docx_structured() çıktısı döndürür.
    BADocxParser ve Orchestrator testlerinde kullanılabilir.
    """
    from pipeline.document_reader import read_docx_structured
    return read_docx_structured(sample_loodos_ba_docx)


@pytest.fixture(scope="session")
def sample_loodos_ba_parsed(sample_loodos_ba_elements) -> dict:
    """
    sample_loodos_ba_elements'ten BADocxParser().parse() çıktısı döndürür.
    """
    from pipeline.ba_docx_parser import BADocxParser
    return BADocxParser().parse(sample_loodos_ba_elements)
