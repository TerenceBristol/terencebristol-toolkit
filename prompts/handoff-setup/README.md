# /handoff setup prompt

Paste one prompt into Claude Code and it walks you through setting up the /handoff skill, asks you a few questions so it fits your work, and runs your first handoff.

**Works in:** Claude Code. It needs to work with files on your computer, so it won't work in the Claude app's chat.

[Back to the AI Toolkit](../../README.md)

---

## Get it

Click the copy button at the top right of the text below, then paste it into Claude Code.

```
Set up the /handoff skill for me, then try it on this chat.

1. Install it. If I already have the terencebristol-toolkit plugin (for example for /improve) but no /handoff, tell me to type /plugin marketplace update terencebristol, then start a new chat and paste this prompt again. If the plugin isn't installed yet, tell me to type these two lines myself, one at a time, then start a new chat and paste this prompt again:
   /plugin marketplace add TerenceBristol/terencebristol-toolkit
   /plugin install terencebristol-toolkit@terencebristol
   If I'd rather have a plain copy I can edit, download https://raw.githubusercontent.com/TerenceBristol/terencebristol-toolkit/main/skills/handoff/SKILL.md into ~/.claude/skills/handoff/SKILL.md, and the script at https://raw.githubusercontent.com/TerenceBristol/terencebristol-toolkit/main/skills/handoff/scripts/condense_transcript.py into ~/.claude/skills/handoff/scripts/. Ask me before you download anything.

2. Ask me these questions one at a time, each with your recommendation:
   - Where should handoff files live? (Recommend: a handoff/ folder in this project.)
   - One file per task, or one per chat? (Recommend: one per task, so a task's state stays in one place.)
   - What's my time zone? (Read the computer's clock and suggest it.)
   - Is there anything every handoff must carry for my work? (Examples: name who made each decision; keep each client's handoffs in that client's folder.)

3. Save my answers in <handoff folder>/README.md with a line "Confirmed: <today's date>", so the skill never asks them again. If the folder isn't handoff/, also add one line to this project's CLAUDE.md: "Handoff files live in <folder>."

4. Check that Python 3 works here (python3 --version). If it doesn't, tell me the handoff still works, it just quotes my words from the chat instead of from the transcript file.

5. Run /handoff on this chat as a first test, then show me the two files it wrote and tell me how I'd use them: open a new chat and paste the kickoff.
```

## How to use it

1. Open Claude Code in the folder you work in.
2. Paste the prompt and answer one short question at a time.
3. Claude Code asks before it runs a command or changes a file: read it, and say yes when it makes sense.

## What it does

- **Installs /handoff with you:** the toolkit plugin (two lines you type) or a plain copy of the two files.
- **Asks 4 setup questions:** where handoff files live, one file per task or per chat, your time zone, and anything every handoff must carry.
- **Saves your answers** where /handoff reads them, so it never asks again.
- **Runs your first handoff** on the same chat and shows you how to use the kickoff.

## Latest change

**1.0.0 (2026-10-27):** first public version. Full history: [CHANGELOG.md](CHANGELOG.md).

## Watch the video

[Claude Code Memory and Context: Less Is More (Ep. 3)](../../videos/claude-code-memory-ep3.md)

[Back to the AI Toolkit](../../README.md)
