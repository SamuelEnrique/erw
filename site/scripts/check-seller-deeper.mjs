// Energy Research Warehouse (ERW) site, session 162: "What a generator earns", deeper (/cost-of-power/seller), on the
// built site. The page's older checks stay in scripts/check-seller.mjs; this one reads the three new blocks.
//
//   npm run build && npx next start -p 3162
//   node scripts/check-seller-deeper.mjs [base-url]      (default http://localhost:3162)
//
// As HTML, in the internal view (the page is in review):
//   hybrid    for ERCOT and CAISO, solar and wind, 2, 4 and 8 hours, both strategies: the plant alone, the battery
//             alone, the co-optimized pair and the two added equal lib/sellerhybrid.ts over data/seller/hybrid.json;
//             the pair is not below the plant and not above the two added; the added column is labeled an upper
//             bound; session 145's row is kept (plant, the battery page's figure, their sum); where the pair is above
//             that kept sum the page says so on its face; other sizes; a grid without a battery model
//   table     every cell of the capture price by hub and year equals lib/capture.ts over data/seller/capture.json;
//             a year not held is a placeholder with a reason; MISO and PJM are rows of words; no MISO hub
//   profile   the box, its one line, its years; no method prose on the face
// In a real browser:
//   table     the switch to wind and to real time, the sort by a year, the hover of a cell
//   profile   the price file is asked for before the paste; after a paste no request leaves the page, the address is
//             as it was, storage and cookies hold nothing of it; the figures equal the library's on the same file; a
//             flat profile captures the simple average; a wrong length, a value below zero and a gap are refused
// Exit 1 on a failure. With --json FILE the figures read are written there for the session's report.
import fs from "node:fs";
import { env, withBrowser } from "./browser.mjs";
import * as C from "../lib/capture.ts";
import * as H from "../lib/sellerhybrid.ts";

