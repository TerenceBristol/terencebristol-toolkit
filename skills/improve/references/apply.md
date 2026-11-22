# /improve: apply

Read from SKILL.md Step 7 after the person's accept.

Apply only what the person accepted: text edits shown word for word on the findings page, and anything else only after plan approval. **Announce:** "Applying N approved changes across M files..."

**Before any edit**
- Record the size baseline for the size line: `wc -w` of each always-loaded CLAUDE.md, and a copy of each file you will change in the scratchpad or `.tmp/improve/` (for the per-file `diff` at the end).
- **Verify before removing.** Before any removal (a CLAUDE.md rule, a skill section, a memory file, a follow-ups entry), grep the destination again to confirm the rule really lives there. If it does not, skip the removal and say: "SKIPPED: <rule> was accepted for removal, but grep shows it is not in <target>. Keeping the original."
- When you back up a CLAUDE.md, name the copy `CLAUDE.before.md`, never `CLAUDE.md`, because Claude Code loads any CLAUDE.md in a folder it reads.

**Edits**
1. Group the changes by file. With 10 or more changes, apply them in waves of helpers, no two helpers on the same file in one wave, and show the wave plan first ("Wave 1: ..., Wave 2 (after Wave 1): ..."). Fewer than 10: one by one.
2. Edit each file with the exact text shown on the page.
3. **Moves:** remove the text from the source and add it to the destination's most fitting section, in the destination's style; keep the meaning, change only format and references.
4. **Path-specific rules** (for example "for `*.test.ts` files"): write them to `.claude/rules/<name>.md` with a path glob in the frontmatter, then remove them from CLAUDE.md.
5. **A procedure moved into a skill** (after plan approval for a new skill): give the skill its frontmatter (name, description as in the skill checks in `config-health.md`), move the steps, and leave one trigger line in CLAUDE.md that names the moment and the skill.
6. **Description rewrites:** edit the frontmatter `description`, keeping its intent and sharpening its clarity and trigger words.
7. **Reference files** (project facts, people, product decisions): edit the project reference file the finding names. Dated or waiting config items go to the follow-ups list, if the person keeps one.
8. **Hooks** (after plan approval): read the target settings file and add the hook under its event key (create the `hooks` key if missing); keep every existing hook, append, never replace. Run its test file and the do-no-harm pass on a replay of the real command.

**Checks after editing**
1. **Full read after a structural edit** (removing a mode, merging workflows, deleting a section): a grep for the removed words is not enough, because text that assumes the removed part survives in shared sections without its words. Read the whole edited file (or have one Explore helper do it) for text that still assumes the old structure: pause or ask steps, other approval paths, choice wording.
2. **Contradiction read:** read every edited section against the rest of its file and against the CLAUDE.md files that load with it, for contradictions and confusing spots.
3. **Hook tests:** after editing a skill linked to a hook (the skill names a hook, a hook header names the skill, or the edit touched a rule-list file in its folder), run that hook's test file and show pass or fail in the summary. A failing test is fixed, or the edit reverted, before the run ends.
4. **Do-no-harm pass again** when the changes touched hooks or steps the person runs: on the applied files, with real inputs (SKILL.md Step 6).

**Summary table**

```
## Changes Applied

| # | File | Change | Type |
|---|------|--------|------|
| 1 | path/to/file.md | Removed duplicate of ... | remove |

N changes across M files.
```

File: short relative path. Change: a short action ("Removed: ...", "Moved: ... to ...", "Edited: X to Y", "Added: ...", "Hook added: ...", "Description rewritten: ..."). Type: remove, move, edit or add. Then the size line and the stale-files line (Step 8).

**Offer the port once.** When an applied change proved itself in one project and plausibly fits the person's other similar projects, ask once in the same session: "Port this to <projects>?", listing only the ones where it fits. Apply it to the ones they pick; do not port without asking and do not ask again after a no.
