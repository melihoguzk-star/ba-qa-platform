# 🎯 New Features Test Guide

## ✨ Two New Features Implemented

### 1. 📄 From BRD Pipeline - Direct Import
### 2. 📝 Paste Text (AI Parse) - AI-Powered Text Parsing

---

## Prerequisites

1. **Streamlit Running:**
   ```bash
   cd /Users/melihoguz/ba-qa-platform
   source venv/bin/activate
   streamlit run app.py
   ```

2. **For AI Parse:** Gemini API key configured in Settings

3. **For Pipeline Import:** At least one completed BRD Pipeline run

---

## 🧪 Test 1: From BRD Pipeline

### Setup (if needed):

**Create a test pipeline run:**
1. Go to **🚀 BRD Pipeline** in sidebar
2. Upload any BRD file or use sample
3. Wait for pipeline to complete (status: "completed")
4. Note the Run ID

### Test Steps:

1. **Navigate to Import & Merge**
   - Sidebar → **📥 Import & Merge**
   - You should see Step 1: Import Document

2. **Select Import Method**
   - Choose **📄 From BRD Pipeline** radio button
   - Info message: "Select a completed pipeline run to import BA/TA/TC outputs"

3. **Select Pipeline Run**
   - Dropdown appears with completed runs
   - Format: "Run #X: ProjectName (JIRA-KEY) - YYYY-MM-DD HH:MM"
   - Select any completed run

4. **Review Run Metrics**
   - See 3 metric cards: BA Score, TA Score, TC Score
   - Scores should be between 0-100%

5. **Select Output Type**
   - Radio buttons appear: BA, TA, TC (with revision numbers)
   - Select one (e.g., BA rev 0)
   - JSON preview appears below

6. **Review Preview**
   - Expand JSON to see structure
   - Should contain ekranlar, backend_islemler, etc.

7. **Set Title & Import**
   - Default title auto-populated: "ProjectName - BA"
   - Edit if desired
   - Click **➡️ Import from Pipeline**

**Expected Result:**
- ✅ Success message: "BA imported from pipeline run #X!"
- ✅ Automatically moves to Step 2: Detect Similar
- ✅ Imported document in session state

---

## 🧪 Test 2: Paste Text (AI Parse)

### Test with Sample Text:

Use this sample BA text:

```
Login Feature Analysis

User Login Screen:
- Email field (required, text input)
- Password field (required, password input)
- Remember me checkbox (optional)
- Login button
- Forgot password link

Backend Operations:
1. User Authentication API
   - POST /api/auth/login
   - Request: email, password
   - Response: token, user_id
   - Description: Authenticate user credentials

2. Password Reset API
   - POST /api/auth/reset-password
   - Request: email
   - Response: success message
   - Description: Send password reset email

Security Requirements:
- All passwords must be hashed using bcrypt
- Session tokens expire after 24 hours
- Rate limiting: max 5 login attempts per minute

Test Scenarios:
1. Successful Login: User enters valid credentials → authenticated
2. Failed Login: User enters wrong password → error message shown
3. Forgot Password: User clicks forgot password → reset email sent
```

### Test Steps:

1. **Navigate to Import & Merge**
   - Sidebar → **📥 Import & Merge**

2. **Select AI Parse Method**
   - Choose **📝 Paste Text (AI Parse)** radio button
   - Info message: "AI will parse your text into structured format"

3. **Paste Sample Text**
   - Paste the sample BA text above into "Document Text" area
   - Text area should accept the full text

4. **Select Document Type**
   - Document Type: **BA**
   - Document Title: "Login Feature Analysis"

5. **Click Parse with AI**
   - Click **🤖 Parse with AI** button
   - Spinner appears: "🤖 AI is parsing your document..."

6. **Wait for AI Response**
   - Should take 3-10 seconds
   - Success message: "✅ Document parsed successfully!"

7. **Review Parsed JSON**
   - Expander appears: "📋 Parsed JSON Preview"
   - Expand to see the structured JSON
   - Should contain:
     - `ekranlar` array with Login Screen
     - `backend_islemler` array with 2 APIs
     - `guvenlik_gereksinimleri` array
     - `test_senaryolari` array

8. **Auto-Continue**
   - Automatically moves to Step 2: Detect Similar
   - Parsed content ready for merge

**Expected Result:**
- ✅ Text successfully parsed to JSON
- ✅ JSON structure matches BA schema
- ✅ All sections populated correctly
- ✅ Ready for similarity detection and merge

---

## 🎯 Success Criteria

### From BRD Pipeline:
- ✅ Lists completed pipeline runs
- ✅ Shows BA/TA/TC scores
- ✅ Displays JSON previews
- ✅ Imports selected output
- ✅ Auto-populates title
- ✅ Continues to Step 2 automatically

