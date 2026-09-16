# /narrate — Generate Audio Narration

Generate audio narration using ElevenLabs text-to-speech. Configuration is read from the project's AGENTS.md.

## What to do

1. **Read narration config.** Find the "Audio Narration" section in `AGENTS.md`. Extract:
   - Script path (e.g., `scripts/narrate.py`)
   - Default voice name and ID
   - Output file pattern (e.g., `stories/{name}/audio.mp3`)
   - Any additional options (section support, voice tables, etc.)

   If there is no "Audio Narration" section in AGENTS.md, stop and tell the user:
   "This project doesn't have an Audio Narration section in AGENTS.md. The `/narrate` skill needs this to know how to run narration. Here's what to add:"
   ```
   ## Audio Narration
   - Script: `scripts/narrate.py`
   - Default voice: <voice-name>
   - Output: `stories/{name}/audio.mp3`
   - Requires `ELEVENLABS_API_KEY` in `.env`
   ```

2. **Identify the content.** If `$ARGUMENTS` names a story or file, find it. Check these locations in order:
   - `stories/{name}/draft.md`
   - Direct file path if provided
   - If no argument given, list available content and ask which to narrate.

3. **Check for a draft.** The content must exist. If it only has a concept or outline but no draft, tell the user there's nothing to narrate yet.

4. **Handle options from arguments:**
   - If `$ARGUMENTS` includes a voice name, look it up in the voice table (check README.md and AGENTS.md) and pass the voice ID to the script.
   - If `$ARGUMENTS` asks for a specific section (e.g., `--section 3`) and the script supports `--section`/`--sections` flags, handle section listing and narration.
   - If `$ARGUMENTS` is "all", narrate every item that doesn't already have an audio file.

5. **Run the narration script** using the path from AGENTS.md config. Use the default voice unless overridden.

6. **Report the result:**
   - Content narrated
   - File location and size
   - Character count sent to TTS
   - How to play it (`start <file>` on Windows, `open <file>` on Mac)

## Rules
- Don't edit any content files. This is audio generation only.
- If the script fails, check that `.env` has `ELEVENLABS_API_KEY` and that dependencies are installed.
- For section narration, always list sections first so the user can pick.
- When narrating "all", skip items that already have audio files — don't regenerate.
