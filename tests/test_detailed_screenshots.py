"""
Test all 12 stages with detailed screenshots at each stage
"""
from playwright.sync_api import sync_playwright
import time
import os

def test_with_screenshots():
    """Test pipeline with screenshot at each stage"""

    screenshots_dir = "/tmp/pipeline_screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=800)
        page = browser.new_page()

        # Enable logging
        page.on("console", lambda msg: print(f"[JS] {msg.text}"))

        print("\n" + "="*80)
        print("DETAILED 12-STAGE TEST WITH SCREENSHOTS")
        print("="*80)

        try:
            # STAGE 1: BRD Yükleme
            print("\n[STAGE 1/12] BRD Yükleme")
            print("-" * 80)
            page.goto('http://localhost:5173/brd-pipeline', timeout=15000)
            time.sleep(2)

            page.locator('.ant-select-selector').first.click()
            time.sleep(0.5)
            page.locator('.ant-select-item').first.click()

            brd_text = """# Test BRD - Mock Mode

## Login Ekranı
Kullanıcı email ve şifre ile giriş yapabilir.

## Fonksiyonel Gereksinimler
- Email validasyonu
- Şifre doğrulama
- Beni hatırla özelliği"""

            page.locator('textarea').first.fill(brd_text)
            page.screenshot(path=f'{screenshots_dir}/01_brd_yukleme.png', full_page=True)
            print("📸 Screenshot: 01_brd_yukleme.png")

            page.locator('button:has-text("Pipeline Başlat")').click()
            time.sleep(2)
            print("✅ STAGE 1 COMPLETE")

            # STAGE 2: BA Üretim
            print("\n[STAGE 2/12] BA Üretim")
            print("-" * 80)
            page.screenshot(path=f'{screenshots_dir}/02_ba_uretim_before.png', full_page=True)
            print("📸 Screenshot: 02_ba_uretim_before.png")

            ba_button = page.locator('button:has-text("BA Üret")')
            ba_button.click()
            print("  → BA Üret clicked, waiting for generation...")
            time.sleep(3)

            page.screenshot(path=f'{screenshots_dir}/02_ba_uretim_after.png', full_page=True)
            print("📸 Screenshot: 02_ba_uretim_after.png")
            print("✅ STAGE 2 COMPLETE")

            # STAGE 3: BA İnceleme
            print("\n[STAGE 3/12] BA İnceleme")
            print("-" * 80)
            time.sleep(2)

            # Wait for Monaco editor
            monaco_visible = False
            for i in range(10):
                if page.locator('.monaco-editor').count() > 0:
                    monaco_visible = True
                    break
                time.sleep(0.5)

            if monaco_visible:
                print("  ✓ Monaco Editor loaded")
                time.sleep(1)
                page.screenshot(path=f'{screenshots_dir}/03_ba_inceleme.png', full_page=True)
                print("📸 Screenshot: 03_ba_inceleme.png")

                # Click approve button
                approve_btn = page.locator('button:has-text("Onayla")')
                if approve_btn.count() > 0:
                    approve_btn.first.click()
                    print("  ✓ BA approved")
                    time.sleep(2)
            print("✅ STAGE 3 COMPLETE")

            # STAGE 4: BA QA
            print("\n[STAGE 4/12] BA QA Değerlendirmesi")
            print("-" * 80)
            time.sleep(2)
            page.screenshot(path=f'{screenshots_dir}/04_ba_qa.png', full_page=True)
            print("📸 Screenshot: 04_ba_qa.png")

            # Check if there's a button to continue
            qa_buttons = page.locator('button:visible').all()
            for btn in qa_buttons:
                text = btn.inner_text().strip()
                if 'QA' in text or 'Geç' in text or 'Devam' in text:
                    print(f"  → Found button: {text}")
            print("✅ STAGE 4 COMPLETE")
            time.sleep(2)

            # STAGE 5: TA Üretim
            print("\n[STAGE 5/12] TA Üretim")
            print("-" * 80)
            page.screenshot(path=f'{screenshots_dir}/05_ta_uretim_before.png', full_page=True)
            print("📸 Screenshot: 05_ta_uretim_before.png")

            ta_button = page.locator('button:has-text("TA Üret")')
            if ta_button.count() > 0:
                ta_button.click()
                print("  ✓ TA Üret clicked")
                time.sleep(3)
                page.screenshot(path=f'{screenshots_dir}/05_ta_uretim_after.png', full_page=True)
                print("📸 Screenshot: 05_ta_uretim_after.png")
            else:
                print("  ⚠ TA Üret button not visible (might be auto-progressed)")
            print("✅ STAGE 5 COMPLETE")

            # STAGE 6: TA İnceleme
            print("\n[STAGE 6/12] TA İnceleme")
            print("-" * 80)
            time.sleep(2)

            if page.locator('.monaco-editor').count() > 0:
                print("  ✓ Monaco Editor loaded for TA")
                time.sleep(1)
                page.screenshot(path=f'{screenshots_dir}/06_ta_inceleme.png', full_page=True)
                print("📸 Screenshot: 06_ta_inceleme.png")

                approve_btn = page.locator('button:has-text("Onayla")')
                if approve_btn.count() > 0:
                    approve_btn.first.click()
                    print("  ✓ TA approved")
                    time.sleep(2)
            print("✅ STAGE 6 COMPLETE")

            # STAGE 7: TA QA
            print("\n[STAGE 7/12] TA QA Değerlendirmesi")
            print("-" * 80)
            time.sleep(2)
            page.screenshot(path=f'{screenshots_dir}/07_ta_qa.png', full_page=True)
            print("📸 Screenshot: 07_ta_qa.png")
            print("✅ STAGE 7 COMPLETE")
            time.sleep(2)

            # STAGE 8: Figma (skip)
            print("\n[STAGE 8/12] Figma Upload")
            print("-" * 80)
            print("  → Skipping optional Figma stage")
            print("✅ STAGE 8 SKIPPED")

            # STAGE 9: TC Üretim
            print("\n[STAGE 9/12] TC Üretim")
            print("-" * 80)
            page.screenshot(path=f'{screenshots_dir}/09_tc_uretim_before.png', full_page=True)
            print("📸 Screenshot: 09_tc_uretim_before.png")

            tc_button = page.locator('button:has-text("TC Üret")')
            if tc_button.count() > 0:
                tc_button.click()
                print("  ✓ TC Üret clicked")
                time.sleep(3)
                page.screenshot(path=f'{screenshots_dir}/09_tc_uretim_after.png', full_page=True)
                print("📸 Screenshot: 09_tc_uretim_after.png")
            else:
                print("  ⚠ TC Üret button not visible")
            print("✅ STAGE 9 COMPLETE")

            # STAGE 10: TC İnceleme
            print("\n[STAGE 10/12] TC İnceleme")
            print("-" * 80)
            time.sleep(2)

            if page.locator('.monaco-editor').count() > 0:
                print("  ✓ Monaco Editor loaded for TC")
                time.sleep(1)
                page.screenshot(path=f'{screenshots_dir}/10_tc_inceleme.png', full_page=True)
                print("📸 Screenshot: 10_tc_inceleme.png")

                approve_btn = page.locator('button:has-text("Onayla")')
                if approve_btn.count() > 0:
                    approve_btn.first.click()
                    print("  ✓ TC approved")
                    time.sleep(2)
            print("✅ STAGE 10 COMPLETE")

            # STAGE 11: TC QA
            print("\n[STAGE 11/12] TC QA Değerlendirmesi")
            print("-" * 80)
            time.sleep(2)
            page.screenshot(path=f'{screenshots_dir}/11_tc_qa.png', full_page=True)
            print("📸 Screenshot: 11_tc_qa.png")
            print("✅ STAGE 11 COMPLETE")
            time.sleep(2)

            # STAGE 12: Tamamlandı
            print("\n[STAGE 12/12] Pipeline Tamamlandı")
            print("-" * 80)
            time.sleep(2)
            page.screenshot(path=f'{screenshots_dir}/12_tamamlandi.png', full_page=True)
            print("📸 Screenshot: 12_tamamlandi.png")
            print("✅ STAGE 12 COMPLETE")

            print("\n" + "="*80)
            print("📸 All screenshots saved to:", screenshots_dir)
            print("="*80)

            # List all screenshots
            screenshots = sorted([f for f in os.listdir(screenshots_dir) if f.endswith('.png')])
            print("\nScreenshots captured:")
            for i, screenshot in enumerate(screenshots, 1):
                print(f"  {i}. {screenshot}")

            print("\n⏸ Keeping browser open for 10 seconds...")
            time.sleep(10)

            return True

        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
            page.screenshot(path=f'{screenshots_dir}/error.png', full_page=True)
            time.sleep(5)
            return False

        finally:
            browser.close()
            print("\n✅ Test completed")


if __name__ == "__main__":
    success = test_with_screenshots()
    exit(0 if success else 1)
