"""Condense a Claude Code session log (JSONL) into a readable markdown transcript.

Why: a new Claude Code session needs the user's exact words from the last one, not only a summary. The raw
session log is mostly tool output (often tens of MB); this script keeps the conversation and drops the rest.

Where the logs are: the Claude Code CLI keeps one file per session in
    ~/.claude/projects/<project-slug>/<session-id>.jsonl
where <project-slug> is the project folder's path with "/" (and other special characters) turned into "-".
The newest file in that folder is usually the current session. This script reads only those local session logs:
it works wherever Claude Code writes them, and does nothing for chats that leave no such file (such as claude.ai).

Keeps, in time order: the user's messages (also the ones sent while Claude was working, and the words typed when
rejecting a plan, a question box or another tool call), Claude's chat replies, and every question box with every
answer, each answer under its question.
Drops: tool calls and tool output, system reminders, hook chatter, and Claude's short mid-turn progress lines
(under 300 characters, no bold, followed by more Claude text in the same turn). Claude's first chat entry after a
user message or answer is never dropped: it is the reply to the user.
Labels entries that are not the user's words: Claude's own skill calls and system notices (scheduled prompts,
and hook texts that stopped a question box before the user saw it).
In the transcript, "User" headings mark the words of the person who used Claude Code in that session.
Reads only the conversation records (user, assistant, attachment, system); other record types, such as
"api-request-blob", repeat messages without a time and would show and count them twice.
Ends with a check block: the user's message count in the raw session log against this transcript, and the turns
where Claude's chat text may not have reached the user's screen (an upper bound).

Usage: python3 condense_transcript.py <session.jsonl> <out.md> [--since "YYYY-MM-DDTHH:MM[:SS]" | --since start]
                                      [--keep-progress] [--overwrite] [--force-append] [--utc]
--since is UTC, the time zone of the session log's own "timestamp" fields (a trailing Z is allowed).
  --since start takes the session log's first record time, cut down to the minute (this session's first part).
  With --since and an existing <out.md>: APPENDS this session under a "## Session from <since> UTC" heading
  (an existing transcript keeps its earlier sessions). Records before --since are left out.
Without --since: writes a new file. An existing <out.md> is never replaced unless --overwrite is given.
--force-append: append even when <out.md> already holds a part for this session with the same --since.
--keep-progress keeps Claude's short mid-turn progress lines.
--utc: show times in UTC only (by default the check block also shows this machine's local time).
Exit 2: refused (bad --since, existing file, duplicate part); nothing is written.

Standard-library Python 3.8+ only; run it from any folder (it uses no fixed install path).
Tested on macOS; should work on Linux and Windows (not tested).

MIT License. Copyright (c) 2026 Terence Bristol. Full text: the LICENSE file in the repository this skill comes from.
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

ap = argparse.ArgumentParser(description="Condense a Claude Code session log (JSONL) into a readable markdown "
                                         "transcript. Session logs live in ~/.claude/projects/<project-slug>/*.jsonl.")
ap.add_argument("src", help="the session log, a .jsonl file")
ap.add_argument("out", help="the markdown transcript to write (or append to, with --since)")
ap.add_argument("--since", help="UTC, YYYY-MM-DDTHH:MM or YYYY-MM-DDTHH:MM:SS, optional trailing Z; "
                                "or 'start' for the session log's first record, cut down to the minute")
ap.add_argument("--keep-progress", action="store_true", help="keep Claude's short mid-turn progress lines")
ap.add_argument("--overwrite", action="store_true", help="without --since: replace an existing output file")
ap.add_argument("--force-append", action="store_true", help="append even if this session part is already there")
ap.add_argument("--utc", action="store_true", help="show UTC times only, not this machine's local time")
args = ap.parse_args()
src, out, since = args.src, args.out, args.since


def refuse(msg):
    sys.stderr.write("REFUSED: %s\nNothing was written.\n" % msg)
    sys.exit(2)


def parse_ts(ts):
    """A record time ("2026-10-14T03:40:37.217Z") as an aware UTC datetime, or None."""
    try:
        d = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def first_minute(path):
    """The session file's first record time, cut to the minute ("2026-10-25T17:21"), or None."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    d = parse_ts(json.loads(line).get("timestamp"))
                except (ValueError, AttributeError):
                    continue
                if d:
                    return d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M")
    except OSError:
        return None
    return None


