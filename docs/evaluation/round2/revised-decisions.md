# Revised offline decisions

Applied `agentic-craft-ui/SKILL.md` and its UI, architecture/context, delivery and visual-presets references; inspected `assets/themes.css`. These are implementation decisions, not application edits or executed checks. No network, external service or browser was used.

## A — Vue renewal CSV export

Keep Vue 3, current tokens/buttons, pnpm, ESLint, Vitest and Vite. Add one native `type="button"` export action beside the view's existing actions. Export the currently displayed renewal records, respecting existing filtering/sorting, with explicit existing field order and column labels. Disable the action when there are no displayed records; no new API call or dependency.

Investigate from the application root:

```powershell
rg --files -g AGENTS.md -g package.json -g pnpm-lock.yaml -g '*Renew*' -g '*renew*' -g '*csv*' -g '*test*' -g '*spec*' -g '*eslint*' -g '*vite*' -g '*vitest*'
rg -n 'renewal|续费|export|CSV' src tests
rg -n 'scripts|lint|test|build|dev' package.json
```

Read the located renewal view, its data/filter source, current button component/tokens, moved helper and all relevant imports/re-exports/consumers/tests. Treat the two-week-old map as a search hint. Search the helper's symbol in current source; if an existing snapshot is available, check it using the skill script after reading `--help`, and refresh only affected existing documentation when stale. Do not make map regeneration a demo prerequisite.

Small sketch, adapted to existing JS/TS conventions:

```js
const cell = value => '"' + String(value ?? '').replaceAll('"', '""') + '"';
const csv = [columnLabels, ...displayedRows.map(toExistingExportFields)]
  .map(row => row.map(cell).join(',')).join('\r\n');
const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
const link = document.createElement('a');
link.href = url;
link.download = 'renewals.csv';
link.click();
setTimeout(() => URL.revokeObjectURL(url), 1000);
```

Use existing date/unit formatting deliberately; do not stringify entire objects or silently drop fields. Unit cases: comma, embedded quote, newline, Unicode, null, empty set and stable header/order; e.g. `a,"b"` must become `"a,""b"""`. Verify a download contains the displayed records and quotes round-trip correctly.

Intended checks after reading actual scripts: use the project's documented lint/test/build commands. If no script wraps the installed tools, run `pnpm exec eslint <changed-files>`, `pnpm exec vitest run <located-export-test>`, and `pnpm exec vite build`; replace placeholders with discovered paths. Start the existing dev script, or `pnpm exec vite --host 127.0.0.1`, and exercise export, empty state and keyboard focus in an available local browser. No install/network prerequisite. All checks: **not-run** in this exercise; browser availability: unknown. The 20-minute deadline limits scope, not the evidence standard.

## B — Independent poetry journal

Build local `index.html`, `styles.css`, `app.js` with no dependencies. Use a quiet masthead, a table of contents beside an article on desktop, and contents above the article on narrow screens. Article width `min(100%, 66ch)`, body `Georgia, "Times New Roman", serif`, 18px/1.75; UI uses system sans. Preserve poem line breaks with `white-space: pre-wrap`; permit long words to wrap. Avoid decorative cards and a dashboard sidebar.

Palette sketch:

```css
:root {
  --page: #F7F0E5; --surface: #FFF9F0;
  --text: #32251F; --muted: #6B584D;
  --brand: #9C482E; --brand-hover: #843C26; --brand-active: #72331F;
  --on-brand: #FFFFFF; --focus: #9C482E;
}
article { max-width: 66ch; font: 18px/1.75 Georgia, "Times New Roman", serif; }
:focus-visible { outline: 2px solid var(--focus); outline-offset: 3px; }
```

Use original sample article/poem text labelled as prototype content. Contents are real links to article headings. Each article has a native bookmark button with `aria-pressed`; clicking updates an in-memory `Set` and visible “Bookmarked” / “Bookmark” text. Changing article preserves the set within this page session; reload clears it. Display “Local prototype · bookmarks reset on reload.” No localStorage, server or fake network loading state. No artificial error state for static articles; an empty bookmarked list says “No bookmarks yet” and offers the contents link.

Validate locally: navigate contents, bookmark/unbookmark, switch articles, verify empty bookmarks and reload reset; keyboard-only path and visible focus; desktop/narrow layouts, breakpoint sides, 200% zoom, long headings and poem line breaks. Calculate normal/hover/active text/background ratios (ordinary and muted text ≥4.5:1, focus against its actual adjacent surface ≥3:1). All runtime, rendering and contrast checks: **not-run** here. Backend/persistence integration: **not-applicable**. Eventual claim only with evidence: “The local reading path and session-only bookmarks work in the tested browser and viewport sizes.” Current claim: design and implementation sketch prepared; no prototype built or tested.

## C — Dense dark monitoring prototype

Use a desktop grid: 192px permanent left navigation, flexible incident list, 360px detail pane. Rows carry severity text, service, summary, timestamp and explicit selected state; timestamps use tabular numerals. Use 14px ordinary text with roughly 40px rows, preserving readable critical fields. Header clearly says “Simulated incidents”; show “Last simulated update,” never “Connected.” Local timer/update control may change sample rows; a pause control stops simulation. Selection and acknowledgement affect only local state and use “Acknowledged in this demo.”

