"""契約測試：依賴新鮮度檢查的地板精度與兩條紅燈出口。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_dependency_freshness as checker


def test_comparison_uses_the_precision_the_declaration_states() -> None:
    assert not checker.is_newer_version("7.4.0", "7")
    assert checker.is_newer_version("8.0.0", "7")
    assert checker.is_newer_version("7.4.0", "7.3")
    assert not checker.is_newer_version("7.3.2", "7.3")


def test_prerelease_suffix_does_not_count_as_newer() -> None:
    assert not checker.is_newer_version("7.0.0rc1", "7.0.0")


def test_hold_marker_is_read_off_the_declaring_line() -> None:
    packages = checker.parse_requirements(
        "pytest>=8.3  # freshness-hold: pytest 9 requires Python 3.10, CI still tests 3.9\n"
        "ruff>=0.16\n",
        "requirements-dev.txt",
    )
    holds = {package["name"]: package["hold"] for package in packages}
    assert holds["ruff"] == ""
    assert holds["pytest"].startswith("pytest 9 requires Python 3.10")


def test_a_held_floor_is_reported_but_does_not_ask_for_work(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(checker, "fetch_pypi_version", lambda name: "9.1.0")
    packages = checker.parse_requirements(
        "pytest>=8.3  # freshness-hold: CI still tests 3.9\n", "requirements-dev.txt"
    )
    rows = checker.collect_status(packages, deferrals={})
    assert rows[0]["outdated"] is True
    assert checker.needs_review(rows[0]) is False
    assert "HELD: CI still tests 3.9" in checker.render_markdown(rows)


def test_a_live_deferral_covers_the_row_and_says_what_it_was_reviewed_against(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(checker, "fetch_pypi_version", lambda name: "9.1.0")
    packages = checker.parse_requirements("pytest>=8.3\n", "requirements-dev.txt")
    rows = checker.collect_status(
        packages,
        deferrals={"pytest": ("9.1", "reviewed 2026-09; wait for the 9.x line to settle")},
    )
    assert checker.needs_review(rows[0]) is False
    assert "DEFERRED at 9.1.0" in checker.render_markdown(rows)


def test_a_deferral_expires_once_pypi_moves_past_the_reviewed_release(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(checker, "fetch_pypi_version", lambda name: "10.0.0")
    packages = checker.parse_requirements("pytest>=8.3\n", "requirements-dev.txt")
    rows = checker.collect_status(packages, deferrals={"pytest": ("9.1", "not this month")})
    assert checker.needs_review(rows[0]) is True
    assert "REVIEW UPDATE" in checker.render_markdown(rows)


def test_deferral_without_a_reviewed_release_is_ignored(tmp_path: Path) -> None:
    path = tmp_path / "dependency-deferrals.json"
    path.write_text(
        json.dumps(
            {
                "deferrals": {
                    "kept": {"deferredLatest": "9.1", "reason": "reviewed, not now"},
                    "no-release": {"reason": "reviewed, not now"},
                    "no-reason": {"deferredLatest": "9.1"},
                }
            }
        ),
        encoding="utf-8",
    )
    assert checker.load_deferrals(path) == {"kept": ("9.1", "reviewed, not now")}


def test_missing_deferrals_file_is_not_an_error(tmp_path: Path) -> None:
    assert checker.load_deferrals(tmp_path / "nope.json") == {}


def test_report_names_both_exits_so_the_next_person_does_not_invent_a_third() -> None:
    report = checker.render_markdown([])
    assert "freshness-hold:" in report
    assert "dependency-deferrals.json" in report
    assert "mute button" in report


@pytest.mark.parametrize("deferred_name", ["demo-package", "Demo_Package", "demo.package", "DEMO..._-PACKAGE"])
@pytest.mark.parametrize("requirement_name", ["demo-package", "Demo_Package", "demo.package", "DEMO..._-PACKAGE"])
@pytest.mark.parametrize("latest, expected_review", [("2.0.0", False), ("3.0.0", True)])
def test_equivalent_package_names_share_a_deferral_and_its_expiry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    deferred_name: str,
    requirement_name: str,
    latest: str,
    expected_review: bool,
) -> None:
    path = tmp_path / "dependency-deferrals.json"
    reason = "已審查，暫緩升級"
    path.write_text(
        json.dumps({"deferrals": {deferred_name: {"deferredLatest": "2.0.0", "reason": reason}}}),
        encoding="utf-8",
    )
    deferrals = checker.load_deferrals(path)
    assert deferrals == {"demo-package": ("2.0.0", reason)}
    monkeypatch.setattr(checker, "fetch_pypi_version", lambda name: latest)
    packages = checker.parse_requirements(f"{requirement_name}>=1.0.0\n", "requirements.txt")
    rows = checker.collect_status(packages, deferrals=deferrals)
    assert checker.needs_review(rows[0]) is expected_review
    assert rows[0]["deferred_reason"] == ("" if expected_review else reason)
    report = checker.render_markdown(rows)
    assert ("REVIEW UPDATE" if expected_review else "DEFERRED at 2.0.0") in report
    assert rows[0]["name"] == requirement_name


def test_equivalent_package_names_are_loaded_only_once(tmp_path: Path) -> None:
    (tmp_path / "requirements-dev.txt").write_text("Demo_Package>=1.0\n", encoding="utf-8")
    (tmp_path / "requirements.txt").write_text(
        "demo.package>=1.0\nDEMO..._-PACKAGE>=1.0\ndemo-package>=1.0\nother-package>=1.0\n",
        encoding="utf-8",
    )
    packages = checker.load_direct_dependencies(tmp_path)
    assert [package["name"] for package in packages] == ["Demo_Package", "other-package"]
