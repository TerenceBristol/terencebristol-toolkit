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

`/improve` starts by asking what to look at: **this conversation only** (the default) or **this conversation plus the sessions since your last run** (up to 10, with a check of what earlier runs recommended). A third mode, `/improve config audit`, checks your setup files without reading any conversation.

| Phase | What happens |
|-------|-------------|
| **Scope** | You pick "this conversation only" or "plus history". |
| **1. Discovery** | A helper maps every setup file in the project and in your global folder: CLAUDE.md, skills, agents, memory, settings and `.claude/rules/`. |
| **2. History scan** | A second helper reads the sessions since your last run (up to 10). It reads both sides of each conversation, strips tool output, and judges your feedback by meaning, not keywords. Every run says which sessions it covered. *(History scope only)* |
| **3. Live analysis** | Reads the current conversation for 9 kinds of signal (below). |
| **4. Cross-check** | Compares what it found with your actual files: rules that exist but keep getting broken, patterns that repeat, files that have grown too big, memory that has gone stale. |
| **5. Findings** | One short list, most important first, each with evidence and a recommendation. Say "walk me through them" to accept, reject or change them one by one. |
| **6. Apply** | Makes only the changes you approved. |

In history scope, up to three helpers run at the same time (discovery, history scan, and an audit of earlier runs that checks whether the changes you accepted really landed). That's why the first findings come quickly.

### The 9 signals it looks for

| Signal | What it means |
|--------|--------------|
| **Corrections** | You corrected what the assistant did |
| **Praise** | You confirmed something worked well |
| **Friction** | Something took several tries |
| **Capability gaps** | You did something by hand that could be automated |
| **Behaviour patterns** | Tone problems, wrong assumptions, over-explaining |
| **Targeted feedback** | Words you typed after `/improve` |
| **Workflow preferences** | Repeated steps the assistant should learn |
| **Techniques** | Approaches that worked and should be written down |
| **Working together** | Gentle suggestions for how you can work better with your assistant |

### How findings are ranked

1. **Targeted:** feedback you typed after the command
2. **Critical:** rules that exist but aren't being followed
3. **Promotion:** patterns seen 3+ times that should become written rules
4. **Misplaced content:** instructions living in the wrong file
5. **Improvement:** direct corrections from the current conversation
6. **Technique:** approaches worth writing down
7. **Maintenance:** files that are too big, contradict each other or are out of date
8. **Reinforcement:** things that work and should stay
9. **New skill:** gaps that could become a new skill or agent
10. **Working together:** suggestions for the human side

### Example finding

```
[Critical | High] Source: 2026-04-28. Rule not being followed.

Rule "ALWAYS use AskUserQuestion for decisions" is in CLAUDE.md
but was broken 3 times in recent sessions.

File: ~/.claude/CLAUDE.md
Proposed: turn it into a hook (the computer enforces it).
Recommendation: turn it into a hook, because the written rule keeps slipping.
```

---

## Files it keeps

`/improve` keeps two small notes files and manages them itself:

- **`~/.claude/improve-learnings.md`** (global): what it has learned about how you like findings and rules written. Read at the start of every run, in every project.
- **`~/.claude/projects/<project-path>/improve-learnings.md`** (per project): that project's patterns and a dated log of runs. It sits in Claude Code's own data folder, never in your project. `<project-path>` is the project's full path with every `/`, space and `.` turned into `-` (for example `/Users/jane/Code/my-app` becomes `-Users-jane-Code-my-app`).

Delete either file any time to start fresh. Patterns confirmed across about 5 runs are offered for promotion into your real setup files and then removed from the notes, so the notes stay small and your setup stays the source of truth.

---

## Works on any project

It finds your setup files on its own, whatever mix you use. It's most useful for assistants whose work isn't code (content, research, planning, YouTube), where the setup is plain English and every improvement shows right away.

---

## Latest change

**5.1.0 (2026-10-01):** the history scan now reads your answers in question boxes, and a do-no-harm check runs before and after changes. Full history: [CHANGELOG.md](CHANGELOG.md).

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
