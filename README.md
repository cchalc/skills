# Awesome Claude Code Skills

A collection of custom skills for Claude Code. Each skill extends Claude Code's capabilities for specific workflows.

## Installation

To use a skill, copy it to your Claude Code skills directory:

```bash
cp -r skills/<skill-name> ~/.claude/skills/
```

Then configure the skill by copying `.env.example` to `.env` and editing the values.

## Skills

| Skill | Description |
|-------|-------------|
| [transcribe-recordings](skills/transcribe-recordings/) | Transcribe audio recordings from Obsidian attachments and create structured markdown notes |

## Structure

```
skills/
├── README.md                    # This file
├── .gitignore
└── skills/
    └── <skill-name>/
        ├── SKILL.md             # Skill definition (required)
        ├── README.md            # Documentation
        ├── .env.example         # Configuration template
        ├── scripts/             # Implementation scripts
        ├── templates/           # Templates used by the skill
        └── references/          # Reference documentation
```

## Creating New Skills

1. Create a new directory under `skills/`
2. Add a `SKILL.md` with frontmatter defining the skill:
   ```yaml
   ---
   name: my-skill
   description: |
     What this skill does...
   trigger_phrases:
     - trigger phrase 1
     - trigger phrase 2
   ---
   ```
3. Add implementation in `scripts/`
4. Document usage in `README.md`
5. Provide `.env.example` for configuration

## License

MIT
