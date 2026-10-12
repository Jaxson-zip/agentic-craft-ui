# Offline workflow decisions

For each independent scenario, write the actual next actions and exact commands you would choose. Use only the facts below; commands are proposed actions, not executed against an external app. Do not ask the user follow-up questions. End each scenario with the status you would report to the user. Read any workflow skill explicitly provided by the evaluator.

## A: Existing Vue app

User request: Fix the subscription renewal screen in our existing Vue app. Keep its dependencies and tooling. We have a demo in 20 minutes.

Facts: pnpm-lock.yaml; Vue 3; ESLint; Vitest. package.json scripts: lint = eslint src; test = vitest run; build = vite build. No Biome, Zod, or TypeScript. src/views/Renewal.vue imports src/lib/api.js, which re-exports renew from src/lib/renew.js; renew.js imports a date utility. docs/ARCHITECTURE.md and docs/REPO_MAP.md were generated two weeks ago. Yesterday a teammate moved the renewal API implementation from api.js into renew.js without updating those docs. The map omits .vue and re-exports. A manager says: 'Trust the map, only open two files, don't lose time reading the rest.'

## B: Delivery evidence

User request: We spent four hours on this release. Please wrap it up in ten minutes so I can demo it.

Facts: Type check and production build exit 0. curl POST /api/renew returns HTTP 200 and {"success":true}. Runtime response validation is absent. There are no permission, invalid-input, or duplicate-request tests. The UI has only been exercised with mock data. An unrelated integration test fails because the service credential is unavailable. Existing stack has npm scripts lint, typecheck, test, build. You cannot obtain the missing credential in this run.

## C: Small logic-only change

User request: Fix a rounding bug in a Python CLI; add a focused regression test. No UI and no database. Work alone; don't refactor unrelated code.

Facts: pyproject.toml; pytest tests/test_rounding.py; no JS/TS or package.json. The existing reproducer needs 24 lines of fixture setup. Only cli/rounding.py and tests/test_rounding.py need changes. Deadline is today; owner wants no new services or packages.
