"""
Test QA stages - they should show evaluation results, not auto-pass
"""
from playwright.sync_api import sync_playwright
import time

def test_qa_stages():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=600)
        page = browser.new_page()

        page.on("console", lambda msg: print(f"[JS] {msg.text}"))

        print("\n" + "="*80)
        print("TESTING QA STAGES (Should show evaluation, not auto-pass)")
        print("="*80)

        try:
            # Setup
            print("\n[1/6] Setting up pipeline...")
            page.goto('http://localhost:5173/brd-pipeline', timeout=15000)
            time.sleep(2)

            page.locator('.ant-select-selector').first.click()
            time.sleep(0.5)
            page.locator('.ant-select-item').first.click()

            brd_text = """# Test BRD
## Login Ekranı
Kullanıcı email ve şifre ile giriş yapabilir."""

            page.locator('textarea').first.fill(brd_text)
            page.locator('button:has-text("Pipeline Başlat")').click()
            time.sleep(2)
            print("✓ Pipeline started")

            # BA Generation
            print("\n[2/6] BA Generation...")
            page.locator('button:has-text("BA Üret")').click()
            time.sleep(3)
            print("✓ BA generated")

            # BA Review
            print("\n[3/6] BA Review...")
            time.sleep(2)
            if page.locator('.monaco-editor').count() > 0:
                print("✓ Monaco editor visible")

            # Click "Onayla ve QA'ya Geç"
            page.locator('button:has-text("Onayla")').first.click()
            print("✓ Clicked 'Onayla ve QA'ya Geç'")
            time.sleep(2)

            # BA QA Stage - Should show QA evaluation UI
            print("\n[4/6] BA QA Stage - Checking for evaluation UI...")
            time.sleep(1)

            # Check for QA evaluation button
            qa_button = page.locator('button:has-text("QA Değerlendirmesi Yap")')
            if qa_button.count() > 0:
                print("✓ QA Değerlendirmesi button found!")
                page.screenshot(path='/tmp/ba_qa_before_eval.png', full_page=True)
                print("📸 Screenshot: /tmp/ba_qa_before_eval.png")

                # Click QA evaluate
                qa_button.click()
                print("  → Clicked 'QA Değerlendirmesi Yap'")
                time.sleep(3)

                # Check for QA results
                if page.locator('text=QA Başarılı').count() > 0 or page.locator('text=QA Başarısız').count() > 0:
                    print("✓ QA results displayed!")
                    page.screenshot(path='/tmp/ba_qa_after_eval.png', full_page=True)
                    print("📸 Screenshot: /tmp/ba_qa_after_eval.png")

                    # Check for score
                    if page.locator('.ant-progress').count() > 0:
                        print("✓ Score progress bar visible")

                    # Check for next button
                    next_button = page.locator('button:has-text("Sonraki Aşamaya Geç")')
                    if next_button.count() > 0:
                        print("✓ 'Sonraki Aşamaya Geç' button visible")
                    else:
                        print("⚠ Next stage button not found")
                else:
                    print("⚠ QA results not displayed")
            else:
                print("✗ QA Değerlendirmesi button NOT found!")
                print("  This means QA was auto-passed (BUG!)")
                page.screenshot(path='/tmp/ba_qa_stage_error.png', full_page=True)
                print("📸 Screenshot: /tmp/ba_qa_stage_error.png")

            print("\n[5/6] Checking current page state...")
            buttons = page.locator('button:visible').all()
            button_texts = [btn.inner_text() for btn in buttons if btn.inner_text().strip()]
            print(f"  Visible buttons: {button_texts[:10]}")

            print("\n[6/6] Keeping browser open for inspection...")
            time.sleep(15)

            print("\n" + "="*80)
            print("TEST COMPLETED")
            print("="*80)

        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
            page.screenshot(path='/tmp/qa_test_error.png', full_page=True)
            time.sleep(5)

        finally:
            browser.close()

if __name__ == "__main__":
    test_qa_stages()
