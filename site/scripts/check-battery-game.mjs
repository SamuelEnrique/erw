// Energy Research Warehouse (ERW) site, session 111: the home battery game, played in a real browser.
//
//   node scripts/check-battery-game.mjs <base-url> <phone|laptop> [level-date]     (default level 2023-08-10)
//
// Plays the game four times at one screen width, in the internal view (the page is in review): Easy, Normal, Hard, and
// Hard with the rooftop add-on, each in its mode of the one page (session 289: the simple page and ?more=1 are gone). Each play follows the perfect battery's plan
// for that day and those rules (lib/battery.ts's optimum), by the controls a person uses: a phone by touch on the two
// buttons, a laptop by the keys. Every request carries the header x-erw-check: 1, so the plays stay off the
// leaderboard and out of the research data. A play takes about 90 seconds; a run about 8 minutes.
//
// Checked, each play:
//   layout     nothing is wider than the screen, before, during and after the play; the two buttons are on the screen
//              and large enough to hold with a thumb
//   controls   following the perfect plan earns at least 90 percent of the perfect battery's score: the controls took
//   end        session 290: the end table's three rows, in order: you, the perfect battery (its earnings equal to
//              lib/battery.ts's optimum for the day and rules) and no battery (lib/battery.ts's noBattery), each with
//              what it bought and sold; the sentence under it; on Normal and Hard the hour you lost the most
//   modes      the page opens in the mode its address names; Easy shows one sentence, a day to pick and Start, and no
//              settings; every mode shows the day at a glance before the play (session 289) and "Play again" after
//   Hard       the notice names the emergency (session 289); the emergency is announced while the price climbs, with its
//              label "game rule, not a real price" and how many kWh the house will need from the battery against the
//              reserve (enough by itself with the default battery since v5);
//              the outage is announced and the buttons are off while it lasts; the reserve line and the wear show
//   add-on     the rooftop switch is offered on Hard only; with it on, the play's title says so and the roof's power
//              and its earnings show
// Exit 1 on a failure; "not proven" (exit 0) without a browser.
import fs from "node:fs";
import { withBrowser, sleep } from "./browser.mjs";
import { DEFAULT_SETTINGS, DIFFICULTIES, SPIKE_LABEL, emergencyOf, noBattery, optimum, rulesOf, simulate } from "../lib/battery.ts";

const base = (process.argv[2] ?? "http://localhost:3111").replace(/\/$/, "");
const device = process.argv[3] === "phone" ? "phone" : "laptop";
const DAY = process.argv[4] ?? "2023-08-10";
const SCREEN = device === "phone" ? { width: 390, height: 844, deviceScaleFactor: 3, mobile: true } : { width: 1366, height: 768, deviceScaleFactor: 1, mobile: false };
const level = JSON.parse(fs.readFileSync(new URL("../data/battery_levels.json", import.meta.url), "utf-8")).levels.find((l) => l.date === DAY);
if (!level) { console.log(`no level of ${DAY} in data/battery_levels.json`); process.exit(2); }
const usd = (v) => `${v < 0 ? "-" : ""}$${Math.abs(v).toFixed(2)}`;
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };

// session 111: Easy is started with its first frames stamped before the press of the start button, as a browser
// sometimes stamps them (production, the fifth play at a laptop's width: the game stopped on its first frame)
const EARLY = `(() => { const raf = window.requestAnimationFrame.bind(window); let k = 0; window.__early = 0;
  window.requestAnimationFrame = (cb) => raf((t) => { if (k++ < 3) { window.__early += 1; return cb(t - 80); } return cb(t); }); return true; })()`;
const ONLY = process.argv[5] ? process.argv[5].split(",") : null;   // a fifth argument plays only the named plays
const PLAYS = [
  { label: "Easy", difficulty: "easy", addons: [] },
  { label: "Normal", difficulty: "normal", addons: [], early: true },  // session 289: Easy has no replay, so Normal carries the early frames
  { label: "Hard", difficulty: "hard", addons: [] },
  { label: "Hard with rooftop solar", difficulty: "hard", addons: ["solar"] },
];

