"""
Simple BA Üret test - Opens browser and waits for manual testing
"""
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=300)
    page = browser.new_page()

    # Enable console logging
    page.on("console", lambda msg: print(f"[BROWSER {msg.type}] {msg.text}"))
    page.on("pageerror", lambda err: print(f"[PAGE ERROR] {err}"))

    print("\n" + "="*80)
    print("SIMPLE BA ÜRET TEST")
    print("="*80)

    try:
        print("\n[1/4] Opening page...")
        page.goto('http://localhost:5173/brd-pipeline', timeout=10000)
        print("✓ Page opened")
        time.sleep(2)

        print("\n[2/4] Selecting project...")
        page.locator('.ant-select-selector').first.click()
        time.sleep(0.5)
        page.locator('.ant-select-item').first.click()
        print("✓ Project selected")
        time.sleep(1)

        print("\n[3/4] Adding BRD content...")
        brd_text = """# Test BRD
## Login Ekranı
Email ve şifre ile giriş yapılır.
"""
        page.locator('textarea').first.fill(brd_text)
        print("✓ Content added")
        time.sleep(1)

        print("\n[4/4] Clicking Pipeline Başlat...")
        page.locator('button:has-text("Pipeline Başlat")').click()
        print("✓ Clicked!")
        time.sleep(3)

        # Check what's on screen
        print("\nChecking page state...")
        buttons = page.locator('button').all()
        print(f"Found {len(buttons)} buttons:")
        for i, btn in enumerate(buttons[:10]):
            text = btn.inner_text()
            if text:
                print(f"  {i+1}. '{text}'")

        print("\n" + "="*80)
        print("KEEPING BROWSER OPEN FOR 30 SECONDS")
        print("Please check if 'BA Üret' button is visible")
        print("="*80)

        for i in range(30):
            time.sleep(1)
            if i % 5 == 0:
                print(f"  {30-i} seconds remaining...")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        page.screenshot(path='/tmp/simple_test_error.png', full_page=True)
        print("Screenshot: /tmp/simple_test_error.png")
        time.sleep(10)

    finally:
        browser.close()
        print("\n✅ Test completed")
