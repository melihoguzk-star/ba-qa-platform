"""
Smart Matching için örnek dokümanlar oluştur
"""

from data.database import (
    create_project,
    create_document,
    create_document_version,
    get_projects
)
import json

def create_sample_documents():
    """Smart matching için örnek dokümanlar oluştur."""

    print("\n" + "="*80)
    print("SMART MATCHING İÇİN ÖRNEK VERI OLUŞTURMA")
    print("="*80)

    # 1. Proje oluştur (eğer yoksa)
    print("\n1. Proje kontrolü...")
    projects = get_projects()

    mobile_banking_project = None
    for p in projects:
        if p['name'] == 'Mobile Banking':
            mobile_banking_project = p
            print(f"   ✅ 'Mobile Banking' projesi mevcut (ID: {p['id']})")
            break

    if not mobile_banking_project:
        project_id = create_project(
            name="Mobile Banking",
            description="Mobil bankacılık uygulaması",
            jira_project_key="MOB",
            tags=["mobile", "banking", "ios", "android"]
        )
        print(f"   ✅ 'Mobile Banking' projesi oluşturuldu (ID: {project_id})")
    else:
        project_id = mobile_banking_project['id']

    # 2. BA Dokümanları oluştur
    print("\n2. BA Dokümanları oluşturuluyor...")

    ba_docs = [
        {
            "title": "Mobile Banking - Authentication & Login",
            "description": "Kullanıcı girişi ve authentication özellikleri",
            "tags": ["login", "authentication", "security"],
            "jira_keys": ["MOB-100", "MOB-101"],
            "sections": [
                {
                    "section_type": "feature",
                    "section_title": "Login Screen",
                    "content_json": json.dumps({
                        "description": "Kullanıcı login ekranı. Email/telefon ve şifre ile giriş yapılır.",
                        "requirements": [
                            "Email veya telefon numarası ile giriş",
                            "Şifre doğrulama",
                            "Şifremi unuttum linki",
                            "Beni hatırla checkbox"
                        ]
                    }, ensure_ascii=False)
                },
                {
                    "section_type": "feature",
                    "section_title": "Biometric Authentication",
                    "content_json": json.dumps({
                        "description": "Biyometrik kimlik doğrulama özellikleri",
                        "requirements": [
                            "Face ID desteği (iOS)",
                            "Touch ID desteği (iOS)",
                            "Fingerprint desteği (Android)",
                            "Biyometrik enable/disable ayarı"
                        ],
                        "security": [
                            "Biyometrik data cihazda saklanır",
                            "3 başarısız denemeden sonra şifre iste",
                            "İlk kurulumda şifre ile doğrulama gerekli"
                        ]
                    }, ensure_ascii=False)
                },
                {
                    "section_type": "feature",
                    "section_title": "Two-Factor Authentication",
                    "content_json": json.dumps({
                        "description": "İki faktörlü kimlik doğrulama",
                        "requirements": [
                            "SMS ile OTP gönderimi",
                            "Email ile OTP gönderimi",
                            "OTP 6 haneli sayısal kod",
                            "5 dakika geçerlilik süresi"
                        ]
                    }, ensure_ascii=False)
                }
            ]
        },
        {
            "title": "Mobile Banking - Payment & Transfers",
            "description": "Ödeme ve para transferi özellikleri",
            "tags": ["payment", "transfer", "money"],
            "jira_keys": ["MOB-200", "MOB-201"],
            "sections": [
                {
                    "section_type": "feature",
                    "section_title": "Money Transfer",
                    "content_json": json.dumps({
                        "description": "Hesaplar arası ve EFT/FAST transfer",
                        "requirements": [
                            "Kendi hesaplarım arası transfer",
                            "Başka hesaba EFT",
                            "FAST transfer (7/24)",
                            "Transfer geçmişi görüntüleme"
                        ]
                    }, ensure_ascii=False)
                },
                {
                    "section_type": "feature",
                    "section_title": "QR Code Payment",
                    "content_json": json.dumps({
                        "description": "QR kod ile ödeme yapma",
                        "requirements": [
                            "QR kod okutma",
                            "Dinamik/statik QR kod desteği",
                            "Tutar girişi",
                            "Ödeme onayı"
                        ]
                    }, ensure_ascii=False)
                },
                {
                    "section_type": "feature",
                    "section_title": "Mobile Payment Methods",
                    "content_json": json.dumps({
                        "description": "Mobil ödeme yöntemleri entegrasyonu",
                        "requirements": [
                            "Apple Pay entegrasyonu",
                            "Google Pay entegrasyonu",
                            "Kart ekleme/silme",
                            "Varsayılan ödeme yöntemi seçimi"
                        ]
                    }, ensure_ascii=False)
                }
            ]
        },
        {
            "title": "Mobile Banking - Dashboard & Account Management",
            "description": "Ana sayfa ve hesap yönetimi",
            "tags": ["dashboard", "account", "overview"],
            "jira_keys": ["MOB-300"],
            "sections": [
                {
                    "section_type": "feature",
                    "section_title": "Dashboard",
                    "content_json": json.dumps({
                        "description": "Ana sayfa görseli ve özellikleri",
                        "requirements": [
                            "Hesap bakiyeleri özeti",
                            "Son işlemler listesi",
                            "Hızlı işlemler (transfer, ödeme)",
                            "Duyurular ve bildirimler"
                        ]
                    }, ensure_ascii=False)
                },
                {
                    "section_type": "feature",
                    "section_title": "Account Details",
                    "content_json": json.dumps({
                        "description": "Hesap detayları ve işlem geçmişi",
                        "requirements": [
                            "IBAN/hesap numarası görüntüleme",
                            "İşlem geçmişi filtreleme",
                            "Ekstre indirme (PDF)",
                            "Hesap hareketleri grafiği"
                        ]
                    }, ensure_ascii=False)
                },
                {
                    "section_type": "feature",
                    "section_title": "Profile & Settings",
                    "content_json": json.dumps({
                        "description": "Kullanıcı profili ve ayarlar",
                        "requirements": [
                            "Profil bilgileri düzenleme",
                            "Şifre değiştirme",
                            "Bildirim tercihleri",
                            "Güvenlik ayarları",
                            "Logout butonu"
                        ]
                    }, ensure_ascii=False)
                }
            ]
        }
    ]

    created_docs = []
    for doc_data in ba_docs:
        # Doküman oluştur
        content = {"sections": doc_data["sections"]}

        doc_id = create_document(
            project_id=project_id,
            doc_type="ba",
            title=doc_data["title"],
            content_json=content,
            description=doc_data["description"],
            tags=doc_data["tags"],
            jira_keys=doc_data["jira_keys"]
        )

        created_docs.append({
            "id": doc_id,
            "title": doc_data["title"]
        })

        print(f"   ✅ {doc_data['title']} (Doc ID: {doc_id})")

    # 3. TA Dokümanı oluştur
    print("\n3. TA Dokümanı oluşturuluyor...")

    ta_content = {
        "sections": [
            {
                "section_type": "architecture",
                "section_title": "Authentication Flow",
                "content_json": json.dumps({
                    "description": "Authentication akış mimarisi",
                    "components": [
                        "OAuth 2.0 authentication server",
                        "JWT token management",
                        "Biometric integration layer",
                        "Session management"
                    ],
                    "apis": [
                        "POST /api/auth/login",
                        "POST /api/auth/biometric",
                        "POST /api/auth/refresh-token",
                        "POST /api/auth/logout"
                    ]
                }, ensure_ascii=False)
            },
            {
                "section_type": "architecture",
                "section_title": "Payment Integration",
                "content_json": json.dumps({
                    "description": "Ödeme sistemleri entegrasyonu",
                    "components": [
                        "Payment gateway adapter",
                        "Apple Pay SDK integration",
                        "Google Pay SDK integration",
                        "QR code scanner library"
                    ]
                }, ensure_ascii=False)
            }
        ]
    }

    ta_doc_id = create_document(
        project_id=project_id,
        doc_type="ta",
        title="Mobile Banking - Technical Architecture",
        content_json=ta_content,
        description="Mobil bankacılık teknik mimarisi",
        tags=["architecture", "api", "security"],
        jira_keys=["MOB-400"]
    )

    print(f"   ✅ Mobile Banking - Technical Architecture (Doc ID: {ta_doc_id})")

    # 4. TC Dokümanı oluştur
    print("\n4. TC Dokümanı oluşturuluyor...")

    tc_content = {
        "sections": [
            {
                "section_type": "test_case",
                "section_title": "Login Test Cases",
                "content_json": json.dumps({
                    "test_cases": [
                        {
                            "id": "TC-001",
                            "title": "Başarılı login",
                            "steps": [
                                "Email ve şifre gir",
                                "Login butonuna tıkla"
                            ],
                            "expected": "Dashboard ekranı açılır"
                        },
                        {
                            "id": "TC-002",
                            "title": "Yanlış şifre ile login",
                            "steps": [
                                "Email gir",
                                "Yanlış şifre gir",
                                "Login butonuna tıkla"
                            ],
                            "expected": "Hata mesajı gösterilir"
                        }
                    ]
                }, ensure_ascii=False)
            },
            {
                "section_type": "test_case",
                "section_title": "Biometric Authentication Test Cases",
                "content_json": json.dumps({
                    "test_cases": [
                        {
                            "id": "TC-010",
                            "title": "Face ID ile başarılı login",
                            "steps": [
                                "Face ID aktif et",
                                "Uygulamayı aç",
                                "Face ID ile doğrula"
                            ],
                            "expected": "Dashboard ekranı açılır"
                        },
                        {
                            "id": "TC-011",
                            "title": "Touch ID ile başarılı login",
                            "steps": [
                                "Touch ID aktif et",
                                "Uygulamayı aç",
                                "Parmak izi ile doğrula"
                            ],
                            "expected": "Dashboard ekranı açılır"
                        }
                    ]
                }, ensure_ascii=False)
            }
        ]
    }

    tc_doc_id = create_document(
        project_id=project_id,
        doc_type="tc",
        title="Mobile Banking - Login & Authentication Test Cases",
        content_json=tc_content,
        description="Login ve authentication test senaryoları",
        tags=["test", "login", "authentication"],
        jira_keys=["MOB-500"]
    )

    print(f"   ✅ Mobile Banking - Login & Authentication Test Cases (Doc ID: {tc_doc_id})")

    print("\n" + "="*80)
    print("✅ ÖRNEK VERİLER OLUŞTURULDU")
    print("="*80)
    print(f"\nToplam: {len(created_docs) + 2} doküman oluşturuldu")
    print("\nBA Dokümanları:")
    for doc in created_docs:
        print(f"  - {doc['title']}")
    print(f"\nTA Dokümanı:")
    print(f"  - Mobile Banking - Technical Architecture")
    print(f"\nTC Dokümanı:")
    print(f"  - Mobile Banking - Login & Authentication Test Cases")

    print("\n" + "="*80)
    print("SONRAKİ ADIM: ChromaDB İndexleme")
    print("="*80)
    print("\nDokümanları ChromaDB'ye indexlemek için:")
    print("1. Document Library sayfasına git")
    print("2. Veya aşağıdaki komutu çalıştır:")
    print("   python index_documents_to_chromadb.py")
    print("\n")


if __name__ == "__main__":
    create_sample_documents()
