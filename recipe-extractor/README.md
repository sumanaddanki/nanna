# Recipe Extractor

Extract recipes from various sources and format them into standardized Markdown.

## Supported Sources

- **YouTube videos** - Cooking/recipe videos
- **Instagram posts/reels** - Cooking content
- **Facebook videos** - Cooking content
- **Images** - Recipe cards, handwritten recipes, screenshots
- **PDFs** - Recipe documents

## Setup

### 1. Install System Dependencies

```bash
# macOS
brew install tesseract tesseract-lang ffmpeg

# For Telugu/Hindi OCR support
brew install tesseract-lang
```

### 2. Create Virtual Environment

```bash
cd recipe-extractor
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

## Usage

```bash
# From YouTube
python extract_recipe.py "https://www.youtube.com/watch?v=VIDEO_ID"

# From Instagram
python extract_recipe.py "https://www.instagram.com/p/POST_ID/"

# From image (supports handwritten recipes!)
python extract_recipe.py "path/to/recipe_photo.jpg"

# From PDF
python extract_recipe.py "path/to/cookbook.pdf"

# Specify output directory
python extract_recipe.py "recipe.jpg" --output my_recipes/
```

## Output

Recipes are saved as Markdown files with:
- Title
- Description
- Prep Time / Cook Time / Servings
- Ingredients (bulleted list)
- Instructions (numbered steps)
- Tips (if applicable)

## Handwritten Recipe Support

The tool uses Tesseract OCR with multi-language support (English, Telugu, Hindi) to extract text from handwritten recipe cards. For best results:
- Use good lighting
- Keep text horizontal
- High resolution images work best

## Legal Note

This tool is for personal use only - extracting recipe facts (ingredients, steps) which are not copyrightable. Not for commercial redistribution.
