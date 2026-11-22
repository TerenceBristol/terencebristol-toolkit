# /improve: findings rules

Read from SKILL.md Step 5 before any card is written.

## Breaking rules, homes and wording

**A rule that keeps breaking.** First look for a contradicting example or table row in the files that load together. Then prove the fix before it becomes standard: count the breaches with a script, and check the fix on a fresh run.

**Enforcement gaps.** A broken rule that a script can check is a hook candidate: read `hooks.md`. A judgment rule broken once gets a clearer rule (a short "because", an example, or a move to the file the work reads), not removal. One broken again and again (across sessions, or more than once in this conversation in current-only scope) moves into the skill step where the work happens, or its checkable part becomes a hook. Capitals or a move to the top of a file are not a fix.

**Homes.** Work down this order and stop at the first that fits, because every always-loaded line costs tokens on every call and dilutes the rules around it:
1. a structural fix (a file, a script, a template, a step order);
2. a check or a hook, when a script can see the breach;
3. an edit to the existing rule that covers the case;
4. the owning skill, or a shared reference file when 2 or more skills need it;
5. a project reference file, for facts, reference detail and project context (/improve may update these files);
6. the follow-ups list, for dated or waiting config items (what, when or what to watch, the source), if the person keeps one;
7. CLAUDE.md last, for universal behaviour no earlier home covers.
Recommend one home with its reason; never ask the person where a rule should live.

**Rule wording.** Write every proposed line by the "Rule wording" section of `config-health.md`.

## Intake test for every addition

An added rule needs all five:
1. **Recurring evidence:** seen at least twice. One direct correction is never high confidence; it waits for a second occurrence.
2. **The principle, not the single example.**
3. **The cited moment** in the record (session date and a short quote).
4. **The intake questions:** would it have helped more than this session? What goes wrong without it? Can a structural fix do it, then a check or hook, then an edit to an existing rule? New text comes last.
5. **Pair it with a cut.** An add that raises the always-loaded words names on its `why` the removal it pairs with, or why it earns its place, because always-loaded text tends to grow a little with every run unless each add is weighed against a cut.

Skip findings that are already written and followed.

## Confidence

Shown on each card so the person can judge how closely to read it; it does not change the order. High = seen in 2 or more sessions, or 3 or more signals; Medium = one session, including a single direct correction, or a pattern match without direct evidence; Low = inferred from config structure or best practice. In current-conversation scope, nothing rises above Medium.

## Order of cards

Removals first, then drifted prior accepts, re-surfaced skipped items, targeted, critical (caused errors, repeated corrections, enforcement gaps), recurring patterns, misplaced content, improvements, techniques, maintenance (size, staleness, descriptions), reinforcement, new skill steps, and last, tips on the person's prompting. On the page, the person's calls come first and the assistant's technical picks fold below (`review-page.md`).
