"""Structural tests for Agent Skills content.

Validates every skills/*/SKILL.md against the structural rules of the
Agent Skills specification (https://agentskills.io/specification) that
can be checked without network access: frontmatter shape, naming rules,
size limits, and local reference integrity.

Full-spec validation runs separately in CI via `agentskills validate`.
"""

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent
SKILL_MD_PATHS = sorted(REPO_ROOT.glob("skills/*/SKILL.md"))

NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_BODY_LINES = 500
VALID_SECTIONS = {"scripts", "references", "assets"}


def parse_skill_md(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path}: missing frontmatter delimiter"
    end = text.find("\n---", 4)
    assert end != -1, f"{path}: unterminated frontmatter"
    frontmatter = yaml.safe_load(text[4:end])
    assert isinstance(frontmatter, dict), f"{path}: frontmatter must be a mapping"
    body = text[end + 4 :]
    return frontmatter, body


@pytest.mark.parametrize(
    "skill_md", SKILL_MD_PATHS, ids=lambda p: str(p.parent.relative_to(REPO_ROOT))
)
class TestSkillStructure:
    def test_required_frontmatter_fields(self, skill_md):
        fm, _ = parse_skill_md(skill_md)
        assert isinstance(fm.get("name"), str), "name must be a string"
        assert fm["name"], "name is required"
        description_field = fm.get("description")
        assert isinstance(description_field, str), "description must be a string"
        assert description_field.strip(), "description is required and must not be empty"

    def test_name_is_valid_and_matches_directory(self, skill_md):
        fm, _ = parse_skill_md(skill_md)
        name = fm["name"]
        assert len(name) <= MAX_NAME_LENGTH, f"name longer than {MAX_NAME_LENGTH} chars"
        assert NAME_PATTERN.match(name), (
            "name must be lowercase alphanumeric with single hyphens"
        )
        assert name == skill_md.parent.name, "name must match the parent directory name"

    def test_description_length_and_type(self, skill_md):
        fm, _ = parse_skill_md(skill_md)
        description = fm["description"]
        if isinstance(description, list):  # YAML folded scalar style
            description = " ".join(description)
        assert len(description) <= MAX_DESCRIPTION_LENGTH, (
            f"description longer than {MAX_DESCRIPTION_LENGTH} chars"
        )

    def test_metadata_values_are_strings(self, skill_md):
        fm, _ = parse_skill_md(skill_md)
        metadata = fm.get("metadata")
        if metadata is not None:
            assert isinstance(metadata, dict), "metadata must be a mapping"
            assert all(isinstance(v, str) for v in metadata.values()), (
                "metadata values must be strings"
            )

    def test_body_under_line_limit(self, skill_md):
        _, body = parse_skill_md(skill_md)
        line_count = len(body.splitlines())
        assert line_count <= MAX_BODY_LINES, (
            f"body has {line_count} lines (limit {MAX_BODY_LINES}); "
            "move detail into references/"
        )

    def test_optional_sections_are_known(self, skill_md):
        for child in skill_md.parent.iterdir():
            if child.is_dir():
                assert child.name in VALID_SECTIONS, (
                    f"unexpected directory '{child.name}'; allowed: {sorted(VALID_SECTIONS)}"
                )

    def test_local_reference_links_resolve(self, skill_md):
        _, body = parse_skill_md(skill_md)
        links = re.findall(r"\]\(([^)#\s]+)\)", body)
        for link in links:
            if "://" in link or link.startswith("mailto:"):
                continue
            target = (skill_md.parent / link).resolve()
            assert target.exists(), f"broken relative link: {link}"
            assert target.is_relative_to(skill_md.parent), f"link escapes skill root: {link}"


def test_repository_has_skills():
    assert SKILL_MD_PATHS, "no SKILL.md found under skills/"


# --- Token budget (token-efficient writing, cf. caveman) -----------------

# Rough token estimate: ~4 chars per token for English/technical prose.
# Real tokenizers vary per agent; this heuristic is deterministic and
# good enough to catch regressions.
CHARS_PER_TOKEN = 4
MAX_BODY_TOKENS = 1200
MAX_DESCRIPTION_TOKENS = 200


def estimate_tokens(text: str) -> int:
    return len(text) // CHARS_PER_TOKEN


@pytest.mark.parametrize(
    "skill_md", SKILL_MD_PATHS, ids=lambda p: str(p.parent.relative_to(REPO_ROOT))
)
class TestTokenBudget:
    def test_description_within_budget(self, skill_md):
        fm, _ = parse_skill_md(skill_md)
        description = fm["description"]
        if isinstance(description, list):
            description = " ".join(description)
        cost = estimate_tokens(description)
        assert cost <= MAX_DESCRIPTION_TOKENS, (
            f"description costs ~{cost} tokens (limit {MAX_DESCRIPTION_TOKENS}); "
            "it loads into every agent's context at startup — tighten the trigger"
        )

    def test_body_within_budget(self, skill_md):
        _, body = parse_skill_md(skill_md)
        cost = estimate_tokens(body)
        assert cost <= MAX_BODY_TOKENS, (
            f"body costs ~{cost} tokens (limit {MAX_BODY_TOKENS}); "
            "move lookup material into references/"
        )
