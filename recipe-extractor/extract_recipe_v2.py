#!/usr/bin/env python3
"""
Recipe Extractor CLI v2 - Aligned with NutriNine
Extracts recipes from YouTube, Instagram, Facebook, images, and PDFs.
Uses Gemini Vision for OCR and formatting.

Usage:
    python extract_recipe_v2.py <url_or_file_path> --output recipes/ --format json
"""

import argparse
import os
import sys
import re
import json
import tempfile
import subprocess
import base64
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
import google.generativeai as genai

# Load environment variables
load_dotenv()

console = Console()

# Gemini OCR Prompt (aligned with NutriNine)
GEMINI_OCR_PROMPT = """Extract ALL text from this image exactly as it appears.

This could be a recipe card, handwritten recipe, or screenshot.

Rules:
1. Include ALL text - ingredients, measurements, instructions, everything
2. Preserve layout and structure
3. For handwritten text, do your best to read it accurately
4. If text is unclear, include it with [?] marker
5. Do not interpret - just extract raw text
6. If multilingual (Telugu/Hindi/Tamil), preserve original and add translation

Return ONLY the extracted text."""

# Gemini Recipe Formatting Prompt
GEMINI_RECIPE_PROMPT = """You are a recipe formatter. Extract and format the recipe information into JSON.

Given raw text from a cooking video/image/document, extract:
- name (recipe title)
- description (1-2 sentences)
- prep_time_minutes (integer, estimate if not specified)
- cooking_time_minutes (integer, estimate if not specified)
- servings (integer, estimate if not specified)
- difficulty (easy/medium/hard)
- instructions (string, numbered steps)
- cooking_tips (optional string)
- ingredients (array of objects with: name, quantity, unit, is_optional, preparation_note)
- is_vegetarian (boolean)
- is_vegan (boolean)
- is_gluten_free (boolean)
- calories_per_serving (integer, estimate if possible)
- confidence (0.0-1.0, your confidence in extraction accuracy)

If the content is NOT a recipe, return: {"is_recipe": false, "reason": "..."}

If text is in regional language (Telugu, Hindi, Tamil), translate to English but keep dish names original.

Return ONLY valid JSON, no markdown code blocks."""


def gemini_ocr_image(image_path: str) -> tuple:
    """
    Extract text from image using Gemini Vision
    Returns: (extracted_text, confidence)
    """
    console.print("[yellow]Extracting text with Gemini Vision...[/yellow]")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    # Read and encode image
    with open(image_path, 'rb') as f:
        image_data = f.read()

    image_b64 = base64.b64encode(image_data).decode('utf-8')

    # Determine mime type
    ext = Path(image_path).suffix.lower()
    mime_map = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    mime_type = mime_map.get(ext, 'image/jpeg')

    # Call Gemini Vision
    response = model.generate_content([
        {'text': GEMINI_OCR_PROMPT},
        {'inline_data': {'mime_type': mime_type, 'data': image_b64}}
    ])

    extracted_text = response.text

    # Estimate confidence based on text quality
    confidence = estimate_ocr_confidence(extracted_text)

    return extracted_text, confidence


def estimate_ocr_confidence(text: str) -> float:
    """Estimate OCR confidence score"""
    if not text or len(text) < 10:
        return 0.3

    confidence = 0.5  # Base

    # Check for recipe keywords
    recipe_keywords = ['ingredients', 'instructions', 'serves', 'prep', 'cook', 'cup', 'tablespoon', 'tsp', 'tbsp']
    keyword_count = sum(1 for kw in recipe_keywords if kw.lower() in text.lower())
    confidence += min(keyword_count * 0.05, 0.3)

    # Check for numbers (measurements)
    if re.search(r'\d+', text):
        confidence += 0.1

    # Check for [?] markers (uncertainty)
    if '[?]' in text:
        confidence -= 0.2

    return min(max(confidence, 0.0), 1.0)


def format_with_gemini(raw_text: str) -> dict:
    """
    Format extracted text into structured recipe JSON using Gemini
    Returns: dict with recipe data
    """
    console.print("[yellow]Formatting recipe with Gemini AI...[/yellow]")

    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    prompt = f"{GEMINI_RECIPE_PROMPT}\n\n---\n\nRaw text:\n\n{raw_text}"

    response = model.generate_content(prompt)
    result_text = response.text.strip()

    # Remove markdown code blocks if present
    result_text = re.sub(r'```json\n?', '', result_text)
    result_text = re.sub(r'```\n?', '', result_text)

    try:
        recipe_data = json.loads(result_text)
        return recipe_data
    except json.JSONDecodeError as e:
        console.print(f"[red]Failed to parse JSON response: {e}[/red]")
        console.print(f"[dim]Raw response: {result_text[:500]}[/dim]")
        raise