const args = process.argv.slice(2);
const jsonAt = args.indexOf("--json");
const jsonFile = jsonAt >= 0 ? args.splice(jsonAt, 2)[1] : null;
const base = (args[0] ?? "http://localhost:3162").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const FILE = JSON.parse(fs.readFileSync(new URL("../data/seller/capture.json", import.meta.url), "utf-8"));
const HYBRID = JSON.parse(fs.readFileSync(new URL("../data/seller/hybrid.json", import.meta.url), "utf-8"));
const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(env("INTERNAL_COSTS_TOKEN") ?? "")}`, { redirect: "manual" });
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exit(1); }
const get = async (path) => { const r = await fetch(base + path, { headers: { Cookie: cookie }, redirect: "manual" }); return { status: r.status, html: await r.text() }; };
const face = (html) => { const i = html.indexOf("<h1"); return i < 0 ? "" : html.slice(i); };
const plain = (html) => html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ");
const two = (v) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const usdWords = (v) => v.toLocaleString("en-US");
const report = { hybrid: [], table: {}, profile: {} };

// (a) the hybrid
{
  let above = 0, cases = 0;
  for (const grid of ["ercot", "caiso"]) for (const fuel of ["solar", "wind"]) for (const dur of [2, 4, 8]) {
    const want = H.totals(H.daysOf(HYBRID.grids[grid], fuel, 100), 100, dur, 100);
    for (const strat of ["foresight", "dayahead"]) {
      const h = face((await get(`/cost-of-power/seller?iso=${grid}&asset=${fuel}&dur=${dur}&strat=${strat}`)).html);
      const raw2 = (k) => { const v = new RegExp(`data-hybrid2="${k}" data-raw="(-?[\\d.]+)"`).exec(h)?.[1]; return v === undefined ? null : Number(v); };
      const raw = (k) => { const v = new RegExp(`data-hybrid="${k}" data-raw="(-?[\\d.]+)"`).exec(h)?.[1]; return v === undefined ? null : Number(v); };
      const got = { plant: raw2("plant"), battery: raw2("battery"), pair: raw2("pair"), added: raw2("added") };
      const kept = { plant: raw("plant"), battery: raw("battery"), combined: raw("combined") };
      const same = got.plant === Math.round(want.plant) && got.battery === Math.round(want.battery) && got.pair === Math.round(want.pair) && got.added === Math.round(want.added);
      const ordered = got.pair !== null && got.pair >= got.plant && got.added >= got.pair && Math.abs(got.added - (got.plant + got.battery)) <= 1;
      const keptOk = kept.plant !== null && kept.battery !== null && kept.combined === C.combined(kept.plant, kept.battery);
      const isAbove = keptOk && got.pair > kept.combined;
      const marked = /data-hybrid-above="1"/.test(h);
      cases++;
      if (isAbove) above++;
      report.hybrid.push({ grid, fuel, dur, strat, ...got, kept, above: isAbove });
      check(same && ordered && keptOk && marked === isAbove && /Added, not co-optimized: upper bound/.test(plain(h)) && /an upper bound for a schedule made the day before/.test(h),
        `${grid} ${fuel}, 100 MW with a 100 MW ${dur}-hour battery, ${strat}: plant USD ${usdWords(got.plant ?? NaN)}, battery alone ${usdWords(got.battery ?? NaN)}, pair ${usdWords(got.pair ?? NaN)}, the two added ${usdWords(got.added ?? NaN)} (the library's); `
        + `kept row: ${usdWords(kept.plant ?? NaN)} + ${usdWords(kept.battery ?? NaN)} = ${usdWords(kept.combined ?? NaN)}${isAbove ? ", BELOW the pair, and the page says so" : ""}`);
    }
  }
  console.log(`     the co-optimized pair is above session 145's kept added figure in ${above} of ${cases} cases`);
  report.above = above; report.cases = cases;
  // other sizes: a battery half the plant's size, a plant that is not 100 MW
  const want = H.totals(H.daysOf(HYBRID.grids.ercot, "solar", 250), 80, 4, 250);
  const h = face((await get("/cost-of-power/seller?iso=ercot&asset=solar&mw=250&bmw=80&dur=4")).html);
  const raw2 = (k) => Number(new RegExp(`data-hybrid2="${k}" data-raw="(-?[\\d.]+)"`).exec(h)?.[1] ?? NaN);
  check(raw2("plant") === Math.round(want.plant) && raw2("pair") === Math.round(want.pair) && raw2("battery") === Math.round(want.battery),
    `ERCOT solar, 250 MW with an 80 MW 4-hour battery: plant USD ${usdWords(raw2("plant"))}, battery ${usdWords(raw2("battery"))}, pair ${usdWords(raw2("pair"))}, the library's for those sizes`);
  const hoverOk = /title="[^"]*Round trip 86 percent[^"]*"/.test(h) && /title="[^"]*percent of its charging came from the plant[^"]*"/.test(h) && /title="[^"]*never above this figure[^"]*"/.test(h) && /title="[^"]*not one measure[^"]*"/.test(h);
  check(hoverOk, "each hybrid figure carries its rules on hover: the round trip, the charging from the plant, the bound, and what the kept row holds");
  const ny = face((await get("/cost-of-power/seller?iso=nyiso&asset=wind")).html);
  check(/data-hybrid="none"[\s\S]{0,400}?not modeled for this grid/.test(ny) && !/data-hybrid2=/.test(ny), 'New York wind: "not modeled for this grid", and no pair');
  const pk = plain(face((await get("/cost-of-power/seller?asset=peaker")).html));
  check(/Your plant's profile\s+A year of your own plant's hourly output/.test(pk), "for a gas peaker the profile box points to solar");
}

