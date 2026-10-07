// Energy Research Warehouse (ERW) site, session 144: the one curtailment page (/curtailment), on the built site.
//
//   npm run build && npx next start -p 3144
//   node scripts/check-curtailment.mjs [base-url]      (default http://localhost:3144)
//
// As HTML, in the internal view (the page is in review). Every number the page marks (data-n) is held to the site's
// own files: data/curtailment_profile.json, data/curtailment/{shares,free_energy,worth,ercot}.json.
//   opens      200, its title, its sections, the Method note's link, no "undefined", no NaN
//   california what /curtailment/v2 showed: a year, a month, a year with no reason, a year with part, months of 2026;
//              the charts by hour, by reason and against the batteries are on the page
//   shares     every month of the table has shares.json's share; the period's share is the file's; all 149 CAISO months
//              and SPP's 97 are in the fold, a month without one is a placeholder with the file's reason on hover;
//              nothing reads "not computable"
//   texas      the days, the whole days' sum and the regions are ercot.json's; a month reads "not held yet" with its
//              reason on hover; every region and year reads "no limit published"; the estimate is named
//   free       for every public grid: each place's counts are the file's, the default place is the one with the most
//              hours, the address /curtailment?grid=<iso>&place=<id>#free-energy opens that place, the two pairs and
//              the gap are the file's, a place not held is a placeholder with the reason on hover, the schematic says so
//   worth      California's value, cheap-hour shares, flat load and battery of 2, 4 and 8 hours are worth.json's; Texas
//              is the hours held and labelled the ERW's estimate; SPP "not held yet" with the file's reason
//   face       one line per grid (FACE), no method or limitation words, no em dash; MISO "paused while terms are
//              reviewed" and PJM "licensed source needed", neither selectable; an address naming one opens the default
//   redirect   /curtailment/v2 answers 308 to /curtailment, its query carried
//   visitor    without the cookie the page is the in-review page and carries no number
// In a real browser: every chart is drawn and answers the mouse with its value and unit (the charts in a fold too); a
// cell of the heatmap says its count; a tile of the schematic opens its place.
// Exit 1 on a failure.
import fs from "node:fs";
import { env, withBrowser } from "./browser.mjs";
import * as c from "../lib/curtailment.ts";
import * as v2 from "../lib/curtailmentv2.ts";
import * as fe from "../lib/freeenergy.ts";

const base = (process.argv[2] ?? "http://localhost:3144").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const read = (p) => JSON.parse(fs.readFileSync(new URL(`../data/${p}`, import.meta.url), "utf-8"));
const profile = read("curtailment_profile.json"), shares = read("curtailment/shares.json"), free = read("curtailment/free_energy.json"), worth = read("curtailment/worth.json"), ercot = read("curtailment/ercot.json");

