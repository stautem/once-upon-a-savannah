# /narrate — Generate Audio Narration

Generate an audio narration of a bedtime story using ElevenLabs text-to-speech.

## What to do

1. **Identify the story.** If `$ARGUMENTS` names a story (e.g., "the-dragon-who-loved-jigsaw-puzzles" or "dragon jigsaw"), find the matching story in `stories/`. If no argument is given, list the available stories and ask which one to narrate.

2. **Run the narration script:**
   ```
   python scripts/narrate.py <story-name>
   ```

3. **Report the result:**
   - Story narrated
   - File location (`stories/{name}/narration.mp3`)
   - File size and character count
   - Remind the user they can play it with `! start stories/{name}/narration.mp3`

4. **If `$ARGUMENTS` is "all"**, narrate every story that doesn't already have a `narration.mp3`.

## Options
- To use a different voice: `python scripts/narrate.py <story-name> --voice <voice-id>`
- To list available voices: `python scripts/narrate.py --list-voices`
- Default voice is Imogen (`jv41DhCf464zw0TI7I1w` — warm British storyteller)
- If `$ARGUMENTS` includes a voice name (e.g., "narrate luna-the-dragon with Tarquin"), look up the voice ID from the table in `README.md` and pass it with `--voice`

## Rules
- Don't edit any story files. This is audio generation only.
- If the script fails, check that `.env` has the `ELEVENLABS_API_KEY` and that `requests` and `python-dotenv` are installed.
