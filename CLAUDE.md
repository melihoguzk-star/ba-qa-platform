# BA&QA Intelligence Platform

## Proje Amacı
Loodos BA/QA dokümanlarını Google Drive'dan otomatik çekip, parse edip,
semantik arama yapan Streamlit platformu.

## Tech Stack
- Python 3.11+, Streamlit (UI), SQLite, ChromaDB
- sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 (Türkçe)
- Google Drive API v3 + Google Docs API

## Yapı
- app.py → Streamlit ana uygulama
- document_manager.py → SQLite CRUD
- document_matching.py → TF-IDF hybrid arama
- chroma_manager.py → ChromaDB vektör DB
- drive_sync/ → [YENİ] Google Drive entegrasyon modülü

## Komutlar
- Çalıştır: streamlit run app.py
- Test: python -m pytest tests/
- Pip: pip install --break-system-packages

## Drive'daki BA Doküman Şablonu
Google Docs formatında, şu yapıda:
- Versiyon Tablosu (Tarih | Yazar | Açıklama | Versiyon)
- 1.1 Amaç → proje açıklaması
- 2.1 Kapsam → iş akış diyagramı, Figma linkleri
- 3.1 Fonksiyonel Analiz → ekran bazlı:
  - İşlem Akışı Tablosu (İşlem | No | Akış | Tasarım)
  - Kabul Kriteri Tablosu (No | Kabul Kriteri)

## Kurallar
- Kod ve değişken isimleri İngilizce
- Her modül için test yaz
- Streamlit'te session_state kullan
- Incremental sync destekle (modifiedTime takibi)
