// Energy Research Warehouse (ERW) site, session 7535 (chain 304): the figures the home battery game (/play/battery)
// shows a player, read off the game's own end screen drawn to HTML, for the replication (replication/battery_game/).
//   node --import ./scripts/tsx-register.mjs scripts/battery-game-figures.mjs           (writes the two files)
//   node --import ./scripts/tsx-register.mjs scripts/battery-game-figures.mjs --check   (compares, writes nothing)
//
// The game is played in the browser, so a figure depends on a play. A case is a level (one of the seven frozen days of
// data/battery_levels.json), a mode (Easy, Normal, Hard, Hard with the rooftop add-on), the battery's settings and one
// play: the perfect plan the page shows (optimum's own actions), waiting all day, a plain rule (charge in the day's 8
// cheapest intervals, sell in its 8 dearest), charging all day, and on Hard with no reserve selling all day (the lights
// go out). Each play's actions are written to cases.json, so the replication replays the same moves.
//
// For each case the end screen's pieces are drawn with the page's own components (app/play/battery/Game.tsx: EndTable,
// EarlyEnd, WorstHour, EndDetail, Debrief, Preview, and the words of Hard's notice, keepWordsFor and outageChargeFor),
// with the props the game gives them (lib/battery.ts: simulate, tally, noBattery, optimum, the same calls Game makes),
// and every number in the words drawn is read with the sentence it stands in. Two figures are not drawn because the page
// draws them only on a click or a canvas: the share card's percent of perfect (perfectShare, rounded as the card rounds
// it) and the page's rules section (an async server page: its figures are its own expressions on lib/battery.ts's
// constants, evaluated here as written). No request, no file read but the levels, nothing stored.
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const OUT = new URL("../../replication/battery_game/", import.meta.url);
const lib = await import("../lib/battery.ts");
const G = await import("../app/play/battery/Game.tsx");
const levels = JSON.parse(fs.readFileSync(new URL("../data/battery_levels.json", import.meta.url), "utf-8")).levels
  .map((l) => ({ ...l, grid: l.grid ?? "ERCOT", tz: l.tz ?? "America/Chicago" }));
const check = process.argv.includes("--check");

const words = (html) => html.replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ").replace(/ ([,.;:)])/g, "$1").trim();
const N = "(-?\\$?-?[\\d,]+(?:\\.\\d+)?)";
const T = "(\\d\\d:\\d\\d)";

// ---- the cases -------------------------------------------------------------------------------------------------------
const NOPE = { ...lib.DEFAULT_SETTINGS, reserve: 0 };
const MODES = [
  { id: "easy", d: "easy", addons: [], s: lib.DEFAULT_SETTINGS },
  { id: "normal", d: "normal", addons: [], s: lib.DEFAULT_SETTINGS },
  { id: "hard", d: "hard", addons: [], s: lib.DEFAULT_SETTINGS },
  { id: "hard-solar", d: "hard", addons: ["solar"], s: lib.DEFAULT_SETTINGS },
];
/** The plain rule: charge in the day's 8 cheapest intervals and sell in its 8 dearest, by the real prices; else wait. */
function plainRule(p) {
  const order = p.map((v, i) => [v, i]);
  const cheap = new Set([...order].sort((a, b) => a[0] - b[0] || a[1] - b[1]).slice(0, 8).map((x) => x[1]));
  const dear = new Set([...order].sort((a, b) => b[0] - a[0] || a[1] - b[1]).slice(0, 8).map((x) => x[1]));
  return p.map((_, i) => (cheap.has(i) ? 1 : dear.has(i) ? -1 : 0));
}
const cases = [];
for (const l of levels) {
  const n = l.price.length;
  for (const m of MODES) {
    const r = lib.rulesOf(m.s, m.d, m.addons);
    const sun = r.solarKw > 0 ? l.solar : undefined;
    const best = lib.optimum(l.price, r, sun).actions;
    cases.push({ id: `${l.slug}|${m.id}|perfect`, level: l.slug, mode: m.id, difficulty: m.d, addons: m.addons, settings: m.s, play: "perfect", actions: best });
    cases.push({ id: `${l.slug}|${m.id}|wait`, level: l.slug, mode: m.id, difficulty: m.d, addons: m.addons, settings: m.s, play: "wait", actions: new Array(n).fill(0) });
    cases.push({ id: `${l.slug}|${m.id}|rule8`, level: l.slug, mode: m.id, difficulty: m.d, addons: m.addons, settings: m.s, play: "rule8", actions: plainRule(l.price) });
  }
  cases.push({ id: `${l.slug}|normal|charge`, level: l.slug, mode: "normal", difficulty: "normal", addons: [], settings: lib.DEFAULT_SETTINGS, play: "charge", actions: new Array(n).fill(1) });
  cases.push({ id: `${l.slug}|hard-r0|perfect`, level: l.slug, mode: "hard-r0", difficulty: "hard", addons: [], settings: NOPE, play: "perfect", actions: lib.optimum(l.price, lib.rulesOf(NOPE, "hard", [])).actions });
  cases.push({ id: `${l.slug}|hard-r0|sell`, level: l.slug, mode: "hard-r0", difficulty: "hard", addons: [], settings: NOPE, play: "sell", actions: new Array(n).fill(-1) });
}

