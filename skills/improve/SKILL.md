---
name: improve
description: Retrospective after a session with corrections or rework. Removes stale or duplicate config first, then proposes fixes to pick from. Use when the user types /improve or /improve config audit.
compatibility: "Designed for Claude Code"
license: MIT
---

# /improve: subtraction-first retrospective

A short list of proposed changes, removals first, the person's calls above the assistant's technical picks; nothing changes until the person picks. Works mid-conversation or at the end of a session.

**Announce:** "Starting retrospective..."

**Files.** `references/…` and `scripts/…` below sit in the folder this SKILL.md is in. If the `references/` folder is missing next to this file, stop and tell the person to install the whole `improve` folder (see the README's "Get it").

## Rules for the whole run

1. **Run after friction, never on a calendar.** Friction means corrections, rework or confusion. Do not suggest scheduled /improve runs.
2. **Subtraction first.** The removal pass (Step 4) runs before any addition, because rules should grow only on recurring evidence and every always-loaded line costs tokens on every call.
3. **Change nothing until the person picks.** Their accept on the findings page approves only text edits shown word for word on it. A new hook, a new skill or a multi-file restructure still goes through a plan first (plan mode where available, otherwise a written plan they approve).
4. **Versioned homes.** Every finding gets a home in a file the person can read and version (Step 5). If the project uses auto memory, memory files count as config: the removal pass and the checks cover them, and a rule that lives only in memory moves to its versioned home. When the person says "remember X" during the run, write it at once to that home and say which file.
5. **Never proceed silently on incomplete data.** Say what was skipped and why (a failed helper, a capped history window, an unreadable file).
6. **Check before you claim.** Grep before calling anything missing or duplicate; check each finding's main example against the primary record, including scope choices the person made in that session. Times come from `date`, never estimates.

## Arguments

Arguments are targeted feedback: they get the highest priority but do not narrow the run; every category is still checked.
- **A session id or `.jsonl` path** (one or more): the history scan covers exactly those sessions; skip the scope question.
- **`config audit`**, or a request for a standalone config health scan: skip the scope question, the conversation analysis and the history scan. Run Discovery, the removal pass and the health checks (Step 4), then the findings page as usual. Announce: "Running config-only audit: skipping conversation analysis." A single pass, best from a fresh conversation.
- **A dedicated config session** ("full sweep", "comprehensive", "config update", "update the entire repository config", "improve everything", or a skill clean-up session): read the "Dedicated config session" part of `references/config-health.md`.
- **A project's own lessons pass:** a project may define its own review pass (for example, lessons files kept per topic). When the person asks for it, follow that project's files for the format; the removal pass, the intake test and the findings page still apply.

## Step 1: Load

1. **Follow-ups first.** If the person keeps a follow-ups list for their setup (dated or waiting config items), read it. An entry that is done or no longer true becomes a "remove" card on the findings page. An entry that has come due is raised in this session, at the top of the chat summary.
2. **Learnings.** Read the global and the project learnings files (paths and the project-folder rule: `references/learnings.md`) and apply them: suppress finding types the person keeps rejecting, boost the ones they accept, and adapt rule wording to their modify signals (for example, if they keep softening "never" to plain wording, propose softer wording for rules that are not hard limits). Never re-propose an item on the global file's "Decided: do not re-propose" list. Announce in one line what loaded ("Loaded learnings: N project patterns, M rejected items suppressed, run log through YYYY-MM-DD", or "No learnings files yet: first run for this project").
3. **Claude Code version.** Compare the first word of `claude --version` with `~/.claude/improve-last-version.txt`. When they differ, or the file is missing, read `references/version-check.md` and run its two checks before Step 4.

## Step 2: Scope

Skip this step when the arguments name sessions or `config audit`. Otherwise first count the sessions since the last run (N, by the window rules in `references/history-scan.md`, item 2), then ask (the question picker if there is one, otherwise plain text): "What scope should this retrospective cover?" Recommend "Historical + current" when /improve is the first thing the person asked for in this conversation and N is above 0 ("Historical, all N sessions" on a first run with no run log, when N is over 10); otherwise recommend "Current conversation only".
- **Current conversation only**: this session's patterns and feedback.
- **Historical + current**: the sessions since the last /improve run (the newest 10 when there are more), the prior-run audit, and this conversation.
- **Historical, all N sessions** (only when N is over 10): every session since the last run, plus the prior-run audit and this conversation; a longer scan (it may use one reading helper per session); when the run log has a `Runtime:` line for an earlier history run, add its total as a rough estimate.

On a first run with no run log, N is the project's total session count and "all N" is the backfill. For historical scope or named sessions, read `references/history-scan.md` and follow it; its helper briefs name the person's pick, the current session's id and this skill's folder.

## Step 3: Gather

First read `references/config-health.md`: its "Config map" section is the Discovery brief, and its checks run at Step 4. Launch the helpers in the background, then analyze the current conversation while they run. If background helpers are not available, do the same work in order in the main conversation.

**Discovery (Explore helper, always).** Catalogs every config file at project and global level, with its purpose, by type and level, per the "Config map".

**History scan and prior-run audit** run only for historical scope or named sessions (Step 2).

**Current conversation** (skip in config audit). Announce: "Analyzing current conversation..." Look for corrections (no, don't, stop, redo), preferences the person restates that a file already states, friction (several attempts, confusion), capability gaps (they did it by hand, or the assistant could not), behaviour (tone, over- or under-explaining, wrong assumptions), the /improve arguments (highest priority), repeated multi-step workflows a skill step could own, techniques that worked (from either speaker), prompt styles that led to better or worse results, and praise (approaches the person confirmed or accepted without pushback).

When this conversation has little signal, say "No significant findings from this session" and go on.

**When a helper fails:** follow "When a helper fails" in `references/config-health.md`.

Then read each file Discovery listed that the findings or the health checks touch; with the health checks, that is most of them.

## Step 4: Removal pass (before any addition)

Read the files that load together in this project (global and project CLAUDE.md files, the skills and shared references the scanned sessions used, the follow-ups list if any). Look for:
- **lines the current model follows anyway** (default behaviour restated);
- **duplicates**: the same rule in two files that load together; keep one home, and the copy goes;
- **stale lines**: paths, tools, versions or facts that no longer hold, above all a statement the session itself disproved (a wrong recipe costs more than a missing one);
- **contradictions** across files that load together, or between a skill and CLAUDE.md;
- **text a registered hook already enforces in full**: it shrinks to one line naming the hook;
- follow-ups entries that are done or no longer true.

Each is a "remove" or "edit" card. Before a card says "duplicate" or "already covered", grep the other home, confirm the match covers the same scope and intent (not just similar wording), and show the evidence on the card ("Verified: `<file>`:N holds `<text>`"). With zero matches it is a "move" card, never a delete.

**Health checks (every run).** Run the checks in `references/config-health.md` on the project and global files. They produce the misplaced-content and maintenance cards.

**Stale files.** When the run comes across leftover working files (executed plans, old handoff notes, finished progress files, old drafts in scratch folders, archive folders), count them. Do not scan for them and never move or delete them; the end of the run reports the count.

## Step 5: Findings

First read `references/findings-rules.md`: rules that keep breaking, enforcement gaps and hooks, the intake test, homes, rule wording, confidence and card order.

**A restated preference is a rule that is not working.** When the person restates a preference a file already holds, the finding is that rule: give it a mechanism (a hook, a script check, a step that puts the fact in front of the assistant) or a rewrite, never another copy.

**Count and check.** Count the final list and state the unit once (finding or edit); re-check each main example (rule 6).

## Step 6: Findings page and the pick

1. With more than four cards, build the findings page: read `references/review-page.md`. With four or fewer, show the cards in chat (same content) and ask (the question picker if there is one, otherwise plain text); the accepted edits then go into one short plan, because only the page accept counts as approval.
2. **Do-no-harm pass** before the person decides, for every proposed change (and again after applying when it touches hooks or steps they run): a separate helper reads the proposed changes against "the setup already works well: can any change make everyday work worse?" and tries each changed path on a real input (a hook on a replay of the real command, a check on known-good files). This is the assistant's own pass; it does not replace the person's own review of a plan.
3. Chat summary in the same turn as the question, in this order: due follow-ups, the coverage line and prior-run audit (historical scope), net size effect, card counts by type (remove, move, edit, add), the version-check result when it ran, the stale-files line, and the page path.
4. One question: accept the picks as shown, or flag items. Each flagged item then goes one at a time with its own question, recommended option first. If the person asks to go one at a time ("walk me through them"), present every card that way in page order; with 8 or more, after 5 ask whether to continue or apply what is decided.
5. Accepted text edits shown word for word on the page go to Step 7. A new hook, a new skill or a multi-file restructure goes into one plan first.

## Step 7: Apply

Read `references/apply.md` and follow it.

## Step 8: End of every run

1. Save both learnings files per `references/learnings.md`, whether or not anything was applied, and write the first word of `claude --version` into `~/.claude/improve-last-version.txt`.
2. Print the size line, even when nothing changed:
   `Size: always-loaded words <before> → <after> (<change>). <file>: +<added> −<removed> lines; <file>: ...`
   Always-loaded means the CLAUDE.md files that load in this project (global, project root, project `.claude/`), counted with `wc -w` before the first edit and after the last. Lines added and removed come from `diff` per changed file, every changed file listed.
3. Print the stale-files line: `Stale files: N seen` (or `Stale files: none seen`), so the person can tidy them.
4. Ask whether the person wants to commit the changes.

## It's working if

- The always-loaded text is the same size or shorter after runs (the size lines show it).
- No rule /improve added comes back as a correction. A rule that does is flagged in the next run as a rule that is not working (Step 5).
