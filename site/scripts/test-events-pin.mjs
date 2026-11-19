// Energy Research Warehouse (ERW) site, session 8410 (chain 503, part B): the pin that holds "add, never change" for
// /events and its nine event pages. Each page is drawn to HTML with the site's own code on the public rows kept beside
// the replication (scripts/events-pages.mjs, session 7531), what session 8410 added is cut out (the section "The whole
// country" and the index's line of regions, each inside its own marks), and what is left must be, byte for byte, the
// page as it was drawn from origin/main before the session (the pin file's hash and its count of checked figures).
//
//   node --import ./scripts/events-page-register.mjs scripts/test-events-pin.mjs            compare with the pin
//   node --import ./scripts/events-page-register.mjs scripts/test-events-pin.mjs --write    write the pin (once, before a change)
//
// Run once as a visitor's build draws the pages and once with EVENTS_DRAW_UNHELD=1 (every figure drawn, the held ones
// included): the pin file holds a hash for each. A hash is not a figure, so no held figure is written anywhere.
import crypto from "node:crypto";
import fs from "node:fs";
import { withoutAdded } from "./events-added.mjs";
import { csvRows, drawPage, figuresOf, PAGES } from "./events-pages.mjs";

const here = (p) => new URL(p, import.meta.url);
const PIN = here("./pins/events-pages-8410.json");
const mode = process.env.EVENTS_DRAW_UNHELD === "1" ? "unheld" : "visitor";
const tables = {
  event_window_daily: csvRows(here("../../replication/events/window_rows.csv")),
  caiso_grid_emergencies: csvRows(here("../../replication/events/notice_rows.csv")),
};
const rowsOf = (name) => tables[name] ?? null;


const now = {};
for (const [slug, file] of PAGES) {
  const { html } = await drawPage(file, rowsOf);
  const kept = withoutAdded(html);
  now[slug] = { sha256: crypto.createHash("sha256").update(kept).digest("hex"), bytes: kept.length, figures: figuresOf(kept).length };
}

if (process.argv.includes("--write")) {
  const pin = fs.existsSync(PIN) ? JSON.parse(fs.readFileSync(PIN, "utf-8")) : { what: "The ten /events pages as drawn from origin/main before session 8410 (chain 503), by scripts/test-events-pin.mjs: a hash of each page's HTML, its length and its count of checked figures, as a visitor's build draws it and with the hold stood aside.", from_commit: process.env.PIN_COMMIT ?? "", modes: {} };
  pin.modes[mode] = now;
  fs.mkdirSync(here("./pins/"), { recursive: true });
  fs.writeFileSync(PIN, JSON.stringify(pin, null, 1) + "\n");
  console.log(`wrote the ${mode} pin of ${Object.keys(now).length} pages`);
} else {
  const pin = JSON.parse(fs.readFileSync(PIN, "utf-8")).modes[mode];
  let n = 0, failed = 0;
  const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
  ok(!!pin && Object.keys(pin).length === PAGES.length, `the pin holds the ${PAGES.length} pages, ${mode}`);
  for (const [slug] of PAGES) {
    const a = now[slug], b = pin?.[slug] ?? {};
    ok(a.figures === b.figures, `${slug} (${mode}): ${a.figures} checked figures, as before (${b.figures})`);
    ok(a.sha256 === b.sha256, `${slug} (${mode}): outside what was added, the page is as it was, byte for byte (${a.bytes} of ${b.bytes} bytes)`);
  }
  console.log(`${n - failed} of ${n} passed`);
  if (failed) process.exitCode = 1;
}
