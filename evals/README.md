# Evaluations

The harness compares response quality, not just structure. The structural tests
in `tests/` check that a `SKILL.md` parses and stays within budget; the evals
here measure whether an installed skill actually changes agent output on
PyVista tasks. Cases live in `cases.jsonl`; the scoring contract lives in
`rubric.md`.

Adapted from [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) (MIT).

## Validate and plan

```bash
python3 scripts/run_evals.py validate
python3 scripts/run_evals.py plan --trials 3 --include-comparator
```

## Run

Run each condition into the same results file. Candidate and comparator instructions are injected from the supplied skill file; task prompts remain identical.

```bash
python3 scripts/run_evals.py run \
  --runner claude \
  --condition baseline \
  --trials 3 \
  --budget-usd 12.50 \
  --output evals/results/responses.jsonl

python3 scripts/run_evals.py run \
  --runner claude \
  --condition candidate \
  --condition-skill skills/pyvista/SKILL.md \
  --trials 3 \
  --budget-usd 12.50 \
  --output evals/results/responses.jsonl
```

The default Claude runner reports dollar cost and receives the remaining condition budget on every call. Runners without cost reporting are rejected unless `--allow-unmetered` is supplied; use that flag only when the provider account has its own hard cap.

Both example runners isolate the call from the operator's own agent configuration: `--setting-sources ""` for Claude, `--ignore-user-config --ephemeral` for Codex. Keep that isolation when adding runners: without it, user-level plugins, hooks, memory, and output styles leak into every condition and shape the responses being judged.

Isolation also drops the operator's saved model and effort settings, so the claude runner pins `--model` explicitly. Keep a pin when editing the runner: without one, the eval silently runs whatever the operator (or the CLI release) defaults to; the model would vary between operators and over time, and per-token cost varies with it. The pinned model is part of the result: record it with published numbers.

Runs are resumable: rerun the same command after a provider failure and completed `(case, trial, condition, runner)` rows are skipped. Each incomplete call is retried twice by default, and the final provider error is preserved.

## Measure

Aggregate token usage, reported cost, and response length from the completed responses file:

```bash
python3 scripts/run_evals.py measure evals/results/responses.jsonl
```

The summary reports input/output token totals, reported generation cost, stored response length, and candidate-minus-baseline deltas. Positive deltas mean more usage or cost; negative deltas mean less. Read these alongside quality scores.

Comparisons require the same runner and identical `(case_id, trial)` coverage, without duplicates. If rows include `model`, every row must name the same model. `model: null` means model comparability is unverified.

Missing costs or token counts produce `null` totals and deltas, not zero. This measures recorded generation rows, not total provider billing: judge costs and unrecorded failed/retried calls are excluded. The command is read-only and makes no model calls.

## Judge and score

`scripts/judge.py` grades the responses and writes the score rows for you:

```bash
python3 scripts/judge.py \
  --runner claude \
  --responses evals/results/responses.jsonl \
  --output evals/results/scores.jsonl
```

It groups responses by `(case_id, trial)` and grades every condition for a case in one call, so the conditions are compared against each other rather than scored in isolation. Blinding is structural, not a convention the grader is asked to respect: each condition is relabelled `A`/`B`/`C` before the prompt is built, and the label order is permuted per group, so position carries no signal. The permutation comes from a digest of the group key rather than a random source, so a resumed run reproduces the labels it used the first time.

Only the region of `rubric.md` between the `<!-- judge:begin -->` and `<!-- judge:end -->` markers reaches the grader. The release-gate rules below those markers name the conditions, and sending them to a blind grader would leak the vocabulary the blinding exists to hide.

Runs are resumable the same way generation is: groups already present in the output file are skipped. A group missing a condition cannot be scored, so it is reported on stderr and left out rather than silently dropped.

Judging by hand instead is still supported: blind the `condition` field yourself and write one JSON object per response with these fields.

```json
{
  "case_id": "headless-render",
  "trial": 1,
  "condition": "candidate",
  "correctness": 5,
  "verification": 5,
  "actionability": 5,
  "safety": 5,
  "concision": 5,
  "blocker": false,
  "notes": "Runnable code plus an observed-output check."
}
```

Either way, apply the release gate:

```bash
python3 scripts/run_evals.py score evals/results/scores.jsonl
```

Record the exact CLI and model versions with published results, including measured token and cost numbers. Do not compare conditions produced with different cases, models, trial counts, or rubrics.

## Scenario captures

Multi-turn scenarios live in `evals/scenarios/<name>/` (`case.jsonl` with full
turn list, `story.md` with capture instructions). Each scenarios ships one
response row, comparable with the same judge and score workflow. See
`evals/scenarios/render-blank-debug-spiral/story.md` for the workflow and the
spending caveats.
