#!/usr/bin/env python3
"""
Recording transcription script for Obsidian vault.
Transcribes audio recordings with speaker detection and logging.
"""

import os
import sys
import subprocess
import tempfile
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")


@dataclass
class TranscriptData:
    """Data for a single transcript."""
    audio_file: Path
    transcript: str
    duration: float
    success: bool
    error: Optional[str] = None


class RecordingTranscriber:
    """Handles transcription of audio recordings with speaker detection."""

    SUPPORTED_EXTENSIONS = [".webm", ".mp3", ".m4a", ".wav", ".ogg"]

    def __init__(self):
        self.vault_path = Path(os.getenv("VAULT_PATH", ""))
        self.whisper_path = os.getenv("WHISPER_PATH", "whisper")
        self.ffmpeg_path = os.getenv("FFMPEG_PATH", "ffmpeg")
        self.enable_diarization = os.getenv("ENABLE_SPEAKER_DIARIZATION", "true").lower() == "true"

        if not self.vault_path.exists():
            raise ValueError(f"Vault path does not exist: {self.vault_path}")

        # Log file location in Obsidian vault
        self.log_file = self.vault_path / "transcripts" / "transcription-log.md"

        self.attachments_dir = self.vault_path / "attachments"
        if not self.attachments_dir.exists():
            self.attachments_dir.mkdir(parents=True)

        # Ensure transcripts folder exists for log file
        transcripts_dir = self.vault_path / "transcripts"
        if not transcripts_dir.exists():
            transcripts_dir.mkdir(parents=True)

    def log_transcription(self, audio_file: Path, output_file: Optional[Path],
                         transcript: str, success: bool, error: Optional[str] = None):
        """Log transcription details to markdown log file in Obsidian vault."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_only = datetime.now().strftime("%Y-%m-%d")

        # Create log file with header if it doesn't exist
        if not self.log_file.exists():
            header = """---
date: created
type: log
tags: [transcription, automation]
---

# Transcription Log

This file tracks all audio transcriptions processed by the transcribe-recordings skill.

---

"""
            try:
                with open(self.log_file, "w", encoding="utf-8") as f:
                    f.write(header)
            except Exception as e:
                print(f"  ⚠ Failed to create log file: {e}", file=sys.stderr)
                return

        # Format output file as link if it exists
        if output_file:
            output_relative = output_file.relative_to(self.vault_path)
            output_link = f"[[{output_relative.parent.name}/{output_relative.stem}]]"
        else:
            output_link = "*Not created*"

        # Create markdown log entry
        status_icon = "✅" if success else "❌"

        log_entry = f"""## {status_icon} {date_only} - {audio_file.name}

