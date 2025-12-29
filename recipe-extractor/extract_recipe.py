#!/usr/bin/env python3
"""
Recipe Extractor CLI
Extracts recipes from YouTube, Instagram, Facebook, images, and PDFs.
Formats them into standardized Markdown using Gemini AI.

Usage:
    python extract_recipe.py <url_or_file_path> --output recipes/
"""

import argparse
import os
import sys
import re
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Load environment variables
load_dotenv()

console = Console()

# Gemini system prompt for recipe formatting
GEMINI_SYSTEM_PROMPT = """You are a recipe formatter. Given raw text from a cooking video/image/document, extract and format it into a clean, standardized recipe in Markdown format with these sections:
- Title
- Description (1-2 sentences)
- Prep Time / Cook Time / Servings
- Ingredients (bulleted list with quantities)
- Instructions (numbered steps)
- Tips (optional)

Only include factual recipe information. If the content is not a recipe, respond with 'NOT_A_RECIPE'.

Important: If the text is in a regional language (Telugu, Hindi, Tamil, etc.), translate to English while keeping any dish names in their original form."""


def is_url(source: str) -> bool:
    """Check if the source is a URL."""
    try:
        result = urlparse(source)
        return all([result.scheme, result.netloc])
    except:
        return False


def detect_source_type(source: str) -> str:
    """Detect the type of source (youtube, instagram, facebook, image, pdf, file)."""
    if is_url(source):
        domain = urlparse(source).netloc.lower()
        if 'youtube.com' in domain or 'youtu.be' in domain:
            return 'youtube'
        elif 'instagram.com' in domain:
            return 'instagram'
        elif 'facebook.com' in domain or 'fb.watch' in domain:
            return 'facebook'
        else:
            return 'url'
    else:
        # It's a file path
        ext = Path(source).suffix.lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.heic']:
            return 'image'
        elif ext == '.pdf':
            return 'pdf'
        else:
            return 'file'


def download_video(url: str, output_dir: str) -> str:
    """Download video using yt-dlp and extract audio."""
    console.print("[yellow]Downloading video...[/yellow]")

    audio_path = os.path.join(output_dir, "audio.mp3")

    cmd = [
        "yt-dlp",
        "-x",  # Extract audio
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "-o", audio_path.replace(".mp3", ".%(ext)s"),
        url
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        # Find the downloaded file (yt-dlp might add extension)
        for f in os.listdir(output_dir):
            if f.startswith("audio") and f.endswith(".mp3"):
                return os.path.join(output_dir, f)
        return audio_path
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error downloading video: {e.stderr.decode()}[/red]")
        raise


def download_instagram(url: str, output_dir: str) -> tuple:
    """Download Instagram content using instaloader."""
    console.print("[yellow]Downloading Instagram content...[/yellow]")

    import instaloader

    L = instaloader.Instaloader(
        download_videos=True,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        dirname_pattern=output_dir
    )

    # Extract shortcode from URL
    match = re.search(r'/(?:p|reel)/([A-Za-z0-9_-]+)', url)
    if not match:
        raise ValueError("Could not extract Instagram post ID from URL")

    shortcode = match.group(1)

    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target=output_dir)

        # Find downloaded files
        video_file = None
        image_file = None
        caption = post.caption or ""

        for f in os.listdir(output_dir):
            if f.endswith('.mp4'):
                video_file = os.path.join(output_dir, f)
            elif f.endswith(('.jpg', '.png')):
                image_file = os.path.join(output_dir, f)

        return video_file, image_file, caption
    except Exception as e:
        console.print(f"[red]Error downloading Instagram: {e}[/red]")
        raise


def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio using OpenAI Whisper."""
    console.print("[yellow]Transcribing audio with Whisper...[/yellow]")

    import whisper

    model = whisper.load_model("base")  # Can use "small", "medium", "large" for better accuracy
    result = model.transcribe(audio_path)

    return result["text"]


def extract_text_from_image(image_path: str) -> str:
    """Extract text from image using pytesseract OCR."""
    console.print("[yellow]Extracting text from image...[/yellow]")

    import pytesseract
    from PIL import Image

    # Open and preprocess image
    img = Image.open(image_path)

    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Use multiple language hints for better handwritten text recognition
    # tel = Telugu, eng = English, hin = Hindi
    try:
        text = pytesseract.image_to_string(img, lang='eng+tel+hin')
    except pytesseract.TesseractError:
        # Fallback to English only
        text = pytesseract.image_to_string(img, lang='eng')

    return text


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using PyMuPDF."""
    console.print("[yellow]Extracting text from PDF...[/yellow]")

    import fitz  # PyMuPDF

    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        text += page.get_text()

    doc.close()
    return text


