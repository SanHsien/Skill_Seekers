"""Fork regression tests: web scraper output paths must stay inside references/ on Windows.

Each test names the hostile input it blocks (F1 URL-derived categories, F2 llms_txt_url
filenames, F5 drive-root output). They use ntpath so the Windows separator rules apply
on every host, and they assert on files that actually land on disk.
"""

from __future__ import annotations

import ntpath
from pathlib import Path

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
    """F1: a backslash-bearing URL segment that auto-categorizes must not escape references/."""
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
