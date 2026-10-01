---
name: improve
description: Review the current conversation and recent session history to suggest improvements to the project's configuration — CLAUDE.md, skills, frameworks, memory, agents. Checks all finding categories every run. Arguments add extra weight to specific areas. Works on any repo structure.
compatibility: "Designed for Claude Code"
---

# Retrospective

Review conversation + recent history, cross-reference against config files, present improvement suggestions as a compact findings list with per-item recommendations.

**Announce:** "Starting retrospective..."

**Arguments = targeted feedback.** Every run still checks all finding categories; args get highest priority but don't narrow the coverage. Exception: the reserved argument `config audit` selects config-audit scope (see Scope Selection). Works mid-conversation or end-of-session.

## Load Learnings

Before scope selection, read BOTH learnings files if they exist:

1. **Global learnings** — `~/.claude/improve-learnings.md`: cross-project patterns about how the user likes /improve and rule-writing to work (presentation format, scope habits, rule-style modify signals). Applies in every project.
2. **Project learnings** — `~/.claude/projects/<mangled-project-path>/improve-learnings.md`: this project's distilled patterns, deferral counters, and date-keyed run log. Derive `<mangled-project-path>` by taking the project's absolute path and replacing every `/`, space, and `.` with `-` (e.g. `/Users/jane/Code/my-app` → `-Users-jane-Code-my-app`) — the same directory Claude Code uses for this project's session files. If the computed directory doesn't exist, list `~/.claude/projects/` and match by project name before creating anything.

Apply what you load:

- **Deprioritize** finding types consistently rejected across runs
- **Boost** categories consistently accepted
- **Adapt** rule-writing style based on modify signals (e.g., if user repeatedly softens NEVER to Avoid, propose softer language for non-critical rules)
- If either file doesn't exist, proceed normally — missing files are created at the end of this run
- **Announce what loaded** in one line before scope selection: "Loaded learnings: N project patterns, M previously-rejected items suppressed, run log through YYYY-MM-DD" (or "No learnings files yet — first run for this project"). The learnings mechanism must be visible, never silent.

## Scope Selection

Before launching any agents, ask the user:

**Question:** "What scope should this retrospective cover?"

**Options (AskUserQuestion):**
- **Current conversation only (default)** — Analyze only this session's patterns and feedback
- **Historical + current conversation** — Sessions since the last /improve run (max 10, anchored via the project run log; newest 10 if no run log exists), prior-run audit, plus current conversation analysis

Store the answer as the `scope` for the rest of the skill.

**Config audit mode is argument-invoked, not offered in the question.** When the user runs `/improve config audit` (or explicitly asks for a standalone config health scan), skip the scope question and set scope = "Config audit only": no conversation analysis — full config health scan (memory consolidation, CLAUDE.md bloat, content placement, skill consistency). Best run from a fresh conversation for standalone maintenance. This is a single-pass scan; only escalate to the heavier Comprehensive Config Session Mode (end of this skill) when the user explicitly asks for a dedicated config improvement session.

## Phase 1 & 2: Discovery + History Scan (Background, Parallel)

**If scope = "Historical + current conversation":** Launch ALL agents in background simultaneously (History Scan covers sessions since the last /improve run, max 10), then immediately proceed to Phase 3.

**If scope = "Current conversation only":** Launch only the Discovery Agent in background, skip History Scan and Prior-Improve Cross-Check agents entirely, then immediately proceed to Phase 3. Announce: "Launching discovery agent (current conversation scope)."

**If scope = "Config audit only":** Launch only the Discovery Agent in background, skip History Scan, Prior-Improve Cross-Check, AND Phase 3 (Current Conversation Analysis) entirely. Proceed directly to Phase 4 (Cross-Reference & Categorize). Announce: "Running config-only audit — skipping conversation analysis."

### Discovery Agent (Explore, background — always runs)

Prompt the agent to search for and catalog ALL config-like files at BOTH project and global levels:
- CLAUDE.md (project root, project .claude/, AND global ~/.claude/CLAUDE.md)
- .claude/commands/ and .claude/skills/ directories (BOTH project-level AND global ~/.claude/commands/)
- .claude/agents/ directory
- .claude/rules/ directory (project-level)
- Shared frameworks, guardrails, style guides (shared/, frameworks/, etc.)
- Memory files at BOTH ~/.claude/projects/[project-path]/memory/ AND the user's global-level memory directory (typically ~/.claude/projects/-[home-dir]/memory/)
- Settings files: project .claude/settings.json, .claude/settings.local.json, global ~/.claude/settings.json, ~/.claude/settings.local.json
- Voice/brand files (vault/, brand/, etc.)
- Any other instruction-like .md files governing behavior

Return a "config map": list of files with purpose, organized by type AND level (project vs global).

### History Scan Agent (general-purpose, background — full scope only)

Prompt the agent to:

