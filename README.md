# 🧠 BA&QA Intelligence Platform

Birleşik BA değerlendirme, QA test analizi, design compliance ve JIRA otomasyon platformu.  
BA ve QA ekibinin tüm kalite süreçlerini tek çatı altında toplayan Streamlit dashboard.

## Modüller

| Sayfa | Açıklama |
|-------|----------|
| 📋 BA Değerlendirme | İş Analizi dokümanını 9 kriter üzerinden puanlar |
| 🧪 TC Değerlendirme | Test Case dokümanını 8 kriter üzerinden puanlar |
| 🎨 Design Compliance | Figma tasarım ↔ BA uyumluluk kontrolü |
| 📈 Raporlar | Trend analizi, geçmiş, CSV export |

## Kurulum

```bash
git clone <repo-url>
cd ba-qa-platform
pip install -r requirements.txt
```

## Secrets (.streamlit/secrets.toml)

```toml
GEMINI_API_KEY = "..."
JIRA_EMAIL = "..."
JIRA_API_TOKEN = "..."
```

## Çalıştırma

```bash
streamlit run app.py
```

## Tech Stack

- **Backend:** Python 3.11+ / Streamlit / Agno Framework
- **AI:** Gemini 2.5 Flash (1M context)
- **Entegrasyonlar:** JIRA REST API / Google Docs / Google Sheets / Figma
- **Data:** SQLite (lokal) / Google Sheets (paylaşılabilir)

## Mimari

`docs_architecture.html` dosyasını tarayıcıda aç.

---

**BA&QA Intelligence Platform v1.0** — Loodos BA&QA Ekibi
