"""Fork regression tests: web scraper output paths must stay inside references/ on Windows.

Each test names the hostile input it blocks (F1 URL-derived categories, F2 llms_txt_url
filenames, F5 drive-root output). They use ntpath so the Windows separator rules apply
on every host, and they assert on files that actually land on disk.
"""

from __future__ import annotations

import ntpath
import os
from pathlib import Path

import pytest

from skill_seekers.cli.doc_scraper import DocToSkillConverter

BACKSLASH = chr(92)
HOSTILE_SEGMENT = BACKSLASH.join(["..", "..", "..", "escaped_category"])


def _converter(output_dir: Path, name: str = "winpaths") -> DocToSkillConverter:
    config = {
        "name": name,
        "base_url": "https://docs.invalid/",
        "output_dir": str(output_dir),
        "selectors": {"main_content": "article", "title": "h1", "code_blocks": "pre code"},
        "rate_limit": 0.0,
        "max_pages": 10,
    }
    return DocToSkillConverter(config, dry_run=True)


def _page(url: str, title: str) -> dict:
    return {
        "url": url,
        "title": title,
        "content": "plain body text",
        "headings": [],
        "code_samples": [],
        "patterns": [],
    }


def test_three_hostile_url_segments_cannot_write_outside_references(tmp_path):
    """F1: a backslash-bearing URL segment that auto-categorizes must not escape references/.

    The escape assertions are substantive only on a Windows host, where the write actually
    leaves the directory. On other hosts the name assertion still runs: ntpath.basename rejects
    any backslash in a file name on every platform, so the sanitizer is checked everywhere.
    """
    skill_dir = tmp_path / "skill"
    (skill_dir / "references").mkdir(parents=True)
    converter = _converter(skill_dir)
    pages = [_page(f"https://docs.invalid/{HOSTILE_SEGMENT}/{i}", f"Page {i}") for i in range(3)]

    categories = converter.smart_categorize(pages)
    assert HOSTILE_SEGMENT in categories, "precondition: the hostile segment becomes a category"
    for category, cat_pages in categories.items():
        converter.create_reference_file(category, cat_pages)

    # The escape check runs first: on Windows the unfixed code writes outside skill_dir,
    # which is exactly what must not happen.
    # Three ".." from references/ lands in tmp_path.parent on Windows.
    assert not (tmp_path.parent / "escaped_category.md").exists()
    assert not (tmp_path / "escaped_category.md").exists()
    assert not (skill_dir / "escaped_category.md").exists()
    refs = (skill_dir / "references").resolve()
    written = sorted(p for p in tmp_path.rglob("*.md"))
    assert written, "precondition: reference files were written"
    for path in written:
        assert path.resolve().parent == refs, f"{path} escaped references/"
        assert ntpath.basename(path.name) == path.name, f"separator in file name: {path.name}"


def test_reference_file_stem_keeps_ordinary_names_and_drops_separators():
    """Regression guard for the F1 fix: normal slugs and spaces keep their file names."""
    from skill_seekers.cli.doc_scraper import reference_file_stem

    assert reference_file_stem("getting-started") == "getting-started"
    assert reference_file_stem("api_reference") == "api_reference"
    assert reference_file_stem("Getting Started") == "Getting Started"
    assert reference_file_stem("CON") == "_CON"
    assert reference_file_stem("..") == "category"
    for hostile in (HOSTILE_SEGMENT, "a/b", "C:evil", "x" + chr(0) + "y"):
        stem = reference_file_stem(hostile)
        assert BACKSLASH not in stem and "/" not in stem and ":" not in stem
        assert ntpath.basename(stem) == stem


def test_llms_txt_url_filename_cannot_carry_windows_traversal():
    """F2: a configured llms_txt_url whose last segment uses backslashes or drive prefixes
    must still produce one file name that the references/ join cannot climb out of."""
    from skill_seekers.cli.llms_txt_downloader import LlmsTxtDownloader

    hostile = "https://docs.invalid/" + BACKSLASH.join(["..", "..", "..", "escaped_llms.txt"])
    name = LlmsTxtDownloader(hostile).get_proper_filename()
    assert name == "escaped_llms.md"

    for url, expected in (
        ("https://docs.invalid/C:evil.txt", "C_evil.md"),
        ("https://docs.invalid/x" + BACKSLASH + "y.txt", "y.md"),
        ("https://docs.invalid/", "llms.md"),
        ("https://docs.invalid/..", "llms.md"),
    ):
        name = LlmsTxtDownloader(url).get_proper_filename()
        assert name == expected, url
        assert BACKSLASH not in name and ":" not in name and "/" not in name
        assert ntpath.basename(name) == name


