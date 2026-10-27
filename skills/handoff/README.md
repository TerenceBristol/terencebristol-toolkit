# /handoff

When a chat gets long, `/handoff` writes a handoff file and a kickoff prompt, so a fresh chat picks up your task exactly where the long one stopped.

**Works in:** Claude Code. The transcript step needs Claude Code's session logs; the rest is written to also work in Cowork (not yet tested there).

---

## Get it

**Option 1: install the toolkit plugin (recommended, easy to update)**

In Claude Code, type these two lines one at a time:

```
/plugin marketplace add TerenceBristol/terencebristol-toolkit
/plugin install terencebristol-toolkit@terencebristol
```

Then start a new session and type `/handoff`. If you already have a different command called `/handoff`, use the full name: `/terencebristol-toolkit:handoff`.

Already have the plugin (for example for `/improve`)? Run `/plugin marketplace update terencebristol` to get `/handoff`. To get the newest version later, run the same line, or switch on auto-update once: type `/plugin`, open **Marketplaces**, pick `terencebristol`, choose **Enable auto-update**.

**Option 2: copy the files (a plain copy you can edit)**

1. Open [`SKILL.md`](SKILL.md) and click "Download raw file". Save it as `~/.claude/skills/handoff/SKILL.md` (make the `handoff` folder first).
2. Open [`scripts/condense_transcript.py`](scripts/condense_transcript.py) and click "Download raw file". Save it as `~/.claude/skills/handoff/scripts/condense_transcript.py` (make the `scripts` folder first).
3. Start a new session and type `/handoff`.

To update, download both files again and replace yours.

Want Claude to walk you through it? Use the [/handoff setup prompt](../../prompts/handoff-setup/).

---

## What it does

Long chats get slower, more expensive and more confused, because Claude re-reads the whole conversation with every message. `/handoff` lets you start fresh without losing the thread:

1. **Writes a handoff file:** the goal, what's done, what's left, the open decisions, and your decisions quoted in your own words.
2. **Saves the approved plan** once, and points to it.
3. **Keeps your exact words:** in Claude Code, a small script turns the chat's session log into a readable transcript of the chat, with your words exact. Elsewhere, Claude quotes your words from the chat.
4. **Writes a kickoff prompt** you paste into the next chat.
5. **Reviews itself:** a fresh helper reads only the handoff, the kickoff and the saved plan, and checks a new chat could really continue from them.

Use it when a chat gets long or when you switch tasks.

---

## Latest change

**1.0.0 (2026-10-27):** first public version. Full history: [CHANGELOG.md](CHANGELOG.md).

---

## Watch the video

[Claude Code Memory and Context: Save Your Limits (Ep. 3)](../../videos/claude-code-memory-ep3.md)

[Back to the AI Toolkit](../../README.md)
