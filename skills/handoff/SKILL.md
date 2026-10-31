---
name: handoff
description: "Writes a handoff file and a kickoff prompt so a fresh chat can pick up a task exactly where this one stopped: goals, what's done, what's left, the decisions in your own words, and the approved plan. Use when you say \"handoff\", \"wrap up for a new chat\", \"give me a kickoff prompt\" or \"continue this in a new session\"."
license: MIT
compatibility: "Designed for Claude Code. The transcript step needs Claude Code's session logs; the rest is written to also work in Cowork (not yet tested there)."
---

# Handoff

Two files: the task's handoff (where things stand, with pointers to the files that hold the detail) and a kickoff prompt you paste into a new chat. Your working files stay the source of truth. Your project's own rules win over the defaults below.

Why: long chats get slower, more expensive and more confused, because Claude re-reads the whole conversation with every message. A handoff lets you start a fresh chat without losing the thread.

## Rules for the whole run

1. **Package, then stop.** When you ask for a handoff so the work continues in another chat, Claude stops the analysis in progress. Settled findings are written as "settled, do not redo"; interrupted threads are written as unfinished.
2. **Never send, commit or run anything** while handing off.
3. **Current state, not history.** Each run replaces the status and the open-items list; it never stacks a new one on top of the old. The handoff stays under about 10,000 words. The transcript keeps the history.
4. **Your words exact, Claude's reasoning short.** Your decisions and instructions are quoted word for word, with the date. Example: `Decided 12 Mar: "Keep the old pricing table, just add the new tier."`, not "the user wants to keep the table".
5. **Guard rules word for word.** A rule about spending, approvals, sending or deleting is copied word for word with its source, never summarised. Files that still say something a later decision overruled are listed as "superseded, do not follow".
6. **Verified only.** State only what was checked. Label guesses as guesses. Write scheduled events as scheduled, never in the past tense.
7. **Real times.** Read the clock first (for example `date '+%Y-%m-%d %H:%M'`). Every time in the handoff and kickoff comes from the clock or a record, in the time zone saved in the handoff folder's README (otherwise the computer's own).

## Step 1: Load the project's handoff rules

1. Read the project's `CLAUDE.md` for any handoff rules (including where the handoff folder lives), and `<handoff folder>/README.md` if it exists. With no folder named anywhere, the handoff folder is `handoff/` in the project root.
2. The README has a `Confirmed: <date>` line: follow its rules and ask nothing in this step.
3. Rules exist but no `Confirmed:` line: show a summary of at most 3 lines, ask "Still correct?" once, then write `Confirmed: <today>` into the README.
4. No rules yet (first run): ask one question at a time, each with a recommendation: where handoff files live (recommended: `handoff/` in the project root); one file per task or one per session (recommended: one per task, named `YYYY-MM-DD-<topic>.md`, dated when the task started; the other choice is one per chat); anything every handoff must carry (examples: name the person behind each decision; keep a client's handoffs in that client's folder). Save the answers and `Confirmed: <today>` in the README. If the folder is not `handoff/`, add one line to the project's `CLAUDE.md`: "Handoff files live in <folder>."
5. Create the handoff folder if it doesn't exist.

## Step 2: Confirm this run

Ask one question at a time, recommendation first with its reason, but only a question whose answer would change the handoff (an unclear task, a next step the conversation does not settle, an open item only the user knows). When the conversation already settles an answer, take the recommendation and list it in the message that reports the handoff, so the user can overrule it, because routine confirmation questions mostly get the recommended answer anyway. Use a multiple-choice question tool where your app has one.

1. **Which task?** List the 5 most recently changed handoff files and recommend one, or "new file" for a new task. A chat with no real task yet (a first test) uses its own setup as the task. Before recommending "new file", search the handoff folder for the same topic, because two handoffs for one task split its state.
2. **What does the next chat do first?** (Skip it for a finished task.) Propose one sentence from the conversation and the approved plan. With an approved plan, propose "Carry out the approved plan: <plan title>".
3. **Open items to carry over.** List what you found (decisions still open, unfinished steps, scheduled events, steps the user owes such as checks, sends or decisions) and ask what is missing.

## Step 3: Write the handoff file

