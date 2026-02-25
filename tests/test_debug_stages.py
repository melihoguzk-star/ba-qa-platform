"""
Debug stage transitions
"""
from playwright.sync_api import sync_playwright
import time
import requests

def test_debug():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=600)
        page = browser.new_page()

        page.on("console", lambda msg: print(f"[JS] {msg.text}"))

        print("\n=== DEBUG TEST ===\n")

        # Step 1-4: Setup
        page.goto('http://localhost:5173/brd-pipeline')
        time.sleep(2)

        page.locator('.ant-select-selector').first.click()
        time.sleep(0.5)
        page.locator('.ant-select-item').first.click()

        page.locator('textarea').first.fill("# Test\nLogin ekranı")

        page.locator('button:has-text("Pipeline Başlat")').click()
        time.sleep(2)

        # Get run_id from URL or API
        print("\nStep 1: Checking initial status...")
        time.sleep(1)

        # Click BA Üret
        print("\nStep 2: Clicking BA Üret...")
        page.locator('button:has-text("BA Üret")').click()
        print("✓ Clicked")

        # Wait and check status multiple times
        for i in range(10):
            time.sleep(1)
            print(f"\n[{i+1}s] Checking page state...")

            # Check via API
            try:
                resp = requests.get('http://localhost:8000/api/v1/pipeline/30/status')
                if resp.status_code == 200:
                    status = resp.json()
                    print(f"  API Status: {status.get('status')}")
                    print(f"  Current Stage: {status.get('current_stage')}")
                else:
                    print(f"  API returned: {resp.status_code}")
            except:
                print("  API call failed")

            # Check visible buttons
            buttons = page.locator('button:visible').all()
            button_texts = [btn.inner_text() for btn in buttons if btn.inner_text().strip()]
            if button_texts:
                print(f"  Visible buttons: {button_texts[:5]}")

            # Check for Monaco editor
            monaco = page.locator('.monaco-editor').count()
            if monaco > 0:
                print(f"  ✓ Monaco Editor found!")
                break

            # Check page title
            title = page.locator('h3, h2, .ant-card-head-title').first
            if title.count() > 0:
                print(f"  Page title: {title.inner_text()}")

        print("\n=== Keeping open for 20s ===")
        time.sleep(20)

        browser.close()

if __name__ == "__main__":
    test_debug()
