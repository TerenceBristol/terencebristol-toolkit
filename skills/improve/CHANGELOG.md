# Changelog

All notable changes to the `/improve` skill are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/).

## [5.0.1] - 2026-08-25

### Fixed
Six clarity gaps in the new historical-scan instructions, caught by a zero-context operability review (a fresh reader executing purely from the file): the History Scan section now restates the mangled `[project-path]` derivation and its existence fallback instead of relying on Load Learnings; the session-UUID derivation from the scratchpad path has a fallback (most recently modified `.jsonl`) at both places it's used; the extract files get a defined location and name (`extract-<session-date>-<session-uuid>.txt` in the session scratchpad) so the size-guard hand-off has a pickup point; the Prior-Improve Cross-Check explicitly recomputes the session window itself (it runs in parallel with History Scan, no hand-off) and explicitly audits ALL logged runs, not the windowed 10; and the legacy date fallback is now explicitly restricted to logs where NO entry has a Scanned-through line (mixed logs use the primary anchor).

## [5.0.0] - 2026-08-25

### Changed
- **BREAKING — Historical window anchored to your last run**: "Historical + current" no longer scans a fixed "5 most recent sessions." It scans the sessions since the last `/improve` run, anchored by a new `Scanned through: <timestamp>, session <uuid>` line each run writes to the project run log — so a morning run's sessions are never re-scanned by an evening run. Capped at 10 sessions per run; if the gap is larger, the skill says what it skipped and offers a follow-up run. First run on a project (no run log): newest 10 sessions, with the remaining history counted and a deeper backfill offered. Legacy day-dated logs fall back to day-granular anchoring with at most a one-time same-day overlap.
- **BREAKING — Full-dialogue semantic extraction**: the history scan now reads both sides of the conversation — your messages AND the assistant's prose replies — and judges feedback by meaning. The keyword filter ("no", "wrong", "perfect", ...) is gone; corrections phrased without trigger words are no longer invisible, and assistant-proposed fixes and techniques now count as lessons.
- **Prior-improve audit reads the run log first**: past runs, their decisions, and changed files come from the per-project learnings run log (all runs, not just recent sessions); session files are only grepped as a log-integrity check within the window, or as full fallback when the log is missing entirely.

### Fixed
- **Tool-result contamination**: session `.jsonl` files store tool results as user-type entries, so the old "extract user messages" instruction could sweep megabytes of tool output into the scan. Extraction now keeps only genuine text blocks (`isMeta` entries and `<command-`/`<system-reminder`/`<local-command` wrappers stripped, assistant `tool_use`/`thinking` excluded). Measured on real data: a 32MB session reduces to ~68KB of dialogue.
- **Run-log date parsing**: anchor dates are regex-extracted (`^### (\d{4}-\d{2}-\d{2})`) and the MAX date wins — headings can carry suffixes (e.g. `2026-08-24b`) and newest-first ordering is not guaranteed.

### Added
- **Coverage statement**: every historical run opens its findings with exactly what was scanned (e.g. "Scanned 3 sessions since the last run (Aug 22–25); nothing older touched") and what was skipped.
- **Learnings visibility**: run start announces what loaded — "Loaded learnings: N project patterns, M previously-rejected items suppressed" — instead of applying learnings silently.
- **Per-session size guard**: if the window's extracted dialogue exceeds ~300KB, analysis splits into one agent per session instead of truncating.

## [4.0.1] - 2026-08-12

