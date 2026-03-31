"""
Generate audio narration for a bedtime story using ElevenLabs TTS.

Usage:
    python scripts/narrate.py <story-name> [--voice VOICE_ID] [--list-voices]

Examples:
    python scripts/narrate.py the-dragon-who-loved-jigsaw-puzzles
    python scripts/narrate.py the-quilt-that-wouldnt-stay-still --voice jv41DhCf464zw0TI7I1w
    python scripts/narrate.py --list-voices
"""

import os
import re
import sys
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

API_KEY = os.getenv("ELEVENLABS_API_KEY")
STORIES_DIR = PROJECT_ROOT / "stories"

# Default voice: Imogen (warm British storyteller)
DEFAULT_VOICE_ID = "jv41DhCf464zw0TI7I1w"

# ElevenLabs max chars per request
MAX_CHUNK_CHARS = 5000

# Voice settings tuned for bedtime narration
VOICE_SETTINGS = {
    "stability": 0.65,        # slightly more expressive than default
    "similarity_boost": 0.75,
    "style": 0.3,             # gentle storytelling style
    "speed": 0.85,            # unhurried bedtime pace
    "use_speaker_boost": True,
}


def list_voices():
    """List available voices from your ElevenLabs account."""
    r = requests.get(
        "https://api.elevenlabs.io/v1/voices",
        headers={"xi-api-key": API_KEY},
    )
    if r.status_code != 200:
        print(f"Error listing voices: {r.status_code} — {r.text[:200]}")
        return

    voices = r.json().get("voices", [])
    if not voices:
        print("No voices found in your account.")
        return

    print(f"\n{'Name':<20} {'Voice ID':<25} {'Labels'}")
    print("-" * 70)
    for v in voices:
        labels = v.get("labels", {})
        info = ", ".join(f"{k}: {val}" for k, val in labels.items() if val)
        print(f"{v['name']:<20} {v['voice_id']:<25} {info}")
    print()


def extract_story_text(draft_path):
    """Read a draft.md file and extract just the story text (no frontmatter).

    Prepends the story title so the narration announces the name before starting.
    """
    text = draft_path.read_text(encoding="utf-8")

    # Extract title from the first markdown heading
    title_match = re.search(r"^#\s+(?:Story:\s*)?(.+)$", text, flags=re.MULTILINE)
    title = title_match.group(1).strip() if title_match else None

    # Remove header block (title, metadata, and the --- separator)
    # The story text starts after the FIRST --- separator; any later ---
    # are scene breaks within the story and must be preserved.
    first_sep = text.find("\n---\n")
    if first_sep != -1:
        story_text = text[first_sep + 5:]  # skip past "\n---\n"
    else:
        # No separator, just use everything after the first blank line
        story_text = text.strip()

    # Remove any markdown headers that aren't part of the story
    story_text = re.sub(r"^#{1,3}\s+.*$", "", story_text, flags=re.MULTILINE)

    # Replace --- scene breaks with paragraph pauses (not read aloud)
    story_text = re.sub(r"^\s*---\s*$", "", story_text, flags=re.MULTILINE)

    # Clean up markdown formatting
    story_text = re.sub(r"\*\*([^*]+)\*\*", r"\1", story_text)  # remove bold
    story_text = re.sub(r"\*([^*]+)\*", r"\1", story_text)  # remove italics

    # Collapse multiple blank lines
    story_text = re.sub(r"\n{3,}", "\n\n", story_text)

    story_text = story_text.strip()

    # Prepend title so the narration announces the story name
    if title:
        story_text = f"{title}.\n\n{story_text}"

    return story_text