const overflow = `(() => ({ doc: document.documentElement.scrollWidth, win: window.innerWidth, wide: [...document.querySelectorAll('main *')].filter((e) => { const r = e.getBoundingClientRect(); return r.width > 0 && r.right > window.innerWidth + 1 && !e.closest('.overflow-x-auto'); }).slice(0, 3).map((e) => e.tagName + ':' + (e.innerText || '').slice(0, 40)) }))()`;
const BOARD = `(() => { const b = document.querySelector('[data-game-phase]'); if (!b) return null; const btn = [...b.querySelectorAll('button')].filter((x) => /charge|sell/i.test(x.innerText));
  return { phase: b.getAttribute('data-game-phase'), idx: Number(b.getAttribute('data-game-idx')), status: [...b.querySelectorAll('[role=status]')].map((e) => e.innerText).join(' | '), text: b.innerText,
    buttons: btn.map((x) => { const r = x.getBoundingClientRect(); return { label: x.innerText, x: r.left + r.width / 2, y: r.top + r.height / 2, w: r.width, h: r.height, top: r.top, bottom: r.bottom, disabled: x.disabled }; }), vh: window.innerHeight }; })()`;
const clickText = (sel, text) => `(() => { const e = [...document.querySelectorAll(${JSON.stringify(sel)})].find((x) => x.innerText.trim().startsWith(${JSON.stringify(text)}) || x.innerText.includes(${JSON.stringify(text)})); if (!e) return false; e.scrollIntoView({ block: 'center' }); e.click(); return true; })()`;