1. **Determine the session window (anchored to the last /improve run):**
   - `[project-path]` is the SAME mangled derivation defined in Load Learnings (absolute path with every `/`, space, and `.` replaced by `-`); if the computed directory doesn't exist, list `~/.claude/projects/` and match by project name — include this rule in the agent's prompt.
   - Read the per-project learnings file's `## Run Log`. Primary anchor: the latest `Scanned through: <ISO timestamp>, session <uuid>` line across entries. Window = `.jsonl` session files in `~/.claude/projects/[project-path]/` modified strictly AFTER that timestamp, excluding that entry's session UUID and the current session.
   - **Legacy fallback** — applies ONLY when NO entry has a Scanned-through line (a mixed log with the line in recent entries uses the primary anchor): regex-extract dates from entry headings (`^### (\d{4}-\d{2}-\d{2})` — headings can carry suffixes like `2026-08-24b`, and newest-first ordering is NOT guaranteed) and take the MAX date; window = files modified on/after that date. A one-time same-day overlap is accepted; it disappears once the first run under this version writes a timestamp.
   - **Current-session exclusion:** derive the current session's UUID from the scratchpad directory path (its last path segment before `/scratchpad`) and exclude that `.jsonl`. Fallback if no scratchpad path is available: treat the most recently modified `.jsonl` (the one actively growing) as the current session.
   - Order newest first, **cap at 10**.
   - **No run log / no learnings file:** window = the 10 newest sessions. Report the total session count so the main conversation can state how much history remains unscanned and offer an opt-in backfill run.
   - **Gap exceeds the cap:** scan the newest 10 and report the count and date range of the unscanned remainder.

2. **Extract the dialogue — both speakers, tool and system noise stripped:**
   - Write a bash script using `jq` per session file (session timestamps are UTC: convert the run-log anchor to UTC before comparing):
     - User turns: entries with `.type=="user" and (.isMeta != true)`: keep string content as-is; for array content keep ONLY `text` blocks. This excludes tool_result blocks, which are ALSO stored as user-type entries (a naive "user messages" extraction floods the scan with tool output; session files run to tens of MB). Then drop extracted texts that START with system-injected wrappers: `<command-`, `<system-reminder`, `<local-command`, `<task-notification` (skill expansions and reminders arrive as user-type text and are noise). Before dropping a `<command-` text, extract its `<command-args>` content (when non-empty) as a `USER-CMD <command-name>:` line: the user's main request often sits there, typed after a slash command, and a plain drop hides it.
     - Assistant turns: entries with `.type=="assistant"` — keep ONLY `text` blocks (no `tool_use`, no `thinking`).
     - Answers and plan rejections: ALSO keep tool_result text whose `tool_use_id` belongs to an `AskUserQuestion` or `ExitPlanMode` tool_use in the same file (collect those ids first), prefixed `USER-ANSWER:`. Never match on the text alone: a Read of an older transcript also contains `The user answered:`, and text matching labels a whole earlier transcript as the user's answers. The user's picks and typed "Other" answers live only in those tool_result texts; without them the scan reports false findings and misses corrections.
   - Prefix each block `USER:` / `ASSISTANT:`, save one extract file per session to the session scratchpad directory, named `extract-<session-date>-<session-uuid>.txt` — a defined location so the size-guard hand-off (one analysis agent per session) can pick the files up.
   - Typical yield: a multi-MB session reduces to under ~150KB of dialogue.

3. **Analyze semantically — NO keyword filter:**
   - Read the extract files in full and judge by meaning: corrections, praise, friction, capability gaps, techniques or fixes the assistant proposed that worked, repeated workflows. Assistant-side lessons count — the skill's purpose is lessons from the conversation, wherever they came from.
   - **Size guard:** if combined extracts exceed ~300KB, do not analyze in one pass — return the extract file list so the main conversation can launch one analysis agent per session. Never truncate silently.
   - Tag findings with session date + brief context quote; note recurring patterns across 2+ sessions (promotion candidates).

4. **Return:** categorized findings with source citations (concise summaries, not raw data), PLUS a coverage block: sessions scanned (count + date range), sessions excluded and why (cap overflow / no run log), and total unscanned history if this is a first run.

### Prior-Improve Cross-Check Agent (general-purpose, background — full scope only)

Launch this as a 3rd background agent in parallel with Discovery and History Scan. Its job: audit what prior `/improve` runs recommended and whether their accepted changes actually landed.

**Primary source = the per-project learnings `## Run Log`** — every dated entry lists scope, acceptance decisions, and changed files/rules. Build the list of past runs from it — ALL logged runs, deliberately NOT limited to the History Scan's session window or its cap of 10; the audit and the scan cover different populations. Then:

