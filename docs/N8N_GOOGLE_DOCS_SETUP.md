# n8n ile Google Docs Okuma - Kurulum Rehberi

## 🎯 Amaç

Şirket Google Drive'ındaki dokümanları public share etmeden okumak için n8n webhook kullanımı.

## 📊 Avantajlar

- ✅ Public sharing gerektirmez
- ✅ OAuth ile güvenli erişim
- ✅ Şirket politikalarına uyumlu
- ✅ Tüm dokümanlara erişim (yetkili olduğunuz)
- ✅ Otomatik authentication

## 🛠️ Kurulum

### 1. Google Cloud Credentials Oluştur

**n8n'de zaten Google OAuth varsa, bu adımı atlayın.**

1. [Google Cloud Console](https://console.cloud.google.com/) açın
2. Yeni proje oluşturun veya mevcut projeyi seçin
3. "APIs & Services" → "Credentials" gidin
4. "Create Credentials" → "OAuth client ID"
5. Application type: "Web application"
6. Authorized redirect URIs:
   ```
   https://your-n8n-instance.com/rest/oauth2-credential/callback
   ```
7. Client ID ve Client Secret'i kaydedin

### 2. Google Drive API'yi Etkinleştir

1. Google Cloud Console'da "APIs & Services" → "Library"
2. "Google Drive API" arayın
3. "Enable" tıklayın
4. "Google Docs API"yi de enable edin

### 3. n8n Credential Oluştur

1. n8n'de "Credentials" → "New"
2. "Google Drive OAuth2 API" seçin
3. Adı: "Google Drive - BA QA Platform"
4. Client ID ve Client Secret girin
5. Scopes:
   ```
   https://www.googleapis.com/auth/drive.readonly
   https://www.googleapis.com/auth/documents.readonly
   ```
6. "Connect my account" tıklayın
7. Google hesabınızla giriş yapın ve izin verin

### 4. n8n Workflow İmport Et

**Seçenek A: JSON İmport**
1. n8n'de "Workflows" → "Add workflow"
2. "⋮" menü → "Import from File"
3. `n8n_workflows/google_docs_reader.json` dosyasını seçin
4. Import edin

**Seçenek B: Manuel Oluştur**

#### Node 1: Webhook (Trigger)
```
- Type: Webhook
- HTTP Method: POST
- Path: read-google-doc
- Response Mode: "Using 'Respond to Webhook' node"
```

#### Node 2: Google Drive
```
- Type: Google Drive
- Credential: Google Drive OAuth2 (yukarıda oluşturduğunuz)
- Operation: Download a file
- File ID: {{ $json.documentId }}
- Options:
  - Google File Conversion:
    - Docs to format: text/plain
```

#### Node 3: Code (Extract Text)
```javascript
// Extract text content
const data = $input.first().binary.data;

let text = '';
if (data) {
  text = data.toString('utf-8');
}

return {
  success: true,
  content: text,
  characterCount: text.length,
  documentId: $input.first().json.documentId
};
```

#### Node 4: Respond to Webhook
```
- Type: Respond to Webhook
- Respond With: JSON
- Response Body: {{ $json }}
```

### 5. Workflow'u Aktif Et

1. Workflow'u kaydedin
2. Sağ üst köşeden "Active" yapın
3. Webhook URL'ini kopyalayın (örnek: `https://n8n.example.com/webhook/read-google-doc`)

## 🔧 Import & Merge'de Kullanım

### Webhook URL Ayarla

Import & Merge sayfasında yeni seçenek eklenecek:

```
☁️ Import from Google Drive (via n8n Webhook)

Webhook URL: [https://n8n.example.com/webhook/read-google-doc]
Document URL: [https://docs.google.com/document/d/...]

[🔗 Fetch via Webhook]
```

### Nasıl Çalışır?

1. Kullanıcı Google Docs URL'ini yapıştırır
2. System URL'den document ID'yi extract eder
3. n8n webhook'una POST request gönderir:
   ```json
   {
     "documentId": "1kKv23VucVctDKHxbYHxmMSsl4Dtxe6q1lA9cCrr7OIjI"
   }
   ```
4. n8n OAuth ile Google'a bağlanır
5. Dokümanı text formatında indirir
6. Response döndürür:
   ```json
   {
     "success": true,
     "content": "doküman metni...",
     "characterCount": 50000,
     "documentId": "..."
   }
   ```
7. Import & Merge metni parse eder

## 📝 Test

### Test Request (curl)

```bash
curl -X POST https://n8n.example.com/webhook/read-google-doc \
  -H "Content-Type: application/json" \
  -d '{
    "documentId": "1kKv23VucVctDKHxbYHxmMSsl4Dtxe6q1lA9cCrr7OIjI"
  }'
```

### Beklenen Response

**Başarılı:**
```json
{
  "success": true,
  "content": "# Document Title\n\nContent here...",
  "characterCount": 15234,
  "documentId": "1kKv23VucVctDKHxbYHxmMSsl4Dtxe6q1lA9cCrr7OIjI"
}
```

**Hata:**
```json
{
  "success": false,
  "error": "Failed to download document"
}
```

## 🔒 Güvenlik

### OAuth Permissions
Sadece read-only access:
```
https://www.googleapis.com/auth/drive.readonly
https://www.googleapis.com/auth/documents.readonly
```

### Webhook Security
n8n webhook'larına authentication ekleyin:

```
Webhook Settings:
- Authentication: Header Auth
- Header Name: X-API-Key
- Header Value: your-secret-key
```

Import & Merge'de:
```python
headers = {
    "Content-Type": "application/json",
    "X-API-Key": os.environ.get("N8N_WEBHOOK_API_KEY")
}
```

## 🎨 Import & Merge UI

Yeni import methodu:

```
Import Methods:
1. 📋 Paste JSON
2. 📄 From BRD Pipeline
3. 📝 Paste Text (AI Parse)
4. 📎 Upload Word Document
5. ☁️ Google Drive (Direct) - Public documents only
6. 🔗 Google Drive (n8n Webhook) - Private documents ✨ NEW
```

## 📊 Workflow Diagram

```
┌─────────────────┐
│  User pastes    │
│  Google Doc URL │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│  Extract Document   │
│  ID from URL        │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  POST to n8n        │
│  Webhook            │
│  {documentId: ...}  │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  n8n: OAuth Login   │
│  to Google          │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Download document  │
│  as text/plain      │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Return text        │
│  content            │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Parse with         │
│  rule-based or AI   │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Import to          │
│  database           │
└─────────────────────┘
```

## 💡 İpuçları

### Document ID Extraction
```python
# URL formats:
# https://docs.google.com/document/d/DOCUMENT_ID/edit
# https://drive.google.com/file/d/DOCUMENT_ID/view

import re

def extract_document_id(url):
    patterns = [
        r'/d/([a-zA-Z0-9_-]+)',
        r'[?&]id=([a-zA-Z0-9_-]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None
```

### Timeout Settings
n8n webhook'u uzun sürebilir (büyük dokümanlar için):
```python
response = requests.post(
    webhook_url,
    json={"documentId": doc_id},
    timeout=60  # 60 saniye
)
```

### Error Handling
```python
try:
    response = requests.post(webhook_url, json=data, timeout=60)
    response.raise_for_status()
    result = response.json()

    if not result.get('success'):
        raise ValueError(f"Webhook error: {result.get('error')}")

    return result['content']

except requests.Timeout:
    raise Exception("Webhook timeout - document may be too large")
except requests.RequestException as e:
    raise Exception(f"Webhook request failed: {str(e)}")
```

## 🚀 Next Steps

1. ✅ n8n workflow oluştur ve test et
2. ✅ Webhook URL'i al
3. ⏳ Import & Merge'e webhook import ekle
4. ⏳ Settings'e webhook URL konfigürasyonu ekle
5. ⏳ Test et ve deploy et

## 📚 Kaynaklar

- [n8n Google Drive Node](https://docs.n8n.io/integrations/builtin/credentials/google/drive/)
- [Google Drive API](https://developers.google.com/drive/api/v3)
- [Google Docs API](https://developers.google.com/docs/api)
