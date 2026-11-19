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
//   ... --pin <file>          read or write another pin file (to hold a landing: write one from main's own checkout with
//                             these two scripts copied in, then compare the merged branch against it)
//   ... --stamp-data          add the data files' hashes to a pin that has none, only while every address still matches
//
// A page's HTML is its code and its data. The pin keeps the sha256 of each data file the page reads as a module
// (demand-pages.mjs, dataFilesOf). While those are what they were, a page that differs is a failure. Once the data
// machine rebuilds one of them, a page that differs can no longer be told from a page that moved with its data: the
// test then says DATA MOVED, names the files, fails nothing, and the Python test that runs it is skipped with those
// words. A page that still matches is counted as held either way.
//
// A hash is not a figure, and /demand draws no held figure (EIA Form EIA-930 and NOAA are public), so there is one mode.
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { ADDRESSES, dataFilesOf, drawDemand, figuresOf, withoutAdded } from "./demand-pages.mjs";

const here = (p) => new URL(p, import.meta.url);
const arg = (name) => { const i = process.argv.indexOf(name); return i > 0 ? process.argv[i + 1] : null; };
const PIN = arg("--pin") ? pathToFileURL(path.resolve(arg("--pin"))) : here("./pins/demand-page-8420.json");

// --only a,b draws those addresses alone (for the Python test's two checks of this script's own rules; never with --write)
const only = arg("--only")?.split(",") ?? null;
const DRAWN = only ? ADDRESSES.filter(([k]) => only.includes(k)) : ADDRESSES;
if (only && (process.argv.includes("--write") || process.argv.includes("--stamp-data") || !DRAWN.length)) { console.log("--only is for a comparison, and names addresses of the pin"); process.exit(2); }

const now = {};
for (const [name, query] of DRAWN) {
  const kept = withoutAdded(await drawDemand(query)).replace(/\r\n/g, "\n");
  now[name] = { query: new URLSearchParams(query).toString(), sha256: crypto.createHash("sha256").update(kept).digest("hex"), bytes: kept.length, figures: figuresOf(kept) };
}
const data = dataFilesOf();

if (process.argv.includes("--write")) {
  if (fs.existsSync(PIN) && !process.argv.includes("--again")) {
    console.log("the pin is already written; it is written once, from unchanged code (pass --again to write it over, and say why in the report)");
    process.exitCode = 2;
  } else {
    const pin = {
      what: "The addresses of /demand as drawn from the branch's base before session 8420 (chain 503, part C), by scripts/test-demand-pin.mjs: a hash of each address's HTML (line ends as LF), its length and its count of checked figures; and the sha256 of each data file the page reads, as they were when the pages were drawn. The consumption view is drawn on made-up rows (scripts/demand-pages.mjs), so its hash holds the page's code, not a table.",
      from_commit: process.env.PIN_COMMIT ?? "",
      addresses: now,
      data,
    };
    fs.mkdirSync(new URL("./", PIN), { recursive: true });
    fs.writeFileSync(PIN, JSON.stringify(pin, null, 1) + "\n");
    console.log(`wrote the pin of ${Object.keys(now).length} addresses and ${Object.keys(data).length} data files`);
  }
} else if (process.argv.includes("--stamp-data")) {
  const pin = JSON.parse(fs.readFileSync(PIN, "utf-8"));
  const same = ADDRESSES.every(([k]) => pin.addresses?.[k]?.sha256 === now[k].sha256);
  if (pin.data) { console.log("the pin already holds its data files' hashes"); process.exitCode = 2; }
  else if (!same) { console.log("not stamped: an address no longer matches the pin, so the data here may not be the data the pin was drawn on"); process.exitCode = 1; }
  else {
    pin.what = "The addresses of /demand as drawn from the branch's base before session 8420 (chain 503, part C), by scripts/test-demand-pin.mjs: a hash of each address's HTML (line ends as LF), its length and its count of checked figures; and the sha256 of each data file the page reads, as they were when the pages were drawn (added while every address still matched). The consumption view is drawn on made-up rows (scripts/demand-pages.mjs), so its hash holds the page's code, not a table.";
    pin.data = data;
    fs.writeFileSync(PIN, JSON.stringify(pin, null, 1) + "\n");
    console.log(`stamped the pin with ${Object.keys(data).length} data files, every address still matching`);
  }
} else {
  const file = JSON.parse(fs.readFileSync(PIN, "utf-8"));
  const pin = file.addresses;
  const moved = Object.keys(file.data ?? {}).filter((k) => data[k] !== file.data[k]);
  let n = 0, failed = 0, unheld = 0;
  const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
  ok(!!pin && Object.keys(pin).length === ADDRESSES.length && ADDRESSES.every(([k]) => k in pin), `the pin holds the ${ADDRESSES.length} addresses`);
  for (const [name] of DRAWN) {
    const a = now[name], b = pin?.[name] ?? {};
    if (moved.length && a.sha256 !== b.sha256) { unheld++; console.log(`skip ${name}: the page differs and its data moved since the pin (${a.bytes} of ${b.bytes} bytes, ${a.figures} of ${b.figures} checked figures)`); continue; }
    ok(a.figures === b.figures, `${name}: ${a.figures} checked figures, as before (${b.figures})`);
    ok(a.sha256 === b.sha256, `${name}: outside what was added, the page is as it was, byte for byte (${a.bytes} of ${b.bytes} bytes)`);
  }
  if (unheld) console.log(`DATA MOVED: ${moved.join(", ")} ${moved.length > 1 ? "are" : "is"} not what the pin was drawn on, and ${unheld} of ${DRAWN.length} addresses differ: they cannot be held to this pin. To hold a landing, write a pin from main's own checkout (--write --pin <file>) and compare the merged branch against it (--pin <file>).`);
  console.log(`${n - failed} of ${n} passed`);
  if (failed) process.exitCode = 1;
}
