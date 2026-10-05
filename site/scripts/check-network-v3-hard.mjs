// Energy Research Warehouse (ERW) site, session 124: the network, version 3, through its hardest days, at a phone's
// width and on a slowed machine, in a real browser.
//
//   npm run build && npx next start -p 3049
//   node scripts/check-network-v3-hard.mjs [base-url] [out.json]      (default http://localhost:3049)
//
// No model call; the only requests are to the site under test. Four parts:
//   1. the live week opens on the newest hour every reporting pair holds, and the page says which hour;
//   2. the replay's hardest days: the first day, a leap day, the two days the clocks change, the peak of Winter Storm
//      Uri and of the January 2024 storm, a day and a year's last day for which EIA's file is blank, the replay's last
//      day; three years asked for in a row without waiting; a year played across the blank weeks of late 2025. On each:
//      the day is shown, the page says so when it holds few pairs or none, and nothing throws;
//   3. the trace on Texas during Uri (its month, the day; nothing through Mexico) and on a blank day; MISO's price;
//   4. a phone's width (390 px): nothing wider than the screen, the panel under the network; and the frame time with
//      the processor slowed four and six times (DevTools CPU throttling), in the live week, a story and the replay.
// The frame times are a headless browser's, drawing with software (no graphics card): they are the slow end, not a
// phone's own figure. Exit 1 on a failure; "not proven" (exit 0) without a browser.
import fs from "node:fs";
import { withBrowser } from "./browser.mjs";
import { PAUSED_PRICE, completeHour } from "../lib/networkV3.ts";

