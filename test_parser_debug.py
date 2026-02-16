"""
Debug heading-based parser to see what's happening
"""
from pipeline.document_parser_v2 import HeadingBasedParser
import json

# Simple test case
simple_doc = """
Kullanıcı Arayüzleri:

Giriş Ekranı:
- Email: Kullanıcı email'i (zorunlu)
- Şifre: Şifre alanı (zorunlu)

Backend:

User Login:
POST /api/auth/login
Kullanıcı girişi yapar
"""

print("🔍 Debug: Heading Detection\n")
print("=" * 70)
print("\nInput Document:")
print(simple_doc)
print("\n" + "=" * 70)

# Test each line
print("\n📊 Line-by-Line Analysis:\n")
lines = simple_doc.strip().split('\n')

for i, line in enumerate(lines, 1):
    line = line.strip()
    if not line:
        print(f"{i:2d}. [EMPTY LINE]")
        continue

    level = HeadingBasedParser._detect_heading_level(line)

    if level > 0:
        print(f"{i:2d}. HEADING L{level}: '{line}'")
    elif line.startswith(('-', '•', '*')):
        print(f"{i:2d}. LIST ITEM:  '{line}'")
    else:
        print(f"{i:2d}. TEXT:       '{line}'")

# Parse structure
print("\n" + "=" * 70)
print("\n📊 Parsed Structure:\n")

structure = HeadingBasedParser.parse_text_to_structure(simple_doc)
print(json.dumps(structure, indent=2, ensure_ascii=False))

# Convert to BA
print("\n" + "=" * 70)
print("\n📄 Final BA JSON:\n")

ba_result = HeadingBasedParser.structure_to_ba(structure)
print(json.dumps(ba_result, indent=2, ensure_ascii=False))

# Analysis
print("\n" + "=" * 70)
print("\n🔍 Analysis:\n")

total_sections = len(structure.get('sections', []))
print(f"Total sections: {total_sections}")

for i, section in enumerate(structure.get('sections', []), 1):
    print(f"\nSection {i}:")
    print(f"  Heading: '{section['heading']}'")
    print(f"  Level: {section['level']}")
    print(f"  Subsections: {len(section.get('subsections', []))}")
    print(f"  Content: '{section.get('content', '')[:50]}...'")

    for j, subsec in enumerate(section.get('subsections', []), 1):
        print(f"    Subsection {j}: '{subsec['heading']}'")
        print(f"      Items: {len(subsec.get('items', []))}")

print("\n" + "=" * 70)
print("\n🎯 Expected Behavior:\n")
print("""
Section 1: 'Kullanıcı Arayüzleri' (L1)
  Subsection 1: 'Giriş Ekranı' (L2)
    - Item: Email
    - Item: Şifre

Section 2: 'Backend' (L1)
  Subsection 1: 'User Login' (L2)
    - Content: POST /api/auth/login
""")

print("\n💡 Issue: Need to detect 'Giriş Ekranı:' as L2, not L1")
print("   Solution: Context-aware heading detection")
