// Energy Research Warehouse (ERW) site, session 93: the network, version 3, in a real browser.
//
//   npm run build && npx next start -p 3093
//   node scripts/check-network-v3.mjs [base-url]      (default http://localhost:3093)
//
// One check per addition, on /network/v3 (in review, so in the internal view), and one that the live page is as it was:
//   a  replay    the date picker loads a day of 2021 from the year's file; the frame is a day; "Play the year" plays
//                and the day advances; the panel's net imports of that day equal the file's own arithmetic
//   b  address   the address holds the view, the day, the grid and the switches; opening that address again restores
//                the same view (not playing); an address it does not understand opens the page as it opens by default
//   c  prices    off by default with no ring; on, a ring on each grid with a public price held for the day, the count the
//                file gives; the panel gains the period's range; PJM never has one
//   d  trace     the panel lists the grid's suppliers and their suppliers with shares that sum to 100, equal to
//                lib/networkV3.ts's trace over the same links, and says physical flows, not contracts
//   live         /network holds no date picker, no Prices switch, no trace, and leaves its address alone
// Exit 1 on a failure; "not proven" (exit 0) without a browser, or where the browser cannot draw 3D.
import fs from "node:fs";
import { withBrowser } from "./browser.mjs";
import { easternHours, trace, PAUSED_PRICE } from "../lib/networkV3.ts";

const base = (process.argv[2] ?? "http://localhost:3093").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const year = (y) => JSON.parse(fs.readFileSync(new URL(`../public/network/daily_${y}.json`, import.meta.url), "utf-8"));
const STATE = `(() => { const d = document.querySelector('[data-network-view]'); return d ? { view: d.getAttribute('data-network-view'), frame: d.getAttribute('data-frame'), t: d.getAttribute('data-t'),
  playing: d.getAttribute('data-playing'), rings: Number(d.getAttribute('data-price-rings')), frames: Number(d.getAttribute('data-frames')), restored: d.getAttribute('data-restored'),
  panel: document.querySelector('[data-panel]')?.getAttribute('data-panel') ?? null, search: window.location.search } : null; })()`;
const setDate = (v) => `(() => { const el = document.querySelector('#replay-day'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(el, '${v}');
  el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); return true; })()`;
const click = (sel) => `(() => { const b = ${sel}; if (!b) return false; b.click(); return true; })()`;
const button = (text) => `[...document.querySelectorAll('button')].find((b) => b.innerText.trim().startsWith(${JSON.stringify(text)}))`;
const num = (s) => Number(String(s).replace(/,/g, ""));

