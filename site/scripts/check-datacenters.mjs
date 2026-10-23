// Energy Research Warehouse (ERW) site, session 166 (part F): the datacenter tracker's accuracy, on the built site.
//
//   npm run build && npx next start -p 3166
//   node scripts/check-datacenters.mjs [base-url]      (default http://localhost:3166)
//
// Session 241: one tracker. /datacenters draws what /datacenters/v2 drew (app/datacenters/LargeLoad.tsx) and the old
// address redirects to it, so every assertion that read /datacenters/v2 reads /datacenters now, and three are new: the
// redirect itself, with a query carried; ERCOT's section with its three figures; the figures' check keys.
//
// As HTML, in the internal view (the page is in review):
//   /datacenters     opens 200; the Status column and filter hold cleaned status words only (never a source's raw
//                    field such as "inDevelopment"); the summary strip states the rows held and the rows counted (in a
//                    named US state and not cancelled), and the counted number is below the rows held; a row without
//                    a US state reads "country not stated" with its reason on hover; the Firmus rows are in the table,
//                    and no bar names Firmus (its cancelled 1,600 MW leaves the totals)
//   /datacenters     also (it was /datacenters/v2): its sentence states the sites held, the sites in a named US state
//                    and the sites with no US state stated, and the three add up; ERCOT's large-load section stands
//                    above it with its three figures, each with a check key
//   /datacenters/v2  answers 308 to /datacenters, a query carried
//   visitor          without the cookie each page is the in-review page
// No browser. Exit 1 on a failure.
import { env, unlockPost } from "./browser.mjs";

