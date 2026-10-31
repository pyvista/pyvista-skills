---
name: template-skill
description: Replace with a one-paragraph activation trigger — what the skill does, when to use it, and when not to use it. This line loads into every agent's context at startup; make it precise and keep it under 1024 characters.
---

# Template Skill

Replace this file's content. Guidance, with the reasoning inline:

- Open with the smallest correct mental model of the domain (one or two sentences). State the default assumptions (versions, backends) so agents do not guess.
- Give the core workflow as numbered steps with one runnable code block. Every example must be runnable as written: imports included, no pseudo-code.
- List the array/API contracts that prevent wrong code (types, shapes, units, mutation semantics). One fact per bullet; never restate a fact.
- End sections with a short "Pitfalls" list — concrete mistakes and their symptom, not paraphrased docs.
- If the skill produces verifiable output, finish with a verification snippet the agent can run and judge.
- Keep the body well under 500 lines. Lookup tables and option-level detail go into `references/<topic>.md`, linked with relative paths one level deep.
- Delete this guidance before committing.
