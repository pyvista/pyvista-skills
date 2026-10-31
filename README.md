# PyVista Skills

[![skills.sh](https://skills.sh/b/pyvista/pyvista-skills)](https://skills.sh/pyvista/pyvista-skills)

Official [Agent Skills](https://agentskills.io/specification) for [PyVista](https://github.com/pyvista/pyvista), the Python library for 3D visualization and mesh analysis.

Skills are reusable instruction packages (`SKILL.md` files) that teach AI coding agents how to work with PyVista effectively — writing correct plotting code, loading and filtering meshes, and verifying rendered output. They follow the open [Agent Skills specification](https://agentskills.io/specification) and work with any compatible coding agent, including Claude Code, OpenAI Codex, Cursor, OpenCode, Gemini CLI, and pi.

## Installation

### Skills CLI (all agents)

Using the [skills CLI](https://github.com/vercel-labs/skills), which auto-detects installed agents:

```sh
npx skills add pyvista/pyvista-skills
```

Useful flags:

```sh
npx skills add pyvista/pyvista-skills -g            # install globally (user-level)
npx skills add pyvista/pyvista-skills -a <agent>    # target a specific agent
npx skills add pyvista/pyvista-skills --copy        # copy instead of symlink
npx skills add pyvista/pyvista-skills -l            # list skills without installing
```

### Claude Code plugin marketplace

In Claude Code, you can also add this repository as a plugin marketplace:

```text
/plugin marketplace add pyvista/pyvista-skills
```

### Manual installation

Copy the skill directory (for example `skills/pyvista/`) into your agent's skills folder:

| Agent        | User-level path                            | Project-level path |
| ------------ | ------------------------------------------ | ------------------ |
| Claude Code  | `~/.claude/skills/`                        | `.claude/skills/`  |
| pi           | `~/.pi/agent/skills/`, `~/.agents/skills/` | `.agents/skills/`  |
| Other agents | use `npx skills add` auto-detection        | —                  |

Verified: the skills CLI discovers this repository and installs `pyvista` to `~/.agents/skills/` (pi) and `~/.claude/skills/` (Claude Code).

## Skills

| Skill     | Description                                                                              |
| --------- | ---------------------------------------------------------------------------------------- |
| `pyvista` | Core PyVista visualization workflows: plotting, mesh I/O, filtering, and common pitfalls |

More skills are planned — see the [roadmap](https://github.com/pyvista/pyvista-skills/issues/1).

## Repository layout

```text
skills/
  pyvista/
    SKILL.md          # skill entry point (frontmatter + instructions)
    references/       # detailed docs loaded on demand
.claude-plugin/       # Claude Code plugin marketplace metadata
.github/workflows/    # CI: spec validation and content tests
```

## Contributing

Skills must validate against the [Agent Skills specification](https://agentskills.io/specification). CI checks frontmatter validity, naming rules, and content structure on every pull request. See `CONTRIBUTING.md` for authoring guidelines (coming soon).

## License

Distributed under the [MIT License](LICENSE), matching PyVista core.