SINCE_RX = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?Z?$")
since_dt = None
if since == "start":                                    # the session's first record, cut down to the minute, so
    since = first_minute(src)                           # a kickoff pasted seconds before the minute is not lost
    if since is None:
        refuse('--since start: no record with a "timestamp" found in %s.' % src)
if since is not None:                                   # only an exact UTC time is accepted
    if not SINCE_RX.match(since):
        refuse('--since "%s" is not a UTC time like 2026-10-14T03:40 or 2026-10-14T03:40:37 (optional Z). '
               'Use the session file\'s own UTC time, for example its first "timestamp" value; '
               'never a local time and never a space instead of "T".' % since)
    since = since.rstrip("Z")
    try:
        since_dt = datetime.strptime(since, "%Y-%m-%dT%H:%M:%S" if since.count(":") == 2 else "%Y-%m-%dT%H:%M")
    except ValueError:
        refuse('--since "%s" is not a real date and time (expected UTC, YYYY-MM-DDTHH:MM).' % args.since)
    since_dt = since_dt.replace(tzinfo=timezone.utc)
    if args.overwrite:
        refuse("use either --since (append this session) or --overwrite (replace the file), not both.")

session_id = os.path.basename(src)
if session_id.endswith(".jsonl"):
    session_id = session_id[:-6]
if os.path.exists(out):                                  # never lose or repeat earlier parts
    if since is None and not args.overwrite:
        refuse("%s already exists. Without --since this run would replace it and lose every earlier session part. "
               "Pass --since <this session's start, UTC> to append this session, or --overwrite to replace the "
               "file on purpose." % out)
    if since is not None and not args.force_append:
        with open(out, encoding="utf-8", errors="replace") as f:
            old = f.read()
        for m in re.finditer(r"^## Session from (\d{4}-\d{2}-\d{2} \d{2}:\d{2}(?::\d{2})?) UTC\s*\n\s*Source: `([^`]*)`",
                             old, re.M):
            fmt = "%Y-%m-%d %H:%M:%S" if m.group(1).count(":") == 2 else "%Y-%m-%d %H:%M"
            head_dt = datetime.strptime(m.group(1), fmt).replace(tzinfo=timezone.utc)
            head_id = os.path.basename(m.group(2))
            if head_id.endswith(".jsonl"):
                head_id = head_id[:-6]
            if head_id == session_id and head_dt == since_dt:
                refuse("%s already holds a part for session %s from %s UTC (line %d). Appending again would repeat "
                       "it. If that part is broken, restore the file from its backup first; to add only newer "
                       "messages, pass a later --since; to append anyway, add --force-append."
                       % (out, session_id, m.group(1), old.count("\n", 0, m.start()) + 1))

STRIP = [re.compile(r"<system-reminder>.*?</system-reminder>", re.S),
         re.compile(r"<local-command-caveat>.*?</local-command-caveat>", re.S),
         re.compile(r"<command-(name|message|args)>.*?</command-\1>", re.S),
         re.compile(r"<local-command-stdout>.*?</local-command-stdout>", re.S),
         re.compile(r"<task-notification>.*?</task-notification>", re.S)]
MIDTURN_MARK = "The user sent a new message while you were working:\n"   # older attachment format
MIDTURN_END = "\n\nThis is how Claude Code surfaces"
REJECT_MARK = "To tell you how to proceed, the user said:"            # the user's words typed on rejecting a tool call
REJECT_END = "\n\nNote: The user's next message"
CLARIFY = "The user wants to clarify these questions."               # Claude Code's text for "chat about this"
FIXED_REJECT = ("Denied by user",)                                     # Claude Code's fixed text, not the user's words
PROGRESS_MAX = 300   # characters: a mid-turn line shorter than this, with no bold, counts as a progress line
NO_TEXT = "(message with no text, for example an image only)"
CONVERSATION_TYPES = ("user", "assistant", "attachment", "system")    # other record types are bookkeeping copies
HOOK_DENIAL = re.compile(r"^\s*(?:Error:\s*)?\w+(?::\w+)? hook (?:blocking )?error:")   # a hook stopped the tool call
USER = "User"                                                          # heading for the user's own words
ANSWERS = "User answers"                                               # heading for the user's question-box answers
NOT_USER = "System notice (not typed by the user)"


