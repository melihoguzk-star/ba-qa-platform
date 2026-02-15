# 📥 Import & Merge - Test Guide

## ✅ Backend Tests: PASSED

All automated tests passed successfully:
- Template creation ✅
- Import simulation ✅
- Similarity detection ✅
- Merge logic ✅
- JSON validation ✅

---

## 🎬 UI Test - Step by Step

### **Scenario: Import Face ID Analysis and Merge with Login Analysis**

---

## Prerequisites

1. **Start Streamlit:**
   ```bash
   cd /Users/melihoguz/ba-qa-platform
   source venv/bin/activate
   streamlit run app.py
   ```

2. **Test Data Ready:**
   - `test_face_id.json` file created ✅
   - Login Analysis template exists in database ✅

---

## Test Steps

### **Step 1: Open Import & Merge** ⏱️ 10 seconds

1. Open browser: http://localhost:8501
2. Sidebar → Click **📥 Import & Merge**
3. You should see: "Step 1: Import Document"

**Expected:**
```
🟢 1. Import
⚪ 2. Detect Similar
⚪ 3. Compare
⚪ 4. Merge
```

---

### **Step 2: Import Face ID JSON** ⏱️ 30 seconds

1. Make sure **"📋 Paste JSON"** is selected
2. Open `test_face_id.json` in editor
3. Copy all content (Cmd+A, Cmd+C)
4. Paste into "Document JSON" text area
5. **Document Type:** Select "BA"
6. **Document Title:** Type "Face ID Login Analysis"
7. Click **"➡️ Import & Analyze"**

**Expected:**
- ✅ "Document parsed successfully!"
- Progress changes to: 🟢 1. Import, 🟢 2. Detect Similar

**If Error:**
- Check JSON is valid (no trailing commas, proper quotes)
- Make sure you copied the entire JSON

---

### **Step 3: Review Similar Documents** ⏱️ 30 seconds

System automatically searches for similar documents.

**Expected Results:**
```
✅ Found X similar documents

🟢 User Authentication System - 75% match
   Match Score: 75%
   - Content Similarity: 65%
   - Metadata Match: 85%
   [Compare & Merge] button

🟠 Login Analysis - 60% match
   ...
```

**What to Check:**
- ✅ At least one similar document found
- ✅ "Login" or "Authentication" in results
- ✅ Match percentage shows (should be > 20%)

**Actions:**
1. Expand the top result (highest match)
2. Review the similarity scores
3. Click **"Compare & Merge"** on top result

**Alternative:**
- If no similar docs: Click "Save as New Document" (still works!)
- If you want to skip merge: Click "Skip Merge → Save as New"

---

### **Step 4: Compare Side-by-Side** ⏱️ 1 minute

You should see two columns:

**Left Column: 📄 Existing Document**
```
Title: "User Authentication System" (or similar)
Type: BA
Version: v1
Content: [JSON preview with email/password login]
```

**Right Column: 📥 New Document**
```
Title: "Face ID Login Analysis"
Type: BA
Status: Imported
Content: [JSON preview with Face ID biometric]
```

**What to Check:**
- ✅ Both JSONs are displayed
- ✅ You can scroll and read both
- ✅ Left = existing (email/password)
- ✅ Right = new (Face ID)

**Actions:**
1. Review both documents
2. Scroll through content
3. Decide: Merge or Save Separate?
   - **"➡️ Merge Documents"** → Continue to merge
   - **"Save New (No Merge)"** → Save as separate doc
   - **"⬅️ Back"** → Go back to similar docs

**For testing:** Click **"➡️ Merge Documents"**

---

### **Step 5: Smart Merge** ⏱️ 2 minutes

**What You'll See:**
```
Step 4: Smart Merge
Merging: Face ID Login Analysis + User Authentication System
```

**Merged Content Preview:**
The system automatically combines both documents:
- Arrays are merged (ekranlar, backend_islemler)
- Original screens + Face ID screens
- Should show 4-5 total screens

**What to Do:**

1. **Review Merged JSON:**
   - Scroll through the merged content
   - Check that both login methods are present
   - Look for:
     - "Login Screen" (original)
     - "Face ID Login Screen" (new)
     - All backend operations combined

2. **Edit if Needed:**
   - You can edit the JSON directly
   - Add/remove sections
   - Fix any conflicts
   - Click **"✓ Validate Merged JSON"** after edits

