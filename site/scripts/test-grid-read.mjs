// Energy Research Warehouse (ERW) site, session 7565: the Grid tool read as an AI lab's energy lead would read it
// (docs/reviews/grid-read-2026-11-16.md, rows 1 and 2). /grid drawn whole by its own function on the live set's public
// reads (the anon key only), PJM's Clean and Mix tabs, then the words checked. Needs SUPABASE_URL and SUPABASE_ANON_KEY
// in the environment (the public reads the site itself makes); exits 2 without them.
//   cd site && node --import ./scripts/grid-read-register.mjs scripts/test-grid-read.mjs
import { renderToReadableStream } from "react-dom/server.edge";

if (!process.env.SUPABASE_URL || !process.env.SUPABASE_ANON_KEY) { console.log("SUPABASE_URL and SUPABASE_ANON_KEY are needed"); process.exit(2); }
delete process.env.SUPABASE_SERVICE_KEY;   // a visitor's reads only

const { default: GridPage } = await import("../app/grid/page.tsx");
const { CARBON_WINDOW_WORDS, DAILY_TABLE_TIP } = await import("../lib/gridwords.ts");
const draw = async (grid, view) => {
  const stream = await renderToReadableStream(await GridPage({ searchParams: Promise.resolve({ grid, view }) }));
  await stream.allReady;
  return (await new Response(stream).text()).replace(/&#x27;|&apos;/g, "'");
};

let failed = 0;
const check = (ok, what) => { console.log(`${ok ? "ok  " : "FAIL"} ${what}`); if (!ok) failed++; };

const clean = await draw("pjm", "clean");
check(!clean.includes("Not in the warehouse yet:</span> PJM's carbon intensity"), "PJM's Clean tab no longer says its carbon intensity is not in the warehouse");
const ranked = /PJM[\s\S]{0,400}?kg CO2\/MWh|data-check="series\|carbon_intensity_hourly\|eia930:PJM/.test(clean);
const empty = clean.includes('data-carbon-window-empty="1"');
check(!empty || clean.includes(CARBON_WINDOW_WORDS("PJM").slice(0, 60)), `when the four-day window is empty the block says the table holds older hours (window empty: ${empty})`);
check(ranked, "the tab still ranks PJM by carbon intensity from the same table");

const mix = await draw("pjm", "mix");
check(!mix.includes("the latest EIA has published") && mix.includes('data-latest-held="1"'), "the Mix lead says the latest hour the warehouse's daily table holds, not EIA's latest");
check(mix.includes(DAILY_TABLE_TIP.slice(0, 50)), "with a tip saying the table loads once a day and the Network tab holds newer hours");
check(!mix.includes("Demand in the latest hour EIA has published") && mix.includes("a day or more behind EIA"), "the demand block's label and note say the same");

console.log(failed ? `${failed} failed` : "all passed");
process.exitCode = failed ? 1 : 0;