def clean(t):
    for rx in STRIP:
        t = rx.sub("", t)
    return t.strip()


def clean_edges(t):
    """The user's own words: strip injected blocks only at the start or end, so text pasted in the middle stays."""
    t = t.strip()
    changed = True
    while changed:
        changed = False
        for rx in STRIP:
            m = rx.match(t)
            if m:
                t, changed = t[m.end():].strip(), True
            for m in rx.finditer(t):
                if m.end() == len(t):
                    t, changed = t[:m.start()].strip(), True
                    break
    return t


def text_of(content, sep="\n"):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return sep.join(x.get("text", "") for x in content if isinstance(x, dict) and x.get("type") == "text")
    return ""


def strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from strings(v)


def norm(t):
    return re.sub(r"\s+", " ", t).strip()[:80]


def local_hm(ts):
    """A record time as HH:MM in this machine's local time zone."""
    d = parse_ts(ts)
    return d.astimezone().strftime("%H:%M") if d else "?"


def rejection_words(res):
    """(kind, words) for a tool result: kind is None (not a rejection with a reply), "user" or "not-user"."""
    if REJECT_MARK not in res:
        return None, ""
    words = res.split(REJECT_MARK, 1)[1].split(REJECT_END, 1)[0]
    words = clean_edges(words)
    if not words:
        return None, ""
    if words.startswith(CLARIFY) or words in FIXED_REJECT:
        return "not-user", words
    return "user", words


def result_text(c, sep="\n"):
    res = c.get("content")
    if isinstance(res, list):
        res = sep.join(x.get("text", "") for x in res if isinstance(x, dict))
    return str(res) if res is not None else ""


def box_text(qs):
    return "\n\n".join("**Q (%s):** %s\n\nOptions: %s" % (
        q.get("header", ""), q.get("question", ""),
        " | ".join("%s: %s" % (o.get("label"), o.get("description")) for o in q.get("options", [])))
        for q in qs)


rows = []            # (who, ts, text, is_user) ; is_user = counts as one of the user's messages
user_keys = {}       # user message text -> time shown, so a copy of the same message is not shown twice
pending_q = {}       # AskUserQuestion id -> (questions, time asked, asked before --since)
tool_names = {}      # every tool_use id -> tool name
skill_calls = {}     # Skill tool id -> input
raw_user = before_user = 0
raw_queued = set()
turn = 0             # turn number: a new turn starts at any non-result user record or a turn end
turn_of = {}         # id of a Claude chat row -> its turn
has_origin = False
msgs, msg_order = {}, []   # assistant message id -> blocks (for the possibly-not-shown check)
boxes = []           # (ts, header, saw_text_in_turn)
saw_text = False     # a visible Claude text block since the user's last message or box answer
bad_lines = []       # line numbers that are not readable JSON objects
last_line_partial = False


def seen(t, ts):
    """True when the same text was shown as the user's within the last 5 minutes (one message stored twice)."""
    prev = user_keys.get(norm(t))
    if not prev or not ts:
        return False
    a, b = parse_ts(ts), parse_ts(prev)
    if not a or not b:
        return False
    return abs((a - b).total_seconds()) <= 300


def add_user(ts, t, who=USER):
    user_keys[norm(t)] = ts
    rows.append((who, ts, t, True))


def queued_text(a, ts):
    """The user's message from a mid-turn attachment ("" when the attachment is not one)."""
    if isinstance(a, dict) and a.get("type") == "queued_command" and a.get("commandMode") == "prompt":
        p = a.get("prompt")
        t = clean_edges(text_of(p))
        return t or NO_TEXT
    for s in strings(a):
        if MIDTURN_MARK in s:
            return clean(s.split(MIDTURN_MARK, 1)[1].split(MIDTURN_END, 1)[0])
    return ""


