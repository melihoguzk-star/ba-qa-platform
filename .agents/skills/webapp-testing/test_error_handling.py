"""
Error Handling Test — Verify error handling features
"""
from playwright.sync_api import sync_playwright
import sys

def test_error_handling():
    """Test error handling components and features"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Test 1: 404 Page
            print("Test 1: 404 Page...")
            page.goto('http://localhost:5173/nonexistent-page')
            page.wait_for_load_state('networkidle')

            # Check for 404 result
            result_404 = page.locator('div.ant-result-404')
            if not result_404.is_visible():
                print("❌ 404 page not showing!")
                sys.exit(1)

            print("✅ 404 page displays correctly")
            page.screenshot(path='/tmp/error_404.png')

            # Test 2: Navigate back to home
            print("\nTest 2: Navigate to home from 404...")
            home_button = page.locator('button:has-text("Ana Sayfaya Dön")')
            home_button.click()
            page.wait_for_load_state('networkidle')

            # Verify we're on the dashboard
            page.wait_for_selector('h1:has-text("Dashboard")', timeout=5000)
            print("✅ Successfully navigated to home from 404")

            # Test 3: Check offline indicator is hidden when online
            print("\nTest 3: Offline indicator (should be hidden)...")
            offline_indicator = page.locator('div.ant-alert-error:has-text("Bağlantı Yok")')
            if offline_indicator.is_visible():
                print("❌ Offline indicator should be hidden when online!")
                sys.exit(1)

            print("✅ Offline indicator is hidden when online")

            # Test 4: Check empty states in Documents page
            print("\nTest 4: Empty state in Documents page...")
            docs_link = page.locator('li.ant-menu-item:has-text("Dokümanlar")')
            docs_link.click()
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(1000)

            # Take screenshot
            page.screenshot(path='/tmp/error_documents_page.png')
            print("✅ Documents page loaded")

            print("\n✅ All error handling tests passed!")

        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            page.screenshot(path='/tmp/error_handling_error.png', full_page=True)
            browser.close()
            sys.exit(1)

        browser.close()

if __name__ == '__main__':
    test_error_handling()
