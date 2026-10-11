// Energy Research Warehouse (ERW) site, session 194: the finance of /cost-of-power's scenarios
// (lib/datacenter/finance.ts) against cases computed by hand, against the generator page's library
// (lib/seller/finance.ts) where the arithmetic is the same, and against the page's own figures over its own files
// (lib/datacenter.ts through scripts/datacenter-ways.mjs). No server, no browser, no network.
//
//   node scripts/test-datacenter-finance.mjs                 the assertions; exits 1 if any fails
//   node scripts/test-datacenter-finance.mjs --cases f.json  prints, as JSON, the results for the cases in f.json
//                                                            ([{ a, b: Assumptions, ways: [Way or null, Way or null] }]);
//                                                            tests/test_session194.py compares them with its Python
//                                                            mirror to 1e-6
//   node scripts/test-datacenter-finance.mjs --page          prints, as JSON, the default page's two ways and the
//                                                            figures of its headline, for the same test
import fs from "node:fs";

const F = await import("../lib/datacenter/finance.ts");
const SF = await import("../lib/seller/finance.ts");
const L = await import("../lib/datacenter.ts");
const W = await import("./datacenter-ways.mjs");

// the exit waits until stdout has taken every byte (session 179: on Linux a pipe takes 64 KiB at a time)
const print = async (v) => { await new Promise((done) => process.stdout.write(JSON.stringify(v) + "\n", done)); process.exit(0); };
const at = process.argv.indexOf("--cases");
if (at > 0) {
  const cases = JSON.parse(fs.readFileSync(process.argv[at + 1], "utf-8"));
  await print(cases.map(({ a, b, ways }) => {
    const wa = F.wayOf(a, ways), wb = F.wayOf(b, ways);
    return { a: wa ? F.resultOf(a, wa) : null, flows: wa ? F.flows(a, wa) : null, against: wa && wb ? F.against(a, wa, b, wb) : null,
      bars: F.sensitivity(a, ways).map((x) => ({ key: x.key, down: x.down, up: x.up, size: x.size, base: x.base })) };
  }));
}
if (process.argv.includes("--page")) {
  const p = W.pageOf({}), f = W.pageOf({ run: "hours", n: String(L.DEFAULTS.n) });
  await print({ x: p.x, ways: p.ways, flexPage: f.ways, per: p.s12?.per ?? null, cost: p.s12?.cost ?? null, energy: p.s12?.energy ?? null, from: p.l12?.[0].m ?? null, to: p.l12?.[11].m ?? null,
    bad: p.bad ? { m: p.bad.m, per: p.bad.cost / p.bad.energy } : null, gpuHour: p.s12 ? L.gpuHour(p.s12.per, p.x.gpu, p.x.pue) : null, gpus: L.gpus(p.x.mw, p.x.gpu, p.x.pue) });
}

let failed = 0;
function check(ok, what, detail = "") {
  if (!ok) failed++;
  console.log(`${ok ? "ok  " : "FAIL"} ${what}${detail ? `: ${detail}` : ""}`);
}
const near = (a, b, tol = 1e-9) => a !== null && b !== null && Math.abs(a - b) <= tol * Math.max(1, Math.abs(b));

// the defaults: the page's two cited ones, and the five the page does not otherwise hold
const d = F.defaultsOf({ run: 0, gpu: 1.3, pue: 1.56 });
check(JSON.stringify(d) === JSON.stringify({ run: 0, gpu: 1.3, pue: 1.56, adder: 0, growth: 0, upfront: 0, life: 20, hurdle: 8 }), "the defaults", JSON.stringify(d));
check(F.defaultsOf({ run: 1, gpu: 1, pue: 1.2 }).run === 1 && F.defaultsOf({ run: 1, gpu: 1, pue: 1.2 }).gpu === 1 && F.defaultsOf({ run: 1, gpu: 1, pue: 1.2 }).pue === 1.2, "the way of running, the power per GPU and the overhead ratio default to \"Your load\"");
check(F.KEYS.length === 8 && new Set(F.KEYS.map((k) => F.SPECS[k].letter)).size === 8, "eight assumptions, eight different letters");
check(JSON.stringify(F.KEYS) === JSON.stringify(["run", "gpu", "pue", "adder", "growth", "upfront", "life", "hurdle"]), "in the page's order");
check(F.KEYS.every((k) => k === "gpu" || k === "pue" || F.SPECS[k].source.length > 20), "every default the library holds states where it comes from");
check(/No cited/.test(F.SPECS.hurdle.source) && /No cited/.test(F.SPECS.life.source) && /No cited/.test(F.SPECS.growth.source) && /No cited/.test(F.SPECS.upfront.source), "the four defaults with no source say so");

