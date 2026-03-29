"""
Voice shootout — generate a short sample from the same story with multiple voices.
Saves each sample to voice-tests/ for comparison.
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")
API_KEY = os.getenv("ELEVENLABS_API_KEY")

SAMPLE_TEXT = (
    "The Dragon Who Loved Jigsaw Puzzles.\n\n"
    "Once upon a time, in a quiet little kingdom by a silver lake, "
    "there lived a princess named Savannah and a dragon named Luna.\n\n"
    "Every morning, they walked down to the shore together. The lake was calm "
    "and cool, with smooth pebble beaches and wildflower meadows that stretched "
    "all the way to the village green. Savannah liked to skip stones across the "
    "water — one, two, three hops — and watch the ripples spread.\n\n"
    "Luna liked to dig.\n\n"
    "She dug in the shallows. She dug in the mud. She sniffed every rock on the "
    "shore as if each one had a secret to tell. Sometimes she found an especially "
    "good rock and carried it around in her mouth for the rest of the morning, "
    "very pleased with herself."
)

VOICES = {
    "tarquin":        "7cOBG34AiHrAzs842Rdi",
    "andrew":         "gUABw7pXQjhjt0kNFBTF",
    "grandma-rachel": "0rEo3eAjssGDUCXHYENf",
    "josh":           "nzFihrBIvB34imQBuxub",
    "sillyman-oxley": "kAXSxs17BYwCxcleeuLV",
}

VOICE_SETTINGS = {
    "stability": 0.65,
    "similarity_boost": 0.75,
    "style": 0.3,
    "use_speaker_boost": True,
}

output_dir = PROJECT_ROOT / "voice-tests"
output_dir.mkdir(exist_ok=True)

for name, voice_id in VOICES.items():
    print(f"Generating {name}...", end=" ", flush=True)
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={"xi-api-key": API_KEY, "Content-Type": "application/json"},
        json={
            "text": SAMPLE_TEXT,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": VOICE_SETTINGS,
        },
    )
    if r.status_code == 200:
        out = output_dir / f"{name}.mp3"
        out.write_bytes(r.content)
        print(f"done ({len(r.content):,} bytes) -> {out}")
    else:
        print(f"ERROR {r.status_code}: {r.text[:200]}")

print(f"\nAll samples saved to {output_dir}/")
print("Listen to each one and pick your favorite!")