def download_video_audio(url: str, output_dir: str) -> str:
    """Download video using yt-dlp and extract audio"""
    console.print("[yellow]Downloading video...[/yellow]")

    audio_path = os.path.join(output_dir, "audio.mp3")

    # Use Python module instead of command to avoid PATH issues
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "-x", "--audio-format", "mp3",
        "--audio-quality", "0",
        "-o", audio_path.replace(".mp3", ".%(ext)s"),
        url
    ]

    # Add ffmpeg location for Windows
    import platform
    if platform.system() == 'Windows':
        ffmpeg_exe = r'C:\ffmpeg\bin\ffmpeg.exe'
        if os.path.exists(ffmpeg_exe):
            cmd.extend(["--ffmpeg-location", r"C:\ffmpeg\bin"])

    subprocess.run(cmd, check=True, capture_output=True)

    # Find downloaded file
    for f in os.listdir(output_dir):
        if f.startswith("audio") and f.endswith(".mp3"):
            return os.path.join(output_dir, f)

    return audio_path


def transcribe_audio_sarvam(audio_path: str) -> str:
    """Transcribe audio using Sarvam AI (better for Telugu/Indic languages)"""
    console.print("[yellow]Transcribing audio with Sarvam AI...[/yellow]")

    import requests

    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        console.print("[yellow]Sarvam API key not found, falling back to Whisper[/yellow]")
        return transcribe_audio_whisper(audio_path)

    url = "https://api.sarvam.ai/speech-to-text"
    headers = {"api-subscription-key": api_key}

    with open(audio_path, 'rb') as audio_file:
        files = {'file': audio_file}
        data = {
            'model': 'saarika:v2.5',
            'language_code': 'unknown'  # Auto-detect
        }

        try:
            response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get('transcript', '')
        except Exception as e:
            console.print(f"[yellow]Sarvam AI failed ({e}), falling back to Whisper[/yellow]")
            return transcribe_audio_whisper(audio_path)


def transcribe_audio_whisper(audio_path: str, model_size: str = "large") -> str:
    """Transcribe audio using Whisper (fallback)

    Args:
        audio_path: Path to audio file
        model_size: Whisper model size (tiny/base/small/medium/large)
                   Default: large (best for Telugu/multilingual)
    """
    console.print(f"[yellow]Transcribing audio with Whisper ({model_size})...[/yellow]")

    import whisper
    import torch

    # Check if CUDA is available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    console.print(f"[dim]Using device: {device}[/dim]")

    if device == "cuda":
        console.print(f"[dim]GPU: {torch.cuda.get_device_name(0)}[/dim]")

    # Load model
    model = whisper.load_model(model_size, device=device)

    # Transcribe with FP16 for GPU acceleration
    fp16 = device == "cuda"
    result = model.transcribe(audio_path, fp16=fp16, language="te")  # Telugu hint

    return result["text"]


def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio - tries Sarvam AI first, falls back to Whisper"""
    return transcribe_audio_sarvam(audio_path)


def save_as_markdown(recipe_data: dict, output_dir: str, source: str) -> str:
    """Save recipe as Markdown file"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Generate filename
    name = recipe_data.get('name', 'recipe')
    filename = re.sub(r'[^\w\s-]', '', name)
    filename = re.sub(r'\s+', '_', filename).strip()[:50]
    filepath = os.path.join(output_dir, f"{filename}.md")

    # Build markdown content
    md = f"""---
source: {source}
extracted: {datetime.now().isoformat()}
confidence: {recipe_data.get('confidence', 0.0):.2f}
---

# {recipe_data.get('name', 'Untitled Recipe')}

{recipe_data.get('description', '')}

**Prep Time:** {recipe_data.get('prep_time_minutes', 0)} min
**Cook Time:** {recipe_data.get('cooking_time_minutes', 0)} min
**Servings:** {recipe_data.get('servings', 4)}
**Difficulty:** {recipe_data.get('difficulty', 'medium')}

## Ingredients

"""

    for ing in recipe_data.get('ingredients', []):
        optional = " (optional)" if ing.get('is_optional') else ""
        prep_note = f", {ing.get('preparation_note')}" if ing.get('preparation_note') else ""
        md += f"- {ing.get('quantity', '')} {ing.get('unit', '')} {ing.get('name', '')}{prep_note}{optional}\n"

    md += f"\n## Instructions\n\n{recipe_data.get('instructions', '')}\n"

    if recipe_data.get('cooking_tips'):
        md += f"\n## Tips\n\n{recipe_data.get('cooking_tips')}\n"

    # Write file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md)

    return filepath


