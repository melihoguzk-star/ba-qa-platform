"""
Test document export functionality (download and preview)
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

# Sample test data
SAMPLE_BA = {
    "metadata": {
        "project": "Test Project",
        "date": "2024-01-01",
        "version": "1.0"
    },
    "amac": "Bu proje test amaçlıdır",
    "kapsam": "Test kapsamı",
    "fonksiyonel_analiz": {
        "Login Ekranı": {
            "aciklama": "Kullanıcı giriş ekranı",
            "islem_akisi": [
                {
                    "islem": "Email gir",
                    "akis": "Kullanıcı email alanına tıklar",
                    "tasarim": "Input field"
                },
                {
                    "islem": "Şifre gir",
                    "akis": "Kullanıcı şifre alanına tıklar",
                    "tasarim": "Password field"
                }
            ],
            "kabul_kriterleri": [
                {"kriter": "Email validasyonu yapılmalı"},
                {"kriter": "Şifre en az 6 karakter olmalı"}
            ]
        }
    }
}

SAMPLE_TA = {
    "metadata": {
        "project": "Test Project",
        "date": "2024-01-01",
        "version": "1.0"
    },
    "teknik_mimari": {
        "backend": "FastAPI",
        "frontend": "React",
        "database": "SQLite"
    },
    "api_spesifikasyonlari": [
        {
            "endpoint": "/api/login",
            "method": "POST",
            "request": {"email": "string", "password": "string"},
            "response": {"token": "string", "user": "object"}
        }
    ],
    "veritabani_semasi": {
        "users": [
            {"field": "id", "type": "INTEGER", "description": "Primary key"},
            {"field": "email", "type": "TEXT", "description": "User email"},
            {"field": "password_hash", "type": "TEXT", "description": "Hashed password"}
        ]
    }
}

SAMPLE_TC = {
    "test_senaryolari": [
        {
            "id": "TC001",
            "isim": "Login - Başarılı Senaryo",
            "oncelik": "High",
            "kategori": "Authentication",
            "on_kosullar": ["Kullanıcı kayıtlı olmalı"],
            "adimlar": [
                "Email alanına geçerli email gir",
                "Şifre alanına geçerli şifre gir",
                "Login butonuna tıkla"
            ],
            "beklenen_sonuc": "Kullanıcı başarıyla giriş yapar ve dashboard'a yönlendirilir",
            "test_verisi": {
                "email": "test@example.com",
                "password": "test123"
            }
        },
        {
            "id": "TC002",
            "isim": "Login - Hatalı Şifre",
            "oncelik": "High",
            "kategori": "Authentication",
            "on_kosullar": ["Kullanıcı kayıtlı olmalı"],
            "adimlar": [
                "Email alanına geçerli email gir",
                "Şifre alanına yanlış şifre gir",
                "Login butonuna tıkla"
            ],
            "beklenen_sonuc": "Hata mesajı gösterilir: 'Şifre yanlış'",
            "test_verisi": {
                "email": "test@example.com",
                "password": "wrong_password"
            }
        }
    ]
}

def test_document_export():
    print("\n" + "="*80)
    print("TESTING DOCUMENT EXPORT FUNCTIONALITY")
    print("="*80)

    # Step 1: Get existing projects
    print("\n[1/7] Getting existing projects...")
    projects_response = requests.get(f"{BASE_URL}/projects")

    if projects_response.status_code != 200:
        print(f"✗ Failed to get projects: {projects_response.status_code}")
        return

    projects = projects_response.json()

    if not projects:
        print("✗ No projects found. Please create a project first.")
        return

    project_id = projects[0]["id"]
    project_name = projects[0]["name"]
    print(f"✓ Using existing project: {project_name} (ID={project_id})")

    # Step 2: Start a pipeline
    print("\n[2/7] Starting pipeline...")
    pipeline_response = requests.post(f"{BASE_URL}/pipeline/start", json={
        "project_id": project_id,
        "project_name": project_name,
        "brd_content": "# Test BRD\n\nThis is a test BRD for document export.",
        "stages": ["ba", "ta", "tc"]
    })

    if pipeline_response.status_code != 202:
        print(f"✗ Failed to start pipeline: {pipeline_response.status_code}")
        return

    pipeline_data = pipeline_response.json()
    run_id = pipeline_data["pipeline_run_id"]
    print(f"✓ Pipeline started: run_id={run_id}")

    # Step 3: Save BA checkpoint
    print("\n[3/7] Saving BA checkpoint...")
    ba_checkpoint_response = requests.post(
        f"{BASE_URL}/pipeline/{run_id}/checkpoint/ba_gen",
        json=SAMPLE_BA
    )

    if ba_checkpoint_response.status_code != 200:
        print(f"✗ Failed to save BA checkpoint: {ba_checkpoint_response.status_code}")
        print(ba_checkpoint_response.text)
        return

    print("✓ BA checkpoint saved")

    # Step 4: Save TA checkpoint
    print("\n[4/7] Saving TA checkpoint...")
    ta_checkpoint_response = requests.post(
        f"{BASE_URL}/pipeline/{run_id}/checkpoint/ta_gen",
        json=SAMPLE_TA
    )

    if ta_checkpoint_response.status_code != 200:
        print(f"✗ Failed to save TA checkpoint: {ta_checkpoint_response.status_code}")
        return

    print("✓ TA checkpoint saved")

    # Step 5: Save TC checkpoint
    print("\n[5/7] Saving TC checkpoint...")
    tc_checkpoint_response = requests.post(
        f"{BASE_URL}/pipeline/{run_id}/checkpoint/tc_gen",
        json=SAMPLE_TC
    )

    if tc_checkpoint_response.status_code != 200:
        print(f"✗ Failed to save TC checkpoint: {tc_checkpoint_response.status_code}")
        return

    print("✓ TC checkpoint saved")

    # Step 6: Test preview endpoints
    print("\n[6/7] Testing preview endpoints...")
    for doc_type in ['ba', 'ta', 'tc']:
        preview_response = requests.get(
            f"{BASE_URL}/documents-export/{run_id}/preview/{doc_type}"
        )

        if preview_response.status_code == 200:
            print(f"  ✓ Preview {doc_type.upper()} - OK")
        else:
            print(f"  ✗ Preview {doc_type.upper()} - Failed: {preview_response.status_code}")

    # Step 7: Test download endpoints
    print("\n[7/7] Testing download endpoints...")
    output_dir = Path("/tmp/ba_qa_exports")
    output_dir.mkdir(exist_ok=True)

    for doc_type in ['ba', 'ta', 'tc']:
        download_response = requests.get(
            f"{BASE_URL}/documents-export/{run_id}/download/{doc_type}"
        )

        if download_response.status_code == 200:
            extension = 'xlsx' if doc_type == 'tc' else 'docx'
            filename = output_dir / f"{doc_type.upper()}_export.{extension}"

            with open(filename, 'wb') as f:
                f.write(download_response.content)

            print(f"  ✓ Download {doc_type.upper()} - Saved to {filename}")
        else:
            print(f"  ✗ Download {doc_type.upper()} - Failed: {download_response.status_code}")
            print(f"     {download_response.text}")

    print("\n" + "="*80)
    print("🎉 DOCUMENT EXPORT TEST COMPLETE!")
    print("="*80)
    print(f"\nExported files saved to: {output_dir}")
    print("\nYou can open these files to verify the export:")
    print(f"  - BA: {output_dir}/BA_export.docx")
    print(f"  - TA: {output_dir}/TA_export.docx")
    print(f"  - TC: {output_dir}/TC_export.xlsx")

if __name__ == "__main__":
    test_document_export()
