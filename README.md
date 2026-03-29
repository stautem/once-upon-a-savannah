# once-upon-a-savannah

Bedtime fairy tales for Savannah.

Stories where she's the princess, surrounded by woodland critters and a loyal dragon, with her grandparents woven in as wise and loving figures. Every story ends happily. Every story is meant to be read aloud, repeated, and remembered.

**Read or listen online:** [stautem.github.io/once-upon-a-savannah](https://stautem.github.io/once-upon-a-savannah/)

## What This Is

A collection of original fairy tales written as a gift. Savannah's grandparents — Big Al and Wilma — used to tell her bedtime stories where she was the princess. These stories carry that tradition forward.

## Stories

| Story | Reading Time | Voice |
|---|---|---|
| Luna the Dragon | ~7 min | Imogen |
| Luna in the Fog | ~8 min | Morgan |
| The Grand Riddle Faire | ~8 min | Josh |
| The Puzzle Garden | ~8 min | Grandma Rachel |
| The Locked-Up Lullabies | ~8 min | Tarquin |
| The Mixed-Up Map | ~10 min | Sillyman Oxley |
| The Dragon Who Loved Jigsaw Puzzles | ~8 min | Andrew |
| The Quilt That Wouldn't Stay Still | ~8 min | Sillyman Oxley |
| The Colors That Went Missing | ~7 min | Imogen |
| The Lantern Festival | ~8 min | Morgan |
| The Moonlight Garden | ~8 min | Grandma Rachel |

## How to Use

- **Online:** Visit the [website](https://stautem.github.io/once-upon-a-savannah/) on any phone or tablet — read along or tap play to listen
- **In person:** Pick a story from `stories/` and read it aloud at bedtime
- **With Claude Code:** Use the commands below to brainstorm, generate, review, revise, and narrate stories

## Project Structure

```
once-upon-a-savannah/
├── stories/              ← stories with outlines, drafts, and audio
│   ├── luna-the-dragon/
│   │   ├── outline.md
│   │   ├── draft.md
│   │   └── narration.mp3
│   └── ...
├── docs/                 ← GitHub Pages site (built from stories/)
├── scripts/
│   ├── build_site.py     ← generates the website from story files
│   ├── narrate.py        ← generates audio narration via ElevenLabs
│   └── voice_test.py     ← voice comparison tool
├── site-templates/       ← HTML/CSS templates for the website
├── characters.md         ← the cast and their personalities
└── templates/            ← story template for generating new tales
```

## Characters

- **Princess Savannah** — the hero, always
- **Luna the Dragon** — brave, cuddly, loud, and loyal. Based on their real black standard poodle
- **Big Al** — big, strong, wise grandpa figure
- **Wilma** — elegant, beautiful, wise grandma figure
- **Mom (Melissa) & Dad (Rick)** — Savannah's parents, available for future stories
- **Woodland critters** — a flexible cast (opossum, raccoon, bat, owl, fox, and more). See `characters.md`

## Narration Voices

Audio narration is generated with [ElevenLabs](https://elevenlabs.io/) using the flash model (`eleven_flash_v2_5`).

| Voice | ID | Style |
|---|---|---|
| Grandma Rachel | `0rEo3eAjssGDUCXHYENf` | Wise Southern senior |
| Imogen | `jv41DhCf464zw0TI7I1w` | Warm British storyteller |
| Morgan | `QQutlXbwqnU9C4Zprxnn` | Neutral, clean narrator |
| Tarquin | `7cOBG34AiHrAzs842Rdi` | Posh English RP |
| Josh | `nzFihrBIvB34imQBuxub` | Teacher for kids |
| Andrew | `gUABw7pXQjhjt0kNFBTF` | Smooth, smart, clear |
| Sillyman Oxley | `kAXSxs17BYwCxcleeuLV` | Lispy and sweet |

Reserved for future multi-voice narration (character voices):
| Voice | ID | Style |
|---|---|---|
| Crazy Eddie | `OTMqA7lryJHXgAnPIQYt` | Raspy cartoon gangster |
| Declan | `1BfrkuYXmEwp8AWqSLWk` | Dark Irish horror narrator |

## Commands

| Command | What it does |
|---|---|
| `/story-idea` | Brainstorm story premises — no files created, just ideas to pick from |
| `/new-tale` | Generate a new fairy tale — outline for approval, then full draft |
| `/read-aloud-check` | Review a draft for bedtime pacing, rhythm, and flow |
| `/revise` | Edit an existing story based on feedback |
| `/narrate` | Generate audio narration for a story using ElevenLabs |
| `/bedtime` | Pick a random story from the collection, ready to read aloud |

## Setup

To generate audio narration, add your ElevenLabs API key:

```
cp .env.example .env
# Edit .env with your key
```

To rebuild the website after adding or editing stories:

```
python scripts/build_site.py
```