const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(env("INTERNAL_COSTS_TOKEN") ?? "")}`, { redirect: "manual" });
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((x) => x.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exit(1); }
const get = async (path, withCookie = true) => { const r = await fetch(base + path, { headers: withCookie ? { Cookie: cookie } : {}, redirect: "manual" }); return { status: r.status, html: await r.text(), location: r.headers.get("location") }; };
const un = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
const plain = (html) => un(html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ");
const face = (html) => { const i = html.indexOf("<h1"); return i < 0 ? "" : html.slice(i); };
const marked = (html) => Object.fromEntries([...html.matchAll(/<span data-n="([^"]+)">([^<]*)<\/span>/g)].map((x) => [un(x[1]), x[2]]));
/** every placeholder of a piece of HTML: its words and its hover reason */
const blanks = (html) => [...html.matchAll(/<span class="[^"]*"\s+data-missing="1"\s+title="([^"]*)">([^<]*)<\/span>/g)].map((x) => ({ why: un(x[1]), words: x[2] }));
const section = (html, id) => new RegExp(`<section id="${id}"[\\s\\S]*?</section>`).exec(html)?.[0] ?? "";
const METHOD_WORDS = /upper bound|cannot see|limitation|caveat|does not say|does not locate|How it is computed|not computable|never scaled|round-trip/i;
const worthPeriod = (side, period) => (period && (period.length === 7 ? side.months?.[period] : side.years[period]) ? period : Object.keys(side.years).sort().at(-1));
const diff = (got, want) => Object.entries(want).filter(([k, val]) => got[k] !== val).map(([k, val]) => `${k}: page ${got[k]}, file ${val}`);

// ---- opens, and the face ------------------------------------------------------------------------------------------
const home = await get("/curtailment");
{
  const html = face(home.html), t = plain(html);
  check(home.status === 200 && /<title>Curtailment/.test(home.html) && !/\bundefined\b|NaN/.test(t), '/curtailment opens as "Curtailment", with no "undefined" and no NaN');
  check(["days", "months", "hours", "reason", "batteries", "free-energy", "worth", "whose"].every((id) => html.includes(`<section id="${id}"`)), "its sections: by day, by month, by hour of the day, by reason, against battery charging, where free energy is, what it is worth, what each grid's number is");
  check(home.html.includes("/data/methods/curtailment") && !METHOD_WORDS.test(t) && !t.includes(String.fromCharCode(0x2014)), "the page names its Method note and carries no method or limitation words, and no em dash, on its face");
  const whose = Object.fromEntries([...html.matchAll(/data-whose="([a-z]+)">([^<]*)</g)].map((x) => [x[1], un(x[2])]));
  check(Object.keys(fe.FACE).length === 7 && Object.entries(fe.FACE).every(([g, f]) => whose[g] === f.line) && un(/data-face="caiso">([^<]*)</.exec(html)?.[1] ?? "") === fe.FACE.caiso.line, "one line per grid says what its number is: the seven lines of FACE, and the chosen grid's under the summary");
  check(/data-grid="miso" data-open="0"[^>]*>MISO[\s\S]{0,80}?paused while terms are reviewed/.test(html) && /data-grid="pjm" data-open="0"[^>]*>PJM[\s\S]{0,80}?licensed source needed/.test(html)
    && !/href="[^"]*grid=(miso|pjm)/.test(html), 'MISO reads "paused while terms are reviewed" and PJM "licensed source needed"; neither can be chosen');
  check(c.GRIDS.filter((g) => g.open).every((g) => new RegExp(`data-grid="${g.id}" data-open="1"`).test(html)), "the five public grids can each be chosen");
  const m = await get("/curtailment?grid=miso");
  check(/data-face="caiso"/.test(m.html) && !/data-face="miso"/.test(m.html), "an address that names MISO opens the default grid, CAISO");
}

// ---- California: what /curtailment/v2 showed ------------------------------------------------------------------------
async function california(period) {
  const { status, html } = await get(`/curtailment?period=${period}`);
  const tag = `California, ${period}:`;
  const r = v2.periodOf(profile, period), got = marked(html), cover = v2.reasonCover(r), peak = v2.peakHour(r);
  const wrong = [];
  const want = (k, val) => { if (got[k] !== val) wrong.push(`${k}: page ${got[k]}, file ${val}`); };
  const absent = (k) => { if (k in got) wrong.push(`${k}: on the page (${got[k]}), not in the file`); };
  for (const [k, val] of [["sum|solar", r.curtailed_solar_mwh], ["sum|wind", r.curtailed_wind_mwh], ["head|solar", r.curtailed_solar_mwh], ["head|wind", r.curtailed_wind_mwh], ["head|peak_solar", peak.solar], ["days_held", r.days_held]]) want(k, v2.whole(val));
  if (cover === "none") { absent("sum|local"); absent("head|local"); } else {
    want("sum|local", v2.whole(r.curtailed_solar_local_mwh + r.curtailed_wind_local_mwh));
    want("head|system", v2.whole(r.curtailed_solar_system_mwh + r.curtailed_wind_system_mwh));
  }
  if (cover === "part") want("head|unspecified", v2.whole(r.curtailed_solar_unspecified_mwh + r.curtailed_wind_unspecified_mwh)); else absent("head|unspecified");
  for (const f of v2.FUELS) {
    for (const x of v2.REASONS) want(`reason|${f.key}|${x.key}`, v2.whole(r[`curtailed_${f.key}_${x.key}_mwh`] ?? 0));
    want(`reason|${f.key}|all`, v2.whole(r[`curtailed_${f.key}_mwh`]));
    for (const k of v2.CATS) { if (v2.hasCats(r)) want(`cat|${f.key}|${k.key}`, v2.whole(r[`curtailed_${f.key}_${k.key}_mwh`] ?? 0)); else absent(`cat|${f.key}|${k.key}`); }
  }
  const bm = v2.batteryMonths(profile);
  const battMonth = period.length === 7 ? (v2.hasBattery(r) ? period : null) : bm.filter((m) => m.startsWith(period)).at(-1) ?? null;
  if (battMonth) {
    const b = profile.months[battMonth];
    want("batt|curtailed", v2.whole(b.curtailed_mwh_battery_days)); want("batt|charging", v2.whole(b.battery_charging_mwh)); want("batt|days", v2.whole(b.battery_days_held));
    if (b.curtailed_while_charging_share_pct !== undefined) { want("batt|while", v2.two(b.curtailed_while_charging_share_pct)); want("sum|while", v2.two(b.curtailed_while_charging_share_pct)); }
  } else { absent("batt|curtailed"); absent("sum|while"); }
  // the period's share is shares.json's: a month's own, a year's from its months (one definition)
  const ps = c.periodShare(shares.grids.caiso, period);
  if (ps) { want("sum|share", c.two(ps.share)); want("head|share", c.two(ps.share)); } else { absent("sum|share"); absent("head|share"); }
  check(status === 200 && wrong.length === 0, `${tag} every marked number is the file's (${Object.keys(got).length} on the page)${wrong.length ? `: ${wrong.slice(0, 5).join("; ")}` : ""}`);
  const t = plain(face(html));
  check(html.includes('data-chart="hours"') && html.includes('data-chart="months-reason"') && html.includes('data-chart="months-fuel"') && (cover === "none") === t.includes("CAISO published no reason for it then") && v2.hasCats(r) === html.includes('data-cats="1"'),
    `${tag} the charts by hour, by reason and by month are on the page; reason ${cover === "none" ? "not published, said so" : cover === "part" ? "published for part" : "published"}; CAISO's categories ${v2.hasCats(r) ? "shown" : "not shown"}`);
  check(battMonth ? html.includes('data-chart="battery"') && (period === battMonth || html.includes(`data-battery-month="${battMonth}"`)) : html.includes('data-battery="none"') && !html.includes('data-chart="battery"'),
    `${tag} the batteries: ${battMonth ? `compared for ${battMonth}` : "a placeholder, with the months that hold them"}`);
  check(!/\bundefined\b|NaN/.test(t) && t.includes("Credit: California ISO") && !t.includes("not computable"), `${tag} no "undefined", no NaN, no "not computable"; the credit to the California ISO`);
}
for (const p of ["2025", "2019", "2022", "2026", "2024-04", "2026-05", "2025-09", "2026-03"]) await california(p);
{
  const d = await get("/curtailment?period=1999-13");
  const newest = Object.keys(profile.years).sort().at(-1);
  check(d.status === 200 && marked(d.html)["head|solar"] === v2.whole(profile.years[newest].curtailed_solar_mwh), `a period it does not understand opens the newest year (${newest})`);
}

