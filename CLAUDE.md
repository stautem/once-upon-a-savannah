# once-upon-a-savannah

@AGENTS.md

## Claude-Specific Notes

- Project-local slash commands live in `.claude/commands/`.
- The Documentation Map below is maintained for the `/update-docs` workflow.

## Documentation Map

<!-- update-docs reads this section. Keep it current when docs are added or removed. -->

| Doc | Audience | Role | Covers |
|-----|----------|------|--------|
| `AGENTS.md` | AI | canonical:agent-instructions | shared project instructions for coding agents |
| `CLAUDE.md` | AI | canonical:ai-instructions | Claude import wrapper, Claude-specific notes, documentation map |
| `README.md` | Human | canonical:navigation | project intro, stories table, commands, voice table, setup |
| `characters.md` | Human+AI | canonical:characters | character bible |
| `templates/fairy-tale.md` | AI | reference | story template used by `/new-tale` |
| `.claude/commands/*.md` | AI/System | reference | project-local slash command definitions |
| `future/WISHLIST.md` | Human | reference | future feature ideas, some completed |
| `stories/narration-progress.md` | Human | reference | snapshot checklist from the 2026-09-16 re-narration pass |

### Derivation Rules
- AGENTS.md is the shared source of truth for project conventions -> CLAUDE.md imports it and adds Claude-specific context
- AGENTS.md is source of truth for shared project guidance -> README summarizes
- characters.md is source of truth for characters -> AGENTS.md and README summarize
- README command table must match available skills (local + global)
