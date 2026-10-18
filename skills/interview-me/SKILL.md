---
name: interview-me
description: "Gets on the same page before knowledge work: looks things up, asks one question at a time with its pick, then agrees the plan. Use when you say \"interview me first\". Not for job interview practice."
license: MIT
compatibility: "Designed for Claude Code. Written to also work in the Claude app (not yet tested there)."
---

# Interview Me

For any knowledge work: documents, decisions, strategy, content, reviews, plans. For code features, a plan follows the interview.

## Holds for the whole interview

1. **Facts before questions.** Before asking, look up every fact you can reach: what the person pointed to (files, messages, tickets, documents), a codebase or test environment, checkable web facts, and how often and how recently anything being redesigned runs. Only real decisions go to the person. Facts that shape the first questions come first; a slow lookup that only later questions need goes to a helper (sub-agent, where your app has them), which returns its open questions to you, while you ask the rest. Being told "check X first" means this rule was missed. Example: asked to redesign a weekly status template, first check how many recent reports used it and which sections people left empty, then ask only who it should serve.
2. **A pick in every question:** your recommendation, its evidence and brief reasoning, worded so a plain "yes" accepts it. In a picker it comes first, labelled "(Recommended)"; a label alone is not a recommendation. Chat lists carry a pick too. Honour any way of working the person asked for. Example: "Lead with the cost numbers or the timeline? I recommend cost first, because you said the board cares most about budget."
3. **One question per message by default.** A decision that needs its own explanation, or whose premise may be challenged, goes alone and is resolved first; a follow-up that depends on its answer waits. Only small, independent, low-context questions with settled parent decisions may share a round. Interdependent decisions share one table of combinations and one question.
4. **Many questions on material decisions, few on routine details.** On open decisions, more questions beat fewer. Decide routine details yourself and write each assumption into the plan or wrap-up for the person to overrule. Done means no open material decision is left, never "asked enough questions".

## Investigation

- Re-read named sources when you need them; earlier summaries and handoffs are history, not current state.
- On unfamiliar work, start with a short blind-spot pass: what unstated requirement or unknown could sink this, given who the person is and what they know? Spend questions there.
- Before recommending a scope, count what it affects (items, records, people).
- Say how strong the evidence is. Check the first recommendation against the person's own data (stated focus, numbers, task list) and your findings, because unchecked first picks get reversed.
- Check a proposal against any written standard (style guide, template, earlier decision, project process, skill step order) before showing it; say in the question which parts it follows. Example: before proposing a report outline, check it against the team's report template and say which sections it keeps.
- Effort comparisons name the extra work and are labelled estimates.
- End with two short lines: what you checked, and what you couldn't.

## Asking

- **Source of each proposal:** the person's ask (quoted), a named source (dated), or "my addition", in a short "Source:" line where it matters. A scope question quotes the brief. Before reversing or narrowing an earlier ask, trace it back to where it started and quote it. Example: "Source: your brief ('keep it to two pages'). The appendix is my addition."
- **Use the question picker** (a multiple-choice question tool, where your app has one) for 2 to 4 clear options; plain text when there is none; open text when options would limit the answer. Wording and creative choices: variations in chat, discussed in open text; picker options then carry a short wording example.
- **Show, don't describe.** For a choice about look, sound, feel or flow, show a sample, two versions, a mock or a worked example in chat first (not only in option previews); talk cannot settle it.
- **Findings and the first question go in one message.** Never ask "ready to continue?"; it costs a turn. The question itself repeats the facts it rests on, because some apps fold text shown just before a picker.
- **Answer the person's questions first**, in plain chat, then continue. Use plain words, and explain any term the person hasn't used themselves.
- **Restate your current read** in two or three bullets above a key question, rarely, so a wrong premise shows.
- **Right person.** Ask the person only what they own (goals, priorities, taste, trade-offs only they can judge); decide what is within your expertise, say what and why, and let them overrule. When only someone else can answer (client, manager, teammate), don't guess or make the person guess: draft the question for them, if that person raised it, only they can answer, and the answer changes a decision now. If the source can't be asked (anonymous feedback), draft one group follow-up or mark the point unanswerable. Example: whether a client accepts a later deadline is the client's call, so draft a one-line question for them.
- **Locked decisions are not templates.** Ask about an edge case a locked decision leaves open; never settle it silently in the plan, because an assumption that contradicts or extends it looks approved when nobody saw it. Before turning a choice into a lasting rule, ask: this time only, or always? Example: the agreed rule is "every section gets a summary"; for a one-paragraph appendix, ask instead of quietly exempting it.
- **Content before format.** Parents before children; content (what are we saying or building?) before format and delivery, which wait until the person signals the content is complete (such as "that's everything", "I think we've covered it all", or a question about next steps). When most decisions are settled, offer a lighter round on the open ones. Example: settle what the proposal recommends before asking whether it should be slides or a memo.
- **Simpler design first.** Before proposing anything to be built, added or tracked (an item, a task, a screen, a mode, check, tracker, routine or path; not your own checks or progress files), ask whether it is worth doing and whether an existing step covers it. Offer the simpler option first ("none" by default for a new tracker or routine), say what it leaves out, and keep every requirement. This limits machinery, not questions. Example: before proposing a new weekly tracker sheet, check whether one more column in the existing task list does the job.
- **Suggest a split** into smaller pieces when an interview keeps producing new questions. The signal is scope (separate outcomes, question count), never your sense of context room.

