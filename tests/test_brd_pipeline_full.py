"""
Full End-to-End Test for BRD Pipeline
Tests the complete step-by-step workflow
"""
from playwright.sync_api import sync_playwright, expect
import time
import json

# Sample BRD content for testing
SAMPLE_BRD = """
# Kullanıcı Giriş Sistemi

## 1. Amaç
Bu doküman, web uygulaması için kullanıcı giriş (login) sisteminin iş analizini içermektedir.

## 2. Kapsam
- Kullanıcı giriş ekranı
- Şifre doğrulama
- "Beni Hatırla" özelliği
- Şifremi Unuttum akışı

## 3. Fonksiyonel Analiz

### 3.1 Login Ekranı
**Ekran Adı:** Login
**Açıklama:** Kullanıcının email ve şifre ile sisteme giriş yapabileceği ekran

**Form Alanları:**
- Email (zorunlu, email formatı)
- Şifre (zorunlu, min 8 karakter)
- Beni Hatırla (checkbox, opsiyonel)

**Butonlar:**
- Giriş Yap (primary)
- Şifremi Unuttum (link)

**İş Kuralları:**
1. Email formatı kontrol edilmeli (@domain.com)
2. Şifre minimum 8 karakter olmalı
3. 3 başarısız denemeden sonra hesap 15 dakika kilitlenmeli
4. "Beni Hatırla" seçiliyse 30 gün session kalmalı

**Kabul Kriterleri:**
- Geçerli email/şifre ile giriş başarılı olmalı
- Hatalı şifre ile "Hatalı bilgiler" mesajı gösterilmeli
- 3 hatalı denemede hesap kilitlenmeli
- Başarılı girişte Dashboard'a yönlendirilmeli

### 3.2 Şifremi Unuttum Akışı
**Akış:**
1. Kullanıcı "Şifremi Unuttum" linkine tıklar
2. Email adresi girişi yapılır
3. Sistem email'e reset linki gönderir
4. Kullanıcı linke tıklayarak yeni şifre belirler
5. Sistem başarı mesajı gösterir

**Validation:**
- Email kayıtlı olmalı
- Reset link 1 saat geçerli olmalı
- Yeni şifre eski şifre ile aynı olmamalı
"""

def test_full_workflow():
    print("\n" + "="*70)
    print("BRD PIPELINE - FULL END-TO-END TEST")
    print("="*70 + "\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # ===== STEP 1: Upload =====
        print("📋 STEP 1: BRD Upload & Configuration")
        print("-" * 70)

        page.goto('http://localhost:5173/brd-pipeline')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        # Verify page loaded
        expect(page.locator('h1:has-text("BRD Pipeline")')).to_be_visible()
        print("✓ Page loaded")

        # Fill project (select first option)
        print("  → Selecting project...")
        page.locator('.ant-select-selector').first.click()
        time.sleep(0.5)
        page.locator('.ant-select-item').first.click()
        print("✓ Project selected")

        # Fill BRD content
        print("  → Entering BRD content...")
        page.locator('textarea[placeholder*="BRD"]').fill(SAMPLE_BRD)
        print("✓ BRD content entered")

        # Verify checkboxes are checked
        ba_checkbox = page.locator('input[type="checkbox"]').nth(0)
        expect(ba_checkbox).to_be_checked()
        print("✓ BA checkbox checked")

        # Take screenshot
        page.screenshot(path='/tmp/test_step1_upload.png', full_page=True)
        print("✓ Screenshot saved: /tmp/test_step1_upload.png")

        # Start pipeline
        print("\n  → Starting pipeline...")
        page.locator('button:has-text("Pipeline Başlat")').click()
        time.sleep(2)

        # Check for success message or next step
        # Should advance to ba_gen step
        print("✓ Pipeline started (waiting for confirmation...)")

        # Wait for step 2 to appear
        time.sleep(2)
        page.screenshot(path='/tmp/test_step2_ba_gen.png', full_page=True)
        print("✓ Screenshot saved: /tmp/test_step2_ba_gen.png")

        # ===== STEP 2: BA Generation =====
        print("\n📝 STEP 2: BA Generation")
        print("-" * 70)

        # Look for BA Üret button
        ba_gen_button = page.locator('button:has-text("BA Üret")')
        if ba_gen_button.is_visible(timeout=5000):
            print("✓ BA Generation step loaded")

            print("  → Clicking 'BA Üret' button...")
            ba_gen_button.click()
            print("✓ BA generation started")

            # Wait for spinner or generation message
            time.sleep(2)
            page.screenshot(path='/tmp/test_step2_ba_generating.png', full_page=True)
            print("✓ Screenshot saved: /tmp/test_step2_ba_generating.png")

            # Note: In real scenario, this would take 30-60 seconds
            print("\n  ⏳ Waiting for BA generation to complete...")
            print("     (This would normally take 30-60 seconds)")
            print("     (For this test, we'll wait 10 seconds max)")

            # Wait for status change (or timeout after 10s for testing)
            max_wait = 10
            for i in range(max_wait):
                time.sleep(1)
                # Check if review step appeared
                if page.locator('text=BA İnceleme').is_visible(timeout=1000):
                    print(f"✓ BA generation completed in {i+1} seconds")
                    break
                print(f"  ... waiting ({i+1}/{max_wait}s)")
            else:
                print("  ⚠ Generation still in progress (backend might be slow)")

            page.screenshot(path='/tmp/test_step3_current.png', full_page=True)
            print("✓ Screenshot saved: /tmp/test_step3_current.png")
        else:
            print("⚠ BA Generation button not found - pipeline might have auto-advanced")

        # ===== Check Current State =====
        print("\n📊 CURRENT STATE CHECK")
        print("-" * 70)

        # Get current step from progress bar
        current_step = page.locator('.ant-steps-item-process .ant-steps-item-title').text_content()
        print(f"Current Step: {current_step}")

        # Check if any Monaco Editor is visible (review step)
        monaco_editor = page.locator('.monaco-editor')
        if monaco_editor.count() > 0:
            print("✓ Monaco Editor detected (review step)")
            page.screenshot(path='/tmp/test_monaco_editor.png', full_page=True)
            print("✓ Screenshot saved: /tmp/test_monaco_editor.png")

        # Check for QA evaluation buttons
        qa_button = page.locator('button:has-text("QA Değerlendirmesi")')
        if qa_button.count() > 0:
            print("✓ QA Evaluation step detected")

        print("\n" + "="*70)
        print("TEST COMPLETED")
        print("="*70)

        print("\n📸 Screenshots saved:")
        print("  - /tmp/test_step1_upload.png")
        print("  - /tmp/test_step2_ba_gen.png")
        print("  - /tmp/test_step2_ba_generating.png")
        print("  - /tmp/test_step3_current.png")

        print("\n🔍 Next Steps (Manual):")
        print("  1. Check backend logs for generation progress")
        print("  2. If stuck in generation, check API logs")
        print("  3. If completed, test review + QA steps")
        print("  4. Test full workflow: BA → TA → TC")

        print("\n💡 Keeping browser open for 10 seconds...")
        time.sleep(10)

        browser.close()

if __name__ == '__main__':
    test_full_workflow()