const code = await withBrowser(async ({ go, evaluate, wait, unlock, sleep, errors, send }) => {
  await unlock(base);
  await go(`${base}/network/v3`);
  await wait(`!!document.querySelector('[data-network-view][data-restored="1"]')`, 20000, "the page to be ready");
  if (await evaluate(`document.body.innerText.includes('This browser cannot draw 3D')`)) { console.log("check-network-v3: NOT PROVEN: this browser cannot draw 3D (WebGL)"); return null; }
  await wait(`!!document.querySelector('canvas')`, 30000, "the network's canvas");
  let s = await evaluate(STATE);
  check(s.view === "live" && s.frame === "hour" && s.rings === 0 && s.search === "" && s.panel === null, `the page opens as the live week, prices off, nothing selected, a bare address (${JSON.stringify(s)})`);
  check(await evaluate(`${button("Prices: off")} !== undefined && !!document.querySelector('#replay-day') && ${button("Play the year")} !== undefined`), "version 3's controls are there: a date picker, Play the year, a Prices switch");

  // a. the replay
  const y21 = year(2021);
  await evaluate(setDate("2021-02-15"));
  s = await wait(`(() => { const s = ${STATE}; return s.view === 'day' && s.t === '2021-02-15' ? s : null; })()`, 20000, "the day 2021-02-15 to load");
  check(s.frame === "day" && s.frames === y21.days.length && s.playing === "0", `a day of 2021 is shown, a frame per day, ${s.frames} days, not playing`);
  check(await evaluate(`document.body.innerText.includes("2021-02-15, EIA's Eastern day")`), "the moment reads as a day, EIA's Eastern day");
  await evaluate(`(() => { const sel = document.querySelector('select'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value').set.call(sel, 'ERCO'); sel.dispatchEvent(new Event('change', { bubbles: true })); return true; })()`);
  await wait(`document.querySelector('[data-panel]')?.getAttribute('data-panel') === 'ERCO'`, 10000, "ERCOT's panel");
  const i = y21.days.indexOf("2021-02-15");
  const net = y21.links.filter((l) => l.a === "ERCO" || l.b === "ERCO").reduce((a, l) => (l.mw[i] === null ? a : a + (l.b === "ERCO" ? l.mw[i] : -l.mw[i])), 0);
  const panel = await evaluate(`document.querySelector('[data-panel]').innerText`);
  const shownNet = panel.match(/Net (imports|exports) this day\s+([\d,]+) MW on average/);
  check(!!shownNet && num(shownNet[2]) === Math.abs(Math.round(net)) && (shownNet[1] === "imports") === (net >= 0), `the panel's net ${shownNet?.[1]} of the day, ${shownNet?.[2]} MW on average, is the file's (${net.toFixed(1)})`);
  // session 109: the replay now holds each day's demand (EIA's daily demand, the day's average MW), so the panel gives
  // the net imports as a share of it and each supplier's share
  const dem = y21.demand?.ERCO?.[i] ?? null;
  check(dem !== null && dem > 0, `the year's file holds ERCOT's demand of the day (${dem} MW on average)`);
  const pct1 = (v) => (v >= 10 ? v.toFixed(0) : v.toFixed(1));
  const wantShare = dem ? (Math.abs(net) / dem) * 100 : NaN;
  const shownShare = panel.match(/MW on average,\s*([\d.]+) percent of its ([\d,]+) MW demand/);
  check(!!shownShare && Math.abs(Number(shownShare[1]) - wantShare) < 0.06 + wantShare * 0.01 && num(shownShare[2]) === Math.round(dem),
    `the panel gives the net ${shownNet?.[1]} as a share of the day's demand: ${shownShare?.[1]} percent of ${shownShare?.[2]} MW (the file: ${wantShare.toFixed(2)} percent of ${dem})`);
  check(!panel.includes("its demand for this day is not held"), "the panel no longer says the day's demand is not held");
  const ties21 = y21.links.filter((l) => (l.a === "ERCO" || l.b === "ERCO") && l.mw[i] !== null && Math.round(l.mw[i]) !== 0).map((l) => ({ other: l.a === "ERCO" ? l.b : l.a, mw: Math.abs(l.mw[i]) }));
  const tieShares = await evaluate(`Object.fromEntries([...document.querySelectorAll('[data-tie-share]')].map((e) => [e.getAttribute('data-tie-share'), e.innerText]))`);
  check(ties21.length > 0 && ties21.every((t) => { const m = (tieShares[t.other] ?? "").match(/([\d.]+)% of demand/); return !!m && Math.abs(Number(m[1]) - (t.mw / dem) * 100) < 0.06; }),
    `each supplier's share of the day's demand is its flow over the demand: ${ties21.map((t) => `${t.other} ${tieShares[t.other]?.replace(/^, /, "")} (the file: ${((t.mw / dem) * 100).toFixed(2)})`).join("; ")}`);
  // a day whose demand is not held, or was screened out, gives no share: the first such day of the year for a grid with ties
  const gap = (() => { for (const [ba, arr] of Object.entries(y21.demand ?? {})) { const k = arr.findIndex((v, j) => v === null && y21.links.some((l) => (l.a === ba || l.b === ba) && l.mw[j] !== null)); if (k >= 0) return { ba, day: y21.days[k] }; } return null; })();
  if (gap) {
    await evaluate(setDate(gap.day));
    await wait(`(() => { const s = ${STATE}; return s.view === 'day' && s.t === '${gap.day}' ? s : null; })()`, 20000, `the day ${gap.day} to load`);
    await evaluate(`(() => { const sel = document.querySelector('select'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value').set.call(sel, '${gap.ba}'); sel.dispatchEvent(new Event('change', { bubbles: true })); return true; })()`);
    await wait(`document.querySelector('[data-panel]')?.getAttribute('data-panel') === '${gap.ba}'`, 10000, `${gap.ba}'s panel`);
    const p2 = await evaluate(`document.querySelector('[data-panel]').innerText`);
    check(p2.includes("its demand for this day is not held") && !(await evaluate(`!!document.querySelector('[data-tie-share]')`)), `a day whose demand is not used gives no share (${gap.ba}, ${gap.day})`);
    await evaluate(setDate("2021-02-15"));
    await wait(`(() => { const s = ${STATE}; return s.view === 'day' && s.t === '2021-02-15' ? s : null; })()`, 20000, "the day 2021-02-15 again");
    await evaluate(`(() => { const sel = document.querySelector('select'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value').set.call(sel, 'ERCO'); sel.dispatchEvent(new Event('change', { bubbles: true })); return true; })()`);
    await wait(`document.querySelector('[data-panel]')?.getAttribute('data-panel') === 'ERCO'`, 10000, "ERCOT's panel again");
  } else {
    console.log("note: every day of 2021 with a tie holds its demand; the no-share case is not exercised");
  }
  await evaluate(click(button("Play the year")));
  await wait(`document.querySelector('[data-network-view]').getAttribute('data-playing') === '1'`, 5000, "the year to play");
  await sleep(1500);
  const moved = await evaluate(STATE);
  check(moved.playing === "1" && moved.t > "2021-02-15" && moved.t.startsWith("2021-"), `Play the year plays: the day moved on to ${moved.t}`);
  await evaluate(click(button("Pause")));
  await wait(`document.querySelector('[data-network-view]').getAttribute('data-playing') === '0'`);

  // c. prices
  await evaluate(setDate("2021-02-15"));
  await wait(`document.querySelector('[data-network-view]').getAttribute('data-t') === '2021-02-15'`);
  check((await evaluate(STATE)).rings === 0 && !(await evaluate(`!!document.querySelector('[data-price-legend]')`)), "prices are off by default: no ring, no legend");
  await evaluate(click(button("Prices: off")));
  s = await wait(`(() => { const s = ${STATE}; return s.rings > 0 ? s : null; })()`, 10000, "the price rings");
  const priced = Object.keys(y21.hub_prices).filter((b) => y21.hub_prices[b][i] !== null && b !== "PJM");
  check(s.rings === priced.length && priced.includes("ERCO"), `with prices on, a ring on each grid with a public price held that day: ${s.rings} (the file: ${priced.join(", ")})`);
  const p2 = await evaluate(`document.querySelector('[data-panel]').innerText`);
  const price = p2.match(/Hub price this day\s+([\d,.]+) USD\/MWh/);
  check(!!price && Math.abs(num(price[1]) - y21.hub_prices.ERCO[i]) < 0.006 && /Over the period shown: [\d,.-]+ to [\d,.]+ USD\/MWh/.test(p2), `the panel gives ERCOT's price of the day, ${price?.[1]} USD/MWh (the file: ${y21.hub_prices.ERCO[i]}), and the period's range`);
  check(await evaluate(`!!document.querySelector('[data-price-legend]')`), "the legend explains the outer ring");
  // the rings are in the 3D scene itself, one mesh each, and the batteries' ring is another kind of object
  const RINGS = `(() => { const g = document.querySelector('[aria-label^="A 3D network"]').__erwGraph; let rings = 0, spheres = 0; g.scene().traverse((o) => { if (o.userData && o.userData.priceRing) rings += 1; if (o.geometry && o.geometry.type === 'SphereGeometry') spheres += 1; }); return { rings, spheres }; })()`;
  const scene = await wait(`(() => { const s = ${RINGS}; return s.rings > 0 ? s : null; })()`, 10000, "the rings in the scene");
  check(scene.rings === priced.length && scene.spheres >= 60, `the scene holds ${scene.rings} price ring(s) among ${scene.spheres} spheres`);
  await evaluate(setDate("2025-07-15"));
  await wait(`document.querySelector('[data-network-view]').getAttribute('data-t') === '2025-07-15'`, 20000, "a day of 2025");
  const y25 = year(2025), j = y25.days.indexOf("2025-07-15");
  // session 124: a paused publisher's hub (MISO) has no ring on this page, though the file still holds its price
  const priced25 = Object.keys(y25.hub_prices).filter((b) => y25.hub_prices[b][j] !== null && b !== "PJM" && !PAUSED_PRICE[b]);
  const scene25 = await wait(`(() => { const s = ${RINGS}; return s.rings === ${priced25.length} ? s : null; })()`, 10000, "the rings of a day of 2025");
  check(scene25.rings === priced25.length && priced25.length >= 5, `a day of 2025 has a ring on ${scene25.rings} grids (${priced25.join(", ")})`);
  const shot = await send("Page.captureScreenshot", { format: "png" });
  fs.mkdirSync(new URL("../../runs/session93/", import.meta.url), { recursive: true });
  fs.writeFileSync(new URL("../../runs/session93/v3_prices_2025-07-15.png", import.meta.url), Buffer.from(shot.data, "base64"));
  await evaluate(setDate("2021-02-15"));
  await wait(`document.querySelector('[data-network-view]').getAttribute('data-t') === '2021-02-15'`, 20000);
  await evaluate(`(() => { const sel = document.querySelector('select'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value').set.call(sel, 'PJM'); sel.dispatchEvent(new Event('change', { bubbles: true })); return true; })()`);
  await wait(`document.querySelector('[data-panel]')?.getAttribute('data-panel') === 'PJM'`);
  check((await evaluate(`document.querySelector('[data-panel]').innerText`)).includes("Not shown: PJM's prices are licensed") && !("PJM" in y21.hub_prices), "PJM has no price and no ring: its prices are licensed");

  // d. trace the power
  await evaluate(`(() => { const sel = document.querySelector('select'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value').set.call(sel, 'CISO'); sel.dispatchEvent(new Event('change', { bubbles: true })); return true; })()`);
  await wait(`document.querySelector('[data-panel]')?.getAttribute('data-panel') === 'CISO'`);
  check(await evaluate(`document.querySelector('[data-trace]')?.getAttribute('data-trace') === 'off' && !document.querySelector('[data-trace-supplier]')`), "the trace is closed until asked for");
  await evaluate(click(button("Trace the power")));
  await wait(`!!document.querySelector('[data-trace-supplier]')`, 10000, "the traced suppliers");
  // session 124: in the replay the trace opens on the month of the day shown; the year is one press away
  check(await evaluate(`document.querySelector('[data-trace-period]')?.getAttribute('data-trace-period') === 'month'`), "in the replay the trace opens on the month of the day shown");
  await evaluate(click(button("the year")));
  await wait(`document.querySelector('[data-trace-period]')?.getAttribute('data-trace-period') === 'view'`, 5000, "the trace over the year");
  const want = trace(y21.links, 0, y21.days.length, "CISO", (h) => easternHours(y21.days[h]));
  const got = await evaluate(`[...document.querySelectorAll('[data-trace-supplier]')].map((li) => ({ id: li.getAttribute('data-trace-supplier'), text: li.querySelector('span').innerText, via: [...li.querySelectorAll('[data-trace-via]')].map((v) => v.getAttribute('data-trace-via')) }))`);
  const shares = got.map((g) => num(g.text.match(/: ([\d.]+) percent/)[1]));
  check(JSON.stringify(got.map((g) => g.id)) === JSON.stringify(want.rows.map((r) => r.id)) && got.length >= 2, `CAISO's suppliers over 2021, largest first: ${got.map((g) => g.id).join(", ")}`);
  check(Math.abs(shares.reduce((a, b) => a + b, 0) - 100) < 0.06 && shares.every((v, k) => Math.abs(v - want.rows[k].share) < 0.006), `their shares sum to 100 and equal the model's (${shares.join(", ")})`);
  check(got.every((g, k) => JSON.stringify(g.via) === JSON.stringify(want.rows[k].via.map((v) => v.id))) && got.some((g) => g.via.length > 0) && got.every((g) => !g.via.includes("CISO")), "each supplier's own suppliers are listed, never CAISO itself");
  check(await evaluate(`document.querySelector('[data-trace]').innerText.includes('physical flows over the ties') && document.querySelector('[data-trace]').innerText.includes('not contracts')`), "the trace says: physical flows, not contracts");

  // b. the address
  s = await evaluate(STATE);
  const q = Object.fromEntries(new URLSearchParams(s.search));
  check(q.view === "day" && q.t === "2021-02-15" && q.grid === "CISO" && q.prices === "1" && q.trace === "1" && !("batteries" in q), `the address holds the view, the day, the grid and the switches: ${s.search}`);
  await go(`${base}/network/v3${s.search}`);
  const back = await wait(`(() => { const s = ${STATE}; return s && s.restored === '1' && s.view === 'day' && s.panel === 'CISO' && s.rings > 0 && document.querySelector('[data-trace-supplier]') ? s : null; })()`, 30000, "the shared view to be restored");
  check(back.t === "2021-02-15" && back.playing === "0" && back.rings === priced.length && back.search === s.search, `the same address opens the same view, not playing (${back.t}, ${back.panel}, ${back.rings} rings)`);
  await go(`${base}/network/v3?view=uri_2021&t=2021-02-15T12:00:00Z&grid=ERCO&batteries=1`);
  const story = await wait(`(() => { const s = ${STATE}; return s && s.restored === '1' && s.view === 'uri_2021' && s.panel === 'ERCO' ? s : null; })()`, 30000, "a story's shared view");
  check(story.t === "2021-02-15T12:00:00Z" && story.playing === "0" && (await evaluate(`${button("Batteries: on")} !== undefined`)), `a story's hour, grid and Batteries switch are restored too (${story.t})`);
  await go(`${base}/network/v3?view=nonsense&t=yesterday&grid=%3Cscript%3E&prices=yes`);
  const odd = await wait(`(() => { const s = ${STATE}; return s && s.restored === '1' ? s : null; })()`, 30000, "an address it does not understand");
  check(odd.view === "live" && odd.panel === null && odd.rings === 0, "an address it does not understand opens the page as it opens by default");

  // the live page is as it was
  await go(`${base}/network`);
  await wait(`!!document.querySelector('[data-network-view]')`, 20000);
  await sleep(2500);
  const liveShot = await send("Page.captureScreenshot", { format: "png" });
  fs.writeFileSync(new URL("../../runs/session93/live_network.png", import.meta.url), Buffer.from(liveShot.data, "base64"));
  check(await evaluate(`document.querySelector('[aria-label^="A 3D network"]').__erwGraph === undefined`), "/network exposes nothing of version 3");
  const live = await evaluate(`({ picker: !!document.querySelector('#replay-day'), prices: [...document.querySelectorAll('button')].some((b) => b.innerText.startsWith('Prices')), year: [...document.querySelectorAll('button')].some((b) => b.innerText.includes('Play the year')),
    attrs: document.querySelector('[data-network-view]').getAttributeNames().sort().join(','), search: window.location.search })`);
  check(!live.picker && !live.prices && !live.year && live.attrs === "class,data-network-view" && live.search === "", `/network is as it was: no date picker, no Prices switch, no Play the year, its address untouched (${JSON.stringify(live)})`);
  await evaluate(`(() => { const sel = document.querySelector('select'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value').set.call(sel, 'ERCO'); sel.dispatchEvent(new Event('change', { bubbles: true })); return true; })()`);
  await wait(`document.querySelector('[data-panel]')?.getAttribute('data-panel') === 'ERCO'`);
  check(await evaluate(`!document.querySelector('[data-trace]') && window.location.search === '' && document.querySelector('[data-panel]').innerText.includes('Hub price this hour')`), "/network's panel has no trace and writes nothing to the address");
  if (errors.length) check(false, `the pages threw: ${errors.slice(0, 3).join(" | ").slice(0, 300)}`);
  return bad ? 1 : 0;
});
if (code === null) { console.log("check-network-v3: NOT PROVEN on this machine (no Chrome or Edge, or no 3D)"); process.exit(0); }
console.log(bad ? `${bad} of ${n} checks FAILED` : `the network, version 3, in a browser: ${n} checks pass`);
process.exit(code);
