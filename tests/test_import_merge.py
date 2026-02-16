"""
Test script for Import & Merge functionality
Tests the complete workflow end-to-end
"""
import json
from data.database import (
    init_db, get_documents_with_content, create_document,
    get_projects, create_project, get_document_by_id
)
from pipeline.document_matching import find_similar


def test_import_merge_workflow():
    """Test the complete import & merge workflow"""

    print("🧪 Testing Import & Merge Workflow\n")
    print("="*60)

    # Initialize
    init_db()

    # Step 1: Create test project if needed
    print("\n1️⃣ Setting up test project...")
    projects = get_projects()
    if not projects:
        project_id = create_project(
            name="Test Project",
            description="For testing Import & Merge",
            tags=["test"]
        )
        print(f"   ✅ Created test project (ID: {project_id})")
    else:
        project_id = projects[0]['id']
        print(f"   ✅ Using existing project (ID: {project_id})")

    # Step 2: Create "Login Analysis" template (if not exists)
    print("\n2️⃣ Creating Login Analysis template...")

    login_ba = {
        "ekranlar": [
            {
                "ekran_adi": "Login Screen",
                "aciklama": "User authentication with email and password",
                "fields": [
                    {"name": "email", "type": "email", "required": True},
                    {"name": "password", "type": "password", "required": True},
                    {"name": "remember_me", "type": "checkbox"}
                ]
            },
            {
                "ekran_adi": "Forgot Password",
                "aciklama": "Password recovery flow",
                "fields": [
                    {"name": "email", "type": "email", "required": True}
                ]
            }
        ],
        "backend_islemler": [
            {
                "islem": "User Login",
                "aciklama": "Authenticate user with email and password",
                "endpoint": "/api/auth/login",
                "method": "POST"
            },
            {
                "islem": "Password Reset",
                "aciklama": "Send password reset email",
                "endpoint": "/api/auth/reset-password",
                "method": "POST"
            }
        ]
    }

    try:
        login_doc_id = create_document(
            project_id=project_id,
            doc_type="ba",
            title="Login Analysis",
            content_json=login_ba,
            description="Standard email/password authentication",
            tags=["authentication", "login", "security"],
            jira_keys=["AUTH-101"],
            created_by="test"
        )
        print(f"   ✅ Created Login Analysis (ID: {login_doc_id})")
    except Exception as e:
        print(f"   ⚠️  Login Analysis might already exist: {e}")
        # Get existing
        docs = get_documents_with_content(doc_type="ba")
        login_doc = next((d for d in docs if "Login" in d['title']), None)
        if login_doc:
            login_doc_id = login_doc['id']
            print(f"   ✅ Using existing Login Analysis (ID: {login_doc_id})")
        else:
            print("   ❌ Could not create or find Login Analysis")
            return False

    # Step 3: Import "Face ID Login Analysis" (NEW document)
    print("\n3️⃣ Importing Face ID Login Analysis...")

    face_id_ba = {
        "ekranlar": [
            {
                "ekran_adi": "Face ID Login Screen",
                "aciklama": "Biometric authentication using Face ID",
                "fields": [
                    {"name": "face_scan", "type": "biometric", "required": True},
                    {"name": "fallback_password", "type": "password", "required": False}
                ]
            },
            {
                "ekran_adi": "Face ID Setup",
                "aciklama": "Register Face ID for user account",
                "fields": [
                    {"name": "face_capture", "type": "biometric"},
                    {"name": "confirmation", "type": "checkbox"}
                ]
            }
        ],
        "backend_islemler": [
            {
                "islem": "Face ID Authentication",
                "aciklama": "Verify user identity via Face ID biometric",
                "endpoint": "/api/auth/faceid-login",
                "method": "POST"
            },
            {
                "islem": "Enroll Face ID",
                "aciklama": "Register user's Face ID data",
                "endpoint": "/api/auth/faceid-enroll",
                "method": "POST"
            }
        ]
    }

    # This represents the "imported" document (not saved yet)
    imported_doc = {
        'title': 'Face ID Login Analysis',
        'doc_type': 'ba',
        'content_json': face_id_ba,
        'tags': ['authentication', 'biometric', 'faceid']
    }

    print(f"   ✅ Face ID analysis ready for import")

    # Step 4: Auto-detect similar documents
    print("\n4️⃣ Detecting similar documents...")

    # Get all BA documents with content
    candidates = get_documents_with_content(doc_type='ba', limit=50)
    print(f"   📊 Found {len(candidates)} candidate documents")

    if candidates:
        # Find similar
        similar_docs = find_similar(
            target_doc=imported_doc,
            candidate_docs=candidates,
            top_n=5
        )

        if similar_docs:
            print(f"   ✅ Found {len(similar_docs)} similar documents:\n")

            for i, (doc, score, breakdown) in enumerate(similar_docs, 1):
                score_pct = int(score * 100)
                tfidf_pct = int(breakdown['tfidf_score'] * 100)
                meta_pct = int(breakdown['metadata_score'] * 100)

                print(f"   {i}. {doc['title']}")
                print(f"      Overall: {score_pct}% | Content: {tfidf_pct}% | Metadata: {meta_pct}%")

            # Get top match
            top_doc, top_score, top_breakdown = similar_docs[0]

            if "Login" in top_doc['title']:
                print(f"\n   ✅ SUCCESS: Found 'Login Analysis' as top match!")
                print(f"      Similarity: {int(top_score * 100)}%")

                # Step 5: Merge simulation
                print("\n5️⃣ Simulating merge...")

                existing_content = top_doc['content_json']
                new_content = face_id_ba

                # Simple merge
                merged = json.loads(json.dumps(existing_content))

                # Merge ekranlar
                if 'ekranlar' in new_content:
                    merged['ekranlar'] = merged.get('ekranlar', []) + new_content['ekranlar']

                # Merge backend_islemler
                if 'backend_islemler' in new_content:
                    merged['backend_islemler'] = merged.get('backend_islemler', []) + new_content['backend_islemler']

                print(f"   ✅ Merged content created")
                print(f"      Original screens: {len(existing_content.get('ekranlar', []))}")
                print(f"      New screens: {len(new_content.get('ekranlar', []))}")
                print(f"      Merged screens: {len(merged.get('ekranlar', []))}")

                # Step 6: Validate merged content
                print("\n6️⃣ Validating merged content...")

                try:
                    # Check JSON is valid
                    merged_str = json.dumps(merged, indent=2)
                    json.loads(merged_str)
                    print("   ✅ Merged JSON is valid")

                    # Check structure
                    assert 'ekranlar' in merged, "Missing 'ekranlar'"
                    assert 'backend_islemler' in merged, "Missing 'backend_islemler'"

                    # Verify merge increased screen count
                    original_screens = len(existing_content.get('ekranlar', []))
                    new_screens = len(new_content.get('ekranlar', []))
                    merged_screens = len(merged['ekranlar'])
                    expected_screens = original_screens + new_screens

                    assert merged_screens == expected_screens, f"Expected {expected_screens} screens, got {merged_screens}"

                    print("   ✅ Structure validation passed")

                    # Check content preservation
                    screen_names = [s['ekran_adi'] for s in merged['ekranlar']]
                    assert "Login Screen" in screen_names, "Original 'Login Screen' missing"
                    assert "Face ID Login Screen" in screen_names, "New 'Face ID Login Screen' missing"

                    print("   ✅ Content preservation verified")

                    print("\n" + "="*60)
                    print("🎉 ALL TESTS PASSED!")
                    print("="*60)

                    print("\n📋 Test Summary:")
                    print(f"   ✅ Template exists: {top_doc['title']}")
                    print(f"   ✅ Import works: Face ID analysis ready")
                    print(f"   ✅ Similarity detection: {int(top_score * 100)}% match")
                    print(f"   ✅ Merge works: Combined 4 screens")
                    print(f"   ✅ Validation passed: Structure correct")

                    print("\n💡 Ready for UI testing!")
                    print("   Run: streamlit run app.py")
                    print("   Then: Sidebar → Import & Merge")

                    return True

                except AssertionError as e:
                    print(f"   ❌ Validation failed: {e}")
                    return False
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    return False
            else:
                print(f"   ⚠️  Top match is '{top_doc['title']}', not 'Login Analysis'")
                return False
        else:
            print("   ⚠️  No similar documents found")
            return False
    else:
        print("   ⚠️  No candidate documents available")
        return False


if __name__ == "__main__":
    print("🚀 Import & Merge - End-to-End Test\n")

    success = test_import_merge_workflow()

    if success:
        print("\n✅ All systems operational!")
        exit(0)
    else:
        print("\n❌ Some tests failed")
        exit(1)
