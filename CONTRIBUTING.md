# Contributing

Skills follow the [Agent Skills specification](https://agentskills.io/specification). CI enforces the rules below on every pull request; run them locally before pushing.

## Local checks

```sh
pip install pre-commit && pre-commit install   # one-time setup
pre-commit run --all-files                     # whitespace, yaml, ruff
npx markdownlint-cli2                          # markdown lint (config: .markdownlint-cli2.jsonc)
npx prettier --check .                         # markdown formatting
python -m pytest -q                            # structural + eval-harness tests
uvx --from skills-ref agentskills validate skills/<name>  # spec validation
python3 scripts/run_evals.py validate          # eval case catalog (offline, no spend)
```

Behavioral evaluation (does an installed skill change agent output?) lives in `evals/` with its harness in `scripts/run_evals.py`, `scripts/judge.py`, and `scripts/run_scenario_eval.py`. Offline subcommands (`validate`, `plan`, `score`, `measure`, scenario `validate`) run without network access and are covered by pytest; anything that spends money is documented in `evals/README.md` and never runs in CI.

Python files (tests, scripts) are linted with **ruff**, all rules enabled (`select = ["ALL"]`; documented exceptions in `ruff.toml`). Markdown is formatted with **prettier**; ruff does not touch Markdown code blocks.

## Authoring a skill

1. Copy `template/SKILL.md` into a new `skills/<name>/` directory. The `name` in frontmatter must match the directory name: lowercase letters, digits, and single hyphens, ≤64 chars.
2. Write the `description` as an activation trigger: what the skill does, when to use it, and when **not** to use it. It is loaded into every agent's context at startup — that line is the skill's always-on cost. Max 1024 chars.
3. Keep the body under 500 lines (CI fails above it). Target far less: every line runs on every activation.
4. State each fact once. Move option tables, format lists, and other lookup material into `references/<topic>.md` (one level deep, relative links).
5. Technical content — code, commands, paths, numbers, API names, error strings — stays verbatim. Never paraphrase an API or drop a parameter to save space.
6. Prefer ruling out mistakes over exhaustive coverage: a short "Pitfalls" list beats a paraphrased API tour.
7. If the skill verifies output (rendering, files), end with a concrete verification snippet an agent can run.

## Review checklist

- [ ] `agentskills validate skills/<name>` passes
- [ ] Frontmatter `name` matches the directory; `description` is a trigger, not prose
- [ ] Body is token-lean: no filler, no duplicated facts, lookup detail in `references/`
- [ ] Examples are runnable as written (imports included, versions stated)
- [ ] Verification snippet included when the skill produces renderable/file output
- [ ] All CI jobs pass

## Filing issues

Open an issue describing the workflow the skill should teach. Feature requests for existing skills: include the exact command or code that behaved unexpectedly and what the agent did instead.
