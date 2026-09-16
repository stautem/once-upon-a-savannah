# /read-aloud-check — Review Content for Rhythm and Pacing

You are reviewing a draft for how it sounds when read aloud. This is a rhythm, pacing, and flow check — not a content or story review.

## What to do

1. **Read project context.** Read `AGENTS.md` to understand the project's voice, tone, and prose style. This determines your calibration:
   - If the project calls for spare/precise/literary prose: use a ~30-word sentence threshold, check for overwriting, dead air, and complex rhythm breaks. Dense sentences are fine if they have internal rhythm.
   - If the project calls for simple/clear/bedtime/children's prose: use a ~20-word sentence threshold, check for wind-down quality, pacing, and rule violations from AGENTS.md. Flag vocabulary that would trip up a reader.
   - If the project has no clear prose style guidance: default to 25 words, note that calibration may need adjustment.

2. **Identify the content.** If `$ARGUMENTS` names a file or story, find it. Check these locations in order:
   - `stories/{name}/draft.md` (creative writing projects)
   - `content/{name}.md` or `content/{name}/index.md`
   - Direct file path if provided
   - If no argument given, list available content and ask which to review.

3. **Review for read-aloud quality.** Always check:
   - **Overlong sentences** — anything over the threshold is suspect. Not a hard rule — flag for a second look.
   - **Stumble words** — awkward consonant clusters, tongue-twisters, words that break flow when spoken.
   - **Rhythm breaks** — monotonous sentence structure, jarring length shifts without purpose.
   - **Sound patterns** — unintentional rhyme, accidental alliteration, repeated words too close together.

   For **spare/literary prose**, also check:
   - **Overwriting** — stacked adjectives, purple phrasing, metaphors that call attention to themselves.
   - **Dead air** — sections where tension drops unintentionally, atmosphere leaks out.
   - **The ending** — does the final paragraph land when spoken? Does the rhythm resolve?

   For **bedtime/children's prose**, also check:
   - **Missing rhythm** — patterns of three, repeated phrases, call-and-response that could be stronger.
   - **The wind-down** — the last quarter should feel like settling. Flag if energy stays too high too late.
   - **Rule violations** — anything that breaks AGENTS.md rules (scary content, moral lecturing, etc.).

4. **Report findings as a list:**
   - Quote the specific line or passage
   - Say what the issue is (plain language)
   - Suggest a fix only if it's obvious — otherwise just flag the problem

5. **End with an overall assessment:**
   - **"Clean read"** — no significant issues
   - **"A few stumbles"** — minor tweaks needed
   - **"Needs a pass"** — enough issues that a focused revision is warranted

6. **Suggest next steps** based on what's available in the project (e.g., `/narrate` for audio, revision commands if they exist).

## Rules
- Don't edit any files. This is a review only.
- Be specific — quote actual text, don't speak in generalities.
- This is about how it *sounds*, not whether the content is good. Different job.
- Don't flag intentional repetition or unusual structures — flag *accidental* patterns.
- Respect the project's style. Don't suggest simplifying vocabulary unless the project's voice calls for simplicity.
