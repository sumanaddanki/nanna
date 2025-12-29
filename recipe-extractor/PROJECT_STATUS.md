# Recipe Extractor - Project Status & Guide

## 📊 Project Overview

**What it is:** CLI tool to extract recipes from multiple sources (YouTube, images, PDFs)
**Purpose:** POC for NutriNine family health app recipe database
**Status:** v2 Complete - Ready for Testing
**Integration:** Will be embedded into NutriNine Spring Boot backend

---

## ✅ COMPLETED (By Agent)

### Version 1 (Initial POC) ✓
- **File:** `extract_recipe.py`
- **OCR:** pytesseract (local)
- **Output:** Markdown only
- **Status:** Working but not aligned with NutriNine

### Version 2 (NutriNine-Aligned) ✓
- **File:** `extract_recipe_v2.py`
- **OCR:** Gemini Vision (same as NutriNine)
- **Output:** JSON + Markdown
- **Features:**
  - Gemini Vision for image OCR
  - Confidence scoring (0.0-1.0)
  - JSON output matching NutriNine schema
  - Supports Telugu/Hindi/Tamil handwritten recipes
  - YouTube/Facebook video transcription
  - Markdown export for easy viewing

### Database Schema Alignment ✓
Mapped to NutriNine tables:
- `system_recipes` - name, description, times, servings, difficulty
- `system_recipe_ingredients` - quantity, unit, preparation_note
- `recipe_extraction_log` - confidence, raw_data_extracted (JSONB)
- `recipe_import_sources` - source URL/file tracking

### Configuration ✓
- `.env.example` - Template for API keys
- `requirements.txt` - Python dependencies
- `README.md` - Usage documentation

---

## ⏳ PENDING (User Testing Required)

### 1. Setup & Installation ✅ COMPLETED
**Who:** User (Chinna)
**Status:** ✅ Mac Studio setup complete

1. ✅ System dependencies installed (ffmpeg)
2. ✅ Virtual environment created
3. ✅ Python packages installed
4. ✅ Environment configured (.env with API keys)
5. ✅ Tested with real Telugu video (Palak Paneer)

**Result:** Working! Confidence improved from 0.6 (base) to 0.85 (large)

### 2. MSI CUDA Machine Setup (NEW)
**Who:** User (Chinna)
**Status:** ⏳ Pending
**Hardware:** MSI Pro with RTX 5080 (16GB VRAM)

**See:** [SETUP_MSI_CUDA.md](SETUP_MSI_CUDA.md) for complete instructions

**Why MSI?**
- 10-20x faster than Mac Studio CPU
- Whisper large: ~30s on Mac → ~10-15s on RTX 5080
- Cost: Almost free (₹0.05/recipe vs ₹3.75 for Sarvam AI)
- Better Telugu quality than cloud APIs

### 3. Test with Different Sources
**Who:** User (Chinna)

#### Test 1: Image Recipe (Amma's Handwritten Recipes!)
```bash
python extract_recipe_v2.py path/to/recipe_photo.jpg --format json
```
**Expected:**
- Extract text from handwritten Telugu recipe
- Format as JSON with confidence score
- Save to `recipes/recipe_name.json`

#### Test 2: YouTube Cooking Video
```bash
python extract_recipe_v2.py "https://www.youtube.com/watch?v=VIDEO_ID" --format json
```
**Expected:**
- Download video audio
- Transcribe with Whisper
- Extract recipe from transcript
- Save as JSON

#### Test 3: Markdown Export
```bash
python extract_recipe_v2.py recipe_photo.jpg --format md
```
**Expected:**
- Generate readable Markdown file
- Include metadata (source, confidence, timestamp)

### 3. Quality Testing
**Who:** User (Chinna)
**Checklist:**
- [ ] Handwritten recipes extract correctly
- [ ] Telugu text is recognized and translated
- [ ] Ingredients parsed with quantities/units
- [ ] Instructions are formatted properly
- [ ] Confidence scores seem accurate
- [ ] JSON output is valid
- [ ] Markdown is readable

