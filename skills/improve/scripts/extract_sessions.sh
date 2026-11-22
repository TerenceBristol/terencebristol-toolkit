#!/bin/bash
# extract_sessions.sh: the /improve history scan extractor. Fix this file when it fails; never write a copy.
# Run it with bash (a downloaded copy may lose its run permission). Needs jq.
#
# Usage: bash extract_sessions.sh <sessions-dir> <out-dir> <since-UTC, e.g. 2026-01-15T13:22:34> <uuid>...
# Writes <out-dir>/extract-<first-date>-<uuid>.txt per session and prints "<uuid> <date> <bytes>".
# Lines: USER: (typed text), USER-CMD <command>: (text typed after a slash command),
# USER-CMD <command> (a bare slash command with no text after it),
# USER-ANSWER: (question-box and plan-approval results, matched by tool_use_id), ASSISTANT: (chat text),
# USER-MIDTURN: (text typed while Claude was working: attachment queued_command with commandMode
# "prompt" and a human origin or no origin field; task notifications use the same type and are never kept).
# Timestamps in session files are UTC; convert the run-log anchor to UTC before passing it.
set -u
[ $# -lt 4 ] && { echo "usage: $0 <sessions-dir> <out-dir> <since-UTC> <uuid>..." >&2; exit 2; }
DIR="$1"; OUT="$2"; SINCE="$3"; shift 3
mkdir -p "$OUT"
for U in "$@"; do
  F="$DIR/$U.jsonl"
  [ -f "$F" ] || { echo "$U missing" >&2; continue; }
  IDS=$(jq -r 'select(.type=="assistant") | .message.content[]? | select(.type=="tool_use" and (.name=="AskUserQuestion" or .name=="ExitPlanMode")) | .id' "$F" | sort -u | jq -R . | jq -s .)
  FIRST=$(jq -r 'select(.timestamp!=null) | .timestamp' "$F" | head -1 | cut -c1-10)
  jq -r --argjson ids "$IDS" --arg since "$SINCE" '
    def cmd($s):
      (($s | [capture("<command-name>(?<n>[^<]*)</command-name>")] | .[0].n) // "") as $n |
      (($s | [capture("<command-args>(?<a>[\\s\\S]*?)</command-args>")] | .[0].a) // "") as $a |
      (if ($a|length)>0 then "USER-CMD \($n): \($a)"
       elif ($n|length)>0 then "USER-CMD \($n)"
       else empty end);
    def usertext($s; $ts):
      if ($s|startswith("<command-")) then cmd($s)
      elif ($s|test("^<(system-reminder|local-command|task-notification)")) then empty
      else "[\($ts[0:16])] USER: \($s)" end;
    select(.timestamp != null and .timestamp >= $since) |
    .timestamp as $ts |
    if .type=="user" and (.isMeta != true) then
      (.message.content) as $c |
      if ($c|type)=="string" then usertext($c; $ts)
      else
        ($c[] |
          if .type=="text" then usertext(.text; $ts)
          elif .type=="tool_result" and ((.tool_use_id) as $t | $ids | index($t)) != null then
            "USER-ANSWER: " + (if (.content|type)=="string" then .content else ([.content[]? | select(.type=="text") | .text] | join("\n")) end)
          else empty end)
      end
    elif .type=="attachment" and .attachment.type=="queued_command" and .attachment.commandMode=="prompt"
         and (.attachment.origin == null or ((.attachment.origin|type)=="object" and .attachment.origin.kind == "human")) then
      (.attachment.prompt) as $p |
      "[\($ts[0:16])] USER-MIDTURN: " + (if ($p|type)=="string" then $p else ([$p[]? | select(.type=="text") | .text] | join("\n")) end)
    elif .type=="assistant" then
      (.message.content[]? | select(.type=="text") | "ASSISTANT: \(.text)")
    else empty end
  ' "$F" > "$OUT/extract-$FIRST-$U.txt"
  echo "$U $FIRST $(wc -c < "$OUT/extract-$FIRST-$U.txt")"
done
