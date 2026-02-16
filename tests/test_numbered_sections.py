"""
Test parser with numbered sections (like the user's document)
"""
from pipeline.document_parser_v2 import parse_text_to_json, HeadingBasedParser
import json

# Sample document with numbered sections (like user's format)
numbered_doc = """
5.3. Teknik & Data Gereksinimleri
• Wallet Entegrasyonu: Apple Wallet (PassKit) ve Google Wallet entegrasyonu.
• Widget & Live Activities: Kilit ekranı sayacı ve ana ekran widget desteği.
• Güvenlik: Cüzdan ve çek ekranlarında ekran görüntüsü almayı (Screenshot) engelleyen güvenlik katmanı.
• Haptic API: İşletim sistemi seviyesinde dokunmatik geri bildirim tetikleyicileri.

5.4. Kapsam Dışı
• Üçüncü parti anket sağlayıcılarının kendi iç arayüz tasarımları kapsam dışıdır.
• Gamification, leaderboard ekranları ayrıca değerlendirilecek.

5.5. Fonksiyon Listesi
• Taslak amaçlı paylaşılmıştır.
"""

print("🧪 Testing Numbered Section Parser\n")
print("=" * 70)

print("\n📝 Input (Numbered sections like '5.3. Section Name'):\n")
print(numbered_doc)

# Test heading detection
print("\n" + "=" * 70)
print("🔍 Line-by-Line Heading Detection:\n")

lines = numbered_doc.strip().split('\n')
for i, line in enumerate(lines, 1):
    line = line.strip()
    if not line:
        continue

    level = HeadingBasedParser._detect_heading_level(line)
    clean = HeadingBasedParser._clean_heading(line)

    if level > 0:
        print(f"{i}. HEADING L{level}: '{clean}'")
        print(f"   Original: '{line}'")
    elif line.startswith(('•', '-', '*')):
        print(f"{i}. BULLET: {line[:60]}...")
    else:
        print(f"{i}. TEXT: {line[:60]}...")

# Parse to structure
print("\n" + "=" * 70)
print("📊 Parsed Structure:\n")

structure = HeadingBasedParser.parse_text_to_structure(numbered_doc)

print(f"Total sections: {len(structure.get('sections', []))}\n")

for i, section in enumerate(structure.get('sections', []), 1):
    print(f"Section {i}: '{section['heading']}' (L{section['level']})")
    print(f"  Subsections: {len(section.get('subsections', []))}")
    print(f"  Items: {len(section.get('items', []))}")

    for j, subsec in enumerate(section.get('subsections', []), 1):
        print(f"    Subsection {j}: '{subsec['heading']}'")
        print(f"      Items: {len(subsec.get('items', []))}")

# Parse to BA
print("\n" + "=" * 70)
print("📄 Converted to BA JSON:\n")

ba_result = parse_text_to_json(numbered_doc, 'ba')

print(f"Keys: {list(ba_result.keys())}\n")

for key, value in ba_result.items():
    if isinstance(value, list) and len(value) > 0:
        print(f"✅ {key}: {len(value)} items")
        if key == "guvenlik_gereksinimleri":
            for item in value[:2]:
                print(f"   - {item.get('gereksinim', 'N/A')}")
    elif isinstance(value, list):
        print(f"⚠️  {key}: 0 items")

print("\n" + "=" * 70)
print("🎯 Expected Result:\n")
print("""
Should recognize:
✅ 5.3. Teknik & Data Gereksinimleri → heading
✅ 5.4. Kapsam Dışı → heading
✅ 5.5. Fonksiyon Listesi → heading
✅ Bullet points (•) → items under sections

Should parse into sections with their items.
""")

print("\n💡 Key Improvement:")
print("   Parser now handles numbered sections (5.3., 1.2., etc.)")
print("   No need for specific keywords!")