// a flat MW at USD 40 in every hour of 8,760, and the same MW off in 100 hours that averaged USD 213.20
const flat = { per: 40, cost: 350400, energy: 8760, held: 8760, flatCost: 350400, down: 0, bad: null, of: 0 };
const flex = { per: 38, cost: 329080, energy: 8660, held: 8760, flatCost: 350400, down: 100, bad: null, of: 0 };
const ways = [flat, flex];
check(F.wayOf(d, ways) === flat && F.wayOf({ ...d, run: 1 }, ways) === flex && F.wayOf({ ...d, run: 1 }, [flat, null]) === null, "a scenario reads the way it runs; a way not held is null");
check(near(F.price(d, flat), 40) && near(F.bill(d, flat), 350400), "price 40, a year 350,400 a MW");
check(near(F.price({ ...d, adder: 10 }, flat), 50) && near(F.bill({ ...d, adder: 10 }, flat), 438000) && near(F.bill({ ...d, adder: 10 }, flex), 329080 + 86600), "other charges of 10 are paid on every MWh consumed");
check(near(F.gpuHour(d, flat), 0.08112, 1e-12) && near(F.gpuHour(d, flat), L.gpuHour(40, 1.3, 1.56), 1e-15), "per GPU-hour: 40 x 1.3 x 1.56 / 1,000 = 0.08112, the page's own formula", String(F.gpuHour(d, flat)));
check(near(F.gpusPerMw(d) * 100, L.gpus(100, 1.3, 1.56), 1e-12) && near(F.gpusPerMw(d), 1000 / 2.028), "GPUs a MW: 1,000 / (1.3 x 1.56) = 493.1, the page's own formula");
check(near(F.gpuHoursYear(d, flat), 8760000 / 2.028) && near(F.gpuHoursYear(d, flex), 8660000 / 2.028), "GPU-hours a year a MW: the hours at full load times the GPUs");
check(F.offOf(d, flat) === null, "a flat load has no hours off");
const off = F.offOf(d, flex);
check(off.hours === 100 && near(off.mwh, 100) && near(off.perMwh, 213.2) && near(off.perGpuHour, 213.2 * 2.028 / 1000), "100 hours off: (350,400 - 329,080) / 100 = 213.20 per MWh not bought, 0.4324 per GPU-hour not run", JSON.stringify(off));
check(near(F.offOf({ ...d, adder: 10 }, flex).perMwh, 223.2), "the other charges are not paid in an hour off either");
check(F.offOf(d, { ...flat, down: 0, energy: 8760 - 1e-12 }) === null, "a shifting load, never off for an hour, has none");