// (b) the table by hub and year, as the server first draws it (day-ahead; the page's fuel)
const page = await get("/cost-of-power/seller?iso=ercot&asset=solar");
const html = face(page.html), text = plain(html);
const T = C.hubYears(FILE);
{
  let cells = 0, held = 0, wrong = 0, missing = 0, partial = 0;
  for (const r of T.rows) {
    const row = new RegExp(`<tr[^>]*data-hy-row="${`${r.grid}|${r.id}`.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}"[\\s\\S]*?</tr>`).exec(html)?.[0] ?? "";
    for (const y of T.years) {
      cells++;
      const c = r.cells.da.solar[y];
      const got = new RegExp(`data-hy="${`${r.id}|da|solar|${y}`.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}"[^>]*>([^<]*)<`).exec(row)?.[1] ?? null;
      if (c) { held++; if (!c.whole) partial++; if (got !== two(c.price)) wrong++; } else { missing++; if (got !== null) wrong++; }
    }
    if ((row.match(/data-missing="1"/g) ?? []).length < T.years.filter((y) => !r.cells.da.solar[y]).length) wrong++;
  }
  report.table = { hubs: T.rows.length, years: T.years, cells, held, notHeld: missing, partial };
  check(wrong === 0 && held > 0, `the capture price by hub and year (solar, day-ahead): ${T.rows.length} hubs by ${T.years.length} years (${T.years[0]} to ${T.years.at(-1)}), ${held} cells held (${partial} partial) equal the file's, ${missing} not held are placeholders with a reason`);
  for (const m of ["rt", "da"]) for (const f of ["solar", "wind"]) {
    const k = T.rows.reduce((a, r) => a + T.years.filter((y) => r.cells[m][f][y]).length, 0);
    report.table[`${m}_${f}`] = k;
  }
  check(/data-hy-blank="miso"[\s\S]{0,900}?paused while terms are reviewed/.test(html) && /data-hy-blank="pjm"[\s\S]{0,900}?licensed source needed/.test(html) && !/INDIANA|Indiana Hub|data-hy-row="(miso|pjm)/.test(html),
    'MISO is a row of words, "paused while terms are reviewed", PJM "licensed source needed", and no hub of either is in the table');
  check(["hub-years", "profile", "hybrid"].every((id) => html.includes(`<section id="${id}"`)) && text.includes("Capture price by hub and year") && text.includes("Your plant's profile")
    && text.includes("Computed on this device. Nothing you paste or upload is sent or stored."), "the three blocks are on the page, and the profile box says on its face that nothing is sent or stored");
  const noLabel = text.split("Added, not co-optimized: upper bound").join(" ");
  const words = /upper bound|merchant only|does not tell|how it is measured|how a lender|not a site|limitation|cannot see|assum/i;
  check(!words.test(noLabel) && !/\bundefined\b|NaN/.test(text) && !page.html.includes(String.fromCharCode(0x2014)), `no method prose on the face beyond the owner's label, no "undefined", no NaN, no em dash${words.test(noLabel) ? ` (found "${words.exec(noLabel)[0]}")` : ""}`);
}

