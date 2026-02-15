# Contributing to BA&QA Intelligence Platform

Katkıda bulunduğunuz için teşekkürler! 🎉

## 🚀 Development Setup

### 1. Repository'yi Clone Edin

```bash
git clone https://github.com/melihoguzk-star/ba-qa-platform.git
cd ba-qa-platform
```

### 2. Virtual Environment Oluşturun

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate  # Windows
```

### 3. Dependencies Yükleyin

```bash
# Ana dependencies
pip install -r requirements.txt

# Test dependencies
pip install -r requirements-test.txt

# Development tools (opsiyonel)
pip install black flake8 isort mypy pre-commit
```

### 4. Pre-commit Hooks Kurun (Önerilen)

```bash
pre-commit install
```

Bu, her commit öncesinde otomatik olarak:
- Code formatting (black)
- Import sorting (isort)
- Linting (flake8)
- Security checks (bandit)

## 🧪 Testing

### Testleri Çalıştırma

```bash
# Tüm testler
PYTHONPATH=. pytest

# Verbose output ile
PYTHONPATH=. pytest -v

# Coverage raporu ile
PYTHONPATH=. pytest --cov=data --cov=agents --cov=pipeline

# HTML coverage raporu
PYTHONPATH=. pytest --cov-report=html
open htmlcov/index.html
```

### Test Markers

```bash
# Sadece unit testler
PYTHONPATH=. pytest -m unit

# Sadece integration testler
PYTHONPATH=. pytest -m integration

# Database testlerini atla
PYTHONPATH=. pytest -m "not db"
```

### Yeni Test Yazma

Tests `tests/` dizininde organize edilmiştir:
- `tests/unit/` - Hızlı, izole unit testler
- `tests/integration/` - Bağımlılıkları olan integration testler
- `tests/conftest.py` - Shared fixtures

Test yazarken:
- Descriptive test isimleri kullanın: `test_feature_with_condition()`
- Arrange-Act-Assert pattern'ı takip edin
- Fixtures kullanın (test data için)
- Appropriate markers ekleyin (`@pytest.mark.unit`)

## 🎨 Code Style

### Formatting

```bash
# Black ile format
black .

# isort ile import sorting
isort .

# Sadece kontrol (değişiklik yapmadan)
black --check .
isort --check-only .
```

### Linting

```bash
# Flake8 ile lint
flake8 .

# MyPy ile type checking (opsiyonel)
mypy agents/ data/ pipeline/
```

### Code Style Kuralları

- **Line length**: 127 karakter max
- **Imports**: isort ile sorted
- **Formatting**: black ile otomatik
- **Docstrings**: Triple quotes (`"""..."""`)
- **Type hints**: Önerilen ama zorunlu değil

## 📝 Commit Guidelines

### Commit Message Format

```
<type>: <subject>

<body>

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Types:**
- `feat`: Yeni özellik
- `fix`: Bug fix
- `docs`: Dokümantasyon
- `test`: Test ekleme/düzeltme
- `refactor`: Refactoring
- `style`: Code style değişiklikleri
- `chore`: Build/config değişiklikleri

**Örnekler:**
```
feat: Add Document Library to sidebar navigation

- Added navigation button in tools section
- Routes to pages/10_Document_Library.py
```

```
test: Add comprehensive AI Client tests with API mocking

- 22 unit tests covering all API interactions
- Anthropic and Gemini API tests
- Key rotation tests
```

## 🔄 Pull Request Process

1. **Branch oluşturun**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Değişikliklerinizi commit edin**
   ```bash
   git add .
   git commit -m "feat: Add new feature"
   ```

3. **Testlerin geçtiğinden emin olun**
   ```bash
   PYTHONPATH=. pytest
   ```

4. **Push edin**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Pull Request açın**
   - Clear description yazın
   - İlgili issue'ları referans verin
   - Screenshots ekleyin (UI değişiklikleri için)

### PR Checklist

- [ ] Testler yazıldı ve geçiyor
- [ ] Code formatted (black, isort)
- [ ] Lint hataları yok (flake8)
- [ ] Dokümantasyon güncellendi
- [ ] CHANGELOG.md güncellendi (major changes için)

## 🏗️ CI/CD Pipeline

GitHub Actions otomatik olarak şunları çalıştırır:

### Test Job
- Python 3.11, 3.12, 3.13 üzerinde test
- pytest ile tüm testler
- Coverage raporu (Codecov'a upload)

### Lint Job
- flake8 syntax checks
- black formatting check
- isort import sorting check

### Security Job
- safety - dependency vulnerability scan
- bandit - code security scan

### Coverage Job
- Coverage raporu oluşturma
- GitHub summary'ye ekleme

## 🐛 Bug Reports

Bug bulduysanız, lütfen bir issue açın:

**Issue şablonu:**
```markdown
**Açıklama:**
[Bug'ın kısa açıklaması]

**Reproduce Adımları:**
1. ...
2. ...
3. ...

**Beklenen Davranış:**
[Ne olmasını bekliyordunuz]

**Gerçek Davranış:**
[Ne oldu]

**Ortam:**
- Python version: [ör. 3.12]
- OS: [ör. macOS 14.0]
- Browser: [ör. Chrome 120]

**Ekran Görüntüleri:**
[Varsa ekleyin]
```

## 💡 Feature Requests

Yeni özellik önerisi için:

1. Issue açın "Feature Request" label ile
2. Use case açıklayın
3. Alternatif çözümleri tartışın

## 📚 Documentation

Dokümantasyon güncellemeleri:
- README.md - Genel bilgiler
- ROADMAP.md - Gelecek planlar
- tests/README.md - Test documentation
- Inline docstrings - Function/class documentation

## 🙏 Code of Conduct

- Respectful ve professional olun
- Constructive feedback verin
- Farklı görüşlere açık olun
- Colaborative çalışın

## 📞 İletişim

Sorularınız için:
- GitHub Issues
- Pull Request discussions
- README'deki iletişim bilgileri

---

**Teşekkürler!** 🎉

Her katkı bu projeyi daha iyi hale getirir.
