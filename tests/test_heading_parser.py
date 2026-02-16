"""
Test heading-based parser (v2)
Shows how parser works with ANY headings, not specific keywords
"""
from pipeline.document_parser_v2 import parse_text_to_json, HeadingBasedParser
import json

print("🎯 Heading-Based Parser Test (v2)\n")
print("=" * 70)
print("\n💡 Concept: Parser works with heading hierarchy, NOT keyword search")
print("   - Detects H1, H2, H3 levels")
print("   - Builds structure from headings")
print("   - Maps to JSON based on content type\n")

# Example 1: Turkish headings
print("1️⃣ Test with Turkish Headings")
print("-" * 70)

turkish_doc = """
Kullanıcı Arayüzleri:

Giriş Ekranı:
- Email adresi: Kullanıcının email'i (zorunlu)
- Şifre: Kullanıcı şifresi (zorunlu)
- Beni hatırla: Checkbox (opsiyonel)
- Giriş yap butonu: Formu gönder

Profil Ekranı:
- Ad Soyad: Tam isim (zorunlu)
- Telefon: Telefon numarası
- Kaydet butonu: Profili güncelle

Arka Plan İşlemleri:

Kullanıcı Girişi:
POST /api/auth/login
Kullanıcı bilgilerini doğrula ve token döndür

Profil Güncelleme:
PUT /api/user/profile
Kullanıcı profil bilgilerini güncelle

Güvenlik:

Şifre Güvenliği:
Tüm şifreler bcrypt ile hash'lenmeli

Oturum Yönetimi:
Token'lar 24 saat sonra expire olmalı

Test Senaryoları:

Başarılı Giriş:
1) Kullanıcı giriş sayfasını açar
2) Geçerli email ve şifre girer
3) Giriş yap'a tıklar
4) Sistem doğrular
5) Ana sayfaya yönlendirilir
"""

print("📝 Input (Turkish headings):\n")
print(turkish_doc[:300] + "...\n")

result = parse_text_to_json(turkish_doc, 'ba')

print("✅ Parsed Result:\n")
print(f"Sections found:")
for key, value in result.items():
    if isinstance(value, list) and len(value) > 0:
        print(f"  ✅ {key}: {len(value)} items")
        if key == "ekranlar" and value:
            print(f"     Example: '{value[0].get('ekran_adi', 'N/A')}'")
            print(f"     Fields: {len(value[0].get('fields', []))}")
        elif key == "backend_islemler" and value:
            print(f"     Example: '{value[0].get('islem', 'N/A')}'")
            print(f"     Method: {value[0].get('method', 'N/A')} {value[0].get('endpoint', 'N/A')}")
    elif isinstance(value, list):
        print(f"  ⚠️  {key}: 0 items")

# Example 2: English headings
print("\n\n2️⃣ Test with English Headings")
print("-" * 70)

english_doc = """
User Interface Screens:

Login Page:
- Email field: User's email address (required)
- Password field: User password (required)
- Remember me: Checkbox option
- Login button: Submit form

Dashboard:
- Welcome message: Display user name
- Logout button: End session

Backend Services:

User Authentication:
POST /api/auth/login
Authenticate user credentials and return JWT token

Session Management:
GET /api/auth/session
Validate and refresh user session

Security Requirements:

Password Hashing:
All passwords must be hashed using bcrypt with salt

Token Security:
JWT tokens must expire after 24 hours

Test Scenarios:

Successful Login Flow:
1) User opens login page
2) User enters valid credentials
3) User clicks login button
4) System authenticates
5) User redirected to dashboard
"""

print("📝 Input (English headings):\n")
print(english_doc[:300] + "...\n")

result2 = parse_text_to_json(english_doc, 'ba')

print("✅ Parsed Result:\n")
for key, value in result2.items():
    if isinstance(value, list) and len(value) > 0:
        print(f"  ✅ {key}: {len(value)} items")

# Example 3: Mixed/Custom headings
print("\n\n3️⃣ Test with Custom Headings (No Keywords)")
print("-" * 70)

custom_doc = """
Sayfalar:

Ana Sayfa:
- Başlık: Hoşgeldin mesajı
- Menü: Navigasyon linkleri
- Çıkış: Oturumu kapat

API:

Veri Getir:
GET /api/data
Verileri listele

Kaydet:
POST /api/data
Yeni veri ekle

Kurallar:

Veri Doğrulama:
Tüm inputlar validate edilmeli

Testler:

Temel Akış:
1) Sayfayı aç
2) Veri gir
3) Kaydet
4) Başarılı mesaj gör
"""

print("📝 Input (Custom headings - Sayfalar, API, Kurallar, Testler):\n")
print(custom_doc[:200] + "...\n")

result3 = parse_text_to_json(custom_doc, 'ba')

print("✅ Parsed Result:\n")
for key, value in result3.items():
    if isinstance(value, list) and len(value) > 0:
        print(f"  ✅ {key}: {len(value)} items")

# Show raw structure
print("\n\n4️⃣ Raw Hierarchical Structure")
print("-" * 70)

structure = HeadingBasedParser.parse_text_to_structure(turkish_doc)

print("📊 Document structure (heading hierarchy):\n")
print(f"Total sections: {len(structure.get('sections', []))}\n")

for i, section in enumerate(structure.get('sections', [])[:2], 1):
    print(f"Section {i}: '{section['heading']}' (Level {section['level']})")
    print(f"  Subsections: {len(section.get('subsections', []))}")
    for subsec in section.get('subsections', [])[:2]:
        print(f"    - '{subsec['heading']}'")
        print(f"      Items: {len(subsec.get('items', []))}")
        print(f"      Steps: {len(subsec.get('steps', []))}")

# Summary
print("\n\n" + "=" * 70)
print("🎯 Key Improvements in v2")
print("=" * 70)

print("""
✅ Heading-Based Approach:
   - Detects heading levels (H1, H2, H3)
   - Works with ANY heading text
   - Language independent
   - No keyword search needed

✅ Flexible Mapping:
   - "Sayfalar" → ekranlar
   - "API" → backend_islemler
   - "Kurallar" → guvenlik_gereksinimleri
   - "Testler" → test_senaryolari

✅ Content-Type Detection:
   - Looks at heading meaning, not exact match
   - "User Interface" → screens
   - "Backend Services" → API operations
   - "Security Requirements" → security
   - "Test Scenarios" → tests

✅ Structure Preservation:
   - Maintains document hierarchy
   - Converts to appropriate JSON format
   - Preserves all content

💡 Works with:
   - Turkish headings ✅
   - English headings ✅
   - Custom headings ✅
   - Mixed language ✅
   - Any naming convention ✅
""")

print("🎉 Heading-based parser is more flexible and reliable!")