// the costs by year and their present value
const u = { ...d, upfront: 100, growth: 10, life: 3, hurdle: 0 };
const fl = F.flows(u, flat);
check(fl.length === 4 && fl[0] === 100000 && near(fl[1], 350400) && near(fl[2], 385440) && near(fl[3], 423984), "the costs: 100 per kW is 100,000 a MW at year 0; then 350,400, 385,440, 423,984 with prices rising 10 percent a year");
check(near(F.presentValue(u, flat), 100000 + 350400 + 385440 + 423984), "at a hurdle rate of zero the present value is the plain sum");
check(near(F.npv(10, [0, 110]), 100) && near(F.annuity(0, 10), 10) && near(F.annuity(10, 1), 1 / 1.1) && near(F.annuity(8, 20), (1 - 1.08 ** -20) / 0.08), "present value and the value of 1 a year: annuity(8 percent, 20) = 9.8181", String(F.annuity(8, 20)));
check(near(F.presentValue(d, flat), 350400 * F.annuity(8, 20)), "20 years at 8 percent: 350,400 x 9.8181 = 3,440,279 a MW", String(F.presentValue(d, flat)));
check(near(F.levelPrice(d, flat), 40, 1e-12) && near(F.levelPrice({ ...d, hurdle: 0, life: 7 }, flat), 40, 1e-12), "with no change of prices the fixed price with the same present value is the last twelve months' price");
const g8 = { ...d, growth: 8 };   // growth equal to the hurdle rate: each year's term is 1 / 1.08
check(near(F.levelPrice(g8, flat), 40 * (20 / 1.08) / F.annuity(8, 20)), "prices rising at the hurdle rate: 40 x (20 / 1.08) / 9.8181 = 75.45", String(F.levelPrice(g8, flat)));
check(near(F.levelPrice(g8, flat) * 8760 * F.annuity(8, 20), F.presentValue(g8, flat)), "and a contract at that price for all the energy has the market's present value");
check(F.levelPrice({ ...d, adder: 25, upfront: 900 }, flat) === F.levelPrice(d, flat), "the fixed price is market energy only: other charges and the upfront cost do not move it");
check(near(F.levelGpuHour(d, flat), F.gpuHour(d, flat), 1e-12) && near(F.levelGpuHour({ ...d, life: 3, hurdle: 15 }, flex), F.gpuHour(d, flex), 1e-12), "all-in per GPU-hour is the page's power per GPU-hour while nothing is paid upfront and prices do not change");
const up = { ...d, upfront: 500 };
check(near(F.levelGpuHour(up, flat), (500000 + 350400 * F.annuity(8, 20)) / ((8760000 / 2.028) * F.annuity(8, 20))) && F.levelGpuHour(up, flat) > F.gpuHour(up, flat), "an upfront cost is spread over the GPU-hours of the years counted");
const r = F.resultOf(d, flex);
check(near(r.price, 38) && near(r.bill, 329080) && near(r.gpuHour, 38 * 2.028 / 1000) && r.off.hours === 100 && near(r.pv, 329080 * F.annuity(8, 20)) && near(r.level, 38) && near(r.allIn, r.gpuHour), "a column's figures together");

// the rate of return, the generator page's own code
check(near(F.irr([-100, 110]), 10, 1e-6) && F.irr([-100, -5, -5]) === null && F.irr([100, 5]) === null, "irr([-100, 110]) = 10 percent; none when every year has one sign");
{
  let seed = 194, worst = 0, n = 0;
  const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
  for (let i = 0; i < 300; i++) {
    const f = [-(1 + rnd() * 1000)];
    for (let t = 0; t < 1 + Math.floor(rnd() * 30); t++) f.push(rnd() * 200 - 20);
    const x = F.irr(f), y = SF.irr(f), rate = rnd() * 30;
    worst = Math.max(worst, x === null || y === null ? (x === y ? 0 : Infinity) : Math.abs(x - y), Math.abs(F.npv(rate, f) - SF.npv(rate, f)));
    n++;
  }
  check(worst === 0, `${n} seeded cases: present value and the rate of return equal the generator page's library exactly`, `largest gap ${worst}`);
}

