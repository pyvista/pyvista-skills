---
name: pre-commit
description: >-
  Configure pre-commit hooks that format and lint every file format in one
  repo: Python (ruff), Markdown (prettier + markdownlint-cli2), YAML, JSON,
  TOML (pre-commit-hooks), and shell (shfmt + shellcheck), with rules for
  resolving formatter conflicts and moving CI lint jobs into pre-commit. Use
  when setting up lint/format automation, fixing hook conflicts, or
  consolidating scattered CI lint steps. Do not use for runtime version
  management (pyenv/uv) or non-git-hooks tooling.
---

# Pre-Commit

Pre-commit runs formatters and linters on changed git files through one
`.pre-commit-config.yaml`. Pin every `repo` block to a tag rev. Locally the
loop is: edit, `git add`, `git commit` — hooks run and fix automatically.
CI and first-time runs must use `--all-files` because staged mode only sees
tracked changed files.

## Core workflow

```sh
pip install pre-commit && pre-commit install
pre-commit run --all-files
```

Minimal config that covers the six common file formats:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-toml
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.17.3
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: local
    hooks:
      - id: prettier
        name: prettier
        entry: npx --yes prettier --write --ignore-unknown
        language: system
        types: [markdown]
      - id: markdownlint
        name: markdownlint-cli2
        entry: npx --yes markdownlint-cli2
        language: system
        types: [markdown]
```

Additional formats go into `references/hooks-per-format.md`.

## Invariants

- One fixer per file type. Two formatters over the same bytes fight
  forever: each commit rewrites the other's output.
- Formatter conflicts are resolved by scoping `files:` regexes. One fixer
  per file type. Example: `ruff >= 0.17` formats Python inside Markdown
  code fences, so scope it with `files: \.py$` and let prettier own
  Markdown entirely.
- Fixers run in pre-commit; CI runs checks only (`ruff check`,
  `prettier --check`, or the same hooks via `pre-commit run --all-files`).
  The same fixer in both places means duplicated or conflicting edits.
- `rev` is a tag, never a branch. Renovate/dependabot keeps it current.

## Pitfalls

- First run modifies files and exits nonzero; the second run passes.
  That is fixers working, not a bug. `git add` their output and commit.
- `mirror` repos (pre-commit/mirrors-prettier) are deprecated; community
  forks (rbubley/mirrors-prettier) or local `npx` hooks are stable today.
- `language: system` hooks fail clean in CI when `node` is missing —
  install in a prior CI step or pin a runner image.
- `--all-files` is the whole-repo run: slow on big monorepos. Use
  `files:` excludes, not manual file lists, to keep the blast radius tight.

## Verify

```sh
pre-commit run --all-files && git diff --exit-code
```

Exit 0 from both commands proves: hooks pass and all fixers are
idempotent. If the second fails, two hooks are fighting over the same
files; scope one out.
