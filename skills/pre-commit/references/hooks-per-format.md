# Hooks per file format

One formatter and one linter per format. Staging blocks below the base
config from `SKILL.md` — append, do not re-declare a format that already
has an owner.

## Formats beyond the base config

| Format    | Formatter hook              | Linter hook                          |
| --------- | --------------------------- | ------------------------------------ |
| `.sh`     | `shfmt` (shfmt_pre_commit)  | `shellcheck` (shellcheck-py)         |
| `.css`    | prettier (already declared) | `stylelint`                          |
| `.html`   | prettier                    | —                                    |
| `.c`/`.h` | `clang-format`              | `clang-format` lint or `cpplint`     |
| `.rs`     | `rustfmt` ('fmt')           | `clippy` (runs via cargo, not hooks) |
| `.go`     | `gofumpt`                   | `golangci-lint`                      |
| `.ipynb`  | `nbQA` (`nbqa --isort`)     | —                                    |
| `.csv`    | — (do not reformat data)    | —                                    |

Pinned revs change; look up the current release tag of each repo when
adding a hook. Never copy a rev from this table blindly.

## Adding a hook

1. Find the formatter's pre-commit mirror or the upstream repo's own
   `pre-commit` metadata ("update mirrored hooks" on the pre-commit docs).
2. Append a `repo:` block, pin the latest release tag.
3. `pre-commit run --all-files`; every existing file must either pass or be
   fixed by exactly one formatter.
4. If two hooks touch the same file type, pick the winner and remove the
   loser — never keep both "because team members prefer both".

## Read-only checks in CI

Fixers live in pre-commit. If CI reruns the same tool, use check mode only:

- `ruff check` (without `--fix`)
- `prettier --check`
- `pre-commit run --all-files` (fine to run in CI, same hooks as local)
