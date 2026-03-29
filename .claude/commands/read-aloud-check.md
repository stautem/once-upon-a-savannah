# /read-aloud-check — Review a Story for Bedtime Pacing

You are reviewing a fairy tale draft for read-aloud quality. This is a rhythm and flow check — not a content review.

## What to do

1. **Identify the story.** If `$ARGUMENTS` names a story or path, use that. Otherwise, list the available stories in `stories/` and ask which one to review.

2. **Read the project rules:**
   - Read `CLAUDE.md` — especially the voice/tone section and what-not-to-do
   - Read the story's `draft.md`

3. **Review for read-aloud quality.** Check for:
   - **Long sentences** — anything over ~20 words is suspect for bedtime reading. Flag it.
   - **Stumble words** — vocabulary that breaks the rhythm or would trip up a reader. Suggest simpler alternatives.
   - **Missing rhythm** — fairy tales thrive on patterns of three, repeated phrases, and call-and-response. Note where these could be added or strengthened.
   - **Pacing** — sections that drag or rush. Bedtime stories should have an even, gentle pace that slows toward the end.
   - **The wind-down** — the last quarter of the story should feel like settling into bed. Flag if the energy stays too high too late.
   - **Rule violations** — catch anything that breaks `CLAUDE.md` rules (scary content, moral lecturing, food guilt, toxic messaging, etc.)

4. **Report findings as a simple list:**
   - Quote the specific line or passage
   - Say what the issue is
   - Suggest a fix (but don't apply it — that's what `/revise` is for)

5. **End with an overall assessment:**
   - "Ready for bedtime" — no issues, reads beautifully
   - "Almost there" — a few small tweaks needed
   - "Needs a revision pass" — structural pacing issues

6. **Ask:** "Want me to fix any of these with /revise?"

## Rules
- Don't edit any files. This is a review only.
- Be specific — quote the actual text, don't speak in generalities.
- This is about how it *sounds*, not how it *reads on screen*. Every note should serve the bedtime reading experience.
- A few long sentences are fine if they have natural rhythm. Don't be overly rigid — use judgment.