// B against A
const B = { ...d, run: 1, upfront: 50 };
const g = F.against(d, flat, B, flex);
check(near(g.bill, -21320) && near(g.gpuHours, -100000 / 2.028) && near(g.pv, 50000 - 21320 * F.annuity(8, 20)), "B flexible with 50 per kW upfront: 21,320 a MW less a year, 49,310 fewer GPU-hours a MW, present value lower by 159,323");
check(near(g.evenUpfront, 21.32 * F.annuity(8, 20)) && near(F.presentValue({ ...B, upfront: g.evenUpfront }, flex), F.presentValue(d, flat)), "the two have the same present value when B's upfront cost is 209.32 per kW", String(g.evenUpfront));
const want = F.irr([-50000, ...Array(20).fill(21320)]);
check(g.more === "b" && g.extra === 50 && g.sameYears && near(g.rate, want, 1e-9) && near(F.npv(g.rate, [-50000, ...Array(20).fill(21320)]), 0, 1e-4) && g.rate > 42 && g.rate < 43, "B's extra 50 per kW returns 42.6 percent a year in lower yearly cost", String(g.rate));
const back = F.against(B, flex, d, flat);
check(back.more === "a" && near(back.rate, g.rate, 1e-9) && near(back.bill, 21320) && near(back.pv, -g.pv), "set the other way round, the dearer upfront is A's and the rate is the same");
check(F.against(d, flat, { ...B, life: 10 }, flex).rate === null && F.against(d, flat, { ...B, life: 10 }, flex).sameYears === false, "no rate is stated when the two count different years");
check(F.against(d, flat, { ...d, run: 1 }, flex).more === null && F.against(d, flat, { ...d, run: 1 }, flex).rate === null, "and none when neither costs more upfront");
check(F.against(d, flat, { ...d, pue: 1.2, upfront: 500 }, flat).rate === null && near(F.against(d, flat, { ...d, pue: 1.2, upfront: 500 }, flat).bill, 0) && F.against(d, flat, { ...d, pue: 1.2, upfront: 500 }, flat).gpuHours > 0,
  "a lower overhead ratio changes the GPUs, not the energy bought: the year's cost is the same, more GPU-hours run, and no rate is stated");
check(F.against(d, flat, { ...d, adder: 5 }, flat).evenUpfront < 0, "a B that costs more with nothing upfront has no upfront cost at which the two are equal");

// the address
const s = F.parseScenarios({ aw: "1", bh: "10", al: "12.6", ag: "99", ad: "x", v: "b", mw: "50", view: "load" }, d);
check(s.a.run === 1 && s.b.hurdle === 10 && s.a.life === 13 && s.a.gpu === 20 && s.a.adder === 0 && s.view === "b", "the address: read, bounded, whole where whole, defaulted where unreadable", JSON.stringify(s));
check(JSON.stringify(F.scenarioQuery(s, d)) === JSON.stringify([["aw", "1"], ["ag", "20"], ["al", "13"], ["bh", "10"], ["v", "b"]]), "only what differs from the defaults is written", JSON.stringify(F.scenarioQuery(s, d)));
check(F.scenarioQuery(F.parseScenarios({}, d), d).length === 0, "no parameter means the defaults, and the defaults write none");
check(F.parseScenarios({ aw: "1", bw: "1" }, d, [true, false]).a.run === 0 && F.parseScenarios({ aw: "0" }, F.defaultsOf({ run: 1, gpu: 1.3, pue: 1.56 }), [false, true]).a.run === 1, "a way of running that is not held falls back to the default");
check(JSON.stringify(F.held([flat, null])) === "[true,false]" && JSON.stringify(F.held(ways)) === "[true,true]", "which ways are held");
check(["aw", "bg", "ap", "bd", "ae", "bu", "al", "bh", "v"].every(F.isScenarioParam) && ["view", "grid", "region", "mw", "run", "n", "pct", "shift", "buy", "gpu", "pue", "ac", "bt", "a", "b"].every((k) => !F.isScenarioParam(k)), "the scenarios' parameters are told from the page's own");
check(F.carry("grid=ercot&aw=1&bh=10&v=b&mw=50&buy=rt") === "&aw=1&bh=10&v=b" && F.carry("grid=ercot&mw=50") === "", "the page's other addresses carry the scenarios");
check(F.differenceWords(d, d) === "A and B hold the same assumptions." && F.differenceWords(d, { ...d, run: 1, hurdle: 10 }) === "B: runs flexible against flat; hurdle rate 10 percent against 8.", "the row in words", F.differenceWords(d, { ...d, run: 1, hurdle: 10 }));
check(F.bound("pue", 0.5, d) === 1 && F.bound("life", 99, d) === 40 && F.bound("growth", -50, d) === -20 && F.bound("run", 7, d) === 1 && F.bound("gpu", NaN, d) === 1.3, "each value is brought inside its bounds");

