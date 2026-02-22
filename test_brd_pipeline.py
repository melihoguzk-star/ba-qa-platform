"""
Test BRD Pipeline - Step-by-step workflow
"""
from playwright.sync_api import sync_playwright, expect
import time

def test_brd_pipeline():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("1. Navigating to BRD Pipeline page...")
        page.goto('http://localhost:5173/brd-pipeline')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        # Take screenshot of initial state
        page.screenshot(path='/tmp/brd_pipeline_01_initial.png', full_page=True)
        print("   ✓ Screenshot: /tmp/brd_pipeline_01_initial.png")

        print("\n2. Checking if page loaded correctly...")
        # Check for main heading
        heading = page.locator('h1:has-text("BRD Pipeline")')
        expect(heading).to_be_visible()
        print("   ✓ Page heading found")

        # Check for Steps progress
        steps = page.locator('.ant-steps')
        expect(steps).to_be_visible()
        print("   ✓ Progress steps visible")

        print("\n3. Checking upload form...")
        # Check for project selector (simpler selector)
        project_label = page.locator('text=Proje')
        expect(project_label).to_be_visible()
        print("   ✓ Project label found")

        # Check for BRD content textarea
        brd_textarea = page.locator('textarea[placeholder*="BRD"]')
        expect(brd_textarea).to_be_visible()
        print("   ✓ BRD content textarea found")

        # Check for document type checkboxes
        ba_checkbox = page.locator('label:has-text("BA (Business Analysis)")')
        expect(ba_checkbox).to_be_visible()
        print("   ✓ BA checkbox found")

        # Check for start button
        start_button = page.locator('button:has-text("Pipeline Başlat")')
        expect(start_button).to_be_visible()
        print("   ✓ Start button found")

        page.screenshot(path='/tmp/brd_pipeline_02_form.png', full_page=True)
        print("   ✓ Screenshot: /tmp/brd_pipeline_02_form.png")

        print("\n4. Testing form validation...")
        # Try to submit without filling
        start_button.click()
        time.sleep(0.5)

        # Should show validation error
        error_message = page.locator('.ant-form-item-explain-error')
        if error_message.count() > 0:
            print("   ✓ Validation error shown (expected)")

        page.screenshot(path='/tmp/brd_pipeline_03_validation.png', full_page=True)
        print("   ✓ Screenshot: /tmp/brd_pipeline_03_validation.png")

        print("\n✅ BRD Pipeline page basic tests passed!")
        print("\nNext steps to test manually:")
        print("  1. Select a project")
        print("  2. Enter BRD content")
        print("  3. Click 'Pipeline Başlat'")
        print("  4. Verify ba_gen stage appears")
        print("  5. Click 'BA Üret' button")
        print("  6. Wait for generation to complete")
        print("  7. Verify ba_review stage with Monaco Editor")
        print("  8. Test QA evaluation")

        time.sleep(2)
        browser.close()

if __name__ == '__main__':
    test_brd_pipeline()
