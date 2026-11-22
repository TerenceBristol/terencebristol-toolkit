# /improve: history scan and prior-run audit

Read from SKILL.md Step 2 when the scope is historical or the arguments name sessions. Two helpers run in the background in parallel with Discovery: the history scan (general-purpose helper) and the prior-run audit (general-purpose helper; historical scope only, not for named sessions). Each brief names the person's scope pick, the current session's id, and the full path of this skill's folder (helpers have not loaded the skill, so they cannot find its `scripts/` folder otherwise).

## History scan helper

Put these rules in its brief.
1. **The project folder.** `<project-path>` is the project's absolute path with every `/`, space and `.` replaced by `-` (the folder rule in `learnings.md`). If that folder does not exist, list `~/.claude/projects/` and match by project name.
2. **The session window.**
   - **Named sessions:** exactly the sessions in the arguments (a uuid means `~/.claude/projects/<project-path>/<uuid>.jsonl`; for a path, its folder is the sessions folder and its file name without `.jsonl` the uuid). Since-time for the extraction: `1970-01-01T00:00:00`. Named sessions are not left out as the current session, and the anchor rules below do not apply.
   - **Otherwise, anchored to the last run:** read the project learnings `## Run Log`. The anchor is the latest `Scanned through: <ISO timestamp>, session <uuid>` line across entries. The window is the `.jsonl` files in `~/.claude/projects/<project-path>/` changed strictly after that time, without that entry's session and the current session.
   - **Old logs with no Scanned-through line in any entry:** take the newest date from the entry headings (`^### (\d{4}-\d{2}-\d{2})`; headings may carry a suffix such as `2025-01-15b`, and the order is not guaranteed newest first); the window is files changed on or after that date. A one-time same-day overlap is accepted.
   - **The current session** is left out: its uuid is the one the main conversation names in this brief (the last folder name before `/scratchpad` in the scratchpad path); only when neither exists, the most recently changed `.jsonl` (the one still growing), which can be wrong when two sessions are live in the project.
   - Newest first, **at most 10**, or every session in the window when the person picked "all N" at the scope question (the size guard, item 5, still applies). With no run log or no learnings file: the 10 newest sessions, plus the total session count so the main conversation can say how much history is unscanned and offer a backfill run. When the gap is over 10 and the person did not pick all: scan the newest 10 and report the count and date range of the rest.
   - **Deleted history:** in a project whose clean-up deletes old session files, nothing older than that is left; when the anchor is older, say how many days of history are gone instead of scanning silently.
3. **Extract the dialogue** with the extractor that ships with this skill, never a one-off copy (when it fails, fix that file):
   `bash <skill folder from the brief>/scripts/extract_sessions.sh <sessions-dir> <scratchpad> <since-UTC> <uuid>…`
   Run it with `bash`, because a downloaded copy may lose its run permission. Session timestamps are UTC, so convert the run-log anchor to UTC first. It writes one `extract-<session-date>-<uuid>.txt` per session into the scratchpad folder (or the project's `.tmp/improve/` when there is none) and prints the uuid, date and size of each. A multi-MB session usually shrinks to under about 150 KB.
   **If `jq` is missing** (the script needs it), write an equivalent extractor from these rules, save it once next to the learnings file as `~/.claude/improve-extract.sh` and reuse it:
   - **User turns:** entries with `.type=="user"` and `.isMeta != true`. Read `.message.content`, which is either a string or a list of blocks: keep a string as it is; from a list keep only `text` blocks. This leaves out `tool_result` blocks, which are also stored as user entries (a plain "user messages" extraction floods the scan with tool output; session files run to tens of MB). Prefix `USER:`.
   - **System wrappers:** drop texts that start with `<system-reminder`, `<local-command` or `<task-notification`. A text that starts with `<command-` becomes `USER-CMD <command-name>: <command-args>` when it has arguments (the person's main request often sits there, typed after a slash command), or `USER-CMD <command-name>` for a bare command.
   - **Answers and plan rejections:** first collect the ids of `AskUserQuestion` and `ExitPlanMode` tool calls in the file; keep `tool_result` text whose `tool_use_id` is one of them, prefixed `USER-ANSWER:` (its content is either a string or a list of `text` blocks; keep both forms). Never match on the text alone, because a Read of an older transcript also contains "The user answered:". The person's picks and typed answers live only there; without them the scan reports false findings and misses corrections.
   - **Typed while the assistant worked:** entries with `.type=="attachment"`, `.attachment.type=="queued_command"`, `.attachment.commandMode=="prompt"` and a human origin (`.attachment.origin.kind=="human"`, or no origin field), prefixed `USER-MIDTURN:`; task notifications use the same type and are never kept.
   - **Assistant turns:** entries with `.type=="assistant"`, `text` blocks only (no `tool_use`, no `thinking`), prefixed `ASSISTANT:`.
4. **Analyze by meaning, no keyword filter.** Read the extracts in full: corrections, restated preferences, praise, friction, capability gaps, techniques or fixes that worked (from either speaker; the assistant's own lessons count), repeated workflows. Tag each finding with the session date and a short quote; mark patterns seen in 2 or more sessions.
5. **Size guard.** When the extracts together are over about 300 KB, do not analyze them in one pass: return the file list, and the main conversation launches one analysis helper per session. Never cut silently.
6. **Return** findings by category with citations (short summaries, not raw text), plus a coverage block: sessions scanned (count and date range), sessions left out and why, and the unscanned total on a first run.

## Prior-run audit helper (historical scope)

Its job: check what earlier /improve runs recommended and whether accepted changes landed. Source: every entry of the project `## Run Log`, all of them, not only the scan window.
1. **Each accepted change:** read the target file and grep for the key phrase. Mark it **Verified** (text present), **Drifted** (file there, text missing or changed) or **Missing** (file gone). Check every change since the last audit, plus a sample of older ones.
2. **Each skipped or rejected item:** its date, what was proposed and why it was declined (if logged), and whether the friction came back in the scan. Items the learnings mark "rejected, don't re-surface" stay suppressed.
3. **Log integrity:** grep the windowed session files for /improve runs (also under the plugin's full name, `/terencebristol-toolkit:improve`) that have no run-log entry, and report them as "unlogged runs". This helper gets no hand-off from the scan, so it recomputes the window by the rules above. Only when the learnings file is missing does it rebuild the run list from the session files (the Changes Applied tables and question answers).
4. **Return** under 400 words: prior runs (count and dates), verified, drifted or missing (to re-apply), skipped but still signalling (to re-surface), with session dates and target files.

## What the main conversation shows first (historical scope)

1. **Coverage line:** what the scan covered, for example "Scanned 3 sessions since the last run (3 to 6 Mar); nothing older touched." Name what a cap or a first run left out and offer the backfill run.
2. **Audit table** of prior runs, before any new finding. Never drop a prior finding silently:

| Date | Recommendations | Implemented | Drifted | Skipped |
|---|---|---|---|---|

Drifted items and re-surfaced skipped items ("previously skipped on <date>") become cards on the findings page, ahead of new findings after the removals.
