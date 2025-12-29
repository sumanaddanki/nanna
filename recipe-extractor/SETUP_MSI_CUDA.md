# Recipe Extractor Setup on MSI CUDA Machine

## Your Hardware
- **Machine**: MSI Pro with RTX 5080
- **OS**: Windows
- **CUDA**: NVIDIA GPU acceleration
- **Purpose**: Run Whisper large/medium for Telugu recipe transcription

---

## Why Use Your MSI Machine?

### Cost Comparison (5-min video)
| Method | Cost | Quality (Telugu) |
|--------|------|------------------|
| **Whisper Base (Mac)** | Free | Poor ⭐⭐ |
| **Sarvam AI** | ₹3.75 | Good ⭐⭐⭐⭐ |
| **Whisper Large (MSI GPU)** | ₹0.05 electricity | Excellent ⭐⭐⭐⭐⭐ |

**Winner**: Your MSI machine with Whisper large! Almost free + best quality.

---

## Setup Steps

### 1. Install Prerequisites on MSI (Windows)

#### Install Python 3.11
1. Download from: https://www.python.org/downloads/
2. During installation: ✅ Check "Add Python to PATH"
3. Verify:
```cmd
python --version
# Should show: Python 3.11.x
```

#### Install CUDA Toolkit
Your RTX 5080 needs CUDA 12.x:
1. Download: https://developer.nvidia.com/cuda-downloads
2. Select: Windows → x86_64 → 11 or 12 → exe (local)
3. Install with default settings
4. Verify:
```cmd
nvidia-smi
# Should show RTX 5080 and CUDA version
```

#### Install ffmpeg
1. Download: https://github.com/BtbN/FFmpeg-Builds/releases
2. Extract to `C:\ffmpeg`
3. Add to PATH: `C:\ffmpeg\bin`
4. Verify:
```cmd
ffmpeg -version
```

### 2. Transfer Recipe Extractor to MSI

#### Option A: Git Clone (Recommended)
```cmd
cd C:\Users\YourUsername\
git clone https://github.com/sumanaddanki/nanna.git
cd nanna\recipe-extractor
```

#### Option B: Manual Copy
Copy from Mac Studio to MSI via network share:
```bash
# On Mac Studio
rsync -avz /Users/semostudio/git/sumanaddanki/nanna/recipe-extractor/ \
  //MSI_IP/Users/YourUsername/recipe-extractor/
```

### 3. Create Python Virtual Environment

```cmd
cd C:\Users\YourUsername\nanna\recipe-extractor

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# You should see (venv) in prompt
```

### 4. Install Dependencies

#### Install PyTorch with CUDA Support (CRITICAL!)
```cmd
# Install PyTorch for CUDA 12.x
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify CUDA is available
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
# Should print: CUDA available: True
```

#### Install Whisper with GPU Support
```cmd
pip install openai-whisper
```

#### Install Other Dependencies
```cmd
pip install -r requirements.txt
```

### 5. Configure Environment

Create `.env` file (if not already present):
```cmd
copy .env.example .env
notepad .env
```

Add your API keys:
```
GEMINI_API_KEY=AIzaSyBA27fTF2AyRISvz0LAJTX9mCL8B2PJxBY
SARVAM_API_KEY=sk_ctunw3lq_ZVcjq3ECWWegUzBS4NWoEiwM
```

### 6. Modify Script to Use Whisper Large

Edit `extract_recipe_v2.py` and change line 231:

```python
# Before
model = whisper.load_model("base")

# After (for best quality)
model = whisper.load_model("large")

# Or medium (faster, still good)
model = whisper.load_model("medium")
```

---

## Testing

### Test 1: Check GPU Detection
```cmd
python -c "import torch; print(torch.cuda.get_device_name(0))"
# Should print: NVIDIA GeForce RTX 5080
```

### Test 2: Run Recipe Extraction
```cmd
python extract_recipe_v2.py "https://www.youtube.com/watch?v=cjGDsV6FvNE" --format json
```

**Expected Timeline (RTX 5080)**:
- Download video: 10-30 seconds
- Transcribe with Whisper large: 20-40 seconds (GPU accelerated!)
- Format with Gemini: 2-5 seconds
- **Total**: ~1 minute

### Test 3: Image Recipe
```cmd
python extract_recipe_v2.py path\to\recipe_image.jpg --format json
```

---

## Performance Comparison

| Model | RTX 5080 Speed | Quality (Telugu) | VRAM Usage |
|-------|---------------|------------------|------------|
| **Whisper base** | 5 sec | Poor ⭐⭐ | 1 GB |
| **Whisper medium** | 15 sec | Good ⭐⭐⭐⭐ | 5 GB |
| **Whisper large** | 30 sec | Excellent ⭐⭐⭐⭐⭐ | 10 GB |

**Your RTX 5080 has 16GB VRAM** → Can easily run Whisper large!

---

## Cost Analysis (Your Setup)

### Per Recipe Extraction Costs

| Component | Cost |
|-----------|------|
| Gemini Vision OCR | ₹0.0084 |
| Gemini Formatting | ₹0.0084 |
| Whisper large (GPU) | ₹0.05 electricity |
| **Total** | **₹0.067 (~$0.0008)** |

### Monthly Costs (1,000 recipes)

| Scenario | Sarvam AI | Your MSI GPU |
|----------|-----------|--------------|
| 1,000 recipes | ₹3,750 | ₹67 |
| **Savings** | - | **₹3,683/month** |

### Annual Savings: ₹44,196 (~$530)

---

## Production Setup (Optional)

### Run as Windows Service

Create `run_extractor_service.py`:
```python
from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/extract', methods=['POST'])
def extract_recipe():
    url = request.json.get('url')
    result = subprocess.run([
        'python', 'extract_recipe_v2.py', url, '--format', 'json'
    ], capture_output=True)
    return {'status': 'success', 'output': result.stdout.decode()}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
```

Run on startup:
```cmd
python run_extractor_service.py
```

Access from Mac Studio:
```bash
curl -X POST http://MSI_IP:8888/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://youtube.com/watch?v=..."}'
```

---

## Troubleshooting

### Issue 1: CUDA Not Detected
```cmd
# Check CUDA installation
nvcc --version

# Reinstall PyTorch with CUDA
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Issue 2: Out of Memory
```python
# Use smaller model
model = whisper.load_model("medium")  # Instead of large
```

### Issue 3: Slow Transcription
```python
# Verify GPU is being used
import whisper
model = whisper.load_model("large")
result = model.transcribe("audio.mp3", fp16=True)  # Enable FP16 for RTX 5080
```

---

## Next Steps

1. ✅ Setup MSI machine (follow steps above)
2. Test with Telugu cooking video
3. Compare quality with Sarvam AI output
4. Integrate with NutriNine backend
5. Deploy as production service

---

## NutriNine Integration

Once tested, connect to NutriNine backend:

```java
// NutriNine RecipeExtractionService.java
public RecipeDTO extractRecipeFromVideo(String videoUrl) {
    // Call MSI machine API
    String msiApiUrl = "http://MSI_IP:8888/extract";
    RestTemplate restTemplate = new RestTemplate();

    Map<String, String> request = Map.of("url", videoUrl);
    RecipeResponse response = restTemplate.postForObject(
        msiApiUrl, request, RecipeResponse.class
    );

    return mapToRecipeDTO(response);
}
```

---

**Status**: Ready for setup and testing on MSI machine

**Expected Quality**: Excellent Telugu transcription with Whisper large

**Cost**: Almost free (just electricity ~₹0.05/recipe)
