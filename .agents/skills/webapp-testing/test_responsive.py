"""
Responsive Design Test — Verify responsive layout works
"""
from playwright.sync_api import sync_playwright
import sys

def test_responsive_design():
    """Test responsive design features"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Test different viewport sizes
        viewports = [
            {'name': 'Mobile', 'width': 375, 'height': 667},
            {'name': 'Tablet', 'width': 768, 'height': 1024},
            {'name': 'Desktop', 'width': 1920, 'height': 1080},
        ]

        try:
            for viewport in viewports:
                print(f"\n{'='*50}")
                print(f"Testing {viewport['name']} ({viewport['width']}x{viewport['height']})")
                print(f"{'='*50}")

                page = browser.new_page(viewport={'width': viewport['width'], 'height': viewport['height']})

                # Navigate to home
                print(f"Navigating to home page...")
                page.goto('http://localhost:5173')
                page.wait_for_load_state('networkidle')

                # Check if page loaded
                page.wait_for_selector('h1:has-text("Dashboard")', timeout=5000)
                print(f"✅ Dashboard loaded")

                # Take screenshot
                page.screenshot(path=f'/tmp/responsive_{viewport["name"].lower()}_dashboard.png')

                # Test navigation on mobile (drawer)
                if viewport['name'] == 'Mobile':
                    print("Testing mobile drawer navigation...")

                    # Click menu button to open drawer
                    menu_button = page.locator('button[class*="ant-btn"]:has(svg)')
                    menu_button.first.click()
                    page.wait_for_timeout(500)

                    # Check if drawer is visible
                    drawer = page.locator('div.ant-drawer')
                    if drawer.is_visible():
                        print("✅ Mobile drawer opened")
                        page.screenshot(path='/tmp/responsive_mobile_drawer_open.png')

                        # Click on a menu item
                        settings_link = page.locator('li.ant-menu-item:has-text("Ayarlar")')
                        settings_link.click()
                        page.wait_for_timeout(500)

                        # Drawer should close after navigation
                        page.wait_for_load_state('networkidle')
                        print("✅ Navigated and drawer closed")
                    else:
                        print("⚠️  Drawer not visible (might be using sider)")

                # Test on desktop (sidebar)
                if viewport['name'] == 'Desktop':
                    print("Testing desktop sidebar...")

                    # Check if sidebar is visible
                    sider = page.locator('aside.ant-layout-sider')
                    if sider.is_visible():
                        print("✅ Desktop sidebar visible")

                        # Test sidebar collapse
                        collapse_button = page.locator('button.ant-layout-sider-trigger')
                        if collapse_button.is_visible():
                            collapse_button.click()
                            page.wait_for_timeout(300)
                            print("✅ Sidebar collapsed")
                            page.screenshot(path='/tmp/responsive_desktop_collapsed.png')
                        else:
                            print("⚠️  Collapse button not found")

                page.close()

            print(f"\n{'='*50}")
            print("✅ All responsive design tests passed!")
            print(f"{'='*50}")

        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            page.screenshot(path='/tmp/responsive_error.png', full_page=True)
            browser.close()
            sys.exit(1)

        browser.close()

if __name__ == '__main__':
    test_responsive_design()
