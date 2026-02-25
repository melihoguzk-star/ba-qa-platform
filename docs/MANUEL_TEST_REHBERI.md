# BRD Pipeline - Manuel Test Rehberi

## Adım Adım Test

### Adım 1: Sayfayı Aç
1. Browser'da git: **http://localhost:5173/brd-pipeline**
2. Sayfa yüklendiğinde görmen gerekenler:
   - Başlık: "BRD Pipeline"
   - Progress bar (12 adım)
   - Form: "Pipeline Konfigürasyonu"

### Adım 2: Proje Seç
1. **"Proje"** dropdown'ına tıkla
2. Listeden herhangi bir proje seç
   - Eğer proje yoksa, önce Documents sayfasından proje oluştur

### Adım 3: BRD İçeriği Gir

**ÖNEMLI:** Şu anda sadece TXT dosyaları veya direkt metin destekleniyor.

**Seçenek A: Dosya Yükle (Sadece .txt)**
1. "BRD Dosyası Yükle" butonuna tıkla
2. Bir .txt dosyası seç
3. İçerik otomatik olarak textarea'ya dolacak

**Seçenek B: Manuel Yapıştır (Önerilen)**
1. Aşağıdaki örnek metni kopyala:

```
# Kullanıcı Giriş Sistemi

## 1. Amaç
Web uygulaması için kullanıcı giriş sistemi

## 2. Kapsam
- Kullanıcı giriş ekranı
- Şifre doğrulama
- Beni Hatırla özelliği

## 3. Fonksiyonel Analiz

### 3.1 Login Ekranı
**Form Alanları:**
- Email (zorunlu)
- Şifre (zorunlu, min 8 karakter)
- Beni Hatırla (checkbox)

**İş Kuralları:**
1. Email formatı kontrol edilmeli
2. Şifre minimum 8 karakter
3. 3 başarısız denemede hesap kilitlenmeli

**Kabul Kriterleri:**
- Geçerli email/şifre ile giriş başarılı
- Hatalı şifre ile hata mesajı
- Başarılı girişte Dashboard'a yönlendir
```

2. "BRD İçeriği" textarea'sına yapıştır

### Adım 4: Doküman Türlerini Seç
1. Varsayılan olarak BA, TA, TC seçili olmalı
2. İstersen bazılarını kaldırabilirsin

### Adım 5: Pipeline'ı Başlat
1. **"Pipeline Başlat"** butonuna tıkla
2. Beklenen sonuç:
   - Yeşil mesaj: "Pipeline oluşturuldu. BA üretimi başlatabilirsiniz."
   - Progress bar 2. adıma (BA Üretim) geçer

### Adım 6: BA Üretimi
1. Görmen gereken:
   - Mavi info box: "BA dokümanını üretmek için butona tıklayın"
   - **"BA Üret"** butonu
2. Butona tıkla
3. Beklenen:
   - Spinner gösterilir
   - "BA dokümanı Claude tarafından üretiliyor..." mesajı

---

## ⚠️ Olası Sorunlar ve Çözümleri

### Sorun 1: "Proje bulunamadı" / Dropdown boş
**Çözüm:**
```bash
# Backend çalışıyor mu kontrol et
curl http://localhost:8000/api/v1/projects

# Proje oluştur
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Projesi", "description": "Test"}'
```

### Sorun 2: "Pipeline Başlat" butonu tepki vermiyor
**Kontrol et:**
1. Console'da hata var mı? (F12 > Console)
2. Network tab'da API çağrısı yapılıyor mu? (F12 > Network)
3. Form validation hatası var mı? (kırmızı mesajlar)

**Çözüm:**
- Proje seçili olmalı
- BRD içeriği dolu olmalı (en az birkaç karakter)

### Sorun 3: DOCX dosyası garbled text gösteriyor
**Bu normal!** Şu anda DOCX parse edilmiyor.

