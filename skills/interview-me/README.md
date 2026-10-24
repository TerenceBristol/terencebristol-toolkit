# /interview-me

Before Claude starts on a piece of knowledge work, `/interview-me` gets you both on the same page: it looks things up first, asks you one question at a time with its own recommendation, then agrees the plan with you.

**Works in:** Claude Code. Claude app: not yet tested.

---

## Get it

**Option 1: install the toolkit plugin (recommended, easy to update)**

In Claude Code, type these two lines one at a time:

```
/plugin marketplace add TerenceBristol/terencebristol-toolkit
/plugin install terencebristol-toolkit@terencebristol
```

Then start a new session and type `/interview-me`. If you already have a different command called `/interview-me`, use the full name: `/terencebristol-toolkit:interview-me`.

To get the newest version later, run `/plugin marketplace update terencebristol`, or switch on auto-update once: type `/plugin`, open **Marketplaces**, pick `terencebristol`, choose **Enable auto-update**.

**Option 2: copy the file (a plain copy you can edit)**

1. Open [`SKILL.md`](SKILL.md) and click "Download raw file".
2. Save it as `~/.claude/skills/interview-me/SKILL.md` (make the `interview-me` folder first).
3. Start a new session and type `/interview-me`.

To update, download the file again and replace yours.

---

## What it does

You give Claude a task: a proposal, a strategy memo, a pile of feedback, a plan. Instead of guessing and drafting right away, `/interview-me` works through it with you first:

1. **Looks things up first.** It reads the files, messages and documents you point to, so it only asks you what you alone can decide.
2. **Shows what it found** as a short story, with what it checked and what it couldn't check.
3. **Asks one question at a time, each with a recommendation.** You react to a proposal instead of a blank prompt. Before it recommends adding anything, it asks whether it's worth doing at all. It settles what the work says before how it looks.
4. **Offers outside research** when the answer depends on how others do it.
5. **Agrees the plan.** A simple question gets an answer. Bigger work ends with a plan you approve, a list of everything you asked for and where it stands, and the decisions made along the way.

For a list of things to go through (feedback, comments, review findings), it shows one short bullet per item with its pick, lets you accept the simple ones in one reply, then goes one by one through the rest.

## When to use it

- Before writing something that matters, like a client proposal or a board update.
- When you get a pile of feedback and need to decide what to accept.
- When you redesign something that already exists, like a report, a template or a process.
- Any time Claude's first draft usually misses what you meant.

It's made for knowledge workers: consultants, managers, writers and product managers. It's not for job interview practice.

Inspired by [Superpowers' brainstorming skill](https://github.com/obra/superpowers) (Jesse Vincent) and [Matt Pocock's grill-me](https://github.com/mattpocock/skills).

---

## Latest change

**1.0.0 (2026-10-18):** first public version. Full history: [CHANGELOG.md](CHANGELOG.md).

---

[Back to the AI Toolkit](../../README.md)
