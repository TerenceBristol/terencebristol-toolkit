# /improve: the learnings files

Read from SKILL.md Step 1 (load and apply) and Step 8 (save).

## The two files

Two files, split by kind, never the same item in both. These are /improve's own files.
1. **Global:** `~/.claude/improve-learnings.md`. How the person works with /improve and with rules across projects: page and presentation preferences, rule-wording modify signals, scope habits, tooling and hook preferences, and the "Decided: do not re-propose" list. Never project state: no counters, run diaries or project file sizes.
2. **Project:** `~/.claude/projects/<project-path>/improve-learnings.md`. This project's patterns, counters and dated run log. `<project-path>` is the project's absolute path with every `/`, space and `.` replaced by `-` (for example `/Users/jane/Code/my-app` becomes `-Users-jane-Code-my-app`), the same folder Claude Code uses for the project's session files. If that folder does not exist, list `~/.claude/projects/` and match by project name before creating anything.

If a file is missing, go on; it is created at the end of this run (SKILL.md Step 8).

## Saving them (Step 8)

- **Project file:** add a dated entry under `## Run Log`, heading `### YYYY-MM-DD: <one-line session signature>` (date and signature only, no run numbers, because counters drift and collide). **First line, required:** `Scanned through: <ISO timestamp>, session <current session uuid>`. The time comes from `date -Iseconds` at scan time, never estimated. The uuid comes from the scratchpad path; without one, the most recently changed `.jsonl` in the project's session folder, noted as such. The next run's window starts from this line. **Second line, required:** `Runtime: <start> to <finish>, <total>`, from the clock reads at the run's start and end, because the next run's "all N" estimate uses it. Then: the scope, the accept rate by type (for example "remove 4/4, add 1/2"), the size line, deferral counter updates (for example "CLAUDE.md size: 5th deferral"), this project's patterns and modify signals, and the commit id when the changes were committed in the same session. Update `## Patterns` and `## Counters` when the run changes them.
- **Global file:** update only when the run showed something about how the person works across projects.
- **Size of both files:** after writing, run `wc -l`. When the project file is over 80 lines, fold the oldest run-log entries into `## Patterns` in this run and delete those raw entries. Keep the global file under about 40 lines the same way; its "do not re-propose" list is kept whole, never folded away.
- **Settled patterns leave the learnings.** Look for a pattern confirmed in about 5 or more runs. Settled behaviour belongs in config: propose it as a card (this run if practical, otherwise flag it for the next) that writes it into the skill, CLAUDE.md or settings, and delete it from the learnings once written. Without this, learnings grow into a patch layer that quietly overrides the skill.

New project file:
```
# Improve Learnings: <project name>

## Patterns (distilled, project-specific)

## Counters (live deferral/tracking state)

## Run Log
### YYYY-MM-DD: <one-line session signature>
- Scanned through: <ISO timestamp from date -Iseconds>, session <uuid>
- Runtime: 14:05 to 14:40, 35 min
- Scope: current-only. Accepted: remove 3/3, edit 2/4.
```