1. **For each logged Accepted change**, verify it actually landed:
   - Read the target file mentioned in the log entry.
   - Grep for the key phrase / rule text that was supposed to be added.
   - Mark as **Verified Implemented** (key text present), **Drifted** (file exists but text missing or modified), or **Missing** (target file doesn't exist).
   - Depth: verify all changes from runs since the last audit, plus a sample of older ones.

2. **For each Skipped / Rejected recommendation**, flag for re-surfacing:
   - Original date + what was recommended and why declined (if logged)
   - Whether the underlying friction has recurred since (cross-reference with current History Scan signals)
   - Respect the learnings file's "rejected, don't re-surface" patterns — those stay suppressed.

3. **Log-integrity check:** grep the windowed session files for `/improve` or `/terencebristol-toolkit:improve` invocations (the plugin install can show either name) with no matching run-log entry → report "unlogged runs" as a finding. This agent runs in parallel with History Scan and receives no hand-off — recompute the window yourself using the History Scan section's rules (Scanned-through anchor, exclusions, cap 10). Fall back to full session-grep reconstruction (extract Changes Applied tables / AskUserQuestion decisions from the .jsonl files) ONLY if the learnings file is missing entirely.

Return a structured report:
- **Prior `/improve` runs:** N (list dates)
- **Verified implemented:** X (no re-action needed — surface to user for confidence/audit trail)
- **Accepted but drifted/missing:** Y (needs re-application)
- **Previously skipped but still signaling:** Z (re-surface as current-run findings)

Keep total output under 400 words. Cite session dates and target files.

## Phase 3: Current Conversation Analysis (Foreground)

**If scope = "Config audit only":** Skip this phase entirely.

**Announce:** "Analyzing current conversation for patterns, feedback, and techniques..."

Analyze the conversation already in context for:

| Signal | What to Look For |
|--------|-----------------|
| **Corrections** | User corrected behavior, said "no", "don't", "stop", asked to redo |
| **Praise** | User confirmed approach, said "yes", "perfect", accepted without pushback |
| **Friction** | Multiple attempts, confusion, back-and-forth to get it right |
| **Capability gaps** | User did things manually, asked for something assistant couldn't do |
| **Behavioral patterns** | Tone issues, over/under-explaining, wrong assumptions |
| **Targeted feedback** | Arguments passed to /improve — HIGHEST PRIORITY |
| **Repeated workflows** | Multi-step manual processes that could become a skill |
| **Techniques discovered** | Novel approaches that worked well — new methods, clever tool usage |
| **User interaction patterns** | User prompting styles that led to better/worse results |

**Low-signal:** If minimal feedback in current conversation, say "No significant findings from this session" and proceed to history/config findings.

## Phase 4: Cross-Reference & Categorize

**Announce:** "Cross-referencing findings against config files..."

Wait for background agents to complete.

### Agent Failure Handling

After waiting for agents to complete, validate each result before proceeding:

**Discovery Agent (critical path):**
- If it fails or returns empty: fall back to hardcoded scan of known config paths directly in foreground:
  - `~/.claude/CLAUDE.md`, `~/.claude/commands/`, `~/.claude/skills/`, `~/.claude/agents/`
  - `.claude/settings.json`, `.claude/settings.local.json`
  - `~/.claude/projects/[project-path]/memory/`
- Announce: "Discovery agent failed — using fallback config path scan"

**History Scan / Prior-Improve agents (optional):**
- If they fail: gracefully degrade to current-conversation-only scope
- Announce: "History scan agent returned no results — skipping cross-session analysis for this run"
- Skip Phase 4b (Pattern Promotion) and Prior-Improve audit display
- A size-guard overflow report from History Scan is NOT a failure: launching one analysis agent per session is the required response, never truncation or degradation

**Key principle:** Never silently proceed with incomplete data — always tell the user what was skipped and why.

Then read each config file from the config map.

### 4a: Enforcement Gap Detection

For each existing rule in config files, check if the current conversation shows it being violated.

- If the rule was violated once: suggest strengthening (emphasis, position, examples) — not removal
- If the rule shows a pattern of repeated violation (across sessions in full scope, OR multiple times within the current conversation in current-only scope): suggest **converting to a hook** instead — hooks are deterministic enforcement, while CLAUDE.md instructions are probabilistic (~80% compliance)

When suggesting "convert to hook", **generate the complete implementation**:

- Detect the right hook event based on rule type:
  - `PreToolUse` with `Bash` matcher: for command gating rules
  - `PreToolUse` with specific tool matcher: for tool-specific rules
  - `PostToolUse`: for validation after tool execution
  - `Notification`: for reminders and announcements
- Generate the actual hook JSON config ready to paste into settings.json
- Include the shell command/script that enforces the rule
- Note: "This rule is currently advisory (~80% compliance as a CLAUDE.md instruction). As a hook, it becomes 100% deterministic."

**Hook config template (for reference during generation):**
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'HOOK_SCRIPT_HERE'"
          }
        ]
      }
    ]
  }
}
```

**Path quoting:** Before generating any hook command, check if the project path contains spaces. If yes, wrap the script path: `bash '/path with spaces/hook.sh'` instead of bare `/path with spaces/hook.sh`. Bare paths with spaces break when the shell splits them into separate arguments.

When presenting enforcement gap findings in Phase 5, offer three options:
- "Strengthen rule" — rewrite with NEVER/ALWAYS emphasis, move to top of file
- "Convert to hook" — create a hook that enforces the rule deterministically. Include the generated JSON config in the finding. Follow up with a second AskUserQuestion: "Which scope should this hook be configured at?" with options: "Project (.claude/settings.json)", "Global (~/.claude/settings.json)", "Project local (.claude/settings.local.json)"
- "Both" — strengthen the rule AND add a hook as backup enforcement

### 4b: Progressive Evolution (Pattern Promotion) — full scope only

**Skip this sub-phase entirely in current-only scope** (requires cross-session history).

When history scan shows the same feedback across 2+ sessions, suggest PROMOTING:
- Memory file → CLAUDE.md rule
- Buried rule → top of CLAUDE.md with NEVER/ALWAYS emphasis
- Implicit pattern → explicit documented rule with examples
- Soft guideline → hard rule with enforcement language

**Promotion Cleanup:** When suggesting a memory → CLAUDE.md promotion, ALSO include a recommendation to delete the original memory file in the same finding. Present both actions together: "Promote rule X to CLAUDE.md Quality Standards AND delete the original memory file [path]." This prevents the duplication pattern where promoted rules exist in both locations.

### 4c: Config Health & Consolidation

Run ALL sub-checks against BOTH project-level and global-level configs from the Discovery Agent config map.

#### Size Thresholds
Measure CLAUDE.md (both project and global) line count and character count.
- **Warning:** >150 lines or >20K characters
- **Critical:** >200 lines or >40K characters (Anthropic officially recommends under 200 lines per CLAUDE.md; academic research confirms linear compliance decay with instruction count)
- Also measure MEMORY.md line count — **Warning:** >120 lines (~60% of 200-line truncation limit), **Critical:** >160 lines (~80%). Secondary: flag if >50 memory files in a single project's memory directory, Critical >70 files.

#### Memory Consolidation
- Read all memory files and group by topic similarity
- Flag duplicates or heavily overlapping files (e.g., two feedback files covering the same rule) — recommend merging
- Flag memory files with stale references: files, functions, or features mentioned in the memory that no longer exist in the codebase
- Flag memory files with relative dates that were never converted to absolute

#### Cross-Reference Memory vs CLAUDE.md (Promoted-But-Not-Cleaned)

For each feedback-type memory file, grep CLAUDE.md (its Quality Standards section, or equivalent rules sections) for the key phrase from the memory's core rule.
- If CLAUDE.md contains the same rule with matching scope and intent: flag memory as **redundant (already promoted)**
- Present with grep evidence: "This memory was promoted to CLAUDE.md line N but the original was never cleaned up"
- Recommend deletion of the memory file (the CLAUDE.md version is authoritative)

This catches the pattern where auto-memory or a prior /improve run promoted a rule to CLAUDE.md but never deleted the original memory file.

#### Stale Project Memory Detection

For each project-type memory file:
1. Check if the memory references a specific release version or milestone
2. Compare against the current milestone (from the project's milestone/feature index doc if one exists, or `git log --oneline -5`)
3. If the memory's context is 2+ release versions behind current: flag as **potentially stale**
4. Check if the memory describes a completed one-time event (audit result, retest completion, deployment verification) vs an ongoing decision or constraint
5. Flag completed events as "stale — recommend deletion" and ongoing decisions as "historical reference — recommend keeping or merging with similar memories"

#### Mandatory Redundancy Verification

When flagging a memory file as redundant because "the rule already exists in [skill/CLAUDE.md]", you MUST:
1. grep the target file for the key phrase from the memory
2. Confirm the match covers the same scope and intent (not just similar wording)
3. Present the grep evidence to the user: "Verified: [skill] line N contains [matched text]"

NEVER claim redundancy without grep verification. False redundancy claims waste user trust and can lead to lost rules.

#### Consolidate-Then-Clean Workflow

When finding redundant or overlapping memory files:
1. First identify WHERE each rule should live (skill, CLAUDE.md, or memory) using the Placement Recommendation logic
2. For rules that belong in a skill: propose integrating them into the skill FIRST
3. For rules that belong in CLAUDE.md: propose adding them there FIRST
4. Only AFTER integration is confirmed → remove the original memory file
5. Never remove a memory file without first ensuring its content lives somewhere authoritative

This prevents rule loss during cleanup.

#### Rule Extraction
- Scan CLAUDE.md for file-type-specific or path-specific instructions (patterns like "for *.test.ts files", "in API routes", "when editing components/", etc.)
- Suggest migrating these to `.claude/rules/` with path-scoping globs in frontmatter
- Rules only load when Claude touches matching files, reducing always-on context cost

#### Skill Extraction
- Flag CLAUDE.md sections longer than ~20 lines that read like procedures or multi-step workflows
- Suggest converting to skills (on-demand loading: ~100 tokens metadata cost vs full content always in context)
- Good candidates: step-by-step processes, detailed how-to instructions, decision trees

#### Skill Consolidation
- Check ALL skills at both project (`<project>/.claude/commands/`, `<project>/.claude/skills/`) and global (`~/.claude/commands/`) levels
- Flag overlapping skills: two skills that cover similar functionality or could be merged
- Flag oversized skills: skills that have grown beyond their original purpose
- Flag stale skills: skills referencing files, APIs, or patterns that no longer exist in the codebase
- Flag shadowed skills: a project skill with the same name as a global skill (intentional override or accidental?)

#### Cross-Skill Consistency

After reading all skill files from the Discovery Agent, review them holistically for contradictions. Check these 5 patterns:

- **Conflicting directives:** One skill says "ALWAYS do X" while another says "NEVER do X" or "avoid X"
- **Overlapping trigger conditions:** Two skills with descriptions claiming the same activation context (e.g., both say "Use when debugging")
- **Inconsistent terminology:** Skills using different terms for the same concept (e.g., "sub-agent" vs "task" vs "background agent")
- **Process conflicts:** Skills prescribing different procedures for the same scenario (e.g., one says "ask before acting" while another says "act then verify")
- **Skills vs CLAUDE.md:** CLAUDE.md establishes a rule but a skill contradicts or overrides it without acknowledgment

Present contradictions as Critical-tier findings with both sources cited (file paths + relevant lines).

#### Content Placement Audit

#### Quality Standards Distribution

Scan CLAUDE.md's Quality Standards section (or equivalent rules section, if present) specifically. Classify each rule as:
- **Universal** — applies across all tasks and skills (e.g., "ALWAYS use AskUserQuestion for decisions")
- **Brainstorming-relevant** — needed during design/conceptualization phases before specific skills load (e.g., "Complete investigation before proposing ticket structure")
- **Skill-specific** — only relevant during a specific skill's execution (e.g., "Read service code before designing end-to-end tests" applies only while a testing skill is running)

For skill-specific rules: recommend moving to the skill file if not already present, or removing from CLAUDE.md if already in the skill.
For brainstorming-relevant rules: recommend keeping in CLAUDE.md but shortening to a one-liner if verbose.
For universal rules: keep as-is.

**Classification heuristic:** A rule is brainstorming-relevant if it guides design decisions or investigation approach before a specific skill activates. A rule is skill-specific if it only applies during one skill's execution and would never be needed outside that context.

Check 5 directions for misplaced content:

**Direction 1: CLAUDE.md → Skill Files**
- Scan CLAUDE.md for sections that reference specific skills by name
- If a section only applies when a specific skill is active, flag it: "This guidance only matters during [skill] — consider moving it into the skill file itself"
- **Secondary detection:** also flag sections describing procedures only relevant during a specific workflow type (brainstorming, reviewing, debugging, planning) even without a skill name mention — these are implicitly skill-specific

**Direction 2: Memory → Skills**
- Scan memory files for entries with type `feedback` or `project` that contain multi-step procedures, decision trees, or workflow descriptions
- If a memory file reads more like a how-to than a fact, flag it: "This memory contains procedural knowledge — consider converting to a skill"
- **Single-skill feedback detection:** For each feedback memory, determine if it contains a rule specific to ONE existing skill's execution context (e.g., a rule about how a ticket-writing skill should handle red flags, or how a testing skill should handle autonomous mode). If so, recommend baking it into that skill file and deleting the memory. Present: "This feedback rule is specific to [skill] — recommend integrating into [skill file path] and deleting the memory."

**Direction 3: Skill Files → CLAUDE.md**
- Scan each skill for universal behavioral rules — rules about general Claude behavior across sessions/tasks
- **Only flag rules that apply universally**, NOT rules about what to do within the skill's own procedure. Example: "ALWAYS present findings one at a time" is skill-internal (don't flag), while "ALWAYS use AskUserQuestion for decisions" is universal (flag)
- If found: "This rule in [skill] applies universally — consider promoting to CLAUDE.md"

**Direction 4: CLAUDE.md → Memory**
- Scan CLAUDE.md for factual/reference content that isn't a behavioral instruction (project facts, external system pointers, user preferences that don't change behavior)
- These are better as memory entries — they persist across sessions but don't consume always-on instruction budget

**Direction 5: Between Skills**
- If two skills share identical or near-identical sections (copy-pasted patterns), flag for extraction into a shared reference or CLAUDE.md rule

#### Skill Budget Monitoring

Calculate total character count across ALL skill `description` fields (from frontmatter of all skill/command files at both project and global levels).

Skill metadata uses a fraction-based budget (default: `skillListingBudgetFraction` = 0.01 in settings, ~1% of context baseline). Skills exceeding the budget are silently dropped from the system prompt. Run `/doctor` or `/context` to verify which skills are visible. If skills are being dropped, suggest adding `"skillListingBudgetFraction": 0.03` to settings.json. **Note: exact budget mechanics are subject to change with Claude Code updates.**

- **Warning:** >12K chars (~75% of estimated budget)
- **Elevated:** >15K chars (~94% of estimated budget)
- If over warning: list all skills sorted by description length, suggest compression targets (ideal: 130 chars per description)
- If over elevated: identify which skills are likely invisible and suggest investigation
- **Always present as Maintenance-tier** regardless of threshold — this is informational monitoring based on unofficial data. Only escalate to Critical if the user reports actually experiencing invisible skills.

#### Skill Description Quality Audit

For each skill, check its description against activation best practices:

- **Third person?** ("Processes files" not "I process files" or "You should use this to...")
- **Trigger conditions?** ("Use when..." or "Triggers when...")
- **Appropriate length?** (130-263 chars ideal range)
- **Specific enough?** (has concrete keywords, not vague "helps with things")

Research showed activation rates range from 20% (bad description) to 90% (optimized). Present as Maintenance-tier findings with suggested rewrites.

#### CLAUDE.md Structural Validation

Check if CLAUDE.md sections follow the WHAT/WHY/HOW framework:
- **WHAT**: Project context, tech stack, repo structure
- **WHY**: Principles, conventions, anti-patterns
- **HOW**: Workflows, commands, operational procedures

Flag sections that mix categories (a HOW section buried in WHY context). Light-touch — suggest reorganization only if structure is genuinely unclear, not for stylistic preference. Present as Maintenance-tier findings.

#### Cross-Level Analysis
- Check for duplicated rules between project and global CLAUDE.md
- Flag contradictory instructions across levels (project rule says X, global rule says Y)
- Flag memory files that belong at the other level (e.g., project-specific feedback stored in global memory, or cross-project feedback stored in project memory)
- Flag skills that exist at both levels with different content

#### Structure
- Files grown organically without clear organization?
- Sections in CLAUDE.md that belong in different files?

### 4d: Categorize All Findings

| Category | When to Use | Priority |
|----------|-------------|----------|
| **Targeted** | From user's explicit /improve args | 1st |
| **Critical** | Caused errors, repeated correction, enforcement gaps | 2nd |
| **Promotion** | Recurring cross-session pattern needing stronger rule | 3rd |
| **Content Misplacement** | From Content Placement Audit — content living in wrong config layer | 4th |
| **Improvement** | Enhancement to existing rules/skills/behaviors | 5th |
| **Technique** | Novel approach that worked — document for reuse | 6th |
| **Maintenance** | Config health: bloat, contradictions, staleness, budget, descriptions | 7th |
| **Reinforcement** | Worked well — strengthen existing documentation | 8th |
| **New Skill** | Repeated pattern that could become a dedicated skill | 9th |
| **User Coaching** | Gentle suggestion for better user-AI interaction | Last |

Skip findings that are already documented AND being followed.

### Confidence Scoring

Assign a confidence level to every finding as a secondary axis:

| Level | Criteria |
|-------|----------|
| **High** | 3+ supporting signals, or recurrence across 2+ sessions, or direct user correction |
| **Medium** | 1-2 signals from current session, or pattern match without direct evidence |
| **Low** | Speculative — inferred from config structure or best practices, no direct user signal |

**Scope note:** In current-only scope, "recurrence across 2+ sessions" is unavailable. Session-based signals cap at Medium unless there's a direct user correction.

Confidence doesn't change priority order (Critical still beats Improvement regardless of confidence), but helps the user decide scrutiny level — high confidence findings can be accepted faster, low confidence ones deserve more thought.

### Placement Recommendation

For each finding, recommend the optimal target based on scope:
- If the finding is a procedural rule that only applies during a specific skill's execution → target that skill file, not memory
- If the finding applies across 2+ skills but isn't universal → CLAUDE.md (Quality Standards or equivalent rules section)
- If the finding is a fact or reference → memory file
- ALWAYS recommend a specific placement with rationale. Never present equal-weight options without a recommendation.

**Proactively recommend, never ask the user to decide.** When a new pattern or preference is discovered, state WHERE it belongs (memory file, specific skill, or CLAUDE.md) with reasoning. Don't ask "should this be in memory or a skill or CLAUDE.md?" Rubric: **Memory file:** user preferences, behavioral feedback, project-specific context that applies across skills. **Skill file:** workflow-specific rules that only matter during that skill's execution. **CLAUDE.md:** universal rules that affect all interactions (quality standards, routing logic, execution rules). **Both memory + skill:** when a rule is broadly applicable but has one skill where enforcement matters most.

## Phase 5: Present Findings

**Announce:** "Found N findings across M categories. Presenting the full list, most impactful first."

### Rule-Writing Quality Standards

All proposed rule changes MUST:
- Start critical rules with **NEVER** or **ALWAYS**
- Lead with **WHY** so edge cases can be judged
- Use precise language: "try to" → "always", "consider" → "must"
- Include a concrete example when not self-evident
- Keep concise — one clear sentence beats a paragraph

### Default to Recommending

When presenting findings with multiple options (Accept/Reject/Modify, or placement choices), ALWAYS lead with a specific recommendation and rationale. Example:
- Instead of: "Should we add to CLAUDE.md or keep as memory?"
- Say: "I recommend CLAUDE.md because [rationale]. [Options: Accept recommendation / Keep as memory / Modify]"

The user values opinionated recommendations over equal-weight menus. Present the recommendation first, then the alternatives. A recommended option may only carry constraints the session evidence supports; any constraint the assistant adds itself is labelled 'my addition' in the option text (otherwise an unrequested constraint rides into a plan inside a Recommended option, and the user has to ask where it came from).

### Memory Consolidation Findings (present during Phase 5, not Phase 6)

When Memory Consolidation in Phase 4c identifies redundant files:
- Present the consolidation analysis as findings in Phase 5 (in the compact findings list, or per-finding if the user opted into the walkthrough)
- Include: which files are redundant, WHERE each rule should be integrated, and what will be removed
- Get user approval for each consolidation group before proceeding — consolidations always count as decisions needing explicit user input
- Phase 6 then EXECUTES the approved consolidations (integrate + delete)

Do NOT defer consolidation decisions to Phase 6. The user wants to review and approve each consolidation during the finding presentation.

**BLOCKING: Batch grep verification before presenting deletions.** BEFORE presenting any delete-as-redundant finding to the user, run a batch grep verification on ALL proposed deletions. Only present files as deletable after grep confirms the match. Include grep evidence inline: "Verified: [file] line N contains [matched text]." Files with zero grep matches must be presented with placement options (keep/bake-into-skill/promote) instead of delete.

**Memory finding question format:** For memory consolidation findings, always include: "Recommendation: [delete (redundant, verified: {grep evidence}) / keep as memory / bake into {specific skill name} / promote to CLAUDE.md] — [rationale]." Options should match the recommended placements, not generic Accept/Reject.

### Presentation

**FIRST — Coverage statement (full scope only, always first)**

One line stating exactly what the historical scan covered — e.g. "Scanned 3 sessions since the last run (Aug 22–25); nothing older touched." If the cap overflowed or this was a first run on the project, state what was skipped and offer the follow-up/backfill run.

**THEN — Audit of Prior `/improve` Runs (full scope only)**

**Skip both sections entirely in current-only scope.** Go straight to presenting findings.

In full scope, before presenting any new findings, surface the Prior-Improve Cross-Check report as an audit trail:

```
## Audit of Prior /improve Runs