CSS tokens, preserving the skill's opaque dark preset pairs:

```css
:root {
  color-scheme: dark;
  --bg-page: #090A0F; --bg-card: #14161F;
  --bg-card-hover: #1A1D28; --bg-muted: #1D202B;
  --text-primary: #F2F3F5; --text-secondary: #B4BDCB; --text-muted: #A6ADB9;
  --border-subtle: #323747; --border-strong: #A6ADB9;
  --badge-success-text: #86EFAC; --badge-success-bg: #123321;
  --badge-warning-text: #FCD34D; --badge-warning-bg: #392A12;
  --badge-danger-text: #FDA4AF; --badge-danger-bg: #3D1A21;
  --badge-neutral-text: #CBD5E1; --badge-neutral-bg: #252833;
  --brand-primary: #93C5FD; --on-brand: #0B1220;
  --brand-primary-hover: #BFDBFE; --brand-primary-active: #60A5FA;
  --focus-ring: #93C5FD;
}
.workspace { display: grid; grid-template-columns: 192px minmax(0, 1fr) 360px; }
.primary { color: var(--on-brand); background: var(--brand-primary); }
.primary:hover { background: var(--brand-primary-hover); }
.primary:active { background: var(--brand-primary-active); }
:focus-visible { outline: 2px solid var(--focus-ring); outline-offset: 3px; }
@media (max-width: 1100px) {
  .workspace { grid-template-columns: 160px minmax(0, 1fr); }
  .detail { grid-column: 2; }
}
@media (max-width: 640px) {
  .workspace { grid-template-columns: 56px minmax(0, 1fr); }
  /* Keep navigation visible as a compact rail with accessible link names. */
}
```

At narrow widths, stack details below the incident list in the content column and reflow each row's secondary fields; keep permanent navigation and main actions accessible. Any unavoidable table overflow stays inside its labelled container. Navigation uses links with `aria-current`; incident selection uses native buttons with accessible names and `aria-pressed`, followed by a labelled detail region. Tab/Shift+Tab and Enter/Space complete selection and acknowledgement; never make row content hover-only. Update the selected row without stealing focus; announce user-triggered selection/status changes politely, not every timer tick. No unnecessary motion; honor reduced-motion if added.

Validate normal, selected, long-summary, zero-incidents and empty-filter states; desktop, 1100px/640px breakpoint sides, narrow screen and 200% zoom; all keyboard actions, visible/unclipped focus, full critical labels and no page overflow. Numerically check all text including badge/action hover/active pairs ≥4.5:1 and focus/necessary control boundaries against adjacent surfaces ≥3:1. Subtle decorative borders need not meet control-boundary contrast. The reference reports preset pair tests; those do not certify this proposed page. Current checks: **not-run**; real incident integration: **not-applicable**. Claim only a local simulation after its interactions/rendering are actually verified.

## D — Polish the subscription form

Read existing form/component/styles, category definitions and submit serializer, response handling, conflict/timeout paths, relevant tests and package scripts. Reuse current tokens and inputs. Improve grouped spacing, label/help/error alignment, field widths and primary-action hierarchy; keep narrow-screen fields stacked and error text next to the affected input. Native labels remain associated with controls, errors use `aria-describedby`, and the existing saving indicator retains inputs and prevents duplicate submissions.

Keep submitted categories exactly `影音娱乐`, `软件工具`, `生活服务`, `其他`. Reject adding `开发工具`: it is not an accepted API value and no approved display-to-value mapping exists. Do not relabel a value in a way that changes its meaning. Sketch:

```js
const allowedCategories = ['影音娱乐', '软件工具', '生活服务', '其他'];
// Render these existing values; preserve the current payload shape and validator.
```

Preserve and inspect the actual save state machine. Confirmed successful response/state reconciliation may show “Saved.” A 409 retains the draft and offers the existing supported way to inspect latest values; do not automatically resubmit stale fields with a newer version. A timeout may already have committed: retain input, show “Save result unknown; check latest status,” and reconcile through the existing read/operation identifier if available before permitting a write retry. Do not invent idempotency headers, operation IDs, merge rules or backend endpoints. If these recovery paths are absent, report the concrete gap; a cosmetic change cannot silently replace the protocol or claim recoverability.

Intended verification: compare category values and serialized payload with the actual API contract; use existing contract/state tests or an isolated existing-handler fixture to exercise confirmed success, 409 draft retention and timeout-after-commit without a second write. Inspect selector/focus/error styles and calculate actual color pairs. Rerun the project's type check/build after the proposed changes and relevant existing lint/tests. Provide a local diff/artifact with the unchanged payload and states reviewable.

Evidence available: type check and build **passed (scenario-supplied; no commands, commit or environment supplied)**. This does not establish any proposed edit is valid. Fresh checks, runtime contract/state checks and contrast calculations: **not-run**. Browser visual, responsive and keyboard validation: **blocked (browser unavailable)**. Live API/persistence verification: **not-run**. No **failed** check is known. Current claim: polish plan prepared; application not modified. An eventual delivery must say which local artifact was produced and which fresh checks passed, and explicitly retain the browser/API limitations; it cannot claim a visually verified or end-to-end complete form based on build/type checks.
