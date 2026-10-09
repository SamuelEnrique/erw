// Energy Research Warehouse (ERW) site, session 166 (part F): the datacenter tracker's accuracy, on the built site.
//
//   npm run build && npx next start -p 3166
//   node scripts/check-datacenters.mjs [base-url]      (default http://localhost:3166)
//
// As HTML, in the internal view (both pages are in review):
//   /datacenters     opens 200; the Status column and filter hold cleaned status words only (never a source's raw
//                    field such as "inDevelopment"); the summary strip states the rows held and the rows counted (in a
//                    named US state and not cancelled), and the counted number is below the rows held; a row without
//                    a US state reads "country not stated" with its reason on hover; the Firmus rows are in the table,
//                    and no bar names Firmus (its cancelled 1,600 MW leaves the totals)
//   /datacenters/v2  opens 200; its sentence states the sites held, the sites in a named US state and the sites with
//                    no US state stated, and the three add up
//   visitor          without the cookie each page is the in-review page
// No browser. Exit 1 on a failure.
import { env } from "./browser.mjs";

const base = (process.argv[2] ?? "http://localhost:3166").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(env("INTERNAL_COSTS_TOKEN") ?? "")}`, { redirect: "manual" });
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
  const barsHtml = p.html.slice(p.html.indexOf('aria-label="Summary"'), p.html.indexOf('aria-label="Facilities"'));
  check(firmusRows.length >= 1 && firmusRows.every((r) => /data-no-country="1"/.test(r)) && !/Firmus/.test(barsHtml), `Firmus's ${firmusRows.length} rows stay in the table without a country, and no bar names Firmus`);
  check(/Stated MW by state[^<]*US rows not cancelled/.test(text) && /Top operators by MW \(US rows not cancelled\)/.test(text), "the two bars say they count US rows not cancelled");
  const v = await get("/datacenters", false);
  check(!v.html.includes('aria-label="Summary"') && /in review/i.test(plain(v.html)), "without the cookie a visitor gets the in-review page");
}
{
  const p = await get("/datacenters/v2");
  const text = plain(p.html);
  const m = /The ERW holds ([\d,]+) datacenter sites: ([\d,]+) in a named US state, ([\d,]+) of those in Texas, and ([\d,]+) with no US state stated, sites outside the US among them\./.exec(text);
  const k = (s) => Number(s.replace(/,/g, ""));
  check(p.status === 200 && !!m && k(m[2]) + k(m[4]) === k(m[1]) && k(m[3]) <= k(m[2]), m ? `/datacenters/v2: ${m[1]} sites, ${m[2]} in a named US state (${m[3]} in Texas), ${m[4]} with no US state stated; they add up` : "/datacenters/v2 states the sites held, in a named US state and with no US state stated");
  check(/title="No source the ERW reads states a country/.test(p.html), "the reason stands on hover");
  const v = await get("/datacenters/v2", false);
  check(!v.html.includes('data-facilities-summary="1"') && /in review/i.test(plain(v.html)), "without the cookie a visitor gets the in-review page");
}
console.log(bad ? `${bad} of ${n} failed` : `all ${n} passed`);
process.exit(bad ? 1 : 0);
