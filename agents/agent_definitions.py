"""
BA&QA Intelligence Platform — Agent Definitions
Tüm agent'lar: BA, TC, Design Compliance
"""
from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.anthropic import Claude


def create_model(api_key: str, model_id: str = "gemini-2.5-flash"):
    """Create a model instance based on the model ID."""
    if model_id.startswith("claude-"):
        return Claude(id=model_id, api_key=api_key)
    else:
        return Gemini(id=model_id, api_key=api_key)


# ─────────────────────────────────────────────
# BA (İş Analizi) Agent'ları
# ─────────────────────────────────────────────

def create_ba_agents(api_key: str):
    model = create_model(api_key)

    agent1 = Agent(name="JIRA Tarayıcı", model=model,
        description="JIRA'dan iş analizi task'larını tarar ve Google Docs linklerini tespit eder.",
        instructions=["Sen bir JIRA task tarayıcısın.", "Task bilgilerini analiz et ve özetle."])

    agent2 = Agent(name="Doküman Okuyucu", model=model,
        description="Google Docs'tan çekilen BA dokümanını okur ve yapısını analiz eder.",
        instructions=["Sen bir iş analizi dokümanı okuyucususun.", "Dokümanın yapısını analiz et."])

    agent3 = Agent(name="Kalite Değerlendirici", model=model,
        description="İş analizi dokümanını 9 kriter üzerinden detaylı değerlendirir.",
        instructions=[
            "Sen son derece deneyimli bir iş analizi kalite kontrol uzmanısın.",
            "ÖNEMLI: Bu bir İŞ ANALİZİ dokümanıdır, TEKNİK TASARIM değil.",
            "PUANLAMA: Varsayılan 5/10. 8+ = MÜKEMMEL. Eksik modül = MAX 3/10.",
            "Belirsiz ifadeler her biri 0.5 puan düşürür.",
            "Genel puan = 9 kriter ortalaması × 100/90. Geçme: 60+.",
            "TÜM çıktılar TÜRKÇE. Sadece JSON döndür.",
        ])

    agent4 = Agent(name="Raporcu", model=model,
        description="Değerlendirme sonuçlarını JIRA comment formatına dönüştürür.",
        instructions=["Değerlendirme sonuçlarını okunabilir rapor formatına dönüştür.", "Emoji kullan. TÜRKÇE yaz."])

    return agent1, agent2, agent3, agent4


# ─────────────────────────────────────────────
# TC (Test Case) Agent'ları
# ─────────────────────────────────────────────

def create_tc_agents(api_key: str):
    model = create_model(api_key)

    agent1 = Agent(name="JIRA & Sheet Tarayıcı", model=model,
        description="JIRA'dan TC task'larını tarar, linked BA task'ı bulur.",
        instructions=["Sen bir JIRA task ve Google Sheets tarayıcısın."])

    agent2 = Agent(name="Doküman Birleştirici", model=model,
        description="BA dokümanı ve TC sheet'lerini birleştirip analiz için hazırlar.",
        instructions=["BA ve TC dokümanlarını birleştir, metrikleri çıkar."])

    agent3 = Agent(name="TC Kalite Değerlendirici", model=model,
        description="Test case dokümanını 8 kriter üzerinden detaylı değerlendirir.",
        instructions=[
            "Sen son derece deneyimli bir test mühendisliği kalite kontrol uzmanısın.",
            "Loodos standart şablonu (23 sütun) beklenir.",
            "PUANLAMA: Varsayılan 5/10. 8+ = MÜKEMMEL.",
            "Genel puan = 8 kriter ortalaması × 100/80. Geçme: 60+.",
            "Sadece happy path varsa edge_cases MAX 4/10.",
            "TÜM çıktılar TÜRKÇE. Sadece JSON döndür.",
        ])

    agent4 = Agent(name="TC Raporcu", model=model,
        description="TC değerlendirme sonuçlarını rapor formatına dönüştürür.",
        instructions=["TC sonuçlarını okunabilir rapor formatına dönüştür.", "Emoji kullan. TÜRKÇE yaz."])

    return agent1, agent2, agent3, agent4


# ─────────────────────────────────────────────
# Design Compliance Agent'ları
# ─────────────────────────────────────────────

