"""Tests for skill_seekers.cors_config.resolve_cors_config."""

import pytest

from skill_seekers.cors_config import resolve_cors_config


@pytest.mark.parametrize(
    "raw, origins, credentials",
    [
        # Empty -> no cross-origin access at all (secure default, not a wildcard).
        ("", [], False),
        ("   ", [], False),
        (",,", [], False),
        # Explicit wildcard -> public, credentials disabled (browsers reject the combo).
        ("*", ["*"], False),
        (" * ", ["*"], False),
        # A wildcard mixed into a list must still collapse to public, no credentials.
        ("*,https://a.com", ["*"], False),
        ("https://a.com, *", ["*"], False),
        # Explicit origins -> credentials enabled.
        ("https://a.com", ["https://a.com"], True),
        ("https://a.com,https://b.com", ["https://a.com", "https://b.com"], True),
        # Whitespace and empty segments are trimmed/dropped.
        ("https://a.com, https://b.com", ["https://a.com", "https://b.com"], True),
        ("https://a.com,,https://b.com", ["https://a.com", "https://b.com"], True),
    ],
)
def test_resolve_cors_config_explicit(raw, origins, credentials):
    assert resolve_cors_config(raw) == (origins, credentials)


def test_resolve_cors_config_env_default_is_not_a_wildcard(monkeypatch):
    """Unset CORS_ORIGINS must not let arbitrary web pages call the server."""
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    assert resolve_cors_config() == ([], False)


def test_resolve_cors_config_env_wildcard_is_explicit_opt_in(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "*")
    assert resolve_cors_config() == (["*"], False)


def test_resolve_cors_config_env_explicit(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "https://x.com,https://y.com")
    assert resolve_cors_config() == (["https://x.com", "https://y.com"], True)
