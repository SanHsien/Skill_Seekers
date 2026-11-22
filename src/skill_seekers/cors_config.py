"""Shared CORS configuration resolver.

Browsers reject ``Access-Control-Allow-Credentials: true`` combined with a
wildcard ``Access-Control-Allow-Origin: *``. This module resolves a safe
``(allow_origins, allow_credentials)`` pair from the ``CORS_ORIGINS`` env var
so every FastAPI/Starlette server in the project shares one policy.

Fork divergence (docs/DECISIONS.md, 2026-11-22): the default is *no* allowed
origins, not ``*``. These servers are unauthenticated, so a wildcard lets any
web page drive them from the user's browser. Public access is an explicit
``CORS_ORIGINS=*`` opt-in.
"""

from __future__ import annotations

import os

DEFAULT_CORS_ORIGINS = ""


def resolve_cors_config(raw: str | None = None) -> tuple[list[str], bool]:
    """Resolve ``(allow_origins, allow_credentials)`` from a CORS_ORIGINS value.

    - unset / empty -> ``([], False)``
      No cross-origin access (same-origin and non-browser clients still work).
    - ``"*"`` (or any list containing ``"*"``) -> ``(["*"], False)``
      Explicit public opt-in; credentials are disabled because browsers reject
      the wildcard-plus-credentials combination.
    - ``"https://a.com, https://b.com"`` -> ``(["https://a.com", "https://b.com"], True)``
      Explicit origins; credentials enabled.

    ``raw`` defaults to the ``CORS_ORIGINS`` environment variable.
    """
    if raw is None:
        raw = os.environ.get("CORS_ORIGINS", DEFAULT_CORS_ORIGINS)
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    if not origins:
        return [], False
    if "*" in origins:
        return ["*"], False
    return origins, True