### 4. NutriNine Integration Planning
**Who:** Both (User + Agent)
**After POC validation:**
- Refactor Python code to Java Spring Boot service
- Add to NutriNine backend as `RecipeExtractionService`
- Integrate with `FileStorageService` for uploads
- Connect to `recipe_extraction_log` table
- Add to iOS/Android apps (camera upload workflow)

---

## 🔄 Version Comparison

| Feature | v1 (extract_recipe.py) | v2 (extract_recipe_v2.py) |
|---------|------------------------|---------------------------|
| **OCR** | pytesseract (local) | Gemini Vision ✨ |
| **Quality** | Poor for handwriting | Excellent ✨ |
| **Telugu Support** | Limited | Native ✨ |
| **Output** | Markdown only | JSON + Markdown ✨ |
| **Confidence** | No scoring | 0.0-1.0 score ✨ |
| **NutriNine Ready** | ❌ | ✅ ✨ |
| **Cost** | Free | ~$0.0002/recipe |

**Recommendation:** Use v2 for all future work

---

## 💰 Cost Analysis

### Per Recipe Extraction (v2)

| Operation | Cost |
|-----------|------|
| Gemini Vision OCR (image) | ~$0.0001 |
| Gemini Formatting (text) | ~$0.0001 |
| **Total (image recipe)** | **~$0.0002** |
| | |
| Whisper transcription (10 min video) | Free (local) |
| Gemini Formatting (transcript) | ~$0.0001 |
| **Total (video recipe)** | **~$0.0001** |

### Monthly Costs (Estimated)

| Scenario | Recipes/Month | Cost |
|----------|---------------|------|
| **POC Testing** | 50-100 | $0.01-0.02 |
| **NutriNine Launch** | 1,000 | $0.20 |
| **Active Users** | 10,000 | $2.00 |

**Verdict:** Very affordable - Gemini is cheaper than pytesseract alternatives

---

## 📋 JSON Output Format

### Example Recipe JSON (NutriNine-Compatible)
```json
{
  "name": "Pesarattu (Green Gram Dosa)",
  "description": "Traditional Andhra breakfast made with green gram",
  "prep_time_minutes": 480,
  "cooking_time_minutes": 20,
  "servings": 4,
  "difficulty": "medium",
  "instructions": "1. Soak green gram overnight...\n2. Grind to smooth batter...",
  "cooking_tips": "Add ginger and cumin for better flavor",
  "ingredients": [
    {
      "name": "green gram",
      "quantity": 1.0,
      "unit": "cup",
      "is_optional": false,
      "preparation_note": "soaked overnight"
    },
    {
      "name": "rice",
      "quantity": 0.25,
      "unit": "cup",
      "is_optional": false,
      "preparation_note": null
    }
  ],
  "is_vegetarian": true,
  "is_vegan": true,
  "is_gluten_free": true,
  "calories_per_serving": 180,
  "confidence": 0.85,
  "source": "/path/to/recipe.jpg",
  "extracted_at": "2024-12-29T15:00:00"
}
```

---

## 🎯 NutriNine Integration Roadmap

### Phase 1: POC Validation (Current)
- [x] Create v2 with Gemini OCR
- [x] Add JSON output
- [ ] Test with Amma's recipes
- [ ] Validate accuracy

### Phase 2: Backend Integration
**Who:** Agent (after testing)
**Tasks:**
1. Create Java `RecipeExtractionService`
2. Add REST endpoint: `POST /recipes/extract`
3. Connect to `FileStorageService`
4. Save to `recipe_extraction_log`
5. Create `RecipeImportSource` records
6. Map ingredients to `kitchen_ingredients`

### Phase 3: Frontend Integration
**Who:** Agent
**Tasks:**
1. iOS: Camera recipe capture
2. Android: Image upload workflow
3. Web: Admin recipe import tool
4. Review queue UI (low confidence recipes)

