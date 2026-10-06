// Energy Research Warehouse (ERW) site, session 134: Supply and trade (/supply), on the built site.
//
//   npm run build && npx next start -p 3134
//   node --import ./scripts/alias-register.mjs scripts/check-supply.mjs [base-url]      (default http://localhost:3134)
//
// As HTML, in the internal view (the page is in review):
//   opens       200, its title, every group, no "undefined", no NaN, no method prose on the face; it names its Method note
//   numbers     every row's latest value and five-year average, and the five headline figures, equal the site's file
//               (data/supply.json), written as the page writes them
//   against     gas in storage in the Lower 48: its change on the week, on the year and against the five-year average,
//               and its change against the five-year average change, are the file's
//   surprises   the rows marked "outside range" are exactly the file's
//   blank       MISO reads "paused while terms are reviewed", PJM and ICE "licensed source needed", what is not pulled
//               "not held yet": each with its reason on hover and no value
//   calendar    the three reports' next releases are worked out as of now from the file's rules; none is in the past
//   address     ?g= shows only the groups chosen; ?s= opens that series' chart; an unknown series opens none
//   method      the Method note opens and holds the research, the terms and the heat rates
//   visitor     without the cookie the page is the in-review page
// In a real browser: every band chart is drawn and answers the mouse with the date, each series and the unit; a trend
// line answers the mouse; a row opens its chart and the address holds it; a "Select" chip leaves one group; at a
// phone's width the page does not scroll sideways.
// Exit 1 on a failure.
import fs from "node:fs";
import { env, withBrowser } from "./browser.mjs";
import { HEADLINE, PLACEHOLDER, dateWords, easternNow, fmt, nextRelease, pct, releaseWords, signed, surprises } from "../lib/supply.ts";

