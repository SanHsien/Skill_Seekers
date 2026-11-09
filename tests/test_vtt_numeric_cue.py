"""WebVTT: a cue whose spoken text is only digits must survive (upstream issue #481)."""

from skill_seekers.cli.video_transcript import parse_vtt


def test_numeric_only_cue_text_is_kept(tmp_path):
    f = tmp_path / "numeric.vtt"
    f.write_text(
        "WEBVTT\n\n1\n00:00:00.000 --> 00:00:01.000\n2026\n\n"
        "2\n00:00:01.000 --> 00:00:02.000\nNext\n",
        encoding="utf-8",
    )
    assert [s.text for s in parse_vtt(str(f))] == ["2026", "Next"]


def test_cue_identifier_without_blank_separator_is_not_text(tmp_path):
    f = tmp_path / "noblank.vtt"
    f.write_text(
        "WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nHello\n2\n00:00:01.000 --> 00:00:02.000\nWorld\n",
        encoding="utf-8",
    )
    assert [s.text for s in parse_vtt(str(f))] == ["Hello", "World"]