def test_llms_txt_downloader_filename_for_existing_urls_is_unchanged():
    """Regression guard for the F2 fix: ordinary llms file names keep their current mapping."""
    from skill_seekers.cli.llms_txt_downloader import LlmsTxtDownloader

    assert LlmsTxtDownloader("https://hono.dev/llms-full.txt").get_proper_filename() == (
        "llms-full.md"
    )
    assert LlmsTxtDownloader("https://hono.dev/llms.txt").get_proper_filename() == "llms.md"


def test_drive_root_output_keeps_its_root_anchor():
    """F5: --output C:\ must stay C:\. Stripping it to "C:" made it drive-relative, so
    os.path.join("C:", "SKILL.md") named a file in whatever directory C: last used."""
    from skill_seekers.cli.skill_converter import SkillConverter

    resolve = SkillConverter.resolve_skill_dir
    assert resolve({"output_dir": "C:" + BACKSLASH}, "n") == "C:" + BACKSLASH
    assert resolve({"output_dir": "C:/"}, "n") == "C:/"
    assert resolve({"output_dir": "C:" + BACKSLASH + "out" + BACKSLASH}, "n") == "C:" + (
        BACKSLASH + "out"
    )
    assert resolve({"output_dir": "C:/out/"}, "n") == "C:/out"
    assert ntpath.isabs(ntpath.join(resolve({"output_dir": "C:" + BACKSLASH}, "n"), "SKILL.md"))
    assert ntpath.join(resolve({"output_dir": "C:" + BACKSLASH}, "n"), "SKILL.md") == (
        "C:" + BACKSLASH + "SKILL.md"
    )


def test_llms_write_refuses_a_name_that_leaves_references(tmp_path, monkeypatch):
    """F2 containment: even if a downloader hands back a traversal name, the explicit llms write
    must refuse it instead of writing outside references/ (the sanitizer is not the only guard)."""
    from skill_seekers.cli import doc_scraper

    class _FakeDownloader:
        def __init__(self, url, *a, **k):
            self.url = url

        def download(self):
            return "# llms content\n"

        def get_proper_filename(self):
            return HOSTILE_SEGMENT.replace("escaped_category", "escaped_llms") + ".md"

    monkeypatch.setattr(doc_scraper, "LlmsTxtDownloader", _FakeDownloader)
    skill_dir = tmp_path / "skill"
    config = {
        "name": "winpaths",
        "base_url": "https://docs.invalid/",
        "output_dir": str(skill_dir),
        "llms_txt_url": "https://docs.invalid/llms.txt",
        "selectors": {"main_content": "article", "title": "h1", "code_blocks": "pre code"},
        "rate_limit": 0.0,
        "max_pages": 10,
    }
    converter = DocToSkillConverter(config, dry_run=True)
    (skill_dir / "references").mkdir(parents=True)
    with pytest.raises(ValueError, match="resolves outside references|Unsafe reference"):
        converter._try_llms_txt()
    assert not (tmp_path.parent / "escaped_llms.md").exists()
    assert not (tmp_path / "escaped_llms.md").exists()
    assert not (skill_dir / "escaped_llms.md").exists()
    assert list((skill_dir / "references").iterdir()) == []


@pytest.mark.parametrize(
    "name",
    [
        "CON",
        "con.md",
        "PRN.txt",
        "aux",
        "NUL.md",
        "COM1.md",
        "lpt9",
        "COM¹.md",
        "LPT³",
        "COM².txt",
        "a‮b.md",
        "x⁦y.md",
    ],
)
def test_resolve_reference_path_refuses_reserved_and_bidi_names(tmp_path, name):
    """Hardening (review): Windows device names, with any case, extension or superscript digit,
    and bidi override characters must never become a reference file name."""
    from skill_seekers.cli.doc_scraper import resolve_reference_path

    with pytest.raises(ValueError):
        resolve_reference_path(str(tmp_path), name)


def test_resolve_reference_path_keeps_ordinary_names(tmp_path):
    """Regression guard: names that only look like device names still resolve inside the root."""
    from skill_seekers.cli.doc_scraper import resolve_reference_path

    for name in ("CONSOLE.md", "com10.md", "api-reference.md"):
        resolved = resolve_reference_path(str(tmp_path), name)
        assert os.path.dirname(os.path.realpath(resolved)) == os.path.realpath(str(tmp_path))
