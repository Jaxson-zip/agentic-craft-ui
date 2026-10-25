# Agentic Craft UI reliability revision

Scope accepted in this conversation: retain UI-first, logic-first, and brownfield modes; remove unsupported performance guarantees; make reference loading conditional; update snapshots when source changes; adapt checks to existing tooling. Prepare and verify a local revision before any publication.

## Design

- Keep SKILL.md as a concise router and shared decision rules. Put UI, architecture/context, collaboration, and delivery details in references/.
- Retain a zero-dependency Python helper. It inventories JS/TS/Vue files and recognizes common exports heuristically; it is not an AST, dependency graph, architecture generator, or dead-code detector.
- Scan from the supplied project root, preserve line locations, expose omissions/errors, and include source/config content hashes. A JSON snapshot can be checked for freshness. Architecture still needs targeted source review.
- Preserve project tools and existing authorization. Parallel work is conditional on independence and available tools; file scopes are conventions unless the host enforces them.
- Delivery evidence separates lint/type checks, runtime contracts, business assertions, UI behavior, and production build. Unavailable checks remain visible.

## Implementation checklist

- [x] Run offline baseline decisions without the revision and against the original skill; record observed issues.
- [x] Add repo-map regression tests, run them against the original implementation, and record failures.
- [x] Implement deterministic exports, Vue script indexing, explicit truncation/errors, and source/config fingerprint checks.
- [x] Revise SKILL.md and add conditional references; rewrite README to reflect actual capabilities and portable installation.
- [x] Run script tests, skill metadata/link validation, and an independent evaluation with the revised skill.
- [x] Review the final diff and record results and limitations in docs/VALIDATION.md.

## Verification commands

Run from the repository root:

```text
python -m unittest discover -s tests -v
python scripts/repo_map.py --help
python -X utf8 C:/Users/Jaxson/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
git diff --check
```

Behavior checks use the three scenarios in tests/behavior/scenarios.md: an existing Vue project with stale maps and tool constraints; a release with incomplete runtime evidence; a small Python CLI fix. Record decisions rather than claiming a full application implementation or model benchmark.