**Çözüm:**
1. DOCX'i aç
2. İçeriği kopyala
3. Textarea'ya yapıştır

### Sorun 4: "BA Üret" tıklayınca hiçbir şey olmuyor
**Kontrol et:**
```bash
# Backend loglarını izle
tail -f /private/tmp/claude-501/-Users-melihoguz-ba-qa-platform/tasks/b081d09.output | grep "ERROR\|pipeline"
```

**Olası sebepler:**
- API keys eksik (.env dosyasında ANTHROPIC_API_KEY ve GEMINI_API_KEY)
- Backend'de hata var

### Sorun 5: API Key hatası
**Kontrol et:**
```bash
# .env dosyasını kontrol et
cat .env | grep API_KEY

# Yoksa ekle
echo 'ANTHROPIC_API_KEY=your-key-here' >> .env
echo 'GEMINI_API_KEY=your-key-here' >> .env

# Backend'i restart et
```

---

## 🐛 Debug Checklist

Eğer bir sorun yaşıyorsan, şunları kontrol et:

### Frontend
- [ ] Browser console'da hata var mı? (F12 > Console)
- [ ] Network tab'da failed request var mı? (F12 > Network)
- [ ] Frontend dev server çalışıyor mu? (http://localhost:5173)

### Backend
- [ ] Backend server çalışıyor mu? (http://localhost:8000/health)
- [ ] API endpoints cevap veriyor mu?
```bash
curl http://localhost:8000/api/v1/projects
curl http://localhost:8000/health
```
- [ ] Backend loglarında hata var mı?
```bash
tail -50 /private/tmp/claude-501/-Users-melihoguz-ba-qa-platform/tasks/b081d09.output
```

### Database
- [ ] Database dosyası var mı?
```bash
ls -la data/*.db
```
- [ ] Pipeline runs tablosu var mı?
```bash
sqlite3 data/baqa.db "SELECT * FROM pipeline_runs LIMIT 5;"
```

---

## 📸 Beklenen Görüntüler

### 1. İlk Yükleme
```
+------------------------------------------+
| BRD Pipeline                             |
+------------------------------------------+
| [1 BRD Yükleme] 2 BA Üretim 3 BA İnc... |
+------------------------------------------+
| Pipeline Konfigürasyonu                  |
|                                          |
| Proje: [Dropdown ▼]                      |
|                                          |
| BRD İçeriği:                             |
| [________________________]               |
| [________________________]               |
|                                          |
| [📁 BRD Dosyası Yükle]                   |
|                                          |
| ☑ BA  ☑ TA  ☑ TC                         |
|                                          |
| [🚀 Pipeline Başlat]                     |
+------------------------------------------+
```

### 2. BA Üretim Aşaması
```
+------------------------------------------+
| BRD Pipeline                             |
+------------------------------------------+
| 1 ✓ [2 BA Üretim] 3 BA İnc...           |
+------------------------------------------+
| BA Doküman Üretimi                       |
|                                          |
| ℹ️  Hazır                                 |
| BA dokümanını üretmek için butona        |
| tıklayın.                                |
|                                          |
| [🚀 BA Üret]                             |
+------------------------------------------+
```

---

## ✅ Test Başarı Kriterleri

1. ✅ Sayfa yükleniyor
2. ✅ Proje seçilebiliyor
3. ✅ BRD içeriği girilebiliyor
4. ✅ Pipeline başlatılabiliyor
5. ⏳ BA üretimi başlıyor (API key gerekli)
6. ⏳ BA review ekranı açılıyor
7. ⏳ QA evaluation çalışıyor
8. ⏳ Full workflow tamamlanabiliyor

---

## 💡 Hızlı Test Komutu

Eğer tüm bunları otomatik yapmak istersen:

```bash
python test_brd_pipeline_full.py
```

Bu script:
- Browser'ı açar
- Formu doldurur
- Pipeline'ı başlatır
- Screenshot'lar alır
- Sonuçları gösterir
