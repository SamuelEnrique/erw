// Energy Research Warehouse (ERW) site, session 167: the project map, one page (/map), in a real browser.
//
//   npm run build && npx next start -p 3167
//   node scripts/check-map.mjs [base-url]      (default http://localhost:3167)
//
// The page's choices, sentence, totals, map, card and table are drawn by the browser, so they are checked in one, in the
// internal view (the page is in review). Every expected figure is computed here from the site's own copy of the tables
// (data/map.json) with the page's own functions (lib/projectmap.ts):
//   visitor     without the cookie /map is the in-review page
//   redirect    /map/v2 lands on /map, its query carried over
//   opens       everything chosen: the sentence's counts and MW by kind, a total for every status, the rows drawn, a canvas
//   lists       every list (kind, grid, technology, status, state): "Clear" chooses none and says so, "Select all" brings
//               every one back; options ticked one by one choose those only; the figures are the file's after each
//   address     the address keeps the choice: a fresh load of it shows the same choice and the same figures
//   states      a click on a state on the drawing chooses it, a second state adds itself, a click again takes it away
//   card        a click on a unit opens its card, field for field the file's (an EIA unit and a datacenter)
//   table       "By technology" follows the choice
//   reset       Reset brings everything back and empties the address
// Exit 1 on a failure; "not proven" (exit 0) without a browser.
import fs from "node:fs";
import { geoAlbersUsa } from "d3-geo";
import { withBrowser } from "./browser.mjs";
import { EVERYTHING, KIND, cardOf, optionsOf, parseChoice, queryOf, select, totals, whole } from "../lib/projectmap.ts";

const base = (process.argv[2] ?? "http://localhost:3167").replace(/\/$/, "");
const f = JSON.parse(fs.readFileSync(new URL("../data/map.json", import.meta.url), "utf-8"));
const projection = geoAlbersUsa().scale(1300).translate([487.5, 305]);
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };

const STATE = `(() => ({ summary: document.querySelector('[data-map-summary]')?.innerText ?? null,
  totals: Object.fromEntries([...document.querySelectorAll('[data-map-total]')].map((e) => [e.getAttribute('data-map-total'), e.innerText])),
  drawn: Number(document.querySelector('[data-map-drawn]')?.getAttribute('data-map-drawn') ?? -1), canvas: !!document.querySelector('[data-map-drawn] canvas'),
  said: Object.fromEntries([...document.querySelectorAll('[data-map-said]')].map((e) => [e.getAttribute('data-map-said'), e.innerText])),
  tech: Object.fromEntries([...document.querySelectorAll('[data-tech-count]')].map((e) => [e.getAttribute('data-tech-count'), e.innerText])),
  search: location.search, path: location.pathname }))()`;