// ---- the figures of one drawn piece ----------------------------------------------------------------------------------
const figures = [];
const unread = [];
const put = (c, key, shown) => figures.push({ case: c, key, shown: String(shown) });
function read(c, piece, text, re, keys) {
  const m = re.exec(text);
  if (!m) { unread.push(`${c} ${piece}: ${text.slice(0, 160)}`); return null; }
  keys.forEach((k, i) => { if (k && m[i + 1] !== undefined) put(c, k, m[i + 1]); });
  return m;
}

function endTable(c, html) {
  for (const row of html.matchAll(/data-end-row="([^"]+)">[^<]*<\/span><\/th>(.*?)<\/tr>/g)) {
    const who = row[1] === "You" ? "you" : row[1] === "The perfect battery" ? "perfect" : "none";
    const cells = [...row[2].matchAll(/<td[^>]*>(.*?)<\/td>/g)].map((x) => x[1]);
    put(c, `end_${who}_earned`, words(cells[0]));
    for (const [k, cell] of [["bought", cells[1]], ["sold", cells[2]]]) {
      const kwh = /^([\d,.]+|none)/.exec(cell)[1];
      put(c, `end_${who}_${k}_kwh`, kwh);
      const at = /at ([\d,.-]+)/.exec(cell);
      if (at) put(c, `end_${who}_${k}_price`, at[1]);
    }
  }
  const why = words(/data-end-why="true">(.*?)<\/p>/.exec(html)[1]);
  if (why.startsWith("A battery earns the spread")) {
    read(c, "end-why", why, new RegExp(`bought at an average of ${N} and sold at ${N} USD per MWh, ${N} apart, and loses ${N} percent of the energy on the round trip(?:, plus ${N} of wear on each kWh it draws out of the battery)?`),
      ["why_buy_price", "why_sell_price", "why_spread", "why_loss_pct", "why_wear"]);
  } else if (why.startsWith("The perfect battery only sold")) {
    read(c, "end-why", why, new RegExp(`only sold, at an average of ${N} USD per MWh`), ["why_sell_price"]);
  } else put(c, "why_wait", "no hour paid");
}
function earlyEnd(c, html) {
  const t = words(html);
  if (!t) { put(c, "early_end", "none"); return; }
  if (t.startsWith("Out of money")) { put(c, "early_end", "bankrupt"); read(c, "early", t, new RegExp(`^Out of money at ${T}`), ["early_at"]); return; }
  put(c, "early_end", "lights_out");
  read(c, "early", t, new RegExp(`^Lights out at ${T}:.*? That is ${N} kWh at USD ${N} per MWh.*?: ${N}\\. .*?The outage needed ${N} kWh from the battery; at its start the battery held ${N} kWh\\.`),
    ["early_at", "early_unserved_kwh", "early_voll", "early_penalty", "early_need_kwh", "early_start_kwh"]);
}
function worst(c, html) {
  const t = words(html);
  if (t.startsWith("You matched")) { put(c, "worst", "matched"); return; }
  const m = read(c, "worst", t, new RegExp(`^The hour you lost the most was ${T} to ${T}\\. (?:The grid was down then, so the perfect battery only kept the house running|The perfect battery (sold power|charged up \\(bought power\\)|waited) then, at an average price of ${N} USD/MWh(?: \\(game rule, not a real price; the real price was ${N} USD/MWh\\))?,) and made ${N} in that hour; you made ${N}\\.`),
    ["worst_from", "worst_to", "worst_did", "worst_price", "worst_real", "worst_perfect", "worst_mine"]);
  if (m && t.includes("The grid was down then")) put(c, "worst_did", "grid down");
}
function detail(c, html, easy) {
  const t = words(html);
  if (!easy) {
    read(c, "detail", t, new RegExp(`^In detail: ${N} in the market(?:, less ${N} of wear)?(?:, plus the fleet bonus ${N})?(?:, plus ${N} for the roof's power)?(?:, less the lights-out charge ${N})?\\.`),
      ["detail_cash", "detail_wear", "detail_bonus", "detail_roof", "detail_penalty"]);
  }
  read(c, "detail", t, new RegExp(`Your fleet of 10,000 homes: ${N}; the perfect battery's fleet: ${N}\\.`), ["fleet_mine", "fleet_perfect"]);
}
function debrief(c, html) {
  const t = words(html);
  read(c, "debrief", t, new RegExp(`peaked at ${N} USD/MWh at ${T} (?:Central|Pacific) time and was lowest, ${N} USD/MWh, at ${T}\\. The dearest hour, the fleet call, began at ${T}\\. Knowing every price in advance, this battery would have (.*?) and (never discharged|discharged .*?): buy when power is cheap, sell when it is dear, within ${N} kWh and ${N} kW, losing ${N} percent of the energy on the round trip(?:, never below its ${N} kWh reserve)?(?:, and paying ${N} of wear for each kWh it discharges)?\\.`),
    ["deb_peak", "deb_peak_at", "deb_low", "deb_low_at", "deb_vpp_at", "deb_charged", "deb_discharged", "deb_kwh", "deb_kw", "deb_loss_pct", "deb_reserve_kwh", "deb_wear"]);
}
function preview(c, html) {
  const t = words(html);
  read(c, "preview", t, new RegExp(`lowest ${N} average ${N} highest ${N} most prices: ${N} to ${N} .*?below about ${N} is cheap`), ["glance_lo", "glance_avg", "glance_hi", "glance_typ_lo", "glance_typ_hi", "glance_cheap"]);
  const sd = /of the day's (\d+) real prices \(([\d,.]+) USD per MWh\)/.exec(html.replace(/&#x27;/g, "'"));
  if (sd) { put(c, "glance_n", sd[1]); put(c, "glance_sd", sd[2]); } else unread.push(`${c} preview: no standard deviation`);
}
function hardWords(c, need, r) {
  const w = G.keepWordsFor(need, r);
  if (!w) { put(c, "keep", "none"); outageBanner(c, need, r); return; }
  if (w.startsWith("Today the roof")) { put(c, "keep", "roof"); outageBanner(c, need, r); return; }
  read(c, "keep", w, new RegExp(`need ${N} kWh from the battery in the outage; your backup reserve holds (?:only )?${N} kWh, (enough by itself|so keep at least ${N} kWh)`), ["keep_need", "keep_reserve", "keep_verdict", "keep_at_least"]);
  outageBanner(c, need, r);
}
/** The banner in the outage (OutageBanner): the charge a dark house would pay, or "roof" when the roof carries it all. */
function outageBanner(c, need, r) {
  const t = words(renderToStaticMarkup(h(G.OutageBanner, { need, rules: r })));
  if (t.includes("Today the roof carries the house")) { put(c, "outage_charge", "roof"); return; }
  read(c, "outage", t, new RegExp(`the house needed in the whole outage \\(${N}\\)`), ["outage_charge"]);
}

