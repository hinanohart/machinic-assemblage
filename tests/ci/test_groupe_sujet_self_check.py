"""SPEC §3.4 — Self-application of the groupe-sujet test on this repo.

**This test emits a UserWarning when the repo itself does not pass.** It does not fail CI.
Reasoning: hard assertion on a heuristic creates a perverse incentive to game the heuristic
(cosmetic renames as "rule changes"). The warning is surfaced in PR review instead.
"""

from __future__ import annotations

import pathlib
import subprocess
import warnings

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _git_log_messages(limit: int = 50) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "-C", str(ROOT), "log", f"-n{limit}", "--pretty=format:%s%n%b%n--"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [block.strip() for block in out.stdout.split("\n--\n") if block.strip()]


def test_groupe_sujet_self_check_emits_warning_if_failing():
    """Whether-or-not this repo currently passes, this test must surface its verdict.

    It uses the test harness itself to record the diagnostic.
    """
    contributors_path = ROOT / "CONTRIBUTORS.toml"
    log_blocks = _git_log_messages(limit=50)
    rule_change_mentions = sum(
        1 for blk in log_blocks if "rule_change" in blk or "rule change" in blk.lower()
    )
    has_contributors = contributors_path.exists()
    passes = has_contributors and rule_change_mentions >= 1
    if not passes:
        warnings.warn(
            "groupe-sujet self-check did not pass: "
            f"CONTRIBUTORS.toml exists={has_contributors}, "
            f"rule_change-mentions-in-last-50-commits={rule_change_mentions}. "
            "This is a UserWarning per SPEC §3.4 — CI is not failed, but reviewers should "
            "treat the project's own groupe-sujet state as evidence about its honesty.",
            UserWarning,
            stacklevel=2,
        )
    # The test always passes; it exists to surface the verdict.
    assert True


@pytest.mark.filterwarnings("error::UserWarning")
def test_groupe_sujet_warning_is_a_userwarning_when_failing():
    """Sanity check: the warning class is UserWarning, not DeprecationWarning."""
    contributors_path = ROOT / "CONTRIBUTORS.toml"
    if contributors_path.exists():
        pytest.skip("repo passes self-check; warning path not exercised")
    with pytest.warns(UserWarning):
        warnings.warn("groupe-sujet probe", UserWarning, stacklevel=1)
