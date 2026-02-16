# n8n Token-Based Google Drive Access

## 🎯 Yaklaşım

BA/TC Değerlendirme aşamalarıyla **aynı pattern**:

1. App → n8n webhook (OAuth token iste)
2. n8n → Google OAuth token döndür
3. App → Token ile direkt Google Drive API call
4. Dokümanı indir ve parse et

## 📊 Akış Karşılaştırması

### Mevcut Pattern (BA/TC Evaluation):
```
┌─────────────┐
│     App     │
└──────┬──────┘
       │ 1. Token iste
       ▼
┌─────────────┐
│ n8n Webhook │
│  (OAuth)    │
└──────┬──────┘
       │ 2. Token döndür
       ▼
┌─────────────┐
│     App     │
│  + Token    │
└──────┬──────┘
       │ 3. Token ile API call
       ▼
┌─────────────┐
│  Gemini/    │
│ Claude API  │
└─────────────┘
```

### Yeni Pattern (Google Drive):
```
┌─────────────┐
│     App     │
└──────┬──────┘
       │ 1. Token iste
       ▼
┌─────────────┐
│ n8n Webhook │
│  (OAuth)    │
└──────┬──────┘
       │ 2. Token döndür
       ▼
┌─────────────┐
│     App     │
│  + Token    │
└──────┬──────┘
       │ 3. Token ile API call
       ▼
┌─────────────┐
│ Google      │
│ Drive API   │
└─────────────┘
```

**Aynı pattern, farklı API!** ✅

## 🛠️ n8n Webhook Kurulumu

### Basit Workflow (3 Node):

#### 1. Webhook Trigger
```
Type: Webhook
HTTP Method: POST
Path: google-token
Response Mode: Using 'Respond to Webhook' node
```

#### 2. Code Node - Get Token
```javascript
// Get OAuth token from Google Drive credential
const credentials = await this.getCredentials('googleDriveOAuth2Api');

if (!credentials || !credentials.oauthTokenData) {
  throw new Error('No Google Drive OAuth credentials configured');
}

const tokenData = credentials.oauthTokenData;

return {
  token: tokenData.access_token,
  token_type: tokenData.token_type || 'Bearer',
  expires_in: tokenData.expires_in,
  scope: tokenData.scope
};
```

#### 3. Respond to Webhook
```
Respond With: JSON
Response Body: {{ $json }}
```

### Workflow JSON
Import: `n8n_workflows/google_token_webhook.json`

## 📝 Webhook Response

**Request:**
```bash
POST https://sh0tdie.app.n8n.cloud/workflow/AzlnBnFIffKIN79P_WkY7
Content-Type: application/json

{}
```

**Response:**
```json
{
  "token": "ya29.a0AfH6SMBx...",
  "token_type": "Bearer",
  "expires_in": 3599,
  "scope": "https://www.googleapis.com/auth/drive.readonly"
}
```

## 💻 App Tarafında Kullanım

### GoogleDriveClient Class

```python
from pipeline.google_drive_client import GoogleDriveClient

# Initialize
client = GoogleDriveClient(
    n8n_docs_webhook="https://sh0tdie.app.n8n.cloud/workflow/AzlnBnFIffKIN79P_WkY7",
    n8n_sheets_webhook="https://sh0tdie.app.n8n.cloud/workflow/dqJS78_cIKH0mHLgizlNj"
)

# 1. Get token from n8n
token = client.get_oauth_token(client.docs_webhook)
# → Calls n8n webhook, returns OAuth token

# 2. Use token to download document
content = client.download_google_doc(document_id="1ABC123xyz")
# → Makes direct API call to Google Drive with token

# Or use convenience method
content, doc_type = client.read_document_from_url(
    "https://docs.google.com/document/d/1ABC123xyz/edit"
)
```

### Adım Adım:

**1. Token Al:**
```python
# App calls n8n webhook
response = requests.post(webhook_url, json={})
token = response.json()['token']
```

**2. Dokümanı İndir:**
```python
# App uses token to call Google API directly
export_url = f"https://docs.google.com/document/d/{doc_id}/export"
response = requests.get(
    export_url,
    headers={'Authorization': f'Bearer {token}'},
    params={'format': 'plain'}
)
content = response.text
```

**3. Parse Et:**
```python
# App parses content (rule-based or AI)
from pipeline.document_parser_v2 import parse_text_to_json
parsed = parse_text_to_json(content, 'ba')
```

## 🔧 Environment Variables

```bash
# .env file
N8N_GOOGLE_DOCS_WEBHOOK=https://sh0tdie.app.n8n.cloud/workflow/AzlnBnFIffKIN79P_WkY7
N8N_GOOGLE_SHEETS_WEBHOOK=https://sh0tdie.app.n8n.cloud/workflow/dqJS78_cIKH0mHLgizlNj
```

