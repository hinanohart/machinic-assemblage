"""Protocol evaluate/commit tests."""

from __future__ import annotations

import json

import pytest

from machinic_assemblage import (
    HeterogeneousEdge,
    Node,
    NodeId,
    ProtocolReport,
    Side,
    Vector,
    build_assemblage,
    commit,
    evaluate,
    record_utterance,
)


def test_evaluate_rejects_non_context(simple_assemblage):
    with pytest.raises(TypeError, match="DeploymentContext"):
        evaluate(simple_assemblage, context="not-a-context", history=())  # type: ignore[arg-type]


def test_evaluate_runs_with_minimal_context(simple_assemblage, minimal_context):
    r = evaluate(simple_assemblage, minimal_context)
    assert isinstance(r, ProtocolReport)
    assert r.assemblage_signature
    assert 0.0 <= r.transversality_index <= 1.0
    assert r.context is minimal_context


def test_no_composite_score_on_report(simple_assemblage, minimal_context):
    r = evaluate(simple_assemblage, minimal_context)
    assert not hasattr(r, "composite_score")
    assert not hasattr(r, "alignment_score")
    assert not hasattr(r.three_ecologies, "composite")


def test_evaluate_with_history_detects_subject_group(minimal_context):
    a = build_assemblage(
        [Node(id=NodeId("alice"), kind="h"), Node(id=NodeId("bob"), kind="h")],
        [
            HeterogeneousEdge(
                members=frozenset({NodeId("alice"), NodeId("bob")}),
                semantic="x",
                side=Side.CONTENT,
                vector=Vector.TERRITORIAL,
            )
        ],
    )
    b = build_assemblage(
        [
            Node(id=NodeId("alice"), kind="h"),
            Node(id=NodeId("bob"), kind="h"),
            Node(id=NodeId("carol"), kind="h"),
        ],
        [
            HeterogeneousEdge(
                members=frozenset({NodeId("alice"), NodeId("bob"), NodeId("carol")}),
                semantic="x",
                side=Side.CONTENT,
                vector=Vector.TERRITORIAL,
            )
        ],
    )
    history = (record_utterance(NodeId("alice"), "bring carol", "rule_change", "2026-01-01"),)
    r = evaluate(a, minimal_context, history=history, assemblage_after=b)
    assert r.is_subject_group is True


def test_commit_appends_jsonl(tmp_path, simple_assemblage, minimal_context):
    r = evaluate(simple_assemblage, minimal_context)
    path = tmp_path / "out" / "reports.jsonl"
    commit(r, path)
    commit(r, path)
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    parsed = json.loads(lines[0])
    assert "assemblage_signature" in parsed
    assert "three_ecologies" in parsed
    assert "composite" not in parsed
    assert "alignment_score" not in parsed


def _concurrent_writer_target(args: tuple[str, int, int]) -> int:
    """Module-level worker for multiprocessing — repeatedly commit() to the same JSONL path.

    Imported fresh in each child process so the fcntl.flock guard is exercised across
    real OS processes, not just threads. Returns the number of writes performed.
    """
    import json as _json
    import pathlib as _pl

    from machinic_assemblage import (
        DeploymentContext,
        HeterogeneousEdge,
        Node,
        NodeId,
        ProtocolReport,
        Side,
        ThreeEcologiesKPI,
        Vector,
        build_assemblage,
        structure_signature,
    )
    from machinic_assemblage import (
        commit as _commit,
    )

    path_str, writer_id, n = args
    p = _pl.Path(path_str)
    asm = build_assemblage(
        [
            Node(id=NodeId(f"w{writer_id}-a"), kind="h"),
            Node(id=NodeId(f"w{writer_id}-b"), kind="h"),
        ],
        [
            HeterogeneousEdge(
                members=frozenset({NodeId(f"w{writer_id}-a"), NodeId(f"w{writer_id}-b")}),
                semantic="x",
                side=Side.CONTENT,
                vector=Vector.TERRITORIAL,
            )
        ],
    )
    ctx = DeploymentContext(
        operator_org=f"writer-{writer_id}",
        revenue_model="none",
        end_users_consent_uri="https://example.org/c",
        used_in_optimization_for=frozenset(),
        declared_at_iso="2026-05-17T00:00:00+00:00",
    )
    # Build a long-ish line to increase the chance of buffer-boundary interleave under stress.
    long_text = "x" * 4096
    for i in range(n):
        report = ProtocolReport(
            timestamp_iso=f"2026-05-17T00:00:{i:02d}+00:00",
            assemblage_signature=structure_signature(asm),
            transversality_index=0.0,
            three_ecologies=ThreeEcologiesKPI(mental=0.5, social=0.5, environmental=0.5),
            is_subject_group=False,
            groupe_sujet_evidence=(f"w{writer_id}-iter-{i}", long_text),
            capture_warnings=(),
            context=ctx,
        )
        _commit(report, p)
    # Sanity: make sure our own writes are well-formed JSON when read back.
    text = p.read_text(encoding="utf-8")
    for line in text.strip().splitlines():
        _json.loads(line)
    return n


@pytest.mark.skipif(
    not hasattr(__import__("os"), "fork"),
    reason="fcntl.flock atomicity test requires POSIX fork()",
)
def test_commit_atomic_under_concurrent_writers(tmp_path):
    """v0.1.3 F6: two processes × 25 writes must produce 50 well-formed JSONL lines.

    Pins the fcntl.flock(LOCK_EX) guarantee added in v0.1.1. Each line carries a 4KB payload
    so the file write spans more than one buffer page; without flock, concurrent appenders
    could interleave bytes from each line.
    """
    import multiprocessing as mp

    path = tmp_path / "concurrent.jsonl"
    n_per_writer = 25
    n_writers = 2
    with mp.get_context("fork").Pool(processes=n_writers) as pool:
        results = pool.map(
            _concurrent_writer_target,
            [(str(path), i, n_per_writer) for i in range(n_writers)],
        )
    assert results == [n_per_writer] * n_writers

    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == n_per_writer * n_writers, (
        f"expected {n_per_writer * n_writers} lines, got {len(lines)}"
    )
    for ln in lines:
        parsed = json.loads(ln)
        assert "assemblage_signature" in parsed
        assert "three_ecologies" in parsed
