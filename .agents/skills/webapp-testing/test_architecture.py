"""
Architecture Page Test — Verify all 5 tabs load correctly
"""
from playwright.sync_api import sync_playwright
import sys

def test_architecture_page():
    """Test the Architecture page loads and all 5 tabs work"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Navigate to home page
            print("Navigating to http://localhost:5173...")
            page.goto('http://localhost:5173')
            page.wait_for_load_state('networkidle')

            # Debug: Take screenshot of the page
            print("Taking screenshot to inspect menu...")
            page.screenshot(path='/tmp/architecture_menu_debug.png', full_page=True)

            # Check if menu item exists
            menu_items = page.locator('li.ant-menu-item').all_text_contents()
            print(f"Found menu items: {menu_items}")

            # Navigate to Architecture page
            print("Clicking Architecture menu item...")
            architecture_link = page.locator('li.ant-menu-item:has-text("Mimari")')

            if not architecture_link.is_visible():
                print("Architecture menu item not visible!")
                sys.exit(1)

            architecture_link.click()
            page.wait_for_load_state('networkidle')

            # Verify we're on the Architecture page
            print("Verifying Architecture page loaded...")
            page.wait_for_selector('h1:has-text("Platform Mimarisi")', timeout=5000)

            # Take screenshot of header
            print("Taking screenshot of Architecture page header...")
            page.screenshot(path='/tmp/architecture_header.png')

            # Test all 5 tabs
            tabs = [
                "AI Agents",
                "Document Intelligence",
                "Entegrasyonlar",
                "Pipeline Akışları",
                "Tech Stack"
            ]

            for tab_name in tabs:
                print(f"Testing tab: {tab_name}...")
                tab = page.locator(f'div[role="tab"]:has-text("{tab_name}")')

                if not tab.is_visible():
                    print(f"❌ Tab '{tab_name}' not found!")
                    sys.exit(1)

                # Click tab
                tab.click()
                page.wait_for_timeout(500)  # Wait for tab content to render

                # Verify tab panel is visible
                tab_panel = page.locator(f'div[role="tabpanel"]:visible')
                if not tab_panel.count() > 0:
                    print(f"❌ Tab panel for '{tab_name}' not visible!")
                    sys.exit(1)

                # Take screenshot
                screenshot_name = tab_name.lower().replace(' ', '_').replace('ı', 'i').replace('ü', 'u').replace('ş', 's')
                page.screenshot(path=f'/tmp/architecture_{screenshot_name}.png')
                print(f"✅ Tab '{tab_name}' loaded successfully")

            print("\n✅ All Architecture page tests passed!")

            # Final screenshot
            page.screenshot(path='/tmp/architecture_final.png', full_page=True)

        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            page.screenshot(path='/tmp/architecture_error.png', full_page=True)
            browser.close()
            sys.exit(1)

        browser.close()

if __name__ == '__main__':
    test_architecture_page()