def format_with_gemini(raw_text: str) -> str:
    """Format extracted text into recipe Markdown using Gemini."""
    console.print("[yellow]Formatting with Gemini AI...[/yellow]")

    import google.generativeai as genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"{GEMINI_SYSTEM_PROMPT}\n\n---\n\nRaw text to format:\n\n{raw_text}"

    response = model.generate_content(prompt)
    return response.text


def save_recipe(content: str, output_dir: str, source: str) -> str:
    """Save the formatted recipe to a Markdown file."""
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Generate filename from title or timestamp
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        filename = re.sub(r'[^\w\s-]', '', title_match.group(1))
        filename = re.sub(r'\s+', '_', filename).strip()[:50]
    else:
        filename = f"recipe_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    filepath = os.path.join(output_dir, f"{filename}.md")

    # Add source metadata
    metadata = f"---\nsource: {source}\nextracted: {datetime.now().isoformat()}\n---\n\n"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(metadata + content)

    return filepath


def process_source(source: str, output_dir: str) -> None:
    """Main processing pipeline."""
    source_type = detect_source_type(source)
    console.print(f"[cyan]Detected source type: {source_type}[/cyan]")

    raw_text = ""

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            if source_type in ['youtube', 'facebook']:
                # Download video and transcribe
                audio_path = download_video(source, temp_dir)
                raw_text = transcribe_audio(audio_path)

            elif source_type == 'instagram':
                # Download Instagram content
                video_file, image_file, caption = download_instagram(source, temp_dir)

                if video_file:
                    # Extract audio from video and transcribe
                    audio_path = os.path.join(temp_dir, "audio.mp3")
                    subprocess.run([
                        "ffmpeg", "-i", video_file,
                        "-vn", "-acodec", "mp3",
                        audio_path
                    ], check=True, capture_output=True)
                    raw_text = transcribe_audio(audio_path)
                elif image_file:
                    raw_text = extract_text_from_image(image_file)

                # Add caption to raw text
                if caption:
                    raw_text = f"Caption: {caption}\n\n{raw_text}"

            elif source_type == 'image':
                raw_text = extract_text_from_image(source)

            elif source_type == 'pdf':
                raw_text = extract_text_from_pdf(source)

            else:
                console.print(f"[red]Unsupported source type: {source_type}[/red]")
                sys.exit(1)

        except Exception as e:
            console.print(f"[red]Error processing source: {e}[/red]")
            sys.exit(1)

    if not raw_text.strip():
        console.print("[red]No text could be extracted from the source.[/red]")
        sys.exit(1)

    console.print("\n[dim]--- Extracted Text (preview) ---[/dim]")
    console.print(f"[dim]{raw_text[:500]}...[/dim]\n" if len(raw_text) > 500 else f"[dim]{raw_text}[/dim]\n")

    # Format with Gemini
    try:
        formatted_recipe = format_with_gemini(raw_text)
    except Exception as e:
        console.print(f"[red]Error formatting with Gemini: {e}[/red]")
        sys.exit(1)

    # Check if it's actually a recipe
    if "NOT_A_RECIPE" in formatted_recipe:
        console.print("[yellow]The content does not appear to be a recipe.[/yellow]")
        sys.exit(0)

    # Save the recipe
    filepath = save_recipe(formatted_recipe, output_dir, source)

    # Display the result
    console.print(Panel(Markdown(formatted_recipe), title="[green]Extracted Recipe[/green]", border_style="green"))
    console.print(f"\n[green]Recipe saved to: {filepath}[/green]")


def main():
    parser = argparse.ArgumentParser(
        description="Extract recipes from various sources and format to Markdown.",
        epilog="Examples:\n"
               "  python extract_recipe.py https://youtube.com/watch?v=xxx\n"
               "  python extract_recipe.py recipe_photo.jpg --output my_recipes/\n"
               "  python extract_recipe.py cookbook.pdf",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "source",
        help="URL (YouTube/Instagram/Facebook) or file path (image/PDF)"
    )

    parser.add_argument(
        "--output", "-o",
        default="recipes/",
        help="Output directory for saved recipes (default: recipes/)"
    )

    args = parser.parse_args()

    console.print(Panel.fit(
        "[bold magenta]Recipe Extractor[/bold magenta]\n"
        "[dim]Extracting recipes from videos, images, and documents[/dim]",
        border_style="magenta"
    ))

    # Validate source
    if not is_url(args.source) and not os.path.exists(args.source):
        console.print(f"[red]Error: Source file not found: {args.source}[/red]")
        sys.exit(1)

    process_source(args.source, args.output)


if __name__ == "__main__":
    main()