## Outside research

When a decision depends on how others do it (a best practice, format, tool, what works for an audience), offer research as a one-line add-on to your first message: "Want me to check how others do X? I'd say yes, because ... Reply yes or skip." If that message ends in a picker, put the offer in the picker as its own small question instead, because the picker is where they reply. No reply means skip. A checkable fact (a date, a price) is not research; look it up. A brief that asks for research counts as yes. Research the job a thing does before its look. If shared links could be source of truth or inspiration, ask in the before-round. When the research covers a product or tool choice, show how 2 or 3 named practitioners do it before recommending. A tool comparison checks each plan's limits (free plans too) on the vendor's pricing page, with a row "your assistant can read or export its data on this plan". Example: choosing a newsletter tool, compare what each plan really includes on the vendor's pricing page, and show how two or three named writers in the field run theirs.

## The flow

1. **Brief.** Answer a direct question in the brief first, briefly (provisional if unchecked); a simple question gets an answer, not an interview. Then one plain line says what happens next.
   **Before-round:** glance at what is quickly visible (file names and dates, the brief's links, one or two key files when cheap) to ground your pick. Then ask, one at a time, any 1 to 3 questions that change where you look or what "good" means (purpose, audience, constraints, success), each with your guess as the pick ("Build on what exists? My guess so far: yes, it's recent."; in a picker, the first option labelled "(Recommended)", as in rule 2). Questions needing the findings wait. Never open with generic questions. "Interview me first" or "ask me questions first" always gets the before-round.
   When the old version is being rebuilt, the before-round first settles the acceptance bar: "match the old one, or may it differ?" (usual pick: match; when the brief asks for change, ask instead which parts must stay). State it in the result, so gaps count as missing requirements, not open questions. Example: a rebuilt report drops columns the old one had; with the bar set to "match it", those are missing requirements, not scope questions.
2. **Investigate**, plus any research the person approved.
3. **Findings** as a short plain story, with the first decision question.
4. **Decisions.** A wide-open choice gets 2 or 3 genuinely different approaches (core idea, trade-offs, effort); skip them only when earlier decisions settle the approach, never because exploring feels slow. For an open-ended piece such as a document, show its outline once and ask "does this look right?" in open text.
5. **Wrap-up**, scaled to the work (below).

**Where we are:** at the start and each step change, one line on where things stand and what comes next ("Investigation done. Next: 4 decisions, then the plan.").

**Scale to the task:** a small or execution-type task (a test-run setup, a follow-up) uses steps 1, 2 and 5, plus 4 for open decisions, and says so; "full flow" from the person forces every step. When invoked by name, never skip clarification because a project default (such as "draft immediately") says so; such defaults apply only when you decide alone.

## Review variant

For going through what exists (feedback, comments, findings, edits, a plan or document to critique):
- Investigate first: every screenshot and linked document, the source material, the impact in numbers; in email threads, every reply from the relevant people in order, unfiltered by date or topic, because filters hide late replies.
- An overview list, one bullet per item: its name in plain words (any code beside it), one or two plain sentences on what it is, and your pick; or per theme (with item numbers) when many are similar; no extra tables. Evidence and sources come item by item. First ask, with your guess, any answer that would change many picks (such as their capacity). Then invite a bulk reply on the simple ones ("Accept my picks for items 1 to 6?"); take the rest one at a time. Choices: Accept / Reject / Change for edits and critiques; Act now / Look into it / Later / No action for feedback.
- If most items are settled, confirm only the open ones. No approaches or outline check here.
- If another skill governs the review (such as a plan-review skill), its workflow wins; this variant sets only how to ask.

## Wrap-up

| Work | Ending |
|---|---|
| A simple question | The answer with a recommendation. No list. |
| A small deliverable (one email, short doc or quick edit) | "Here's what I'll do: ..." in chat and the person's yes, then do it. |
| Multi-step or hard-to-undo work | A plan for approval: ask whether to write a plan they approve before anything changes (plan mode in Claude Code), with your pick (outside Claude Code, a written plan in chat). "Then plan mode" in the brief counts as yes. |

The last two rows also give:
- **Coverage check:** everything the person asked for, in the brief and since: decided, in the plan, parked, or dropped and why; plus answers to what they would probably still ask.
- **Decision log:** each decision, the options rejected, and why.
- **Assumptions:** the routine details you decided (rule 4).
- **Before working alone:** what you need from the person first.

When plan mode is already active, follow the flow and write the result as the plan instead of a chat wrap-up.

## Going back

Go back when it beats pushing on: a new constraint, to the investigation or before-round; a challenged approach, to the approaches; anything unclear, clarify first.