### Fixed
- **History scan message type**: session `.jsonl` user messages are `"type":"user"`, not `"type":"human"` — the historical scan script instruction now matches the real format (followed literally, the old wording found nothing).
- **README Example Finding** updated to the v4 compact-list format (recommendation line instead of per-finding Accept/Reject/Modify, which is now the opt-in walkthrough).
- **Stale "always full sweep" wording** in the frontmatter description and intro, which contradicted the v4 scope defaults and the scope-limiting `config audit` argument — now says every run checks all finding categories.
- **"config audit" ambiguity**: clarified that `/improve config audit` invokes the light single-pass scope, and Comprehensive Config Session Mode requires an explicit request for a dedicated session (removed "config audit" from that mode's detection signals).
- **Generalized author-specific examples** (private skill names, milestone-index filename, "RC version" jargon) into generic equivalents; removed a dated anecdote.
- **"CLAUDE.md Quality Standards" hedged** with "or equivalent rules section" everywhere it's scanned — not every CLAUDE.md has that section.
- **README pipeline description** now mentions all three full-scope background agents and the prior-runs audit table; per-project learnings path now explains the directory-name mangling.

## [4.0.0] - 2026-08-12

### Added
- **Two-Level Learnings System**: Learnings are now split by kind. A global file (`~/.claude/improve-learnings.md`) holds cross-project patterns about how you work (presentation preferences, modify signals, scope habits); a per-project file (`~/.claude/projects/<mangled-project-path>/improve-learnings.md`) holds each project's distilled patterns, deferral counters, and date-keyed run log. Both are read at the start of every run and updated at the end.
- **Settled-Pattern Promotion**: Learnings patterns confirmed across ~5+ runs are surfaced as findings proposing promotion into the skill, CLAUDE.md, or settings — then deleted from learnings. Prevents the learnings file from becoming a permanent patch layer that silently overrides the skill.
- **Enforced Size Summarization**: After every save, an actual `wc -l` check — project files over 80 lines are condensed immediately (oldest run entries → Patterns), global stays under ~40 lines.

### Changed
- **BREAKING — Findings presentation default**: Findings are now presented as one compact list in chat (grouped by tier, each with evidence, target file, and recommendation), with AskUserQuestion reserved for items genuinely needing a decision. The previous per-finding one-at-a-time walkthrough remains available on request ("walk me through them").
- **BREAKING — Scope question simplified to 2 options**: "Current conversation only" (default, listed first) and "Historical + current conversation". Config-audit mode is no longer offered in the question — invoke it explicitly with `/improve config audit`.
- **Run entries are date-keyed** (`### YYYY-MM-DD — session signature`), replacing global run counters, which drift and collide across projects.

### Migration
- Your existing `~/.claude/improve-learnings.md` keeps working as the global file. Project-specific content (counters, run history) migrates naturally: each project's file is created on that project's first v4 run. Optionally move project-specific patterns out of the global file by hand.

## [3.2.0] - 2026-06-15

### Added
- **Config Audit Only Scope**: Third scope option — skips conversation analysis entirely, runs only config health checks. Ideal for standalone maintenance from a fresh conversation.
- **Batch Grep Verification Gate**: BLOCKING requirement before presenting delete-as-redundant findings — all proposed deletions must be grep-verified with evidence inline. Files with zero matches get placement options instead.
- **Verify-Before-Removing Gate**: Before executing any removal in Phase 6, re-grep the target destination to catch false-positive audit claims from Phase 4c.
- **Wave-Based Parallel Execution**: For 10+ approved changes in Phase 6, groups changes by file and executes via parallel sub-agents with no-conflict constraint.
- **Promoted-But-Not-Cleaned Detection**: New memory audit sub-check — catches memory files that were promoted to CLAUDE.md but never deleted, using grep verification with evidence.
- **Stale Project Memory Detection**: Flags project-type memories referencing old RC versions or completed one-time events, distinguishing deletable from keepable.
- **Single-Skill Feedback Detection**: Identifies feedback memories specific to one skill's execution context and recommends baking into that skill file.
- **Quality Standards Distribution Analysis**: Classifies CLAUDE.md Quality Standards rules as Universal, Brainstorming-relevant, or Skill-specific, with placement recommendations.
- **Memory File Monitoring**: Size threshold monitoring for MEMORY.md (warning >120 lines, critical >160) and memory file count (warning >50, critical >70).
- **Promotion Cleanup**: When promoting memory → CLAUDE.md, recommends deleting the original memory file in the same finding to prevent duplication.
- **Enhanced Memory Finding Question Format**: Consolidation findings now include grep evidence and specific placement recommendations instead of generic Accept/Reject.
- **Comprehensive Config Session Mode**: New end-of-file section adapting the /improve workflow for dedicated config improvement sessions — full memory audit as dedicated phase, wave execution, plan mode integration.

### Changed
- **Size Thresholds Raised**: CLAUDE.md warning from >100 to >150 lines; critical from >150 to >200 lines (aligns with Anthropic's official recommendation). Character thresholds unchanged.
- **Skill Budget Guidance Enhanced**: Now references `skillListingBudgetFraction` setting, `/doctor` and `/context` commands, and settings.json adjustment instead of generic budget note.
- **Hook Path Quoting**: Added guidance to wrap hook command paths containing spaces as `bash '/path with spaces/hook.sh'` to prevent shell splitting errors.
- **Generalized personal path reference**: Discovery Agent memory path now uses a generic description instead of a hardcoded username.

## [3.1.0] - 2026-05-05

### Added
- **Mandatory Redundancy Verification**: Before flagging a memory file as redundant, the skill now requires grep verification — confirming the rule actually exists in the claimed destination file with matching scope and intent. Prevents false redundancy claims that could lead to lost rules.
- **Consolidate-Then-Clean Workflow**: When merging or removing memory files, the skill now ensures content is integrated into its destination (skill, CLAUDE.md, or another memory file) BEFORE removing the source. Prevents accidental rule loss during cleanup.
- **Placement Recommendation**: Every finding now includes an opinionated target recommendation — whether it belongs in a specific skill file, CLAUDE.md, or memory — with rationale. No more equal-weight menus without guidance.
- **Default to Recommending**: All multi-option presentations now lead with a specific recommendation and rationale, followed by alternatives. The skill expresses a preference rather than deferring every decision to the user.
- **Memory Consolidation Findings in Phase 5**: Consolidation decisions are now presented during the interactive Phase 5 (where you Accept/Reject/Modify), not deferred to Phase 6 execution. You review and approve each consolidation group before anything gets merged or deleted.

## [3.0.0] - 2026-04-22

### Added
- **Self-learning loop**: Reads `~/.claude/improve-learnings.md` before each run and writes acceptance patterns after. The skill adapts over time — deprioritizing finding types you consistently reject and boosting what you accept.
- **Bidirectional content placement audit** with 5 migration directions:
  - CLAUDE.md → Skill files (skill-specific instructions)
  - Memory → Skills (procedural knowledge in memory)
  - Skill files → CLAUDE.md (universal rules buried in skills)
  - CLAUDE.md → Memory (factual content consuming instruction budget)
  - Between skills (duplicated sections)
- **Cross-skill consistency checking**: Detects contradictions across skill files — conflicting directives, overlapping triggers, inconsistent terminology, process conflicts, and skills-vs-CLAUDE.md mismatches
- **Skill budget monitoring**: Tracks total skill description character count against the community-discovered ~16K metadata budget. Warns when approaching the limit where skills become silently invisible.
- **Skill description quality audit**: Checks each skill's description for activation best practices — third-person voice, trigger conditions, appropriate length, specificity
- **CLAUDE.md structural validation**: Light-touch check against the WHAT/WHY/HOW framework
- **Confidence scoring** on all findings (High / Medium / Low) based on signal strength and cross-session recurrence
- **Smarter hook recommendations**: Generates complete hook JSON config with event type detection, ready to paste into settings.json. Includes compliance improvement estimate.
- **Agent failure graceful degradation**: Discovery Agent falls back to hardcoded config paths; History/Prior-Improve agents degrade to current-only scope. Always announces what was skipped.
- **Content Misplacement** as a new finding category (priority 4th, between Promotion and Improvement)

### Changed
- Phase 5 finding format now includes confidence level: `[Tier | Confidence]`
- Phase 6 expanded with application steps for content moves, skill description rewrites, and learnings file updates
- Priority system now has 10 tiers (added Content Misplacement)
- Removed redundant "Contradictions" sub-section (now covered by Cross-Skill Consistency with 5 specific patterns)

## [2.0.0] - 2026-04-14

### Added
- **Scope selection** — choose "Historical + current conversation" or "Current conversation only" before launch, so you can run a quick current-session-only retrospective without waiting for the full history scan
- **8 structured config health sub-checks** (replacing the previous 4 vague bullets):
  - Size thresholds — warns at >100 lines / >20K chars, critical at >150 lines / >40K chars
  - Memory consolidation — detects duplicate/overlapping memory files, stale references, unconverted relative dates
  - Rule extraction — suggests moving file-type-specific CLAUDE.md rules to `.claude/rules/` with path-scoping
  - Skill extraction — flags CLAUDE.md sections >20 lines that should become on-demand skills
  - Skill consolidation — checks all skills (project + global) for overlapping, stale, oversized, or shadowed skills
  - Cross-level analysis — detects duplicates and contradictions between project and global configs
  - Contradictions — within-level conflicts between skills, rules, and CLAUDE.md
  - Structure — organic growth without clear organization
- **Hook promotion** for enforcement gaps — when rules are repeatedly violated, offers "Strengthen rule", "Convert to hook", or "Both", with a follow-up question for hook scope (project, global, or project-local)
- **4 new change types** in Phase 6: hook creation in settings.json, `.claude/rules/` file creation, memory file merging, and skill extraction from CLAUDE.md
- **Prior /improve audit** — shows a verification table of what past `/improve` runs recommended and whether changes actually landed (full scope only)

### Changed
- Discovery Agent now catalogs both project-level AND global-level configs, including settings files and `.claude/rules/`
- Phase 4a offers 3 response options (Strengthen / Convert to hook / Both) instead of just strengthening
- Phase 4b (Progressive Evolution) is now skipped in current-only scope
- Phase 5 audit table is now skipped in current-only scope
- Phase 6 steps renumbered (1-11) to accommodate new change types

## [1.0.0] - 2026-04-05

### Added
- Initial release of the `/improve` retrospective skill
- 6-phase analysis cycle: Discovery, History Scan, Live Analysis, Cross-Reference, Present Findings, Apply Changes
- 3 parallel background agents (Discovery, History Scan, Prior-Improve Cross-Check)
- 9 signal detection categories: corrections, praise, friction, capability gaps, behavioral patterns, targeted feedback, workflow preferences, techniques, user interaction
- 9-tier priority system (Targeted → Critical → Promotion → Improvement → Technique → Maintenance → Reinforcement → New Skill → User Coaching)
- Rule-writing quality standards (NEVER/ALWAYS emphasis, lead with WHY, concrete examples)
- One-at-a-time finding presentation with Accept/Reject/Modify options
- Automatic memory file creation for feedback-type findings
- Summary table of all applied changes
