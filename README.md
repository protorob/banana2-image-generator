# pynanoban

Generate product label images from a text prompt and optional style reference images, powered by Google Gemini.

## What it does

`banana.py` takes a text prompt describing a label design, optionally reads style reference images from a `reference/` folder, sends everything to the Gemini image generation API, and saves the results to `generated/`.

Useful for rapid brainstorming of label concepts and for style-transfer generation once you have a reference image you like.

## Setup

**1. Install dependencies**
```bash
python -m venv venv
source venv/bin/activate
pip install google-genai python-dotenv
```

**2. Add your Gemini API key**
```bash
cp .env.example .env
# edit .env and set your key:
# GEMINI_API_KEY=your_key_here
```

## Usage

```bash
source venv/bin/activate

# Use prompt.txt (recommended)
python banana.py

# Inline prompt
python banana.py "A minimal modern label for a spritz aperitivo"

# Generate multiple variations at once
python banana.py --count 6

# Skip reference images even if reference/ is not empty
python banana.py --no-reference --count 4

# All flags combined
python banana.py "Rustic honey jar label" --count 3 --no-reference
```

## Prompt

Edit `prompt.txt` to set your active prompt. It is picked up automatically on every run.

```
A clean, minimal modern product label for a spritz aperitivo bottle...
```

Alternatively pass the prompt directly as a CLI argument — it takes priority over `prompt.txt`.

## Reference images

Drop `.png`, `.jpg`, or `.webp` images into `reference/` to guide the style of the output. The model will use them as visual context alongside your prompt.

Leave `reference/` empty (or use `--no-reference`) to generate freely from the prompt alone.

## Output

Generated images are saved to `generated/` with timestamped filenames:
```
generated/label_20260304_143012_0.png
generated/label_20260304_143015_0.png
```

## Brainstorming workflow

1. Start with `--no-reference --count 6` to explore directions freely
2. Pick the best result and copy it into `reference/`
3. Re-run without `--no-reference` to generate variations in that style
4. Iterate until you have a direction worth developing further

## Project structure

```
pynanoban/
├── banana.py        # main script
├── prompt.txt       # active prompt
├── reference/       # style reference images (optional)
├── generated/       # output images
├── .env             # API key (do not commit)
└── .env.example     # safe template
```
