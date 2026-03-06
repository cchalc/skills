# Transcribe Recordings Skill

Automatically transcribe voice recordings from your Obsidian vault's attachments folder and generate well-structured, intelligently organized markdown notes.

## Quick Start

```bash
# 1. Set your Anthropic API key in .env
nano ~/.claude/skills/transcribe-recordings/.env
# Set ANTHROPIC_API_KEY=sk-ant-...

# 2. Run the skill
/transcribe-recordings
```

## Features

### Core Capabilities
- **Audio Transcription**: Uses Whisper AI to convert recordings to text
- **Intelligent Analysis**: Claude API analyzes content for categorization
- **Smart Naming**: Files named based on content (e.g., `20260303-databricks-apps-growth.md`)
- **Auto-Categorization**: Places notes in appropriate folders
- **Batch Processing**: Processes all recordings at once
- **Storage Optimization**: Deletes originals after transcription (configurable)

### Supported Formats
- `.webm` (Obsidian voice recordings)
- `.mp3`
- `.m4a`
- `.wav`
- `.ogg`

### Folder Placement Logic
Notes are automatically placed in:
- **training/**: Databricks features, technical topics, presentations, keynotes
- **work/**: Meetings, client work, planning sessions, team discussions
- **transcripts/**: Unclear or mixed content (fallback default)

### Generated Note Structure

```markdown
---
date: 2026-03-03
type: training
tags: [databricks, apps, serverless]
---

# Databricks Apps Introduction

## Overview
2-3 sentence summary of the content...

## Key Points
- Main point 1
- Main point 2
- Main point 3

## Transcript
Full transcription of the audio...

## Related Topics
- [[related-note-1]]
- [[related-note-2]]

## Actions
- [ ] Action item 1
- [ ] Action item 2

## Tags
#databricks #apps #serverless

---
*Transcribed: 2026-03-03*
```

## Configuration

### Environment Variables

Edit `~/.claude/skills/transcribe-recordings/.env`:

```bash
# Required: Your Anthropic API key
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Required: Path to your Obsidian vault
VAULT_PATH=/path/to/vault

# Optional: Custom paths (defaults shown)
WHISPER_PATH=/Users/christopher.chalcraft/.local/bin/whisper
FFMPEG_PATH=/Users/christopher.chalcraft/.local/bin/ffmpeg

# Optional: Delete recordings after transcription (default: true)
DELETE_AFTER_TRANSCRIBE=true

# Optional: Phase 2 feature (default: false)
AUTO_WATCH_ENABLED=false
```

## Installation

### Dependencies

1. **Whisper AI** (required)
   ```bash
   uv tool install openai-whisper
   ```

2. **FFmpeg** (required by Whisper)
   ```bash
   brew install ffmpeg
   ```

3. **Python packages** (auto-installed)
   - Already set up in `.venv/`
   - anthropic
   - python-dotenv
   - watchdog

### Verify Installation

```bash
# Check Whisper
whisper --help

# Check FFmpeg
ffmpeg -version

# Check Python environment
~/.claude/skills/transcribe-recordings/.venv/bin/python --version
```

## Usage

### Manual Mode (Recommended)

```bash
# Process all recordings in attachments/
/transcribe-recordings
```

This will:
1. Find all recordings in `attachments/`
2. Transcribe each using Whisper
3. Analyze content with Claude API
4. Create markdown notes
5. Delete original recordings (if configured)

### Expected Output

```
✓ Checking dependencies...
✓ Found 3 recording(s) in attachments/

Processing Recording 20260303121928.webm...
  - Transcribing... (156 chars)
  - Analyzing content... ✓
  - Creating markdown... ✓
  - Created: training/20260303-databricks-apps-intro.md
  - Cleaned up recording ✓

Processing Recording 20260303121946.webm...
  - Transcribing... (342 chars)
  - Analyzing content... ✓
  - Creating markdown... ✓
  - Created: training/20260303-databricks-apps-growth.md
  - Cleaned up recording ✓

============================================================
Summary:
- 2 recording(s) processed successfully
- 0 error(s)
- Total time: 1 minutes 45 seconds
- Notes created in: training/ (2)
============================================================
```

## Performance

- **Processing time**: ~2-3 minutes per 1-minute recording
  - Whisper transcription: ~1x audio length
  - Content analysis: ~3-5 seconds
- **Storage savings**: ~98% (500KB recording → 3KB markdown)
- **API costs**: ~$0.01-0.03 per recording (Claude analysis)

## Troubleshooting

### "Whisper not found"
```bash
uv tool install openai-whisper
# Verify installation
which whisper
```

### "FFmpeg not found"
```bash
brew install ffmpeg
# Verify installation
which ffmpeg
```

### "ANTHROPIC_API_KEY not set"
Edit `.env` and add your API key:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Empty transcripts
- Check audio quality (recording should contain clear speech)
- Original file will NOT be deleted if transcript is empty
- Review recording manually

### Content analysis fails
- Script falls back to basic categorization
- Notes placed in `transcripts/` folder
- Check API key is valid

### Duplicate filenames
- Script automatically appends `-2`, `-3`, etc.
- No overwrites occur

## File Structure

```
~/.claude/skills/transcribe-recordings/
├── SKILL.md                    # Skill definition
├── README.md                   # This file
├── .env                        # Configuration (not committed)
├── .env.example                # Example configuration
├── .venv/                      # Python virtual environment
├── scripts/
│   ├── transcribe.py          # Main orchestration
│   ├── analyze_content.py     # Claude API analysis
│   └── requirements.txt       # Python dependencies
├── templates/
│   └── note_template.md       # Markdown template
└── references/
    └── (documentation)
```

## Advanced Features (Phase 2)

### Automatic File Watching

Enable automatic processing of new recordings:

1. Set `AUTO_WATCH_ENABLED=true` in `.env`
2. Create launchd agent (instructions TBD)
3. New recordings will auto-process

This is an optional enhancement for a hands-free workflow.

## Examples

### Input Recording
- File: `attachments/Recording 20260303121928.webm`
- Duration: 45 seconds
- Content: Discussion about Databricks Apps

### Generated Note
- File: `training/20260303-databricks-apps-intro.md`
- Size: ~2KB
- Contains: Summary, key points, full transcript, tags, backlinks

## Limitations

- Requires internet connection (Whisper runs locally, but Claude API needs connectivity)
- Best results with clear audio and English speech
- Multi-speaker recordings not separated (future enhancement)
- Single language per recording (multi-language support future)

## Security

- API keys stored in `.env` (not committed to git)
- Recordings processed locally with Whisper
- Only transcript text sent to Claude API (not audio)

## Future Enhancements

- Speaker diarization for multi-person recordings
- Multi-language support
- Custom categorization rules
- Quality scoring for transcript confidence
- Selective transcription (choose which to process)
- Integration with Obsidian metadata
- Real-time processing via file watcher

## Support

For issues or questions:
1. Check troubleshooting section above
2. Verify dependencies installed
3. Review `.env` configuration
4. Check logs for specific errors
