from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "fork-product-tests.yml"
TEST_LIST = ROOT / "tools" / "fork_product_tests.txt"

# Tests added by fork commits that port upstream fixes; losing any of them from the
# list means those fixes are verified nowhere in CI again.
REQUIRED_PORTED_TESTS = (
    "tests/test_vtt_numeric_cue.py",
    "tests/test_workflow_preview_substitution.py",
    "tests/test_heading_headerlinks.py",
    "tests/test_adaptors/test_enhance_via_agent_client.py",
    "tests/test_codeql_hardening.py",
    "tests/test_embedding_server.py",
    "tests/test_source_detector.py",
    "tests/test_windows_output_paths.py",
    "tests/test_source_text_embedding.py",
    "tests/test_notion_rate_limit.py",
    "tests/test_unc_output_root.py",
)


def _listed_tests() -> list[str]:
    lines = TEST_LIST.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


def test_every_listed_product_test_file_exists() -> None:
    listed = _listed_tests()
    assert listed
    missing = [path for path in listed if not (ROOT / path).is_file()]
    assert missing == []


def test_list_keeps_fork_ported_tests() -> None:
    listed = set(_listed_tests())
    assert set(REQUIRED_PORTED_TESTS) <= listed


def test_list_has_no_duplicates() -> None:
    listed = _listed_tests()
    assert len(listed) == len(set(listed))


def test_workflow_runs_only_on_the_fork_and_on_windows() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "if: github.repository == 'SanHsien/Skill_Seekers'" in text
    assert "runs-on: windows-latest" in text
    assert "ubuntu" not in text


def test_workflow_reads_the_list_and_selects_offline_tests() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "tools/fork_product_tests.txt" in text
    assert "not network" in text
    assert "--locked" in text


def test_workflow_is_least_privilege_and_bounded() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert re.search(r"^permissions:\n  contents: read$", text, re.MULTILINE)
    assert "timeout-minutes:" in text
    assert "concurrency:" in text
    assert "persist-credentials: false" in text


def test_workflow_actions_are_pinned_to_commit_sha() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    uses = re.findall(r"^\s*uses:\s*(\S+)", text, re.MULTILINE)
    assert uses
    for ref in uses:
        assert re.fullmatch(r"[\w./-]+@[0-9a-f]{40}", ref), ref


def test_upstream_tests_workflow_is_left_to_upstream() -> None:
    text = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
    assert "yusufkaraaslan/Skill_Seekers" in text
    assert "SanHsien" not in text


def test_workflow_list_reader_trims_and_skips_comments_like_the_python_reader() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    reader = next(line for line in text.splitlines() if "Get-Content tools/fork_product_tests.txt" in line)
    assert "$_.Trim()" in reader
    assert 'StartsWith("#")' in reader
    assert "$_ -and" in reader


def test_workflow_isolates_home_and_pins_python() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "HOME: ${{ runner.temp }}" in text
    assert "USERPROFILE: ${{ runner.temp }}" in text
    assert "New-Item -ItemType Directory" in text
    pytest_line = next(line for line in text.splitlines() if "-m pytest" in line)
    assert "--python 3.12" in pytest_line


def test_runner_context_is_not_used_in_job_level_env() -> None:
    """GitHub rejects the whole workflow when job-level env reads `runner.*`."""
    lines = WORKFLOW.read_text(encoding="utf-8").splitlines()
    job_env = False
    for line in lines:
        if line == "    env:":
            job_env = True
            continue
        if job_env and not line.startswith("      "):
            job_env = False
        if job_env:
            assert "runner." not in line, line