| Date | Recommendations | Implemented | Drifted | Skipped |
|------|----------------|-------------|---------|---------|
| 2026-04-11 | 6 | 6 ✅ | 0 | 0 |
| 2026-04-09 | 5 | 3 ✅ | 1 ⚠️ | 1 (re-surfaced below) |
```

This gives the user confidence (verified-implemented), highlights drift (needs re-application), and re-surfaces previously-skipped items as new findings to reconsider. NEVER silently drop prior findings — always show the verification.

**THEN — Present All Findings as a Compact List (default)**

Present every finding in ONE chat message, grouped by tier, most impactful first. Each finding is a short block:

**Format:** "[Tier | Confidence] — [Source: current conversation / past session date] — [Description of finding and proposed change]. File: [full path]. Proposed: [what to add/modify/remove]. Recommendation: [specific recommended action]"

**Count and check before presenting.** Count findings from the final list and state the unit once (finding or edit). Before a finding reaches the user, check its main example against the primary record, including scope choices the user made in that session (a stated count that doesn't match the list, or a finding whose example comes from an out-of-scope chat, costs trust).

**Order:**
1. Drifted items (prior accept didn't land — needs re-application)
2. Re-surfaced previously-skipped items (with note: "previously skipped on [date]")
3. Targeted (from /improve args)
4. Critical → Promotion → Content Misplacement → Improvement → Technique → Maintenance → Reinforcement → New Skill → User Coaching

After the list, resolve ONLY the items that genuinely need a user decision via AskUserQuestion (placement choices, hook scope, contested or low-confidence findings) — recommended option first. Then proceed to Phase 6, or, for large change sets, write an execution plan and get approval per the user's planning workflow before applying.

**Do-no-harm pass before approval, and again after applying when the changes touch hooks or steps the user runs** (each pass in real use found blockers, such as a hook that would have blocked plan mode or a file move that would have broken dozens of path references): a separate helper reads the plan against "the setup already works well: can any change make everyday work worse?" and exercises each changed path on a real input (a hook on a replay of a real command, a check on known-good files). This is the assistant's own pass; it does not replace the user's own plan review.

**Opt-in alternative — per-finding walkthrough:** if the user asks to go one at a time ("walk me through them"), present each finding via AskUserQuestion with Accept / Reject / Modify options, in the same order. In this mode, if 8+ findings, after presenting 5, ask: "Continue with remaining findings, or apply what we have so far?"

## Phase 6: Apply Changes

**Announce:** "Applying N approved changes across M files..."

**Scaling guidance:** For 10+ approved changes, group changes by target file and execute in parallel waves using sub-agents. Constraint: no two agents edit the same file in the same wave. For <10 changes, sequential execution is fine. When using parallel waves, present the wave structure to the user before executing: "Wave 1: [agents], Wave 2 (after Wave 1): [agents]."

**After applying:** when the changes touch hooks or steps the user runs, run the do-no-harm pass again (Phase 5 paragraph) on the applied files, next to the full-read and adversarial reviews.

**Verify-before-removing gate:** Before executing ANY removal (deleting a memory file, removing a CLAUDE.md rule, or deleting a skill section), re-grep the target destination to confirm the rule actually exists there. If the grep fails — the rule was approved for removal based on a claim it existed elsewhere, but it doesn't — skip the removal and flag it: "SKIPPED: [rule] was approved for removal but grep shows it's not in [target]. Keeping original." This catches false-positive audit claims that pass Phase 4c verification but don't survive a second check at execution time.

1. Group approved changes by file
2. Edit existing files with approved modifications
3. Create new files if needed (new memory entries, new skill stubs)
4. For hook conversions:
   - Read the target settings.json file (project or global, per user's scope choice)
   - Add the hook configuration under the appropriate event key (PreToolUse, PostToolUse, etc.)
   - If the hooks key doesn't exist yet, create it
   - Preserve all existing hooks — append, never replace
5. For rule extractions:
   - Create the `.claude/rules/` directory if it doesn't exist
   - Write the extracted rule to a new `.md` file with path-scoping glob in frontmatter
   - Remove the extracted section from CLAUDE.md
6. For memory file merges:
   - Combine the content of overlapping memory files into one
   - Update the frontmatter (name, description) to reflect the merged scope
   - Delete the duplicate file
   - Update MEMORY.md index to remove the deleted entry and update the surviving entry
7. For skill extractions:
   - Create the new skill `.md` file with proper frontmatter (name, description)
   - Move the procedural content from CLAUDE.md into the skill
   - Replace the CLAUDE.md section with a one-line reference: "See /skill-name for details"
7a. **After ANY structural edit to a skill file** (removing a mode, merging workflows, deleting a section): a line-anchored edit map plus a vocabulary grep sweep is NOT sufficient verification. Semantics of the removed concept can survive in SHARED sections that never mention its vocabulary (in one real trim, the edit map and post-edit grep were clean, yet three leftovers survived in shared phase sections; only a post-completion full-file read caught them). After the grep sweep, full-read the edited file (or spawn one Explore agent) hunting for surviving text that ASSUMES the removed structure: pause/ask patterns, alternative approval paths, choice language.
7b. **Contradiction read:** after all edits, read every edited section against the rest of its file and against CLAUDE.md for contradictions and confusing spots (in real use this found 2 to 5 issues per run).
8. For feedback-type findings, ALSO save as memory files:
   - File: `feedback_[topic].md` in project's memory directory
   - Frontmatter: name, description, type: feedback
   - Content: rule + **Why:** + **How to apply:**
9. Update MEMORY.md index if new memory files created
10. For Content Misplacement findings:
    - Remove content from the source file
    - Add it to the destination file in the appropriate section
    - If moving TO a skill file: place in the most relevant section, adjust formatting to match the skill's style
    - If moving FROM a skill to CLAUDE.md: place in the most relevant existing section
    - Preserve meaning — only adjust formatting and context references
11. For Skill Description rewrites:
    - Edit the `description` field in the skill's frontmatter
    - Preserve the original intent, improve clarity and activation keywords
12. Present a summary table in the conversation:

    ## Changes Applied

    | # | File | Change | Category |
    |---|------|--------|----------|
    | 1 | path/to/file.md | Brief description of what changed | Category |

    N changes across M files.

    - **File**: short relative path (not full absolute)
    - **Change**: concise action (e.g. "Added rule: …", "Strengthened: X → Y", "New memory: …", "Hook added: …", "Rule extracted: …", "Memory merged: …", "Skill created: …", "Content moved: …", "Description rewritten: …")
    - **Category**: tier from Phase 4d (Critical, Promotion, Content Misplacement, Improvement, etc.)
13. Ask if user wants to commit changes

## Save Learnings

After Phase 6 completes (regardless of whether any changes were applied), update BOTH learnings files. Content is split by kind, not duplicated:

### 1. Project learnings file (`~/.claude/projects/<mangled-project-path>/improve-learnings.md` — create if missing, same path rule as Load Learnings)

- Append a date-keyed entry under `## Run Log`: heading `### YYYY-MM-DD — <one-line session signature>`. NO run numbers — date + signature only (run counters drift and collide).
  - **REQUIRED first line:** `Scanned through: <ISO timestamp>, session <current session UUID>` — timestamp from `date -Iseconds` at scan time (NEVER estimated or fabricated), session UUID from the scratchpad directory path (fallback if unavailable: the most recently modified `.jsonl` in the project's sessions directory, noted as such). This line is the anchor the NEXT run's History Scan window starts from.
  - Scope chosen, acceptance rate by category (e.g., "Critical: 3/3 accepted")
  - Deferral counter updates (e.g., "CLAUDE.md size: 5th deferral, 210 lines")
  - Project-specific patterns or "Modify" signals from this run
  - If the run's changes were committed in the same session, the commit id (without it, the next reader can assume the work is still uncommitted)
- Update `## Patterns` and `## Counters` sections when the run changes them

**File structure (first-run creation):**
```
# Improve Learnings — <project name>

## Patterns (distilled, project-specific)

## Counters (live deferral/tracking state)

## Run Log
### YYYY-MM-DD — <one-line session signature>
- Scanned through: 2026-01-01T18:30:00+08:00, session aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
- Scope: current-only. Acceptance: Critical 3/3, Improvement 2/4.
```

### 2. Global learnings file (`~/.claude/improve-learnings.md`)

- Update ONLY when the run revealed something about how the user works ACROSS projects: presentation-format preferences, rule-writing modify signals (e.g., "user softened NEVER→SHOULD for style rules"), scope habits, tooling/enforcement preferences
- NEVER store project state here: no counters, no run diaries, no project file sizes

### Size enforcement (both files)

After writing, check the file with `wc -l`. If a project file exceeds 80 lines, condense the oldest Run Log entries into `## Patterns` NOW — in this run, not "later" — then delete those raw entries. Keep the global file under ~40 lines the same way.

### Settled-Pattern Promotion

While updating, scan both files for any pattern confirmed across ~5+ runs. Settled behavior belongs in config, not learnings: surface each such pattern as a finding (this run if still practical, otherwise flag it for the next run) proposing to bake it into the skill file, CLAUDE.md, or settings — and DELETE it from learnings once baked. Learnings files track what's still being learned; without this rule they grow into a permanent patch layer that silently overrides the skill.

## Comprehensive Config Session Mode

When the user explicitly requests a dedicated config improvement session (e.g., "full config sweep", "comprehensive improvement", "update the entire repository config"), the standard /improve workflow adapts:

**How it differs from end-of-session runs:**
- Full memory audit becomes a dedicated phase: read every memory file, grep-verify each against CLAUDE.md and skills, present candidates by category (redundant/stale/promote-to-skill/promote-to-CLAUDE.md)
- Phase 6 uses wave-based parallel execution (group changes by file, execute via sub-agents with no-conflict constraint)
- Plan mode integration: after presenting all findings (compact list + decision questions per Phase 5), enter plan mode to write the execution plan, get user approval, then execute
- The user expects an explicit decision on each improvement individually (via the findings list + decision questions, or the per-finding walkthrough if they opt in) — never batch items into an assumed-approval plan

**Detection signals:** User says "full sweep", "comprehensive", "config update", "improve everything", or explicitly requests memory consolidation / skill standardization as a dedicated session. (A bare `/improve config audit` invokes the lighter single-pass config-audit scope from Scope Selection, NOT this mode.)

**Key lesson:** Securing an explicit per-item decision before executing achieves near-100% acceptance in dedicated sessions. Batch plans that assume all items are approved get rejected for individual review.
