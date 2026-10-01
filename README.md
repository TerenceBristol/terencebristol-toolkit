# AI Toolkit for Knowledge Work

The skills, prompts and files I use every day for my own work with AI. Free, no email. I don't code for a living, and you don't need to either.

I'm Terence. I've used AI heavily in my work since 2022. Everything here is something I use myself, shared as a starting point so you can make it your own.

YouTube: [Terence | AI for Knowledge Work](https://www.youtube.com/@terencebristol)

---

## What's here

| Kind | What it is | Items |
|------|-----------|-------|
| **Skills** | Instructions Claude follows for a whole task, saved so you can run them again with one command | [/improve](skills/improve/): your Claude Code setup gets better after every conversation |
| **Prompts** | Text you paste into Claude. Most of mine interview you first, so the result fits your work | Coming with the next videos |
| **Sample files** | Made-up files to practise on when you don't want to use your own | Coming with the next videos |
| **Maps** | The diagrams from my videos | Coming with the next videos |
| **Video pages** | One page per video with everything from it in one place | Coming with the next videos |

Every item has its own page with what it does, how to get it, and what changed lately.

---

## How to use these (no coding needed)

You don't need a GitHub account for any of this.

- **Copy a prompt:** open the prompt's file and click the copy button at the top right of the text.
- **Download one file:** open the file and click "Download raw file" (the arrow icon at the top right).
- **Download a set of files:** where an item has several files, it also has a `.zip`. Open the `.zip` and click "Download raw file", then double-click it on your computer to unpack it.
- **Coming from a video?** The link in the description takes you straight to that video's page.

---

## Install the skills in Claude Code

All my skills come as one plugin. In Claude Code, type these two lines one at a time:

```
/plugin marketplace add TerenceBristol/terencebristol-toolkit
/plugin install terencebristol-toolkit@terencebristol
```

Start a new session and type the skill's name, for example `/improve`. You can also just ask Claude to use it ("run the improve skill").

**Getting updates:** when I add a skill or change one, run `/plugin marketplace update terencebristol`. To get updates without thinking about it, type `/plugin`, open the **Marketplaces** tab, pick `terencebristol` and choose **Enable auto-update**.

Prefer a plain copy you can edit? Each skill's page shows how.

---

## Moved here from claude-improve?

This toolkit used to be the `claude-improve` repo. Old links still work.

- The skill file `improve.md` now lives at [`skills/improve/SKILL.md`](skills/improve/SKILL.md).
- The old install step (copy `improve.md` into `~/.claude/commands/`) still works, but new copies go to `~/.claude/skills/improve/SKILL.md`. Or install the plugin above and get updates with one command.
- The full version history is in [`skills/improve/CHANGELOG.md`](skills/improve/CHANGELOG.md).

---

## License

MIT. Use anything here, change it, make it your own.
