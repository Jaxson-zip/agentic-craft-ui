# Offline decisions — no additional UI workflow skill

These are proposed actions and implementable sketches. I read only the supplied scenario file. I did not inspect an application, run application checks, open a browser, access the network, or consult the evaluated skill. Paths below are discovered or illustrative, not claims about existing files.

## A — CSV export in the existing Vue renewal view

Use the existing button component and tokens. Export the renewal rows already available to the view, using the view's current filtering and ordering; disable the button when there are no rows. Do not introduce a dependency or redesign the screen.

First inspect the actual checkout rather than trusting the two-week-old architecture map:

```powershell
Get-Content -LiteralPath package.json
rg --files -g 'AGENTS.md' -g '*renew*' -g '*Renew*' -g '*csv*' -g '*CSV*' -g '*Button*' -g '*token*' -g '*vitest*'
rg -n 'renewal|Renewal|download|text/csv|exportCsv' src
```

Read applicable project instructions, the matched renewal component, its data mapping, neighboring button usage, and the current helper imports. If the architecture map points to yesterday's moved helper, locate its actual export with `rg -n 'helperExportName' src`; update no unrelated imports. Inspect available scripts and installed dependencies before choosing commands; no package installation in this environment.

Use explicit existing table fields and labels, not arbitrary keys from API objects. A small pure helper supports meaningful escaping tests:

```ts
export function csvCell(value: unknown): string {
  const text = value == null ? '' : String(value)
  return `"${text.replace(/"/g, '""')}"`
}

