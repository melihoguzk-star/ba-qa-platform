# Test Dosyaları

Bu klasör tüm test dosyalarını içerir.

## 📂 Klasör Yapısı

```
tests/
├── unit/               # Unit testler (pytest)
├── integration/        # Integration testler (pytest)
├── fixtures/          # Test fixtures
├── test_*.py          # Demo/manual test scripts
└── TEST_README.md     # Bu dosya
```

## 🧪 Test Çeşitleri

### 1. Pytest Testleri
- `unit/` - Unit testler
- `integration/` - Integration testler
- `conftest.py` - Pytest configuration

**Çalıştırma:**
```bash
# Tüm pytest testleri
pytest

# Sadece unit testler
pytest tests/unit/

# Sadece integration testler
pytest tests/integration/

# Verbose output
pytest -v

# Coverage ile
pytest --cov=pipeline --cov-report=html
```

### 2. Manuel Test Scripts
Root dizinindeki `test_*.py` dosyaları - manuel çalıştırılabilen demo scriptler

**Çalıştırma:**
```bash
# Proje root dizininden çalıştırın
python3 tests/test_document_reader.py
python3 tests/test_numbered_sections.py
python3 tests/test_heading_parser.py
```

## 📝 Mevcut Test Dosyaları

### Document Parser Testleri
- `test_heading_parser.py` - Başlık bazlı parser testleri
- `test_numbered_sections.py` - Numaralı bölüm testleri
- `test_parser_debug.py` - Parser debug testleri
- `test_both_parsers.py` - Rule-based ve AI parser karşılaştırması
- `test_rule_parser.py` - Rule-based parser testleri

### Document Reader Testleri
- `test_document_reader.py` - Word ve Google Drive okuma testleri

### Integration Testleri
- `test_import_merge.py` - Import & Merge workflow testleri
- `test_new_features.py` - Yeni özellik testleri

### OpenAPI Testleri
- `test_openapi_generator.py` - OpenAPI generator testleri

## ✨ Yeni Test Oluştururken

### 1. Pytest Test (Otomatik)
```python
# tests/unit/test_my_feature.py
import pytest
from pipeline.my_module import my_function

def test_my_function():
    """Test description"""
    result = my_function(input_data)
    assert result == expected_output

def test_my_function_error_handling():
    """Test error cases"""
    with pytest.raises(ValueError):
        my_function(invalid_input)
```

### 2. Manuel Test Script (Demo)
```python
# tests/test_my_feature.py
"""
Test My Feature - Manual test script

Demonstrates how the feature works
"""
from pipeline.my_module import my_function

def test_basic_usage():
    print("🧪 Testing Basic Usage")
    print("=" * 70)

    result = my_function(test_input)
    print(f"✅ Result: {result}")

    return result is not None

if __name__ == "__main__":
    print("Test My Feature")
    print("=" * 70)

    try:
        result = test_basic_usage()
        print(f"\n{'✅ PASS' if result else '❌ FAIL'}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
```

### 3. Dosya Konumu
- ✅ **Pytest testler:** `tests/unit/` veya `tests/integration/`
- ✅ **Manuel scriptler:** `tests/test_*.py`
- ❌ **Root dizin:** Test dosyası koymayın!

### 4. Import Yöntemi
Tüm testler proje root dizininden çalıştırıldığı için:

```python
# ✅ Doğru
from pipeline.document_parser import parse_text
from data.database import get_documents
from agents.ba_agent import generate_ba

# ❌ Yanlış
from ..pipeline.document_parser import parse_text  # Relative import
import sys; sys.path.append('..')  # Path manipulation
```

## 🎯 Test Best Practices

### 1. Test İsimlendirme
```python
# ✅ İyi
def test_parse_numbered_sections_with_bullets():
    """Test parser with numbered sections (5.3., 5.4.) and bullet points"""

# ❌ Kötü
def test1():
    """Test"""
```

### 2. Test Organizasyonu
```python
def test_feature():
    # Arrange - Hazırlık
    input_data = create_test_data()
    expected = expected_result()

    # Act - İşlem
    result = function_under_test(input_data)

    # Assert - Doğrulama
    assert result == expected
```

### 3. Assertions
```python
# ✅ Açıklayıcı assertions
assert len(result) == 3, f"Expected 3 items, got {len(result)}"
assert result['status'] == 'success', f"Expected success, got {result['status']}"

# ❌ Belirsiz assertions
assert result
assert x
```

### 4. Test Coverage
```python
# Test normal case
def test_function_success():
    result = function(valid_input)
    assert result is not None

# Test error cases
def test_function_invalid_input():
    with pytest.raises(ValueError):
        function(invalid_input)

# Test edge cases
def test_function_empty_input():
    result = function("")
    assert result == default_value
```

## 📊 Test Komutları

```bash
# Tüm testleri çalıştır
pytest

# Verbose output
pytest -v

# Sadece failed testleri göster
pytest --tb=short

# Sadece belirli bir test
pytest tests/unit/test_parser.py::test_numbered_sections

# Coverage raporu
pytest --cov=pipeline --cov-report=html
open htmlcov/index.html

# Parallel testing (hızlı)
pytest -n auto

# Stop at first failure
pytest -x

# Watch mode (test değişince otomatik çalıştır)
ptw  # pytest-watch

# Manuel test scriptler
python3 tests/test_document_reader.py
python3 tests/test_numbered_sections.py
```

## 🔍 Debugging

```bash
# Pytest debugging
pytest --pdb  # Drop into debugger on failure

# Print statements
pytest -s  # Show print() output

# Specific test with verbose
pytest -vv tests/unit/test_parser.py::test_function

# Manuel script debugging
python3 -m pdb tests/test_document_reader.py
```

## 📦 Test Dependencies

Requirements for testing:
```bash
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-xdist>=3.3.0  # Parallel testing
python-docx>=1.1.0
requests>=2.31.0
```

Install:
```bash
pip install -r requirements.txt
pip install pytest pytest-cov pytest-xdist
```

## 🎓 Örnek Test Senaryoları

### Parser Test
```python
def test_parse_numbered_sections():
    """Test parser with numbered sections like 5.3., 5.4."""
    doc = """
    5.3. Teknik Gereksinimler
    • Item 1
    • Item 2
    """
    result = parse_text_to_json(doc, 'ba')
    assert len(result['guvenlik_gereksinimleri']) > 0
```

### Integration Test
```python
def test_import_word_document(tmp_path):
    """Test full Word document import workflow"""
    # Create test .docx
    doc_path = tmp_path / "test.docx"
    create_test_document(doc_path)

    # Import
    with open(doc_path, 'rb') as f:
        content = f.read()

    text = read_docx(content)
    result = parse_text_to_json(text, 'ba')

    assert 'ekranlar' in result
    assert len(result['ekranlar']) > 0
```

## 📚 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Test Coverage](https://coverage.readthedocs.io/)

## 🚀 CI/CD

Tests çalıştırma GitHub Actions:
```yaml
- name: Run tests
  run: |
    pytest -v --cov=pipeline --cov-report=xml
```

## ❓ Sorular

Test yazımı ile ilgili sorularınız için:
- README.md kontrol edin
- Mevcut testlere bakın (examples)
- pytest documentation okuyun