const code = await withBrowser(async ({ go, evaluate, wait, unlock: open, requests, errors, sleep }) => {
  await open(base);
  await go(`${base}/cost-of-power/seller?iso=ercot&asset=solar`);
  await wait(`!!document.querySelector('[data-hub-years] [data-hy]') && !!document.querySelector('[data-profile="prices"]')`, 40000, "the table and the price file");
  // the table: the switch, the sort, the hover
  const cell = (id, m, f, y) => evaluate(`document.querySelector('[data-hy="${id}|${m}|${f}|${y}"]')?.textContent ?? null`);
  await evaluate(`document.querySelector('[data-hy-switch="fuel|wind"]').click()`);
  await evaluate(`document.querySelector('[data-hy-switch="prices|rt"]').click()`);
  await wait(`document.querySelector('[data-hub-years]').getAttribute('data-hy-fuel') === 'wind' && document.querySelector('[data-hub-years]').getAttribute('data-hy-market') === 'rt'`, 5000, "the switch");
  const west = T.rows.find((r) => r.id === "HB_WEST");
  check((await cell("HB_WEST", "rt", "wind", "2023")) === two(west.cells.rt.wind["2023"].price), `the switch to wind and real time redraws the table: West hub 2023, USD ${two(west.cells.rt.wind["2023"].price)} per MWh, the file's`);
  await evaluate(`document.querySelector('[data-hy-sort="2025"]').click()`);
  await sleep(300);
  const order = await evaluate(`[...document.querySelectorAll('[data-hy-row]')].map((tr) => { const c = tr.querySelector('[data-hy$="|2025"]'); return c ? Number(c.textContent.replace(/,/g, '')) : null; })`);
  const nums = order.filter((v) => v !== null);
  check(nums.length > 5 && nums.every((v, i) => i === 0 || nums[i - 1] >= v) && order.indexOf(null) === nums.length, `a click on 2025 sorts the hubs by it, highest first, the hubs without a figure last (${nums.length} with one; top ${nums[0]}, bottom ${nums.at(-1)})`);
  const tip = await evaluate(`document.querySelector('[data-hy="HB_WEST|rt|wind|2023"]').closest('td').getAttribute('title')`);
  check(/simple average over the same hours: [\d.]+/.test(tip) && /Capture ratio: [\d.]+ percent/.test(tip) && /Hours held: [\d,]+ of the year's 8,760/.test(tip) && /Generation: EIA-930/.test(tip) && /Prices: \w+/.test(tip),
    `a cell answers the mouse with the simple average, the capture ratio, the hours held and the source ("${tip.slice(0, 170)}")`);
  const missingTip = await evaluate(`document.querySelector('[data-hy-row="caiso|TH_SP15_GEN-APND"] [data-missing]')?.getAttribute('title') ?? ''`);
  check(/held from \d{4}-\d{2}-\d{2}/.test(missingTip), `a year not held answers the mouse with its reason ("${missingTip.slice(0, 140)}")`);

  // the profile: the price file was asked for on load, by a plain address
  const asked = requests.filter((r) => /\/seller\/prices\//.test(r.url));
  check(asked.length === 1 && /\/seller\/prices\/ercot_2025\.json$/.test(asked[0].url), `the box asked for one static file before any paste, by grid and year alone (${asked.map((r) => r.url.replace(base, "")).join(", ")})`);
  const PRICES = JSON.parse(fs.readFileSync(new URL("../public/seller/prices/ercot_2025.json", import.meta.url), "utf-8"));
  const setText = (js) => evaluate(`(() => { const el = document.querySelector('[data-profile="text"]'); const s = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set; s.call(el, ${js}); el.dispatchEvent(new Event('input', { bubbles: true })); })()`);
  // a test input, typed as a reader would: a day shape that rises and falls, 100 MW at noon, the same every day
  const shape = Array.from({ length: 8760 }, (_, i) => { const h = i % 24; return h >= 6 && h <= 18 ? Math.round(100 * Math.sin(((h - 6) / 12) * Math.PI) * 1000) / 1000 : 0; });
  await sleep(1500);
  const before = requests.length, address = await evaluate("location.href"), cookiesBefore = await evaluate("document.cookie"), stores = await evaluate("localStorage.length + sessionStorage.length");
  await setText(JSON.stringify(shape.join("\n")));
  await wait(`!!document.querySelector('[data-profile="result"]')`, 20000, "the profile's result");
  await sleep(2500);
  const attrs = await evaluate(`(() => { const el = document.querySelector('[data-profile="result"]'); return Object.fromEntries(['revenue', 'energy', 'capture', 'flat', 'pair', 'plant'].map((k) => [k, Number(el.getAttribute('data-profile-' + k))])); })()`);
  const want = H.profileResult(shape, PRICES.price, 100, 4);
  const sent = requests.slice(before);
  check(sent.length === 0, `after the paste no request leaves the page${sent.length ? ` (${sent.length}: ${sent[0].url.slice(0, 120)})` : ""}`);
  check((await evaluate("location.href")) === address && (await evaluate("document.cookie")) === cookiesBefore && (await evaluate("localStorage.length + sessionStorage.length")) === stores
    && await evaluate(`(() => { const all = JSON.stringify(Object.entries(localStorage)) + JSON.stringify(Object.entries(sessionStorage)) + document.cookie + location.href; return !all.includes('96.593') && !all.includes('70.711'); })()`),
    "the address, the cookies and local and session storage are as they were, and hold nothing of the profile");
  check(await evaluate(`(async () => { if (!('indexedDB' in window) || !indexedDB.databases) return true; return (await indexedDB.databases()).length === 0; })()`), "no database was opened in the browser");
  check(Math.abs(attrs.revenue - want.revenue) < 0.01 && Math.abs(attrs.capture - want.capture) < 1e-5 && Math.abs(attrs.pair - want.hybrid.pair) < 0.01 && Math.abs(attrs.plant - want.hybrid.plant) < 0.01,
    `the profile's figures are the library's on the same file: revenue USD ${usdWords(Math.round(attrs.revenue))}, capture price ${two(attrs.capture)} against a simple average of ${two(attrs.flat)} USD per MWh, the pair USD ${usdWords(Math.round(attrs.pair))} against the plant's ${usdWords(Math.round(attrs.plant))}`);
  check(Math.abs(attrs.capture * attrs.energy - attrs.revenue) < 1 && attrs.pair >= attrs.plant, "capture price times generation is the revenue (to a dollar, the price read to six decimals), and the pair is not below the plant");
  report.profile = { ...attrs, year: 2025, grid: "ercot" };
  const shown = await evaluate(`document.querySelector('[data-profile="result"]').innerText`);
  check(/Capture price/.test(shown) && /Co-optimized pair, one interconnection/.test(shown) && /Added, not co-optimized: upper bound/.test(shown) && /Battery alone, 100 MW, 4-hour/.test(shown), "the result shows revenue, the capture price, the plant, the battery alone, the pair and the two added");
  check(await evaluate(`!document.querySelector('[data-profile="box"] [name]') && !document.querySelector('[data-profile="box"]').closest('form')`), "the box's fields have no name and stand in no form");
  // a flat profile captures the simple average
  await setText(JSON.stringify(Array.from({ length: 8760 }, () => "1").join("\n")));
  await sleep(1500);
  const flat = await evaluate(`(() => { const el = document.querySelector('[data-profile="result"]'); return el ? [Number(el.getAttribute('data-profile-capture')), Number(el.getAttribute('data-profile-flat'))] : null; })()`);
  check(flat !== null && Math.abs(flat[0] - flat[1]) < 1e-6, `a plant that generates the same in every hour captures the simple average exactly (${flat?.[0]} and ${flat?.[1]})`);
  // refused, never repaired
  for (const [what, js, re] of [
    ["8,759 values", JSON.stringify(Array.from({ length: 8759 }, () => "1").join("\n")), /8,759 values were read and 2025 has 8,760 hours/],
    ["a value below zero", JSON.stringify(["1", "-2", ...Array.from({ length: 8758 }, () => "1")].join("\n")), /Line 2 is below zero/],
    ["a gap", JSON.stringify(["1", "", ...Array.from({ length: 8758 }, () => "1")].join("\n")), /Line 2 is empty: a gap/],
    ["a value that is not a number", JSON.stringify(["1", "n/a", ...Array.from({ length: 8758 }, () => "1")].join("\n")), /Line 2 is not a number/],
  ]) {
    await setText(js);
    await sleep(700);
    const said = await evaluate(`[document.querySelector('[data-profile="refused"]')?.innerText ?? '', !!document.querySelector('[data-profile="result"]')]`);
    check(re.test(said[0]) && said[1] === false, `${what} is refused with a plain sentence and no figure ("${said[0].slice(0, 110)}")`);
  }
  check(requests.slice(before).length === 0, "none of the pastes made a request");
  check(errors.length === 0, `no script error on the page${errors.length ? `: ${errors[0].slice(0, 160)}` : ""}`);
  return 0;
});
if (code === null) console.log("note: no Chrome or Edge on this machine; the browser checks were not run");
if (jsonFile) fs.writeFileSync(jsonFile, JSON.stringify(report, null, 1));
console.log(bad ? `${bad} of ${n} failed` : `all ${n} passed`);
process.exit(bad ? 1 : 0);
