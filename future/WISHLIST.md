# Wishlist

Ideas for the future. Not building these now — just saving them so they don't get lost.

---

## Illustrations

Generate images for stories using AI image generation (DALL-E, Midjourney, or similar). Could build a `/illustrate` command that takes a story and generates key scene illustrations. Would make the stories feel like real picture books.

**What to figure out:**
- Art style — storybook watercolor? Classic Disney? Something specific to this project?
- How many illustrations per story? Key scenes only, or every page?
- Format — inline with the text, or separate image files?
- Tool — DALL-E API, Midjourney, Stable Diffusion, or commission a real artist?

## Phone-Accessible Reading

Make stories accessible on phones for bedtime reading without needing a laptop.

**Options:**
- **GitHub Pages** — render the repo as a simple website. Free, automatic, version-controlled.
- **Simple PWA** — a basic web app that works offline. Could cache stories for reading without internet.
- **Shared Google Doc** — simplest option. Just paste stories into a shared doc.
- **Notion / Obsidian** — if already using these tools, just sync the markdown.

## Text-to-Speech Audio

Generate audio narration of stories so Savannah can listen instead of (or in addition to) being read to.

**Options:**
- **ElevenLabs** — high-quality, natural-sounding TTS. Multiple voice options. API available.
- **Google Cloud TTS** — good quality, already set up if using GCP. Multiple voices and languages.
- **OpenAI TTS** — simple API, good quality.
- Could build a `/narrate` command that takes a story and generates an audio file.

## Voice Cloning (Moonshot)

Clone the voices of Savannah's grandparents (Big Al and Wilma) from existing audio recordings so the stories sound like they're being read by them.

**What's needed:**
- Audio samples of Al and Wilma speaking (the more, the better — minutes to hours)
- A voice cloning service (ElevenLabs supports this with their Professional Voice Cloning)
- Quality assessment of existing audio (clean speech vs. background noise matters)
- Ethical consideration — this is a gift made with love, using their voices to continue a tradition they started

**What to figure out:**
- How much audio exists? Minutes or hours?
- How clean is the audio? (Background noise, multiple speakers, etc.)
- Are both grandparents' voices available, or just one?
- ElevenLabs Professional Voice Cloning requires ~30 minutes of clean audio for best results, but can work with less.

## Story Collection / Book

Compile stories into a printable book format. A physical book of fairy tales would be an incredible gift.

**Options:**
- Pandoc → PDF with custom template (fairy tale formatting, illustrations, decorative elements)
- Professional printing services (Blurb, Lulu, etc.) for a real bound book
- Handmade / letterpress for something truly special

## Story Generator Improvements

- A `/bedtime` command that picks a random story or generates one on the fly
- Seasonal stories (Christmas tale, birthday tale, etc.)
- Stories that incorporate real events ("the time Luna chased a squirrel" → fairy tale version)
- A way for Savannah to request stories by theme ("tell me one about the ocean")