const base = (process.argv[2] ?? "http://localhost:3134").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const file = JSON.parse(fs.readFileSync(new URL("../data/supply.json", import.meta.url), "utf-8"));
const row = (id) => file.rows.find((r) => r.id === id);
const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(env("INTERNAL_COSTS_TOKEN") ?? "")}`, { redirect: "manual" });
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exit(1); }
const get = async (path, withCookie = true) => { const r = await fetch(base + path, { headers: withCookie ? { Cookie: cookie } : {} }); return { status: r.status, html: await r.text() }; };
const plain = (html) => html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ");
/** The page's own part of the HTML: from its first element to the end of the document's main. */
const face = (html) => { const i = html.indexOf('data-supply="1"'); return i < 0 ? "" : html.slice(i); };
const marked = (html, kind) => Object.fromEntries([...html.matchAll(/data-n="([^"|]+)\|([^"]+)"[^>]*>([^<]*)</g)].filter((m) => (kind === "head" ? m[1] === "head" : m[2] === kind)).map((m) => [kind === "head" ? m[2] : m[1], m[3]]));
const rowHtml = (html, id) => { const m = new RegExp(`<tr[^>]*data-row="${id}"[\\s\\S]*?</tr>`).exec(html); return m ? m[0] : ""; };

const page = await get("/supply");
const html = face(page.html);
const text = plain(html);
{
  const words = /\b(methodology|limitations?|disputed)\b|\bnot held\b(?! yet)|against expectations|consensus/i.exec(text);
  check(page.status === 200 && !!html && text.includes("Supply and trade") && !/\bundefined\b|NaN/.test(text) && !words, `/supply opens, with no "undefined", no NaN and no method prose on its face${words ? ` (found "${words[0]}")` : ""}`);
  check(file.groups.every((g) => html.includes(`data-group="${g.id}"`)) && file.groups.every((g) => html.includes(`data-chip="${g.id}"`)), `all ${file.groups.length} groups are on the page, each with its "Select" chip`);
  check(page.html.includes("/data/methods/supply_and_trade") && text.includes("Method, sources and gaps"), "the page names its Method note");
  check(text.includes("Tighter or looser than last week, last year and normal for the season"), "the page states its question");
}
{
  const ok = file.rows.filter((r) => r.status === "ok");
  const last = marked(html, "last");
  const wrong = ok.filter((r) => last[r.id] !== fmt(r.last.v, r.unit));
  check(Object.keys(last).length === ok.length && wrong.length === 0, `the latest value of each of the ${ok.length} rows held is the file's${wrong.length ? ` (not ${wrong.slice(0, 3).map((r) => r.id).join(", ")})` : ""}`);
  const avg = marked(html, "avg5");
  const have = ok.filter((r) => r.avg5);
  const off = have.filter((r) => avg[r.id] !== fmt(r.avg5.v, r.unit, r.last.v));
  check(Object.keys(avg).length === have.length && off.length === 0, `the five-year average of each of the ${have.length} rows that has one is the file's; the other ${ok.length - have.length} show a placeholder`);
  const head = marked(html, "head");
  check(HEADLINE.every((id) => head[id] === fmt(row(id).last.v, row(id).unit)) && Object.keys(head).length === HEADLINE.length, `the ${HEADLINE.length} headline figures are the file's (gas in storage ${head[HEADLINE[0]]} Bcf, commercial crude ${head[HEADLINE[1]]} million bbl)`);
}
{
  const r = row("eia-nw2-epg0-swo-r48-bcf");
  const t = plain(rowHtml(html, r.id));
  const want = [signed(r.prev.ch, r.unit, r.last.v), signed(r.year.ch, r.unit, r.last.v), pct(r.year.pct), fmt(r.avg5.v, r.unit, r.last.v), signed(r.avg5.ch, r.unit, r.last.v), signed(r.change.surprise, r.unit, r.last.v)];
  const lost = want.filter((w) => !t.includes(w));
  check(lost.length === 0 && /tighter|looser/.test(t), `gas in storage, the Lower 48: on the week ${want[0]}, on the year ${want[1]} (${want[2]}), against the five-year average ${want[4]}, change against the five-year average change ${want[5]}${lost.length ? ` (missing ${lost.join(", ")})` : ""}`);
  const outside = [...html.matchAll(/data-surprise="([^"]+)"/g)].map((m) => m[1]).sort();
  const expected = surprises(file).map((x) => x.id).sort();
  check(outside.join() === expected.join() && expected.length > 0, `${expected.length} rows are marked "outside range", exactly the file's`);
  const list = /data-surprises="1"[\s\S]*?<\/section>/.exec(html)?.[0] ?? "";
  const top = surprises(file).slice(0, 8);
  check(top.every((x) => plain(list).includes(`${x.label}, ${x.at}`)), `the list at the top holds the ${top.length} farthest of them`);
}
{
  const blank = file.rows.filter((r) => r.status !== "ok");
  const wrong = blank.filter((r) => { const h = rowHtml(html, r.id); return !h.includes(`data-status="${r.status}"`) || !plain(h).includes(PLACEHOLDER[r.status]) || !/data-missing="1"/.test(h) || !/title="[^"]{20,}"/.test(h) || /data-n=/.test(h); });
  check(blank.length > 0 && wrong.length === 0, `the ${blank.length} rows with no value read their placeholder, with the reason on hover and no number${wrong.length ? ` (not ${wrong.map((r) => r.id).join(", ")})` : ""}`);
  const say = (id) => plain(rowHtml(html, id));
  check(say("cleared-miso").includes("paused while terms are reviewed") && say("cleared-pjm").includes("licensed source needed") && say("ice-brent").includes("licensed source needed") && say("gasprod-weekly").includes("licensed source needed")
    && say("cleared-ercot").includes("not held yet") && say("burn-caiso-oil").includes("not held yet"), "MISO paused, PJM and ICE and weekly gas production licensed, the rest not held yet");
}
{
  const rel = Object.fromEntries([...html.matchAll(/data-release="([^"]+)"[^>]*>([^<]*)</g)].map((m) => [m[1], m[2]]));
  const at = easternNow(new Date());
  const due = Object.fromEntries(file.calendar.reports.map((r) => [r.id, releaseWords(nextRelease(r, at).next)]));
  check(file.calendar.reports.length === 3 && file.calendar.reports.every((r) => rel[r.id] === due[r.id] && nextRelease(r, at).next > at),
    `the next releases are worked out as of now from the file's rules and alternate dates, and none is in the past (${file.calendar.reports.map((r) => `${r.id} ${due[r.id]}`).join("; ")})`);
}
{
  const one = face((await get("/supply?g=gasstor,position")).html);
  const shown = [...one.matchAll(/data-group="([^"]+)"/g)].map((m) => m[1]);
  check(shown.join() === "gasstor,position" && !one.includes('data-row="eia-wcestus1"'), "?g=gasstor,position shows those two groups and no other");
  const open = face((await get("/supply?s=eia-wgtstus1")).html);
  check(open.includes('data-open-chart="eia-wgtstus1"') && (open.match(/data-band="eia-wgtstus1"/g) ?? []).length === 2, "?s=eia-wgtstus1 opens the gasoline stocks chart above the tables");
  const none = await get("/supply?s=cleared-miso&g=nowhere");
  check(none.status === 200 && !none.html.includes("data-open-chart=") && file.groups.every((g) => none.html.includes(`data-group="${g.id}"`)), "an address naming a series with no value, or a group that does not exist, is the whole page with no chart open");
}
{
  const m = await get("/data/methods/supply_and_trade");
  const t = plain(m.html);
  check(m.status === 200 && ["What trader desks and public dashboards show each morning", "five-year average change", "public domain", "personal, non-commercial use", "A blank hour is never read as zero"].every((w) => t.includes(w)), "the Method note opens and holds the research, the terms and the fuel burn's rules");
  const v = await get("/supply", false);
  check(v.status === 200 && v.html.includes('data-in-review="1"') && !v.html.includes('data-supply="1"') && !v.html.includes("data-n="), "as a visitor: the in-review page, and nothing of Supply and trade");
}

const code = await withBrowser(async ({ go, evaluate, wait, unlock: open, errors }) => {
  await open(base);
  await go(`${base}/supply`);
  const bands = await wait(`(() => { const all = document.querySelectorAll('[data-chart="band"]'); const drawn = document.querySelectorAll('[data-chart="band"] canvas'); return all.length >= 8 && all.length === drawn.length ? all.length : 0; })()`, 40000, "the band charts");
  check(true, `the ${bands} seasonal band charts are drawn`);
  check(await evaluate(`!!document.querySelector('a[href="/data/methods/supply_and_trade"]')`), "in the internal view the Method note is a link");
  const r = row("eia-nw2-epg0-swo-r48-bcf");
  const i = r.season.t.indexOf(r.last.t);
  const tip = await evaluate(`(() => { const el = document.querySelector('[data-band="${r.id}"]'); const chart = window.echarts.getInstanceByDom(el);
    chart.dispatchAction({ type: 'showTip', seriesIndex: 4, dataIndex: ${i} });
    return new Promise((ok) => setTimeout(() => ok([...el.querySelectorAll('div')].map((d) => d.innerText || '').filter((t) => /Five-year average/.test(t)).sort((x, y) => x.length - y.length)[0] ?? ''), 400)); })()`);
  check(tip.includes(dateWords(r.last.t)) && tip.includes(fmt(r.last.v, r.unit)) && /Five-year average/.test(tip) && /Five-year range/.test(tip) && /Bcf/.test(tip),
    `a band chart answers the mouse with the date, each series and the unit ("${tip.replace(/\s+/g, " ").slice(0, 150)}")`);
  const trend = await evaluate(`(() => { const svg = document.querySelector('[data-trend="eia-wcestus1"] svg'); const b = svg.getBoundingClientRect();
    svg.dispatchEvent(new MouseEvent('mouseover', { bubbles: true, clientX: b.left + b.width / 2, clientY: b.top + 5 }));
    svg.dispatchEvent(new MouseEvent('mousemove', { bubbles: true, clientX: b.left + b.width / 2, clientY: b.top + 5 }));
    return new Promise((ok) => setTimeout(() => ok(document.querySelector('[data-trend="eia-wcestus1"] [role="tooltip"]')?.innerText ?? ''), 300)); })()`);
  check(/Commercial crude|crude/i.test(trend) && /million bbl on \d+ \w{3} 20\d\d/.test(trend), `a trend line answers the mouse with the series, the value and the date ("${trend.replace(/\s+/g, " ").slice(0, 110)}")`);
  await evaluate(`document.querySelector('[data-open="eia-wdistus1"]').click()`);
  await wait(`location.search.includes('s=eia-wdistus1') && !!document.querySelector('[data-open-chart="eia-wdistus1"] canvas')`, 20000, "the opened chart");
  check(true, "a row opens its seasonal chart, and the address holds it");
  await evaluate(`document.querySelector('[data-chip="position"]').click()`);
  await wait(`location.search.includes('g=position') && document.querySelectorAll('[data-group]').length === 1`, 20000, "one group");
  check((await evaluate(`location.search`)).includes("s=eia-wdistus1") && (await evaluate(`!!document.querySelector('[data-row="cftc-067651"]') && !document.querySelector('[data-bands]')`)),
    'a "Select" chip leaves its one group, keeps the open chart and is in the address');
  check(errors.length === 0, `no script error on the page${errors.length ? `: ${errors[0].slice(0, 160)}` : ""}`);
  return 0;
});
if (code === null) console.log("not proven here: no browser on this machine (the HTML checks above stand)");
else {
  await withBrowser(async ({ go, evaluate, wait, unlock: open, send }) => {
    await open(base);
    await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 1, mobile: false });
    await go(`${base}/supply`);
    await wait(`document.querySelectorAll('[data-chart="band"] canvas').length >= 8`, 40000, "the band charts on a phone");
    const w = await evaluate(`[document.documentElement.scrollWidth, window.innerWidth]`);
    check(w[0] <= w[1] + 1, `at a phone's width the page does not scroll sideways (${w[0]} in ${w[1]}); its tables scroll inside themselves`);
    return 0;
  }, { width: 390, height: 844 });
}
console.log(`${n - bad} of ${n} checks pass`);
process.exitCode = bad ? 1 : 0;
