"""Shared state locations for the Skill Seekers web UI.

All UI-level state lives under ``~/.skill-seekers/ui/`` so the web layer
never writes into the user's project workspace except through the normal
toolchain outputs (``output/``, ``configs/``).
"""

from __future__ import annotations

import json
import os
import tempfile
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from collections.abc import Callable

UI_STATE_DIR = Path(os.environ.get("SKILL_SEEKERS_UI_DIR", Path.home() / ".skill-seekers" / "ui"))

PROJECTS_FILE = UI_STATE_DIR / "projects.json"
JOBS_FILE = UI_STATE_DIR / "jobs.json"
ACTIVITY_FILE = UI_STATE_DIR / "activity.json"
SKILLS_META_FILE = UI_STATE_DIR / "skills.json"
SETTINGS_FILE = UI_STATE_DIR / "settings.json"
TRASH_DIR = UI_STATE_DIR / "trash"
MARKET_CACHE_DIR = UI_STATE_DIR / "marketplace_cache"

DEFAULT_SETTINGS: dict[str, Any] = {
    "output_dir": "output",
    "configs_dir": "configs",
    "default_agent": "claude",
    "auto_upload": False,
    "publish_configs": False,
    "watch_mode": False,
    "enabled_clis": [],
}

_state_lock = threading.RLock()
_transaction = threading.local()


@contextmanager
def state_transaction():
    """Serialize state transactions across threads and runner processes."""
    with _state_lock:
        if getattr(_transaction, "active", False):
            yield
            return
        ensure_dirs()
        with open(UI_STATE_DIR / ".state.lock", "a+b") as lock:
            if os.name == "nt":
                import msvcrt

                lock.seek(0, os.SEEK_END)
                if lock.tell() == 0:
                    lock.write(b"0")
                    lock.flush()
                lock.seek(0)
                # LK_LOCK gives up after ~10 s; poll LK_NBLCK so this blocks
                # like the POSIX flock(LOCK_EX) branch instead of raising.
                while True:
                    try:
                        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
                        break
                    except OSError:
                        time.sleep(0.05)
            else:
                import fcntl

                fcntl.flock(lock, fcntl.LOCK_EX)
            _transaction.active = True
            try:
                yield
            finally:
                _transaction.active = False
                if os.name == "nt":
                    lock.seek(0)
                    msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(lock, fcntl.LOCK_UN)


def workspace_dir(root: Path, kind: str) -> Path:
    """Resolve configured output/config paths relative to the workspace."""
    value = load_settings().get(f"{kind}_dir") or kind
    return (root / Path(value).expanduser()).resolve()


def contained(base: Path, *parts: str) -> Path:
    """Join ``parts`` under ``base`` and refuse anything that escapes it."""
    root = os.path.normpath(os.path.abspath(base))
    full = os.path.normpath(os.path.join(root, *parts))
    if full != root and not full.startswith(root + os.sep):
        raise ValueError("path escapes its directory")
    return Path(full)


def allowed_roots(root: Path) -> list[str]:
    """Directories an API-supplied path may live under.

    The workspace root, the configured output and configs directories, the
    config source cache, the user's home directory, plus any extra roots
    listed in ``SKILL_SEEKERS_ALLOWED_ROOTS`` (``os.pathsep``-separated).
    """
    cache = os.environ.get("SKILL_SEEKERS_CACHE_DIR") or str(Path.home() / ".skill-seekers" / "cache")
    bases = [
        str(root),
        str(workspace_dir(root, "output")),
        str(workspace_dir(root, "configs")),
        os.path.expanduser(cache),
        str(Path.home()),
    ]
    bases += [p for p in os.environ.get("SKILL_SEEKERS_ALLOWED_ROOTS", "").split(os.pathsep) if p]
    return [os.path.normcase(os.path.normpath(os.path.abspath(b))) for b in bases]


def _is_within(folded: str, base: str) -> bool:
    """True when ``folded`` is ``base`` or below it (``base`` may be a drive root)."""
    prefix = base if base.endswith(os.sep) else base + os.sep
    return folded == base or folded.startswith(prefix)


def user_path(root: Path, value: str) -> Path:
    """Resolve a path chosen through the API and keep it inside the allowed roots.

    Relative values resolve against ``root``; ``~`` is expanded. Anything that
    normalises to a location outside the allowed roots is refused, so a request
    cannot point the server at system files. The check is lexical: callers
    still resolve links afterwards, and a link inside an allowed root may point
    elsewhere.
    """
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise ValueError("expected a filesystem path")
    full = os.path.normpath(os.path.join(os.path.abspath(root), os.path.expanduser(value)))
    folded = os.path.normcase(full)
    for base in allowed_roots(root):
        if _is_within(folded, base):
            return Path(full)
    raise ValueError(
        "path is outside the workspace and the home directory; "
        "add its folder to SKILL_SEEKERS_ALLOWED_ROOTS to allow it"
    )


def safe_name(value: str) -> str:
    """Validate a single filesystem component supplied through the API."""
    if not value or value in (".", "..") or any(c in value for c in "/\\\x00:"):
        raise ValueError("expected a name, not a filesystem path")
    return value


def atomic_write(path: Path, data: bytes) -> None:
    """Replace a file atomically using a private, unique temporary file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, filename = tempfile.mkstemp(prefix=f".{path.name}-", dir=path.parent)
    tmp = Path(filename)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)


def ensure_dirs() -> None:
    """Create the UI state directory tree if missing."""
    UI_STATE_DIR.mkdir(parents=True, exist_ok=True)
    TRASH_DIR.mkdir(parents=True, exist_ok=True)
    MARKET_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default: Any) -> Any:
    """Read a JSON file, returning ``default`` when missing or corrupt."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return default


def write_json(path: Path, data: Any) -> None:
    """Atomically write JSON to ``path``."""
    with state_transaction():
        atomic_write(path, json.dumps(data, indent=2, default=str).encode("utf-8"))


def update_json(path: Path, update: Callable[[Any], Any], default: Any) -> Any:
    """Apply a read-modify-write operation as one transaction."""
    with state_transaction():
        data = update(read_json(path, default))
        write_json(path, data)
        return data


def load_settings() -> dict[str, Any]:
    """Load UI settings merged over defaults."""
    stored = read_json(SETTINGS_FILE, {})
    merged = dict(DEFAULT_SETTINGS)
    if isinstance(stored, dict):
        merged.update(stored)
    return merged


def save_settings(settings: dict[str, Any]) -> None:
    """Persist UI settings."""
    write_json(SETTINGS_FILE, settings)
