// Energy Research Warehouse (ERW) site, session 7560: the datacenter tracker read as an AI lab's energy lead would
// read it (docs/reviews/datacenters-read-2026-11-16.md). The facilities table drawn to HTML by its own component on
// three of the table's own rows as the live set served them on 17 November 2026 (no row of a held field: operator
// names, places and statuses only, which the page prints). Rows 2 and 3 of the read.
//   cd site && node --import ./scripts/tsx-register.mjs scripts/test-datacenters-read.mjs
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const { DatacentersTable, QUEUE_STATUS, NO_GRID } = await import("../app/datacenters/DatacentersTable.tsx");

let failed = 0;
const check = (ok, what) => { console.log(`${ok ? "ok  " : "FAIL"} ${what}`); if (!ok) failed++; };

const base = {
  operator: "", developer: "", site: "", state: "", county: "", city: "", country: "US", mw: null, phase: "", status: "",
  plannedYear: "", power: "", utility: "", confidence: null, placed: false, firstStory: "", storyUrls: [], kind: "queue",
  kinds: ["queue"], siteType: "", mwSpan: "", queueMw: null, sourceUrls: [], siting: null, grid: "", gridBasis: "",
  mwBasis: "", powerKind: "", energizedYear: "", utilityEia: "", utilitiesInCounty: "",
};
const rows = [
  // ercot:interconnection_queue, the two rows whose status is the queue's own (17 November 2026)
  { ...base, id: "q1", site: "Giga Texas Data Center", state: "TX", status: "completed", grid: "ERCOT", gridBasis: "queue" },
  { ...base, id: "q2", site: "Alpha Digital Campus Combined-cycle and Co-located Load", state: "TX", status: "active", grid: "ERCOT", gridBasis: "queue" },
  // digitalrealty:data-centers, Phoenix: Arizona has no ISO
  { ...base, id: "o1", operator: "Digital Realty", site: "PHX10", city: "Phoenix", state: "AZ", kind: "operator", kinds: ["operator"] },
  // a row with no US state stated: no grid line at all (it reads "country not stated")
  { ...base, id: "n1", operator: "Polar DC", site: "Tordal campus", country: "", kind: "news", kinds: ["news"], mw: 40 },
];
const html = renderToStaticMarkup(h(DatacentersTable, { rows }));

check(html.includes(">queue: completed<") && !/>completed</.test(html), "ERCOT's Completed reads 'queue: completed', never a bare 'completed'");
check(html.includes(">queue: active<") && !/>active</.test(html), "a queue's Active reads 'queue: active', never a bare 'active'");
check(html.includes(`title="${QUEUE_STATUS.completed.tip.replace(/'/g, "&#x27;")}"`), "the completed status carries its tip: a signed agreement, built or not");
check(html.includes('data-facility-grid="none"') && html.includes(`>${NO_GRID.text}<`), "Phoenix's row says no ISO is set, not a blank");
check((html.match(/data-facility-grid="none"/g) ?? []).length === 1, "a row with no US state carries no grid line (one 'no ISO set' of four rows)");
check(html.includes('data-facility-grid="ERCOT"'), "a queue row keeps its grid");
check(html.includes('<option value="completed">queue: completed</option>'), "the Status filter names the queue's statuses the same way");
const withScore = renderToStaticMarkup(h(DatacentersTable, { rows: [{ ...rows[3], confidence: 0.7 }] }));
check(withScore.includes('data-confidence="1"') && withScore.includes("does not say how likely the facility is to be built"), "'model confidence 0.7' says on hover what it scores (row 9)");

console.log(failed ? `${failed} failed` : "all passed");
process.exitCode = failed ? 1 : 0;