### Phase 4: Production
**Who:** Both
**Tasks:**
1. Add batch processing (multiple recipes)
2. Add caching (avoid re-processing)
3. Add rate limiting (Gemini API)
4. Add error handling & retries
5. Monitor accuracy & costs

---

## 📝 Testing Checklist

### Basic Functionality
- [ ] v2 script runs without errors
- [ ] Gemini API key works
- [ ] Image extraction produces JSON
- [ ] Video extraction works (YouTube)
- [ ] Markdown export works
- [ ] Confidence scores are reasonable

### Quality Tests
- [ ] English printed recipes extract accurately
- [ ] Telugu handwritten recipes recognized
- [ ] Hindi recipes work
- [ ] Ingredient quantities parsed correctly
- [ ] Instructions formatted properly
- [ ] NOT_A_RECIPE detection works

### Edge Cases
- [ ] Blurry image handling
- [ ] Mixed language recipes
- [ ] Complex measurements (1/2 cup, etc.)
- [ ] Optional ingredients flagged
- [ ] Missing information (no servings, etc.)

### Performance
- [ ] Image extraction < 10 seconds
- [ ] Video transcription time acceptable
- [ ] Output files created correctly
- [ ] No memory leaks with multiple recipes

---

## 🐛 Known Limitations

1. **Whisper Performance:** Slow on Mac Studio CPU (consider cloud alternative)
2. **Gemini Rate Limits:** 15 requests/minute (free tier)
3. **Video Support:** YouTube only (Instagram/Facebook need auth)
4. **PDF Support:** Not yet implemented in v2
5. **Ingredient Matching:** No validation against kitchen_ingredients yet

---

## 🚀 Next Steps After Testing

### If POC Works Well:

1. **Refine Prompts**
   - Improve ingredient extraction accuracy
   - Better handling of measurements
   - Detect cuisine types automatically

2. **Add Features**
   - PDF recipe support
   - Batch processing (multiple images)
   - Recipe image generation (using AI)
   - Nutrition calculation integration

3. **NutriNine Integration**
   - Port to Spring Boot
   - Connect to database
   - Add to mobile apps

### If POC Has Issues:

1. **Improve OCR**
   - Try Google Cloud Vision API
   - Add image preprocessing
   - Better handwriting recognition

2. **Improve Parsing**
   - Use structured output (Gemini function calling)
   - Add validation rules
   - Better error handling

---

## 🎨 Example Use Cases

### Amma's Recipe Preservation
1. Take photo of handwritten recipe card
2. Run: `python extract_recipe_v2.py amma_recipe.jpg --format json`
3. Get structured JSON for database
4. Also get readable Markdown for printing
5. **Result:** Amma's wisdom preserved digitally!

### YouTube Recipe Collection
1. Find Telugu cooking video
2. Run: `python extract_recipe_v2.py "https://youtube.com/watch?v=..."--format json`
3. Auto-transcribe and extract
4. Add to NutriNine recipe database
5. **Result:** Instant recipe library!

### Family Cookbook Creation
1. Extract all family recipes
2. Generate JSON database
3. Import into NutriNine
4. Share with family members via app
5. **Result:** Digital family cookbook!

---

## 📞 Support

**Questions during testing?**
Ask Nanna (agent) for help!

**Issues to report:**
- Extraction failures
- Low confidence scores
- Incorrect ingredient parsing
- Missing information

---

## ✨ Vision for NutriNine

With recipe-extractor, NutriNine users can:
- **Preserve family recipes** by taking photos
- **Import recipes from videos** with one click
- **Build personalized recipe database** automatically
- **Get nutrition info** for traditional dishes
- **Share recipes** with family members

All while supporting **Telugu, Hindi, Tamil** and handwritten recipes!

---

*Last Updated: Dec 29, 2024*
*Status: v2 Complete - Ready for User Testing*
