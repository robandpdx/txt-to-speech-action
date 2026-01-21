"""Minimal speech library scaffolding for the txt-to-speech composite action."""
from pathlib import Path

from .library import synthesize_text_file

_PACKAGE_ROOT = Path(__file__).resolve().parent
_REPO_ROOT = _PACKAGE_ROOT.parent

# Default location the action expects for host/guest scripts.
SCRIPTS_ROOT = (_REPO_ROOT / "scripts").resolve()

__all__ = ["SCRIPTS_ROOT", "synthesize_text_file"]
