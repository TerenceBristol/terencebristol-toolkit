# /improve: config map and health checks

Read from SKILL.md Step 3 (the config map is the Discovery brief) and Step 4 (the health checks).

## Config map

Discovery catalogs every config file at project and global level, with its purpose, sorted by type and level:
- CLAUDE.md files: project root, project `.claude/`, global `~/.claude/CLAUDE.md`;
- commands and skills (project `.claude/commands/` and `.claude/skills/`, global `~/.claude/commands/` and `~/.claude/skills/`), agents (`.claude/agents/`, `~/.claude/agents/`), project `.claude/rules/`;
- shared references and style or voice files (`shared/` folders, frameworks, guardrails) and the project's reference files;
- settings files (project and global `settings.json` and `settings.local.json`), the hooks they register, the skill each hook names in its header, and any hook test files;
- memory folders, if auto memory is on (`~/.claude/projects/<project-path>/memory/`);
- the follow-ups list, if there is one, and any other instruction-like `.md` file that governs behaviour.

Fallback paths when Discovery fails: the CLAUDE.md files, the `~/.claude/` commands, skills, agents and shared folders, and the project `.claude/` settings files.

### When a helper fails

If Discovery fails or returns nothing, scan the fallback paths above yourself and announce "Discovery agent failed: using fallback config path scan". If the history or audit helper fails, fall back to current-conversation scope, skip the prior-run audit and recurring-pattern checks, and say so. A size-guard report from the history scan is not a failure: it means one analysis helper per session.

## Health checks

Run on the project and global files at every run. They produce the misplaced-content and maintenance cards. Each check gives cards in the usual order and format. Label every size figure an estimate.

- **Size of always-loaded files.** Every CLAUDE.md that loads in the project costs tokens on every call, so measure each in estimated tokens. Estimate: characters divided by about 3, with HTML comments left out (they are stripped before loading): `python3 -c "import re,sys; print(len(re.sub(r'<!--.*?-->', '', open(sys.argv[1], encoding='utf-8').read(), flags=re.S)))" <file>`. Recalibrate the ratio now and then against a `/context` reading. Compare each file with a budget the person sets (for example its measured size plus a few percent headroom); with no budget, flag a file over about 200 lines and say the threshold is a guess. Warning: over budget. Critical: more than 25% over (a guess). Report the estimate, the budget and the three largest sections, because that is where cuts pay off.
- **CLAUDE.md sort.** Every-reply rules, hard limits and facts about the person stay. Procedures and situation rules move to the skill or file that runs them and leave a one-line trigger that names a moment the assistant can see. Project-only lines go to the project file. A section of more than about 20 lines that reads like a procedure is a skill step candidate (a skill costs only its description until it loads). Suggest a reorganisation only when the structure is unclear, not for style.
- **Path-specific rules.** CLAUDE.md lines that apply only to some files or folders ("for `*.test.ts` files", "in API routes") can move to `.claude/rules/` with a path glob, so they load only when the assistant touches those files.
- **Placement, five directions.**
  1. CLAUDE.md to a skill: a section that matters only while one skill runs (it names the skill, or describes a workflow such as brainstorming, reviewing, debugging or planning) moves into that skill. Rules needed while designing or investigating before any skill loads stay in CLAUDE.md, as one line if long; universal rules stay as they are.
  2. Reference or memory files to a skill: a file that holds a procedure, or a rule for one skill's execution, moves into that skill.
  3. A skill to CLAUDE.md: a rule inside a skill about the assistant's behaviour everywhere (not the skill's own procedure) is flagged for promotion. "Present findings one at a time" is skill-internal; "ask with the question picker for decisions" is universal.
  4. CLAUDE.md to a reference file: facts and reference detail that do not change behaviour move to the project reference files.
  5. Between skills: identical or near-identical sections in two skills move to one shared reference file.
- **Skills.** Check project and global skills and commands:
  - overlapping skills, or two descriptions that claim the same moment;
  - skills that grew past their purpose, or a main file over about 2,000 words or 500 lines (rare modes and reference material belong in separate files with "When X, read Y" pointers);
  - stale skills naming files, tools or paths that no longer exist;
  - a project skill with the same name as a global one (intended override or accident?);
  - descriptions: one or two sentences, what it does, then "Use when ..." with the person's real words for the moment; third person; concrete words. Give a suggested rewrite;
  - total description length: when `/context` or `/doctor` shows skills missing from the listing, that is a finding; over about 12,000 characters in total is a warning (a guess). Maintenance type unless the person reports skills not loading.
- **Contradictions across skills** (Critical, both sources cited with path and line): opposite directives; different terms for one concept; different procedures for the same situation ("ask before acting" against "act, then verify"); a skill that overrides CLAUDE.md without saying so.
- **Hook and skill links.** For every registered hook and every skill that names one: the hook's header names its skill and the skill names the hook; the hook's rule list exists where the hook reads it (inside the skill's folder when the rule belongs to a skill); a test file exists. A broken link or missing file is Maintenance; Critical when a blocking hook's rule file is missing. CLAUDE.md text that restates a rule a hook enforces in full shrinks to one line naming the hook.
- **Across levels.** Rules duplicated or contradicting between project and global CLAUDE.md; skills at both levels with different content; reference, memory or learnings content kept at the wrong level (project facts in a global file, cross-project lessons in one project).
- **Stale reference content.** A project reference file, memory file or follow-ups entry that is two or more releases behind the current milestone (the project's feature index, or `git log --oneline -5`), or that describes a finished one-time event (an audit result, a completed retest), is a stale card: remove, or keep as history with its date. A whole config file these checks find stale also counts toward the stale-files line at the end of the run.

## Rule wording

For every proposed line:
- One rule, one reason: say what to do, with a short reason, so edge cases can be judged. "Never" only for hard limits.
- When clarifying a rule, keep its own wording and add the reason in one clause.
- Never escalate "try to" into "always" or "consider" into "must".
- In a CLAUDE.md file, a dated story becomes one block-level HTML comment line right after its rule (stripped before loading; never inside a code block); in skill and agent files, stories are deleted.
- Files read by smaller helper models state their scope and give positive examples, because those helpers follow text literally.
- Add a concrete example when the rule is not self-evident. One clear sentence beats a paragraph.
- A recommended option carries only constraints the evidence supports; one the assistant adds itself is labelled "my addition".

## Dedicated config session

When the arguments ask for a dedicated config session ("full sweep", "comprehensive", "config update", "update the entire repository config", "improve everything", or a skill clean-up session):
- every config file gets the Step 4 checks, and every candidate is grep-checked against CLAUDE.md and the skills;
- the findings page shows every item with its pick, so the person decides each one, never an assumed-approval plan; flagged items go one at a time;
- after their accept, write the execution plan (plan mode where available), then apply in waves of helpers, no two on one file (SKILL.md Step 7).
