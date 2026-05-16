"""G-Q1 — no research-mode bypass switch.

`evaluate(...)` must not accept any `mode=` kwarg that bypasses `DeploymentContext`.
Static signature check.
"""

from __future__ import annotations

import inspect

from machinic_assemblage import evaluate


def test_evaluate_signature_has_no_mode_param():
    sig = inspect.signature(evaluate)
    assert "mode" not in sig.parameters
    assert "research" not in sig.parameters
    assert "bypass" not in sig.parameters


def test_evaluate_signature_requires_context():
    sig = inspect.signature(evaluate)
    assert "context" in sig.parameters
    p = sig.parameters["context"]
    assert p.default is inspect.Parameter.empty, "evaluate(context=...) must be required; SPEC §2.5"