### AI Parse:
- ✅ Accepts unstructured text
- ✅ Calls Gemini API successfully
- ✅ Returns structured JSON
- ✅ Matches document type schema (BA/TA/TC)
- ✅ Shows preview before import
- ✅ Continues to Step 2 automatically

---

## 🐛 Troubleshooting

### BRD Pipeline Import Issues:

**"No pipeline runs found"**
- Run BRD Pipeline first to create a run
- Go to 🚀 BRD Pipeline → Upload BRD → Complete

**"No completed pipeline runs found"**
- Check pipeline status is "completed"
- In-progress runs are hidden
- Wait for current run to finish

**"No outputs found for this pipeline run"**
- Pipeline may have failed without outputs
- Check Pipeline History for error logs
- Re-run the pipeline

**JSON preview shows empty {}**
- Output content may be corrupted
- Check database integrity
- Re-run the pipeline

### AI Parse Issues:

**"Gemini API key not found"**
- Go to Settings (⚙️)
- Add your Gemini API key
- Save and retry

**"AI parsing error: quota/limit"**
- Gemini API quota exhausted
- Wait for quota reset (usually next day)
- Or use JSON import method instead

**"AI returned empty response"**
- Text may be too complex
- Try with simpler/shorter text
- Check API key is valid

**Parsed JSON doesn't match schema**
- AI may have misunderstood text format
- Try being more explicit in your text
- Use clearer section headers
- Or edit the JSON manually after parsing

---

## 💡 Tips for Best Results

### BRD Pipeline Import:
- Use the most recent pipeline run
- Check scores before importing (high scores = better quality)
- Compare revisions to get the best version
- Title auto-populates but can be edited

### AI Text Parsing:
- Use clear section headers (e.g., "Screens:", "APIs:")
- Structure your text logically
- Include field types and requirements explicitly
- Keep text concise but complete
- BA example: "Email field (required, text input)"
- TA example: "POST /api/users - Create user endpoint"
- TC example: "TC-001: Test successful login"

---

## 🔄 Complete Workflow Example

### Scenario: Import Face ID feature from Word doc

1. **Copy text from Word document**
   - User has Face ID feature spec in Word
   - Copy the text content

2. **Use AI Parse**
   - Import & Merge → Paste Text (AI Parse)
   - Paste the text
   - Type: BA
   - Title: "Face ID Login Analysis"
   - Click Parse with AI

3. **Review Parsed JSON**
   - AI converts text → structured JSON
   - Review in preview
   - Automatic continue to Step 2

4. **Detect Similar Documents**
   - System finds existing "Login Analysis" (75% match)
   - Shows similarity breakdown

5. **Compare Side-by-Side**
   - View existing email/password login
   - View new Face ID login
   - Click "Merge Documents"

6. **Smart Merge**
   - Combined: 4 screens (2 old + 2 new)
   - Review merged content
   - Save as new version (v2)

7. **Verify in Library**
   - Document Library → Documents
   - "Login Analysis" now v2
   - Contains both login methods
   - Version history shows merge

**Total time:** ~3 minutes (with AI parsing)

---

## 📊 Feature Comparison

| Feature | Method | Speed | Accuracy | Best For |
|---------|--------|-------|----------|----------|
| Paste JSON | Manual | Fast (5s) | 100% | Pipeline outputs, existing JSON |
| From Pipeline | Automated | Fast (10s) | 100% | Reusing pipeline results |
| AI Parse | AI-powered | Medium (10-30s) | 85-95% | Word docs, unstructured text |

---

## 🎉 What's Next?

After successful import with either method:

1. **Step 2: Detect Similar**
   - System finds related documents automatically
   - Uses TF-IDF + metadata matching

2. **Step 3: Compare**
   - Side-by-side JSON comparison
   - Similarity score displayed

3. **Step 4: Merge**
   - Smart merge with conflict resolution
   - Edit merged content
   - Save as version/new doc/replace

---

## ✅ Testing Checklist

- [ ] BRD Pipeline import works
- [ ] Can list completed runs
- [ ] Can preview BA/TA/TC outputs
- [ ] Import creates correct doc structure
- [ ] AI Parse accepts text input
- [ ] Gemini API responds successfully
- [ ] Parsed JSON matches schema
- [ ] Both methods continue to Step 2
- [ ] Similarity detection works after import
- [ ] Merge workflow completes end-to-end

---

**Features Ready! 🚀**

These two features complete the Import & Merge workflow, allowing users to:
- ✅ Import directly from BRD Pipeline (saves time)
- ✅ Parse Word/text documents with AI (no manual JSON creation)
- ✅ Continue to merge with existing documents
- ✅ Track lineage and versions

**Total Import Methods: 3**
1. 📋 Paste JSON (manual, fast, accurate)
2. 📄 From BRD Pipeline (automated, fast, accurate)
3. 📝 Paste Text (AI-powered, medium, smart)