export function makeCsv(rows: readonly (readonly unknown[])[]): string {
  return rows.map(row => row.map(csvCell).join(',')).join('\r\n')
}
```

In the component, construct `[headers, ...visibleRows.map(toExportFields)]`, create a `Blob` with `text/csv;charset=utf-8`, obtain an object URL, click a temporary download anchor with a stable filename, remove the anchor and revoke the URL after the click has been dispatched. Connect this to the existing button's event convention. Keep row field selection in the view or its existing mapping layer.

Add focused Vitest cases for embedded commas, embedded double quotes, embedded line breaks, null values, and header/data ordering. For example, `csvCell('a,"b"')` must equal `"a,""b"""`. Verify using the discovered paths and existing scripts:

```powershell
pnpm exec vitest run <actual-csv-test-path>
pnpm exec eslint <actual-renewal-view-path> <actual-csv-helper-path> <actual-csv-test-path>
pnpm run build
```

Run the project's existing type-check script too if present. If a local browser is available, launch the existing Vite development script, export representative data, inspect the downloaded CSV and confirm the button matches its neighbors. If time or tooling prevents that interaction check, report it explicitly. Completion requires the relevant executed checks to pass; a proposed command is not evidence.

## B — Independent poetry journal reading prototype

Create local `index.html`, `styles.css`, and `app.js`. Use a quiet editorial layout: compact journal masthead, issue label, generous article title and byline, a left table of contents on wide screens, and a single reading column. Keep article measure around `64ch`; preserve poetry line breaks deliberately. On small screens put the contents above the article in a disclosure and keep the title and reading column within the viewport. Use a system serif stack for poems and titles and a system sans-serif stack for controls.

```css
:root {
  --paper: #fff8ed;
  --ink: #302720;
  --muted: #6b5548;
  --brand: #a4432d;
  --brand-ink: #fff8ed;
  --rule: #d8c5b1;
  --focus: #713224;
}
body { background: var(--paper); color: var(--ink); }
article { max-width: 64ch; line-height: 1.7; }
```

The table of contents uses real fragment links to article headings. Each bookmark is a native button with `aria-pressed`, a visible “Bookmark”/“Bookmarked” label, and an accessible name identifying the poem. Store bookmarked article IDs in a `Set` in memory. Reloading resets bookmarks. A small visible note explains that bookmarks last for this visit; do not promise persistence. Leave article reading usable if JavaScript fails. No loading state is necessary for static embedded text; provide a sensible empty bookmark list if that list is displayed.

```js
const bookmarked = new Set();
document.querySelectorAll('[data-bookmark]').forEach(button => {
  button.addEventListener('click', () => {
    const id = button.dataset.bookmark;
    if (bookmarked.has(id)) bookmarked.delete(id);
    else bookmarked.add(id);
    const active = bookmarked.has(id);
    button.setAttribute('aria-pressed', String(active));
    button.textContent = active ? 'Bookmarked' : 'Bookmark';
  });
});
```

Validate heading order, fragment targets, semantic landmarks, button names, toggling and reset behavior, and absence of network requests or storage calls. Check text/control contrast with a local calculation. If a local browser is available, inspect at roughly 360, 768, and 1440 pixels, at 200% zoom, and using Tab, Enter and Space. Confirm no horizontal overflow, preserved poem formatting and visible focus. The lack of a browser research tool does not establish whether a local browser is available. If no rendering tool is available either, report source and static checks separately and leave visual/interaction verification explicitly pending.

Appropriate completion wording, only after doing the named work: “Created a local reading prototype with contents navigation and temporary bookmarks. [List actual checks.] Browser visual checks remain pending if unavailable.” Do not claim researched design, persistence or server integration.

## C — Dense dark monitoring prototype

Use a desktop grid with a permanent 208px navigation rail, a flexible incidents list, and a 360px detail pane. The main area should shrink with `minmax(0, 1fr)` and contain overflow instead of overflowing the whole page. Use compact rows with readable text, explicit severity labels, timestamp and service, and a native button per row to open details. Mark the selected incident and keep selection distinct from severity. Show “Simulated data” near the page title.

```css
:root {
  color-scheme: dark;
  --canvas: #0b1220;
  --surface: #111c2e;
  --border: #34455e;
  --text: #edf2f7;
  --text-muted: #aebcd0;
  --critical-bg: #4a1b24;
  --critical-text: #ffd5dc;
  --warning-bg: #453411;
  --warning-text: #ffe3a3;
  --resolved-bg: #123b31;
  --resolved-text: #b8f3df;
  --primary-bg: #8ab4ff;
  --primary-text: #081426;
  --focus: #f8d77a;
}
body { background: var(--canvas); color: var(--text); }
.muted { color: var(--text-muted); }
.status-critical { background: var(--critical-bg); color: var(--critical-text); }
.status-warning { background: var(--warning-bg); color: var(--warning-text); }
.status-resolved { background: var(--resolved-bg); color: var(--resolved-text); }
.primary { background: var(--primary-bg); color: var(--primary-text); }
:focus-visible { outline: 3px solid var(--focus); outline-offset: 3px; }
```

Use native links for navigation and buttons for actions. Store `selectedIncidentId`, filters and simulated incidents locally. Selecting a row updates the detail pane and its labeled heading. Keep focus on the row for routine selection, with an explicit “Go to details” control if needed. A detail close/back control on narrow screens restores focus to the originating row. Navigation remains a visible left rail, narrowed to a labeled icon rail on small screens; accessible labels must remain available. Below the width needed for two content panes, display list or detail in the main region and provide a back control. Collapse secondary row metadata while retaining severity, service and incident summary.

If simulating updates, clearly label the simulation, keep insertion cadence moderate, and pause updates with a visible control. Do not move keyboard focus or reorder the focused row unexpectedly. Avoid flashing indicators; respect reduced motion. Show an explicit empty filter state and a local “incident no longer available” state when selection becomes invalid.

Validation criteria: ordinary and muted text meet at least 4.5:1 against every surface on which they appear; each badge label and primary action label meets 4.5:1 against its background; focus outline has at least 3:1 against adjacent surfaces and is never clipped. Calculate the actual pairs locally rather than inferring accessibility from hex colors. Test all controls using Tab/Shift+Tab and Enter/Space, selected incident updates, pause, filters, empty results and detail return focus. Check desktop density and narrow layouts, 200% zoom, no page-wide overflow, readable target sizes and reduced motion. Report any unexecuted browser checks. Completion means a local simulated monitoring prototype, with no claim of real incidents, live monitoring or integrated backend.

## D — Polish the real subscription form

Inspect the component, existing tokens, input components, validation bindings and HTTP save implementation first. Make a focused presentation change: consistent label spacing, alignment, readable helper/error text, clearer grouping and existing primary/secondary button hierarchy. Use existing components and responsive stacking. Preserve field names, values, event bindings, validation, submit behavior and state transitions.

Keep the exact category values `影音娱乐`, `软件工具`, `生活服务`, and `其他`. Do not add `开发工具`: the API does not accept it. Improve option styling or presentation within the existing category set.

```ts
const categories = ['影音娱乐', '软件工具', '生活服务', '其他'] as const
// Bind each option's submitted value to the same exact string.
```

Style the existing saving, field-error, conflict and timeout messages coherently without converting any of them into success. A 409 is a conflict, not a generic successful save; a timeout leaves the save outcome uncertain because the server may already have committed. Do not automatically resend after a timeout or discard unsaved values. Inspect the existing reconciliation behavior and preserve it. If these states are currently mishandled, record a concrete finding and avoid silently expanding a visual request into changes to HTTP semantics. Any proposed behavioral fix needs its own focused verification and scope decision.

Review the diff to ensure the visual edits leave category payloads and save handlers intact. Run the actual existing type-check and build scripts after the edits, plus the existing relevant form tests if present. If feasible, use the existing test harness to confirm category values and save-state rendering; do not invent backend behavior or a new server contract. The facts say type check and build pass, but that alone does not verify the new visual changes or browser behavior. Record the commands and exit results actually obtained in execution.

Because the browser is unavailable, the reviewable deliverable is the local source diff with a concise change note and verification record. No fabricated screenshot or rendered visual approval. A truthful completion statement would be: “The form presentation changes are available locally for review. Category values and save bindings are preserved by diff inspection; [actual executed checks] passed. Browser layout, keyboard interaction, and the real HTTP conflict/timeout flow remain unverified in this run.” Do not describe it as visually verified or production deployed.