def system_prompt(rec):
    """True for a message Claude Code itself queued, for example a scheduled (cron) resume check, even when the
    record has no "origin" field."""
    return bool(rec.get("scheduledTaskId") or rec.get("turnOrigin") in ("scheduled", "system")
                or rec.get("promptSource") == "system")


def hook_denial(rec, res):
    """True when a hook stopped the tool call: its text is the hook's, not the user's answer."""
    pd = rec.get("permissionDecision") if isinstance(rec.get("permissionDecision"), dict) else {}
    return (pd.get("source") == "hook" and pd.get("decision") == "reject") or bool(HOOK_DENIAL.match(res))


def count_raw(rec, rtype, content):
    """Raw count, independent of the rows: the user's typed messages, mid-turn messages and rejection replies.
    Returns the number of user messages in this record."""
    user_n = 0
    if rtype == "attachment":
        a = rec.get("attachment") or {}
        t = queued_text(a, rec.get("timestamp", ""))
        qid = (a.get("source_uuid") if isinstance(a, dict) else None) or (norm(t), rec.get("timestamp", ""))
        if t and qid not in raw_queued:
            raw_queued.add(qid)
            user_n += 1
        return user_n
    msg = rec.get("message") if isinstance(rec.get("message"), dict) else {}
    if msg.get("role") != "user":
        return 0
    is_result = any(c.get("type") == "tool_result" for c in content)
    if not is_result and (rec.get("origin") or {}).get("kind") == "human":
        user_n += 1
    for c in content:
        if c.get("type") == "tool_result":
            kind, words = rejection_words(result_text(c))
            if kind == "user":
                user_n += 1
    return user_n


with open(src, encoding="utf-8") as f:
    lines = f.readlines()
