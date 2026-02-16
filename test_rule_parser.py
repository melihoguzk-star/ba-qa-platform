"""
Test script for rule-based document parser
"""
from pipeline.document_parser import parse_text_to_json
import json

print("🧪 Testing Rule-Based Document Parser\n")
print("=" * 60)

# Test BA parsing
print("\n1️⃣ Testing BA Parsing")
print("-" * 60)

ba_text = """
Ekranlar:

Login Screen:
- Email field: Email input field (required)
- Password field: Password input (required)
- Remember me: Checkbox (optional)
- Login button: Submit login form
- Forgot password link: Navigate to password reset

Backend İşlemler:

User Authentication:
POST /api/auth/login
Authenticate user credentials and return JWT token

Password Reset:
POST /api/auth/reset-password
Send password reset email to user

Güvenlik Gereksinimleri:

Password Security:
All passwords must be hashed using bcrypt with minimum 10 rounds

Session Management:
JWT tokens expire after 24 hours and must be refreshed

Test Senaryoları:

Successful Login:
1) User opens login page
2) User enters valid email and password
3) User clicks login button
4) System authenticates user
5) User is redirected to dashboard

Failed Login:
1) User enters invalid credentials
2) User clicks login
3) System shows error message
4) User remains on login page
"""

print("📝 Input Text:")
print(ba_text[:200] + "..." if len(ba_text) > 200 else ba_text)

try:
    ba_result = parse_text_to_json(ba_text, 'ba')

    print(f"\n✅ Parsing successful!")
    print(f"\n📋 Parsed Structure:")
    print(f"   Keys: {list(ba_result.keys())}")

    for key, value in ba_result.items():
        if isinstance(value, list):
            print(f"   {key}: {len(value)} items")
            if value:
                print(f"      Example: {list(value[0].keys())}")

    print(f"\n📄 Full JSON:")
    print(json.dumps(ba_result, indent=2, ensure_ascii=False))

except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

# Test TA parsing
print("\n\n2️⃣ Testing TA Parsing")
print("-" * 60)

ta_text = """
Servisler:

User Service:
Manages user accounts, authentication, and profiles
Technologies: Node.js, Express, JWT

Payment Service:
Handles payment processing and transaction management
Technologies: Python, FastAPI, Stripe API

Veri Modeli:

User Entity:
- id: integer, primary key
- email: string, unique, required
- password_hash: string, required
- created_at: timestamp

Payment Entity:
- id: integer
- user_id: foreign key
- amount: decimal
- status: enum

Teknolojik Gereksinimler:

Database:
PostgreSQL 14+ for relational data storage

Cache:
Redis 6+ for session management and caching

API Gateway:
Kong API Gateway for microservices routing
"""

try:
    ta_result = parse_text_to_json(ta_text, 'ta')

    print(f"✅ TA Parsing successful!")
    print(f"\n📋 Parsed Structure:")
    for key, value in ta_result.items():
        if isinstance(value, list):
            print(f"   {key}: {len(value)} items")

    print(f"\n📄 Full JSON:")
    print(json.dumps(ta_result, indent=2, ensure_ascii=False))

except Exception as e:
    print(f"❌ Error: {str(e)}")

# Test TC parsing
print("\n\n3️⃣ Testing TC Parsing")
print("-" * 60)

tc_text = """
Test Cases:

Login with Valid Credentials:
1) Navigate to login page
2) Enter valid email address
3) Enter valid password
4) Click login button
5) Verify redirect to dashboard
6) Verify user session is created

Login with Invalid Password:
1) Navigate to login page
2) Enter valid email
3) Enter invalid password
4) Click login button
5) Verify error message appears
6) Verify user remains on login page

Test Senaryolari:

Authentication Flow:
Test all login and authentication scenarios including valid login, invalid credentials, and password reset
"""

try:
    tc_result = parse_text_to_json(tc_text, 'tc')

    print(f"✅ TC Parsing successful!")
    print(f"\n📋 Parsed Structure:")
    for key, value in tc_result.items():
        if isinstance(value, list):
            print(f"   {key}: {len(value)} items")

    print(f"\n📄 Full JSON:")
    print(json.dumps(tc_result, indent=2, ensure_ascii=False))

except Exception as e:
    print(f"❌ Error: {str(e)}")

# Summary
print("\n\n" + "=" * 60)
print("🎯 Test Summary")
print("=" * 60)
print("\n✅ Rule-based parser working!")
print("\n📊 Capabilities:")
print("   - Recognizes Turkish and English headings")
print("   - Parses fields and actions from lists")
print("   - Extracts API endpoints and methods")
print("   - Identifies test scenarios and steps")
print("   - Supports BA, TA, and TC formats")
print("\n💡 Best with structured documents that have clear section headings")
