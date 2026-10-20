---
name: improve
description: Retrospective after a session with corrections or rework. Removes stale or duplicate config first, then proposes fixes to pick from. Use when the user types /improve or /improve config audit.
compatibility: "Designed for Claude Code"
license: MIT
---

# /improve: subtraction-first retrospective

A short list of proposed changes, removals first; nothing changes until the person picks. Works mid-conversation or at the end of a session.

**Announce:** "Starting retrospective..."

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
- **`config audit`**, or a request for a standalone config health scan: skip the scope question, the conversation analysis and the history scan. Run Discovery, the removal pass and the health checks (Step 4), then the findings page as usual. Announce: "Running config-only audit: skipping conversation analysis." Best run from a fresh conversation. It is a single pass, not the dedicated session below.
- **A dedicated config session** ("full sweep", "comprehensive", "config update", "update the entire repository config", "improve everything", or a skill clean-up session):
  - every config file gets the Step 4 checks, and every candidate is grep-checked against CLAUDE.md and the skills;
  - the findings page shows every item with its pick, so the person decides each one, never an assumed-approval plan; flagged items go one at a time;
  - after their accept, write the execution plan (plan mode where available), then apply in waves of helpers, no two on one file (Step 7).
- **A project's own lessons pass:** a project may define its own review pass (for example, lessons files kept per topic). When the person asks for it, follow that project's files for the format; the removal pass, the intake test and the findings page below still apply.

## Step 1: Load

1. **Follow-ups first.** If the person keeps a follow-ups list for their setup (dated or waiting config items), read it. An entry that is done or no longer true becomes a "remove" card on the findings page. An entry that has come due is raised in this session, at the top of the chat summary.
2. **Learnings.** Read the two learnings files (below) and apply them: suppress finding types the person keeps rejecting, boost the ones they accept, and adapt rule wording to their modify signals (for example, if they keep softening "never" to plain wording, propose softer wording for rules that are not hard limits). Never re-propose an item on the global file's "Decided: do not re-propose" list. Announce in one line what loaded ("Loaded learnings: N project patterns, M rejected items suppressed, run log through YYYY-MM-DD", or "No learnings files yet: first run for this project"). The mechanism is never silent.
3. **Claude Code version.** Compare the first word of `claude --version` with `~/.claude/improve-last-version.txt`. When they differ, or the file is missing, run the two version checks (below) before Step 4.

### The learnings files

Two files, split by kind, never the same item in both. These are /improve's own files.
1. **Global:** `~/.claude/improve-learnings.md`. How the person works with /improve and with rules across projects: page and presentation preferences, rule-wording modify signals, scope habits, tooling and hook preferences, and the "Decided: do not re-propose" list. Never project state: no counters, run diaries or project file sizes.
2. **Project:** `~/.claude/projects/<project-path>/improve-learnings.md`. This project's patterns, counters and dated run log. `<project-path>` is the project's absolute path with every `/`, space and `.` replaced by `-` (for example `/Users/jane/Code/my-app` becomes `-Users-jane-Code-my-app`), the same folder Claude Code uses for the project's session files. If that folder does not exist, list `~/.claude/projects/` and match by project name before creating anything.

If a file is missing, go on; it is created at the end of this run (Step 8).

### Version checks (only after a Claude Code version change)

