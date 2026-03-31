"""
Generate audio narration for a bedtime story using one or more TTS providers.

Usage:
    python scripts/narrate.py <story-name> [--provider PROVIDER] [--voice VOICE_ID]
    python scripts/narrate.py <story-name> --provider polly --fallback-voice Amy
    python scripts/narrate.py --list-voices [--provider PROVIDER]

Examples:
    python scripts/narrate.py the-dragon-who-loved-jigsaw-puzzles
    python scripts/narrate.py the-quilt-that-wouldnt-stay-still --provider elevenlabs --voice jv41DhCf464zw0TI7I1w
    python scripts/narrate.py the-lantern-trail --provider polly --fallback-voice Amy
    python scripts/narrate.py --list-voices --provider elevenlabs
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
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

# Default voice: Imogen (warm British storyteller)
DEFAULT_VOICE_ID = "jv41DhCf464zw0TI7I1w"
DEFAULT_PROVIDER = "auto"
DEFAULT_FALLBACK_PROVIDER = "polly"
DEFAULT_POLLY_VOICE = "Amy"

# Provider chunk limits
MAX_CHUNK_CHARS_ELEVENLABS = 5000
# AWS Polly SynthesizeSpeech allows up to 6000 total characters,
# with no more than 3000 billed characters. Use a conservative cap.
MAX_CHUNK_CHARS_POLLY = 2800

# Voice settings tuned for bedtime narration
VOICE_SETTINGS = {
    "stability": 0.65,        # slightly more expressive than default
    "similarity_boost": 0.75,
    "style": 0.3,             # gentle storytelling style
    "speed": 0.85,            # unhurried bedtime pace
    "use_speaker_boost": True,
}


class TTSProviderError(RuntimeError):
    """Provider failure with enough detail to decide whether failover is safe."""

    def __init__(self, provider, message, *, should_failover=False):
        super().__init__(message)
        self.provider = provider
        self.should_failover = should_failover


def require_boto3():
    """Import boto3 lazily so ElevenLabs-only usage does not require it."""
    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError
    except ImportError as exc:
        raise RuntimeError(
            "AWS Polly support requires boto3. Install it with: pip install boto3"
        ) from exc

    return boto3, BotoCoreError, ClientError


def list_elevenlabs_voices():
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


def list_polly_voices(region_name=AWS_REGION):
    """List a bedtime-friendly subset of Polly voices."""
    boto3, BotoCoreError, ClientError = require_boto3()

    try:
        client = boto3.client("polly", region_name=region_name)
        paginator = client.get_paginator("describe_voices")
        voices = []
        for page in paginator.paginate(Engine="standard", LanguageCode="en-GB"):
            voices.extend(page.get("Voices", []))
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(f"Error listing Polly voices: {exc}") from exc

    if not voices:
        print("No Polly voices found.")
        return

    print(f"\n{'Name':<20} {'Voice ID':<20} {'Language':<10} {'Gender'}")
    print("-" * 70)
    for voice in voices:
        print(
            f"{voice['Name']:<20} {voice['Id']:<20} "
            f"{voice['LanguageCode']:<10} {voice.get('Gender', '')}"
        )
    print()


def list_voices(provider, region_name=AWS_REGION):
    """List available voices for the selected provider."""
    if provider == "elevenlabs":
        if not API_KEY:
            print("Error: ELEVENLABS_API_KEY not found. Add it to .env in the project root.")
            return
        list_elevenlabs_voices()
        return

    if provider == "polly":
        list_polly_voices(region_name=region_name)
        return

    # Auto mode is ambiguous here; print both when possible.
    print("ElevenLabs voices:")
    if API_KEY:
        list_elevenlabs_voices()
    else:
        print("  Skipped: ELEVENLABS_API_KEY not configured.\n")

    print("AWS Polly voices:")
    try:
        list_polly_voices(region_name=region_name)
    except RuntimeError as exc:
        print(f"  Skipped: {exc}\n")


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


def chunk_text(text, max_chars):
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


def get_chunk_limit(provider):
    """Return a chunk size safe for the provider path in use."""
    if provider in {"auto", "polly"}:
        return MAX_CHUNK_CHARS_POLLY
    return MAX_CHUNK_CHARS_ELEVENLABS


def is_elevenlabs_failover_error(status_code, text):
    """Return True only for errors where switching providers is appropriate."""
    body = (text or "").lower()
    failover_terms = (
        "quota",
        "credit",
        "usage limit",
        "rate limit",
        "too many requests",
        "insufficient balance",
    )
    return status_code in {402, 429} or any(term in body for term in failover_terms)


def generate_audio_elevenlabs(text, voice_id, previous_text=None, next_text=None):
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
        raise TTSProviderError(
            "elevenlabs",
            f"ElevenLabs API error {r.status_code}: {r.text[:300]}",
            should_failover=is_elevenlabs_failover_error(r.status_code, r.text),
        )

    return r.content


def generate_audio_polly(text, voice_id, region_name=AWS_REGION):
    """Send text to AWS Polly and return audio bytes."""
    boto3, BotoCoreError, ClientError = require_boto3()

    try:
        client = boto3.client("polly", region_name=region_name)
        response = client.synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            VoiceId=voice_id,
            Engine="standard",
            TextType="text",
        )
        return response["AudioStream"].read()
    except (BotoCoreError, ClientError) as exc:
        raise TTSProviderError("polly", f"AWS Polly error: {exc}") from exc


def validate_provider_config(provider, fallback_provider):
    """Fail early for missing primary credentials, but allow auto fallback."""
    if provider == "elevenlabs" and not API_KEY:
        print("Error: ELEVENLABS_API_KEY not found. Add it to .env in the project root.")
        sys.exit(1)

    if provider == "auto" and fallback_provider != "polly":
        print(f"Error: Unsupported fallback provider: {fallback_provider}")
        sys.exit(1)


def narrate_story(
    story_name,
    *,
    provider=DEFAULT_PROVIDER,
    voice_id=DEFAULT_VOICE_ID,
    fallback_provider=DEFAULT_FALLBACK_PROVIDER,
    fallback_voice=DEFAULT_POLLY_VOICE,
    region_name=AWS_REGION,
):
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
    chunks = chunk_text(story_text, max_chars=get_chunk_limit(provider))
    print(f"Split into {len(chunks)} chunk(s)")

    # Generate audio for each chunk, passing adjacent text for continuity.
    audio_parts = []
    providers_used = []
    failover_provider_active = None
    for i, chunk in enumerate(chunks):
        active_provider = failover_provider_active or provider
        prev_text = chunks[i - 1][-300:] if i > 0 else None
        next_text = chunks[i + 1][:300] if i < len(chunks) - 1 else None
        print(
            f"  Generating chunk {i + 1}/{len(chunks)} ({len(chunk):,} chars)...",
            end=" ",
            flush=True,
        )

        try:
            if active_provider in {"auto", "elevenlabs"}:
                if not API_KEY:
                    if active_provider == "elevenlabs":
                        raise TTSProviderError(
                            "elevenlabs",
                            "ELEVENLABS_API_KEY not found. Add it to .env in the project root.",
                        )
                    raise TTSProviderError(
                        "elevenlabs",
                        "ELEVENLABS_API_KEY not found for primary provider.",
                        should_failover=True,
                    )

                audio = generate_audio_elevenlabs(
                    chunk,
                    voice_id,
                    previous_text=prev_text,
                    next_text=next_text,
                )
                providers_used.append("elevenlabs")
                audio_parts.append(audio)
                print(f"done via elevenlabs ({len(audio):,} bytes)")
                continue

            audio = generate_audio_polly(chunk, fallback_voice, region_name=region_name)
            providers_used.append("polly")
            audio_parts.append(audio)
            print(f"done via polly ({len(audio):,} bytes)")
        except TTSProviderError as exc:
            if provider == "auto" and exc.provider == "elevenlabs" and exc.should_failover:
                failover_provider_active = fallback_provider
                print("primary limit reached; falling back to polly...", end=" ", flush=True)
                audio = generate_audio_polly(chunk, fallback_voice, region_name=region_name)
                providers_used.append("polly")
                audio_parts.append(audio)
                print(f"done ({len(audio):,} bytes)")
                continue
            raise

    # Combine audio chunks
    output_path = story_dir / "narration.mp3"
    with open(output_path, "wb") as f:
        for part in audio_parts:
            f.write(part)

    total_bytes = sum(len(p) for p in audio_parts)
    print(f"\nSaved: {output_path}")
    print(f"Total size: {total_bytes:,} bytes ({total_bytes / 1024:.0f} KB)")
    print(f"Characters used: {total_chars:,}")
    if providers_used:
        unique_providers = list(dict.fromkeys(providers_used))
        print(f"Providers used: {', '.join(unique_providers)}")
        if len(set(providers_used)) > 1:
            print("Warning: narration mixed multiple providers, so the voice may shift between chunks.")

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate audio narration for bedtime stories")
    parser.add_argument("story", nargs="?", help="Story folder name (e.g., the-dragon-who-loved-jigsaw-puzzles)")
    parser.add_argument(
        "--provider",
        choices=["auto", "elevenlabs", "polly"],
        default=DEFAULT_PROVIDER,
        help="TTS provider to use. 'auto' tries ElevenLabs first, then Polly on provider-limit errors.",
    )
    parser.add_argument("--voice", default=DEFAULT_VOICE_ID, help="ElevenLabs voice ID")
    parser.add_argument(
        "--fallback-provider",
        choices=["polly"],
        default=DEFAULT_FALLBACK_PROVIDER,
        help="Backup provider used when --provider auto fails over.",
    )
    parser.add_argument(
        "--fallback-voice",
        default=DEFAULT_POLLY_VOICE,
        help="AWS Polly voice ID used for Polly narration or auto fallback.",
    )
    parser.add_argument(
        "--region",
        default=AWS_REGION,
        help="AWS region for Polly requests (default: AWS_DEFAULT_REGION or us-east-1).",
    )
    parser.add_argument("--list-voices", action="store_true", help="List available voices")
    args = parser.parse_args()

    validate_provider_config(args.provider, args.fallback_provider)

    if args.list_voices:
        list_voices(args.provider, region_name=args.region)
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

    narrate_story(
        args.story,
        provider=args.provider,
        voice_id=args.voice,
        fallback_provider=args.fallback_provider,
        fallback_voice=args.fallback_voice,
        region_name=args.region,
    )


if __name__ == "__main__":
    main()
