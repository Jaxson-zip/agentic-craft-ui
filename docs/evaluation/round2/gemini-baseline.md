# Round 2 — Gemini baseline decisions

Applied the supplied `baseline/SKILL.md` and its `references/ui.md`, `references/delivery.md`, and `references/architecture-context.md`. This is an offline decision exercise. Only those instructions and the supplied scenarios were read. No application was inspected or modified, no network request was made, and no browser, build, lint, or application test was executed. Commands and implementation sketches below are proposals, not evidence of execution.

The supplied skill prioritizes user intent and existing authorization. Therefore the explicit autonomous decisions, approved palette, required navigation, and evaluation prohibition on questions take precedence over its style confirmation and ecosystem approval gates. Ecosystem research is unavailable here; I do not infer that suitable prior art does not exist. No external dependencies are needed for these sketches.

## A — Existing Vue renewal view

Treat this as a small brownfield feature. Reuse the existing button, tokens, data source, package manager, and test infrastructure. No prototype approval or broad architecture rewrite. Export the current filtered renewal rows, in the same order as the view; label the button “Export CSV” and communicate that scope in its accessible description. Use existing stable column labels and raw values, not strings copied from DOM cells.

### Investigation and commands

From the application root, the intended initial commands are:

```powershell
git status --short
rg --files -g AGENTS.md -g package.json -g pnpm-lock.yaml -g '*eslint*' -g '*vitest*' -g '*vite*' -g '*REPO_MAP*' -g '*snapshot*'
Get-Content -LiteralPath package.json
rg --files src tests
rg -n 'renewal|renewals|续费|export.*csv|text/csv' src tests
```

If `tests` is absent, use the actual test directory found by `rg --files`. Read relevant AGENTS rules, the renewal view, its composables and import/re-export chain, the current helper implementation, button component usage, and nearby tests. Inspect current user edits before changing anything. The two-week-old map is a locator only: yesterday's helper move requires tracing imports in current source, beyond an arbitrary one- or two-file limit.

For a discovered compatible snapshot, the intended map commands are:

```powershell
python G:/skill/agentic-craft-ui-evaluation/round-2/baseline/scripts/repo_map.py --help
python G:/skill/agentic-craft-ui-evaluation/round-2/baseline/scripts/repo_map.py . --check <discovered-snapshot-path>
```

Exit 1 means stale: regenerate at the existing project's map/snapshot locations, preserving its scope, then inspect moved source and consumers. Exit 2 means an error, not a fresh map. If the script, Python, or snapshot is unavailable, continue with `rg` and source reads. Update only affected map/document entries; do not create a new architecture documentation suite for this button.

### Implementable sketch

Add a small pure serializer beside the existing export/helper code, adapting the language to the project. Quoting every cell handles commas, quotes, and embedded newlines without a special-case detector:

```ts
export function csvCell(value: unknown): string {
  return `"${String(value ?? '').replace(/"/g, '""')}"`;
}

