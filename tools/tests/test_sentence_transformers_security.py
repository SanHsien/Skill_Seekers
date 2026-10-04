"""Security regression coverage for optional Sentence Transformers support."""

import json
from pathlib import Path

import pytest


def test_rejects_custom_local_module_without_trust(tmp_path: Path) -> None:
    """A model's modules.json cannot import arbitrary local Python by default."""
    sentence_transformers = pytest.importorskip("sentence_transformers")
    marker = tmp_path / "custom-module-executed"
    (tmp_path / "modules.json").write_text(
        json.dumps(
            [
                {
                    "idx": 0,
                    "name": "0_Malicious",
                    "path": "",
                    "type": "malicious.Malicious",
                }
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "malicious.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="trust_remote_code=True"):
        sentence_transformers.SentenceTransformer(str(tmp_path), local_files_only=True)

    assert not marker.exists()
