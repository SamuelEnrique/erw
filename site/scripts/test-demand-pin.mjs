// Energy Research Warehouse (ERW) site, session 8420 (chain 503, part C): the pin that holds "add, never change" for
// /demand. Every address the page answered before the session (scripts/demand-pages.mjs, ADDRESSES: each of the eight
// areas under each ranking, the weather view at each figure and year, the consumption view on made-up rows, and the
// addresses the page does not understand) is drawn to HTML with the page's own function, what the session added is cut
// out (the tab of the new view), and what is left must be, byte for byte, the page as it was drawn from the branch's
// base before the session (the pin file: a hash of each address's HTML, its length and its count of checked figures).
// Line ends are read as LF before the hash, so a checkout that converts them draws the same pin.
//
//   node --import ./scripts/battery-awards-page-register.mjs scripts/test-demand-pin.mjs            compare with the pin
//   node --import ./scripts/battery-awards-page-register.mjs scripts/test-demand-pin.mjs --write    write the pin (once, before a change)
//
// A hash is not a figure, and /demand draws no held figure (EIA Form EIA-930 and NOAA are public), so there is one mode.
import crypto from "node:crypto";
import fs from "node:fs";
import { ADDRESSES, drawDemand, figuresOf, withoutAdded } from "./demand-pages.mjs";

const here = (p) => new URL(p, import.meta.url);
const PIN = here("./pins/demand-page-8420.json");

const now = {};
for (const [name, query] of ADDRESSES) {
  const kept = withoutAdded(await drawDemand(query)).replace(/\r\n/g, "\n");
  now[name] = { query: new URLSearchParams(query).toString(), sha256: crypto.createHash("sha256").update(kept).digest("hex"), bytes: kept.length, figures: figuresOf(kept) };
}

if (process.argv.includes("--write")) {
  if (fs.existsSync(PIN) && !process.argv.includes("--again")) {
    console.log("the pin is already written; it is written once, from unchanged code (pass --again to write it over, and say why in the report)");
    process.exitCode = 2;
  } else {
    const pin = {
      what: "The addresses of /demand as drawn from the branch's base before session 8420 (chain 503, part C), by scripts/test-demand-pin.mjs: a hash of each address's HTML (line ends as LF), its length and its count of checked figures. The consumption view is drawn on made-up rows (scripts/demand-pages.mjs), so its hash holds the page's code, not a table.",
      from_commit: process.env.PIN_COMMIT ?? "",
      addresses: now,
    };
    fs.mkdirSync(here("./pins/"), { recursive: true });
    fs.writeFileSync(PIN, JSON.stringify(pin, null, 1) + "\n");
    console.log(`wrote the pin of ${Object.keys(now).length} addresses`);
  }
} else {
  const pin = JSON.parse(fs.readFileSync(PIN, "utf-8")).addresses;
  let n = 0, failed = 0;
  const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
  ok(!!pin && Object.keys(pin).length === ADDRESSES.length && ADDRESSES.every(([k]) => k in pin), `the pin holds the ${ADDRESSES.length} addresses`);
  for (const [name] of ADDRESSES) {
    const a = now[name], b = pin?.[name] ?? {};
    ok(a.figures === b.figures, `${name}: ${a.figures} checked figures, as before (${b.figures})`);
    ok(a.sha256 === b.sha256, `${name}: outside what was added, the page is as it was, byte for byte (${a.bytes} of ${b.bytes} bytes)`);
  }
  console.log(`${n - failed} of ${n} passed`);
  if (failed) process.exitCode = 1;
}