function expected(c) {
  const picked = select(f, c);
  const t = totals(f, picked);
  const drawn = picked.filter((i) => f.la[i] !== null && f.lo[i] !== null && projection([f.lo[i], f.la[i]]) !== null).length;
  return { picked, t, drawn };
}
/** The pieces the sentence must hold for a choice: the count and MW of each kind chosen. */
function pieces(t) {
  const [op, pl, q, dc] = t.byKind;
  const out = [];
  if (op.rows + pl.rows) out.push(`${whole(op.rows + pl.rows)} `, `${whole(op.mw + pl.mw)} MW`);
  if (q.rows) out.push(`${whole(q.rows)} queue positions`, `${whole(q.mw)} MW requested`);
  if (dc.rows) out.push(`${whole(dc.rows)} datacenters`);
  return out;
}
async function compare(wait, c, label) {
  const e = expected(c);
  const want = e.t.rows === 0 ? ["Nothing on this map matches these choices."] : pieces(e.t);
  const s = await wait(`(() => { const s = ${STATE}; return s.summary && ${JSON.stringify(want)}.every((w) => s.summary.includes(w)) && s.drawn === ${e.drawn} ? s : null; })()`,
    15000, `${label}: the sentence to say ${want.join(", ")}`).catch(() => null);
  check(!!s, `${label}: the sentence and the rows drawn are the file's (${e.t.rows ? want.join(", ") : "nothing"}; ${whole(e.drawn)} drawn)`);
  if (!s) return null;
  const tiles = f.statuses.map((st, i) => [st.slug, e.t.byStatus[i]]).filter(([, x]) => x.rows > 0);
  check(tiles.length === Object.keys(s.totals).length && tiles.every(([slug, x]) => s.totals[slug] === (x.withMw ? whole(x.mw) : "not stated")),
    `${label}: a total for each status chosen, the file's (${tiles.map(([slug, x]) => `${slug} ${whole(x.mw)}`).join(", ") || "none"})`);
  const kinds = [KIND.operating, KIND.planned, KIND.queue].filter((k) => c.kind === null || c.kind.includes(k));
  const cells = {};
  f.techs.forEach((tt, ti) => { if (tt.slug !== "datacenter" && kinds.some((k) => e.t.byTech[ti][k].rows)) for (const k of kinds) cells[`${tt.slug}|${f.kinds[k].slug}`] = e.t.byTech[ti][k].rows ? whole(e.t.byTech[ti][k].rows) : "0"; });
  check(JSON.stringify(Object.entries(s.tech).sort()) === JSON.stringify(Object.entries(cells).sort()), `${label}: "By technology" holds the file's counts for what is chosen (${Object.keys(cells).length} cells)`);
  return s;
}
const click = (sel) => `(() => { const el = document.querySelector(${JSON.stringify(sel)}); if (!el) return false; el.click(); return true; })()`;
const option = (which, slug) => `[data-map-option="${which}|${optionsOf(f, which).indexOf(slug)}"]`;

