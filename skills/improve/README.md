# /improve

Your Claude Code setup gets better after every conversation: `/improve` reads what happened, spots what you corrected or liked, and suggests changes to your instructions. Nothing changes without your yes.

**Works in:** Claude Code (desktop app Code tab or terminal). It reads the conversation files Claude Code saves on your computer, so it won't work in the Claude app's chat.

[Back to the AI Toolkit for Knowledge Work](../../README.md)

---

## Get it

**Option 1: install the toolkit plugin (recommended, easy to update)**

In Claude Code, type these two lines one at a time:

```
/plugin marketplace add TerenceBristol/terencebristol-toolkit
/plugin install terencebristol-toolkit@terencebristol
```

Then start a new session and type `/improve`. If you already have a different command called `/improve`, use the full name: `/terencebristol-toolkit:improve`.

To get the newest version later, run `/plugin marketplace update terencebristol`, or switch on auto-update once: type `/plugin`, open **Marketplaces**, pick `terencebristol`, choose **Enable auto-update**.

**Option 2: copy the file (a plain copy you can edit)**

1. Open [`SKILL.md`](SKILL.md) and click "Download raw file".
2. Save it as `~/.claude/skills/improve/SKILL.md` (make the `improve` folder first).
3. Start a new session and type `/improve`.

To update, download the file again and replace yours.

---

## What it does

`/improve` asks what to look at: **this conversation only** (the default) or **this conversation plus the sessions since your last run** (up to 10, with a check of what earlier runs recommended). You can also name sessions by id, and `/improve config audit` checks your setup files without reading any conversation.

| Step | What happens |
|-------|-------------|
| **1. Load** | Reads its notes files (what you accepted or rejected before) and, after a Claude Code update, checks whether any of your workarounds were fixed and reruns your hook tests if you have them. |
| **2. Scope** | You pick "this conversation only" or "plus history". |
| **3. Gather** | Helpers map every setup file (CLAUDE.md, skills, agents, settings, hooks, `.claude/rules/`) and, in history scope, read the past sessions by meaning, including your answers in question boxes. It also reads the current conversation. |
| **4. Removal pass** | Before it adds anything, it looks for lines to cut: rules the model follows anyway, duplicates, stale facts and contradictions. Then health checks: file sizes, misplaced rules, overlapping skills. |
| **5. Findings** | Each finding gets one recommended home, from a structural fix or a hook down to CLAUDE.md last. A new rule needs evidence from at least two moments. |
| **6. Findings page** | With more than four proposed changes, one local page shows each of them word for word, with its evidence and a preset pick (four or fewer are shown in chat). You accept the picks in one answer, or flag the ones you want to discuss. A helper first checks that no change makes your everyday work worse. |
| **7. Apply** | Makes only the changes you accepted. New hooks, new skills and bigger restructures go through a plan first. |
| **8. Wrap up** | Saves what it learned, prints how much your always-loaded instructions grew or shrank, and asks whether you want to commit. |

### What it looks for

Corrections, things you had to repeat, friction (several tries), work you did by hand that could be automated, tone and wrong assumptions, repeated workflows, techniques that worked, and what you praised. Anything you type after `/improve` gets the highest priority.

### How findings are ordered

Removals first, then earlier accepted changes that drifted, items you skipped before that came back, then your typed feedback, critical items (rules that keep breaking), recurring patterns, misplaced content, improvements, techniques, maintenance, things that work and should stay, new skill steps, and last, tips for the human side.

### Example finding

```
[add | Critical | High | needs a plan] ~/.claude/CLAUDE.md:42

Rule "Ask before deleting files" was broken 3 times in recent sessions.
Proposed: a hook that blocks the delete command (the computer enforces it),
plus the rule with a short reason.
Evidence: sessions of 2 and 5 May, quotes on the card.
```

---

## Files it keeps

`/improve` keeps four small files and manages them itself:

- **`~/.claude/improve-learnings.md`** (global): what it has learned about how you like findings and rules written. Read at the start of every run, in every project.
- **`~/.claude/improve-last-version.txt`**: the Claude Code version of the last run, so it knows when to run the update checks.
- **`~/.claude/improve-extract.sh`**: the small script the history scan writes on its first run to pull the dialogue out of past sessions, reused after that.
- **`~/.claude/projects/<project-path>/improve-learnings.md`** (per project): that project's patterns and a dated log of runs. It sits in Claude Code's own data folder, never in your project. `<project-path>` is the project's full path with every `/`, space and `.` turned into `-` (for example `/Users/jane/Code/my-app` becomes `-Users-jane-Code-my-app`).

Delete any of them any time to start fresh. Patterns confirmed across about 5 runs are offered for promotion into your real setup files and then removed from the notes, so the notes stay small and your setup stays the source of truth.

---

## Works on any project

It finds your setup files on its own, whatever mix you use. It's most useful for assistants whose work isn't code (content, research, planning, YouTube), where the setup is plain English and every improvement shows right away.

---

## Latest change

**6.0.0 (2026-10-20):** rebuilt: removals come first, findings arrive on one page you accept in one answer, and it checks your workarounds after a Claude Code update. Full history: [CHANGELOG.md](CHANGELOG.md).

---

## Watch the video

[My AI Agents Now Upgrade Themselves (Claude Code)](https://youtu.be/heLMN5oDHEU)

---

## Credits

Built by studying six approaches from the Claude Code community:

- **[ChristopherA's Bootstrap Seed](https://gist.github.com/ChristopherA/fd2985551e765a86f4fbb24080263a2f):** patterns grow into rules over time
- **[bokan's /self-improvement](https://github.com/bokan/claude-skill-self-improvement):** parallel helpers and ranked friction patterns with evidence
- **[AccidentalRebel's Session Retrospective](https://github.com/accidentalrebel/claude-skill-session-retrospective):** reading the saved conversation files, and "techniques discovered" as a signal ([blog post](https://www.accidentalrebel.com/building-a-session-retrospective-skill-for-claude-code.html))
- **[Sionic AI /retrospective](https://huggingface.co/blog/sionic-ai/claude-code-skills-training):** write while the context is fresh
- **[One-Prompt Reflection Pattern](https://dev.to/aviad_rozenhek_cba37e0660/self-improving-ai-one-prompt-that-makes-claude-learn-from-every-mistake-16ek):** how to write good rules (NEVER/ALWAYS, the why first, real examples)
- **[Human-AI Retrospective](https://dev.to/gjergji_make/running-retrospectives-with-ai-treating-your-model-like-a-teammate-3e09):** the human side of the work

## License

MIT. Use it, change it, make it your own.

[Back to the AI Toolkit for Knowledge Work](../../README.md)