const base = (process.argv[2] ?? "http://localhost:3049").replace(/\/$/, "");
const outFile = process.argv[3] ?? null;
let bad = 0, n = 0;
const out = { base, at: new Date().toISOString(), checks: [], frames: [], load: {} };
const check = (ok, what) => { n += 1; out.checks.push({ ok: !!ok, what }); if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const year = (y) => JSON.parse(fs.readFileSync(new URL(`../public/network/daily_${y}.json`, import.meta.url), "utf-8"));
const index = JSON.parse(fs.readFileSync(new URL("../public/network/daily_index.json", import.meta.url), "utf-8"));
const VIEW = `(() => { const d = document.querySelector('[data-network-view]'); return d ? { view: d.getAttribute('data-network-view'), t: d.getAttribute('data-t'), playing: d.getAttribute('data-playing'),
  thin: document.querySelector('[data-thin-day]')?.getAttribute('data-thin-day') ?? null, text: d.innerText } : null; })()`;
const LINKS = `(() => { const g = document.querySelector('[aria-label^="A 3D network"]')?.__erwGraph; return g ? g.graphData().links.length : null; })()`;
const setDate = (v) => `(() => { const el = document.querySelector('#replay-day'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(el, '${v}');
  el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); return true; })()`;
const click = (sel) => `(() => { const b = ${sel}; if (!b) return false; b.click(); return true; })()`;
const button = (text) => `[...document.querySelectorAll('button')].find((b) => b.innerText.trim().startsWith(${JSON.stringify(text)}))`;
const pick = (id) => `(() => { const sel = document.querySelector('select'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value').set.call(sel, '${id}'); sel.dispatchEvent(new Event('change', { bubbles: true })); return true; })()`;
// requestAnimationFrame intervals over a while, in ms
const FRAMES = (ms) => `new Promise((resolve) => { const t = []; let last = performance.now(); const t0 = last; const f = (now) => { t.push(now - last); last = now; if (now - t0 < ${ms}) requestAnimationFrame(f); else resolve(t); }; requestAnimationFrame(f); })`;
const stats = (t) => { const s = [...t].sort((a, b) => a - b); const q = (p) => s[Math.min(s.length - 1, Math.floor(p * s.length))];
  return { frames: t.length, per_second: Math.round((10 * 1000 * t.length) / t.reduce((a, b) => a + b, 0)) / 10, median_ms: Math.round(q(0.5) * 10) / 10, p95_ms: Math.round(q(0.95) * 10) / 10, longest_ms: Math.round(s[s.length - 1]) }; };

const code = await withBrowser(async ({ go, evaluate, wait, unlock, sleep, errors, send }) => {
  await unlock(base);
  const t0 = Date.now();
  await go(`${base}/network/v3`);
  await wait(`document.querySelector('[data-network-view]')?.getAttribute('data-restored') === '1' && !!document.querySelector('[aria-label^="A 3D network"]')?.__erwGraph`, 30000, "the network");
  out.load.to_network_ms = Date.now() - t0;

  // 1. the newest complete hour
  const snap = await evaluate(`fetch('/network/v3', { headers: { RSC: '0' } }).then(() => null)`).catch(() => null);
  void snap;
  const said = await evaluate(`({ line: document.querySelector('[data-newest-complete]')?.getAttribute('data-newest-complete') ?? null, opens: document.querySelector('[data-complete-hour]')?.getAttribute('data-complete-hour') ?? null,
    t: document.querySelector('[data-network-view]').getAttribute('data-t'), text: document.querySelector('[data-newest-complete]')?.innerText ?? '', silent: document.querySelector('[data-silent-pairs]')?.innerText ?? '' })`);
  check(!!said.line && said.line === said.opens && said.t === said.line, `the live week opens on the newest complete hour, and the page names it twice the same: ${said.line}`);
  check(/Newest hour complete for every reporting pair: \d{4}-\d{2}-\d{2} \d{2}:00 UTC \(\d+ of the week's \d+ pairs report/.test(said.text), `the line says which hour and how many pairs: "${said.text.slice(0, 150)}"`);
  const committed = JSON.parse(fs.readFileSync(new URL("../data/grid_network.json", import.meta.url), "utf-8"));
  const c0 = completeHour(committed.hours, committed.links);
  console.log(`     (the committed week, for reference: complete at ${c0.hour}, ${c0.reporting} of ${c0.pairs} pairs reporting, ${c0.silent.length} silent)`);
  out.complete = { page: said.line, silent_words: said.silent };

  // 2. the hardest days
  const DAYS = [["2019-01-01", "the first day of the replay"], ["2020-02-29", "a leap day"], ["2021-03-14", "a 23-hour day"], ["2021-11-07", "a 25-hour day"], ["2021-02-15", "the peak of Winter Storm Uri"],
    ["2024-01-14", "the January 2024 storm"], ["2025-11-20", "a day EIA's file is blank for"], ["2025-12-31", "a year's last day, blank"], [index.last, "the replay's last day"]];
  const cache = {};
  for (const [day, what] of DAYS) {
    const before = errors.length;
    await evaluate(setDate(day));
    let v = null;
    try { v = await wait(`(() => { const v = ${VIEW}; return v && v.t === '${day}' ? v : null; })()`, 30000, day); } catch { /* reported below */ }
    await sleep(700);
    const y = (cache[day.slice(0, 4)] ??= year(day.slice(0, 4)));
    const i = y.days.indexOf(day), held = y.pairs_held[i], usual = y.pairs_usual;
    const links = await evaluate(LINKS);
    const thin = await evaluate(`document.querySelector('[data-thin-day]')?.getAttribute('data-thin-day') ?? null`);
    const wantThin = held < 0.5 * usual ? `${held}/${usual}` : null;
    const moving = y.links.filter((l) => l.mw[i] !== null && l.mw[i] !== 0).length;   // a tie at exactly zero is held and has nothing to draw
    check(!!v && errors.length === before && thin === wantThin && links === moving,
      `${day}, ${what}: shown, ${links} flows drawn (the file holds ${held} pairs that day, ${held - moving} of them at zero); ${wantThin ? `the page says it holds ${held} of the usual ${usual}` : "no warning, as it holds its pairs"}${errors.length > before ? `; ERRORS: ${errors.slice(before).join(" | ").slice(0, 200)}` : ""}`);
  }
  // three years asked for without waiting: the last one asked for is the one shown
  await evaluate(`(() => { ${["2019-06-01", "2023-06-01", "2022-06-01"].map((d) => `(${setDate(d)})`).join("; ")}; return true; })()`);
  let last = null;
  try { last = await wait(`(() => { const v = ${VIEW}; return v && v.t === '2022-06-01' ? v : null; })()`, 40000, "the last day asked for"); } catch { /* below */ }
  await sleep(2500);
  const settled = await evaluate(VIEW);
  check(!!last && settled.t === "2022-06-01", `three years asked for in a row: the last one asked for is shown (${settled?.t})`);
  // a year played across the blank weeks
  await evaluate(setDate("2025-11-01"));
  await wait(`(() => { const v = ${VIEW}; return v && v.t === '2025-11-01'; })()`, 30000, "1 November 2025");
  const e0 = errors.length;
  await evaluate(click(button("Play the year")));
  await sleep(9000);
  const played = await evaluate(VIEW);
  await evaluate(click(button("Pause")));
  check(played.t > "2025-11-10" && errors.length === e0, `played from 1 November 2025 across the blank weeks to ${played.t} with no error${played.thin ? ` (the day shown holds ${played.thin} pairs and says so)` : ""}`);

  // 3. the trace on Texas during Uri, and on a blank day; MISO
  await evaluate(setDate("2021-02-15"));
  await wait(`(() => { const v = ${VIEW}; return v && v.t === '2021-02-15'; })()`, 30000);
  await evaluate(pick("ERCO"));
  await wait(`document.querySelector('[data-panel]')?.getAttribute('data-panel') === 'ERCO'`);
  if (await evaluate(`document.querySelector('[data-trace]')?.getAttribute('data-trace') === 'off'`)) await evaluate(click(button("Trace the power")));
  await wait(`!!document.querySelector('[data-trace-supplier]')`, 10000, "the trace");
  const TR = `({ period: document.querySelector('[data-trace-period]')?.getAttribute('data-trace-period'), frames: document.querySelector('[data-trace-frames]')?.getAttribute('data-trace-frames'),
    rows: [...document.querySelectorAll('[data-trace-supplier]')].map((li) => ({ id: li.getAttribute('data-trace-supplier'), text: li.querySelector('span').innerText, island: !!li.querySelector('[data-trace-island]'), via: li.querySelectorAll('[data-trace-via]').length })),
    head: document.querySelector('[data-trace-frames]')?.innerText ?? '' })`;
  const feb = await evaluate(TR);
  const cen = feb.rows.find((r) => r.id === "CEN"), swpp = feb.rows.find((r) => r.id === "SWPP");
  check(feb.period === "month" && feb.frames === "28/28" && !!swpp && !!cen && feb.rows.length === 2, `Texas, February 2021: over its month, 28 of 28 days, supplied by ${feb.rows.map((r) => r.text.replace(/\s+/g, " ")).join(" and ")}`);
  check(!!cen && cen.island && cen.via === 0 && !!swpp && swpp.via > 0, "nothing is traced through Mexico; SPP's own suppliers are listed");
  await evaluate(click(button("this day")));
  await wait(`document.querySelector('[data-trace-period]')?.getAttribute('data-trace-period') === 'day'`);
  const one = await evaluate(TR);
  check(one.frames === "1/1" && /On 2021-02-15/.test(one.head), `the trace of the one day: ${one.head.replace(/\s+/g, " ").slice(0, 90)}`);
  await evaluate(setDate("2025-11-20"));
  await wait(`(() => { const v = ${VIEW}; return v && v.t === '2025-11-20'; })()`, 30000);
  await sleep(500);
  const blank = await evaluate(`({ frames: document.querySelector('[data-trace-frames]')?.getAttribute('data-trace-frames'), text: document.querySelector('[data-trace]')?.innerText ?? '' })`);
  check(blank.frames === "0/1" && /No neighbour supplied it on net over this period/.test(blank.text) && /0 of its 1 days hold a flow/.test(blank.text.replace(/\s+/g, " ")), "on a blank day the trace says no day of the period holds a flow, and lists nobody");
  await evaluate(click(button("its month")));
  await wait(`document.querySelector('[data-trace-period]')?.getAttribute('data-trace-period') === 'month'`);
  const nov = await evaluate(`document.querySelector('[data-trace-frames]')?.getAttribute('data-trace-frames')`);
  const y25 = year(2025);
  const novHeld = y25.days.map((d, i) => (d.startsWith("2025-11") && y25.links.some((l) => (l.a === "ERCO" || l.b === "ERCO") && l.mw[i] !== null) ? 1 : 0)).reduce((a, b) => a + b, 0);
  check(nov === `${novHeld}/30`, `November 2025 for Texas: the trace says ${nov} days hold a flow (the file: ${novHeld} of 30)`);
  // MISO: no price, in words; no ring
  await evaluate(click(button("Live now")));
  await wait(`document.querySelector('[data-network-view]')?.getAttribute('data-network-view') === 'live'`);
  await evaluate(click(button("Pause")));
  await evaluate(pick("MISO"));
  await wait(`document.querySelector('[data-panel]')?.getAttribute('data-panel') === 'MISO'`);
  const miso = await evaluate(`({ paused: document.querySelector('[data-price-paused]')?.innerText ?? null, panel: document.querySelector('[data-panel]').innerText })`);
  check(miso.paused === PAUSED_PRICE.MISO && !/Hub price this hour\s+[\d,.]+ USD\/MWh/.test(miso.panel), `MISO's panel shows no price and says why: "${(miso.paused ?? "").slice(0, 70)}..."`);
  check(await evaluate(`document.body.textContent.includes('MISO has no ring: it is paused.')`), "the page's fold says MISO is paused, in words");

  // 4a. a phone's width
  await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
  await go(`${base}/network/v3?grid=CISO`);
  await wait(`document.querySelector('[data-network-view]')?.getAttribute('data-restored') === '1' && !!document.querySelector('[data-panel]')`, 30000, "the page at a phone's width");
  await sleep(2500);
  const phone = await evaluate(`(() => { const c = document.querySelector('[aria-label^="A 3D network"]').getBoundingClientRect(), p = document.querySelector('[data-panel]').getBoundingClientRect(), d = document.querySelector('#replay-day').getBoundingClientRect();
    const wide = [...document.querySelectorAll('body *')].filter((e) => e.getBoundingClientRect().right > window.innerWidth + 1 && !e.closest('.overflow-x-auto') && getComputedStyle(e).position !== 'fixed').length;
    return { scroll: document.documentElement.scrollWidth, client: document.documentElement.clientWidth, canvasW: Math.round(c.width), canvasBottom: Math.round(c.bottom), panelTop: Math.round(p.top), dateRight: Math.round(d.right), wide }; })()`);
  check(phone.scroll <= phone.client && phone.wide === 0, `at 390 px the page is no wider than the screen (${phone.scroll} in ${phone.client}); ${phone.wide} elements stick out`);
  check(phone.panelTop >= phone.canvasBottom - 1 && phone.canvasW <= 390 && phone.dateRight <= 390, `the panel is under the network (canvas ${phone.canvasW} px wide, ends at ${phone.canvasBottom}; panel starts at ${phone.panelTop}); the date picker fits`);
  const shot = await send("Page.captureScreenshot", { format: "png" });
  fs.mkdirSync(new URL("../../runs/session124/", import.meta.url), { recursive: true });
  fs.writeFileSync(new URL("../../runs/session124/v3_phone_390.png", import.meta.url), Buffer.from(shot.data, "base64"));
  out.phone = phone;

  // 4b. frame times, the processor slowed
  const measure = async (rate, name, prepare) => {
    await send("Emulation.setCPUThrottlingRate", { rate });
    const t1 = Date.now();
    await prepare();
    const ready = Date.now() - t1;
    await sleep(1500);
    const s = stats(await evaluate(FRAMES(6000)));
    out.frames.push({ width: 390, cpu_slowed: rate, view: name, ready_ms: ready, ...s });
    console.log(`     390 px, processor slowed ${rate}x, ${name}: ready in ${ready} ms; ${s.per_second} frames a second, median ${s.median_ms} ms, 95th percentile ${s.p95_ms} ms, longest ${s.longest_ms} ms`);
    return s;
  };
  for (const rate of [1, 4, 6]) {
    await measure(rate, "the live week, turning", async () => { await evaluate(click(button("Live now"))); await evaluate(click(button("Pause"))); await sleep(300); });
    await measure(rate, "the replay, playing 2021", async () => { await evaluate(setDate("2021-01-01")); await wait(`(() => { const v = ${VIEW}; return v && v.view === 'day' && v.t.startsWith('2021'); })()`, 60000, "2021"); await evaluate(click(button("Play the year"))); });
    await evaluate(click(button("Pause")));
    await measure(rate, "Texas during Uri, playing", async () => { await evaluate(click(button("Texas during Uri"))); await wait(`document.querySelector('[data-network-view]')?.getAttribute('data-network-view') === 'uri_2021'`, 60000, "the story"); });
    await evaluate(click(button("Pause")));
  }
  await send("Emulation.setCPUThrottlingRate", { rate: 1 });
  const slowest = out.frames.filter((f) => f.cpu_slowed === 6).reduce((a, f) => Math.min(a, f.per_second), Infinity);
  check(out.frames.length === 9 && out.frames.every((f) => f.frames > 5), `frames were drawn in every view at every speed; the slowest, with the processor slowed six times, ${slowest} a second`);
  check(errors.length === 0, `no error in the page through all of it${errors.length ? `: ${errors.join(" | ").slice(0, 300)}` : ""}`);
  return bad ? 1 : 0;
}, { width: 1280, height: 900 });
if (code === null) { console.log("not proven here: no browser on this machine"); process.exit(0); }
if (outFile) fs.writeFileSync(outFile, JSON.stringify(out, null, 1) + "\n");
console.log(bad ? `${bad} of ${n} failed` : `the network, version 3, through its hardest days: ${n} checks pass`);
process.exit(code);