const code = await withBrowser(async ({ go, evaluate, wait, unlock, send, sleep }) => {
  await go(`${base}/map`);
  check(await evaluate(`!!document.querySelector('[data-in-review="1"]') && !document.querySelector('[data-map-summary]')`), "visitor: /map is the in-review page, with no figure of the map");
  await unlock(base);

  await go(`${base}/map/v2?grid=ercot`);
  await wait(`!!document.querySelector('[data-map-summary]')`, 30000, "the page to be ready");
  let s = await evaluate(STATE);
  check(s.path === "/map" && s.search === "?grid=ercot", `redirect: /map/v2?grid=ercot lands on /map?grid=ercot (${s.path}${s.search})`);
  await compare(wait, { ...EVERYTHING, grid: [0] }, "redirect: ERCOT");

  await go(`${base}/map`);
  await wait(`!!document.querySelector('[data-map-drawn] canvas')`, 30000, "the map's canvas");
  s = await compare(wait, EVERYTHING, "opens");
  check(!!s && s.canvas, "opens: the map is a canvas");
  check(await evaluate(`document.querySelector('[data-map-units]')?.innerText === ${JSON.stringify(whole(f.counts.units))}`), `opens: the header counts the file's ${whole(f.counts.units)} units`);
  check(await evaluate(`document.querySelector('[data-map-card]')?.getAttribute('data-map-card') === 'empty'`), "opens: no card until a unit is clicked");
  check(await evaluate(`!document.querySelector('#queue') && !document.querySelector('#table')`), "opens: no queue beside the map and no table of what is selected (both deleted)");
  check(await evaluate(`[...document.querySelectorAll('details')].every((d) => !/What the inventory leaves out|How to read it/.test(d.innerText))`), "opens: the two note blocks are gone from the face");
  if (f.held.length) check(await evaluate(`(document.querySelector('[data-map-held]')?.innerText ?? '').includes('MISO queue positions: paused while terms are reviewed')`), "opens: MISO's queue reads \"paused while terms are reviewed\"");

  // every list: Clear, then Select all
  for (const which of ["kind", "grid", "tech", "status", "state"]) {
    await evaluate(`document.querySelector('[data-map-filter="${which}"]').open = true`);
    await evaluate(click(`[data-map-clear="${which}"]`));
    s = await compare(wait, { ...EVERYTHING, [which]: [] }, `${which}: Clear`);
    check(!!s && s.said[which] === "none" && s.search === `?${which}=none`, `${which}: Clear says none and the address says ${which}=none (${s?.said[which]}, ${s?.search})`);
    await evaluate(click(`[data-map-all="${which}"]`));
    s = await compare(wait, EVERYTHING, `${which}: Select all`);
    check(!!s && s.said[which] === "all" && s.search === "", `${which}: Select all says all and empties the address (${s?.said[which]}, "${s?.search}")`);
  }

  // options ticked one by one: two grids, two technologies, two statuses, two states, two kinds
  const picks = [["grid", ["ercot", "caiso"]], ["tech", ["solar", "battery"]], ["kind", ["operating", "planned"]], ["status", ["u", "v"]], ["state", ["TX", "CA"]]];
  let c = { ...EVERYTHING };
  for (const [which, slugs] of picks) {
    await evaluate(click(`[data-map-clear="${which}"]`));
    for (const slug of slugs) await evaluate(click(option(which, slug)));
    c = { ...c, [which]: slugs.map((x) => optionsOf(f, which).indexOf(x)).sort((a, b) => a - b) };
    s = await compare(wait, c, `ticked ${which} ${slugs.join(" and ")}`);
  }
  const address = queryOf(c, f);
  check(!!s && s.search === address, `address: the choice is written as ${address} (${s?.search})`);

  // the address round trip: a fresh load of it shows the same choice and figures
  await go(`${base}/map${address}`);
  await wait(`!!document.querySelector('[data-map-summary]')`, 30000, "the page to be ready");
  s = await compare(wait, parseChoice(address, f), "address: a fresh load of the address");
  check(!!s && s.said.grid === "2 of 9" && s.said.state === `2 of ${f.states.length}` && s.said.kind === "2 of 4", `address: the panel shows the choice again (${JSON.stringify(s?.said)})`);

  // Reset
  await evaluate(click("[data-map-reset]"));
  s = await compare(wait, EVERYTHING, "reset");
  check(!!s && s.search === "" && Object.values(s.said).every((v) => v === "all"), `reset: every list is all and the address is empty ("${s?.search}")`);

  // a state clicked on the drawing: no unit drawn (kind: none), so the click reaches the state itself
  const px = async (lon, lat) => evaluate(`(() => { const el = document.querySelector('[data-map-drawn]'); el.scrollIntoView({ block: 'center' }); const ch = echarts.getInstanceByDom(el);
    const p = ch.convertToPixel({ geoIndex: 0 }, ${JSON.stringify(projection([lon, lat]))}); const r = el.getBoundingClientRect(); return [r.left + p[0], r.top + p[1]]; })()`);
  const mouse = async ([x, y]) => {
    await send("Input.dispatchMouseEvent", { type: "mouseMoved", x, y });
    await send("Input.dispatchMouseEvent", { type: "mousePressed", x, y, button: "left", clickCount: 1 });
    await send("Input.dispatchMouseEvent", { type: "mouseReleased", x, y, button: "left", clickCount: 1 });
    await sleep(400);
  };
  await evaluate(click(`[data-map-clear="kind"]`));
  await wait(`(${STATE}).drawn === 0`, 15000, "nothing drawn");
  await sleep(500);
  const TX = [-99.3, 31.3], CA = [-119.6, 37.2];
  await mouse(await px(...TX));
  s = await wait(`(() => { const s = ${STATE}; return s.said.state === 'TX' ? s : null; })()`, 8000, "Texas chosen").catch(() => null);
  check(!!s && s.search === "?kind=none&state=TX", `states: a click on Texas chooses Texas alone (${s?.search})`);
  await mouse(await px(...CA));
  s = await wait(`(() => { const s = ${STATE}; return s.said.state === '2 of ${f.states.length}' ? s : null; })()`, 8000, "California added").catch(() => null);
  check(!!s && s.search === "?kind=none&state=CA,TX", `states: a click on California adds it (${s?.search})`);
  await mouse(await px(...TX));
  s = await wait(`(() => { const s = ${STATE}; return s.said.state === 'CA' ? s : null; })()`, 8000, "Texas taken away").catch(() => null);
  check(!!s && s.search === "?kind=none&state=CA", `states: a click on Texas again takes it away (${s?.search})`);
  await mouse(await px(...CA));
  s = await wait(`(() => { const s = ${STATE}; return s.said.state === 'all' ? s : null; })()`, 8000, "every state again").catch(() => null);
  check(!!s && s.search === "?kind=none", `states: taking the last state away shows every state again (${s?.search})`);

  // the card: a choice that draws one unit alone, clicked
  const cardCheck = async (address, label) => {
    await go(`${base}/map${address}`);
    await wait(`!!document.querySelector('[data-map-drawn] canvas')`, 30000, "the map's canvas");
    const e = expected(parseChoice(address, f));
    const placed = e.picked.filter((i) => f.la[i] !== null && projection([f.lo[i], f.la[i]]));
    if (placed.length !== 1) { check(false, `${label}: the choice ${address} draws one unit (${placed.length})`); return; }
    const i = placed[0];
    await wait(`(${STATE}).drawn === 1`, 15000, "one unit drawn");
    await sleep(800);
    await mouse(await px(f.lo[i], f.la[i]));
    const want = cardOf(f, i);
    const got = await wait(`(() => { const el = document.querySelector('[data-map-card]'); if (!el || el.getAttribute('data-map-card') !== ${JSON.stringify(want.id)}) return null;
      return { name: el.querySelector('[data-card-name]')?.innerText, fields: Object.fromEntries([...el.querySelectorAll('[data-card-field]')].map((x) => [x.getAttribute('data-card-field'), x.innerText.trim()])) }; })()`,
      8000, `${label}: the card of ${want.id}`).catch(() => null);
    check(!!got, `${label}: a click on the unit opens the card of ${want.id}`);
    if (!got) return;
    check(got.name === want.name, `${label}: the card's name is the file's (${want.name})`);
    const bad = want.rows.filter((r) => got.fields[r.key] !== r.value).map((r) => `${r.key}: "${got.fields[r.key]}" not "${r.value}"`);
    check(bad.length === 0, `${label}: the card's ${want.rows.length} fields are the file's (${want.rows.map((r) => r.label).join(", ")})${bad.length ? `; ${bad.join("; ")}` : ""}`);
    check((got.fields.read_from ?? "").includes(want.table), `${label}: the card names the ERW table it was read from (${want.table})`);
    if (want.stories.length) check(got.fields.stories === `Stories: ${want.stories.map((_, k) => k + 1).join(" ")}`, `${label}: the card links the ${want.stories.length} stories`);
  };
  await cardCheck(`?kind=operating&min=${f.mw[0]}`, "card, the largest operating unit");
  // a datacenter alone in its state on the drawing, with the stories it has
  const dcs = f.kinds[KIND.datacenter];
  const byState = new Map();
  for (let i = dcs.start; i < dcs.start + dcs.rows; i++) if (f.la[i] !== null && projection([f.lo[i], f.la[i]])) byState.set(f.s[i], [...(byState.get(f.s[i]) ?? []), i]);
  const lone = [...byState.entries()].find(([, rows]) => rows.length === 1);
  if (lone) await cardCheck(`?kind=datacenter&state=${f.states[lone[0]]}`, "card, a datacenter");
  return bad;
});
if (code === null) { console.log("check-map: NOT PROVEN (no browser on this machine)"); process.exit(0); }
console.log(`the project map, one page, in a browser: ${n - bad} of ${n} checks pass`);
process.exit(bad ? 1 : 0);
