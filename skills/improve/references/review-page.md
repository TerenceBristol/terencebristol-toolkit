# /improve: the findings page

Read from SKILL.md Step 6 when there are more than four cards. One local HTML page holds every card, so the person can read the whole round at once and accept the picks in one answer.

## Build it

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
     "words": -42, "pick": "accept", "plan": false, "call": "tech", "why": "one home per rule"}
  ]
}
```

   (Format only; the values are an example.) Fields: `type` is remove, move, edit or add; `before` and `after` are the exact text, word for word (for a move, `after` names the new file and line); `moment` cites the session date and a short quote; `evidence` holds the grep proof; `words` is the change in always-loaded words (0 for files that do not always load); `pick` is accept, skip or flag (the assistant's pick, preset on the page); `plan: true` marks a new hook, a new skill or a multi-file restructure; `why` is the one-line reason; `call` is "you" or "tech" and puts the card in a group on the page. Set `call` on every card: "you" when the change alters what the person sees, does or decides (a new step, question or habit, wording they read); "tech" when it is housekeeping they never see (stale paths, duplicates, pointers, size trims, wording fixes). A card without `call` counts as "tech" only when it is a remove, edit or move with High confidence and an accept pick. `size.after` assumes every accept pick is taken.
2. Render: `python3 <this skill's folder>/scripts/review_page.py <json>`. It writes the `.html` beside the JSON and prints the path. The page lists every card on the left: the person's calls first, then the technical picks (folded when more than 5), removals first in each, the others in your order. The chosen card shows in full on the right: headline, the marked change with removed words struck red and added words green, then the clean After text they approve; a "When" bullet from `moment`; the pick and why; Checked, tier, confidence and words in a Details fold. The net size effect, the number of cards that need a plan and, when the always-loaded words grow, an adds line sit on top. `why` and `evidence` may be lists (shown as bullets). Optional per card: `headline` (a one-line takeaway, else `title`). If the layout files next to the script can't load, a simpler stacked page renders with the same answer line.
3. Open the page in the browser or a side pane, and give its path in chat.

**No Python?** Build the page yourself as one self-contained `.html` file beside the JSON (no outside scripts, styles or fonts; escape all card text). On top: the title, the coverage line, the card count by type (remove, move, edit, add), the net size effect (before, after, change), due items, notes, and one line: "Your accept approves only the edits shown word for word; cards marked 'needs a plan' go into a plan first." Then the cards, the person's calls first and the technical picks below, removal cards first in each and the rest in your order. Each card shows its id, type, tier, confidence, file, title, the before and after text word for word (removed words red, added words green), the moment, the evidence, the word change, the reason, a "needs a plan" badge when `plan` is true, and a pick control (accept, skip, flag) preset to `pick`, with a short note box for a flag. Add the "Copy my answer" button below.

## The answer

A **"Copy my answer"** button copies one line built from the picks, and the same line also shows in a visible text box in case the browser blocks copying, for example `/improve page answer: accept all picks as shown.` or `/improve page answer: accept F1, F2; skip F4; flag F3 (why this file?).` Ask one question in the same turn as the chat summary (the question picker if there is one, otherwise plain text): "Accept all picks as shown (Recommended)" or "I changed or flagged cards (paste the page answer)".

- The person's accept approves the text edits shown word for word, nothing else. A card with `plan: true` goes into one plan after the accept.
- Each flagged card gets its own question, one at a time, recommended option first.
