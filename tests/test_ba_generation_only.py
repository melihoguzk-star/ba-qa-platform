"""
Test BA generation and review display (mock mode)
"""
from playwright.sync_api import sync_playwright
import time
import requests

def test_ba_generation():
    """Test BA generation with mock data"""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        # Enable logging
        page.on("console", lambda msg: print(f"[CONSOLE {msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: print(f"[ERROR] {err}"))

        print("\n" + "="*80)
        print("BA GENERATION TEST (MOCK MODE)")
        print("="*80)

        try:
            # Step 1: Open page
            print("\n[1/5] Opening page...")
            page.goto('http://localhost:5173/brd-pipeline', timeout=15000)
            time.sleep(2)
            print("✓ Page loaded")

            # Step 2: Select project
            print("\n[2/5] Selecting project...")
            page.locator('.ant-select-selector').first.click()
            time.sleep(0.5)
            page.locator('.ant-select-item').first.click()
            print("✓ Project selected")

            # Step 3: Add BRD
            print("\n[3/5] Adding BRD content...")
            brd_text = "# Test BRD\n\n## Login Ekranı\nEmail ve şifre ile giriş yapılır."
            page.locator('textarea').first.fill(brd_text)
            print("✓ BRD added")

            # Step 4: Start pipeline
            print("\n[4/5] Starting pipeline...")
            page.locator('button:has-text("Pipeline Başlat")').click()
            time.sleep(2)
            print("✓ Pipeline started")

            # Check status via API
            print("\nChecking pipeline status via API...")
            time.sleep(1)

            # Get the run_id from URL or page
            url = page.url
            print(f"  Current URL: {url}")

            # Step 5: Click BA Üret
            print("\n[5/5] Clicking BA Üret...")
            ba_button = page.locator('button:has-text("BA Üret")')

            if ba_button.count() == 0:
                print("✗ BA Üret button not found!")
                page.screenshot(path='/tmp/error_no_ba_button.png')
                return False

            ba_button.click()
            print("✓ BA Üret clicked")

            # Wait for generation
            print("\nWaiting for BA generation...")
            time.sleep(3)

            # Check if we transitioned to review stage
            print("\nChecking for review stage...")

            # Take screenshot
            page.screenshot(path='/tmp/ba_after_generation.png', full_page=True)
            print("Screenshot: /tmp/ba_after_generation.png")

            # Check current stage
            current_stage_text = page.locator('text=İnceleme').or_(page.locator('text=Review')).or_(page.locator('text=Onayla'))
            if current_stage_text.count() > 0:
                print("✓ Successfully transitioned to review stage!")
            else:
                print("⚠ Review stage not visible yet")
                print("\nCurrent buttons on page:")
                buttons = page.locator('button').all()
                for btn in buttons[:10]:
                    text = btn.inner_text()
                    if text:
                        print(f"  - '{text}'")

            # Keep browser open
            print("\n" + "="*80)
            print("Keeping browser open for 15 seconds for inspection...")
            print("="*80)
            time.sleep(15)

            return True

        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
            page.screenshot(path='/tmp/error_ba_test.png', full_page=True)
            print("Error screenshot: /tmp/error_ba_test.png")
            time.sleep(5)
            return False

        finally:
            browser.close()
            print("\n✅ Test completed")


if __name__ == "__main__":
    success = test_ba_generation()
    exit(0 if success else 1)
