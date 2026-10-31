"""Tests for distribution metadata (.claude-plugin)."""

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
PLUGIN_JSON = REPO_ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE_JSON = REPO_ROOT / ".claude-plugin" / "marketplace.json"
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def test_plugin_json_is_valid_semver():
    plugin = json.loads(PLUGIN_JSON.read_text())
    assert SEMVER.match(plugin["version"]), (
        f"plugin.json version {plugin['version']!r} is not semver (x.y.z)"
    )


def test_marketplace_plugins_reference_existing_skills():
    marketplace = json.loads(MARKETPLACE_JSON.read_text())
    for entry in marketplace["plugins"]:
        for skill in entry.get("skills", []):
            skill_dir = (REPO_ROOT / skill).resolve()
            assert (skill_dir / "SKILL.md").is_file(), (
                f"marketplace references missing skill: {skill}"
            )


def test_marketplace_versions_match_plugin():
    plugin = json.loads(PLUGIN_JSON.read_text())
    marketplace = json.loads(MARKETPLACE_JSON.read_text())
    versions = {e.get("version") for e in marketplace["plugins"] if e.get("version")}
    assert versions <= {plugin["version"]}, (
        f"marketplace plugin versions {versions} disagree with plugin.json {plugin['version']}"
    )


@pytest.mark.parametrize("path", [PLUGIN_JSON, MARKETPLACE_JSON])
def test_metadata_files_parse(path):
    json.loads(path.read_text())  # raises on invalid JSON
