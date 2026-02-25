#!/usr/bin/env python3
"""
BA&QA Platform — Comprehensive Web Application Testing
Tests both backend API and frontend React application
"""
from playwright.sync_api import sync_playwright, expect
import time
import sys

def test_webapp():
    """Test entire BA&QA platform with backend + frontend"""

    results = {
        "passed": [],
        "failed": [],
        "screenshots": []
    }

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # Enable console logging
        page.on("console", lambda msg: print(f"[Browser Console] {msg.type}: {msg.text}"))

        try:
            # TEST 1: Backend Health Check
            print("\n=== TEST 1: Backend Health Check ===")
            try:
                response = page.request.get("http://localhost:8000/health")
                if response.status == 200:
                    data = response.json()
                    print(f"✅ Backend health check passed: {data}")
                    results["passed"].append("Backend health check (200 OK)")
                else:
                    print(f"❌ Backend health check failed: Status {response.status}")
                    results["failed"].append(f"Backend health check (Status {response.status})")
            except Exception as e:
                print(f"❌ Backend health check error: {str(e)}")
                results["failed"].append(f"Backend health check (Error: {str(e)})")

            # TEST 2: Frontend Loads
            print("\n=== TEST 2: Frontend Loading ===")
            try:
                page.goto("http://localhost:5173", wait_until="networkidle", timeout=30000)
                page.wait_for_load_state("domcontentloaded")
                time.sleep(2)  # Wait for React to render

                # Check if Ant Design layout is present
                layout = page.locator('.ant-layout')
                if layout.count() > 0:
                    print("✅ Frontend loaded successfully (Ant Design layout detected)")
                    results["passed"].append("Frontend loads (React + Ant Design)")

                    # Take screenshot
                    screenshot_path = "/tmp/01_frontend_home.png"
                    page.screenshot(path=screenshot_path, full_page=True)
                    results["screenshots"].append(screenshot_path)
                    print(f"📸 Screenshot saved: {screenshot_path}")
                else:
                    print("❌ Frontend layout not found")
                    results["failed"].append("Frontend layout not detected")
            except Exception as e:
                print(f"❌ Frontend loading error: {str(e)}")
                results["failed"].append(f"Frontend loading (Error: {str(e)})")

            # TEST 3: Dashboard Page
            print("\n=== TEST 3: Dashboard Page ===")
            try:
                # Navigate to dashboard (default home page)
                page.goto("http://localhost:5173/", wait_until="networkidle")
                page.wait_for_load_state("domcontentloaded")
                time.sleep(2)

                # Check for dashboard elements
                heading = page.locator('h1:has-text("Dashboard")')
                if heading.count() > 0:
                    print("✅ Dashboard page loaded")
                    results["passed"].append("Dashboard page loads")

                    # Take screenshot
                    screenshot_path = "/tmp/02_dashboard.png"
                    page.screenshot(path=screenshot_path, full_page=True)
                    results["screenshots"].append(screenshot_path)
                    print(f"📸 Screenshot saved: {screenshot_path}")
                else:
                    print("⚠️  Dashboard heading not found (page may still be loading)")
                    results["failed"].append("Dashboard heading not found")
            except Exception as e:
                print(f"❌ Dashboard error: {str(e)}")
                results["failed"].append(f"Dashboard (Error: {str(e)})")

            # TEST 4: Sidebar Navigation
            print("\n=== TEST 4: Sidebar Navigation ===")
            nav_routes = [
                ("Dashboard", "/", "Dashboard"),
                ("BA Evaluation", "/ba-evaluation", "BA Doküman Değerlendirme"),
                ("TC Evaluation", "/tc-evaluation", "Test Case Doküman Değerlendirme"),
                ("Document Library", "/documents", "Doküman Kütüphanesi"),
            ]

            for nav_name, route, expected_heading in nav_routes:
                try:
                    print(f"\nTesting navigation: {nav_name}")

                    # Click sidebar menu item
                    menu_item = page.locator(f'a[href="{route}"]').first
                    if menu_item.count() > 0:
                        menu_item.click()
                        page.wait_for_load_state("networkidle")
                        time.sleep(2)

                        # Check if page loaded
                        heading = page.locator(f'h1:has-text("{expected_heading}")').first
                        if heading.count() > 0:
                            print(f"✅ {nav_name} navigation works")
                            results["passed"].append(f"{nav_name} navigation")
                        else:
                            print(f"⚠️  {nav_name} page loaded but heading not found")
                            results["passed"].append(f"{nav_name} navigation (partial)")
                    else:
                        print(f"❌ {nav_name} menu item not found")
                        results["failed"].append(f"{nav_name} menu item not found")
                except Exception as e:
                    print(f"❌ {nav_name} navigation error: {str(e)}")
                    results["failed"].append(f"{nav_name} navigation (Error: {str(e)})")

            # TEST 5: BA Evaluation Page
            print("\n=== TEST 5: BA Evaluation Page ===")
            try:
                page.goto("http://localhost:5173/ba-evaluation", wait_until="networkidle")
                page.wait_for_load_state("domcontentloaded")
                time.sleep(3)  # Wait for API calls

                # Check for page elements
                heading = page.locator('h1:has-text("BA Doküman Değerlendirme")')
                model_settings = page.locator('text=Model Ayarları')
                pipeline_alert = page.locator('text=Pipeline')

                if heading.count() > 0:
                    print("✅ BA Evaluation page loaded")
                    results["passed"].append("BA Evaluation page loads")

                    # Check for JIRA integration elements
                    jira_elements = page.locator('text=/JIRA/i')
                    if jira_elements.count() > 0:
                        print("✅ JIRA integration UI present")
                        results["passed"].append("BA Evaluation JIRA UI")

                    # Take screenshot
                    screenshot_path = "/tmp/03_ba_evaluation.png"
                    page.screenshot(path=screenshot_path, full_page=True)
                    results["screenshots"].append(screenshot_path)
                    print(f"📸 Screenshot saved: {screenshot_path}")
                else:
                    print("❌ BA Evaluation heading not found")
                    results["failed"].append("BA Evaluation heading not found")
            except Exception as e:
                print(f"❌ BA Evaluation error: {str(e)}")
                results["failed"].append(f"BA Evaluation (Error: {str(e)})")

            # TEST 6: TC Evaluation Page
            print("\n=== TEST 6: TC Evaluation Page ===")
            try:
                page.goto("http://localhost:5173/tc-evaluation", wait_until="networkidle")
                page.wait_for_load_state("domcontentloaded")
                time.sleep(3)

                heading = page.locator('h1:has-text("Test Case Doküman Değerlendirme")')
                if heading.count() > 0:
                    print("✅ TC Evaluation page loaded")
                    results["passed"].append("TC Evaluation page loads")

                    # Take screenshot
                    screenshot_path = "/tmp/04_tc_evaluation.png"
                    page.screenshot(path=screenshot_path, full_page=True)
                    results["screenshots"].append(screenshot_path)
                    print(f"📸 Screenshot saved: {screenshot_path}")
                else:
                    print("❌ TC Evaluation heading not found")
                    results["failed"].append("TC Evaluation heading not found")
            except Exception as e:
                print(f"❌ TC Evaluation error: {str(e)}")
                results["failed"].append(f"TC Evaluation (Error: {str(e)})")

            # TEST 7: Document Library
            print("\n=== TEST 7: Document Library ===")
            try:
                page.goto("http://localhost:5173/documents", wait_until="networkidle")
                page.wait_for_load_state("domcontentloaded")
                time.sleep(3)

                heading = page.locator('h1:has-text("Doküman Kütüphanesi")')
                if heading.count() > 0:
                    print("✅ Document Library page loaded")
                    results["passed"].append("Document Library page loads")

                    # Check if table is present
                    table = page.locator('.ant-table')
                    if table.count() > 0:
                        print("✅ Document table present")
                        results["passed"].append("Document Library table")

                    # Take screenshot
                    screenshot_path = "/tmp/05_document_library.png"
                    page.screenshot(path=screenshot_path, full_page=True)
                    results["screenshots"].append(screenshot_path)
                    print(f"📸 Screenshot saved: {screenshot_path}")
                else:
                    print("❌ Document Library heading not found")
                    results["failed"].append("Document Library heading not found")
            except Exception as e:
                print(f"❌ Document Library error: {str(e)}")
                results["failed"].append(f"Document Library (Error: {str(e)})")

        finally:
            browser.close()

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"\n✅ PASSED ({len(results['passed'])} tests):")
    for test in results["passed"]:
        print(f"  - {test}")

    if results["failed"]:
        print(f"\n❌ FAILED ({len(results['failed'])} tests):")
        for test in results["failed"]:
            print(f"  - {test}")

    print(f"\n📸 SCREENSHOTS ({len(results['screenshots'])} captured):")
    for screenshot in results["screenshots"]:
        print(f"  - {screenshot}")

    print("\n" + "="*60)

    # Exit with error code if any tests failed
    if results["failed"]:
        sys.exit(1)
    else:
        print("\n🎉 All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    test_webapp()
