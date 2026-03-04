import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}
REFERENCE_DIR = Path('reference')
GENERATED_DIR = Path('generated')

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    sys.exit("Error: GEMINI_API_KEY not found.\n"
             "  Add it to a .env file: GEMINI_API_KEY=your_key_here")

client = genai.Client(api_key=api_key)

MODEL_ID = "gemini-2.5-flash-image"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_reference_images() -> list[Path]:
    """Return all image files found in the reference/ directory, or [] if none."""
    if not REFERENCE_DIR.exists() or not any(REFERENCE_DIR.iterdir()):
        return []

    return sorted(
        f for f in REFERENCE_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    )


def upload_images(image_paths: list[Path]) -> list:
    """Upload images to the Gemini File API and return file objects."""
    uploaded = []
    for path in image_paths:
        print(f"  Uploading: {path.name}")
        file_obj = client.files.upload(file=path)
        uploaded.append(file_obj)
    return uploaded


def save_generated_images(response) -> list[Path]:
    """Parse the response and save any image parts to generated/."""
    GENERATED_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved = []

    for i, part in enumerate(response.candidates[0].content.parts):
        if part.inline_data:
            mime = part.inline_data.mime_type
            ext = '.png' if 'png' in mime else '.jpg'
            filepath = GENERATED_DIR / f"label_{timestamp}_{i}{ext}"
            filepath.write_bytes(part.inline_data.data)
            print(f"  Saved: {filepath}")
            saved.append(filepath)
        elif part.text:
            print(f"  Model note: {part.text}")

    return saved


# ---------------------------------------------------------------------------
# Main generation logic
# ---------------------------------------------------------------------------

def generate_labels(prompt: str, count: int = 1) -> list[Path]:
    print("\n--- Loading reference images ---")
    ref_images = load_reference_images()
    if ref_images:
        print(f"Found {len(ref_images)} reference image(s).")
    else:
        print("No reference images found — running from prompt only.")

    # Build contents: optional reference images + text prompt
    contents = []
    if ref_images:
        print("\n--- Uploading to Gemini File API ---")
        uploaded_files = upload_images(ref_images)
        for f in uploaded_files:
            contents.append(types.Part.from_uri(file_uri=f.uri, mime_type=f.mime_type))
    contents.append(prompt)

    print(f"\n--- Generating product labels (count: {count}) ---")
    print(f"Prompt: {prompt}\n")

    all_saved = []
    for i in range(count):
        if count > 1:
            print(f"  Generation {i + 1}/{count}...")
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"]
            ),
        )
        all_saved.extend(save_generated_images(response))

    if all_saved:
        print(f"\nDone! {len(all_saved)} image(s) saved to '{GENERATED_DIR}/'")
    else:
        print("\nNo images were generated. "
              "Try rephrasing your prompt or check the model response.")

    return all_saved


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

DEFAULT_PROMPT = (
    "Using the visual style, color palette, typography, and layout of the "
    "reference images, create a professional product label for a premium "
    "artisan product. The label should be print-ready with clean edges, "
    "suitable for retail packaging."
)


def main():
    parser = argparse.ArgumentParser(
        description="Generate product labels from reference style images using Gemini.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python banana.py
  python banana.py "Create a minimalist olive oil label in the style of the references"
  python banana.py "Honey jar label, rustic feel, warm tones, script font" --count 4
  python banana.py --count 3
        """,
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Prompt describing the label to generate. "
             "If omitted, prompt.txt is used, then interactive input.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        metavar="N",
        help="Number of images to generate (default: 1).",
    )
    args = parser.parse_args()

    prompt_file = Path("prompt.txt")

    if args.prompt:
        prompt = args.prompt
    elif prompt_file.exists():
        prompt = prompt_file.read_text(encoding="utf-8").strip()
        print(f"Using prompt from prompt.txt:\n  {prompt}\n")
    else:
        print("Describe the product label you want to generate.")
        print("(Press Enter to use the default prompt)\n")
        user_input = input("Prompt> ").strip()
        prompt = user_input if user_input else DEFAULT_PROMPT

    generate_labels(prompt, count=args.count)


if __name__ == "__main__":
    main()
