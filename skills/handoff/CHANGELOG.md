# Changelog

All notable changes to the `/handoff` skill are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/).

## [1.2.0] - 2026-10-31

### Changed
- No kickoff prompt for finished work: the handoff alone is written, and the report says no kickoff is needed.
- One kickoff file per next chat, with no second copies beside it, and no repeat of the state the handoff already holds.

## [1.1.0] - 2026-10-29

### Changed
- Step 2 asks only the questions whose answer would change the handoff; settled answers are taken and listed for the user to overrule.

## [1.0.0] - 2026-10-27

### Added
- First public version: a handoff file, a saved plan, a kickoff prompt and a self-review, plus a script that turns a Claude Code session log into a transcript of your exact words.
