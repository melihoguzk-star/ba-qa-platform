# Import Features - Word & Google Drive Support

## 🎯 Overview

The Import & Merge page now supports **5 import methods**:

1. 📋 Paste JSON - Direct JSON import
2. 📄 From BRD Pipeline - Import from completed pipeline runs
3. 📝 Paste Text (AI Parse) - Parse text with AI or rules
4. **📎 Upload Word Document** - NEW! Upload .docx files
5. **☁️ Import from Google Drive** - NEW! Import via Drive link

## 📎 Upload Word Document

### How it works:
1. Upload a `.docx` file (Microsoft Word format)
2. Text is automatically extracted with structure preserved
3. Choose parsing method (Rule-based or AI-powered)
4. Document is parsed to JSON format

### Features:
- ✅ Preserves heading hierarchy (H1, H2, H3)
- ✅ Extracts bullet points and numbered lists
- ✅ Maintains document structure
- ✅ Works with Turkish and English documents
- ✅ Supports both rule-based and AI parsing

### Example:
```
Upload: login_analysis.docx
Extract: ~5000 characters
Parse: → JSON with screens, backend operations, etc.
```

## ☁️ Import from Google Drive

### How it works:
1. Share your document in Google Drive
2. Set access to "Anyone with the link can view"
3. Copy and paste the link
4. Document is downloaded and parsed

### Supported formats:
- ✅ Google Docs (native)
- ✅ Word documents (.docx) stored in Drive
- ✅ Text files (.txt)
- ⚠️  PDF files (not yet supported)

### Supported URLs:
- `https://drive.google.com/file/d/FILE_ID/view`
- `https://docs.google.com/document/d/FILE_ID/edit`
- `https://drive.google.com/open?id=FILE_ID`

### How to share:
1. Open document in Google Drive
2. Click "Share" button (top-right)
3. Change "Restricted" to **"Anyone with the link"**
4. Set permission to **"Viewer"**
5. Click "Copy link"
6. Paste in Import & Merge page

### Example:
```
URL: https://docs.google.com/document/d/1ABC123xyz/edit
Download: ~10KB
Extract: ~8000 characters
Parse: → JSON
```

## 🔧 Technical Implementation

### Word Document Reading (`pipeline/document_reader.py`)

```python
from pipeline.document_reader import read_docx

# Read .docx file
file_content = open('document.docx', 'rb').read()
extracted_text = read_docx(file_content)

# Text includes:
# - Headings marked with # (H1), ## (H2), ### (H3)
# - Paragraphs preserved
# - Bullet points maintained
```

### Google Drive Download

```python
from pipeline.document_reader import (
    extract_google_drive_file_id,
    read_document_from_drive,
    export_google_doc_as_text
)

# Extract file ID from URL
file_id = extract_google_drive_file_id(url)

# Download and extract text
if 'docs.google.com/document' in url:
    # Google Docs - use export API
    text = export_google_doc_as_text(url)
else:
    # Regular file - download and extract
    text = read_document_from_drive(url)
```

### Parsing

After extraction, text is parsed using either:

1. **Rule-based Parser** (Free, Fast)
   - Detects heading hierarchy
   - Extracts bullet points
   - Maps to JSON based on content type
   - Works best with structured documents

2. **AI-powered Parser** (Flexible, Requires API Key)
   - Uses Gemini API
   - Understands context
   - Handles unstructured text
   - More expensive but more flexible

## 🎨 User Interface

### Import Method Selection
```
[📋 Paste JSON] [📄 From Pipeline] [📝 Paste Text]
[📎 Upload Word] [☁️ Google Drive]
```

### Upload Word Flow
1. Choose "📎 Upload Word Document"
2. Upload .docx file
3. Select document type (BA/TA/TC)
4. Choose parsing method
5. Click "📄 Extract & Parse"
6. Review parsed JSON
7. Continue to similarity detection