- **Existing file:** read it from disk first. Keep its sections. Replace "Current state" and "Open items" with today's; drop old status notes and old open-items lists.
- **New file:** these sections, in this order: Read this first; Goal; Open decisions (each with Claude's recommendation); Current state; Decisions (who decided, their words); Approved plan; Open items; Next chat starts with. Open decisions come before history.
- **Point, don't restate.** Name the file that holds a detail instead of copying it.
- **Save the approved plan once.** When the chat agreed a plan, save it as `<handoff folder>/plan-<topic>.md` (or the project's own plan file, if it has one) and have the handoff point to that file, with "Approved by <name>, <date>" and which steps are done. Copy nothing more: a copied plan doubles the handoff and its stale lines mislead the next chat. A finished plan shrinks to one line: done, date, where its record is.
- **Fresh body.** Re-read the whole file after editing and fix every stale section; a fresh header on a stale body is the classic failure.
- **Size.** Count the words. Over about 10,000: turn restated content into pointers until it fits.

## Step 3b: The transcript (your exact words)

- **In Claude Code:** find this chat's session log: the newest `~/.claude/projects/<project-slug>/*.jsonl` that holds this chat's recent messages. The folder name is the project's full path with every `/` turned into `-` (for example `/Users/sam/work` becomes `-Users-sam-work`). Run the script that ships with this skill (it sits in `scripts/` inside the folder this `SKILL.md` is in): `python3 <this skill's folder>/scripts/condense_transcript.py <session.jsonl> <handoff folder>/<handoff-name>-transcript.md`. For a task that already has a transcript from an earlier chat, add `--since start` so this chat is appended under its own heading. A second handoff in the same chat: write a new file instead (`<handoff-name>-transcript-2.md`, no `--since`) and point the handoff to both. If the script refuses (it won't overwrite or double-append), read its message, then check the transcript file before using `--overwrite`. Run it with `--help` for the other options.
- **Read the count line.** It prints "User messages: raw N, transcript M" and a verdict:
  - "(match)": every user message made it in.
  - "MISMATCH": some user words are missing; find them in the session log and add them to the transcript by hand.
  - "(not checked: no origin fields)": the log has no markers to count against (for example a run with no chat window); skim the transcript against the chat and add anything missing.
  - "(NOT CHECKED: N unreadable lines)": part of the log couldn't be read (often the session is still writing it); run the script again in a moment, and if it repeats, check those lines by hand.
  - "(match for this part, but N of the user's messages are before --since)": fine when an earlier part of this transcript already holds them; otherwise the `--since` value is wrong.
  - "possibly not shown: N" (any verdict): Claude replies that may never have reached the user's screen. They are listed in the transcript's "Script checks" section at its end. Read each one; one that carried a question or a decision goes under the handoff's Open decisions.
- **No session log** (Cowork, the Claude app, or the script can't run): quote the user's decisions and instructions word for word from the chat into the handoff's Decisions section instead. Do this while they are still in the chat, before it gets long or summarised.
- The handoff and the kickoff point to the transcript file, never to the raw session log (it can be tens of megabytes).

## Step 4: Write the kickoff prompt

**Finished task:** when the task is finished and no next chat continues it, write the handoff only and say in the report that no kickoff is needed, because a kickoff for finished work has nothing to start.

A plain-text file, `<handoff folder>/kickoff-<topic>.txt`, overwritten on every run (one prompt, the latest state). No placeholders. One kickoff per next chat: never a second copy beside it (a `-b` copy, a `.pre-<date>` backup, a dated copy), because a chat started from an old copy works from stale state. It restates no state the handoff holds (counts, statuses, findings); the word-for-word items below stay. Content, in this order:

1. **Open questions for the user**, each with Claude's recommendation, asked first, before any work. If an event was scheduled, a check comes here too ("Did the 14 Mar call happen? What changed?").
2. **One line on the task**, quoting the user's own scope word for word, never a narrower summary.
3. **"Already decided, do not re-ask"**: a list of the settled points, each with the user's words and the date. Points mentioned only in passing get re-asked otherwise.
4. **What to read:** "Read `<handoff path>` fully first", then the transcript, if there is one.
5. **"Check live first":** the live sources to re-read before trusting the snapshot (a board, a shared doc, an inbox, a repo).
6. **How to start:** the real first steps.
7. **The confirmed first task**, then this line: "When I paste this kickoff with words of my own, my words decide what runs."
8. **Hard limits** that must survive: approvals already given, things NOT to do, copied word for word.

Don't tell the next chat to skip clarifying questions or to go beyond the confirmed first task.

## Step 5: Review (the cold read)

Before reporting, test whether a fresh chat could really continue from the two files alone (a finished task: from the handoff alone):

1. Search both files for guard-rule words (spend, budget, send, delete, approve) and check each against its source (rule 5).
2. Start a fresh helper (a sub-agent, where your app has them) that gets ONLY the handoff file, the kickoff (if one was written) and the saved plan file (if there is one), nothing from this chat. Ask it: "Could you start this task from these files alone? List anything missing, unclear or contradictory." Where there is no helper, read the two files yourself as if you had never seen the chat.
3. Fix every gap it finds, then report.

## Step 6: Report

- Both file paths (a finished task: the handoff path only).
- "Handoff: <N> words".
- Every agreed deliverable as done, pending or deferred, checked against the files.
- The review line: "Review: <N> gaps found, <N> fixed".
- What the user does next: open a new chat and paste the kickoff; for a finished task, nothing (no kickoff was written).