const base = (process.argv[2] ?? "http://localhost:3166").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const unlock = await unlockPost(base, env("INTERNAL_COSTS_TOKEN") ?? "");
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exit(1); }
const get = async (path, withCookie = true) => { const r = await fetch(base + path, { headers: withCookie ? { Cookie: cookie } : {} }); return { status: r.status, html: await r.text() }; };
const decode = (t) => t.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&");
const plain = (html) => decode(html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ");
const num = (html, k) => { const m = new RegExp(`data-check="datacenters\\|${k}"[^>]*data-raw="([^"]*)"`).exec(html) ?? new RegExp(`data-raw="([^"]*)"[^>]*data-check="datacenters\\|${k}"`).exec(html); return m ? Number(m[1]) : null; };
const VOCAB = new Set(["planned", "under construction", "operating", "withdrawn", "completed", "active", "not stated"]);

{
  const p = await get("/datacenters");
  const text = plain(p.html);
  check(p.status === 200 && text.includes("Datacenter power tracker") && !/\bundefined\b|NaN/.test(text), "/datacenters opens, with no \"undefined\" and no NaN");
  // the Status filter's options, and every Status cell of the table
  const sel = /<label[^>]*>\s*Status\s*<select[\s\S]*?<\/select>/.exec(p.html)?.[0] ?? "";
  const options = [...sel.matchAll(/<option[^>]*>([^<]*)<\/option>/g)].map((m) => decode(m[1]).trim()).filter((o) => o !== "All");
  check(options.length > 0 && options.every((o) => VOCAB.has(o)) && !/inDevelopment/.test(p.html), `the Status filter offers cleaned words only: ${options.join(", ")}`);
  const rows = [...p.html.matchAll(/<tr class="border-b border-rule align-top">([\s\S]*?)<\/tr>/g)].map((m) => m[1]);
  const statusCells = rows.map((r) => decode((r.split(/<\/td>/)[4] ?? "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim());
  check(rows.length > 300 && statusCells.every((s) => VOCAB.has(s)), `every Status cell of the ${rows.length} rows is a cleaned word (${[...new Set(statusCells)].join(", ")})`);
  const held = num(p.html, "count"), counted = num(p.html, "counted"), noUs = num(p.html, "no_us_state"), cancelled = num(p.html, "cancelled");
  check(held !== null && counted !== null && noUs !== null && cancelled !== null && counted + noUs + cancelled === held && counted < held,
    `the summary: ${held} held, ${counted} in a named US state and not cancelled, ${noUs} with no US state stated, ${cancelled} cancelled (they add up)`);
  const noCountry = (p.html.match(/data-no-country="1"/g) ?? []).length;
  check(noCountry === noUs && /title="No source the ERW reads states a country/.test(p.html), `${noCountry} rows read "country not stated", with the reason on hover, as many as the summary says`);
  const firmusRows = rows.filter((r) => /Firmus/.test(r));
  // the bars' own items (the strip's hover names Firmus as an example, and that is not a bar)
  // session 241: the summary ends where ERCOT's section begins (its list of notes is not a bar)
  const barsHtml = p.html.slice(p.html.indexOf('aria-label="Summary"'), p.html.indexOf('data-large-load="1"'));
  const barItems = [...barsHtml.matchAll(/<li[^>]*>([\s\S]*?)<\/li>/g)].map((m) => plain(m[1]));
  check(firmusRows.length >= 1 && firmusRows.every((r) => /data-no-country="1"/.test(r)) && barItems.length > 0 && !barItems.some((t) => /Firmus/.test(t)),
    `Firmus's ${firmusRows.length} rows stay in the table without a country, and none of the ${barItems.length} bars names Firmus`);
  check(/Stated MW by state[^<]*US rows not cancelled/.test(text) && /Top operators by MW \(US rows not cancelled\)/.test(text), "the two bars say they count US rows not cancelled");
  // session 2301 (chain 087): every bar's figure has a hover card (a focusable trigger and its tooltip, naming the facilities counted and the source), and the fold under the bars holds the same figures as a table
  const tips = [...barsHtml.matchAll(/data-bar-tip="([^"]+)"[\s\S]*?<button[^>]*data-tip-trigger[^>]*aria-describedby="([^"]+)"[\s\S]*?role="tooltip" id="([^"]+)"[^>]*>([\s\S]*?)<\/span>\s*<\/span>\s*<\/li>/g)].map((m) => ({ bar: m[1], by: m[2], id: m[3], words: plain(m[4]) }));
  const barCount = (barsHtml.match(/data-bar-tip="/g) ?? []).length;
  check(barCount > 0 && tips.length === barCount && tips.every((t) => t.by === t.id && /MW, \d[\d,]* (facility|facilities)/.test(t.words) && /datacenter_facilities/.test(t.words)),
    `each of the ${barCount} bars has a hover card its figure describes, naming the facilities counted and datacenter_facilities (${tips.length} read)`);
  const barRows = (p.html.match(/data-bar-row="/g) ?? []).length;
  check(p.html.includes('data-bars-table="1"') && barRows === barCount && /The bars&#x27; figures|The bars' figures/.test(p.html), `the fold under the bars holds the same ${barCount} figures as a table (${barRows} rows)`);
  check(p.html.includes('data-tip="bars-state"') && p.html.includes('data-tip="bars-operator"') && p.html.includes('data-tip="power-mw"'), "the source tips stand by the two bars and the power side's MW column");
  check(p.html.includes('data-series-chart="large-load"') && /data-source="ercot_large_load_status\|/.test(p.html), "ERCOT's large-load figures are drawn by the shared chart, framed with their source");
  // session 2302 (chain 087): the ERCOT positions whose operator alone names a data center (Bullock Gas, Liberty Thermal
  // Energy Center: docs/reviews/datacenters-power-side-2026-10-23.md) are on the power side when the live set holds them,
  // read here from the live set itself with the page's own pattern; when it does not, the check says so and passes
  {
    const url = (env("SUPABASE_URL") ?? "").replace(/\/+$/, ""), key = env("SUPABASE_ANON_KEY") ?? "";
    let live = null;
    if (url && key) {
      try {
        const r = await fetch(`${url}/rest/v1/entities?table_name=eq.ercot_interconnection_queue&operator=imatch.data%20%3Fcent(%3F%3Aer%7Cre)s%3F%7Cdatacenter&select=entity_id,operator`, { headers: { apikey: key, Authorization: `Bearer ${key}` } });
        if (r.ok) live = await r.json();
      } catch { live = null; }
    }
    if (live === null) console.log("skip the operator-named positions: the live set could not be read here (SUPABASE_URL and SUPABASE_ANON_KEY)");
    else if (!live.length) console.log("skip the operator-named positions: the live set's ERCOT queue holds no position whose operator names a data center");
    else {
      const shown = live.filter((x) => new RegExp(`data-power-site="${x.entity_id.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}"[^>]*data-matched-by="operator"`).test(p.html));
      check(shown.length === live.length, `the ${live.length} ERCOT positions named a data center by their operator alone are on the power side, marked so (${shown.length} shown: ${live.map((x) => x.entity_id).join(", ")})`);
      check(/named a data center by its operator&#x27;s name|named a data center by its operator's name/.test(p.html), "a row named by its operator says so under its name");
    }
  }
  const v = await get("/datacenters", false);
  check(!v.html.includes('aria-label="Summary"') && /in review/i.test(plain(v.html)), "without the cookie a visitor gets the in-review page");
}
{
  const p = await get("/datacenters");   // session 241: the sentence is on the one page
  const text = plain(p.html);
  const m = /The ERW holds ([\d,]+) datacenter sites: ([\d,]+) in a named US state, ([\d,]+) of those in Texas, and ([\d,]+) with no US state stated, sites outside the US among them\s*\./.exec(text);
  const k = (s) => Number(s.replace(/,/g, ""));
  check(p.status === 200 && !!m && k(m[2]) + k(m[4]) === k(m[1]) && k(m[3]) <= k(m[2]), m ? `/datacenters, the Texas section: ${m[1]} sites, ${m[2]} in a named US state (${m[3]} in Texas), ${m[4]} with no US state stated; they add up` : `/datacenters states the sites held, in a named US state and with no US state stated (the page says: "${(/The ERW holds[^.]{0,200}/.exec(text) ?? [""])[0]}")`);
  const para = (/data-facilities-summary="1"[\s\S]*?<\/p>/.exec(p.html) ?? [""])[0];
  check(/title="No source the ERW reads states a country\. A site with no US state stated/.test(para), "the reason stands on hover, in the sentence itself");
  // ERCOT's section: the summary sentence, the three figures of the newest report, each with its check key, and the chart and table's titles
  const figures = ["approved", "nonsimultaneous", "simultaneous"].map((k) => new RegExp(`data-load="${k}"[^>]*>\\s*<span[^>]*data-check="series\\|ercot_large_load_status\\|ercot:large_load\\|[a-z_]+_mw\\|\\d{4}-\\d{2}-\\d{2}T00:00:00Z"`).test(p.html));
  check(p.html.includes('data-load-summary="1"') && figures.every(Boolean) && text.includes("ERCOT: large load approved and energized, over time") && text.includes("Beside it: the facilities the ERW holds") && text.includes("A request is not a built facility"),
    `ERCOT's large-load section stands on /datacenters: its sentence, its three figures with their check keys (${figures.filter(Boolean).length} of 3), and the words "A request is not a built facility"`);
  const rowsKeyed = (p.html.match(/data-load-row="\d{4}-\d{2}-\d{2}\|approved"/g) ?? []).length;
  check(rowsKeyed >= 9, `the table by report holds ${rowsKeyed} reports`);
  const v = await get("/datacenters", false);
  check(!v.html.includes('data-facilities-summary="1"') && !v.html.includes('data-large-load="1"') && /in review/i.test(plain(v.html)), "without the cookie a visitor gets the in-review page, and neither section");
  // the old address: a permanent redirect to the one page, with and without a query, for a visitor and for the internal view alike
  for (const [path, to] of [["/datacenters/v2", "/datacenters"], ["/datacenters/v2?state=TX", "/datacenters?state=TX"]]) {
    const r = await fetch(base + path, { redirect: "manual" });
    const where = (r.headers.get("location") ?? "").replace(/^https?:\/\/[^/]+/, "");
    check(r.status === 308 && where === to, `${path} answers ${r.status} to ${where || "nothing"} (asked: 308 to ${to})`);
  }
}
console.log(bad ? `${bad} of ${n} failed` : `all ${n} passed`);
process.exit(bad ? 1 : 0);