// the sensitivity: eight bars, sorted, each side the all-in figure with one assumption moved by its step
const bars = F.sensitivity(d, ways);
check(bars.length === 8 && bars.every((b, i) => i === 0 || bars[i - 1].size >= b.size), "eight bars, sorted by size", bars.map((b) => b.key).join(", "));
const pue = bars.find((b) => b.key === "pue");
check(pue.down.value === 1.46 && pue.up.value === 1.66 && near(pue.down.v, F.levelGpuHour({ ...d, pue: 1.46 }, flat)) && near(pue.up.v, F.levelGpuHour({ ...d, pue: 1.66 }, flat)), "the overhead ratio by 0.1, each side recomputed");
const run = bars.find((b) => b.key === "run");
check(run.down === null && run.up.value === 1 && near(run.up.v, F.levelGpuHour({ ...d, run: 1 }, flex)), "the way of running has one step: the other way");
check(F.sensitivity({ ...d, run: 1 }, ways).find((b) => b.key === "run").down.value === 0 && F.sensitivity(d, [flat, null]).find((b) => b.key === "run").size === 0, "from flexible the step is to flat; with the other way not held there is none");
check(["adder", "upfront"].every((k) => bars.find((b) => b.key === k).down === null && bars.find((b) => b.key === k).up !== null) && bars.find((b) => b.key === "growth").down !== null, "an assumption at its lower bound has no lower step; the change of prices has both");
check(F.sensitivity({ ...d, run: 1 }, [flat, null]).length === 0, "no chart for a scenario whose own way is not held");

// the page's own files: a scenario at its defaults is the page's headline, for every grid's main region
for (const grid of Object.keys(W.INDEX.grids)) {
  const p = W.pageOf({ grid }), w = p.ways[0];
  if (!p.s12 || !w) { check(p.ways[0] === null, `${grid}: no twelve months are held, and no way is handed over`); continue; }
  const a = F.defaultsOf(p.load), res = F.resultOf(a, w);
  check(res.price === p.s12.per && res.bill === p.s12.cost && near(res.gpuHour, L.gpuHour(p.s12.per, p.x.gpu, p.x.pue), 1e-15) && near(res.gpus * p.x.mw, L.gpus(p.x.mw, p.x.gpu, p.x.pue), 1e-12) && (p.bad ? w.bad.per === p.bad.cost / p.bad.energy && w.bad.m === p.bad.m : w.bad === null),
    `${grid}, ${p.x.region}, ${p.x.buy}: at the defaults the price, the year's cost, the GPU-hour, the GPUs and the bad month are the page's`, `USD ${L.two(res.price)} per MWh, ${res.gpuHour.toFixed(4)} per GPU-hour`);
  check(near(res.level, res.price, 1e-12) && near(res.allIn, res.gpuHour, 1e-12) && res.off === null, `${grid}: the fixed price is the price, the all-in figure the GPU-hour, and a flat load has no hours off`);
  const f = W.pageOf({ grid, run: "hours", n: String(L.DEFAULTS.n), buy: p.x.buy });
  check(JSON.stringify(f.ways[0]) === JSON.stringify(p.ways[0]) && JSON.stringify(f.ways[1]) === JSON.stringify(p.ways[1]), `${grid}: the flat page and the flexible page hand over the same two ways`);
  const fx = p.ways[1];
  if (fx) {
    const o = F.offOf(a, fx);
    check(fx.per === f.s12.per && fx.down === f.s12.down && o !== null && near(o.perMwh * o.mwh, fx.flatCost - fx.cost) && fx.cost < w.cost && fx.flatCost === w.cost,
      `${grid}: the flexible way is the flexible page's own; its hours off, the energy not bought and what it would have cost add up`, `off in ${fx.down} hours, USD ${L.two(o.perMwh)} per MWh not bought`);
  } else check(!p.region.da || !L.lastTwelve(L.monthsRuled(p.files, p.x.region, p.x.buy, W.ALT, "forecast").months), `${grid}: no flexible way, because the rule cannot decide here`);
}

console.log(failed ? `\n${failed} FAILED` : "\nall passed");
process.exit(failed ? 1 : 0);
