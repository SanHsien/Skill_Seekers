"""Unit tests for fixes and hardening in SanHsien fork."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from skill_seekers.cli.arguments.enhance import ENHANCE_ARGUMENTS, add_enhance_arguments
from skill_seekers.cli.doctor import main as doctor_main
from skill_seekers.services.git_repo import validate_path_segment


class TestPathSegmentValidation:
    @pytest.mark.parametrize(
        "unsafe_name",
        [
            "",
            ".",
            "..",
            "../outside",
            "..\\outside",
            "nested/source",
            r"nested\source",
            "/absolute",
            r"C:\cache",
            r"D:\something",
        ],
    )
    def test_rejects_unsafe_segments(self, unsafe_name: str) -> None:
        with pytest.raises(ValueError, match="single path segment"):
            validate_path_segment(unsafe_name, label="test")

    @pytest.mark.parametrize(
        "safe_name",
        [
            "react",
            "my-config",
            "skill_v2",
            "config.json",
        ],
    )
    def test_accepts_safe_segments(self, safe_name: str) -> None:
        assert validate_path_segment(safe_name, label="test") == safe_name


class TestDoctorStandaloneEntryPoint:
    def test_doctor_main_callable(self) -> None:
        assert callable(doctor_main)

    def test_doctor_help(self) -> None:
        with pytest.raises(SystemExit) as exc:
            doctor_main(["--help"])
        assert exc.value.code == 0


class TestEnhanceLevelArgument:
    def test_enhance_level_in_arguments_dict(self) -> None:
        assert "enhance_level" in ENHANCE_ARGUMENTS
        assert "--enhance-level" in ENHANCE_ARGUMENTS["enhance_level"]["flags"]

    def test_enhance_level_argparse_parsing(self) -> None:
        parser = argparse.ArgumentParser()
        add_enhance_arguments(parser)
        args = parser.parse_args(["output/test", "--enhance-level", "2"])
        assert args.enhance_level == 2

    @pytest.mark.parametrize("level", [0, 1, 2, 3])
    def test_enhance_level_choices(self, level: int) -> None:
        parser = argparse.ArgumentParser()
        add_enhance_arguments(parser)
        args = parser.parse_args(["output/test", "--enhance-level", str(level)])
        assert args.enhance_level == level

    def test_enhance_level_zero_skips(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        from skill_seekers.cli.enhance_command import main as enhance_main

        skill_dir = tmp_path / "test_skill"
        skill_dir.mkdir()
        code = enhance_main([str(skill_dir), "--enhance-level", "0"])
        assert code == 0
        captured = capsys.readouterr()
        assert "Enhancement skipped (--enhance-level 0)" in captured.out


class TestCliResilientImports:
    def test_cli_import_without_heavy_dependencies(self) -> None:
        import skill_seekers.cli as cli

        assert hasattr(cli, "__version__")

