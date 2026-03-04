# pynanoban — Claude Code context

## What this project does
Generates product label images using the Google Gemini image generation API (`gemini-2.5-flash-image`).
The main script is `banana.py`. It optionally takes style reference images from `reference/` and a text prompt, then saves generated images to `generated/`.

## Stack
- Python 3.12
- `google-genai` (new SDK — **not** `google-generativeai`, that one is deprecated)
- `python-dotenv` for API key loading
- Virtual environment at `venv/`

## Running the script
```bash
source venv/bin/activate
python banana.py
```

## Key files
- `banana.py` — main script
- `prompt.txt` — active prompt, read automatically if no CLI prompt is given
- `reference/` — optional style reference images (.png, .jpg, .webp, .gif)
- `generated/` — output images, named `label_YYYYMMDD_HHMMSS_N.png`
- `.env` — contains `GEMINI_API_KEY` (never commit this)
- `.env.example` — safe template to commit

## CLI flags
| Flag | Default | Description |
|---|---|---|
| `prompt` (positional) | — | Inline prompt string |
| `--count N` | 1 | Number of images to generate |
| `--no-reference` | false | Ignore reference/ images even if present |

## Prompt priority
1. CLI positional argument
2. `prompt.txt`
3. Interactive input → falls back to built-in default

## API notes
- Model: `gemini-2.5-flash-image`
- File upload uses `client.files.upload(file=path)` — parameter is `file`, not `path`
- Generation config uses `types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"])`
- Reference images are passed as `types.Part.from_uri(file_uri=f.uri, mime_type=f.mime_type)`

## Workflow tip
Run `--no-reference --count 6` to brainstorm freely from prompt only.
Once a generated image looks right, drop it into `reference/` and re-run to steer toward that style.
