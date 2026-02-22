# BRD Pipeline - Test Checklist

## ✅ Automated Test Results

**Visual Tests:** PASSED ✓
- Page loads correctly
- 12-step progress bar visible
- Form renders with all fields
- Screenshots saved: `/tmp/brd_pipeline_01_initial.png`

---

## 📋 Manual Test Checklist

### 1. Initial Upload Step ✅

**Navigate to:** http://localhost:5173/brd-pipeline

**Verify:**
- [ ] Page title "BRD Pipeline" visible
- [ ] 12-step progress bar showing "BRD Yükleme" as current
- [ ] Form has these fields:
  - [ ] Proje dropdown
  - [ ] BRD İçeriği textarea
  - [ ] Dosya Yükle button
  - [ ] Figma URL input (optional)
  - [ ] BA/TA/TC checkboxes (all checked by default)
  - [ ] "Pipeline Başlat" button

**Test Actions:**
1. Click "Pipeline Başlat" without filling → Should show validation error ✓
2. Select a project from dropdown
3. Enter BRD content (sample):
```
Proje: Test Projesi
Amaç: Kullanıcı login sistemi
Kapsam: Login, logout, şifre sıfırlama
```
4. Click "Pipeline Başlat" → Should succeed

**Expected Result:**
- Message: "Pipeline oluşturuldu. BA üretimi başlatabilirsiniz."
- Progress moves to step 2: "BA Üretim"

---

### 2. BA Generation Step

**Verify:**
- [ ] Card title: "BA Doküman Üretimi"
- [ ] Alert message: "BA dokümanını üretmek için butona tıklayın"
- [ ] "BA Üret" button visible

**Test Actions:**
1. Click "BA Üret"

**Expected Result:**
- Spinner appears
- Message: "BA dokümanı Claude tarafından üretiliyor..."
- After 30-60 seconds, auto-advances to "BA İnceleme"

**Status API Check:**
```bash
# While generation is running:
curl http://localhost:8000/api/v1/pipeline/{run_id}/status
# Should return: {"status": "running", "current_stage": "ba_gen"}
```

---

### 3. BA Review Step

**Verify:**
- [ ] Card title: "BA İnceleme ve Düzenleme"
- [ ] Monaco Editor (VS Code style) visible
- [ ] JSON content loaded
- [ ] "Onayla ve QA'ya Geç" button

**Test Actions:**
1. Review generated BA JSON
2. (Optional) Edit content in Monaco Editor
3. Click "Onayla ve QA'ya Geç"

**Expected Result:**
- If edited: Message "Değişiklikler kaydedildi"
- Moves to step 4: "BA QA"

---

### 4. BA QA Evaluation Step

**Verify:**
- [ ] Card title: "BA Kalite Değerlendirmesi"
- [ ] Alert: "BA dokümanı Gemini tarafından değerlendirilecek"
- [ ] Two buttons:
  - [ ] "QA Değerlendirmesi Yap"
  - [ ] "QA'yı Atla (Force Pass)"

**Test Actions:**

**Option A: Normal QA**
1. Click "QA Değerlendirmesi Yap"
2. Wait 10-15 seconds

**Expected Results:**
- If score ≥ 60:
  - Green success alert
  - Progress bar showing score
  - Auto-advances to "TA Üretim" after 1.5s
- If score < 60:
  - Yellow warning alert
  - Suggestions list shown
  - Options: "Geri Dön ve Düzenle" or "Yine de Devam Et"

**Option B: Force Pass**
1. Click "QA'yı Atla (Force Pass)"

**Expected Results:**
- Score: 100
- Assessment: "Force passed by user"
- Advances to "TA Üretim"

---

### 5. TA Generation Step

**Same flow as BA:**
1. Click "TA Üret"
2. Wait for generation (30-60s)
3. Review in Monaco Editor
4. Approve and go to QA
5. Evaluate QA or force pass

---

### 6. TA QA → Figma Upload

**After TA QA passes:**
- [ ] Advances to "Figma (Opsiyonel)" step
- [ ] Option to skip: "Figma Olmadan Devam Et"

**Test Actions:**
1. Click "Figma Olmadan Devam Et"

**Expected Result:**
- Advances to "TC Üretim"

---

### 7. TC Generation Step

**Same flow as BA/TA:**
1. Click "TC Üret"
2. Wait for generation
3. Review + edit if needed
4. QA evaluation

---

### 8. Completion Step (Done)

**Verify:**
- [ ] Card title: "Pipeline Tamamlandı!"
- [ ] Green checkmark icon
- [ ] Success alert
- [ ] "Yeni Pipeline" button
- [ ] "Üretilen Dokümanlar" card with:
  - [ ] BA card with content
  - [ ] TA card with content
  - [ ] TC card with content
  - [ ] Each has QA score progress bar
  - [ ] "Kütüphaneye Kaydet" button
  - [ ] "Export" button

**Test Actions:**
1. Click "Kütüphaneye Kaydet" for BA

**Expected Result:**
- Message: "BA dokümanı kütüphaneye kaydedildi"
- Document appears in Documents page

2. Click "Yeni Pipeline"

**Expected Result:**
- Resets to step 1 (upload)
- Form is cleared

---

## 🧪 Backend API Testing

### Check Pipeline Status
```bash
# Get run ID from network tab or console
RUN_ID=1

# Check status
curl http://localhost:8000/api/v1/pipeline/$RUN_ID/status | jq

# Expected stages:
# ba_generation → ba_qa → ta_generation → ta_qa → figma_upload → tc_generation → tc_qa → completed
```

### Check Checkpoint
```bash
# Get checkpoint for BA
curl http://localhost:8000/api/v1/pipeline/$RUN_ID/checkpoint/ba_gen | jq

# Should return generated BA JSON
```

### Get Results
```bash
# Get final results
curl http://localhost:8000/api/v1/pipeline/$RUN_ID/results | jq

# Should return:
# {
#   "ba": {...},
#   "ta": {...},
#   "tc": {...},
#   "scores": {
#     "ba": 75,
#     "ta": 82,
#     "tc": 68
#   }
# }
```

---

## 🐛 Known Issues / Edge Cases

### Issue 1: Generation Timeout
- **Symptom:** Pipeline stuck in "running" state
- **Check:** Backend logs for errors
- **Fix:** Restart pipeline

### Issue 2: QA Evaluation Fails
- **Symptom:** Error message during QA
- **Workaround:** Use "Force Pass" option
- **Root Cause:** Gemini API quota or rate limit

### Issue 3: Monaco Editor Not Loading
- **Symptom:** Blank editor in review step
- **Fix:** Refresh page
- **Check:** Console for errors

---

## ✅ Test Summary

**Current Status:**
- ✅ UI renders correctly
- ✅ Form validation works
- ✅ 12-step workflow implemented
- ⏳ Backend integration (needs testing with real API)
- ⏳ Monaco Editor (needs manual verification)
- ⏳ QA evaluation (needs Gemini API)

**Next Steps:**
1. Test full workflow end-to-end
2. Verify checkpoint persistence
3. Test force pass functionality
4. Export DOCX (if implemented)

---

## 📸 Screenshots

Saved at:
- `/tmp/brd_pipeline_01_initial.png` - Initial upload form ✓
- `/tmp/brd_pipeline_02_form.png` - Form details
- `/tmp/brd_pipeline_03_validation.png` - Validation errors

**Manual Screenshots Needed:**
- BA generation in progress
- BA review with Monaco Editor
- QA results (pass and fail)
- Final completion screen