def create_design_agents(api_key: str, model: str = "gemini-2.5-flash"):
    """Create design compliance agents with specified model (Gemini or Claude)."""
    vision_model = create_model(api_key, model)

    requirements_agent = Agent(
        name="Requirements Extractor", model=vision_model,
        instructions=[
            "Sen bir İş Analizi uzmanısın. Görevin, verilen iş analizi dokümanından "
            "gereksinimleri yapılandırılmış biçimde çıkarmak.",
            "",
            "Dokümanı analiz ederken şunları yap:",
            "1. Her fonksiyonel gereksinimi tanımla ve benzersiz bir ID ver (REQ-001, REQ-002, ...)",
            "2. Her gereksinim için: açıklama, kabul kriterleri, UI bileşeni beklentisi çıkar",
            "3. UI metinleri/label'ları varsa aynen koru (buton adları, başlıklar, placeholder'lar)",
            "4. İş kurallarını ve doğrulama koşullarını listele",
            "5. Kullanıcı rolleri ve yetkilendirme gereksinimlerini belirt",
            "",
            "Çıktını şu formatta ver:",
            "## Gereksinim Listesi",
            "Her gereksinim için:",
            "- **ID**: REQ-XXX",
            "- **Açıklama**: ...",
            "- **Kabul Kriterleri**: ...",
            "- **Beklenen UI Bileşeni**: ...",
            "- **UI Metinleri**: ...",
            "- **İş Kuralları**: ...",
            "",
            "Türkçe cevap ver. Hiçbir gereksinimi atlama."
        ],
        markdown=True,
    )

    screen_agent = Agent(
        name="Screen Analyzer", model=vision_model,
        instructions=[
            "Sen bir UI/UX analiz uzmanısın. Görevin, verilen tasarım ekran görüntüsünü "
            "detaylı biçimde analiz etmek.",
            "",
            "Ekran görüntüsünü analiz ederken şunları yap:",
            "1. Ekrandaki TÜM UI bileşenlerini tespit et ve listele",
            "2. Her bileşenin üzerindeki metni/label'ı AYNEN yaz",
            "3. Sayfa yapısını ve navigasyon öğelerini tanımla",
            "4. Form alanlarının tipini belirt (text input, dropdown, checkbox, radio, vb.)",
            "5. Görünür iş kurallarını tespit et (zorunlu alan işaretleri, validasyon mesajları vb.)",
            "6. Kullanıcı akışı ve etkileşim kalıplarını değerlendir",
            "",
            "Türkçe cevap ver. Ekranda gördüğün HER ŞEYİ raporla."
        ],
        markdown=True,
    )

    compliance_agent = Agent(
        name="Compliance Checker", model=vision_model,
        instructions=[
            "Sen bir Kalite Güvence (QA) uzmanısın. Görevin, iş analizi gereksinimlerini "
            "tasarım ekranı analiziyle karşılaştırarak uyumluluk kontrolü yapmak.",
            "",
            "Karşılaştırma yaparken 4 ana kontrol gerçekleştir:",
            "1. Gereksinim ↔ Tasarım Eşleştirme (✅ UYUMLU / ⚠️ KISMİ / ❌ EKSİK)",
            "2. Eksik/Fazla Özellik Tespiti",
            "3. Acceptance Criteria Karşılaştırma",
            "4. UI Text/Label Doğrulama",
            "",
            "Ciddiyet seviyesi belirt: 🔴 KRİTİK / 🟡 ORTA / 🟢 DÜŞÜK",
            "Türkçe ve çok detaylı cevap ver."
        ],
        markdown=True,
    )

    report_agent = Agent(
        name="Report Generator", model=vision_model,
        instructions=[
            "Sen bir BA&QA raporlama uzmanısın. Görevin, uyumluluk kontrol sonuçlarını "
            "yapılandırılmış bir rapora dönüştürmek.",
            "",
            "RAPOR YAPISI (mutlaka bu sırayla):",
            "",
            "## 1️⃣ Gereksinim Eşleşme Matrisi",
            "| REQ ID | Gereksinim Açıklaması | Tasarımdaki Karşılığı | Durum | Notlar |",
            "|--------|----------------------|----------------------|-------|--------|",
            "| REQ-001 | ... | Ekran adı / Bileşen | ✅ UYUMLU / ⚠️ KISMİ / ❌ EKSİK | ... |",
            "",
            "Her gereksinim için bir satır ekle. Tasarımda hangi ekran/bileşende karşılandığını belirt.",
            "",
            "## 2️⃣ Eksik Kapsam Listesi",
            "BA'da tanımlı ancak tasarımda bulunamayan özellikler:",
            "",
            "| REQ ID | Eksik Özellik | Açıklama |",
            "|--------|--------------|----------|",
            "| REQ-XXX | ... | BA'da belirtilmiş ama tasarımda yok |",
            "",
            "## 3️⃣ Ciddiyet Bazlı Bulgular",
            "",
            "### 🔴 KRİTİK Bulgular",
            "| ID | Bulgu | Etkilenen Gereksinim | Açıklama |",
            "|----|-------|---------------------|----------|",
            "| C-1 | ... | REQ-XXX | Kritik seviye uyumsuzluk detayı |",
            "",
            "### 🟡 ORTA Bulgular",
            "| ID | Bulgu | Etkilenen Gereksinim | Açıklama |",
            "|----|-------|---------------------|----------|",
            "| M-1 | ... | REQ-XXX | Orta seviye uyumsuzluk detayı |",
            "",
            "### 🟢 DÜŞÜK Bulgular",
            "| ID | Bulgu | Etkilenen Gereksinim | Açıklama |",
            "|----|-------|---------------------|----------|",
            "| L-1 | ... | REQ-XXX | Düşük seviye uyumsuzluk detayı |",
            "",
            "ÖNEMLI:",
            "- Skorlama YAPMA, sadece uyumluluk durumunu raporla",
            "- Tüm tabloları Markdown formatında oluştur",
            "- Her bulguyu net ve anlaşılır yaz (JIRA ticket oluşturulabilir netlikte)",
            "- Raporu TÜRKÇE yaz",
            "- Tablolarda eksik satır bırakma, tüm gereksinimleri ve bulguları listele"
        ],
        markdown=True,
    )

    return requirements_agent, screen_agent, compliance_agent, report_agent