def chunk_text(text, max_chars=MAX_CHUNK_CHARS):
    """Split text into chunks at paragraph boundaries, respecting max size."""
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If adding this paragraph would exceed the limit, save current chunk
        if current_chunk and len(current_chunk) + len(para) + 2 > max_chars:
            chunks.append(current_chunk.strip())
            current_chunk = ""

        # If a single paragraph exceeds max, split on sentences
        if len(para) > max_chars:
            sentences = re.split(r"(?<=[.!?])\s+", para)
            for sentence in sentences:
                if len(current_chunk) + len(sentence) + 1 > max_chars:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    current_chunk += " " + sentence if current_chunk else sentence
        else:
            current_chunk += "\n\n" + para if current_chunk else para

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def generate_audio(text, voice_id, previous_text=None, next_text=None):
    """Send text to ElevenLabs and return audio bytes."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    payload = {
        "text": text,
        "model_id": "eleven_flash_v2_5",
        "voice_settings": VOICE_SETTINGS,
    }
    if previous_text:
        payload["previous_text"] = previous_text
    if next_text:
        payload["next_text"] = next_text

    r = requests.post(
        url,
        headers={"xi-api-key": API_KEY, "Content-Type": "application/json"},
        json=payload,
    )

    if r.status_code != 200:
        raise RuntimeError(f"ElevenLabs API error {r.status_code}: {r.text[:300]}")

    return r.content


def narrate_story(story_name, voice_id=DEFAULT_VOICE_ID):
    """Generate narration for a story and save as MP3."""
    story_dir = STORIES_DIR / story_name
    draft_path = story_dir / "draft.md"

    if not draft_path.exists():
        print(f"Error: No draft found at {draft_path}")
        sys.exit(1)

    print(f"Reading: {draft_path}")
    story_text = extract_story_text(draft_path)
    total_chars = len(story_text)
    print(f"Story length: {total_chars:,} characters")

    # Chunk the text
    chunks = chunk_text(story_text)
    print(f"Split into {len(chunks)} chunk(s)")

    # Generate audio for each chunk, passing adjacent text for continuity
    audio_parts = []
    for i, chunk in enumerate(chunks):
        prev_text = chunks[i - 1][-300:] if i > 0 else None
        next_text = chunks[i + 1][:300] if i < len(chunks) - 1 else None
        print(f"  Generating chunk {i + 1}/{len(chunks)} ({len(chunk):,} chars)...", end=" ", flush=True)
        audio = generate_audio(chunk, voice_id, previous_text=prev_text, next_text=next_text)
        audio_parts.append(audio)
        print(f"done ({len(audio):,} bytes)")

    # Combine audio chunks
    output_path = story_dir / "narration.mp3"
    with open(output_path, "wb") as f:
        for part in audio_parts:
            f.write(part)

    total_bytes = sum(len(p) for p in audio_parts)
    print(f"\nSaved: {output_path}")
    print(f"Total size: {total_bytes:,} bytes ({total_bytes / 1024:.0f} KB)")
    print(f"Characters used: {total_chars:,}")

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate audio narration for bedtime stories")
    parser.add_argument("story", nargs="?", help="Story folder name (e.g., the-dragon-who-loved-jigsaw-puzzles)")
    parser.add_argument("--voice", default=DEFAULT_VOICE_ID, help="ElevenLabs voice ID")
    parser.add_argument("--list-voices", action="store_true", help="List available voices")
    args = parser.parse_args()

    if not API_KEY:
        print("Error: ELEVENLABS_API_KEY not found. Add it to .env in the project root.")
        sys.exit(1)

    if args.list_voices:
        list_voices()
        return

    if not args.story:
        # List available stories
        stories = sorted(d.name for d in STORIES_DIR.iterdir() if d.is_dir() and (d / "draft.md").exists())
        print("Available stories:")
        for s in stories:
            has_audio = "  [has audio]" if (STORIES_DIR / s / "narration.mp3").exists() else ""
            print(f"  {s}{has_audio}")
        print(f"\nUsage: python scripts/narrate.py <story-name>")
        return

    narrate_story(args.story, args.voice)


if __name__ == "__main__":
    main()
