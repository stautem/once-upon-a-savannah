"""
Build the GitHub Pages site from story markdown files.

Usage:
    python scripts/build_site.py

Reads stories from stories/*/draft.md, generates HTML pages in docs/,
and copies any narration.mp3 files alongside them.
"""

import json
import re
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
STORIES_DIR = PROJECT_ROOT / "stories"
TEMPLATES_DIR = PROJECT_ROOT / "site-templates"
DOCS_DIR = PROJECT_ROOT / "docs"
NARRATION_LOG = STORIES_DIR / "narration-log.json"

# Bits per second for each TTS provider's MP3 output. Used to estimate audio
# duration from file size when we don't want to parse the MP3 itself.
PROVIDER_BITRATES = {
    "elevenlabs": 128_000,
    "polly": 48_000,
}
DEFAULT_BITRATE = PROVIDER_BITRATES["elevenlabs"]


def load_duration_lookup():
    """Return a {slug: duration_seconds} map from the narration log.

    The log can have multiple entries per story (re-narrations); use the most
    recent timestamp for each slug.
    """
    if not NARRATION_LOG.exists():
        return {}

    entries = json.loads(NARRATION_LOG.read_text(encoding="utf-8"))
    latest = {}
    for e in entries:
        slug = e.get("story")
        if not slug:
            continue
        prev = latest.get(slug)
        if prev is None or e.get("timestamp", "") > prev.get("timestamp", ""):
            latest[slug] = e

    durations = {}
    for slug, entry in latest.items():
        byte_count = entry.get("bytes")
        if not byte_count:
            continue
        providers = entry.get("providers") or []
        bitrate = PROVIDER_BITRATES.get(providers[0] if providers else "", DEFAULT_BITRATE)
        durations[slug] = round((byte_count * 8) / bitrate)
    return durations


def story_duration(slug, narration_path, duration_lookup):
    """Best-effort duration in seconds for a story's narration."""
    if slug in duration_lookup:
        return duration_lookup[slug]
    # Fallback: estimate from file size assuming the default (ElevenLabs) bitrate.
    print(f" [warn: no narration-log entry, estimating from file size]", end="")
    byte_count = narration_path.stat().st_size
    return round((byte_count * 8) / DEFAULT_BITRATE)


def parse_draft(draft_path):
    """Parse a draft.md file into metadata and story body."""
    text = draft_path.read_text(encoding="utf-8")

    # Extract title from first heading
    title_match = re.search(r"^#\s+(?:Story:\s*)?(.+)$", text, flags=re.MULTILINE)
    title = title_match.group(1).strip() if title_match else draft_path.parent.name

    # Extract metadata fields
    def extract_field(name):
        match = re.search(rf"\*\*{name}:\*\*\s*(.+)$", text, flags=re.MULTILINE)
        return match.group(1).strip() if match else ""

    reading_time = extract_field("Reading time")
    characters = extract_field("Characters")

    # Story body: everything after the first --- line
    # Find the first line that is exactly "---" (the frontmatter separator)
    lines = text.split("\n")
    separator_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "---":
            separator_idx = i
            break

    if separator_idx is not None:
        body = "\n".join(lines[separator_idx + 1:]).strip()
    else:
        body = text.strip()

    # Remove any remaining markdown headers
    body = re.sub(r"^#{1,3}\s+.*$", "", body, flags=re.MULTILINE)

    return {
        "title": title,
        "reading_time": reading_time,
        "characters": characters,
        "body": body,
    }


def markdown_to_html(text):
    """Convert simple story markdown to HTML.

    Handles paragraphs, *italics*, **bold**, and --- horizontal rules.
    No external dependencies needed — the stories are simple prose.
    """
    html_parts = []
    paragraphs = text.strip().split("\n\n")

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # Horizontal rules
        if re.match(r"^-{3,}$", para):
            html_parts.append("<hr>")
            continue

        # Convert markdown formatting
        para = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", para)
        para = re.sub(r"\*(.+?)\*", r"<em>\1</em>", para)

        # Wrap in paragraph tag, preserving single line breaks as <br>
        para = para.replace("\n", "<br>\n")
        html_parts.append(f"<p>{para}</p>")

    return "\n\n".join(html_parts)