const code = await withBrowser(async ({ go, evaluate, wait, unlock, send, errors }) => {
  await send("Emulation.setDeviceMetricsOverride", SCREEN);
  if (device === "phone") await send("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 1 });
  await send("Network.setExtraHTTPHeaders", { headers: { "x-erw-check": "1" } });
  await unlock(base);

  let held = 0;   // what the script is holding now: 1 charge, -1 sell, 0 nothing
  const KEY = { 1: "KeyC", [-1]: "KeyS" };
  const VK = { 1: 67, [-1]: 83 };
  const release = async () => {
    if (held === 0) return;
    if (device === "phone") await send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
    else await send("Input.dispatchKeyEvent", { type: "keyUp", code: KEY[held], key: held === 1 ? "c" : "s", windowsVirtualKeyCode: VK[held] });
    held = 0;
  };
  const press = async (want, board) => {
    if (want === held) return;
    await release();
    if (want === 0) return;
    if (device === "phone") {
      const b = board.buttons.find((x) => (want === 1 ? /charge/i : /sell/i).test(x.label));
      if (!b || b.disabled) return;
      await send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x: Math.round(b.x), y: Math.round(b.y) }] });
    } else {
      await send("Input.dispatchKeyEvent", { type: "keyDown", code: KEY[want], key: want === 1 ? "c" : "s", windowsVirtualKeyCode: VK[want] });
    }
    held = want;
  };

  for (const p of PLAYS) {
    if (ONLY && !ONLY.includes(p.label)) continue;
    const tag = `${device}, ${p.label}`;
    const rules = rulesOf(DEFAULT_SETTINGS, p.difficulty, p.addons);
    const sun = p.addons.includes("solar") ? level.solar : undefined;
    const best = optimum(level.price, rules, sun);
    const em = emergencyOf(level.price, rules);
    // session 289: one page; the mode is in the address (Easy needs none) and its button is the one checked
    await go(`${base}/play/battery${p.difficulty === "easy" ? "" : `?mode=${p.difficulty}`}`);
    await wait(`[...document.querySelectorAll('button')].some((b) => b.innerText.trim() === 'Start')`, 30000, `${tag}: the page to be ready`);
    let o = await evaluate(overflow);
    check(o.doc <= o.win + 1 && o.wide.length === 0, `${tag}: nothing is wider than the screen before the play (${o.doc} of ${o.win} px${o.wide.length ? `; ${o.wide.join(" / ")}` : ""})`);
    check(await evaluate(`[...document.querySelectorAll('button[role=radio]')].find((b) => b.getAttribute('aria-checked') === 'true')?.innerText.trim() === ${JSON.stringify(DIFFICULTIES[p.difficulty].label)}`), `${tag}: the page opens in its mode`);
    if (p.difficulty === "easy") {
      const page = await evaluate(`document.querySelector('main').innerText`);
      check(page.includes("Buy power into your battery when it is cheap and sell it when it is dear. You start with $5; the game ends if you go below $0.")
        && !/The battery: settings/.test(page), `${tag}: one sentence, a day to pick and Start; no settings`);
    }
    const offered = await evaluate(`[...document.querySelectorAll('input[role=switch]')].length`);
    check((p.difficulty === "hard") === (offered > 0), `${tag}: the add-on switch is ${p.difficulty === "hard" ? "offered" : "not offered"} (${offered})`);
    check(await evaluate(`(() => { const s = document.querySelector('main select'); const i = [...s.options].findIndex((x) => x.text.includes(${JSON.stringify(DAY)})); if (i < 0) return false;
      Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value').set.call(s, s.options[i].value); s.dispatchEvent(new Event('change', { bubbles: true })); return true; })()`), `${tag}: the day ${DAY} can be picked`);
    if (p.addons.includes("solar")) {
      await sleep(300);
      check(await evaluate(`(() => { const i = [...document.querySelectorAll('input[role=switch]')].find((x) => !x.disabled); if (!i) return false; i.scrollIntoView({ block: 'center' }); i.click(); return true; })()`), `${tag}: the rooftop switch can be turned on for ${DAY}`);
    }
    check(await evaluate(clickText("button", "Start")), `${tag}: Start`);
    // session 289: the day at a glance comes first, with its lowest, average and highest price
    const glance = await wait(`document.querySelector('[data-game-preview]')?.innerText ?? null`, 10000, `${tag}: the day at a glance`).catch(() => null);
    const pl = level.price, avg = pl.reduce((x, v) => x + v, 0) / pl.length;
    const f2 = (v) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    check(typeof glance === "string" && [Math.min(...pl), avg, Math.max(...pl)].every((v) => glance.includes(f2(v))), `${tag}: the day at a glance shows its lowest, average and highest price (${f2(Math.min(...pl))}, ${f2(avg)}, ${f2(Math.max(...pl))})`);
    if (p.early) await evaluate(EARLY);
    await evaluate(clickText("button", "Start now"));
    await wait(`document.querySelector('[data-game-phase]')?.getAttribute('data-game-phase') === 'play'`, 15000, `${tag}: the play to start`);
    const seen = { spike: "", notice: "", outage: "", fleet: false, roof: "", reserve: false, wear: false, offInOutage: null, title: "" };
    let first = true, last = null, end = null;
    const t0 = Date.now();
    while (Date.now() - t0 < 130_000) {
      const b = await evaluate(BOARD);
      if (!b) break;
      last = b;
      if (b.phase !== "play") { end = b; break; }
      if (first) {
        first = false;
        seen.title = b.text.split("\n")[0];
        const o2 = await evaluate(overflow);
        check(o2.doc <= o2.win + 1 && o2.wide.length === 0, `${tag}: nothing is wider than the screen during the play (${o2.doc} of ${o2.win} px${o2.wide.length ? `; ${o2.wide.join(" / ")}` : ""})`);
        check(b.buttons.length === 2 && b.buttons.every((x) => x.h >= 44 && x.w >= 100 && x.top >= 0 && x.bottom <= b.vh), `${tag}: the two buttons are on the screen and large enough to hold (${b.buttons.map((x) => `${x.label.split("\n")[0]} ${Math.round(x.w)} by ${Math.round(x.h)} px, to ${Math.round(x.bottom)} of ${b.vh}`).join("; ")})`);
      }
      if (/Grid emergency and fleet call \(game rules\)/.test(b.status)) seen.spike = b.status;
      if (/^In 15 minutes: the grid emergency and the fleet call/.test(b.status)) seen.notice = b.status;
      if (/Outage \(a game rule\)/.test(b.status)) { seen.outage = b.status; seen.offInOutage = b.buttons.every((x) => x.disabled); }
      if (/fleet call/i.test(b.status)) seen.fleet = true;
      const roof = b.text.match(/roof: [\d.]+ of 5 kW now[^\n]*/);
      if (roof) seen.roof = roof[0];
      if (/wear /.test(b.text)) seen.wear = true;
      const inOutage = em.outage && b.idx >= em.outage.first && b.idx <= em.outage.last;
      await press(inOutage ? 0 : (best.actions[Math.min(b.idx, best.actions.length - 1)] ?? 0), b);
      await sleep(90);
    }
    await release();
    check(!!end && end.phase === "done", `${tag}: the day plays to its end (${Math.round((Date.now() - t0) / 1000)} s)`);
    if (p.early) {
      const early = await evaluate(`window.__early ?? 0`);
      check(early >= 2 && !!end && end.phase === "done", `${tag}: ${early} frames stamped before the press of the start button did not stop the game`);
      // the end screen's replay reads its position the same way: started with its first frames stamped early, it still runs
      await wait(`[...document.querySelectorAll('button')].some((b) => b.innerText.trim() === 'Play the replay')`, 15000, `${tag}: the replay's button`).catch(() => null);
      await evaluate(EARLY);
      const began = await evaluate(clickText("button", "Play the replay"));
      await sleep(2500);
      const replay = await evaluate(`(() => { const r = document.querySelector('input[aria-label="Replay position"]'); return r ? { at: Number(r.value), early: window.__early ?? 0, pause: [...document.querySelectorAll('button')].some((b) => b.innerText.trim() === 'Pause') } : null; })()`);
      check(began && !!replay && replay.early >= 2 && replay.pause && replay.at >= 1 && errors.length === 0, `${tag}: the replay, started with ${replay?.early ?? 0} frames stamped early, runs (at interval ${replay?.at ?? "none"} after 2.5 s)`);
      await evaluate(clickText("button", "Pause"));
    }
    // session 290: the end table, three rows (you, the perfect battery, no battery), and the sentence under it
    const rows = await wait(`(() => { const t = document.querySelector('[data-end-table]'); return t ? [...t.querySelectorAll('tbody tr')].map((r) => [...r.children].map((c) => c.innerText.replace(/\\s+/g, ' ').trim())) : null; })()`, 15000, `${tag}: the end table`).catch(() => null);
    check(Array.isArray(rows) && rows.length === 3 && rows.map((r) => r[0]).join("|") === "You|The perfect battery|No battery", `${tag}: the end table's rows are you, the perfect battery and no battery`);
    if (Array.isArray(rows) && rows.length === 3) {
      const num = (t) => Number(t.replace(/[$,]/g, ""));
      const none = noBattery(level.price, rules, sun);
      check(rows[1][1] === usd(best.score), `${tag}: the perfect battery earned ${usd(best.score)} for this day and these rules: "${rows[1][1]}"`);
      check(rows[2][1] === usd(none), `${tag}: no battery earned ${usd(none)}: "${rows[2][1]}"`);
      check(rows.slice(0, 2).every((r) => /^\d+\.\d{2}/.test(r[2]) && /^\d+\.\d{2}/.test(r[3])), `${tag}: the rows say what was bought and sold, kWh`);
      const got = num(rows[0][1]);
      check(best.score > 0 && got >= 0.9 * best.score, `${tag}: following the perfect plan by the ${device === "phone" ? "buttons" : "keys"} earned ${usd(got)} of the perfect ${usd(best.score)} (${Math.round((100 * got) / best.score)} percent): the controls took`);
    }
    const why = await evaluate(`document.querySelector('[data-end-why]')?.innerText ?? ""`);
    check(why.length > 40, `${tag}: one sentence under the table on why the battery earns what it does: "${why.slice(0, 120)}"`);
    if (p.difficulty !== "easy") {
      const worst = await evaluate(`document.querySelector('[data-worst-hour]')?.innerText ?? ""`);
      check(/^The hour you lost the most was \d{1,2}:\d{2}.* to \d{1,2}:\d{2}.*you made -?\$[\d,.]+\.$/.test(worst) || worst === "You matched the perfect battery in every hour.", `${tag}: the hour lost the most, or none: "${worst}"`);
    }
    o = await evaluate(overflow);
    check(o.doc <= o.win + 1 && o.wide.length === 0, `${tag}: nothing is wider than the screen on the end screen (${o.doc} of ${o.win} px${o.wide.length ? `; ${o.wide.join(" / ")}` : ""})`);
    check(await evaluate(`[...document.querySelectorAll('button')].some((b) => b.innerText.trim() === 'Play again')`), `${tag}: "Play again" is offered after the play`);
    if (p.difficulty === "hard") {
      check(seen.spike.includes(SPIKE_LABEL) && /Next the grid goes down for two hours\./.test(seen.spike), `${tag}: the emergency is announced with its label "${SPIKE_LABEL}" and what comes next`);
      // session 111: the announcement says how much the house will need; session 289 (ruling 2a): the notice before it
      // names the emergency, and both say whether the reserve covers the need (it does with the default battery since v5)
      const need = simulate(level.price, best.actions, rules, sun).outageNeedKwh;
      const words = need > 0 ? `The house will need ${need.toFixed(2)} kWh from the battery in the outage; your backup reserve holds ${rules.reserveKwh + 1e-9 >= need ? `${rules.reserveKwh.toFixed(2)} kWh, enough by itself` : `only ${rules.reserveKwh.toFixed(2)} kWh`}` : "Today the roof carries the house through the outage.";
      check(seen.notice.includes(words) && seen.spike.includes(words), `${tag}: the notice names the emergency, and it and the announcement say: "${words}"`);
      check(/Outage \(a game rule\): the grid is down\. Your house runs on its battery/.test(seen.outage) && seen.offInOutage === true, `${tag}: the outage is announced and the two buttons are off while it lasts`);
      check(seen.wear, `${tag}: the wear on the battery shows beside the money`);
      check(/^.*, Hard/.test(seen.title), `${tag}: the play's title names the difficulty: "${seen.title}"`);
    } else {
      check(seen.spike === "" && seen.outage === "", `${tag}: no emergency and no outage`);
    }
    if (p.addons.includes("solar")) {
      check(/with rooftop solar/.test(seen.title) && seen.roof !== "", `${tag}: the title says "with rooftop solar" and the roof's power shows: "${seen.roof}"`);
      check(/\(the roof's power first\)/.test(seen.outage), `${tag}: in the outage the house takes the roof's power first, and the notice says so`);
    } else {
      check(seen.roof === "", `${tag}: no roof without the add-on`);
    }
    check(seen.fleet, `${tag}: the fleet call is announced`);
  }
  check(errors.length === 0, `${device}: no error was thrown in the page (${errors.length}${errors.length ? `: ${errors[0].slice(0, 160)}` : ""})`);
  return bad;
}, { width: SCREEN.width, height: SCREEN.height });
if (code === null) { console.log("check-battery-game: NOT PROVEN (no browser on this machine)"); process.exit(0); }
console.log(`the battery game on a ${device} (${SCREEN.width} by ${SCREEN.height}), ${DAY}: ${n - bad} of ${n} checks pass`);
process.exitCode = bad ? 1 : 0;