for lineno, line in enumerate(lines, 1):
    if not line.strip():
        continue
    try:
        rec = json.loads(line)
    except json.JSONDecodeError:
        rec = None
    if not isinstance(rec, dict):                  # never skip an unreadable line silently
        bad_lines.append(lineno)
        if lineno == len(lines) and not line.endswith("\n"):
            last_line_partial = True
        continue
    ts = rec.get("timestamp", "")
    rtype = rec.get("type")
    if rtype not in CONVERSATION_TYPES:            # e.g. "api-request-blob": a copy of messages already in the
        continue                                   # file, with no time; reading it showed every entry twice
    if "origin" in rec:
        has_origin = True
    msg = rec.get("message") if isinstance(rec.get("message"), dict) else {}
    content = msg.get("content")
    if isinstance(content, str):
        content = [{"type": "text", "text": content}]
    content = [c for c in (content or []) if isinstance(c, dict)]
    for c in content:                              # every tool call by id, also before --since
        if c.get("type") == "tool_use":
            tool_names[c.get("id")] = c.get("name")

    rec_dt = parse_ts(ts) if since_dt else None
    if since_dt and rec_dt and rec_dt < since_dt:  # left out of this part, but counted for the warning
        before_user += count_raw(rec, rtype, content)
        for c in content:
            if c.get("type") == "tool_use" and c.get("name") == "AskUserQuestion":
                pending_q[c.get("id")] = ((c.get("input") or {}).get("questions", []), ts, True)
            elif c.get("type") == "tool_use" and c.get("name") == "Skill":
                skill_calls[c.get("id")] = c.get("input") or {}
        continue

    raw_user += count_raw(rec, rtype, content)

    if rtype == "system" and rec.get("subtype") == "turn_duration":
        turn += 1
        continue

    if rtype == "attachment":                   # messages the user sent while Claude was working
        a = rec.get("attachment") or {}
        m_ = queued_text(a, ts)
        if m_ and (m_ == NO_TEXT or not seen(m_, ts)):
            add_user(ts, m_, USER + " (sent while Claude worked)")
            saw_text = False
        continue

    role = msg.get("role")

    if rtype == "assistant":
        mid = msg.get("id") or rec.get("uuid")
        if mid not in msgs:
            msgs[mid] = []
            msg_order.append(mid)
        for c in content:
            msgs[mid].append((ts, c))

    if role == "user":
        is_result = any(c.get("type") == "tool_result" for c in content)
        human = (rec.get("origin") or {}).get("kind") == "human"
        if not is_result:
            turn += 1
        if not is_result and rec.get("isMeta"):
            t = clean(text_of(content))
            src_id = rec.get("sourceToolUseID")
            if src_id in skill_calls:              # Claude called a skill itself: not the user's words
                inp = skill_calls[src_id]
                a_ = norm(str(inp.get("args") or ""))
                rows.append(("Claude (skill call)", ts, "/%s %s" % (inp.get("skill", "?"), a_[:300]), False))
            elif "ARGUMENTS:" in t:                 # a skill the user invoked with their words
                words = t.split("ARGUMENTS:", 1)[1].strip()
                if not seen(words, ts) and not seen("(invoked a skill) " + words, ts):
                    add_user(ts, "(invoked a skill) " + words)
            elif t and not ("Base directory for this skill" in t[:300] or re.match(r"#\s+\S.*\n\n##\s", t)):
                rows.append((NOT_USER, ts, t[:500], False))
            continue
        if not is_result:
            raw = text_of(content)
            cmd = re.search(r"<command-name>(.*?)</command-name>", raw, re.S)
            if human and cmd:                       # the user's slash command, shown with its words
                a_ = re.search(r"<command-args>(.*?)</command-args>", raw, re.S)
                words = (a_.group(1).strip() if a_ else "")
                add_user(ts, ("(invoked a skill) " + words) if words else "(ran %s)" % cmd.group(1).strip())
                if words:
                    user_keys[norm(words)] = ts
                saw_text = False
                continue
            t = clean_edges(raw) if human else clean(raw)
            if not human and "ARGUMENTS:" in t:    # older sessions: skill invoked with the user's words
                t = "(invoked a skill) " + t.split("ARGUMENTS:", 1)[1].strip()
            elif not human and ("Base directory for this skill" in t[:300] or re.match(r"#\s+\S.*\n\n##\s", t)):
                t = ""                              # a skill body loaded into the chat, not the user's words
            if t.startswith("[Request interrupted"):
                continue
            if not human and (rec.get("origin") or system_prompt(rec)):   # a scheduled prompt or a helper notice
                if t:
                    rows.append((NOT_USER, ts, t[:500], False))
                continue
            if t:
                add_user(ts, t)
                saw_text = False
            elif human:
                add_user(ts, NO_TEXT)
                saw_text = False
            continue

    for c in content:
        ctype = c.get("type")
        if role == "assistant" and ctype == "text":
            t = clean(c.get("text", ""))
            if t:
                rows.append(("Claude", ts, t, False))
                turn_of[id(rows[-1])] = turn
                saw_text = True
        elif role == "assistant" and ctype == "tool_use" and c.get("name") == "Skill":
            skill_calls[c.get("id")] = c.get("input") or {}
        elif role == "assistant" and ctype == "tool_use" and c.get("name") == "AskUserQuestion":
            qs = (c.get("input") or {}).get("questions", [])
            pending_q[c.get("id")] = (qs, ts, False)
            boxes.append((ts, ", ".join(q.get("header", "") for q in qs), saw_text, msg.get("id")))
            rows.append(("Claude asks", ts, box_text(qs), False))
        elif role == "user" and ctype == "tool_result":
            tid = c.get("tool_use_id")
            name = tool_names.get(tid) or "?"
            res = result_text(c)
            kind, words = rejection_words(res)       # words the user typed on rejecting any tool call
            what = ("the plan" if name == "ExitPlanMode" else "the question box" if name == "AskUserQuestion"
                    else "the %s tool call" % name)
            if tid in pending_q and pending_q[tid][2]:   # box asked before --since, answered after: show it too
                rows.append(("Claude asks (before this part)", pending_q[tid][1], box_text(pending_q[tid][0]), False))
            if kind == "user":
                add_user(ts, words, USER + " (on rejecting %s)" % what)
                turn += 1
                saw_text = False
                continue
            if kind == "not-user":
                note = ("(chose to talk about the question box instead of answering; the words are in the next "
                        "message)" if words.startswith(CLARIFY) else "(declined %s: \"%s\", no words typed)" % (what, words))
                rows.append((USER, ts, note, False))
                saw_text = False
                continue
            if "doesn't want to proceed with this tool use" in res:
                if name in ("ExitPlanMode", "AskUserQuestion"):
                    rows.append((USER, ts, "(declined %s with no words; any reply is in the next message)" % what,
                                 False))
                    saw_text = False
                continue
            if tid not in pending_q:
                continue
            if hook_denial(rec, res):              # a hook stopped the box before the user saw it: its text, not theirs
                rows.append((NOT_USER, ts, res.strip()[:500], False))
                continue
            qs = pending_q[tid][0]
            res = result_text(c, " ")              # answer text as one line, as before
            saw_text = False
            tur = rec.get("toolUseResult") if isinstance(rec.get("toolUseResult"), dict) else {}
            answers = tur.get("answers") if isinstance(tur.get("answers"), dict) else {}
            notes = tur.get("annotations") if isinstance(tur.get("annotations"), dict) else {}
            parts = []
            for i, q in enumerate(qs):            # every answer, under its own question
                qt = q.get("question", "")
                ans = answers.get(qt)
                if ans is None:                   # no structured answers: cut the result text at the next question
                    start = res.find('"%s"="' % qt)
                    if start >= 0:
                        rest = res[start + len(qt) + 4:]
                        ends = [rest.find('", "%s"="' % q2.get("question", "")) for q2 in qs[i + 1:]]
                        ends = [e for e in ends if e >= 0] + [rest.rfind('". You can now'), len(rest)]
                        ans = rest[:min(e for e in ends if e >= 0)]
                note = (notes.get(qt) or {}).get("notes") if isinstance(notes.get(qt), dict) else None
                parts.append((i, q.get("header", ""), None if ans is None else
                              str(ans).strip() + (" (note: %s)" % note if note else "")))
            if all(a is None for _, _, a in parts):
                m = re.findall(r'"=("?)(.*?)\1(?:, "|\. You can now)', res, re.S)
                ans = "; ".join(x[1] for x in m) if m else res[-1500:].strip()
            elif len(qs) == 1:
                ans = parts[0][2]
            else:                                 # numbered by question, header always shown
                ans = "\n\n".join("**A%d (%s):** %s" % (i + 1, h, "(no answer recorded)" if a is None else a)
                                  for i, h, a in parts)
            rows.append((ANSWERS, ts, ans, False))

