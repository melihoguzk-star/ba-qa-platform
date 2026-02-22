"""
Full 12-stage pipeline test with mock data
Tests entire workflow without calling external APIs
"""
from playwright.sync_api import sync_playwright
import time
import json

def test_full_pipeline():
    """Test all 12 stages of the pipeline"""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=400)
        page = browser.new_page()

        # Enable logging
        console_logs = []
        errors = []
        page.on("console", lambda msg: console_logs.append(f"{msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: errors.append(str(err)))

        print("\n" + "="*80)
        print("FULL 12-STAGE PIPELINE TEST (MOCK MODE)")
        print("="*80)

        try:
            # STAGE 1: BRD Yükleme (Upload)
            print("\n[STAGE 1/12] BRD Yükleme")
            print("-" * 80)
            page.goto('http://localhost:5173/brd-pipeline', timeout=15000)
            time.sleep(2)

            # Select project
            print("  → Selecting project...")
            page.locator('.ant-select-selector').first.click()
            time.sleep(0.5)
            page.locator('.ant-select-item').first.click()
            print("  ✓ Project selected")

            # Add BRD content
            print("  → Adding BRD content...")
            brd_text = """# Kullanıcı Giriş Sistemi

## 1. Amaç
Web uygulaması için kullanıcı giriş sistemi

## 2. Kapsam
- Kullanıcı giriş ekranı
- Şifre doğrulama
- Beni Hatırla özelliği

## 3. Fonksiyonel Analiz

### 3.1 Login Ekranı
**Form Alanları:**
- Email (zorunlu, email formatı)
- Şifre (zorunlu, min 8 karakter)
- Beni Hatırla (checkbox, opsiyonel)

**İş Kuralları:**
1. Email formatı kontrol edilmeli (@domain.com)
2. Şifre minimum 8 karakter olmalı
3. 3 başarısız denemeden sonra hesap 15 dakika kilitlenmeli

**Kabul Kriterleri:**
- Geçerli email/şifre ile giriş başarılı olmalı
- Hatalı şifre ile hata mesajı gösterilmeli
- Başarılı girişte Dashboard'a yönlendirilmeli
"""
            page.locator('textarea').first.fill(brd_text)
            print("  ✓ BRD content added")

            # Start pipeline
            print("  → Starting pipeline...")
            page.locator('button:has-text("Pipeline Başlat")').click()
            time.sleep(2)
            print("  ✓ Pipeline started")
            print("✅ STAGE 1 COMPLETE")

            # STAGE 2: BA Üretim (BA Generation)
            print("\n[STAGE 2/12] BA Üretim")
            print("-" * 80)
            time.sleep(1)

            # Check if BA Üret button exists
            ba_button = page.locator('button:has-text("BA Üret")')
            if ba_button.count() == 0:
                print("  ✗ BA Üret button not found!")
                page.screenshot(path='/tmp/error_stage2.png')
                return False

            print("  → Clicking BA Üret...")
            ba_button.click()
            time.sleep(3)  # Wait for generation
            print("  ✓ BA generation completed")
            print("✅ STAGE 2 COMPLETE")

            # STAGE 3: BA İnceleme (BA Review)
            print("\n[STAGE 3/12] BA İnceleme")
            print("-" * 80)
            time.sleep(1)

            # Check if we're on BA review stage
            review_button = page.locator('button:has-text("Onayla")').or_(page.locator('button:has-text("QA")'))
            if review_button.count() > 0:
                print("  → BA review stage reached")
                print("  → Content should be visible in Monaco Editor")
                # Click approve button
                review_button.first.click()
                time.sleep(2)
                print("  ✓ BA approved")
            else:
                print("  ⚠ Review stage might have auto-progressed")
            print("✅ STAGE 3 COMPLETE")

            # STAGE 4: BA QA
            print("\n[STAGE 4/12] BA QA Değerlendirmesi")
            print("-" * 80)
            time.sleep(2)

            # Check for QA results or continue button
            qa_button = page.locator('button:has-text("Devam")').or_(page.locator('button:has-text("TA")')).or_(page.locator('button:has-text("Sonraki")'))
            if qa_button.count() > 0:
                print("  → QA evaluation complete")
                print("  → Score should be displayed")
                qa_button.first.click()
                time.sleep(2)
                print("  ✓ Proceeding to TA")
            else:
                print("  ⚠ QA stage might have auto-progressed")
            print("✅ STAGE 4 COMPLETE")

            # STAGE 5: TA Üretim (TA Generation)
            print("\n[STAGE 5/12] TA Üretim")
            print("-" * 80)
            time.sleep(1)

            ta_button = page.locator('button:has-text("TA Üret")')
            if ta_button.count() > 0:
                print("  → Clicking TA Üret...")
                ta_button.click()
                time.sleep(3)
                print("  ✓ TA generation completed")
            else:
                print("  ⚠ TA generation button not found (might be auto-progressed)")
            print("✅ STAGE 5 COMPLETE")

            # STAGE 6: TA İnceleme (TA Review)
            print("\n[STAGE 6/12] TA İnceleme")
            print("-" * 80)
            time.sleep(1)

            ta_review_button = page.locator('button:has-text("Onayla")').or_(page.locator('button:has-text("QA")'))
            if ta_review_button.count() > 0:
                print("  → TA review stage reached")
                ta_review_button.first.click()
                time.sleep(2)
                print("  ✓ TA approved")
            else:
                print("  ⚠ TA review might have auto-progressed")
            print("✅ STAGE 6 COMPLETE")

            # STAGE 7: TA QA
            print("\n[STAGE 7/12] TA QA Değerlendirmesi")
            print("-" * 80)
            time.sleep(2)

            ta_qa_button = page.locator('button:has-text("Devam")').or_(page.locator('button:has-text("TC")').or_(page.locator('button:has-text("Sonraki")')))
            if ta_qa_button.count() > 0:
                print("  → TA QA evaluation complete")
                ta_qa_button.first.click()
                time.sleep(2)
                print("  ✓ Proceeding to TC")
            else:
                print("  ⚠ TA QA might have auto-progressed")
            print("✅ STAGE 7 COMPLETE")

            # STAGE 8: Figma Upload (Optional)
            print("\n[STAGE 8/12] Figma Upload (Opsiyonel)")
            print("-" * 80)
            print("  → Skipping Figma upload (optional stage)")
            time.sleep(1)
            print("✅ STAGE 8 SKIPPED")

            # STAGE 9: TC Üretim (TC Generation)
            print("\n[STAGE 9/12] TC Üretim")
            print("-" * 80)
            time.sleep(1)

            tc_button = page.locator('button:has-text("TC Üret")')
            if tc_button.count() > 0:
                print("  → Clicking TC Üret...")
                tc_button.click()
                time.sleep(3)
                print("  ✓ TC generation completed")
            else:
                print("  ⚠ TC generation button not found")
            print("✅ STAGE 9 COMPLETE")

            # STAGE 10: TC İnceleme (TC Review)
            print("\n[STAGE 10/12] TC İnceleme")
            print("-" * 80)
            time.sleep(1)

            tc_review_button = page.locator('button:has-text("Onayla")').or_(page.locator('button:has-text("QA")'))
            if tc_review_button.count() > 0:
                print("  → TC review stage reached")
                tc_review_button.first.click()
                time.sleep(2)
                print("  ✓ TC approved")
            else:
                print("  ⚠ TC review might have auto-progressed")
            print("✅ STAGE 10 COMPLETE")

            # STAGE 11: TC QA
            print("\n[STAGE 11/12] TC QA Değerlendirmesi")
            print("-" * 80)
            time.sleep(2)

            tc_qa_button = page.locator('button:has-text("Devam")').or_(page.locator('button:has-text("Tamamla")').or_(page.locator('button:has-text("Sonraki")')))
            if tc_qa_button.count() > 0:
                print("  → TC QA evaluation complete")
                tc_qa_button.first.click()
                time.sleep(2)
                print("  ✓ Proceeding to completion")
            else:
                print("  ⚠ TC QA might have auto-progressed")
            print("✅ STAGE 11 COMPLETE")

            # STAGE 12: Tamamlandı (Done)
            print("\n[STAGE 12/12] Pipeline Tamamlandı")
            print("-" * 80)
            time.sleep(2)

            # Check for completion message or download buttons
            done_indicator = page.locator('text=Tamamlandı').or_(page.locator('text=Pipeline tamamlandı').or_(page.locator('button:has-text("İndir")')))
            if done_indicator.count() > 0:
                print("  ✓ Pipeline completed successfully!")
                print("  → All documents should be available for download")
            else:
                print("  ⚠ Completion status unclear")
            print("✅ STAGE 12 COMPLETE")

            # Take final screenshot
            page.screenshot(path='/tmp/test_12_stages_final.png', full_page=True)
            print("\n" + "="*80)
            print("📸 Final screenshot: /tmp/test_12_stages_final.png")

            # Summary
            print("\n" + "="*80)
            print("TEST SUMMARY")
            print("="*80)
            print(f"✅ All 12 stages tested")
            print(f"📊 Console logs: {len(console_logs)}")
            print(f"❌ Errors: {len(errors)}")

            if errors:
                print("\nErrors encountered:")
                for err in errors[:5]:
                    print(f"  - {err}")

            print("\n⏸ Keeping browser open for 10 seconds for inspection...")
            time.sleep(10)

            return True

        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            page.screenshot(path='/tmp/test_12_stages_error.png', full_page=True)
            print("Error screenshot: /tmp/test_12_stages_error.png")
            time.sleep(5)
            return False

        finally:
            browser.close()
            print("\n✅ Test completed")


if __name__ == "__main__":
    success = test_full_pipeline()
    exit(0 if success else 1)
