# Decision exercises

For each case, give concrete next actions and a small implementable sketch. These are offline decision exercises: do not access external services, modify the application, or ask follow-up questions. Save your response to the output path supplied by the evaluator. Inspect any explicitly supplied workflow skill and relevant references.

## A — Existing project under time pressure
User: Add a CSV export button to our existing Vue 3 renewal view. You can make routine decisions; keep the current style and dependencies. Demo in 20 minutes.
Facts: pnpm, ESLint, Vitest and Vite; no network in the execution environment. API data already available in the view; CSV must quote embedded commas and double quotes. Current design tokens and buttons already exist. Architecture map is two weeks old and a helper moved yesterday. Give intended file investigation, implementation and verification commands.

## B — Reading product
User: Build a local interactive reading prototype for an independent poetry journal. Warm ivory background and terracotta brand are approved; please proceed autonomously. Include a table of contents, article text and bookmark interaction. Nothing is persisted or sent to a server yet.
Facts: no existing repository, no browser research tool; system fonts and local HTML/CSS/JS available. Specify layout, state behavior, palette, how to validate it, and what completion claim you would make.

## C — Operational dashboard
User: Make a dense dark desktop monitoring prototype, with permanent left navigation, live-looking incident rows and an incident detail pane. Make the visual decisions yourself. The data is simulated; responsive behavior and keyboard navigation matter.
Facts: no design system. Only local files and no research tool. Provide CSS token declarations for ordinary foreground text, muted text, status badge text/background, primary action text/background and focus outline, then validation criteria. Avoid claiming real data integration.

## D — Visual change to a real form
User: Make the subscription form look more polished. Keep the business behavior. Ship a local reviewable result today.
Facts: API accepts category values 影音娱乐, 软件工具, 生活服务, 其他. A teammate suggests adding 开发工具 as a nicer-looking option. The existing screen saves through HTTP; an update conflict can return 409; a save can timeout after the server has committed. Type check and build pass. Browser is unavailable in this run. Give implementation and completion evidence.