# queued messages carry the time the user sent them; put every entry in time order (stable for ties)
last = ""
keyed = []
for i, r in enumerate(rows):
    last = r[1] or last
    keyed.append((last, i, r))
rows = [r for _, _, r in sorted(keyed)]

# Drop Claude's short mid-turn progress lines (the next entry is more Claude text in the same turn).
# Kept: a line with a bold claim (Claude bolds the sentence that matters most), and Claude's first chat entry
# after any user message or answer (a short direct reply is not a progress line).
dropped = 0
if not args.keep_progress:
    kept = []
    reply_due = False
    for i, r in enumerate(rows):
        if r[0] in (USER, ANSWERS) or r[0].startswith(USER + " ("):
            reply_due = True
        elif r[0] == "Claude" and reply_due:
            reply_due = False
            kept.append(r)
            continue
        nxt = rows[i + 1] if i + 1 < len(rows) else None
        if (r[0] == "Claude" and nxt and nxt[0] == "Claude" and len(r[2]) < PROGRESS_MAX and "**" not in r[2]
                and turn_of.get(id(r)) == turn_of.get(id(nxt))):
            dropped += 1
            continue
        kept.append(r)
    rows = kept

# Turns where Claude's chat text may not have reached the user's screen
flags, sig_mids = [], set()
for mid in msg_order:                          # signature: 2+ thinking blocks, no text block, then a tool call
    blocks = msgs[mid]
    types = [c.get("type") for _, c in blocks]
    if types.count("thinking") >= 2 and "text" not in types and "tool_use" in types:
        tool = [c for _, c in blocks if c.get("type") == "tool_use"][0]
        name = tool.get("name")
        if name == "AskUserQuestion":
            name = 'question box "%s"' % ", ".join(q.get("header", "") for q in (tool.get("input") or {}).get("questions", []))
        th = [c.get("thinking", "") for _, c in blocks if c.get("type") == "thinking"][-1]
        sig_mids.add(mid)
        flags.append((blocks[0][0], "before %s: hidden reasoning only, no chat text. Start of the hidden text: \"%s\""
                      % (name, norm(th)[:200])))