export function makeCsv(rows: readonly (readonly unknown[])[]): string {
  return rows.map(row => row.map(csvCell).join(',')).join('\r\n');
}
```

Construct a header plus explicit columns from `visibleRenewals`; do not serialize arbitrary API object properties. For example, `[row.name, row.renewalDate, row.amount, row.currency]` only if those are the actual discovered fields. Preserve existing date/currency semantics and precision. Use an explicit null-to-empty policy. Unicode should survive a UTF-8 download; a UTF-8 BOM may be added for spreadsheet compatibility using the project's existing export convention. Check any existing spreadsheet formula policy before exporting user-controlled fields; quote escaping alone does not neutralize formulas, and no undocumented transformation of values should be introduced.

Use an existing button with `type="button"`, disabled for zero exportable rows. Its handler snapshots the current rows, creates `new Blob(['\uFEFF', csv], { type: 'text/csv;charset=utf-8' })`, creates an object URL, clicks a temporary download anchor with a stable filename such as `renewals.csv`, removes the anchor, and revokes the URL after the download dispatch. Reuse existing notice/error handling if available. This is a client-side export; no new API request or persistence layer.

### Proposed verification

Add targeted Vitest cases for `ACME, Inc.`, `He said "renew"`, CR/LF in a field, null/empty cells, Chinese text, consistent header/order, and numeric zero. Assert exact output such as `"He said ""renew"""`. A view/handler test should prove the exported rows follow the filtered view and the button does not submit a containing form; reuse current component-test facilities. Keep production builds and lint within the existing scripts.

After replacing illustrative paths with discovered ones, intended commands are:

```powershell
pnpm exec vitest run <csv-test-path> <renewal-view-test-path>
pnpm exec eslint <changed-view-path> <changed-helper-path> <changed-test-paths>
pnpm run build
git diff --check
git diff --stat
```

Use the actual `package.json` scripts if they wrap these tools or supply required configuration. Run the existing type-check script only if present; do not invent one or install packages. If local browser access exists, run the project's existing dev command, click Export on comma/quote/Unicode fixtures, inspect the downloaded file, and confirm current filters, row order, empty behavior, focus, and styling. If browser/download inspection is unavailable, record it as blocked. The 20-minute deadline limits scope, not the truth of completion evidence. Here all application checks are **not run**; external research is **blocked** by the environment.

## B — Poetry journal reading prototype

Proceed with approved warm ivory and terracotta. Their editorial purpose and user approval override the reference's generic cold-white preference. Preserve an uncluttered reading experience rather than introducing a management shell. System serif for poetry and prose, system sans-serif for navigation and controls; no fonts or libraries fetched.

Proposed local files: `index.html`, `styles.css`, `app.js`. Layout: a modest journal masthead with issue title and an in-session bookmark count; an issue table of contents beside a centered reading column on wide screens; a single column with a collapsible contents panel below 760px. Reading width approximately `min(100%, 42rem)`, body 18px with 1.75 line-height, restrained heading sizes and 24–48px section spacing. Verse preserves authored line breaks via `white-space: pre-wrap`, while long words can wrap. At 320px, padding shrinks without clipping poetry or creating page overflow.

```css
:root {
  --bg-base: #fffaf2;
  --bg-surface: #fffdf8;
  --text-primary: #2d2824;
  --text-secondary: #65554c;
  --brand-accent: #9e472a;
  --border-subtle: #d5c5b6;
  --action-bg: #2d2824;
  --action-text: #fffaf2;
  --focus: #7b341e;
}
.reading { max-width: 42rem; font: 18px/1.75 Georgia, serif; }
.poem { white-space: pre-wrap; overflow-wrap: anywhere; }
button { min-height: 44px; }
:where(a, button):focus-visible {
  outline: 2px solid var(--focus); outline-offset: 3px;
}
```

Terracotta appears in issue markers, rules, links, and the selected bookmark indicator. Neutral dark text/background serves any prominent positive action, following the baseline CTA convention. No invented decorative macOS controls, dashboard cards, or emoji icons.

Keep a local article array containing id, title, author, type, and body. A contents link selects an article, renders its title/text, updates `aria-current`, and moves keyboard focus to the article heading (`tabindex="-1"`). Maintain `selectedId` and `new Set()` of bookmarked article IDs in memory. A native button uses `aria-pressed`, toggles membership, and changes its label between “Bookmark” and “Remove bookmark”; a polite status message confirms the change. Selection does not lose bookmarks during this open page session. Reload resets both states. Do not use localStorage, cookies, or network calls. Label the page “Local reading prototype — sample content; bookmarks last only while this page is open.” Use original short sample poems rather than assuming rights to external journal text.

With synchronous local data, a loading spinner is **not applicable**. Include a deliberate no-articles state (“No pieces in this issue”), an unavailable-selection message with return-to-contents action, an empty bookmark view with a link to contents, long titles, and a long poem. These are fixture states, not server failures.

Proposed checks: open the local HTML; select every article; toggle bookmarks twice; switch articles and revisit; reload to verify reset; verify contents disclosure via keyboard; check screen-reader names and selected state; inspect at 1440, 390, and 320px plus 200% zoom; measure text/button/focus contrast on actual backgrounds; honor reduced motion. If Node is installed, `node --check app.js` checks syntax only. A build, HTTP smoke, persistence test, and ER diagram are **not applicable** to this static prototype. No browser check was executed here.

Completion claim after those local checks pass: “The local reading prototype supports contents navigation, reading, and bookmarks within the current session. It uses sample content and has no persistence or server integration.” At present only the implementation decision is complete; the prototype and its checks are **not run**.

## C — Dense dark monitoring prototype

Choose a crisp dark operational console from the user's explicit direction: permanent left navigation on desktop, consistent incident rows, and a detail pane. This requested structure takes precedence over the skill's lightweight-tool center-flow preference. Use approximately `208px minmax(0, 1fr) 360px` columns at desktop widths, a restrained top status/filter bar, 14px ordinary text, 12px metadata, 40–44px rows, and tabular numerals for times and counts. No decorative glow that reduces legibility.

At 900–1199px, reduce navigation and show the detail pane beneath the list or as a selected-incident view. Below 900px, retain labeled navigation in an accessible toggle panel, render incident rows as compact stacked entries, and use a detail view with a “Back to incidents” control. Desktop permanence remains intact; mobile adaptation prevents the three columns from becoming unusable. Preserve selected incident and filters across responsive layout changes. Avoid page-wide horizontal scroll at 320px.

Concrete tokens deliberately use pale muted text and a pale-blue primary action so the dark theme's compact text remains readable:

```css
:root {
  color-scheme: dark;
  --bg-base: #0b1220;
  --bg-surface: #111b2e;
  --bg-hover: #162133;
  --border-subtle: #344155;
  --text-primary: #f3f6fb;
  --text-muted: #b8c2d1;

  --status-critical-text: #fecaca;
  --status-critical-bg: #451e28;
  --status-warning-text: #fde68a;
  --status-warning-bg: #40351c;
  --status-resolved-text: #bbf7d0;
  --status-resolved-bg: #163b2b;
  --status-neutral-text: #dbeafe;
  --status-neutral-bg: #243247;

  --primary-action-text: #0b1220;
  --primary-action-bg: #93c5fd;
  --primary-action-hover-bg: #bfdbfe;
  --focus-outline: #fbbf24;
}
body { background: var(--bg-base); color: var(--text-primary); }
.muted { color: var(--text-muted); }
.badge-critical {
  color: var(--status-critical-text);
  background: var(--status-critical-bg);
}
.primary {
  color: var(--primary-action-text);
  background: var(--primary-action-bg);
}
:where(a, button, input, select):focus-visible {
  outline: 2px solid var(--focus-outline); outline-offset: 3px;
}
.incident-time { font-variant-numeric: tabular-nums; }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation: none !important;
    transition: none !important;
    scroll-behavior: auto !important;
  }
}
```

All badges also contain severity words, never communicate solely through color. Use native links for navigation and native buttons for incident selection. For a simple dense list, standard Tab/Shift+Tab plus Enter/Space is sufficient; do not assign `role="grid"` without implementing its keyboard model. Selected row has a persistent visual marker and an accessible selected indication; activation updates the detail heading and focus predictably. On mobile Back returns focus to the selected row. Include a skip link and avoid nested competing click targets.

State sketch: `incidents`, `selectedId`, `filter`, `paused` held in memory. Seed normal incidents, a long service name, missing owner, and multiple severities. A controlled local timer changes one fixture's age/status, while a “Pause simulation” control stops updates and a visible label reads “Simulated monitoring data.” Preserve selection during updates and do not reorder focused rows automatically. Do not announce every timestamp tick. Optional “Acknowledge” changes only in-memory mock state and explicitly reports “Acknowledged in simulation.” Provide empty-filter reset, no-incidents state, and selectable simulated loading/error fixtures; none imply a failed backend integration.

Proposed acceptance criteria: ordinary text and primary-button labels reach at least 7:1 against every actual base/surface/hover background; muted readable metadata and status text reach at least 4.5:1 on their actual backgrounds (target 7:1 for compact text); focus outline reaches at least 3:1 against adjacent colors and remains unclipped. Measure the supplied tokens, not just the stock reference palette, including hover/selected states. Verify 1440/1280 desktop columns, 900px adaptation, 390/320px layout, 200% zoom, touch targets at least 44px, complete keyboard selection/filter/detail/back flow, pause behavior, long text, and reduced motion. Timer controls and scenario fixtures must work without any request to a server. All criteria are **proposed/not run**, and real ingestion/API integration is **not applicable** to this prototype.

## D — Polish the real subscription form

Use brownfield investigation: inspect the form, its imported input/button components and tokens, schema/types, category constant, API client/save handler, callers, and existing success/error tests. Trace the actual HTTP response handling; successful type-check/build does not establish runtime save behavior. Preserve field names, allowed values, validation, identity, endpoint, payload, and existing concurrency/retry contract.

Reject `开发工具` as a new submitted value: the server accepts exactly `影音娱乐`, `软件工具`, `生活服务`, and `其他`. Keep those four values and labels. If useful, explanatory text can clarify that development subscriptions fit under `软件工具`; do not add a new enum or silently remap a new option. This is a visual request, not category taxonomy or API redesign.

Implementable visual sketch: inherit current CSS variables; constrain form width to about 640px; clear heading, field groups with 16–24px spacing, associated labels, consistent 44px controls, stable inline error/help space, and one prominent existing Save button. Use a single column on small screens, preserve DOM/tab order, and retain visible focus. Bind styling to existing field-invalid and save-state signals rather than changing validation or replacing the submit pipeline. A field wrapper can use `aria-describedby` for help/error text and `aria-invalid` when the existing validator fails. All non-submit auxiliary controls must use `type="button"`.

State presentation must reflect actual outcomes:

- Saving: existing in-flight guard prevents duplicate submit; show “Saving…” and `aria-busy` while preserving values.
- Confirmed success: present saved state only after the existing response and record/version logic establish it.
- 409: retain the draft and expose an explicit conflict message. Offer the application's existing latest-record/diff flow; do not silently overwrite. Loading latest must not erase the retained draft without an explicit user choice.
- Timeout: use “Save outcome unknown; the server may have saved your changes.” Preserve the draft. Do not present a definite failure or automatically retry a mutation that may already have committed. Use an existing read/status reconciliation or idempotency mechanism if the current contract provides one. Do not invent an idempotency header or backend guarantee.

If those guards/reconciliation flows are absent, record the pre-existing behavior gap separately. A styling-only change must not quietly become a retry/concurrency redesign. The local review should expose the missing state handling as a concrete limitation; any proposed behavior repair remains separately scoped and unclaimed.

Proposed checks: targeted existing tests verify the exact four option values and unchanged payloads; deferred-save tests verify one in-flight request, retained values, and busy state; 409 fixtures verify draft preservation; timeout-after-commit fixtures verify uncertainty, no automatic duplicate POST, and reconciliation only if supported. Contract checks assert key response fields and resulting record/version state, not merely an HTTP status. Run the actual existing lint, targeted test, type-check, build commands and `git diff --check`, and inspect the diff for category/API changes. Do not perform a real subscription mutation solely to create review evidence.

The only known evidence supplied by the scenario is that **type-check and build pass**. Their exact commands, environment, revision, and relation to the eventual patch are unknown; record them as supplied prior evidence, not freshly run checks. Re-run them on the actual patch before claiming static validation. Browser validation is **blocked** in this run. Contrast calculations and source inspection could provide partial assurance, while layout, focus navigation, actual rendered feedback, and end-to-end saves remain unverified. No screenshots or visual pass should be fabricated.

Deliver a reviewable local diff with a concise checklist of proposed form states and precise validation results. A truthful completion statement would be: “The form styling is ready for local review, with the four API category values and save contract preserved. [Executed static checks and results]. Browser layout/keyboard verification is blocked; 409 and timeout save behavior is [tested status or specific gap].” Do not call the change fully visually verified, successfully integrated, or shipped externally on the basis of type-check/build alone. In this exercise, the result is this decision document; application implementation and all new verification remain **not run**.
