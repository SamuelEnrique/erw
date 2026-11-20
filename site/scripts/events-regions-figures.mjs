// Energy Research Warehouse (ERW) site, session 8440 (chain 503, part E): every figure the section "The whole country"
// and the index's line of regions print, for each event whose file is on the site, written to one JSON file for the
// replication (replication/events/replicate_regions.py), which recomputes each from the file on its own.
//
//   node --import ./scripts/events-page-register.mjs scripts/events-regions-figures.mjs <out.json>
//   node --import ./scripts/events-page-register.mjs scripts/events-regions-figures.mjs --fixture <dir>
//
// The files are read where the site reads them (site/data/regions/events/, or ERW_REGIONS_DIR in a test). With
// --fixture the test's fixture (scripts/regions-fixture.mjs: values made by a rule, not data) is written to
// <dir>/events/elliott_2022.json and nothing is drawn. A held file gives no figure, as the page gives none.
import fs from "node:fs";
import path from "node:path";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { eventFixture } from "./regions-fixture.mjs";

const EVENTS = ["uri_2021", "covid_2020", "caiso_heat_2020", "caiso_heat_2022", "elliott_2022", "ercot_heat_2023", "cold_2025", "east_heat_2025", "cold_2026"];
const args = process.argv.slice(2);
if (args[0] === "--fixture") {
  const dir = args[1];
  fs.mkdirSync(path.join(dir, "events"), { recursive: true });
  fs.writeFileSync(path.join(dir, "events", "elliott_2022.json"), JSON.stringify(eventFixture()));
  console.log(`wrote the fixture to ${path.join(dir, "events", "elliott_2022.json")}`);
} else if (!args[0]) {
  console.error("usage: events-regions-figures.mjs <out.json> | --fixture <dir>");
  process.exitCode = 2;
} else {
  const C = await import("../lib/countryfiles.ts");
  const W = await import("../app/events/WholeCountry.tsx");
  const figs = (html) => Object.fromEntries([...html.matchAll(/<span data-n="([^"]+)">([^<]*)<\/span>/g)].map((m) => [m[1], m[2]]));
  const out = { what: "The figures of the section The whole country and of the index's line of regions, as the site's own code draws them from each event's file.", threshold_pct: C.REACHED_PCT, events: {} };
  for (const event of EVENTS) {
    const file = C.eventRegionsFile(event);
    if (!file) { out.events[event] = { file: false }; continue; }
    const held = W.heldWhy(file);
    const section = renderToStaticMarkup(createElement(W.WholeCountry, { event, path: `/events/${event.replace(/_/g, "-")}`, file, q: {}, first: "CAL", firstWhy: "" }));
    const line = renderToStaticMarkup(createElement(W.RegionsReached, { event }));
    out.events[event] = { file: true, held: !!held, built: file.built ?? "", start: file.start, end: file.end, hours: file.hours, figures: { ...figs(section), ...figs(line) } };
    console.log(`${event}: ${Object.keys(out.events[event].figures).length} figures${held ? " (held)" : ""}`);
  }
  fs.writeFileSync(args[0], JSON.stringify(out, null, 1) + "\n");
  console.log(`wrote ${args[0]}`);
}