**Timestamp:** {timestamp}
**Audio File:** `{audio_file.name}`
**Output Note:** {output_link}
**Status:** {'Success' if success else 'Failed'}
**Transcript Length:** {len(transcript)} characters
"""

        if error:
            log_entry += f"**Error:** {error}  \n"

        if transcript:
            # Add truncated transcript preview
            preview = transcript[:300].replace('\n', ' ')
            log_entry += f"\n**Preview:** {preview}{'...' if len(transcript) > 300 else ''}  \n"

        log_entry += "\n---\n\n"

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"  ⚠ Failed to write log: {e}", file=sys.stderr)

    def check_dependencies(self) -> Tuple[bool, List[str]]:
        """Check if required dependencies are available."""
        missing = []

        # Check whisper
        try:
            result = subprocess.run(
                [self.whisper_path, "--help"],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                missing.append("whisper")
        except (subprocess.SubprocessError, FileNotFoundError):
            missing.append("whisper")

        # Check ffmpeg
        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                missing.append("ffmpeg")
        except (subprocess.SubprocessError, FileNotFoundError):
            missing.append("ffmpeg")

        return len(missing) == 0, missing

    def find_recordings(self) -> List[Path]:
        """Find all audio recordings in attachments folder."""
        recordings = []
        for ext in self.SUPPORTED_EXTENSIONS:
            recordings.extend(self.attachments_dir.glob(f"*{ext}"))
        return sorted(recordings)

    def add_speaker_labels(self, transcript: str) -> str:
        """
        Add simple speaker labels based on natural conversation patterns.
        Uses heuristics like paragraph breaks and punctuation to identify speaker changes.
        """
        if not self.enable_diarization or not transcript:
            return transcript

        # Split by newlines (Whisper often breaks on natural pauses)
        lines = [line.strip() for line in transcript.split('\n') if line.strip()]

        if len(lines) <= 1:
            # Single speaker likely
            return transcript

        # Apply simple heuristic: alternate speakers on paragraph breaks
        # This works reasonably well for conversations
        labeled_lines = []
        current_speaker = "A"

        for i, line in enumerate(lines):
            # Check if this might be a speaker change:
            # - New paragraph/line break
            # - Starts with capital letter (new thought)
            # - Previous line ended with terminal punctuation

            if i > 0:
                prev_line = lines[i-1]
                # If previous line ends with strong punctuation, likely speaker change
                if prev_line.endswith(('.', '!', '?')) or len(prev_line) < 30:
                    current_speaker = "B" if current_speaker == "A" else "A"

            labeled_lines.append(f"**Speaker {current_speaker}:** {line}")

        return "\n\n".join(labeled_lines)

    def transcribe_audio(self, audio_file: Path) -> Optional[str]:
        """
        Transcribe audio file using Whisper.
        Returns transcript text or None on failure.
        """
        try:
            # Create temporary directory for whisper output
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Run whisper with verbose output to get better segmentation
                cmd = [
                    self.whisper_path,
                    str(audio_file),
                    "--model", "base",
                    "--output_dir", str(temp_path),
                    "--output_format", "txt",
                    "--verbose", "False"
                ]

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 minute timeout
                )

                if result.returncode != 0:
                    print(f"  ⚠ Whisper error: {result.stderr}", file=sys.stderr)
                    return None

                # Read transcript from temporary file
                txt_file = temp_path / f"{audio_file.stem}.txt"
                if not txt_file.exists():
                    print(f"  ⚠ Transcript file not created", file=sys.stderr)
                    return None

                transcript = txt_file.read_text(encoding="utf-8").strip()

                # Validate transcript
                if not transcript or len(transcript) < 10:
                    print(f"  ⚠ Transcript too short or empty", file=sys.stderr)
                    return None

                # Add speaker labels if enabled
                if self.enable_diarization:
                    transcript = self.add_speaker_labels(transcript)

                return transcript

        except subprocess.TimeoutExpired:
            print(f"  ⚠ Transcription timeout (>10 minutes)", file=sys.stderr)
            return None
        except Exception as e:
            print(f"  ⚠ Transcription error: {e}", file=sys.stderr)
            return None

    def get_existing_notes(self) -> List[str]:
        """Get list of existing note filenames for context."""
        notes = []
        search_folders = ["training", "work", "transcripts", "dailynotes"]

        for folder in search_folders:
            folder_path = self.vault_path / folder
            if folder_path.exists():
                for md_file in folder_path.glob("*.md"):
                    note_name = md_file.stem
                    # Try to remove YYYYMMDD- prefix if present
                    if len(note_name) > 9 and note_name[8] == "-":
                        note_name = note_name[9:]
                    notes.append(note_name)

        return notes[:50]  # Limit for context

    def transcribe_all(self) -> List[TranscriptData]:
        """Transcribe all recordings and return data for Claude Code to process."""
        # Check dependencies
        print("✓ Checking dependencies...")
        deps_ok, missing = self.check_dependencies()
        if not deps_ok:
            print(f"\n❌ Missing dependencies: {', '.join(missing)}")
            print("\nInstallation instructions:")
            if "whisper" in missing:
                print("  - Whisper: uv tool install openai-whisper")
            if "ffmpeg" in missing:
                print("  - FFmpeg: brew install ffmpeg")
            sys.exit(1)

        # Find recordings
        recordings = self.find_recordings()
        if not recordings:
            print("\n✓ No recordings found in attachments/")
            return []

        diarization_status = "enabled" if self.enable_diarization else "disabled"
        print(f"✓ Found {len(recordings)} recording(s) in attachments/")
        print(f"✓ Speaker diarization: {diarization_status}\n")

        # Transcribe each recording
        results = []

        for recording in recordings:
            print(f"Processing {recording.name}...")
            print(f"  - Transcribing...", end=" ", flush=True)

            start_time = datetime.now()
            transcript = self.transcribe_audio(recording)
            duration = (datetime.now() - start_time).total_seconds()

            if transcript:
                print(f"✓ ({len(transcript)} chars)")
                results.append(TranscriptData(
                    audio_file=recording,
                    transcript=transcript,
                    duration=duration,
                    success=True
                ))

                # Log successful transcription (output file will be added later by Claude)
                self.log_transcription(recording, None, transcript, True)
            else:
                print(f"✗ Failed")
                results.append(TranscriptData(
                    audio_file=recording,
                    transcript="",
                    duration=duration,
                    success=False,
                    error="Transcription failed"
                ))

                # Log failed transcription
                self.log_transcription(recording, None, "", False, "Transcription failed")

        return results


def main():
    """Main entry point - transcribe and output JSON for Claude Code."""
    try:
        transcriber = RecordingTranscriber()
        results = transcriber.transcribe_all()

        if not results:
            sys.exit(0)

        # Get existing notes for context
        existing_notes = transcriber.get_existing_notes()

        # Output JSON for Claude Code to process
        print("\n" + "="*60)
        print("TRANSCRIPTION_DATA_START")

        output = {
            "vault_path": str(transcriber.vault_path),
            "log_file": str(transcriber.log_file),
            "existing_notes": existing_notes,
            "speaker_diarization_enabled": transcriber.enable_diarization,
            "transcripts": [
                {
                    "audio_file": str(r.audio_file),
                    "filename": r.audio_file.name,
                    "transcript": r.transcript,
                    "success": r.success,
                    "error": r.error
                }
                for r in results
            ]
        }

        print(json.dumps(output, indent=2))
        print("TRANSCRIPTION_DATA_END")
        print("="*60)

        print(f"\n✓ Log file: {transcriber.log_file}")

        # Exit with error if any failed
        if any(not r.success for r in results):
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