`~/.claude/improve-last-version.txt` holds one line: the version /improve last ran on (for example `2.1.200`). Step 8 rewrites it at the end of every run. Both checks run once per version change.
1. **Changelog check, workarounds only.** If the person keeps a list of workarounds for Claude Code problems (in the follow-ups list or a setup notes file), read the Claude Code changelog (`https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md`) for the versions after the last-run version up to the current one. For each workaround, look for its issue number or a fix that matches its problem, and record **fixed in <version>** (quote the changelog line), **not mentioned** or **unclear**. A fixed one becomes a card: re-test the workaround, then remove it, or keep it with the reason (a workaround that is a hook or a multi-file change goes through a plan). Match on the workaround's issue number and on any "version to watch" it names. A workaround whose own wait condition is not met yet gets a note in the summary, not a card. Nothing else in the changelog is in scope. One line per workaround goes in the chat summary. With no workaround list, skip this check and say so.
2. **Hook tests.** If the person keeps test files for their hooks (global or in the project's `.claude/`), run each once, because an update can change hook inputs or behaviour. Read each file's header first for where it writes; when it does not say, name the file in chat before running it. Show one pass or fail line per file. A failure becomes a Critical card with the failing output summarised, and its fix goes through a plan.

## Step 2: Scope

Skip this step when the arguments name sessions or `config audit`. Otherwise ask (the question picker if there is one, otherwise plain text): "What scope should this retrospective cover?"
- **Current conversation only (Recommended)**: this session's patterns and feedback.
- **Historical + current**: the sessions since the last /improve run (up to 10), the prior-run audit, and this conversation.

For historical scope or named sessions, two helpers run in the background in parallel with Discovery: the history scan (general-purpose helper) and the prior-run audit (general-purpose helper; historical scope only, not for named sessions).

### History scan helper

Put these rules in its brief.
1. **The project folder.** `<project-path>` is the folder rule from "The learnings files" (absolute path with every `/`, space and `.` replaced by `-`; if missing, match by project name under `~/.claude/projects/`).
2. **The session window.**
   - **Named sessions:** exactly the sessions in the arguments (a uuid means `~/.claude/projects/<project-path>/<uuid>.jsonl`; for a path, its folder is the sessions folder and its file name without `.jsonl` the uuid). Since-time for the extraction: `1970-01-01T00:00:00`. Named sessions are not left out as the current session, and the anchor rules below do not apply.
   - **Otherwise, anchored to the last run:** read the project learnings `## Run Log`. The anchor is the latest `Scanned through: <ISO timestamp>, session <uuid>` line across entries. The window is the `.jsonl` files in `~/.claude/projects/<project-path>/` changed strictly after that time, without that entry's session and the current session.
   - **Old logs with no Scanned-through line in any entry:** take the newest date from the entry headings (`^### (\d{4}-\d{2}-\d{2})`; headings may carry a suffix such as `2025-01-15b`, and the order is not guaranteed newest first); the window is files changed on or after that date. A one-time same-day overlap is accepted.
   - **The current session** is left out: its uuid is the last folder name before `/scratchpad` in the scratchpad path; without a scratchpad path, the most recently changed `.jsonl` (the one still growing).
   - Newest first, **at most 10**. With no run log or no learnings file: the 10 newest sessions, plus the total session count so the main conversation can say how much history is unscanned and offer a backfill run. When the gap is over 10: scan the newest 10 and report the count and date range of the rest.
3. **Extract the dialogue** with a `jq` script. Save it once as `~/.claude/improve-extract.sh` (the helper creates it on the first run) and reuse it; when it fails, fix that file instead of writing a new copy each run. Session timestamps are UTC, so convert the run-log anchor to UTC first and keep only entries at or after it. The rules:
   - **User turns:** entries with `.type=="user"` and `.isMeta != true`. Read `.message.content`, which is either a string or a list of blocks: keep a string as it is; from a list keep only `text` blocks. This leaves out `tool_result` blocks, which are also stored as user entries (a plain "user messages" extraction floods the scan with tool output; session files run to tens of MB). Prefix `USER:`.
   - **System wrappers:** drop texts that start with `<system-reminder`, `<local-command` or `<task-notification`. A text that starts with `<command-` becomes `USER-CMD <command-name>: <command-args>` when it has arguments (the person's main request often sits there, typed after a slash command), or `USER-CMD <command-name>` for a bare command.
   - **Answers and plan rejections:** first collect the ids of `AskUserQuestion` and `ExitPlanMode` tool calls in the file; keep `tool_result` text whose `tool_use_id` is one of them, prefixed `USER-ANSWER:` (its content is either a string or a list of `text` blocks; keep both forms). Never match on the text alone, because a Read of an older transcript also contains "The user answered:". The person's picks and typed answers live only there; without them the scan reports false findings and misses corrections.
   - **Assistant turns:** entries with `.type=="assistant"`, `text` blocks only (no `tool_use`, no `thinking`), prefixed `ASSISTANT:`.
   - Write one file per session into the scratchpad folder (or the project's `.tmp/improve/` when there is none), named `extract-<session-date>-<uuid>.txt`, and print the uuid, date and size of each. A multi-MB session usually shrinks to under about 150 KB.
4. **Analyze by meaning, no keyword filter.** Read the extracts in full: corrections, restated preferences, praise, friction, capability gaps, techniques or fixes that worked (from either speaker; the assistant's own lessons count), repeated workflows. Tag each finding with the session date and a short quote; mark patterns seen in 2 or more sessions.
5. **Size guard.** When the extracts together are over about 300 KB, do not analyze them in one pass: return the file list, and the main conversation launches one analysis helper per session. Never cut silently.
6. **Return** findings by category with citations (short summaries, not raw text), plus a coverage block: sessions scanned (count and date range), sessions left out and why, and the unscanned total on a first run.

### Prior-run audit helper (historical scope)

Its job: check what earlier /improve runs recommended and whether accepted changes landed. Source: every entry of the project `## Run Log`, all of them, not only the scan window.
1. **Each accepted change:** read the target file and grep for the key phrase. Mark it **Verified** (text present), **Drifted** (file there, text missing or changed) or **Missing** (file gone). Check every change since the last audit, plus a sample of older ones.
2. **Each skipped or rejected item:** its date, what was proposed and why it was declined (if logged), and whether the friction came back in the scan. Items the learnings mark "rejected, don't re-surface" stay suppressed.
3. **Log integrity:** grep the windowed session files for /improve runs (also under the plugin's full name, `/terencebristol-toolkit:improve`) that have no run-log entry, and report them as "unlogged runs". This helper gets no hand-off from the scan, so it recomputes the window by the rules above. Only when the learnings file is missing does it rebuild the run list from the session files (the Changes Applied tables and question answers).
4. **Return** under 400 words: prior runs (count and dates), verified, drifted or missing (to re-apply), skipped but still signalling (to re-surface), with session dates and target files.

### What the main conversation shows first (historical scope)

1. **Coverage line:** what the scan covered, for example "Scanned 3 sessions since the last run (3 to 6 Mar); nothing older touched." Name what a cap or a first run left out and offer the backfill run.
2. **Audit table** of prior runs, before any new finding. Never drop a prior finding silently:

| Date | Recommendations | Implemented | Drifted | Skipped |
|---|---|---|---|---|

Drifted items and re-surfaced skipped items ("previously skipped on <date>") become cards on the findings page, ahead of new findings after the removals.

## Step 3: Gather

Launch the helpers in the background, then analyze the current conversation while they run. If background helpers are not available, do the same work in order in the main conversation.

**Discovery (Explore helper, always).** Catalogs every config file at project and global level, with its purpose, sorted by type and level:
- CLAUDE.md files: project root, project `.claude/`, global `~/.claude/CLAUDE.md`;
- commands and skills (project `.claude/commands/` and `.claude/skills/`, global `~/.claude/commands/` and `~/.claude/skills/`), agents (`.claude/agents/`, `~/.claude/agents/`), project `.claude/rules/`;
- shared references and style or voice files (`shared/` folders, frameworks, guardrails) and the project's reference files;
- settings files (project and global `settings.json` and `settings.local.json`), the hooks they register, the skill each hook names in its header, and any hook test files;
- memory folders, if auto memory is on (`~/.claude/projects/<project-path>/memory/`);
- the follow-ups list, if there is one, and any other instruction-like `.md` file that governs behaviour.

Fallback paths when Discovery fails: the CLAUDE.md files, the `~/.claude/` commands, skills, agents and shared folders, and the project `.claude/` settings files.

**History scan and prior-run audit** run only for historical scope or named sessions (Step 2).

**Current conversation** (skip in config audit). Announce: "Analyzing current conversation..." Look for corrections (no, don't, stop, redo), preferences the person restates that a file already states, friction (several attempts, confusion), capability gaps (they did it by hand, or the assistant could not), behaviour (tone, over- or under-explaining, wrong assumptions), the /improve arguments (highest priority), repeated multi-step workflows a skill step could own, techniques that worked (from either speaker), prompt styles that led to better or worse results, and praise (approaches the person confirmed or accepted without pushback).

When this conversation has little signal, say "No significant findings from this session" and go on.

**When a helper fails.** If Discovery fails or returns nothing, scan the fallback paths yourself and announce "Discovery agent failed: using fallback config path scan". If the history or audit helper fails, fall back to current-conversation scope, skip the prior-run audit and recurring-pattern checks, and say so. A size-guard report from the history scan is not a failure: it means one analysis helper per session.

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

**Health checks (every run).** Run the checks below on the project and global files. They produce the misplaced-content and maintenance cards. Each check gives cards in the usual order and format. Label every size figure an estimate.

- **Size of always-loaded files.** Every CLAUDE.md that loads in the project costs tokens on every call, so measure each in estimated tokens. Estimate: characters divided by about 3, with HTML comments left out (they are stripped before loading): `python3 -c "import re,sys; print(len(re.sub(r'<!--.*?-->', '', open(sys.argv[1], encoding='utf-8').read(), flags=re.S)))" <file>`. Recalibrate the ratio now and then against a `/context` reading. Compare each file with a budget the person sets (for example its measured size plus a few percent headroom); with no budget, flag a file over about 200 lines and say the threshold is a guess. Warning: over budget. Critical: more than 25% over (a guess). Report the estimate, the budget and the three largest sections, because that is where cuts pay off.
- **CLAUDE.md sort.** Every-reply rules, hard limits and facts about the person stay. Procedures and situation rules move to the skill or file that runs them and leave a one-line trigger that names a moment the assistant can see. Project-only lines go to the project file. A section of more than about 20 lines that reads like a procedure is a skill step candidate (a skill costs only its description until it loads). Suggest a reorganisation only when the structure is unclear, not for style.
- **Path-specific rules.** CLAUDE.md lines that apply only to some files or folders ("for `*.test.ts` files", "in API routes") can move to `.claude/rules/` with a path glob, so they load only when the assistant touches those files.
- **Placement, five directions.**
  1. CLAUDE.md to a skill: a section that matters only while one skill runs (it names the skill, or describes a workflow such as brainstorming, reviewing, debugging or planning) moves into that skill. Rules needed while designing or investigating before any skill loads stay in CLAUDE.md, as one line if long; universal rules stay as they are.
  2. Reference or memory files to a skill: a file that holds a procedure, or a rule for one skill's execution, moves into that skill.
  3. A skill to CLAUDE.md: a rule inside a skill about the assistant's behaviour everywhere (not the skill's own procedure) is flagged for promotion. "Present findings one at a time" is skill-internal; "ask with the question picker for decisions" is universal.
  4. CLAUDE.md to a reference file: facts and reference detail that do not change behaviour move to the project reference files.
  5. Between skills: identical or near-identical sections in two skills move to one shared reference file.
- **Skills.** Check project and global skills and commands:
  - overlapping skills, or two descriptions that claim the same moment;
  - skills that grew past their purpose, or a main file over about 2,000 words or 500 lines (this skill is one file on purpose so it can be copied alone; do not flag it) (rare modes and reference material belong in separate files with "When X, read Y" pointers);
  - stale skills naming files, tools or paths that no longer exist;
  - a project skill with the same name as a global one (intended override or accident?);
  - descriptions: one or two sentences, what it does, then "Use when ..." with the person's real words for the moment; third person; concrete words. Give a suggested rewrite;
  - total description length: when `/context` or `/doctor` shows skills missing from the listing, that is a finding; over about 12,000 characters in total is a warning (a guess). Maintenance type unless the person reports skills not loading.
- **Contradictions across skills** (Critical, both sources cited with path and line): opposite directives; different terms for one concept; different procedures for the same situation ("ask before acting" against "act, then verify"); a skill that overrides CLAUDE.md without saying so.
- **Hook and skill links.** For every registered hook and every skill that names one: the hook's header names its skill and the skill names the hook; the hook's rule list exists where the hook reads it (inside the skill's folder when the rule belongs to a skill); a test file exists. A broken link or missing file is Maintenance; Critical when a blocking hook's rule file is missing. CLAUDE.md text that restates a rule a hook enforces in full shrinks to one line naming the hook.
- **Across levels.** Rules duplicated or contradicting between project and global CLAUDE.md; skills at both levels with different content; reference, memory or learnings content kept at the wrong level (project facts in a global file, cross-project lessons in one project).
- **Stale reference content.** A project reference file, memory file or follow-ups entry that is two or more releases behind the current milestone (the project's feature index, or `git log --oneline -5`), or that describes a finished one-time event (an audit result, a completed retest), is a stale card: remove, or keep as history with its date.

**Stale files.** When the run comes across leftover working files (executed plans, old handoff notes, finished progress files, old drafts in scratch folders, archive folders), count them. Do not scan for them and never move or delete them; the end of the run reports the count. A whole config file the health checks find stale counts toward that line too.

## Step 5: Findings

**A restated preference is a rule that is not working.** When the person restates a preference a file already holds, the finding is that rule: give it a mechanism (a hook, a script check, a step that puts the fact in front of the assistant) or a rewrite, never another copy.

**A rule that keeps breaking.** First look for a contradicting example or table row in the files that load together. Then prove the fix before it becomes standard: count the breaches with a script, and check the fix on a fresh run.

**Enforcement gaps.** A broken rule that a script can check is a hook candidate (below). A judgment rule broken once gets a clearer rule (a short "because", an example, or a move to the file the work reads), not removal. One broken again and again (across sessions, or more than once in this conversation in current-only scope) moves into the skill step where the work happens, or its checkable part becomes a hook. Capitals or a move to the top of a file are not a fix.

### Hook findings

A new hook always goes through a plan, never the findings page alone.
- **When to propose one.** A rule is a hook candidate when a script can see the breach in a tool call or a written file (a command, a path, a file name, a word list, a missing field), because a hook acts on every call while a written rule can be missed. Propose it after the first miss only for outward or irreversible actions; otherwise after two failures. Prefer a block over a reminder note.
- **The card** offers three picks, "Convert to hook" recommended for checkable rules: **Convert to hook** (the generated config on the card); **Clarify rule** (the rule plus a short "because", moved to the file and section the work reads; "never" only for hard limits); **Both** (the clarified rule, with the hook as backup). After "Convert to hook", ask which settings file it goes in: project `.claude/settings.json`, global `~/.claude/settings.json`, or project local `.claude/settings.local.json`.
- **Generate the full implementation.** Pick the event: `PreToolUse` with the `Bash` matcher for command rules; `PreToolUse` with the tool's matcher for tool-specific rules; `PostToolUse` for checks after a tool runs; `Notification` for reminders. Write the settings JSON ready to paste, and the script that enforces the rule. **Paths with spaces:** quote the script path in the command (`bash '/path with spaces/hook.sh'`), because a bare path splits into separate arguments.

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash", "hooks": [ { "type": "command", "command": "bash '/abs/path/hook.sh'" } ] }
    ]
  }
}
```

- **Hook and skill link.** When the hook enforces a rule that belongs to a skill, put the hook's rule list in a file inside that skill's folder (a hook tied to a CLAUDE.md rule keeps its list in one shared folder); name the skill in the hook's header comment and the hook in the skill; add a test file with realistic legitimate inputs that contain the blocked pattern and must pass. Never put hooks in skill frontmatter, because skills are often read as files, not invoked, and frontmatter hooks run only on invocation.

**Intake test for every addition.** An added rule needs all four:
1. **Recurring evidence:** seen at least twice. One direct correction is never high confidence; it waits for a second occurrence.
2. **The principle, not the single example.**
3. **The cited moment** in the record (session date and a short quote).
4. **The intake questions:** would it have helped more than this session? What goes wrong without it? Can a structural fix do it, then a check or hook, then an edit to an existing rule? New text comes last.

Skip findings that are already written and followed.

**Homes.** Work down this order and stop at the first that fits, because every always-loaded line costs tokens on every call and dilutes the rules around it:
1. a structural fix (a file, a script, a template, a step order);
2. a check or a hook, when a script can see the breach;
3. an edit to the existing rule that covers the case;
4. the owning skill, or a shared reference file when 2 or more skills need it;
5. a project reference file, for facts, reference detail and project context (/improve may update these files);
6. the follow-ups list, for dated or waiting config items (what, when or what to watch, the source), if the person keeps one;
7. CLAUDE.md last, for universal behaviour no earlier home covers.
Recommend one home with its reason; never ask the person where a rule should live.

**Rule wording** (for every proposed line):
- One rule, one reason: say what to do, with a short reason, so edge cases can be judged. "Never" only for hard limits.
- When clarifying a rule, keep its own wording and add the reason in one clause.
- Never escalate "try to" into "always" or "consider" into "must".
- In a CLAUDE.md file, a dated story becomes one block-level HTML comment line right after its rule (stripped before loading; never inside a code block); in skill and agent files, stories are deleted.
- Files read by smaller helper models state their scope and give positive examples, because those helpers follow text literally.
- Add a concrete example when the rule is not self-evident. One clear sentence beats a paragraph.
- A recommended option carries only constraints the evidence supports; one the assistant adds itself is labelled "my addition".

**Confidence** (shown on each card so the person can judge how closely to read it; it does not change the order): High = seen in 2 or more sessions, or 3 or more signals; Medium = one session, including a single direct correction, or a pattern match without direct evidence; Low = inferred from config structure or best practice. In current-conversation scope, nothing rises above Medium.

**Order of cards:** removals first, then drifted prior accepts, re-surfaced skipped items, targeted, critical (caused errors, repeated corrections, enforcement gaps), recurring patterns, misplaced content, improvements, techniques, maintenance (size, staleness, descriptions), reinforcement, new skill steps, and last, tips on the person's prompting.

**Count and check.** Count the final list and state the unit once (finding or edit); re-check each main example (rule 6).

## Step 6: Findings page and the pick

1. With more than four cards, build the findings page (below) and open it in the browser or a side pane. With four or fewer, show the cards in chat (same content) and ask (the question picker if there is one, otherwise plain text); the accepted edits then go into one short plan, because only the page accept counts as approval.
2. **Do-no-harm pass** before the person decides, for every proposed change (and again after applying when it touches hooks or steps they run): a separate helper reads the proposed changes against "the setup already works well: can any change make everyday work worse?" and tries each changed path on a real input (a hook on a replay of the real command, a check on known-good files). This is the assistant's own pass; it does not replace the person's own review of a plan.
3. Chat summary in the same turn as the question, in this order: due follow-ups, the coverage line and prior-run audit (historical scope), net size effect, card counts by type (remove, move, edit, add), the version-check result when it ran, the stale-files line, and the page path.
4. One question: accept the picks as shown, or flag items. Each flagged item then goes one at a time with its own question, recommended option first. If the person asks to go one at a time ("walk me through them"), present every card that way in page order; with 8 or more, after 5 ask whether to continue or apply what is decided.
5. Accepted text edits shown word for word on the page go to Step 7. A new hook, a new skill or a multi-file restructure goes into one plan first.

### The findings page

One local HTML page holds every card, so the person can read the whole round at once and accept the picks in one answer.
1. Write the cards to `<project>/.tmp/improve/cards-<YYYY-MM-DD>.json` (date from `date +%F`; any scratch folder the project ignores in git works):

```json
{
  "title": "/improve findings: <project>, <date>",
  "coverage": "Scope: current conversation. History: none scanned.",
  "size": {"before": 11800, "after": 11640},
  "due": ["Re-test the build workaround, due on or after <date>: ..."],
  "notes": ["Stale files: 3 seen"],
  "cards": [
    {"id": "F1", "type": "remove", "tier": "Maintenance", "confidence": "High",
     "file": "~/.claude/CLAUDE.md:120", "title": "Duplicate of the test rule",
     "before": "<exact current text>", "after": "",
     "moment": "", "evidence": "Verified: .claude/skills/testing/SKILL.md:4 holds <text>",
     "words": -42, "pick": "accept", "plan": false, "why": "one home per rule"}
  ]
}
```

   (Format only; the values are an example.) Fields: `type` is remove, move, edit or add; `before` and `after` are the exact text, word for word (for a move, `after` names the new file and line); `moment` cites the session date and a short quote; `evidence` holds the grep proof; `words` is the change in always-loaded words (0 for files that do not always load); `pick` is accept, skip or flag (the assistant's pick, preset on the page); `plan: true` marks a new hook, a new skill or a multi-file restructure; `why` is the one-line reason. `size.after` assumes every accept pick is taken.
2. Build the page from the JSON as one self-contained `.html` file beside it (no outside scripts, styles or fonts; escape all card text). On top: the title, the coverage line, the card count by type (remove, move, edit, add), the net size effect (before, after, change), due items, notes, and one line: "Your accept approves only the edits shown word for word; cards marked 'needs a plan' go into a plan first." Then the cards, removal cards first and the rest in your order. Each card shows its id, type, tier, confidence, file, title, the before and after text word for word, the moment, the evidence, the word change, the reason, a "needs a plan" badge when `plan` is true, and a pick control (accept, skip, flag) preset to `pick`, with a short note box for a flag.
3. A **"Copy my answer"** button copies one line built from the picks, and the same line also shows in a visible text box in case the browser blocks copying, for example `/improve page answer: accept all picks as shown.` or `/improve page answer: accept F1, F2; skip F4; flag F3 (why this file?).`
4. Give the page path in chat, and ask one question in the same turn as the chat summary: "Accept all picks as shown (Recommended)" or "I changed or flagged cards (paste the page answer)".

The person's accept approves the text edits shown word for word, nothing else. A card with `plan: true` goes into one plan after the accept. Each flagged card gets its own question, one at a time, recommended option first.

## Step 7: Apply

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
5. **A procedure moved into a skill** (after plan approval for a new skill): give the skill its frontmatter (name, description as in the Step 4 skill checks), move the steps, and leave one trigger line in CLAUDE.md that names the moment and the skill.
6. **Description rewrites:** edit the frontmatter `description`, keeping its intent and sharpening its clarity and trigger words.
7. **Reference files** (project facts, people, product decisions): edit the project reference file the finding names. Dated or waiting config items go to the follow-ups list, if the person keeps one.
8. **Hooks** (after plan approval): read the target settings file and add the hook under its event key (create the `hooks` key if missing); keep every existing hook, append, never replace. Run its test file and the do-no-harm pass on a replay of the real command.

**Checks after editing**
1. **Full read after a structural edit** (removing a mode, merging workflows, deleting a section): a grep for the removed words is not enough, because text that assumes the removed part survives in shared sections without its words. Read the whole edited file (or have one Explore helper do it) for text that still assumes the old structure: pause or ask steps, other approval paths, choice wording.
2. **Contradiction read:** read every edited section against the rest of its file and against the CLAUDE.md files that load with it, for contradictions and confusing spots.
3. **Hook tests:** after editing a skill linked to a hook (the skill names a hook, a hook header names the skill, or the edit touched a rule-list file in its folder), run that hook's test file and show pass or fail in the summary. A failing test is fixed, or the edit reverted, before the run ends.
4. **Do-no-harm pass again** when the changes touched hooks or steps the person runs: on the applied files, with real inputs (Step 6).

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

## Step 8: End of every run

1. **Save learnings** (both files from Step 1), whether or not anything was applied, and write the first word of `claude --version` into `~/.claude/improve-last-version.txt`.
   - **Project file:** add a dated entry under `## Run Log`, heading `### YYYY-MM-DD: <one-line session signature>` (date and signature only, no run numbers, because counters drift and collide). **First line, required:** `Scanned through: <ISO timestamp>, session <current session uuid>`. The time comes from `date -Iseconds` at scan time, never estimated. The uuid comes from the scratchpad path; without one, the most recently changed `.jsonl` in the project's session folder, noted as such. The next run's window starts from this line. Then: the scope, the accept rate by type (for example "remove 4/4, add 1/2"), the size line, deferral counter updates (for example "CLAUDE.md size: 5th deferral"), this project's patterns and modify signals, and the commit id when the changes were committed in the same session. Update `## Patterns` and `## Counters` when the run changes them.
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
   - Scope: current-only. Accepted: remove 3/3, edit 2/4.
   ```
2. Print the size line, even when nothing changed:
   `Size: always-loaded words <before> → <after> (<change>). <file>: +<added> −<removed> lines; <file>: ...`
   Always-loaded means the CLAUDE.md files that load in this project (global, project root, project `.claude/`), counted with `wc -w` before the first edit and after the last. Lines added and removed come from `diff` per changed file, every changed file listed.
3. Print the stale-files line: `Stale files: N seen` (or `Stale files: none seen`), so the person can tidy them.
4. Ask whether the person wants to commit the changes.

## It's working if

- The always-loaded text is the same size or shorter after runs (the size lines show it).
- No rule /improve added comes back as a correction. A rule that does is flagged in the next run as a rule that is not working (Step 5).
