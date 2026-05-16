"""Protocol orchestration: `evaluate` and `commit`.

See SPEC §3.1.
"""

from __future__ import annotations

import dataclasses
import datetime as _dt
import json
import os
import pathlib
from collections.abc import Sequence

from machinic_assemblage.assemblage import structure_signature
from machinic_assemblage.capture_detector import evaluate_capture
from machinic_assemblage.ecologies import compute_three_ecologies
from machinic_assemblage.groupe_sujet import detect_subject_group
from machinic_assemblage.transversality import transversality_index
from machinic_assemblage.types import (
    Assemblage,
    DeploymentContext,
    ProtocolReport,
    Utterance,
)


def _now_iso() -> str:
    return _dt.datetime.now(tz=_dt.UTC).isoformat()


def evaluate(
    assemblage: Assemblage,
    context: DeploymentContext,
    history: Sequence[Utterance] = (),
    assemblage_after: Assemblage | None = None,
) -> ProtocolReport:
    """Evaluate the assemblage under the supplied deployment context.

    SPEC §2.5: `context` is mandatory. There is no `mode="research"` switch and there will
    not be one. SPEC §2.6: the report exposes three ecologies as three numbers; aggregation
    is the caller's responsibility.
    """
    if not isinstance(context, DeploymentContext):
        raise TypeError(
            "evaluate(context=...) requires DeploymentContext; "
            "see SPEC §2.5 — there is no research-mode bypass."
        )

    t = transversality_index(assemblage, history)
    eco = compute_three_ecologies(assemblage, context, history)
    is_group, evidence = detect_subject_group(history, assemblage, assemblage_after)
    warnings = evaluate_capture(context, history)
    sig = structure_signature(assemblage)
    return ProtocolReport(
        timestamp_iso=_now_iso(),
        assemblage_signature=sig,
        transversality_index=t,
        three_ecologies=eco,
        is_subject_group=is_group,
        groupe_sujet_evidence=evidence,
        capture_warnings=warnings,
        context=context,
    )


def _to_jsonable(obj: object) -> object:
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: _to_jsonable(getattr(obj, f.name)) for f in dataclasses.fields(obj)}
    if isinstance(obj, (frozenset, set)):
        return [_to_jsonable(x) for x in sorted(obj, key=repr)]
    if isinstance(obj, tuple):
        return [_to_jsonable(x) for x in obj]
    if isinstance(obj, list):
        return [_to_jsonable(x) for x in obj]
    if isinstance(obj, dict):
        return {str(k): _to_jsonable(v) for k, v in obj.items()}
    if hasattr(obj, "value") and obj.__class__.__name__ in {"Side", "Vector"}:
        return obj.value
    return obj


def commit(report: ProtocolReport, path: str | os.PathLike[str]) -> None:
    """Append a `ProtocolReport` as one JSON line to `path`.

    Creates the parent directory if needed. Persistence is intentionally simple — operators
    are expected to ship their reports through whatever audit pipeline they actually use.
    """
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(_to_jsonable(report), separators=(",", ":"))
    with p.open("a", encoding="utf-8") as f:
        f.write(line)
        f.write("\n")
