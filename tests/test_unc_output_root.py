"""Fork regression test: a UNC share root keeps its anchor as an output directory (F5)."""

import ntpath

BACKSLASH = chr(92)


def test_unc_share_root_keeps_its_anchor():
    """F5: a UNC share root keeps its trailing separator, like a drive root."""
    from skill_seekers.cli.skill_converter import SkillConverter

    resolve = SkillConverter.resolve_skill_dir
    share_root = BACKSLASH * 2 + "server" + BACKSLASH + "share" + BACKSLASH
    assert resolve({"output_dir": share_root}, "n") == share_root
    assert resolve({"output_dir": share_root[:-1]}, "n") == share_root[:-1]
    assert (
        ntpath.join(resolve({"output_dir": share_root}, "n"), "SKILL.md") == share_root + "SKILL.md"
    )
