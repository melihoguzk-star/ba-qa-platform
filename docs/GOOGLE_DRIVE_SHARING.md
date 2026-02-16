# Google Drive Paylaşım Rehberi

## 🎯 Sorun: HTML Kodu Geliyor

Eğer Google Docs'tan doküman import ederken HTML kodu geliyorsa, doküman düzgün paylaşılmamış demektir.

### ❌ Hatalı Durum
```
✅ Downloaded and extracted 1233787 characters

Preview shows:
<!doctype html><html lang="en-US"...
<style data-href="https://www.gstatic.com...
```

Bu HTML, Google Docs'un **giriş sayfası** veya **yetki hatası sayfası**dır - doküman içeriği değil!

---

## ✅ Çözüm: Doğru Paylaşım Ayarları

### Adım 1: Dokümanı Aç
Google Drive'da dokümanınızı açın.

### Adım 2: Share Butonuna Tıkla
Sağ üst köşede **"Share"** butonuna tıklayın.

### Adım 3: Paylaşım Ayarını Değiştir

**ÖNCESİ (Yanlış):**
```
🔒 Restricted
   Only people added can open with this link
```

**SONRASI (Doğru):**
```
🌐 Anyone with the link
   Anyone on the internet with this link can view
```

### Adım 4: İzin Seviyesini Ayarla
Dropdown menüden **"Viewer"** seçin (Editor veya Commenter değil)

```
📖 Viewer  ← Bunu seçin
✏️  Commenter
✍️  Editor
```

### Adım 5: Linki Kopyala
**"Copy link"** butonuna tıklayın ve linki kopyalayın.

### Adım 6: Import & Merge'de Kullan
Kopyaladığınız linki Import & Merge sayfasına yapıştırın.

---

## 📋 Detaylı Adımlar (Görsel)

### 1. Share Dialog
```
┌─────────────────────────────────────┐
│  Share "Document Name"              │
├─────────────────────────────────────┤
│                                     │
│  🔒 Restricted ▼                    │  ← Bunu değiştir
│     Only people added can open      │
│                                     │
│  Add people, groups, or calendar... │
│                                     │
│  ┌─────────────────┐               │
│  │   Copy link     │               │
│  └─────────────────┘               │
│                                     │
│  [ Done ]                          │
└─────────────────────────────────────┘
```

### 2. Değiştirme
Dropdown'a tıklayın:
```
┌─────────────────────────────┐
│  Restricted                 │
│  ✅ Anyone with the link     │  ← Bunu seç
└─────────────────────────────┘
```

### 3. İzin Seviyesi
```
┌─────────────────────────────┐
│  ✅ Viewer                   │  ← Bunu seç
│  Commenter                  │
│  Editor                     │
└─────────────────────────────┘
```

### 4. Final Görünüm
```
┌─────────────────────────────────────┐
│  Share "Document Name"              │
├─────────────────────────────────────┤
│                                     │
│  🌐 Anyone with the link ▼          │  ✅ Doğru!
│     Anyone on internet can view     │
│                                     │
│  General access                     │
│  Viewer ▼                          │  ✅ Doğru!
│                                     │
│  ┌─────────────────┐               │
│  │   Copy link     │  ← Tıkla      │
│  └─────────────────┘               │
│                                     │
│  [ Done ]                          │
└─────────────────────────────────────┘
```

---

## 🔍 Kontrol Listesi

Import etmeden önce kontrol edin:

- [ ] "Share" butonuna tıkladım
- [ ] "Restricted" yerine **"Anyone with the link"** seçtim
- [ ] İzin seviyesi **"Viewer"** olarak ayarlı
- [ ] "Copy link" ile linki kopyaladım
- [ ] Linki Import & Merge sayfasına yapıştırdım

---

## ❓ Sık Sorulan Sorular

### S: "Anyone with the link" güvenli mi?
**C:** Evet, link sadece okuma yetkisi verir. Kimse dokümanı düzenleyemez veya silemez. Link'i bilmeyen kimse erişemez.

### S: Şirket politikası public paylaşıma izin vermiyor
**C:** İki seçenek:
1. Word'e export edin (File → Download → Microsoft Word)
2. "📎 Upload Word Document" ile yükleyin

### S: Link'i değiştirince eski link çalışır mı?
**C:** Hayır, eski link geçersiz olur. Yeni linki kullanmanız gerekir.

### S: Birden fazla doküman import edeceğim
**C:** Her doküman için aynı adımları tekrarlayın veya tüm dokümanları aynı klasöre koyun ve klasör paylaşımını ayarlayın.

### S: HTML kodu gelmeye devam ediyor
**C:** Olası nedenler:
- Share ayarları henüz güncellenmedi (1-2 dakika bekleyin)
- Yanlış link kopyalandı (doğru linki tekrar kopyalayın)
- Tarayıcı cache (farklı tarayıcıda deneyin)
- Doküman silindi veya taşındı

---

## 🛠️ Alternatif: Word Export

Eğer public paylaşım mümkün değilse:

### Adım 1: Export
```
File → Download → Microsoft Word (.docx)
```

### Adım 2: Upload
```
Import & Merge → 📎 Upload Word Document
```

Bu yöntem:
- ✅ Paylaşım gerektirmez
- ✅ Şirket politikalarına uyumlu
- ✅ Aynı sonucu verir
- ⚠️  Manual adım gerektirir (otomatik değil)

---

## 🎓 Özet

**Sorun:** Google Docs HTML döndürüyor
**Neden:** Doküman public değil
**Çözüm:** "Anyone with the link" + "Viewer" izni

**Alternatif:** .docx export + upload

**Test:** Link'i incognito/private browsing'de aç - dokümanı görebiliyorsanız, link doğru paylaşılmış demektir.

---

## 📞 Hala Sorun mu Var?

1. Linki incognito pencerede açmayı deneyin
2. Dokümanın silinmediğinden emin olun
3. Farklı bir Google Docs dokümanı ile test edin
4. Word export + upload yöntemini kullanın

---

## ✨ İpucu

Link'i test etmek için:
1. Tarayıcıda yeni incognito/private pencere açın
2. Link'i yapıştırın
3. Dokümanı görebiliyorsanız → paylaşım doğru ✅
4. Giriş ekranı geliyorsa → paylaşım yanlış ❌
