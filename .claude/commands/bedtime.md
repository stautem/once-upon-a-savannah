# /bedtime — Pick a Random Bedtime Story

You are picking a story for bedtime from the once-upon-a-savannah collection.

## What to do

1. **Scan the library.** List all story folders in `stories/` and read each `draft.md` frontmatter (title, characters, reading time).

2. **Pick one at random.** If there are multiple stories, choose one randomly. If `$ARGUMENTS` provides a preference (e.g., "something with Luna," "a short one," "the one about the garden"), filter first, then pick.

3. **Present the story.** Output:
   - The story title
   - Reading time
   - Characters in this story
   - A one-line teaser (don't spoil the ending)
   - Then the full story text, ready to read aloud

4. **If there's only one story**, just present it — no need to pretend you're choosing.

5. **If there are no stories yet**, say so and offer to create one with `/new-tale`.

## Rules
- Don't create or edit any files.
- Present the story cleanly — no markdown formatting clutter. This should be easy to read aloud from a screen.
- If the user asked for a theme and nothing matches, say so and offer to generate a new one with `/new-tale`.
