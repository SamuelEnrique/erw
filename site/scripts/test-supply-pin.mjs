// Energy Research Warehouse (ERW) site, session 8430 (chain 503, part D): the pin that holds "add, never change" for
// /supply. The whole page is drawn to HTML by its own function (scripts/supply-read-page.mjs, session 7541) at every
// address it answered before the session: the page with nothing chosen, each group alone, two groups together, every
// series with its seasonal chart open, a chart open inside one group, and an address that names nothing the file holds.
// What session 8430 added is cut out (the section "The whole country", inside its marks: scripts/supply-added.mjs), and
// what is left must be, byte for byte, the page as the code drew it before the session (the pin file's hash of each
// address, its length and its count of checked figures).
//
//   node --import ./scripts/supply-pin-register.mjs scripts/test-supply-pin.mjs            compare with the pin
//   node --import ./scripts/supply-pin-register.mjs scripts/test-supply-pin.mjs --write    write the pin (once, before a change)
//
// The page is drawn on a copy of its two input files kept beside the pin (scripts/pins/supply-page-8430-input.json,
// served by scripts/supply-pin-loader.mjs), with the clock standing at the pin's own time and the page's one read of
// the live set answered by a stand-in, so the pin holds the code and not the week's data: a rebuild of data/supply.json
// does not move it. A hash is not a figure. No network, nothing written but the pin on --write.
import crypto from "node:crypto";
import fs from "node:fs";
import { figureCount, fixClock, standInCatalogue, withoutSupplyAdded } from "./supply-added.mjs";

const here = (p) => new URL(p, import.meta.url);
const PIN = here("./pins/supply-page-8430.json");
const INPUT = here("./pins/supply-page-8430-input.json");
const CLOCK = "2026-11-19T12:00:00Z";
const UNREAD = "~catalogue-unread";
const write = process.argv.includes("--write");

if (write && fs.existsSync(PIN)) {
  console.error("the pin is already written (scripts/pins/supply-page-8430.json): it is written once, from the code before the session's change");
  process.exit(2);
}
if (write && !fs.existsSync(INPUT)) {
  // the copy of the two input files, taken before the page is first imported, so this same run draws from it
  fs.mkdirSync(here("./pins/"), { recursive: true });
  fs.writeFileSync(INPUT, JSON.stringify({
    what: "A copy of site/data/supply.json and site/data/license_status.json (both public files of this repository) as they stood when the pin of /supply was written (scripts/test-supply-pin.mjs, session 8430, chain 503). Read only by scripts/supply-pin-loader.mjs, so the pin holds the page's code and not the week's data. Never read by the site.",
    from_commit: process.env.PIN_COMMIT ?? "",
    supply: JSON.parse(fs.readFileSync(here("../data/supply.json"), "utf-8")),
    license_status: JSON.parse(fs.readFileSync(here("../data/license_status.json"), "utf-8")),
  }) + "\n");
  console.log("wrote the copy of the page's two input files");
}

/** Every address the page answered before the session, from the file the pin is drawn on. */
function addresses(file) {
  const ok = file.rows.filter((r) => r.status === "ok").map((r) => r.id);
  const groups = file.groups.map((g) => g.id);
  const burn = file.rows.find((r) => r.group === "burn" && r.status === "ok");
  return [
    "",
    ...groups.map((g) => `g=${g}`),
    `g=${groups[0]},${groups[groups.length - 1]}`,
    ...ok.map((id) => `s=${id}`),
    ...(burn ? [`g=burn&s=${burn.id}`] : []),
    "s=cleared-miso&g=nowhere",
  ];
}

const pinned = write ? null : JSON.parse(fs.readFileSync(PIN, "utf-8"));
const clock = pinned?.clock ?? CLOCK;
const list = pinned ? Object.keys(pinned.addresses) : [...addresses(JSON.parse(fs.readFileSync(INPUT, "utf-8")).supply), UNREAD];

const undoClock = fixClock(clock);
const { drawSupply } = await import("./supply-read-page.mjs");
const log = console.error;
console.error = () => {};  // the page's own line about a read that was not made is not wanted here
const now = {};
try {
  for (const address of list) {
    const undo = standInCatalogue(address !== UNREAD);
    try {
      const kept = withoutSupplyAdded(await drawSupply(address === UNREAD ? "" : address));
      now[address] = { sha256: crypto.createHash("sha256").update(kept).digest("hex"), bytes: kept.length, figures: figureCount(kept) };
    } finally { undo(); }
  }
} finally { console.error = log; undoClock(); }

if (write) {
  fs.writeFileSync(PIN, JSON.stringify({
    what: "The page /supply as its code drew it before session 8430 (chain 503, part D), by scripts/test-supply-pin.mjs: for each address, a hash of the page's HTML, its length and its count of checked figures, drawn on the copy of its input files in supply-page-8430-input.json with the clock at `clock` and the catalogue read answered by a stand-in (the last address: not read).",
    from_commit: process.env.PIN_COMMIT ?? "", clock, addresses: now,
  }, null, 1) + "\n");
  console.log(`wrote the pin of ${list.length} addresses`);
} else {
  let n = 0, failed = 0;
  const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
  ok(list.length >= 100 && list.includes("") && list.includes(UNREAD), `the pin holds ${list.length} addresses of /supply, the whole page and the catalogue not read among them`);
  ok(fs.existsSync(INPUT), "the copy of the page's input files stands beside the pin");
  for (const address of list) {
    const a = now[address], b = pinned.addresses[address];
    const name = address === "" ? "/supply" : address === UNREAD ? "/supply (catalogue not read)" : `/supply?${address}`;
    ok(a.figures === b.figures, `${name}: ${a.figures} checked figures, as before (${b.figures})`);
    ok(a.sha256 === b.sha256, `${name}: outside what was added, the page is as it was, byte for byte (${a.bytes} of ${b.bytes} bytes)`);
  }
  console.log(`${n - failed} of ${n} passed`);
  if (failed) process.exitCode = 1;
}