3. **Choose Save Option:**
   - **💾 Update existing (new version)** ← RECOMMENDED
     - Creates v2 of existing document
     - Preserves history
     - Best for evolution

   - **📝 Save as new document**
     - Creates separate document
     - Links to original (lineage)
     - Good for variants

   - **🔄 Replace existing**
     - Overwrites current
     - No version history
     - Use with caution

4. **Set Title:**
   - Default: "User Authentication System (Merged)"
   - Change if desired

5. **Click:** **"💾 Save Merged Document"**

**Expected:**
- ✅ "Updated ... with merged content! (v2)" or
- ✅ "Saved as new document! (ID: X)"
- 🎈 Balloons animation!

---

### **Step 6: Verify in Document Library** ⏱️ 1 minute

1. Sidebar → Click **📚 Document Library**
2. Go to **📄 Documents** tab
3. Find your merged document

**What to Check:**

**If you chose "Update existing":**
- ✅ Document shows v2 (or higher)
- ✅ Click "Version History" button
- ✅ Should show v1, v2 with change notes
- ✅ v2 note: "Merged with Face ID Login Analysis"

**If you chose "Save as new":**
- ✅ New document appears in list
- ✅ Title includes "(Merged)"
- ✅ Metadata shows: 🌳 "Adapted from: ..."
- ✅ Click "🌳 View Lineage" button
- ✅ Shows source document link

**Content Verification:**
1. Click "View Content" button
2. Scroll through JSON
3. Confirm both login methods present:
   - Email/password login ✅
   - Face ID biometric login ✅
4. Check backend operations include both ✅

---

## 🎯 Success Criteria

### ✅ All These Should Work:

1. **Import** - Face ID JSON imported without errors
2. **Detection** - System found similar "Login" documents
3. **Similarity** - Match score displayed (> 20%)
4. **Comparison** - Side-by-side view worked
5. **Merge** - Combined content makes sense
6. **Validation** - Merged JSON is valid
7. **Save** - Document saved successfully
8. **Verification** - Can view merged doc in library
9. **Lineage** - Version history or source link present
10. **Content** - Both login methods in final document

---

## 🐛 Troubleshooting

### "Invalid JSON" Error
- **Cause:** Syntax error in pasted JSON
- **Fix:** Use `test_face_id.json` - it's pre-validated
- **Check:** Trailing commas, quotes, brackets

### "No similar documents found"
- **Cause:** No existing login/auth documents
- **Fix:** Click "Save as New Document" - still works!
- **Alternative:** Run `python demo_documents.py` first

### "Error saving"
- **Cause:** Database permission or path issue
- **Fix:** Check `data/baqa.db` exists and writable
- **Alternative:** Re-run `python migrate_phase3.py`

### Merge content is empty
- **Cause:** Both documents have different structure
- **Fix:** Edit manually in the JSON editor
- **Check:** Use "✓ Validate" before saving

### Version history not showing
- **Cause:** Used "Replace" instead of "Update"
- **Fix:** Next time use "Update existing (new version)"
- **Note:** This is by design for replace option

---

## 📊 Expected Results Summary

| Step | Action | Expected Result | Time |
|------|--------|----------------|------|
| 1 | Open Import & Merge | Progress indicator shows | 10s |
| 2 | Paste JSON & Import | "Document parsed successfully!" | 30s |
| 3 | Auto-detect similar | "Found X similar documents" | 30s |
| 4 | Compare side-by-side | Two JSON previews displayed | 1m |
| 5 | Merge & save | "Updated ... (v2)" + Balloons | 2m |
| 6 | Verify in library | Document with v2 or lineage | 1m |

**Total Time:** ~5 minutes

---

## 🎉 Success!

If all steps passed:
- ✅ Import & Merge is fully operational!
- ✅ Face ID analysis successfully merged
- ✅ Template-based workflow working
- ✅ Your use case is solved!

---

## 💡 Next Steps

**Real-World Usage:**
1. Run BRD Pipeline for Face ID feature
2. Copy output JSON
3. Import & Merge with existing Login analysis
4. Review merged result
5. Save as new version
6. Continue development with combined spec

**Experiment:**
- Try merging different document types
- Test with TA (Technical Analysis)
- Test with TC (Test Cases)
- Create variants of same feature
- Build a document evolution tree

---

## 📝 Feedback

After testing, note:
- What worked well? ✅
- What was confusing? ❓
- What features are missing? 💭
- What should be improved? 🔧

Share feedback to improve the workflow!

---

**Test completed! 🎊**