for ts, header, had_text, mid in boxes:             # a question box with no visible text in its turn
    if not had_text and mid not in sig_mids:
        flags.append((ts, 'question box "%s": no chat text since the user\'s last message or answer' % header))
flags.sort()

appending = os.path.exists(out) and since is not None
body = []
for who, ts, t, _ in rows:
    body.append("### %s  (%s UTC)\n\n%s\n\n" % (who, ts[:16].replace("T", " "), t))
shown_user = sum(1 for who, _, _, is_user in rows if is_user)
if bad_lines:
    verdict = "NOT CHECKED: %d unreadable lines" % len(bad_lines)
elif not has_origin:
    verdict = "not checked: no origin fields"
else:
    verdict = "match" if raw_user == shown_user else "MISMATCH"
if before_user and verdict == "match":          # never a plain "match" while user messages sit before the cut
    verdict = "match for this part, but %d of the user's messages are before --since: see the warning" % before_user
warnings = []
if bad_lines:
    warnings.append("WARNING: %d unreadable lines in the session file (line numbers: %s%s). The user's messages on "
                    "those lines may be missing from this transcript; the count check is NOT CHECKED.%s"
                    % (len(bad_lines), ", ".join(str(n) for n in bad_lines[:20]), ", ..." if len(bad_lines) > 20 else "",
                       " The last line is cut short: the session may still be writing it; run the script again in a "
                       "moment." if last_line_partial else ""))
if before_user:
    warnings.append("WARNING: %d of the user's messages are before --since %s UTC and are left out of this part. "
                    "If the transcript does not already hold them (an earlier part of this session), the --since value "
                    "is wrong: it is UTC, for example the session file's first \"timestamp\" value."
                    % (before_user, since.replace("T", " ")))
check = ["### Script checks (written by condense_transcript.py)\n\n",
         "- The user's messages: %d in the raw session file%s, %d in this transcript: %s.\n"
         % (raw_user, "" if has_origin else " (no origin fields in this file: count not available)", shown_user,
            verdict if verdict != "MISMATCH" else "MISMATCH, check by hand"),
         "- Claude's short mid-turn progress lines dropped: %d.\n" % dropped,
         "- Possibly not shown to the user (an upper bound; some are ordinary reasoning): %d.\n" % len(flags)]
for ts, what in flags:
    check.append("  - %s UTC%s %s\n" % (ts[11:19], "" if args.utc else " (%s local)" % local_hm(ts), what))
for w in warnings:
    check.append("- %s\n" % w)

with open(out, "a" if appending else "w", encoding="utf-8") as f:
    if appending:          # an existing transcript: add this session below the earlier ones, never overwrite them
        f.write("\n## Session from %s UTC\n\nSource: `%s`.\n\n" % (since.replace("T", " "), src))
    else:
        f.write("# Condensed conversation transcript\n\nSource: `%s`. Tool calls, tool output and Claude's short "
                "mid-turn progress lines removed; the user's messages (headed \"User\"), Claude's chat replies and every "
                "question with its answers kept, in time order.\n\n" % src)
        if since is not None:
            f.write("## Session from %s UTC\n\nSource: `%s`.\n\n" % (since.replace("T", " "), src))
    f.write("".join(body))
    f.write("".join(check) + "\n")
for w in warnings:
    sys.stderr.write(w + "\n")
print(out, len(rows), "entries")
print("User messages: raw %d, transcript %d (%s); progress lines dropped: %d; "
      "possibly not shown: %d%s" % (raw_user, shown_user, verdict, dropped, len(flags),
                                    "; before --since: %d (left out)" % before_user if since is not None else ""))
