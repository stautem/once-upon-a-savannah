"""
Normalize narration loudness so every story plays at the same gentle level.

Uses ffmpeg's two-pass EBU R128 loudnorm filter. Pass one measures the file,
pass two applies linear gain plus gentle range compression so chunk boundaries
and provider drift do not produce audible volume steps.

Usage:
    python scripts/normalize_audio.py                 # all stories/*/narration.mp3
    python scripts/normalize_audio.py <story-name>    # one story
    python scripts/normalize_audio.py --measure       # report loudness only
    python scripts/normalize_audio.py --force         # redo files already at target
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
STORIES_DIR = PROJECT_ROOT / "stories"
DOCS_STORIES_DIR = PROJECT_ROOT / "docs" / "stories"

# Bedtime targets: well below podcast norms so overnight playback stays quiet
# even at low device volume, with a tight range so nothing jumps out.
TARGET_LUFS = -24.0
TARGET_LRA = 5.0
TARGET_TRUE_PEAK = -1.5
OUTPUT_BITRATE = "128k"
# Files already this close to target are skipped to avoid needless re-encoding.
TOLERANCE_LU = 0.7


def require_ffmpeg():
    if shutil.which("ffmpeg") is None:
        sys.exit("ffmpeg is required for loudness normalization but was not found on PATH.")


def measure_loudness(path):
    """Return the loudnorm first-pass measurement as a dict."""
    filt = f"loudnorm=I={TARGET_LUFS}:LRA={TARGET_LRA}:TP={TARGET_TRUE_PEAK}:print_format=json"
    result = subprocess.run(
        ["ffmpeg", "-nostats", "-hide_banner", "-i", str(path), "-af", filt, "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    match = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", result.stderr)
    if not match:
        raise RuntimeError(f"Could not read loudnorm output for {path}:\n{result.stderr[-800:]}")
    return json.loads(match.group(0))


def normalize_file(path, *, quiet=False, force=False):
    """Two-pass normalize an MP3 in place. Returns (before_lufs, after_lufs).

    Skips files already within TOLERANCE_LU of the target unless force=True.
    """
    path = Path(path)
    stats = measure_loudness(path)
    before = float(stats["input_i"])
    if not force and abs(before - TARGET_LUFS) <= TOLERANCE_LU:
        if not quiet:
            print(f"  {path.parent.name}: {before:.1f} LUFS (already normalized, skipped)")
        return before, before

    filt = (
        f"loudnorm=I={TARGET_LUFS}:LRA={TARGET_LRA}:TP={TARGET_TRUE_PEAK}"
        f":measured_I={stats['input_i']}:measured_LRA={stats['input_lra']}"
        f":measured_TP={stats['input_tp']}:measured_thresh={stats['input_thresh']}"
        f":offset={stats['target_offset']}:linear=true:print_format=summary"
    )
    tmp = path.with_suffix(".normalized.mp3")
    result = subprocess.run(
        [
            "ffmpeg", "-y", "-nostats", "-hide_banner", "-i", str(path),
            "-af", filt, "-ar", "44100", "-ac", "1", "-c:a", "libmp3lame", "-b:a", OUTPUT_BITRATE,
            str(tmp),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"ffmpeg failed for {path}:\n{result.stderr[-800:]}")
    tmp.replace(path)

    after = float(measure_loudness(path)["input_i"])
    if not quiet:
        print(f"  {path.parent.name}: {before:.1f} -> {after:.1f} LUFS")
    return before, after


def story_files(story_name=None):
    """Narration files to process.

    Prefers stories/{slug}/narration.mp3 and falls back to the git-tracked copy
    under docs/stories/ when the working copy is absent (e.g. a fresh clone).
    """
    if story_name:
        for base in (STORIES_DIR, DOCS_STORIES_DIR):
            path = base / story_name / "narration.mp3"
            if path.exists():
                return [path]
        sys.exit(f"No narration found for {story_name}")
    found = {p.parent.name: p for p in DOCS_STORIES_DIR.glob("*/narration.mp3")}
    found.update({p.parent.name: p for p in STORIES_DIR.glob("*/narration.mp3")})
    return [found[k] for k in sorted(found)]


def main():
    parser = argparse.ArgumentParser(description="Normalize narration loudness")
    parser.add_argument("story", nargs="?", help="Story folder name (default: all stories)")
    parser.add_argument("--measure", action="store_true", help="Report loudness without changing files")
    parser.add_argument("--force", action="store_true", help="Re-normalize even files already at target")
    args = parser.parse_args()

    require_ffmpeg()
    files = story_files(args.story)
    if not files:
        sys.exit("No narration files found.")

    if args.measure:
        for path in files:
            stats = measure_loudness(path)
            print(f"  {path.parent.name}: I={float(stats['input_i']):.1f} LUFS  LRA={float(stats['input_lra']):.1f} LU  TP={float(stats['input_tp']):.1f} dBTP")
        return

    print(f"Normalizing {len(files)} file(s) to {TARGET_LUFS} LUFS, LRA {TARGET_LRA}, TP {TARGET_TRUE_PEAK} dBTP")
    for path in files:
        normalize_file(path, force=args.force)
    print("Done.")


if __name__ == "__main__":
    main()
