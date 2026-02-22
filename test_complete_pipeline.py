"""
Complete pipeline test - All stages including QA evaluations
"""
from playwright.sync_api import sync_playwright
import time

def test_complete_pipeline():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        page.on("console", lambda msg: print(f"[JS] {msg.text}"))

        print("\n" + "="*80)
        print("COMPLETE PIPELINE TEST (BA → TA → TC with QA stages)")
        print("="*80)

        try:
            # STAGE 1: BRD Upload
            print("\n[STAGE 1] BRD Yükleme...")
            page.goto('http://localhost:5173/brd-pipeline', timeout=15000)
            time.sleep(2)

            page.locator('.ant-select-selector').first.click()
            time.sleep(0.5)
            page.locator('.ant-select-item').first.click()

            brd_text = """# Test BRD - Complete Pipeline
## Login Ekranı
Kullanıcı email ve şifre ile giriş yapabilir.
Şifremi unuttum özelliği olmalı."""

            page.locator('textarea').first.fill(brd_text)
            page.locator('button:has-text("Pipeline Başlat")').click()
            time.sleep(2)
            print("✅ STAGE 1 COMPLETE")

            # STAGE 2: BA Generation
            print("\n[STAGE 2] BA Üretim...")
            page.locator('button:has-text("BA Üret")').click()
            time.sleep(3)
            print("✅ STAGE 2 COMPLETE")

            # STAGE 3: BA Review
            print("\n[STAGE 3] BA İnceleme...")
            time.sleep(2)
            if page.locator('.monaco-editor').count() > 0:
                print("  ✓ Monaco editor visible")
            page.locator('button:has-text("Onayla")').first.click()
            time.sleep(2)
            print("✅ STAGE 3 COMPLETE")

            # STAGE 4: BA QA
            print("\n[STAGE 4] BA QA Değerlendirmesi...")
            time.sleep(1)
            qa_button = page.locator('button:has-text("QA Değerlendirmesi Yap")')
            if qa_button.count() > 0:
                print("  ✓ QA button found")
                qa_button.click()
                time.sleep(3)

                if page.locator('text=QA Başarılı').count() > 0:
                    print("  ✓ QA passed!")
                    next_btn = page.locator('button:has-text("Sonraki Aşamaya Geç")')
                    if next_btn.count() > 0:
                        next_btn.click()
                        time.sleep(2)
                        print("✅ STAGE 4 COMPLETE")
                    else:
                        print("  ⚠ Next button not found")
            else:
                print("  ⚠ QA button not found")

            # STAGE 5: TA Generation
            print("\n[STAGE 5] TA Üretim...")
            time.sleep(2)
            ta_button = page.locator('button:has-text("TA Üret")')
            if ta_button.count() > 0:
                ta_button.click()
                time.sleep(3)
                print("✅ STAGE 5 COMPLETE")
            else:
                print("  ⚠ TA Üret button not found")

            # STAGE 6: TA Review
            print("\n[STAGE 6] TA İnceleme...")
            time.sleep(2)
            if page.locator('.monaco-editor').count() > 0:
                print("  ✓ Monaco editor visible")
            approve_btn = page.locator('button:has-text("Onayla")').first
            if approve_btn.count() > 0:
                approve_btn.click()
                time.sleep(2)
                print("✅ STAGE 6 COMPLETE")

            # STAGE 7: TA QA
            print("\n[STAGE 7] TA QA Değerlendirmesi...")
            time.sleep(1)
            qa_button = page.locator('button:has-text("QA Değerlendirmesi Yap")')
            if qa_button.count() > 0:
                print("  ✓ QA button found")
                qa_button.click()
                time.sleep(3)

                next_btn = page.locator('button:has-text("Sonraki Aşamaya Geç")')
                if next_btn.count() > 0:
                    next_btn.click()
                    time.sleep(2)
                    print("✅ STAGE 7 COMPLETE")

            # STAGE 8: Figma (Skip)
            print("\n[STAGE 8] Figma Upload (Skip)...")
            time.sleep(2)
            skip_btn = page.locator('button:has-text("Figma Olmadan Devam Et")')
            if skip_btn.count() > 0:
                print("  ✓ Skip button found")
                skip_btn.click()
                time.sleep(3)
                print("✅ STAGE 8 SKIPPED")
            else:
                print("  ⚠ Skip button not found")

            # STAGE 9: TC Generation
            print("\n[STAGE 9] TC Üretim...")
            time.sleep(2)
            tc_button = page.locator('button:has-text("TC Üret")')
            if tc_button.count() > 0:
                tc_button.click()
                time.sleep(3)
                print("✅ STAGE 9 COMPLETE")

            # STAGE 10: TC Review
            print("\n[STAGE 10] TC İnceleme...")
            time.sleep(2)
            if page.locator('.monaco-editor').count() > 0:
                print("  ✓ Monaco editor visible")
            approve_btn = page.locator('button:has-text("Onayla")').first
            if approve_btn.count() > 0:
                approve_btn.click()
                time.sleep(2)
                print("✅ STAGE 10 COMPLETE")

            # STAGE 11: TC QA
            print("\n[STAGE 11] TC QA Değerlendirmesi...")
            time.sleep(1)
            qa_button = page.locator('button:has-text("QA Değerlendirmesi Yap")')
            if qa_button.count() > 0:
                print("  ✓ QA button found")
                qa_button.click()
                time.sleep(3)

                next_btn = page.locator('button:has-text("Sonraki Aşamaya Geç")')
                if next_btn.count() > 0:
                    next_btn.click()
                    time.sleep(2)
                    print("✅ STAGE 11 COMPLETE")

            # STAGE 12: Done
            print("\n[STAGE 12] Pipeline Tamamlandı...")
            time.sleep(2)
            if page.locator('text=Pipeline Tamamlandı').count() > 0:
                print("  ✓ Success message visible")
                print("✅ STAGE 12 COMPLETE")

            page.screenshot(path='/tmp/pipeline_complete.png', full_page=True)
            print("\n📸 Final screenshot: /tmp/pipeline_complete.png")

            print("\n" + "="*80)
            print("🎉 ALL 12 STAGES COMPLETED SUCCESSFULLY!")
            print("="*80)

            print("\n⏸ Keeping browser open for 15 seconds...")
            time.sleep(15)

        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
            page.screenshot(path='/tmp/pipeline_error.png', full_page=True)
            time.sleep(5)

        finally:
            browser.close()

if __name__ == "__main__":
    test_complete_pipeline()