### Google Drive Flow
1. Choose "☁️ Import from Google Drive"
2. Paste Google Drive link
3. Select document type (BA/TA/TC)
4. Choose parsing method
5. Click "☁️ Download & Parse"
6. Review extracted text preview
7. Review parsed JSON
8. Continue to similarity detection

## 📊 Benefits

### For Users:
- ✅ No need to copy-paste text manually
- ✅ Direct import from Google Drive (team collaboration)
- ✅ Works with existing Word documents
- ✅ Structure is automatically preserved
- ✅ Fast and convenient

### For Teams:
- ✅ Centralized documents in Google Drive
- ✅ Version control via Drive
- ✅ Share link instead of file
- ✅ No email attachments needed
- ✅ Consistent workflow

## 🔒 Security & Privacy

### Google Drive:
- Documents must be set to "Anyone with link"
- No OAuth authentication required
- No access to private documents
- Download happens server-side
- No data is stored (only parsed JSON)

### Word Documents:
- Uploaded files are processed in memory
- No files stored on disk
- Only extracted text is kept (in session)
- File contents not logged

## ⚠️ Limitations

### Google Drive:
- ❌ Cannot access private/restricted documents
- ❌ Requires "Anyone with link" sharing
- ❌ PDF files not yet supported
- ⚠️  Large files (>10MB) may be slow

### Word Documents:
- ❌ Only .docx format (not .doc)
- ⚠️  Complex formatting may be simplified
- ⚠️  Tables/images not extracted (text only)
- ⚠️  Embedded objects ignored

## 🚀 Future Enhancements

Potential improvements:
- [ ] PDF support (using PyPDF2 or pdfplumber)
- [ ] Google Sheets import (for test cases)
- [ ] Confluence import
- [ ] Direct Google Docs API integration (OAuth)
- [ ] Batch import (multiple files)
- [ ] OneDrive/SharePoint support
- [ ] Table extraction from Word
- [ ] Image OCR for scanned documents

## 📝 Example Usage

### Scenario 1: Upload BA Document
```
1. BA team creates document in Word
2. Exports as .docx
3. Uploads to Import & Merge
4. System extracts and parses
5. BA reviews JSON
6. Merges with existing documents
```

### Scenario 2: Shared Google Doc
```
1. Team collaborates on Google Doc
2. PM shares link with QA
3. QA pastes link in Import & Merge
4. System downloads and parses
5. QA reviews and imports
6. Document tracked in database
```

### Scenario 3: Migrating Legacy Docs
```
1. Existing Word documents in Drive
2. Share links one by one
3. Import via Google Drive method
4. Build document library
5. All documents now in system
```

## 🎓 Best Practices

### For Word Documents:
- ✅ Use clear heading hierarchy (H1, H2, H3)
- ✅ Use bullet points for lists
- ✅ Keep structure consistent
- ✅ Avoid complex formatting
- ✅ Use standard Word styles

### For Google Drive:
- ✅ Set proper sharing permissions
- ✅ Use meaningful document names
- ✅ Keep documents organized in folders
- ✅ Use Google Docs for collaboration
- ✅ Export to .docx for complex formatting

### For Parsing:
- ✅ Try rule-based first (free & fast)
- ✅ Use AI for unstructured documents
- ✅ Review parsed JSON before import
- ✅ Provide clear document titles
- ✅ Choose correct document type (BA/TA/TC)

## 🔍 Troubleshooting

### "Cannot access file" error:
- Check sharing settings (must be "Anyone with link")
- Verify link is correct
- Try re-sharing the document

### "Unsupported file format":
- Only .docx, .txt, and Google Docs supported
- Convert .doc to .docx
- Export PDF to Word

### "Parser couldn't find content":
- Document may lack clear structure
- Try AI-powered parsing
- Check if headings are properly formatted

### "AI parsing failed":
- Check API key is set
- Document may be too large
- Try breaking into smaller sections
