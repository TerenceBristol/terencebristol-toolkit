# /improve: hook findings

Read from SKILL.md Step 5 when a broken rule is one a script can check.

A new hook always goes through a plan, never the findings page alone.
- **When to propose one.** A rule is a hook candidate when a script can see the breach in a tool call or a written file (a command, a path, a file name, a word list, a missing field), because a hook acts on every call while a written rule can be missed. Propose it after the first miss only for outward or irreversible actions; otherwise after two failures. Prefer a block over a reminder note.
- **The card** offers three picks, "Convert to hook" recommended for checkable rules: **Convert to hook** (the generated config on the card); **Clarify rule** (the rule plus a short "because", moved to the file and section the work reads; "never" only for hard limits); **Both** (the clarified rule, with the hook as backup). After "Convert to hook", ask which settings file it goes in: project `.claude/settings.json`, global `~/.claude/settings.json`, or project local `.claude/settings.local.json`.
- **Generate the full implementation.** Pick the event: `PreToolUse` with the `Bash` matcher for command rules; `PreToolUse` with the tool's matcher for tool-specific rules; `PostToolUse` for checks after a tool runs; `Notification` for reminders. Write the settings JSON ready to paste, and the script that enforces the rule. **Paths with spaces:** quote the script path in the command (`bash '/path with spaces/hook.sh'`), because a bare path splits into separate arguments.

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash", "hooks": [ { "type": "command", "command": "bash '/abs/path/hook.sh'" } ] }
    ]
  }
}
```

- **Hook and skill link.** When the hook enforces a rule that belongs to a skill, put the hook's rule list in a file inside that skill's folder (a hook tied to a CLAUDE.md rule keeps its list in one shared folder); name the skill in the hook's header comment and the hook in the skill; add a test file with realistic legitimate inputs that contain the blocked pattern and must pass. Never put hooks in skill frontmatter, because skills are often read as files, not invoked, and frontmatter hooks run only on invocation.
