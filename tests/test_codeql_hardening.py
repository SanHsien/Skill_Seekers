"""Regression tests for the CodeQL hardening of the web layer and workflow loader."""

from __future__ import annotations

import pytest

from skill_seekers.cli.enhancement_workflow import _log_safe
from skill_seekers.web.paths import contained
from skill_seekers.web.routes.analyze import REPO_RE
from skill_seekers.web.routes.workflows import _validate_yaml


def test_contained_joins_inside_base(tmp_path):
    assert contained(tmp_path, "a", "b.json") == tmp_path / "a" / "b.json"


@pytest.mark.parametrize("part", ["..", "../x", "a/../../x"])
def test_contained_rejects_escape(tmp_path, part):
    with pytest.raises(ValueError):
        contained(tmp_path, part)


def test_log_safe_strips_line_breaks():
    assert _log_safe("a\r\nb\nc") == "abc"


def test_repo_regex_is_bounded_and_ascii():
    assert REPO_RE.fullmatch("owner/repo.name-1")
    assert not REPO_RE.fullmatch("o" * 101 + "/repo")
    assert not REPO_RE.fullmatch("owner/réPo")


def test_invalid_yaml_reports_line_without_parser_text():
    result = _validate_yaml("name: [unclosed\nstages: x")
    assert result["valid"] is False
    assert result["error"].startswith("YAML syntax error")
    assert "expected" not in result["error"]


def test_user_path_accepts_workspace_and_home(tmp_path, monkeypatch):
    from pathlib import Path

    from skill_seekers.web.paths import user_path

    monkeypatch.setattr(Path, "home", classmethod(lambda _cls: tmp_path / "home"))
    assert user_path(tmp_path, "sub/dir") == tmp_path / "sub" / "dir"
    assert user_path(tmp_path, str(tmp_path / "home" / "proj")) == tmp_path / "home" / "proj"


@pytest.mark.parametrize("value", ["../../outside", "", "a\x00b"])
def test_user_path_rejects_outside_and_garbage(tmp_path, monkeypatch, value):
    from pathlib import Path

    from skill_seekers.web.paths import user_path

    monkeypatch.setattr(Path, "home", classmethod(lambda _cls: tmp_path / "home"))
    with pytest.raises(ValueError):
        user_path(tmp_path / "ws", value)


def test_user_path_allows_extra_roots_from_environment(tmp_path, monkeypatch):
    from pathlib import Path

    from skill_seekers.web.paths import user_path

    extra = tmp_path / "extra"
    monkeypatch.setattr(Path, "home", classmethod(lambda _cls: tmp_path / "home"))
    monkeypatch.setenv("SKILL_SEEKERS_ALLOWED_ROOTS", str(extra))
    assert user_path(tmp_path / "ws", str(extra / "x")) == extra / "x"


def test_create_flags_reject_workflow_paths():
    from skill_seekers.web.runner import _create_flag_argv

    assert _create_flag_argv({"workflows": ["security-focus"]})[-2:] == [
        "--enhance-workflow",
        "security-focus",
    ]
    with pytest.raises(ValueError):
        _create_flag_argv({"workflows": ["../../etc/passwd"]})
