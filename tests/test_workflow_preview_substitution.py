"""Workflow engine: dry-run preview exists, and custom prompts tolerate literal braces.

Ported from upstream PR #482 (open at head eaeb401): the two defects exist in
this tree; the PR's context pass-through and prompt rewording are not adopted.
"""

import logging
from unittest.mock import MagicMock

from skill_seekers.cli.enhancement_workflow import (
    EnhancementWorkflow,
    WorkflowEngine,
    WorkflowStage,
)


def _engine(stage: WorkflowStage) -> WorkflowEngine:
    engine = WorkflowEngine.__new__(WorkflowEngine)
    engine.workflow = EnhancementWorkflow(name="t", description="d", stages=[stage])
    engine.history = []
    engine.enhancer = None
    engine.agent = None
    return engine


def _custom_stage(prompt: str) -> WorkflowStage:
    return WorkflowStage(name="polish", type="custom", prompt=prompt, target="all")


def test_preview_lists_stages_without_calling_ai(caplog):
    """--workflow-dry-run calls engine.preview(); it must exist and make no AI call."""
    engine = _engine(_custom_stage("Improve {skill_dir}"))
    engine.enhancer = MagicMock()
    with caplog.at_level(logging.INFO):
        engine.preview(context={"skill_dir": "out/x"})
    assert "polish" in caplog.text
    assert "skill_dir='out/x'" in caplog.text
    engine.enhancer.call.assert_not_called()


def test_custom_prompt_keeps_literal_json_braces_and_substitutes_context():
    """A literal JSON example in a prompt must not disable context substitution."""
    engine = _engine(_custom_stage('Dir {skill_dir}. Output {"findings": []} and {unknown}.'))
    engine.enhancer = MagicMock()
    engine.enhancer.call.return_value = "{}"
    engine._run_custom_stage(engine.workflow.stages[0], {"skill_dir": "out/x"})
    sent = engine.enhancer.call.call_args[0][0]
    assert "Dir out/x." in sent
    assert '{"findings": []}' in sent
    assert "{unknown}" in sent


def test_custom_prompt_keeps_str_format_escapes_conversions_and_specs():
    """F7: prompts written for str.format keep {{ }} escapes, !r conversions and :spec formats.

    The tolerant pass that handles literal JSON must not replace an escaped {{skill_dir}}
    with the context value, and must not leave !r or :04d unapplied.
    """
    engine = _engine(_custom_stage("Literal {{skill_dir}}; name={name!r}; n={count:04d}"))
    engine.enhancer = MagicMock()
    engine.enhancer.call.return_value = "{}"
    engine._run_custom_stage(
        engine.workflow.stages[0],
        {"skill_dir": "out/x", "name": "demo", "count": 7},
    )
    sent = engine.enhancer.call.call_args[0][0]
    assert sent == "Literal {skill_dir}; name='demo'; n=0007"