## 🎨 Import & Merge UI

```python
# pages/11_Import_Merge.py

# 1. User pastes Google Docs URL
drive_url = st.text_input("Google Docs URL")

# 2. Extract document ID
doc_id = extract_google_drive_file_id(drive_url)

# 3. Get token from n8n
client = GoogleDriveClient(docs_webhook, sheets_webhook)
token = client.get_oauth_token(client.docs_webhook)

# 4. Download with token
content = client.download_google_doc(doc_id)

# 5. Parse
parsed = parse_text_to_json(content, 'ba')
```

## ✨ Avantajlar

### vs Previous Approach:

**Önceki (Karmaşık):**
```
App → n8n → n8n downloads doc → n8n returns content → App
```
- ❌ n8n dosyayı indiriyor (gereksiz)
- ❌ Tüm içerik webhook'tan geçiyor (yavaş)
- ❌ Timeout riski (büyük dosyalar)
- ❌ n8n'de fazladan işlem

**Yeni (Basit - BA/TC Pattern):**
```
App → n8n → n8n returns token → App downloads doc directly
```
- ✅ n8n sadece token veriyor
- ✅ App direkt API'ye bağlanıyor
- ✅ Hızlı ve efficient
- ✅ Mevcut pattern ile tutarlı
- ✅ Token cache'lenebilir

### Teknik Faydalar:

1. **Aynı Pattern** - BA/TC evaluation ile aynı
2. **Basit n8n Workflow** - Sadece 3 node
3. **Hızlı** - Token direkt dönüyor
4. **Scalable** - Token re-use mümkün
5. **Maintainable** - Tek sorumluluk (n8n = token, app = download)

## 🔒 Güvenlik

### OAuth Scopes:
```
https://www.googleapis.com/auth/drive.readonly
https://www.googleapis.com/auth/documents.readonly
https://www.googleapis.com/auth/spreadsheets.readonly
```

### Token Lifetime:
- Access token: ~1 saat
- App her request'te yeni token alabilir
- Veya token'ı cache'leyip expire olana kadar kullanabilir

### Best Practices:
- ✅ Token'ı memory'de tut (disk'e yazma)
- ✅ Token'ı log'lama
- ✅ HTTPS kullan
- ✅ n8n webhook'ları credential gerektirebilir

## 🧪 Test

### 1. n8n Webhook Test:
```bash
curl -X POST https://sh0tdie.app.n8n.cloud/workflow/AzlnBnFIffKIN79P_WkY7 \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected:**
```json
{
  "token": "ya29.a0AfH6SMBx...",
  "token_type": "Bearer"
}
```

### 2. Token ile Document Download:
```bash
TOKEN="ya29.a0AfH6SMBx..."
DOC_ID="1kKv23VucVctDKHxbYHxmMSsl4Dtxe6q1lA9cCrr7OIjI"

curl "https://docs.google.com/document/d/${DOC_ID}/export?format=plain" \
  -H "Authorization: Bearer ${TOKEN}"
```

**Expected:**
```
Document title

Section 1
Content here...
```

## 📚 Karşılaştırma: Mevcut n8n Webhooks

Sizin mevcut webhook'larınız muhtemelen zaten bu pattern'i kullanıyor:

### BA/TC Evaluation Webhooks:
```python
# Gemini API için token
response = requests.post(gemini_webhook_url)
gemini_token = response.json()['token']

# Token ile Gemini API call
result = call_gemini_with_token(gemini_token, prompt)
```

### Google Drive için Aynı:
```python
# Google OAuth için token
response = requests.post(google_docs_webhook_url)
google_token = response.json()['token']

# Token ile Google Drive API call
content = download_doc_with_token(google_token, doc_id)
```

**Tek fark: API endpoint (Gemini vs Google Drive)**

## 🚀 Migration

Eski karmaşık approach'tan yeniye geçiş:

### Remove:
- ❌ `n8n_workflows/google_docs_reader.json` (document download workflow)
- ❌ Karmaşık download logic n8n'de

### Keep/Add:
- ✅ `n8n_workflows/google_token_webhook.json` (simple token provider)
- ✅ `pipeline/google_drive_client.py` (app-side download)
- ✅ BA/TC pattern ile tutarlılık

## 💡 Summary

**Eski Yaklaşım:**
"n8n her şeyi yapsın (token al + document indir + döndür)"

**Yeni Yaklaşım (Sizin öneriniz):**
"n8n sadece token versin, app direkt API'ye bağlansın"

**Sonuç:**
- ✅ Basit
- ✅ Hızlı
- ✅ Mevcut pattern ile tutarlı (BA/TC evaluation)
- ✅ Maintainable
- ✅ Scalable

Tam olarak haklısınız - BA/TC değerlendirme akışını kullanmalıyız! 🎯
