# once-upon-a-savannah

Bedtime fairy tales for Savannah. This is a gift project — every creative decision should serve the goal of making something warm, comforting, and repeatable that can be read aloud at bedtime.

## Voice & Tone

- **Warm, comforting, cozy.** Classic fairy tale cadence. Think Cinderella, Pocahontas, Goodnight Moon.
- **Simple and clear.** These are bedtime stories. The language should flow easily when read aloud. No complex sentences, no vocabulary that breaks the rhythm.
- **Gentle humor.** The critters can be funny. The situations can be silly. But the warmth never breaks.
- **Repetition is a feature.** Fairy tales use repeated phrases, repeated structures, call-and-response patterns. These make stories easier to remember and more comforting to hear again.
- **Every story ends happily.** No ambiguity. No lingering dread. No bittersweet. Pure comfort. Happily ever after, every time.

## The Rules

- **Princess Savannah is always the hero.** She's kind, brave, and adventurous. She solves problems through courage and friendship, never through violence or cruelty.
- **Luna is always a dragon** — but she's not always the twist. She can be the mystery, the sidekick, the comic relief, or just part of the crew from the start. Black-scaled, brave, smart, cuddly, loud, and demanding. Based on their real black standard poodle — she should always feel like the real Luna underneath the dragon exterior.
- **Big Al and Wilma are always wise, loving figures.** They can appear as dragon experts, magicians, kingdom elders, forest sages — whatever fits the story. Keep the relationship fairy-tale-abstract — they're magical elders who guide and protect Savannah, not explicitly grandparents. But they should always *feel* like the real people: Al is big, strong, burly, protective. Wilma is elegant, beautiful, gentle, knowing.
- **Mom (Melissa) and Dad (Rick)** are available but not yet developed. Include them only when the story calls for it.
- **Woodland critters are the supporting cast.** There's no fixed crew — each story picks 2-4 critters that fit the adventure. See `characters.md` for the full palette. New critters can be invented as needed.
- **Settings vary.** A kingdom one story, a forest village the next, a seaside town after that. Don't lock into one world — let each tale build its own place.
- **Stories should be 1,000-2,000 words.** Readable aloud in 5-10 minutes at a comfortable bedtime pace.
- **Stories should be repeatable.** Simple enough to memorize the beats. Comforting enough to hear many times. The structure should feel familiar even as the specific adventure changes.

## Story Structure

Every story follows this basic shape (with room for variation):

1. **The peaceful kingdom** — establish the world, the characters, the warmth
2. **The problem** — something small and solvable disrupts the peace (never truly dangerous)
3. **The call** — Savannah decides to help, gathers her friends
4. **The adventure** — journey, discovery, helpers along the way
5. **The twist** — the "scary" thing is actually friendly or helpful, or the problem turns out to have a sweet solution
6. **The resolution** — the problem is solved through kindness and friendship
7. **Happily ever after** — everyone is safe, warm, and together

## What NOT to Do

- Don't make it scary. Even the "problem" should feel manageable, not threatening.
- Don't add moral lessons unless they emerge naturally. This isn't didactic — it's comfort.
- Don't make the language literary or complex. Read every sentence aloud — if it stumbles, simplify it.
- Don't include food guilt, body shaming, or anything in that territory. No "ate too much," no comments about size or appearance being a problem, no diet talk, no food restriction framing. Characters can eat and enjoy food freely. Keep it joyful and uncomplicated.
- Don't include any toxic messaging — no shaming of any kind, no put-downs played for laughs, no "you're not enough" undertones. These stories should only ever build a kid up.
- Don't forget who this is for. Savannah misses her grandparents' bedtime stories. These are meant to carry that feeling forward.

## Characters

See `characters.md` for the full character bible. Key references:

- Savannah = princess, hero, kind and brave
- Luna = black dragon, brave and cuddly and loud (their real poodle)
- Big Al = grandpa, big and strong and wise
- Wilma = grandma, elegant and beautiful and knowing
- Mom (Melissa) & Dad (Rick) = parents, not yet fleshed out
- Critters = flexible cast, pick from the palette in characters.md or invent new ones

## Audio Narration

Stories can be narrated via `scripts/narrate.py` with either ElevenLabs or AWS Polly.

- Default mode: `auto` — tries ElevenLabs first, then falls back to AWS Polly only on ElevenLabs quota / credit / rate-limit failures
- Default ElevenLabs voice: Imogen (warm British storyteller)
- Default Polly fallback voice: Amy
- Run: `python scripts/narrate.py <story-name>`
- Force provider: `python scripts/narrate.py <story-name> --provider polly`
- All voices: `python scripts/narrate.py --list-voices --provider elevenlabs`
- Custom ElevenLabs voice: `python scripts/narrate.py <story-name> --provider elevenlabs --voice <voice-id>`
- Custom Polly voice: `python scripts/narrate.py <story-name> --provider polly --fallback-voice <voice-id>`
- See `README.md` for the full voice table
- Requires `ELEVENLABS_API_KEY` in `.env` for ElevenLabs narration
- Requires AWS credentials plus `boto3` for Polly narration: `pip install boto3`
- Output: `stories/{name}/narration.mp3` (gitignored)
- ElevenLabs voice settings: stability 0.65, similarity 0.75, style 0.3, speed 0.85, speaker boost on
- Cross-chunk context: ElevenLabs passes adjacent text between API calls for smoother transitions
- Story text extraction strips the header block (up to first `---`), scene break `---` lines, and markdown formatting

## Documentation Map

<!-- update-docs reads this section. Keep it current when docs are added or removed. -->

| Doc | Audience | Role | Covers |
|-----|----------|------|--------|
| `CLAUDE.md` | AI | canonical:ai-instructions | voice/tone, rules, story structure, characters, narration |
| `README.md` | Human | canonical:navigation | project intro, stories table, commands, voice table, setup |
| `characters.md` | Human+AI | canonical:characters | character bible |
| `.claude/commands/*.md` | AI/System | reference | skill definitions |
| `future/WISHLIST.md` | Human | reference | future feature ideas, some completed |

### Derivation Rules
- CLAUDE.md is source of truth for voice/tone → README summarizes
- characters.md is source of truth for characters → CLAUDE.md and README summarize
- README command table must match available skills (local + global)
