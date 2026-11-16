// Energy Research Warehouse (ERW) site, session 7536 (chain 304): /play/ev drawn to HTML with the site's own code, its
// faults of 16 November 2026 held fixed (docs/reviews/ev-game-faults-2026-11-16.md) and its decisions fold checked.
//   node --import ./scripts/tsx-register.mjs scripts/test-ev-game-render.mjs      (tests/test_session7536_ev_game.py runs it)
// The page (app/play/ev/page.tsx) reads a file and is drawn by the server; its two components are drawn here as it
// mounts them. Exits 1 on any failure. No request, nothing written.
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const { EvGame } = await import("../app/play/ev/EvGame.tsx");
const { EvDecisions, EV_DECISIONS } = await import("../app/play/ev/Decisions.tsx");
const D = JSON.parse(fs.readFileSync(new URL("../data/ev_prices.json", import.meta.url), "utf-8"));
const us = { code: "US", name: "United States", power: D.us.power, gas: D.us.gas };
const draw = (start, states = D.states) => renderToStaticMarkup(h(EvGame, { states, us, built: D.built_at, ...(start ? { start } : {}) }));
const text = (html) => html.replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ");

let bad = 0;
const check = (ok, what) => { if (!ok) bad++; console.log(`${ok ? "ok  " : "FAIL"} ${what}`); };

// the page as every visitor opens it: the United States at the defaults, its four keyed figures
const open = draw(null);
check(/<option value="US" selected="">/.test(open), "the game opens on the United States");
check(/data-check="ev\|US\|payback" data-raw="3.2">3.2</.test(open), "the opening payback carries its key, 3.2 years");
check(/\$<span data-check="ev\|US\|npv" data-raw="5131">5,131</.test(open), "the opening net present value carries its key, $5,131");
check(!/license needed/.test(open) && !/data-license-held/.test(open), "no figure of the game is held for a license (its keys, ev|..., name no table)");

// fault 1: a keyed payback that rounds to a whole number of years is printed to one decimal, as every other payback is
for (const code of ["KY", "NE", "ND", "TN", "DC", "NJ"]) {
  const m = draw({ code }).match(/data-check="ev\|[A-Z]+\|payback" data-raw="([\d.]+)">([^<]+)</);
  check(m && /^\d+\.\d$/.test(m[2]) && Number(m[2]) === Number(m[1]), `fault 1: ${code} at the defaults prints its payback as ${m ? m[2] : "nothing"} years (one decimal)`);
}
check(/>3\.0<\/span> years/.test(draw({ code: "KY" })), "fault 1: Kentucky reads 3.0 years, not 3 years");

// fault 2: a net present value below zero at the defaults keeps its key, the sign before the dollar
const hi = draw({ code: "HI" });
check(/-\$<span data-check="ev\|HI\|npv" data-raw="-1056">1,056</.test(hi), "fault 2: Hawaii's net present value at the defaults reads -$1,056 and keeps its key");

// fault 4: a state without a held price says which price is missing, not that a public charger's price is wanted
const noPower = D.states.map((s) => (s.code === "VT" ? { ...s, power: null } : s));
const vt = text(draw({ code: "VT" }, noPower));
check(/The warehouse holds no electricity price for Vermont, so the game has no results to show there\./.test(vt) && !/public charger's price on the left/.test(vt), "fault 4: a state without an electricity price says so in place of the results");
check(/Type a public charger's price on the left to see the results\./.test(text(draw({ code: "US", v: { homeShare: 50 } }))), "half charged away from home and no public price: the results wait for that price");

// the start prop is for drawing only: the page passes none
const page = fs.readFileSync(new URL("../app/play/ev/page.tsx", import.meta.url), "utf-8");
check(!/start=/.test(page), "the page passes no start: every visitor opens on the defaults");
check(/<EvDecisions \/>/.test(page) && /from "\.\/Decisions"/.test(page), "the page mounts the decisions fold");

// the decisions fold
const dec = renderToStaticMarkup(h(EvDecisions));
check(new RegExp(`data-decision-count="${EV_DECISIONS.length}"`).test(dec) && EV_DECISIONS.length === 11, `the decisions fold lists ${EV_DECISIONS.length} choices`);
check(EV_DECISIONS.every((d) => dec.includes(`data-decision-default="${d.key}"`) && dec.includes(`data-decision-source="${d.key}"`) && d.def && d.source), "each choice has its default and its source in its hover");
check(!/<details[^>]*open/.test(dec), "the fold is closed to start");
check(!/—/.test(dec) && !EV_DECISIONS.some((d) => /—/.test(d.text + d.def + d.source)), "no em dash in the fold");
check(/href="\/data\/methods\/ev_game"/.test(dec), "the fold links the method note");

console.log(bad ? `${bad} failed` : "all passed");
process.exitCode = bad ? 1 : 0;
