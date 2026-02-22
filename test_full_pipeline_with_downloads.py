"""
Comprehensive Pipeline Test - Full flow with document downloads
Tests BA generation, review stages, and document download functionality
"""
from playwright.sync_api import sync_playwright, expect
import time
import requests
import os

BASE_URL = "http://localhost:8000/api/v1"
FRONTEND_URL = "http://localhost:5173"

def setup_backend_data():
    """Setup backend with correct mock data"""
    print("\n" + "="*80)
    print("BACKEND SETUP")
    print("="*80)

    # Get or create project
    projects_response = requests.get(f"{BASE_URL}/projects")
    projects = projects_response.json()

    if not projects:
        # Create test project
        create_response = requests.post(f"{BASE_URL}/projects", json={
            "name": "Test Pipeline Project",
            "description": "Automated test project"
        })
        project = create_response.json()
        project_id = project["id"]
        project_name = project["name"]
        print(f"✓ Created project: {project_name} (ID={project_id})")
    else:
        project_id = projects[0]["id"]
        project_name = projects[0]["name"]
        print(f"✓ Using project: {project_name} (ID={project_id})")

    return project_id, project_name


def test_full_pipeline():
    """Test complete pipeline flow with downloads"""

    project_id, project_name = setup_backend_data()

    print("\n" + "="*80)
    print("STARTING FULL PIPELINE TEST")
    print("="*80)

    with sync_playwright() as p:
        # Launch browser in headed mode to see what's happening
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()

        # Enable console logging
        page.on("console", lambda msg: print(f"[BROWSER] {msg.type}: {msg.text}"))
        page.on("pageerror", lambda exc: print(f"[BROWSER ERROR] {exc}"))

        try:
            print("\n[1/10] Navigate to BRD Pipeline page...")
            page.goto(FRONTEND_URL + '/brd-pipeline', wait_until='networkidle', timeout=20000)
            page.screenshot(path='/tmp/test_01_loaded.png', full_page=True)
            print("  ✓ Page loaded")

            print("\n[2/10] Select project...")
            page.wait_for_selector('.ant-select-selector', timeout=10000)
            page.locator('.ant-select-selector').first.click()
            time.sleep(0.5)
            page.locator('.ant-select-item').first.click()
            time.sleep(1)
            page.screenshot(path='/tmp/test_02_project_selected.png', full_page=True)
            print("  ✓ Project selected")

            print("\n[3/10] Enter BRD content and start pipeline...")
            page.locator('textarea').first.fill("# Test BRD\n\nLogin ve Dashboard ekranları için test.")
            time.sleep(0.5)
            page.locator('button:has-text("Pipeline Başlat")').click()

            # Wait for pipeline to start - look for BA generation button
            page.wait_for_selector('button:has-text("BA Üret")', timeout=15000)
            time.sleep(2)
            page.screenshot(path='/tmp/test_03_pipeline_started.png', full_page=True)
            print("  ✓ Pipeline started, ready for BA generation")

            print("\n[4/10] Generate BA document...")
            ba_button = page.locator('button:has-text("BA Üret")')
            ba_button.click()
            print("  - Clicked BA Üret button, waiting for generation...")

            # Wait for BA generation to complete - look for approval button or download button
            # This might take a while, so increase timeout
            try:
                page.wait_for_selector('button:has-text("Onayla"), button:has-text("İndir")', timeout=60000)
                time.sleep(2)
                page.screenshot(path='/tmp/test_04_ba_generated.png', full_page=True)
                print("  ✓ BA generated successfully")
            except Exception as e:
                print(f"  ✗ BA generation timeout or error: {e}")
                page.screenshot(path='/tmp/test_04_ba_generation_failed.png', full_page=True)
                raise

            print("\n[5/10] Test BA download from Review stage...")
            download_buttons = page.locator('button:has-text("İndir")').all()
            if len(download_buttons) > 0:
                print(f"  ✓ Found {len(download_buttons)} download button(s)")

                # Setup download handler
                with page.expect_download(timeout=30000) as download_info:
                    download_buttons[0].click()
                    time.sleep(1)

                download = download_info.value
                filename = download.suggested_filename
                save_path = f'/tmp/{filename}'
                download.save_as(save_path)

                # Verify file size
                file_size = os.path.getsize(save_path)
                print(f"  ✓ Downloaded: {filename} ({file_size} bytes)")

                if file_size < 1000:
                    print(f"  ⚠ Warning: File size seems small ({file_size} bytes)")
                else:
                    print(f"  ✓ File size looks good")
            else:
                print("  ✗ No download button found!")
                page.screenshot(path='/tmp/test_05_no_download_button.png', full_page=True)

            print("\n[6/10] Test BA preview...")
            preview_buttons = page.locator('button:has-text("Önizle")').all()
            if len(preview_buttons) > 0:
                preview_buttons[0].click()
                time.sleep(1)

                # Check if modal opened
                modal = page.locator('.ant-modal')
                if modal.count() > 0:
                    print("  ✓ Preview modal opened")
                    page.screenshot(path='/tmp/test_06_preview_modal.png')

                    # Close modal
                    page.locator('.ant-modal button:has-text("Kapat")').click()
                    time.sleep(0.5)
                else:
                    print("  ✗ Preview modal not found")
            else:
                print("  ⚠ No preview button found")

            print("\n[7/10] Approve BA and continue...")
            approve_btn = page.locator('button:has-text("Onayla")').first
            approve_btn.click()
            time.sleep(2)
            page.screenshot(path='/tmp/test_07_ba_approved.png', full_page=True)
            print("  ✓ BA approved, moved to BA QA")

            print("\n[8/10] Skip BA QA and continue to TA...")
            skip_qa = page.locator('button:has-text("QA\'yı Atla")')
            if skip_qa.count() > 0:
                skip_qa.first.click()
                time.sleep(2)
                print("  ✓ Skipped BA QA")

            # Generate TA
            page.wait_for_selector('button:has-text("TA Üret")', timeout=10000)
            page.locator('button:has-text("TA Üret")').click()
            print("  - Generating TA...")

            page.wait_for_selector('button:has-text("Onayla"), button:has-text("İndir")', timeout=60000)
            time.sleep(2)
            page.screenshot(path='/tmp/test_08_ta_generated.png', full_page=True)
            print("  ✓ TA generated")

            # Approve TA
            page.locator('button:has-text("Onayla")').first.click()
            time.sleep(2)

            # Skip TA QA
            skip_qa = page.locator('button:has-text("QA\'yı Atla")')
            if skip_qa.count() > 0:
                skip_qa.first.click()
                time.sleep(2)

            print("\n[9/10] Continue to TC generation...")
            # Skip Figma if needed (this automatically triggers TC generation)
            skip_figma = page.locator('button:has-text("Figma Olmadan Devam Et")')
            if skip_figma.count() > 0:
                skip_figma.click()
                print("  ✓ Skipped Figma, TC generation started...")

                # Wait for TC to complete and transition to review
                page.wait_for_selector('button:has-text("Onayla"), button:has-text("İndir")', timeout=60000)
                time.sleep(2)
                page.screenshot(path='/tmp/test_09_tc_generated.png', full_page=True)
                print("  ✓ TC generated")
            else:
                # If no Figma skip button, manually generate TC
                page.wait_for_selector('button:has-text("TC Üret")', timeout=10000)
                page.locator('button:has-text("TC Üret")').click()
                print("  - Generating TC...")

                page.wait_for_selector('button:has-text("Onayla"), button:has-text("İndir")', timeout=60000)
                time.sleep(2)
                page.screenshot(path='/tmp/test_09_tc_generated.png', full_page=True)
                print("  ✓ TC generated")

            # Approve TC
            page.locator('button:has-text("Onayla")').first.click()
            time.sleep(2)

            # Wait for TC QA stage - either automatic pass or manual skip
            print("  - Waiting for TC QA stage...")
            time.sleep(2)  # Give QA a moment to evaluate

            # Try to find either the next stage button (if QA passed) or skip button
            try:
                # Wait for one of the buttons to appear
                page.wait_for_selector('button:has-text("Sonraki Aşamaya Geç"), button:has-text("QA\'yı Atla")', timeout=10000)

                next_stage = page.locator('button:has-text("Sonraki Aşamaya Geç")')
                skip_qa = page.locator('button:has-text("QA\'yı Atla")')

                if next_stage.count() > 0:
                    # QA passed automatically, click next stage button
                    print("  ✓ TC QA passed automatically")
                    next_stage.click()
                    time.sleep(2)
                elif skip_qa.count() > 0:
                    # QA not evaluated, skip it
                    print("  ✓ Skipping TC QA")
                    skip_qa.first.click()
                    time.sleep(2)
            except Exception as e:
                print(f"  ⚠ Could not find QA buttons: {e}")

            print("\n[10/10] Waiting for Done stage...")
            # Wait for Done stage to appear
            try:
                page.wait_for_selector('text=Pipeline Tamamlandı, text=Tüm dokümanlar başarıyla oluşturuldu', timeout=15000)
                print("  ✓ Reached Done stage")
            except:
                print("  ⚠ Done stage text not found, checking current page...")

            time.sleep(2)
            page.screenshot(path='/tmp/test_10_done_stage.png', full_page=True)

            # Count download buttons at done stage
            download_buttons = page.locator('button:has-text("İndir")').all()
            print(f"  ✓ Found {len(download_buttons)} download buttons")

            # Download all three documents
            doc_types = ['BA', 'TA', 'TC']
            for i, doc_type in enumerate(doc_types):
                if i < len(download_buttons):
                    print(f"\n  Downloading {doc_type}...")
                    try:
                        with page.expect_download(timeout=30000) as download_info:
                            download_buttons[i].click()
                            time.sleep(1)

                        download = download_info.value
                        filename = download.suggested_filename
                        save_path = f'/tmp/done_{filename}'
                        download.save_as(save_path)

                        file_size = os.path.getsize(save_path)
                        print(f"  ✓ {doc_type} downloaded: {filename} ({file_size} bytes)")
                    except Exception as e:
                        print(f"  ✗ Failed to download {doc_type}: {e}")

            print("\n" + "="*80)
            print("🎉 FULL PIPELINE TEST COMPLETE!")
            print("="*80)
            print("\nResults:")
            print("  - Screenshots saved to /tmp/test_*.png")
            print("  - Documents saved to /tmp/")
            print("\nKeeping browser open for 10 seconds for inspection...")
            time.sleep(10)

        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
            page.screenshot(path='/tmp/test_error.png', full_page=True)
            print("📸 Error screenshot: /tmp/test_error.png")
            time.sleep(5)
            raise

        finally:
            browser.close()


if __name__ == "__main__":
    print("\n" + "="*80)
    print("BA&QA PLATFORM - FULL PIPELINE TEST")
    print("="*80)
    print("\nThis test will:")
    print("  1. Setup backend with test project")
    print("  2. Navigate to BRD Pipeline page")
    print("  3. Start a new pipeline")
    print("  4. Generate BA, TA, and TC documents")
    print("  5. Test download functionality at each stage")
    print("  6. Verify all documents download correctly")
    print("\n" + "="*80)

    test_full_pipeline()