def build_story_card(slug, meta, has_audio):
    """Generate an index page story card."""
    audio_badge = '<span class="audio-badge">Has Audio</span>' if has_audio else ""

    # Shorten characters list for the card
    chars = meta["characters"]
    if len(chars) > 60:
        chars = chars[:57] + "..."

    return f"""      <a href="stories/{slug}/" class="story-card">
        <h2>{meta['title']}</h2>
        <p class="meta">{meta['reading_time']} &middot; {chars}</p>
        {audio_badge}
      </a>"""


def build_audio_player():
    """Generate the audio player HTML block."""
    return """      <div class="audio-player">
        <p>Listen to this story:</p>
        <audio controls preload="none">
          <source src="narration.mp3" type="audio/mpeg">
          Your browser does not support the audio element.
        </audio>
      </div>"""


def build_site():
    """Build the complete site."""
    # Load templates
    index_template = (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")
    story_template = (TEMPLATES_DIR / "story.html").read_text(encoding="utf-8")

    # Clean and create docs directory
    if DOCS_DIR.exists():
        shutil.rmtree(DOCS_DIR)
    DOCS_DIR.mkdir()

    # Copy static assets
    shutil.copy2(TEMPLATES_DIR / "style.css", DOCS_DIR / "style.css")
    shutil.copy2(TEMPLATES_DIR / "player.js", DOCS_DIR / "player.js")
    shutil.copy2(TEMPLATES_DIR / "mix.html", DOCS_DIR / "mix.html")

    # Find all stories
    story_dirs = sorted(
        d for d in STORIES_DIR.iterdir()
        if d.is_dir() and (d / "draft.md").exists()
    )

    duration_lookup = load_duration_lookup()
    stories = []

    for story_dir in story_dirs:
        slug = story_dir.name
        draft_path = story_dir / "draft.md"
        narration_path = story_dir / "narration.mp3"
        has_audio = narration_path.exists()

        print(f"  Building: {slug}", end="")

        # Parse the draft
        meta = parse_draft(draft_path)

        # Convert story body to HTML
        story_html = markdown_to_html(meta["body"])

        # Build the story page
        audio_player = build_audio_player() if has_audio else ""
        page_html = story_template
        page_html = page_html.replace("{{title}}", meta["title"])
        page_html = page_html.replace("{{reading_time}}", meta["reading_time"])
        page_html = page_html.replace("{{characters}}", meta["characters"])
        page_html = page_html.replace("{{audio_player}}", audio_player)
        page_html = page_html.replace("{{story_html}}", story_html)

        # Write story page
        story_out_dir = DOCS_DIR / "stories" / slug
        story_out_dir.mkdir(parents=True)
        (story_out_dir / "index.html").write_text(page_html, encoding="utf-8")

        # Copy narration if it exists
        duration = None
        if has_audio:
            shutil.copy2(narration_path, story_out_dir / "narration.mp3")
            duration = story_duration(slug, narration_path, duration_lookup)
            print(f" [+ audio, ~{duration // 60}m{duration % 60:02d}s]")
        else:
            print()

        stories.append((slug, meta, has_audio, duration))

    # Sort stories by title for the index
    stories.sort(key=lambda s: s[1]["title"])

    # Build index page
    story_cards = "\n".join(
        build_story_card(slug, meta, has_audio)
        for slug, meta, has_audio, _ in stories
    )
    index_html = index_template.replace("{{story_cards}}", story_cards)
    (DOCS_DIR / "index.html").write_text(index_html, encoding="utf-8")

    # Write the manifest used by shuffle + sleep-mix JavaScript.
    manifest = [
        {
            "slug": slug,
            "title": meta["title"],
            "url": f"stories/{slug}/",
            "audio": f"stories/{slug}/narration.mp3",
            "duration": duration,
        }
        for slug, meta, has_audio, duration in stories
        if has_audio
    ]
    (DOCS_DIR / "stories.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    # Summary
    audio_count = len(manifest)
    print(f"\nBuilt {len(stories)} story pages ({audio_count} with audio)")
    print(f"Output: {DOCS_DIR}")
    print("Ready for GitHub Pages!")


if __name__ == "__main__":
    print("Building Once Upon a Savannah...\n")
    build_site()