// ---- draw every case -------------------------------------------------------------------------------------------------
const clock = (tz, ts) => new Intl.DateTimeFormat("en-US", { timeZone: tz, hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).format(new Date(ts));
const seen = new Set();
for (const c of cases) {
  const l = levels.find((x) => x.slug === c.level);
  const r = lib.rulesOf(c.settings, c.difficulty, c.addons);
  const sun = r.solarKw > 0 ? l.solar : undefined;
  const best = lib.optimum(l.price, r, sun);
  const perfect = lib.simulate(l.price, best.actions, r, sun);
  const mine = lib.simulate(l.price, c.actions, r, sun);
  const easy = c.difficulty === "easy";
  const ends = { mine: lib.tally(l.price, c.actions, r, sun), perfect: lib.tally(l.price, best.actions, r, sun), none: lib.noBattery(l.price, r, sun) };
  endTable(c.id, renderToStaticMarkup(h(G.EndTable, { mine: ends.mine, perfect: ends.perfect, none: ends.none, rules: r, big: easy })));
  const at = mine.end === null ? "" : clock(l.tz, l.ts_utc[Math.min(l.price.length - 1, mine.end)]);
  earlyEnd(c.id, renderToStaticMarkup(h(G.EarlyEnd, { mine, at })));
  if (!easy) worst(c.id, renderToStaticMarkup(h(G.WorstHour, { level: l, rules: r, mine, perfect })));
  detail(c.id, renderToStaticMarkup(h(G.EndDetail, { result: { mine, rules: r, preset: lib.presetOf(c.settings, c.difficulty, c.addons) }, perfect, easy, server: "" })), easy);
  const share = lib.perfectShare(mine.score, perfect.score);
  put(c.id, "share_pct", share === null ? "none" : String(Math.round(share)));
  // once a level and mode: the debrief, the notice's words; once a level: the day at a glance
  const lm = `${c.level}|${c.mode}`;
  if (!seen.has(lm)) {
    seen.add(lm);
    if (!easy) debrief(`${lm}|day`, renderToStaticMarkup(h(G.Debrief, { level: l, result: { rules: r }, best: best.actions, vppFirst: lib.vppHour(lib.emergencyOf(l.price, r).prices).first })));
    if (c.difficulty === "hard") hardWords(`${lm}|day`, perfect.outageNeedKwh, r);
  }
  if (!seen.has(c.level)) { seen.add(c.level); preview(`${c.level}|glance`, renderToStaticMarkup(h(G.Preview, { level: l, hard: false, onDone: () => {}, hover: "" }))); }
}
// the rules section of the page (app/play/battery/page.tsx), its expressions as written there
const { EMERGENCY, LIGHTS_OUT, SETTINGS, START_MONEY, FLEET_MW, FLEET_MWH, SOLAR } = lib;
const rules = [
  ["start_money", START_MONEY], ["ramp", EMERGENCY.ramp.map((r) => `${Math.round(r * 100)}`).join(", ")], ["cap", EMERGENCY.cap.toLocaleString("en-US")], ["house_kw", EMERGENCY.houseKw],
  ["voll", LIGHTS_OUT.usdPerMwh.toLocaleString("en-US")], ["lights_out_2h", ((LIGHTS_OUT.usdPerMwh * EMERGENCY.houseKw * EMERGENCY.outageIntervals) / 4000).toFixed(2)],
  ["voll_study", LIGHTS_OUT.study.toLocaleString("en-US")], ["voll_residential", LIGHTS_OUT.residential.toLocaleString("en-US")], ["solar_kw", SOLAR.kw],
  ["reserve_pct", Math.round(SETTINGS.reserve.def * 100)], ["reserve_kwh", (13.5 * SETTINGS.reserve.def).toFixed(2)], ["outage_need_kwh", ((EMERGENCY.houseKw * EMERGENCY.outageIntervals) / 4 / Math.sqrt(0.9)).toFixed(2)],
  ["fleet_mw", FLEET_MW], ["fleet_mwh", FLEET_MWH], ["deg_default", SETTINGS.deg.def], ["kwh_default", SETTINGS.kwh.def], ["kw_default", SETTINGS.kw.def], ["rte_default_pct", Math.round(SETTINGS.rte.def * 100)],
];
for (const [k, v] of rules) put("page|rules", k, v);

// ---- write or compare ------------------------------------------------------------------------------------------------
const body = { note: "ERW, session 7535: the figures /play/battery shows a player, read off its end screen drawn with the site's own components (site/scripts/battery-game-figures.mjs). Each figure as printed.", n: figures.length, figures };
const casesBody = { note: "ERW, session 7535: the plays of the replication. Each case: a frozen level (site/data/battery_levels.json), a mode, the settings, and the play's 15-minute actions (1 charge, 0 wait, -1 sell). The perfect play's actions are the page's own optimum; the others are stated rules.", cases };
const P = new URL("page_figures.json", OUT), C = new URL("cases.json", OUT);
if (unread.length) { console.log(`NOT READ ${unread.length}:`); unread.slice(0, 20).forEach((u) => console.log(`  ${u}`)); }
if (check) {
  const was = JSON.parse(fs.readFileSync(P, "utf-8"));
  const same = JSON.stringify(was.figures) === JSON.stringify(figures);
  console.log(same ? `page_figures: ${figures.length} figures, as committed` : `page_figures: DIFFERENT from the committed file (${was.figures.length} committed, ${figures.length} drawn)`);
  process.exitCode = same && !unread.length ? 0 : 1;
} else {
  fs.mkdirSync(OUT, { recursive: true });
  fs.writeFileSync(P, JSON.stringify(body, null, 1) + "\n");
  fs.writeFileSync(C, JSON.stringify(casesBody) + "\n");
  console.log(`wrote ${figures.length} figures of ${cases.length} cases`);
  process.exitCode = unread.length ? 1 : 0;
}
