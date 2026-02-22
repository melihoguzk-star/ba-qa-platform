"""
Test Settings Page — All 4 tabs
"""
import time
from playwright.sync_api import sync_playwright

def test_settings():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Test 1: Backend health check
        print("✓ Test 1: Backend health check...")
        try:
            response = page.goto('http://localhost:8000/health')
            assert response.status == 200, f"Health check failed: {response.status}"
            health_data = page.content()
            assert 'healthy' in health_data, "Health check response invalid"
            print("  ✅ Backend is healthy")
        except Exception as e:
            print(f"  ❌ Backend health check failed: {e}")
            browser.close()
            return

        # Test 2: Frontend loads
        print("\n✓ Test 2: Frontend loads...")
        try:
            page.goto('http://localhost:5173')
            page.wait_for_load_state('networkidle')
            time.sleep(2)  # Extra wait for React hydration

            # Check if React app loaded
            title = page.title()
            print(f"  ✅ Frontend loaded (title: {title})")
        except Exception as e:
            print(f"  ❌ Frontend load failed: {e}")
            browser.close()
            return

        # Test 3: Navigate to Settings
        print("\n✓ Test 3: Navigate to Settings page...")
        try:
            # Click Settings in sidebar (using menu item text)
            settings_link = page.locator('li.ant-menu-item:has-text("Ayarlar")')
            settings_link.click()
            page.wait_for_url('**/settings')
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            # Verify page loaded
            heading = page.locator('h2:has-text("Ayarlar")')
            assert heading.is_visible(), "Settings page heading not found"
            print("  ✅ Settings page loaded")
        except Exception as e:
            print(f"  ❌ Settings navigation failed: {e}")
            page.screenshot(path='/tmp/settings_nav_error.png', full_page=True)
            print(f"  📸 Error screenshot saved to /tmp/settings_nav_error.png")
            browser.close()
            return

        # Test 4: Tab 1 - API Keys
        print("\n✓ Test 4: API Keys tab...")
        try:
            api_keys_tab = page.locator('div[role="tab"]:has-text("API Keys")')
            api_keys_tab.click()
            time.sleep(1)

            # Check for Gemini keys card
            gemini_card = page.locator('text=Gemini API Keys')
            assert gemini_card.is_visible(), "Gemini keys card not found"

            page.screenshot(path='/tmp/settings_tab1_apikeys.png', full_page=True)
            print("  ✅ API Keys tab loaded")
            print("  📸 Screenshot: /tmp/settings_tab1_apikeys.png")
        except Exception as e:
            print(f"  ❌ API Keys tab failed: {e}")
            page.screenshot(path='/tmp/settings_tab1_error.png', full_page=True)
            print(f"  📸 Error screenshot: /tmp/settings_tab1_error.png")

        # Test 5: Tab 2 - Rotation
        print("\n✓ Test 5: Rotation tab...")
        try:
            rotation_tab = page.locator('div[role="tab"]:has-text("Rotation")')
            rotation_tab.click()
            time.sleep(1)

            # Check for rotation strategy
            strategy_text = page.locator('text=Rotation Stratejisi')
            assert strategy_text.is_visible(), "Rotation strategy not found"

            page.screenshot(path='/tmp/settings_tab2_rotation.png', full_page=True)
            print("  ✅ Rotation tab loaded")
            print("  📸 Screenshot: /tmp/settings_tab2_rotation.png")
        except Exception as e:
            print(f"  ❌ Rotation tab failed: {e}")
            page.screenshot(path='/tmp/settings_tab2_error.png', full_page=True)
            print(f"  📸 Error screenshot: /tmp/settings_tab2_error.png")

        # Test 6: Tab 3 - Statistics
        print("\n✓ Test 6: Statistics tab...")
        try:
            stats_tab = page.locator('div[role="tab"]:has-text("İstatistikler")')
            stats_tab.click()
            time.sleep(1)

            # Check for usage statistics
            usage_stats = page.locator('text=Kullanım İstatistikleri')
            assert usage_stats.is_visible(), "Usage statistics not found"

            page.screenshot(path='/tmp/settings_tab3_statistics.png', full_page=True)
            print("  ✅ Statistics tab loaded")
            print("  📸 Screenshot: /tmp/settings_tab3_statistics.png")
        except Exception as e:
            print(f"  ❌ Statistics tab failed: {e}")
            page.screenshot(path='/tmp/settings_tab3_error.png', full_page=True)
            print(f"  📸 Error screenshot: /tmp/settings_tab3_error.png")

        # Test 7: Tab 4 - Vector Store
        print("\n✓ Test 7: Vector Store tab...")
        try:
            vector_tab = page.locator('div[role="tab"]:has-text("Vector Store")')
            vector_tab.click()
            time.sleep(1)

            # Check for configuration
            config_text = page.locator('text=Konfigürasyon')
            assert config_text.is_visible(), "Configuration not found"

            page.screenshot(path='/tmp/settings_tab4_vectorstore.png', full_page=True)
            print("  ✅ Vector Store tab loaded")
            print("  📸 Screenshot: /tmp/settings_tab4_vectorstore.png")
        except Exception as e:
            print(f"  ❌ Vector Store tab failed: {e}")
            page.screenshot(path='/tmp/settings_tab4_error.png', full_page=True)
            print(f"  📸 Error screenshot: /tmp/settings_tab4_error.png")

        print("\n" + "="*60)
        print("✅ All Settings page tests completed!")
        print("="*60)

        browser.close()

if __name__ == '__main__':
    test_settings()
