# Claude Code İş Akışı Yönetimi

## İş Akışı Orkestrasyon

### 1. Varsayılan Plan Modu
- Önemsiz olmayan HER görev için (3+ adım veya mimari kararlar) plan moduna gir
- Bir şeyler ters giderse, DUR ve hemen yeniden planla — zorlamaya devam etme
- Plan modunu sadece inşa etmek için değil, doğrulama adımları için de kullan
- Belirsizliği azaltmak için ayrıntılı spesifikasyonları önceden yaz

### 2. Alt-Ajan Stratejisi
- Ana bağlam penceresini temiz tutmak için alt-ajanları bolca kullan
- Araştırma, keşif ve paralel analizleri alt-ajanlara devret
- Karmaşık problemler için alt-ajanlar aracılığıyla daha fazla hesaplama gücü kullan
- Odaklı yürütme için her alt-ajana tek bir görev ver

### 3. Kendini Geliştirme Döngüsü
- Kullanıcıdan HER düzeltmeden sonra: `tasks/lessons.md` dosyasını kalıpla güncelle
- Aynı hatanın tekrarını engelleyen kuralları kendin için yaz
- Hata oranı düşene kadar bu dersler üzerinde acımasızca iterasyon yap
- İlgili proje için oturum başlangıcında dersleri gözden geçir

### 4. Bitmeden Önce Doğrulama
- Çalıştığını kanıtlamadan hiçbir görevi tamamlanmış olarak işaretleme
- Uygun olduğunda ana dal ile kendi değişikliklerin arasındaki farkı karşılaştır
- Kendine sor: "Kıdemli bir mühendis bunu onaylar mıydı?"
- Testleri çalıştır, logları kontrol et, doğruluğu göster

### 5. Zarafet Talebi (Dengeli)
- Önemsiz olmayan değişiklikler için: dur ve "daha zarif bir yol var mı?" diye sor
- Bir düzeltme acemice hissediyorsa: "Şimdi her şeyi bildiğime göre, zarif çözümü uygula"
- Basit, bariz düzeltmeler için bunu atla — aşırı mühendislik yapma
- Sunmadan önce kendi çalışmanı sorgula

### 6. Otonom Hata Düzeltme
- Bir hata raporu verildiğinde: sadece düzelt. El tutma bekleme
- Loglara, hatalara, başarısız testlere bak — sonra çöz
- Kullanıcıdan sıfır bağlam değiştirme gerektir
- Nasıl yapılacağı söylenmeden başarısız CI testlerini düzelt

## Görev Yönetimi

1. **Önce Planla:** İşaretlenebilir maddelerle `tasks/todo.md` dosyasına plan yaz
2. **Planı Doğrula:** Uygulamaya başlamadan önce kontrol et
3. **İlerlemeyi Takip Et:** İlerledikçe maddeleri tamamlanmış olarak işaretle
4. **Değişiklikleri Açıkla:** Her adımda üst düzey özet ver
5. **Sonuçları Belgele:** `tasks/todo.md` dosyasına inceleme bölümü ekle
6. **Dersleri Kaydet:** Düzeltmelerden sonra `tasks/lessons.md` dosyasını güncelle

## Temel İlkeler

- **Önce Basitlik:** Her değişikliği mümkün olduğunca basit yap. Minimum kod etkisi
- **Tembellik Yok:** Kök nedenleri bul. Geçici düzeltmeler yok. Kıdemli geliştirici standartları
- **Minimum Etki:** Değişiklikler sadece gerekli olan yerlere dokunmalı. Hata oluşturmaktan kaçın2