// ---- shares ---------------------------------------------------------------------------------------------------------
for (const grid of ["caiso", "spp"]) {
  const g = shares.grids[grid], html = (grid === "caiso" ? home : await get(`/curtailment?grid=${grid}`)).html, got = marked(html), marks = c.shareMarks(g);
  const table = [...section(html, "months").matchAll(/data-n="share\|(\d{4}-\d\d)">([^<]*)</g)];
  check(table.length >= 12 && table.every(([, m, val]) => g.months[m] && val === c.two(g.months[m].share_pct)), `${grid}: each of the ${table.length} months of the table has shares.json's share`);
  check(got["share|last"] === c.two(g.months[marks.last].share_pct) && got["share|highest"] === c.two(g.months[marks.highest].share_pct) && got["share|months"] === c.whole(g.months_with_share),
    `${grid}: the newest month's share (${c.two(g.months[marks.last].share_pct)} percent, ${marks.last}), the highest (${c.two(g.months[marks.highest].share_pct)}, ${marks.highest}) and the ${g.months_with_share} months with one are the file's`);
  const fold = Object.fromEntries([...html.matchAll(/data-share-month="(\d{4}-\d\d)">([^<]*)</g)].map((x) => [x[1], x[2]]));
  const missing = [...html.matchAll(/data-share-missing="(\d{4}-\d\d)"><span class="[^"]*"\s+data-missing="1"\s+title="([^"]*)">([^<]*)</g)];
  check(Object.keys(fold).length === Object.keys(g.months).length && Object.entries(g.months).every(([m, r]) => fold[m] === c.two(r.share_pct)), `${grid}: all ${Object.keys(g.months).length} months with a share are in the fold, each the file's`);
  check(missing.length === Object.keys(g.missing).length && missing.every(([, m, why, words]) => un(why) === g.missing[m] && words === "not held yet") && !plain(html).includes("not computable"),
    `${grid}: ${missing.length} months without a share read "not held yet" with the file's reason on hover; nothing reads "not computable"`);
}
{
  const s = await get("/curtailment?grid=spp"), got = marked(s.html), g = shares.grids.spp, marks = c.shareMarks(g);
  const wrong = diff(got, { "sum|curtailed": c.whole(g.months[marks.last].curtailed_mwh), "sum|share": c.two(g.months[marks.last].share_pct), "sum|highest": c.two(g.months[marks.highest].share_pct), "head|share": c.two(g.months[marks.last].share_pct), "head|curtailed": c.whole(g.months[marks.last].curtailed_mwh) });
  check(wrong.length === 0 && /data-face="spp"/.test(s.html) && !s.html.includes('data-chart="hours"'), `SPP: its summary and headline numbers are shares.json's, and California's hourly sections are not on its view${wrong.length ? `: ${wrong.join("; ")}` : ""}`);
}

// ---- Texas ----------------------------------------------------------------------------------------------------------
{
  const e = await get("/curtailment?grid=ercot"), html = face(e.html), got = marked(html), tx = section(html, "texas"), t = plain(html);
  const want = { "sum|below": c.whole(ercot.window.both.below_hsl_mwh), "sum|share": c.two(ercot.window.both.share_pct), "sum|wind": c.two(ercot.window.wind.share_pct), "sum|solar": c.two(ercot.window.solar.share_pct),
    "head|below": c.whole(ercot.window.both.below_hsl_mwh), "head|share": c.two(ercot.window.both.share_pct), "tx|hours": c.whole(ercot.hours_held), "tx|window|wind": c.whole(ercot.window.wind.below_hsl_mwh), "tx|window|solar": c.whole(ercot.window.solar.below_hsl_mwh) };
  for (const [d, r] of Object.entries(ercot.days)) { want[`tx|${d}|wind`] = c.whole(r.wind.below_hsl_mwh); want[`tx|${d}|solar`] = c.whole(r.solar.below_hsl_mwh); want[`tx|${d}|share`] = c.two(r.both.share_pct); }
  for (const f of ["wind", "solar"]) for (const r of ercot.regions[f]) want[`tx|region|${f}|${r.id}`] = c.whole(r.generation_mwh);
  const wrong = diff(got, want);
  check(e.status === 200 && wrong.length === 0, `Texas: the ${ercot.whole_days} days held, their sum (${want["sum|below"]} MWh below the limit, ${want["sum|share"]} percent) and the output of ${ercot.regions.wind.length + ercot.regions.solar.length} regions are ercot.json's${wrong.length ? `: ${wrong.slice(0, 5).join("; ")}` : ""}`);
  const noMonth = Object.entries(ercot.months).filter(([, r]) => r.missing);
  check(noMonth.every(([m, r]) => new RegExp(`data-month-missing="${m}">[\\s\\S]{0,200}?data-missing="1"`).test(tx) && blanks(tx).some((b) => b.why === r.missing && b.words === "not held yet")) && !noMonth.some(([m]) => `tx|${m}|wind` in got),
    `Texas: ${noMonth.map(([m]) => m).join(" and ") || "no month"} read${noMonth.length === 1 ? "s" : ""} "not held yet" with the hours held on hover, and no figure`);
  const limits = blanks(tx).filter((b) => b.words === "no limit published");
  check(limits.length === ercot.regions.wind.length + ercot.regions.solar.length + Object.keys(ercot.years).length && limits.every((b) => b.why === ercot.region_reason || b.why === ercot.year_reason) && blanks(tx).some((b) => b.why === ercot.history_reason),
    `Texas: each of ${ercot.regions.wind.length + ercot.regions.solar.length} regions and ${Object.keys(ercot.years).length} years reads "no limit published" with the reason on hover; the history before the first reading "not held yet"`);
  check(t.includes(fe.FACE.ercot.line) && (html.match(/data-estimate="1"/g) ?? []).length >= 2 && html.includes('data-chart="texas-hours"') && html.includes('data-chart="texas-pattern"') && /data-days-share="1">[\d.]+</.test(html),
    "Texas: the figure is named the ERW's estimate in the section and in the worth; the hours and the hour-of-day pattern are charts");
  const w = worth.grids.ercot, win = w.hubs[w.main_hub].rt.window;
  const ww = diff(got, { "worth|value": c.usd(win.value_usd), "worth|per": c.two(win.usd_per_mwh_curtailed), "worth|hours": c.whole(win.hours_priced), "bat|per_mw": c.whole(w.battery.window.absorb_mwh_per_mw["4"]), [`worth|ercot|HB_WEST|rt|neg`]: c.two(w.hubs.HB_WEST.rt.window.share_mwh_negative_pct) });
  check(ww.length === 0 && blanks(section(html, "worth")).some((b) => b.why === w.months_missing) && blanks(section(html, "worth")).some((b) => b.why === w.battery.fleet_missing),
    `Texas, worth: USD ${c.usd(win.value_usd)} over ${win.hours_priced} priced hours and ${w.battery.window.absorb_mwh_per_mw["4"]} MWh per MW for a 4-hour battery are worth.json's; a month and the fleet are placeholders with the file's reasons${ww.length ? `: ${ww.join("; ")}` : ""}`);
}

// ---- where free energy is -------------------------------------------------------------------------------------------
for (const [id, g] of Object.entries(free.grids)) {
  const r = await get(`/curtailment?grid=${id}`), html = section(face(r.html), "free-energy"), got = marked(html);
  const want = {}, reasons = [];
  for (const l of g.locations) for (const w of ["month", "year"]) { if (fe.isHeld(l[w])) { want[`loc|${l.id}|${w}|under5`] = c.whole(l[w].under5); want[`loc|${l.id}|${w}|negative`] = c.whole(l[w].negative); } else reasons.push(l[w].missing); }
  const wrong = diff(got, want);
  const win = fe.ranked(g, "year").length >= 2 ? "year" : "month", top = fe.ranked(g, win)[0];
  const tiles = [...html.matchAll(/data-tile="([^"]+)" data-count="(\d*)"/g)].map((x) => [un(x[1]), x[2]]);
  const places = g.locations.filter((l) => l.kind !== "average");
  check(r.status === 200 && wrong.length === 0 && reasons.every((why) => blanks(html).some((b) => b.why === why && b.words === "not held yet")),
    `${g.name}: the counts of its ${g.locations.length} places, last month and last twelve months, are the file's (${Object.keys(want).length} numbers); ${reasons.length} windows not held read "not held yet" with the reason${wrong.length ? `: ${wrong.slice(0, 4).join("; ")}` : ""}`);
  check(tiles.length === places.length && tiles.every(([p, count]) => { const l = g.locations.find((x) => x.id === p); return fe.isHeld(l[win]) ? count === String(l[win].under5) : count === ""; })
    && tiles[0][0] === top.id && /A schematic, not a map/.test(html) && new RegExp(`data-tile="${top.id.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}"[^>]*aria-current="true"`).test(html),
    `${g.name}: the schematic has a tile for each of its ${places.length} hubs and zones with the file's count, says it is a schematic, and opens on ${top.id}, the place with the most hours`);
  const wantGap = {};
  for (const w of ["year", "month"]) { const x = g.gap[w]; if (fe.hasGap(x)) { wantGap[`gap|${w}`] = c.two(x.gap); wantGap[`gap|${w}|cheapest`] = c.two(x.cheapest.mean); wantGap[`gap|${w}|dearest`] = c.two(x.dearest.mean); } }
  const gw = diff(got, wantGap), noGap = ["year", "month"].filter((w) => !fe.hasGap(g.gap[w]));
  check(gw.length === 0 && noGap.every((w) => blanks(html).some((b) => b.why === g.gap[w].missing)) && got[`top|${win}`] === c.whole(top.win.under5),
    `${g.name}: the gap between its cheapest and dearest place is the file's (${["year", "month"].map((w) => (fe.hasGap(g.gap[w]) ? `${w} ${c.two(g.gap[w].gap)}` : `${w} not held yet`)).join(", ")} USD per MWh)${gw.length ? `: ${gw.join("; ")}` : ""}`);
}
{
  const r = await get("/curtailment?grid=ercot&place=HB_WEST"), html = section(face(r.html), "free-energy"), got = marked(html);
  const l = free.grids.ercot.locations.find((x) => x.id === "HB_WEST");
  check(/data-tile="HB_WEST"[^>]*aria-current="true"/.test(html) && html.includes("HB WEST: hours under USD") && html.includes('data-chart="free-heat"') && (!l.heat.whole || (got["heat|under5"] === c.whole(fe.heatTotal(l.heat, "under5")) && got["heat|negative"] === c.whole(fe.heatTotal(l.heat, "negative")))),
    `/curtailment?grid=ercot&place=HB_WEST#free-energy opens West Texas: its heatmap, and the cells' sum (${fe.heatTotal(l.heat, "under5")} hours under USD 5, ${fe.heatTotal(l.heat, "negative")} below zero)`);
  const other = await get("/curtailment?grid=nyiso&place=" + encodeURIComponent("N.Y.C."));
  check(/data-tile="N\.Y\.C\."[^>]*aria-current="true"/.test(other.html) && (await get("/curtailment?grid=ercot&place=NOWHERE")).html.includes('aria-current="true"'), "a place with dots in its name opens; a place the grid does not hold opens the default");
  const y = fe.summaryPairs(free, "year"), m = fe.summaryPairs(free, "month"), want = {};
  if (y.texas) Object.assign(want, { "pair|texas|west|under5": c.whole(y.texas.west.under5), "pair|texas|west|negative": c.whole(y.texas.west.negative), "pair|texas|houston|under5": c.whole(y.texas.houston.under5) });
  if (y.california) Object.assign(want, { "pair|california|south|under5": c.whole(y.california.south.under5), "pair|california|south|negative": c.whole(y.california.south.negative), "pair|california|north|under5": c.whole(y.california.north.under5) });
  if (m.texas && m.california) Object.assign(want, { "pair|texas|west|month": c.whole(m.texas.west.under5), "pair|texas|houston|month": c.whole(m.texas.houston.under5), "pair|california|south|month": c.whole(m.california.south.under5), "pair|california|north|month": c.whole(m.california.north.under5) });
  const wrong = diff(got, want), sum = /data-free-summary="1"[\s\S]*?<\/p>/.exec(html)?.[0] ?? "";
  check(wrong.length === 0 && Object.keys(want).length >= 6 && /West Texas/.test(sum) && /Houston/.test(sum) && /SP15/.test(sum) && /NP15/.test(sum),
    `the summary sentence calls out West Texas against Houston (${want["pair|texas|west|under5"]} hours under USD 5 against ${want["pair|texas|houston|under5"]}) and California south against north (${want["pair|california|south|under5"]} against ${want["pair|california|north|under5"]}), from the file's pairs${wrong.length ? `: ${wrong.join("; ")}` : ""}`);
  check(/title="Hours priced under USD 5 per MWh\. The hours below zero are among them: each hour is counted once\."/.test(html), "the count under USD 5 says on hover that it includes the hours below zero, each counted once");
}

// ---- what it is worth -----------------------------------------------------------------------------------------------
for (const [q, period, dur] of [["/curtailment", null, 4], ["/curtailment?period=2025&dur=2", "2025", 2], ["/curtailment?period=2026-04&dur=8", "2026-04", 8], ["/curtailment?period=2019", "2019", 4]]) {
  const r = await get(q), html = section(face(r.html), "worth"), got = marked(html);
  const g = worth.grids.caiso, side = g.hubs[g.main_hub].rt, p = worthPeriod(side, period ?? v2.choice({}, profile)), val = p.length === 7 ? side.months[p] : side.years[p], b = p.length === 7 ? g.battery.months[p] : g.battery.years[p], d = String(dur);
  const want = { "worth|value": c.usd(val.value_usd), "worth|per": c.two(val.usd_per_mwh_curtailed), "worth|mwh": c.whole(val.curtailed_mwh_priced), "worth|neg": c.two(val.share_mwh_negative_pct), "worth|under5": c.two(val.share_mwh_under5_pct),
    "worth|flat": c.two(val.price_curtailed_hours_mean), "worth|all": c.two(val.price_all_hours_mean), "bat|per_mw": c.whole(b.absorb_mwh_per_mw[d]), "bat|curtailed": c.whole(b.curtailed_mwh) };
  for (const [hub, sides] of Object.entries(g.hubs)) for (const [mk, s] of Object.entries(sides)) { const x = p.length === 7 ? s.months[p] : s.years[p]; if (x) { want[`worth|caiso|${hub}|${mk}|value`] = c.usd(x.value_usd); want[`worth|caiso|${hub}|${mk}|flat`] = c.two(x.price_curtailed_hours_mean); } }
  for (const x of worth.durations_hours) want[`bat|${x}|per_mw`] = c.whole(b.absorb_mwh_per_mw[String(x)]);
  if (b.fleet) { Object.assign(want, { "bat|fleet": c.whole(b.fleet.fleet_charged_in_curtailed_hours_mwh), "bat|share": c.two(b.fleet.absorbable_pct_of_fleet_charged[d]), "bat|absorb": c.whole(b.fleet.absorb_fleet_mwh[d]) }); for (const x of worth.durations_hours) want[`bat|${x}|share`] = c.two(b.fleet.absorbable_pct_of_fleet_charged[String(x)]); }
  const wrong = diff(got, want);
  check(r.status === 200 && wrong.length === 0 && (b.fleet || blanks(html).some((x) => x.why === b.fleet_missing)) && html.includes('data-chart="worth-months"') && html.includes('data-chart="battery-months"'),
    `California, worth, ${p}${period && p !== period ? ` (the prices do not hold ${period})` : ""}, ${dur} hours: USD ${c.usd(val.value_usd)} at SP15, ${c.two(val.share_mwh_negative_pct)} percent in hours below zero, a flat load at ${c.two(val.price_curtailed_hours_mean)} against ${c.two(val.price_all_hours_mean)}; the battery ${b.fleet ? `${c.two(b.fleet.absorbable_pct_of_fleet_charged[d])} percent of what the fleet charged` : "against the fleet: a placeholder with the file's reason"}${wrong.length ? `: ${wrong.slice(0, 5).join("; ")}` : ""}`);
}
{
  const s = await get("/curtailment?grid=spp"), html = section(face(s.html), "worth");
  check(blanks(html).filter((b) => b.why === worth.grids.spp.missing && b.words === "not held yet").length >= 3 && !/data-n="worth\|value"/.test(html), 'SPP, worth: "not held yet" with the file\'s reason on hover, and no number');
  check(/data-blank="miso">paused while terms are reviewed</.test(html) && /data-blank="pjm">licensed source needed</.test(html) && ["nyiso", "isone"].every((g) => blanks(html).some((b) => b.why === worth.not_held[g])),
    'the table grid by grid: MISO "paused while terms are reviewed", PJM "licensed source needed", NYISO and ISO-NE placeholders with the file\'s reasons');
  const ne = await get("/curtailment?grid=isone"), t = plain(face(ne.html));
  check(ne.status === 200 && t.includes(fe.FACE.isone.line) && !ne.html.includes('<section id="days"') && ne.html.includes('<section id="free-energy"') && !/\bundefined\b|NaN/.test(t), "ISO-NE: its line says what exists, no curtailment number is shown, and its prices are in the free energy section");
}

// ---- the redirect, and the visitor ----------------------------------------------------------------------------------
{
  const r = await get("/curtailment/v2?period=2026-05");
  check([307, 308].includes(r.status) && /\/curtailment\?period=2026-05$/.test(r.location ?? ""), `/curtailment/v2?period=2026-05 answers ${r.status} to ${r.location}: the address redirects and carries its query`);
  const f = await fetch(`${base}/curtailment/v2?period=2026-05`, { headers: { Cookie: cookie } }), html = await f.text();
  check(f.status === 200 && marked(html)["head|solar"] === v2.whole(profile.months["2026-05"].curtailed_solar_mwh), "followed, it is the one page showing May 2026");
  const v = await get("/curtailment", false);
  check(v.status === 200 && v.html.includes('data-in-review="1"') && !v.html.includes("data-n=") && !v.html.includes('data-summary="1"'), "as a visitor: the in-review page, and no number of the tool");
}

// ---- a real browser: every chart answers the mouse ------------------------------------------------------------------
const code = await withBrowser(async ({ go, evaluate, wait, unlock: open, errors, sleep }) => {
  await open(base);
  const tip = (id, s, i) => evaluate(`(() => { const el = document.querySelector('[data-chart="${id}"]'); if (!el) return 'NO CHART'; const chart = window.echarts && window.echarts.getInstanceByDom(el); if (!chart) return 'NO INSTANCE';
    chart.resize(); chart.dispatchAction({ type: 'showTip', seriesIndex: ${s}, dataIndex: ${i} });
    return new Promise((ok) => setTimeout(() => ok([...el.querySelectorAll('div')].map((d) => d.innerText || '').filter((t) => t.trim()).sort((x, y) => x.length - y.length)[0] ?? ''), 450)); })()`);
  const charts = async (path, wants) => {
    await go(base + path);
    await evaluate(`document.querySelectorAll('details').forEach((d) => { d.open = true; })`);
    await wait(`[...document.querySelectorAll('[data-chart]')].length >= ${wants.length} && [...document.querySelectorAll('[data-chart]')].every((el) => el.querySelector('canvas'))`, 45000, `the charts of ${path}`);
    await sleep(600);
    for (const [id, s, i, re] of wants) {
      const t = (await tip(id, s, i)).replace(/\s+/g, " ");
      check(re.test(t), `${path}: the chart "${id}" answers the mouse ("${t.slice(0, 110)}")`);
    }
  };
  await charts("/curtailment?period=2026-04", [
    ["days", 0, 5, /\d{4}-\d\d-\d\d.*Solar curtailed: [\d,.]+ MWh/], ["months", 0, 100, /\d{4}-\d\d.*curtailed: [\d,.]+ MWh.*Share of available output: [\d.]+ percent/], ["hours", 0, 12, /12:00.*Solar: [\d,.]+ MWh/],
    ["months-reason", 0, 60, /\d{4}-\d\d.*Local congestion: [\d,.]+ MWh.*days held/], ["battery", 0, 12, /12:00.*Wind and solar curtailed: [\d,.]+ MW.*Battery charging: [\d,.]+ MW/], ["months-fuel", 0, 80, /\d{4}-\d\d.*Solar: [\d,.]+ MWh.*days held/],
    ["free-heat", 0, 30, /hours under USD 5, \d+ below zero|not held/], ["worth-months", 0, 19, /\d{4}-\d\d.*Value: -?[\d,.]+ USD.*Per MWh curtailed: -?[\d.]+ USD\/MWh.*percent of it in hours below zero/], ["battery-months", 0, 7, /\d{4}-\d\d.*Curtailed: [\d,.]+ MWh.*The fleet charged in those hours: [\d,.]+ MWh.*percent of what the fleet charged/],
  ]);
  const title = await evaluate(`document.querySelector('[data-tile]').getAttribute('title')`);
  check(/hours under USD 5, [\d,]+ of them below zero, of [\d,]+ held/.test(title), `a tile of the schematic says its count on hover ("${title}")`);
  await evaluate(`[...document.querySelectorAll('[data-tile]')].at(1).click()`);
  await wait(`location.search.includes('place=') && location.hash === '#free-energy' && document.querySelectorAll('[data-tile][aria-current="true"]').length === 1`, 20000, "the tile's place");
  check(await evaluate(`document.querySelector('[data-tile][aria-current="true"]').getAttribute('data-tile') === new URLSearchParams(location.search).get('place')`), "choosing a tile opens that place, in the address and on the page");
  await charts("/curtailment?grid=ercot&place=HB_WEST#free-energy", [
    ["days", 0, 3, /\d{4}-\d\d-\d\d.*below the limit: [\d,.]+ MWh/], ["texas-hours", 0, 40, /\d\d-\d\d \d\d:00.*Wind limit: [\d,.]+ MW.*Wind output: [\d,.]+ MW.*Below the limit: wind [\d,]+ MW, solar [\d,]+ MW/],
    ["texas-pattern", 0, 18, /18:00.*Wind below the limit: [\d,.]+ MWh.*hours of the day held/], ["free-heat", 0, 100, /HB WEST\. .*(hours under USD 5, \d+ below zero|not held)/],
  ]);
  await charts("/curtailment?grid=spp", [["days", 0, 10, /Wind curtailed: [\d,.]+ MWh/], ["months", 0, 3, /2014-\d\d.*Wind curtailed: [\d,.]+ MWh.*Share not held yet: curtailment and output are both held for 0 of/], ["free-heat", 0, 10, /hours under USD 5|not held/]]);
  check(errors.length === 0, `no script error on the page${errors.length ? `: ${errors[0].slice(0, 160)}` : ""}`);
  return 0;
});
if (code === null) console.log("note: no Chrome or Edge on this machine; the browser checks were not run");
console.log(bad ? `${bad} of ${n} failed` : `all ${n} passed`);
process.exit(bad ? 1 : 0);