def save_as_json(recipe_data: dict, output_dir: str, source: str) -> str:
    """Save recipe as JSON file (NutriNine format)"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Generate filename
    name = recipe_data.get('name', 'recipe')
    filename = re.sub(r'[^\w\s-]', '', name)
    filename = re.sub(r'\s+', '_', filename).strip()[:50]
    filepath = os.path.join(output_dir, f"{filename}.json")

    # Add metadata
    recipe_data['source'] = source
    recipe_data['extracted_at'] = datetime.now().isoformat()

    # Write JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(recipe_data, f, indent=2, ensure_ascii=False)

    return filepath


def process_image(image_path: str, output_dir: str, output_format: str):
    """Process image recipe"""
    # Extract text with Gemini Vision
    raw_text, ocr_confidence = gemini_ocr_image(image_path)

    console.print(f"\n[dim]Extracted text (confidence: {ocr_confidence:.2f}):[/dim]")
    console.print(f"[dim]{raw_text[:500]}...[/dim]\n")

    # Format with Gemini
    recipe_data = format_with_gemini(raw_text)

    # Check if it's actually a recipe
    if recipe_data.get('is_recipe') == False:
        console.print(f"[yellow]Not a recipe: {recipe_data.get('reason', 'Unknown')}[/yellow]")
        return

    # Update confidence (combine OCR + formatting confidence)
    recipe_data['confidence'] = (ocr_confidence + recipe_data.get('confidence', 0.5)) / 2

    # Save output
    if output_format == 'json':
        filepath = save_as_json(recipe_data, output_dir, image_path)
    else:
        filepath = save_as_markdown(recipe_data, output_dir, image_path)

    console.print(f"[green]✓ Recipe saved to: {filepath}[/green]")
    console.print(f"[dim]Confidence: {recipe_data['confidence']:.2f}[/dim]")


def process_video(url: str, output_dir: str, output_format: str, whisper_model: str = "large"):
    """Process video (YouTube/Facebook)"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Download audio
        audio_path = download_video_audio(url, temp_dir)

        # Transcribe (skip Sarvam, use Whisper directly if large model requested)
        if whisper_model != "base":
            console.print(f"[cyan]Using Whisper {whisper_model} (skipping Sarvam AI)[/cyan]")
            raw_text = transcribe_audio_whisper(audio_path, model_size=whisper_model)
        else:
            raw_text = transcribe_audio(audio_path)

        console.print(f"\n[dim]Transcribed text:[/dim]")
        console.print(f"[dim]{raw_text[:500]}...[/dim]\n")

        # Format
        recipe_data = format_with_gemini(raw_text)

        if recipe_data.get('is_recipe') == False:
            console.print(f"[yellow]Not a recipe: {recipe_data.get('reason')}[/yellow]")
            return

        # Save
        if output_format == 'json':
            filepath = save_as_json(recipe_data, output_dir, url)
        else:
            filepath = save_as_markdown(recipe_data, output_dir, url)

        console.print(f"[green]✓ Recipe saved to: {filepath}[/green]")


def main():
    parser = argparse.ArgumentParser(
        description="Extract recipes from various sources (v2 - Gemini-powered)"
    )

    parser.add_argument("source", help="URL or file path (image/PDF)")
    parser.add_argument("--output", "-o", default="recipes/", help="Output directory")
    parser.add_argument("--format", "-f", choices=['md', 'json'], default='md', help="Output format (default: md)")
    parser.add_argument("--whisper-model", "-w", choices=['tiny', 'base', 'small', 'medium', 'large'],
                       default='large', help="Whisper model size (default: large, best for Telugu)")

    args = parser.parse_args()

    console.print(Panel.fit(
        "[bold magenta]Recipe Extractor v2[/bold magenta]\n"
        "[dim]Powered by Gemini Vision & AI[/dim]",
        border_style="magenta"
    ))

    # Detect source type
    if args.source.startswith('http'):
        # Video URL
        process_video(args.source, args.output, args.format, args.whisper_model)
    elif os.path.isfile(args.source):
        # Image file
        process_image(args.source, args.output, args.format)
    else:
        console.print(f"[red]Error: File not found: {args.source}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
