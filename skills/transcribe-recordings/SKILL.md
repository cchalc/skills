---
name: transcribe-recordings
description: |
  Transcribe audio recordings from Obsidian attachments folder and create
  structured markdown notes. Uses Whisper AI for transcription and Claude Code
  for intelligent content analysis, categorization, tags, and related backlinks.
  Supports .webm, .mp3, .m4a formats. Use when you want to process
  voice recordings into organized notes. No separate API key required.
trigger_phrases:
  - transcribe recordings
  - process audio recordings
  - convert recordings to notes
  - transcribe voice memos
---

# Transcribe Recordings

Automatically transcribe voice recordings from your Obsidian vault's attachments folder and generate well-structured, intelligently organized markdown notes using Claude Code.

## Usage

```bash
/transcribe-recordings
```

This will:
1. Find all audio recordings (.webm, .mp3, .m4a) in the attachments/ folder
2. Transcribe each using Whisper AI (runs locally)
3. Pass transcripts to Claude Code for intelligent analysis
4. Claude Code creates Obsidian-formatted markdown with tags, backlinks, and frontmatter
5. Save notes using `YYYYMMDD-descriptive-name.md` format
6. Archive in appropriate folders (training/, work/, transcripts/)
7. Delete original recordings to save space (configurable)

**No separate API key needed** - uses your active Claude Code session!

## Requirements

- **Whisper AI**: For audio transcription
  ```bash
  uv tool install openai-whisper
  ```

- **FFmpeg**: Required by Whisper for audio processing
  ```bash
  brew install ffmpeg
  ```

- **Python dependencies**: Installed automatically
  - python-dotenv
  - watchdog (for automation)

## Configuration

Edit `~/.claude/skills/transcribe-recordings/.env`:

```bash
VAULT_PATH=/path/to/your/obsidian/vault
WHISPER_PATH=/Users/your-user/.local/bin/whisper
FFMPEG_PATH=/Users/your-user/.local/bin/ffmpeg
DELETE_AFTER_TRANSCRIBE=true
AUTO_WATCH_ENABLED=false
```

**Note**: No API key required - analysis happens through Claude Code!

## Features

### Intelligent Content Analysis
- **Smart naming**: Files named based on content (e.g., `20260303-databricks-apps-growth.md`)
- **Auto-categorization**: Places notes in appropriate folders
  - `training/`: Databricks features, tech topics, presentations
  - `work/`: Meetings, client work, planning
  - `transcripts/`: Mixed or unclear content (fallback)
- **Relevant tags**: Extracted from transcript content
- **Backlinks**: Automatically links to related existing notes
- **Summary**: 2-3 sentence overview at the top
- **Action items**: TODOs converted to checkboxes

### Note Structure
Generated notes include:
- YAML frontmatter (date, type, tags)
- Overview/summary section
- Key points as bullets
- Full transcript with sections
- Related topics with backlinks
- Action items as checkboxes
- Tags at bottom

### Batch Processing
- Processes all pending recordings in one command
- Each recording becomes a separate note
- Handles duplicate filenames automatically
- Progress indicators for each step

## Performance

- ~30-60 seconds per 1-minute recording (Whisper transcription)
- Storage savings: ~98% (500KB recording → 3KB markdown)
- No additional API costs - uses your Claude Code session

## Optional: Automation (Phase 2)

Enable automatic processing of new recordings:

1. Set `AUTO_WATCH_ENABLED=true` in `.env`
2. Install launchd agent:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.claude.transcribe-recordings.plist
   ```

This monitors the attachments/ folder and auto-processes new recordings.

## Troubleshooting

### "Whisper not found"
Install using: `uv tool install openai-whisper`

### "FFmpeg not found"
Install using: `brew install ffmpeg`

### Empty transcripts
- Check audio quality
- Ensure recording contains speech
- Original file will NOT be deleted if transcript is empty

## Examples

**Input:** `attachments/Recording 20260303121928.webm`

**Output:** `training/20260303-databricks-apps-intro.md`

```markdown
---
date: 2026-03-03
type: training
tags: [databricks, apps, serverless]
---

# Databricks Apps Introduction

## Overview
Discussion of Databricks Apps capabilities, focusing on serverless
deployment and integration with Unity Catalog.

## Key Points
- Apps support React and FastAPI frameworks
- Serverless compute handles scaling automatically
- Built-in OAuth integration with Unity Catalog

## Transcript
[Full transcription...]

## Related Topics
- [[databricks-serverless]]
- [[unity-catalog-overview]]

## Actions
- [ ] Review Apps documentation
- [ ] Test sample deployment

## Tags
#databricks #apps #serverless

---
*Transcribed: 2026-03-03*
```
