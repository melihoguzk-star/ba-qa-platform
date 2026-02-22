"""
Full BRD Pipeline Test - BA Üret butonunu test eder
"""
from playwright.sync_api import sync_playwright
import time
import json

def test_ba_uret_button():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        # Enable console and error logging
        console_logs = []
        errors = []

        page.on("console", lambda msg: console_logs.append(f"{msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: errors.append(str(err)))

        # Monitor network requests
        requests = []
        responses = []

        def log_request(request):
            if '/api/' in request.url:
                requests.append({
                    'method': request.method,
                    'url': request.url,
                    'time': time.time()
                })

        def log_response(response):
            if '/api/' in response.url:
                responses.append({
                    'status': response.status,
                    'url': response.url,
                    'time': time.time()
                })

        page.on("request", log_request)
        page.on("response", log_response)

        print("\n" + "="*80)
        print("BRD PIPELINE - FULL TEST")
        print("="*80)

        # Step 1: Open page
        print("\n[1/7] Opening BRD Pipeline page...")
        page.goto('http://localhost:5173/brd-pipeline')
        page.wait_for_load_state('networkidle')
        time.sleep(1)
        print("✓ Page loaded")

        # Step 2: Select project
        print("\n[2/7] Selecting project...")
        try:
            # Wait for project dropdown to be visible
            page.wait_for_selector('.ant-select-selector', timeout=5000)
            page.locator('.ant-select-selector').first.click()
            time.sleep(0.5)

            # Select first project
            page.wait_for_selector('.ant-select-item', timeout=5000)
            project_items = page.locator('.ant-select-item').all()
            if project_items:
                project_items[0].click()
                print(f"✓ Project selected ({len(project_items)} projects available)")
            else:
                print("✗ No projects found!")
                return
        except Exception as e:
            print(f"✗ Failed to select project: {e}")
            return

        time.sleep(1)

        # Step 3: Add BRD content
        print("\n[3/7] Adding BRD content...")
        brd_content = """# Kullanıcı Giriş Sistemi

## 1. Amaç
Web uygulaması için kullanıcı giriş sistemi

## 2. Kapsam
- Kullanıcı giriş ekranı
- Şifre doğrulama
- Beni Hatırla özelliği

## 3. Fonksiyonel Analiz

### 3.1 Login Ekranı
**Ekran Adı:** Login
**Açıklama:** Kullanıcının email ve şifre ile sisteme giriş yapabileceği ekran

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

        try:
            textarea = page.locator('textarea').first
            textarea.fill(brd_content)
            print(f"✓ BRD content added ({len(brd_content)} characters)")
        except Exception as e:
            print(f"✗ Failed to add BRD content: {e}")
            return

        time.sleep(1)

        # Step 4: Start pipeline
        print("\n[4/7] Starting pipeline...")
        try:
            start_button = page.locator('button:has-text("Pipeline Başlat")')
            start_button.click()
            print("✓ Clicked 'Pipeline Başlat' button")
            time.sleep(3)

            # Check for success message
            success_messages = page.locator('.ant-message-success').all()
            if success_messages:
                print("✓ Success message appeared")
            else:
                print("⚠ No success message (might still be OK)")
        except Exception as e:
            print(f"✗ Failed to start pipeline: {e}")
            page.screenshot(path='/tmp/error_pipeline_start.png', full_page=True)
            print("Screenshot saved: /tmp/error_pipeline_start.png")
            return

        time.sleep(2)

        # Step 5: Check for BA Üretim stage
        print("\n[5/7] Checking for BA Üretim stage...")
        try:
            # Look for BA Üret button
            ba_uret_button = page.locator('button:has-text("BA Üret")')
            if ba_uret_button.count() > 0:
                print("✓ BA Üret button found")

                # Check if button is enabled
                is_disabled = ba_uret_button.is_disabled()
                print(f"  Button disabled: {is_disabled}")

                # Get button attributes
                button_html = ba_uret_button.evaluate('el => el.outerHTML')
                print(f"  Button HTML: {button_html[:200]}")
            else:
                print("✗ BA Üret button NOT found")
                print("\nSearching for any buttons on page:")
                all_buttons = page.locator('button').all()
                for i, btn in enumerate(all_buttons[:10]):
                    text = btn.inner_text()
                    print(f"  Button {i+1}: '{text}'")

                page.screenshot(path='/tmp/error_no_ba_button.png', full_page=True)
                print("\nScreenshot saved: /tmp/error_no_ba_button.png")
                return
        except Exception as e:
            print(f"✗ Error checking BA button: {e}")
            page.screenshot(path='/tmp/error_ba_check.png', full_page=True)
            return

        time.sleep(1)

        # Step 6: Click BA Üret button
        print("\n[6/7] Clicking BA Üret button...")
        try:
            # Clear previous requests/responses
            requests.clear()
            responses.clear()

            ba_uret_button.click()
            print("✓ Clicked 'BA Üret' button")

            # Wait a bit for request to be sent
            time.sleep(2)

            # Check network activity
            print(f"\n  Network activity after click:")
            print(f"  - Requests: {len(requests)}")
            print(f"  - Responses: {len(responses)}")

            if requests:
                print("\n  API Requests made:")
                for req in requests:
                    print(f"    {req['method']} {req['url']}")
            else:
                print("  ⚠ NO API REQUESTS MADE!")

            if responses:
                print("\n  API Responses received:")
                for resp in responses:
                    print(f"    {resp['status']} {resp['url']}")

            # Check for loading state
            time.sleep(1)
            spinners = page.locator('.ant-spin').all()
            if spinners:
                print(f"\n  ✓ Loading spinner found ({len(spinners)} spinners)")
            else:
                print("\n  ⚠ No loading spinner found")

        except Exception as e:
            print(f"✗ Failed to click BA Üret: {e}")
            page.screenshot(path='/tmp/error_ba_click.png', full_page=True)
            return

        # Step 7: Monitor progress
        print("\n[7/7] Monitoring for 10 seconds...")
        for i in range(10):
            time.sleep(1)

            # Check for new messages
            messages = page.locator('.ant-message').all()
            if messages:
                print(f"  [{i+1}s] Messages on screen: {len(messages)}")

            # Check console logs
            if console_logs:
                recent_logs = console_logs[-3:]
                for log in recent_logs:
                    if 'error' in log.lower() or 'failed' in log.lower():
                        print(f"  [{i+1}s] Console: {log}")

        # Final screenshot
        page.screenshot(path='/tmp/test_final_state.png', full_page=True)
        print("\n✓ Final screenshot saved: /tmp/test_final_state.png")

        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Console logs: {len(console_logs)}")
        print(f"Errors: {len(errors)}")
        print(f"API Requests: {len(requests)}")
        print(f"API Responses: {len(responses)}")

        if errors:
            print("\nPage Errors:")
            for err in errors[:5]:
                print(f"  - {err}")

        if console_logs:
            print("\nRecent Console Logs:")
            for log in console_logs[-10:]:
                print(f"  {log}")

        print("\n⏸ Keeping browser open for 10 seconds for manual inspection...")
        time.sleep(10)

        browser.close()
        print("\n✅ Test completed")

if __name__ == "__main__":
    test_ba_uret_button()
