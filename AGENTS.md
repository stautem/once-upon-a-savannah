# once-upon-a-savannah

This file provides shared project instructions for coding agents working in this repository, including Codex, Claude Code, Gemini CLI, Cursor, and similar tools.

## Project Goal

Create bedtime fairy tales for Savannah. Every creative decision should support a warm, comforting, repeatable reading experience that works well aloud at bedtime.

## Voice & Tone

- Keep the tone warm, comforting, and cozy. Aim for a classic fairy-tale cadence.
- Use simple, clear language that reads smoothly aloud. If a sentence stumbles when spoken, simplify it.
- Use gentle humor when it fits, but never break the warmth of the story.
- Treat repetition as a feature. Repeated phrasing and structures make stories more memorable and soothing.
- End every story happily. Avoid ambiguity, bittersweet endings, or lingering dread.

## Story Rules

- Princess Savannah is always the hero. She solves problems through courage, kindness, and friendship.
- Luna is always a dragon based on the real black standard poodle: black-scaled, brave, smart, cuddly, loud, and demanding.
- Big Al and Wilma are always wise, loving elder figures. Keep them fairy-tale-abstract rather than explicitly calling them grandparents.
- Mom (Melissa) and Dad (Rick) can appear when needed, but they are not yet deeply developed.
- Use woodland critters as the supporting cast. Pick the critters that fit the story, and invent new ones when useful.
- Let settings vary from story to story. Do not lock the project into one fixed world.
- Keep stories between 1,000 and 2,000 words so they read aloud in about 5 to 10 minutes.
- Make stories repeatable. The beats should feel familiar and comforting across rereads.

## Story Structure

Use this shape unless a specific story needs a light variation:

1. The peaceful kingdom
2. The problem
3. The call
4. The adventure
5. The twist
6. The resolution
7. Happily ever after

## What Not To Do

- Do not make the story scary. Problems should feel manageable rather than threatening.
- Do not force moral lessons. Let any lesson emerge naturally. The takeaway may be said out loud at most once — in narration or in one character's line, never both, and never again in the closing paragraph on top of it. Zero is better than one.
- Do not make the prose literary or complex at the expense of read-aloud rhythm.
- Do not stack comparisons. One "like" or "as" per thing at most, and only when it is plain, concrete, and adds something. Most things need none. This includes personifying scenery or objects with "as if it had decided to..." chains — treat that as a comparison too.
- Do not pad a sentence, or add a follow-up sentence, that only restates what was just shown — in any shape: "the way X does/is/always has," "the kind that...," or a flat sentence that just re-asserts the one before it. This includes narrating the meaning of a nonverbal cue (a growl, a tail-thump) right after showing it. Trust the scene.
- Avoid "the kind of X that/who..." as a default descriptive frame. Fine once; a crutch at three or more.
- Keep roll-call sequences (one line per critter/villager doing the same beat) to three, and don't repeat the same roll-call twice in one story.
- Keep humor physical and situational, not dry narrator irony pitched over a child's head.
- Vary how the problem resolves. Not every story needs to end with "it was here/true all along, it just needed someone to notice."
- Do not treat character bible details as required beats. They are background; the plot comes from the story. This includes reciting a character's bible description verbatim (e.g. Luna's "brave and smart and cuddly and loud") as a scene beat.
- Do not include food guilt, body shaming, diet talk, or any similar framing.
- Do not include toxic messaging, shaming, put-downs played for laughs, or "not enough" undertones.
- Do not lose sight of the purpose of the project: carrying forward the feeling of Savannah hearing bedtime stories from her grandparents.

## Characters

Use [characters.md](./characters.md) as the character bible. Key recurring roles:

- Savannah: princess, hero, kind, brave
- Luna: black dragon, brave, cuddly, loud, based on the real dog
- Big Al: big, strong, protective, wise elder
- Wilma: elegant, gentle, knowing elder
- Spencer: a prince in the regular cast, kind, strong, steady, fond of Savannah and hasn't told her yet
- Mom and Dad: available for future use
- Woodland critters: flexible supporting cast

## Repository Structure

- `stories/` contains each story folder with `outline.md`, `draft.md`, and optional `narration.mp3`
- `docs/` contains the generated GitHub Pages site
- `scripts/build_site.py` rebuilds the site from the story drafts
- `scripts/narrate.py` generates narration audio
- `scripts/normalize_audio.py` normalizes narration loudness (ffmpeg loudnorm)
- `scripts/voice_test.py` supports narration voice comparison
- `site-templates/` contains the site HTML and CSS templates
- `templates/fairy-tale.md` is the story template

## Audio Narration

Stories can be narrated with `scripts/narrate.py` using either ElevenLabs or AWS Polly.

- Default mode is `auto`: try ElevenLabs first, then fall back to AWS Polly on quota, credit, or rate-limit failures
- Default ElevenLabs voice: Imogen
- Default Polly fallback voice: Amy
- Output path: `stories/{name}/narration.mp3`
- ElevenLabs requires `ELEVENLABS_API_KEY` in `.env`
- Polly requires AWS credentials plus `boto3`
- Voice settings are tuned for bedtime delivery: stability `0.65`, similarity `0.75`, style `0.3`, speed `0.85`, speaker boost on
- Story extraction strips the draft header block, scene-break separators, and markdown formatting before synthesis
- After chunks are combined, the file is re-encoded and loudness-normalized with ffmpeg to `-24` LUFS, LRA `5`, true peak `-1.5` dBTP; requires `ffmpeg` on PATH

Common commands:

- `python scripts/narrate.py <story-name>`
- `python scripts/narrate.py <story-name> --provider polly`
- `python scripts/narrate.py --list-voices --provider elevenlabs`
- `python scripts/normalize_audio.py [story-name] [--measure] [--force]` to re-normalize existing narrations; files already at target are skipped
