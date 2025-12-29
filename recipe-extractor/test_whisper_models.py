#!/usr/bin/env python3
"""
Test Whisper Model Performance & Cost

Compares tiny, base, small, medium, large models on:
- Speed (transcription time)
- Quality (transcription accuracy for Telugu)
- Cost (electricity + API calls)
"""

import time
import os
from dotenv import load_dotenv
from extract_recipe_v2 import download_video_audio, transcribe_audio_whisper, format_with_gemini
import tempfile
import json
from rich.console import Console
from rich.table import Table

load_dotenv()
console = Console()

# Test video: Palak Paneer by Vismai Food (Telugu)
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=cjGDsV6FvNE"

# Cost constants (per minute of GPU/CPU time)
ELECTRICITY_COST_PER_MINUTE = 0.05 / 60  # ₹0.05 per recipe / 60 min
GEMINI_COST_PER_CALL = 0.0084  # ₹0.0084 per call


def test_model(model_name: str, audio_path: str):
    """Test a single Whisper model"""
    console.print(f"\n[bold cyan]Testing Whisper {model_name}...[/bold cyan]")

    start_time = time.time()
    transcript = transcribe_audio_whisper(audio_path, model_size=model_name)
    transcription_time = time.time() - start_time

    # Check if Telugu was transcribed
    has_telugu = any(ord(c) >= 0x0C00 and ord(c) <= 0x0C7F for c in transcript)

    # Format with Gemini
    start_format = time.time()
    recipe_data = format_with_gemini(transcript)
    format_time = time.time() - start_format

    total_time = transcription_time + format_time

    # Calculate costs
    electricity_cost = transcription_time * ELECTRICITY_COST_PER_MINUTE
    gemini_cost = GEMINI_COST_PER_CALL
    total_cost = electricity_cost + gemini_cost

    return {
        "model": model_name,
        "transcription_time": transcription_time,
        "format_time": format_time,
        "total_time": total_time,
        "has_telugu": has_telugu,
        "transcript_length": len(transcript),
        "confidence": recipe_data.get("confidence", 0.0),
        "ingredients_count": len(recipe_data.get("ingredients", [])),
        "electricity_cost": electricity_cost,
        "gemini_cost": gemini_cost,
        "total_cost": total_cost,
        "recipe_name": recipe_data.get("name", "Unknown"),
    }


def main():
    console.print("[bold magenta]Whisper Model Comparison Test[/bold magenta]\n")

    # Download video audio once
    console.print("[yellow]Downloading test video...[/yellow]")
    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = download_video_audio(TEST_VIDEO_URL, temp_dir)

        # Test models
        models_to_test = ["tiny", "base", "small", "medium", "large"]
        results = []

        for model in models_to_test:
            try:
                result = test_model(model, audio_path)
                results.append(result)
            except Exception as e:
                console.print(f"[red]Error testing {model}: {e}[/red]")

    # Display results
    table = Table(title="Whisper Model Performance Comparison")
    table.add_column("Model", style="cyan")
    table.add_column("Transcription Time", style="green")
    table.add_column("Total Time", style="green")
    table.add_column("Telugu?", style="yellow")
    table.add_column("Confidence", style="magenta")
    table.add_column("Ingredients", style="blue")
    table.add_column("Total Cost (₹)", style="red")

    for r in results:
        table.add_row(
            r["model"],
            f"{r['transcription_time']:.1f}s",
            f"{r['total_time']:.1f}s",
            "✓" if r["has_telugu"] else "✗",
            f"{r['confidence']:.2f}",
            str(r["ingredients_count"]),
            f"₹{r['total_cost']:.4f}",
        )

    console.print(table)

    # Summary
    console.print("\n[bold]Summary:[/bold]")
    best_quality = max(results, key=lambda x: x["confidence"])
    fastest = min(results, key=lambda x: x["total_time"])
    cheapest = min(results, key=lambda x: x["total_cost"])

    console.print(f"[green]Best Quality:[/green] {best_quality['model']} (confidence: {best_quality['confidence']:.2f})")
    console.print(f"[green]Fastest:[/green] {fastest['model']} ({fastest['total_time']:.1f}s)")
    console.print(f"[green]Cheapest:[/green] {cheapest['model']} (₹{cheapest['total_cost']:.4f})")

    console.print(f"\n[bold]Recommendation for MSI CUDA Machine:[/bold]")
    console.print(f"Use [cyan]large[/cyan] model for best Telugu quality")
    console.print(f"Expected speed on RTX 5080: ~10-15s (vs {best_quality['transcription_time']:.1f}s on CPU)")
    console.print(f"Cost per recipe: ₹{best_quality['total_cost']:.4f}")

    # Save results
    with open("model_comparison_results.json", "w") as f:
        json.dump(results, f, indent=2)

    console.print("\n[dim]Results saved to: model_comparison_results.json[/dim]")


if __name__ == "__main__":
    main()
