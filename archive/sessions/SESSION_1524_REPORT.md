# Session 1524 report: AccessLint on the pages session 1504 did not read

Energy Research Warehouse (ERW), session 1524, chain 163, samueloldlaptop, 6 November 2026, 12:56 to 13:05 UTC. Model: Claude Opus 5.5. Model spend USD 0. No warehouse data written; nothing sent or posted. Run on session 1523's kept gate build (`erw-land-9cb66ff6`, port 3523), in the internal view: the token was posted to the form at `/internal/open` by `runs/s1504/unlock9222.mjs`, never put in an address.

## What it did

- **Chain 158's second unfinished step.** Session 1504 ran AccessLint (`audit_live`) on ten pages. This session read the rest of the snapshot's addresses, and the three explorers at a phone's width.
  - **At 1280, eleven pages, no violation.** They are `/about`, `/terms`, `/network`, `/storage`, the four methods pages (`battery_stack`, `cost_of_power`, `grid_network`, `storage`), the generator's California solar and wind, and the battery for California at 4 hours. The battery's other snapshot addresses are the same page with other inputs, and the generator's default and `/` were read by session 1504.
  - **At 390, the three explorers, no violation.** `/explore/ercot-peak-premium`, `/explore/demand-growth` and `/explore/interconnection` were each held at 390 by 844 by `Emulation.setDeviceMetricsOverride` (`runs/s1524/phone_tabs.mjs`; a headless window alone stays near 480). Each read an inner and scroll width of 390, so none overflows. AccessLint reused the held tabs.
  - **A check that the pages were the real ones**: each tab showed its own title and the "internal" mark (for example "The grid: US48, Network | ERW", 7,533 characters of text), not the in-review page.
- **One finding, on an internal page**: `/internal/open`, the token form, is critical under `input-assistance/accessible-authentication` (WCAG 2.2, 3.3.8). The rule says the password field's `autocomplete="off"` blocks password managers. Visitors never see the page; it is the owner's way into the internal view.

## Decisions made without you

- The form's `autocomplete="off"` is not changed. Whether a password manager should keep the internal token is a security choice, not a fault this chain fixes. It is in the next file's open faults and below.

## For Samuel's ruling

- `/internal/open`: allow password managers (`autocomplete="current-password"`, which AccessLint asks for) or keep `off` (the token is not then stored by a browser). Recommendation: allow it. A manager-held token is safer than one pasted from a file, and the form posts it in the body either way.
