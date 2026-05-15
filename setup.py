"""Package metadata and legacy setup shim.

This file intentionally contains no runtime side-effects. Build and
installation metadata are provided in `pyproject.toml`. Runtime setup
tasks (database creation, seeding, etc.) are handled by the container
entrypoint or explicit developer scripts, not during package build.
"""

from pathlib import Path

# Keep a minimal shim so legacy tooling that expects `setup.py` to exist
# won't fail. Do not perform any actions on import or execution.

__all__ = ["Path"]
