#!/usr/bin/env python3
"""
Helper script to update transcription log with output file paths.
Updates the markdown log in Obsidian vault.
"""

import sys
from pathlib import Path
from datetime import datetime


def update_log_with_output(log_file: Path, audio_filename: str, output_file: Path, vault_path: Path):
    """Update markdown log entry to include output file path as a link."""
    try:
        if not log_file.exists():
            return

        # Read current log content
        content = log_file.read_text(encoding="utf-8")

        # Find the entry for this audio file
        search_str = f"**Audio File:** `{audio_filename}`"

        if search_str not in content:
            return

        # Create the output note link
        output_relative = output_file.relative_to(vault_path)
        output_link = f"[[{output_relative.parent.name}/{output_relative.stem}]]"

        # Replace "Not created" with the actual link
        content = content.replace(
            f"{search_str}\n**Output Note:** *Not created*",
            f"{search_str}\n**Output Note:** {output_link}"
        )

        # Write updated content
        log_file.write_text(content, encoding="utf-8")

    except Exception as e:
        print(f"Warning: Failed to update log: {e}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: update_log.py <log_file> <audio_filename> <output_file> <vault_path>")
        sys.exit(1)

    log_file = Path(sys.argv[1])
    audio_filename = sys.argv[2]
    output_file = Path(sys.argv[3])
    vault_path = Path(sys.argv[4])

    update_log_with_output(log_file, audio_filename, output_file, vault_path)
