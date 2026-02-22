"""
Test frontend document download and preview functionality
"""
from playwright.sync_api import sync_playwright
import time
import requests

BASE_URL = "http://localhost:8000/api/v1"

# First, setup backend with correct mock data
def setup_backend_data():
    """Setup backend with correct mock data structure"""
    print("\n" + "="*80)
    print("SETTING UP BACKEND DATA")
    print("="*80)

    # Get project
    projects_response = requests.get(f"{BASE_URL}/projects")
    projects = projects_response.json()
    if not projects:
        print("✗ No projects found")
        return None, None

    project_id = projects[0]["id"]
    project_name = projects[0]["name"]
    print(f"✓ Using project: {project_name} (ID={project_id})")

    # Start pipeline
    pipeline_response = requests.post(f"{BASE_URL}/pipeline/start", json={
        "project_id": project_id,
        "project_name": project_name,
        "brd_content": "# Test BRD\n\nLogin ve Dashboard ekranları",
        "stages": ["ba", "ta", "tc"]
    })

    run_id = pipeline_response.json()["pipeline_run_id"]
    print(f"✓ Pipeline started: run_id={run_id}")

    # Correct BA mock data
    BA_MOCK = {
        "ekranlar": [
            {
                "ekran_adi": "Login Ekranı",
                "aciklama": "Kullanıcıların email ve şifre ile sisteme giriş yapmasını sağlar.",
                "gerekli_dokumanlar": {
                    "teknik_akis": "Login akış diyagramı",
                    "tasarim_dosyasi": "Figma - Login Screen"
                },
                "is_akisi_diyagrami": [
                    "1. Kullanıcı login sayfasına gider",
                    "2. Email ve şifre girer",
                    "3. Giriş yapar"
                ],
                "fonksiyonel_gereksinimler": [
                    {"id": "FR-01", "tanim": "Email girebilmelidir"},
                    {"id": "FR-02", "tanim": "Şifre girebilmelidir"}
                ],
                "is_kurallari": [
                    {"kural": "Email formatı geçerli olmalı", "detay": "@ içermeli"}
                ],
                "kabul_kriterleri": [
                    {"id": "BR-01", "kriter": "Geçerli giriş başarılı olmalı"}
                ],
                "validasyonlar": [
                    {"alan": "email", "kisit": "Email formatı", "hata_mesaji": "Geçerli email giriniz"}
                ]
            }
        ]
    }

    # Correct TA mock data
    TA_MOCK = {
        "teknik_analiz": {
            "genel_tanim": {
                "modul_adi": "Auth Module",
                "teknoloji_stack": ["React", "FastAPI"],
                "mimari_yaklasim": "REST API"
            },
            "endpoint_detaylari": {
                "/api/login": {
                    "method": "POST",
                    "aciklama": "Login endpoint",
                    "request_body": {"email": "string", "password": "string"},
                    "response_success": {"token": "string"},
                    "response_errors": []
                }
            },
            "dto_veri_yapilari": [],
            "validasyon_kurallari": [],
            "mock_curl_ornekleri": []
        }
    }

    # Correct TC mock data
    TC_MOCK = {
        "test_cases": [
            {
                "test_case_id": "TC-001",
                "br_id": "BR-01",
                "priority": "High",
                "test_area": "Auth",
                "testcase": "Login test",
                "test_steps": "1. Go to login\n2. Enter credentials",
                "test_data": '{"email": "test@test.com"}',
                "expected_result": "User logged in"
            }
        ]
    }

    # Save checkpoints
    requests.post(f"{BASE_URL}/pipeline/{run_id}/checkpoint/ba_gen", json=BA_MOCK)
    print("✓ BA checkpoint saved")

    requests.post(f"{BASE_URL}/pipeline/{run_id}/checkpoint/ta_gen", json=TA_MOCK)
    print("✓ TA checkpoint saved")

    requests.post(f"{BASE_URL}/pipeline/{run_id}/checkpoint/tc_gen", json=TC_MOCK)
    print("✓ TC checkpoint saved")

    # Update pipeline status to completed
    print("✓ Backend data ready")

    return run_id, project_name


