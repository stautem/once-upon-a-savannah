"""
Build the GitHub Pages site from story markdown files.

Usage:
    python scripts/build_site.py

Reads stories from stories/*/draft.md, generates HTML pages in docs/,
and copies any narration.mp3 files alongside them.
"""

import re
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
STORIES_DIR = PROJECT_ROOT / "stories"
TEMPLATES_DIR = PROJECT_ROOT / "site-templates"
DOCS_DIR = PROJECT_ROOT / "docs"


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

    # Copy CSS
    shutil.copy2(TEMPLATES_DIR / "style.css", DOCS_DIR / "style.css")

    # Find all stories
    story_dirs = sorted(
        d for d in STORIES_DIR.iterdir()
        if d.is_dir() and (d / "draft.md").exists()
    )

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
        if has_audio:
            shutil.copy2(narration_path, story_out_dir / "narration.mp3")
            print(" [+ audio]")
        else:
            print()

        stories.append((slug, meta, has_audio))

    # Sort stories by title for the index
    stories.sort(key=lambda s: s[1]["title"])

    # Build index page
    story_cards = "\n".join(
        build_story_card(slug, meta, has_audio)
        for slug, meta, has_audio in stories
    )
    index_html = index_template.replace("{{story_cards}}", story_cards)
    (DOCS_DIR / "index.html").write_text(index_html, encoding="utf-8")

    # Summary
    audio_count = sum(1 for _, _, has_audio in stories if has_audio)
    print(f"\nBuilt {len(stories)} story pages ({audio_count} with audio)")
    print(f"Output: {DOCS_DIR}")
    print("Ready for GitHub Pages!")


if __name__ == "__main__":
    print("Building Once Upon a Savannah...\n")
    build_site()
