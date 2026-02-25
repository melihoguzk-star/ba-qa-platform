"""
Manual upload test - Opens browser and waits for you to interact
"""
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    print("Opening BRD Pipeline page...")
    page.goto('http://localhost:5173/brd-pipeline')
    page.wait_for_load_state('networkidle')

    # Enable console logging
    page.on("console", lambda msg: print(f"BROWSER: {msg.type.upper()}: {msg.text}"))
    page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))

    print("\n" + "="*70)
    print("Browser is open. Try to:")
    print("1. Select a project")
    print("2. Upload a BRD document or paste text")
    print("3. Check for any errors")
    print("="*70)
    print("\nI'll keep the browser open for 5 minutes...")
    print("Check the console output above for any errors.\n")

    # Take initial screenshot
    page.screenshot(path='/tmp/manual_test_initial.png', full_page=True)
    print("Screenshot saved: /tmp/manual_test_initial.png")

    # Wait for 5 minutes
    time.sleep(300)

    print("\nClosing browser...")
    browser.close()
