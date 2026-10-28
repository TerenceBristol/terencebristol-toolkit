# Claude Code Memory and Context: Less Is More (Ep. 3)

Video: https://youtu.be/W3idMEb2_IE

Everything from this video, free.

## Items

- [/handoff](../skills/handoff/): writes a handoff file and a kickoff prompt, so a fresh chat picks up your task exactly where the long one stopped. Use it as is, or as inspiration to build your own.
- [/handoff setup prompt](../prompts/handoff-setup/): paste one prompt into Claude Code and it walks you through installing /handoff, asks you a few setup questions, and runs your first handoff.

## Prompts from the video

To use sub-agents (tip 4), tell your Claude:

```
use sub-agents to do X and Y
```

The two guidelines from my CLAUDE.md (tip 4), to add to yours:

```
Parallel: Do things in parallel using different sub-agents where it makes sense and doesn't degrade the quality.
Cost: Use a cheaper model for simple tasks like reading files or searching.
```

[Back to the AI Toolkit](../README.md)
