"""Stamp pinned OmniVoice builds with upstream and app version macros."""
import re
from pathlib import Path


def stamp_version(source: Path, commit: str) -> Path:
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Invalid pinned OmniVoice commit")
    version_file = Path(source) / "tools" / "version.cmake"
    content = (
        'set(CONTENT [=[#pragma once\n'
        f'#define OMNIVOICE_VERSION "{commit} (pinned)"\n'
        f'#define VOICEBLUEPRINT_VERSION "{commit} (pinned)"\n'
        ']=])\n'
        'if(EXISTS "${OUTPUT}")\n'
        '  file(READ "${OUTPUT}" EXISTING)\n'
        '  if("${EXISTING}" STREQUAL "${CONTENT}")\n'
        '    return()\n'
        '  endif()\n'
        'endif()\n'
        'file(WRITE "${OUTPUT}" "${CONTENT}")\n'
    )
    version_file.write_text(content, encoding="utf-8")
    return version_file
