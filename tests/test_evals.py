"""Offline smoke tests for the evals harness in scripts/ and evals/.

These stub out every provider call: no test spends money or talks to the
network. Live behavior (runner adherence, budgets against real CLIs) is
covered by the scenario workflow documented in evals/README.md.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from judge import assign_labels, grader_rubric, parse_judge_scores
from run_evals import (
    WEIGHTS,
    _condition_prompt,
    _strip_frontmatter,
    completed_keys,
    load_cases,
    main,
    summarize_scores,
    summarize_usage,
    validate_cases,
)
from run_scenario_eval import load_scenario

REPO_ROOT = Path(__file__).parent.parent
CASES = REPO_ROOT / "evals" / "cases.jsonl"
RUBRIC = REPO_ROOT / "evals" / "rubric.md"
SCENARIO = REPO_ROOT / "evals" / "scenarios" / "render-blank-debug-spiral"


def _score_row(case_id: str, trial: int, condition: str, **overrides) -> dict:
    row = {
        "case_id": case_id,
        "trial": trial,
        "condition": condition,
        **{metric: 4 for metric in WEIGHTS},
        "blocker": False,
        "notes": "",
    }
    row.update(overrides)
    return row


def _response_row(case_id: str, trial: int, condition: str) -> dict:
    return {
        "case_id": case_id,
        "trial": trial,
        "condition": condition,
        "runner": "claude",
        "response": "runnable code",
        "usage": {"input_tokens": 10, "output_tokens": 5},
        "cost_usd": 0.01,
        "model": "claude-test-model",
    }


def test_default_cases_validate():
    cases = load_cases(CASES)
    assert len(cases) >= 10
    assert validate_cases(cases) == []


def test_plan_lists_paired_conditions(capsys):
    assert main(["plan", "--trials", "1"]) == 0
    rows = [json.loads(line) for line in capsys.readouterr().out.splitlines() if line.strip()]
    conditions = {row["condition"] for row in rows}
    assert conditions == {"baseline", "candidate"}


def test_score_gate_fails_on_regression_beyond_tolerance():
    baseline = [_score_row("case-a", 1, "baseline", safety=4.0)]
    candidate = [_score_row("case-a", 1, "candidate", safety=3.5)]
    summary = summarize_scores(baseline + candidate)
    gates = summary["release_gate"]
    assert gates["passed"] is False
    assert any("safety" in reason for reason in gates["reasons"])


def test_score_gate_arithmetic():
    baseline = [_score_row("case-a", 1, "baseline")]
    candidate = [_score_row("case-a", 1, "candidate", correctness=5, verification=5)]
    summary = summarize_scores(baseline + candidate)
    assert summary["release_gate"]["passed"] is True


def test_score_gate_fails_on_blocking_finding():
    baseline = [_score_row("case-a", 1, "baseline")]
    candidate = [_score_row("case-a", 1, "candidate", blocker=True)]
    summary = summarize_scores(baseline + candidate)
    gates = summary["release_gate"]
    assert gates["passed"] is False
    assert any("blocking" in reason for reason in gates["reasons"])


def test_measure_reports_usage_and_cost_delta():
    rows = [_response_row("case-a", 1, "baseline"), _response_row("case-a", 1, "candidate")]
    summary = summarize_usage(rows)
    assert summary["delta"]["candidate"]["cost_usd"] == 0.0
    assert summary["delta"]["candidate"]["input_tokens"] == 0.0


def test_condition_prompt_injects_skill_for_candidate(tmp_path):
    skill = tmp_path / "SKILL.md"
    skill.write_text("---\nname: x\n---\nBody text.\n")
    assert _condition_prompt("task", "baseline", None) == "task"
    candidate = _condition_prompt("task", "candidate", skill)
    assert "Body text." in candidate
    assert "task" in candidate


def test_strip_frontmatter_runs_without_closing_block():
    text = "---\nname: x\nbody without closing fence\n"
    assert _strip_frontmatter(text) == text


def test_completed_keys_reads_resumable_rows():
    rows = [_response_row("case-a", 1, "baseline")]
    assert ("case-a", 1, "baseline", "claude") in completed_keys(rows)


def test_rubric_grader_slice_excludes_release_gate():
    sliced = grader_rubric(RUBRIC.read_text(encoding="utf-8"))
    assert "baseline" not in sliced
    assert "Correctness" in sliced


def test_assign_labels_is_deterministic_and_sampled_over_groups():
    conditions = sorted({"baseline", "candidate"})
    first = assign_labels(("case-a", 1), conditions)
    assert first == assign_labels(("case-a", 1), conditions)
    # Different groups may map differently, but every group is a permutation.
    assert sorted(assign_labels(("case-b", 2), conditions).values()) == ["A", "B"]


def test_parse_judge_scores_checks_ranges():
    labels = {"baseline": "A", "candidate": "B"}
    payload = json.dumps(
        {
            "A": {
                "correctness": 4,
                "verification": 4,
                "actionability": 4,
                "safety": 4,
                "concision": 4,
                "blocker": False,
                "notes": "ok",
            },
            "B": {
                "correctness": 9,
                "verification": 4,
                "actionability": 4,
                "safety": 4,
                "concision": 4,
                "blocker": False,
                "notes": "out of range",
            },
        }
    )
    with pytest.raises(ValueError, match="must be between 1 and 5"):
        parse_judge_scores(payload, ("case-a", 1), labels)


def test_scenario_validates_and_loads():
    case = load_scenario(SCENARIO)
    assert len(case["turns"]) == 6
    turn_ids = [turn["id"] for turn in case["turns"]]
    assert turn_ids[-1] == "stop"


def test_scenario_rejects_single_turn(tmp_path):
    directory = tmp_path / "scenario"
    directory.mkdir()
    turn = {"id": "only", "prompt": "one turn"}
    case = {
        "id": "too-short",
        "category": "persistence",
        "prompt": "Evaluate",
        "risk": "low",
        "criteria": ["one"],
        "turns": [turn],
    }
    (directory / "case.jsonl").write_text(json.dumps(case) + "\n")
    with pytest.raises(ValueError, match="at least two turns"):
        load_scenario(directory)


def test_scenario_story_case_prompt_shape():
    cases = load_cases(SCENARIO / "case.jsonl")
    assert validate_cases(cases) == []