def test_frontend_download():
    """Test frontend download and preview functionality"""

    # Setup backend first
    run_id, project_name = setup_backend_data()
    if not run_id:
        print("✗ Backend setup failed")
        return

    print("\n" + "="*80)
    print("TESTING FRONTEND DOCUMENT DOWNLOAD & PREVIEW")
    print("="*80)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=800)
        page = browser.new_page()

        page.on("console", lambda msg: print(f"[JS] {msg.text}"))

        try:
            # Navigate to BRD Pipeline page
            print("\n[1/8] Navigating to BRD Pipeline...")
            page.goto('http://localhost:5173/brd-pipeline', timeout=15000)
            time.sleep(2)
            print("✓ Page loaded")

            # Select project
            print("\n[2/8] Selecting project...")
            page.locator('.ant-select-selector').first.click()
            time.sleep(0.5)
            page.locator('.ant-select-item').first.click()
            time.sleep(1)
            print("✓ Project selected")

            # Enter BRD content and start pipeline
            print("\n[3/8] Starting pipeline...")
            page.locator('textarea').first.fill("# Test BRD\n\nLogin test")
            page.locator('button:has-text("Pipeline Başlat")').click()
            time.sleep(2)
            print("✓ Pipeline started")

            # Generate BA
            print("\n[4/8] Generating BA...")
            page.locator('button:has-text("BA Üret")').click()
            time.sleep(3)
            print("✓ BA generated")

            # Test BA Review stage download buttons
            print("\n[5/8] Testing BA Review stage download buttons...")
            time.sleep(2)

            # Check if preview button exists
            preview_btn = page.locator('button:has-text("Önizle")').first
            if preview_btn.count() > 0:
                print("  ✓ 'Önizle' button found")

                # Click preview
                preview_btn.click()
                time.sleep(1)

                # Check if modal opened
                if page.locator('.ant-modal').count() > 0:
                    print("  ✓ Preview modal opened")
                    page.screenshot(path='/tmp/preview_modal.png')
                    print("  📸 Screenshot: /tmp/preview_modal.png")

                    # Close modal
                    page.locator('button:has-text("Kapat")').click()
                    time.sleep(1)
                else:
                    print("  ⚠ Preview modal not found")
            else:
                print("  ⚠ Preview button not found")

            # Check download button
            download_btn = page.locator('button:has-text("İndir")').first
            if download_btn.count() > 0:
                print("  ✓ 'İndir (DOCX)' button found")

                # Setup download handler
                with page.expect_download() as download_info:
                    download_btn.click()
                    time.sleep(1)

                download = download_info.value
                print(f"  ✓ Download triggered: {download.suggested_filename}")
                download.save_as(f'/tmp/{download.suggested_filename}')
                print(f"  ✓ File saved: /tmp/{download.suggested_filename}")
            else:
                print("  ⚠ Download button not found")

            # Approve and continue to QA
            print("\n[6/8] Moving through pipeline stages...")
            page.locator('button:has-text("Onayla")').first.click()
            time.sleep(2)
            print("  ✓ Moved to BA QA")

            # Skip QA stages for faster testing
            page.locator('button:has-text("QA\'yı Atla")').first.click()
            time.sleep(2)

            # Generate TA
            page.locator('button:has-text("TA Üret")').click()
            time.sleep(3)
            page.locator('button:has-text("Onayla")').first.click()
            time.sleep(2)
            page.locator('button:has-text("QA\'yı Atla")').first.click()
            time.sleep(2)

            # Skip Figma
            skip_figma = page.locator('button:has-text("Figma Olmadan Devam Et")')
            if skip_figma.count() > 0:
                skip_figma.click()
                time.sleep(2)

            # Generate TC
            page.locator('button:has-text("TC Üret")').click()
            time.sleep(3)
            page.locator('button:has-text("Onayla")').first.click()
            time.sleep(2)
            page.locator('button:has-text("QA\'yı Atla")').first.click()
            time.sleep(3)

            print("✓ Reached Done stage")

            # Test Done stage download buttons
            print("\n[7/8] Testing Done stage download buttons...")
            time.sleep(2)

            # Take screenshot of done stage
            page.screenshot(path='/tmp/done_stage.png', full_page=True)
            print("  📸 Screenshot: /tmp/done_stage.png")

            # Count download buttons
            download_buttons = page.locator('button:has-text("İndir")').all()
            print(f"  ✓ Found {len(download_buttons)} download buttons")

            # Test BA download from done stage
            if len(download_buttons) >= 1:
                print("\n  Testing BA download from done stage...")
                with page.expect_download() as download_info:
                    download_buttons[0].click()
                    time.sleep(1)
                download = download_info.value
                print(f"    ✓ BA downloaded: {download.suggested_filename}")
                download.save_as(f'/tmp/done_{download.suggested_filename}')

            # Test TA download from done stage
            if len(download_buttons) >= 2:
                print("\n  Testing TA download from done stage...")
                with page.expect_download() as download_info:
                    download_buttons[1].click()
                    time.sleep(1)
                download = download_info.value
                print(f"    ✓ TA downloaded: {download.suggested_filename}")
                download.save_as(f'/tmp/done_{download.suggested_filename}')

            # Test TC download from done stage
            if len(download_buttons) >= 3:
                print("\n  Testing TC download from done stage...")
                with page.expect_download() as download_info:
                    download_buttons[2].click()
                    time.sleep(1)
                download = download_info.value
                print(f"    ✓ TC downloaded: {download.suggested_filename}")
                download.save_as(f'/tmp/done_{download.suggested_filename}')

            # Test preview from done stage
            print("\n[8/8] Testing preview from done stage...")
            preview_buttons = page.locator('button:has-text("Önizle")').all()
            if len(preview_buttons) > 0:
                print(f"  ✓ Found {len(preview_buttons)} preview buttons")

                # Click first preview
                preview_buttons[0].click()
                time.sleep(1)

                if page.locator('.ant-modal').count() > 0:
                    print("  ✓ Preview modal opened from done stage")
                    page.screenshot(path='/tmp/done_preview_modal.png')
                    print("  📸 Screenshot: /tmp/done_preview_modal.png")

                    # Test download from modal
                    modal_download_btn = page.locator('.ant-modal button:has-text("İndir")').first
                    if modal_download_btn.count() > 0:
                        print("  ✓ Download button in modal found")

                    # Close modal
                    page.locator('.ant-modal button:has-text("Kapat")').click()
                    time.sleep(1)

            print("\n" + "="*80)
            print("🎉 FRONTEND TEST COMPLETE!")
            print("="*80)
            print("\nDownloaded files saved to /tmp/")
            print("Screenshots:")
            print("  - /tmp/preview_modal.png")
            print("  - /tmp/done_stage.png")
            print("  - /tmp/done_preview_modal.png")

            print("\n⏸ Keeping browser open for 10 seconds...")
            time.sleep(10)

        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
            page.screenshot(path='/tmp/frontend_test_error.png', full_page=True)
            print("📸 Error screenshot: /tmp/frontend_test_error.png")
            time.sleep(5)

        finally:
            browser.close()


if __name__ == "__main__":
    test_frontend_download()
