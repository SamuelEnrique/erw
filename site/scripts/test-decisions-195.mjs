// Energy Research Warehouse (ERW) site, session 195: the arithmetic the shared decisions block rests on, with no
// browser and no table: the libraries alone.
//
//   node scripts/test-decisions-195.mjs
//
//   1. the debt payment scenario A gives the page (debtUsd) is the page's own default of before the session, to the
//      dollar, for every duration and asset at many sizes;
//   2. the old names: an older link's `fom` and `ds` (battery, generator) and `gpu` and `pue` (datacenter) are read as
//      the scenarios' assumptions; `ds` gives a capital cost at which scenario A pays exactly that; a scenario's own
//      parameter wins; an old name at its default moves nothing; the address the scenarios write holds no old name;
//   3. the battery's last twelve months end with the last complete month in the table.
// Prints one line per assertion; exits 1 if any fails.
import * as B from "../lib/batterystack.ts";
import * as BF from "../lib/battery/finance.ts";
import * as M from "../lib/merchant.ts";
import * as SF from "../lib/seller/finance.ts";
import * as DF from "../lib/datacenter/finance.ts";

let failed = 0, n = 0;
const check = (ok, what, detail = "") => { n += 1; if (!ok) failed += 1; console.log(`${ok ? "ok  " : "FAIL"} ${what}${detail ? `: ${detail}` : ""}`); };
const SIZES = [1, 7.5, 33, 50, 100, 137, 200, 250.5, 1000, 5000];

// 1: the debt payment, to the dollar
{
  const off = [];
  for (const dur of B.DURATIONS) for (const mw of SIZES) {
    const a = BF.debtUsd(BF.defaultsOf(B.COSTS[dur]), mw), b = Math.round(B.debtPerMw(dur) * mw);
    if (a !== b) off.push(`${dur} h, ${mw} MW: ${a} against ${b}`);
  }
  check(off.length === 0, "battery: scenario A's default debt payment is the page's own, to the dollar, at 3 durations and 10 sizes", off.join("; "));
  check(BF.debtUsd(BF.defaultsOf(B.COSTS[4]), 100) === 6783357, "battery, 4 hours, 100 MW: USD 6,783,357, the figure of the Method note");
  const offS = [];
  for (const k of Object.keys(M.DEFAULTS)) for (const mw of SIZES) {
    const a = SF.debtUsd(SF.defaultsOf(M.DEFAULTS[k]), mw), b = Math.round(M.debtPerMw(k) * mw);
    if (a !== b) offS.push(`${k}, ${mw} MW: ${a} against ${b}`);
  }
  check(offS.length === 0, "generator: scenario A's default debt payment is the page's own, to the dollar, for 5 assets at 10 sizes", offS.join("; "));
  check(SF.debtUsd(SF.defaultsOf(M.DEFAULTS.solar), 100) === 7078769, "generator, solar, 100 MW: USD 7,078,769, the figure of the Method note");
  // the page's inputs take the same default from an address that names nothing
  check(B.inputsOf({}).ds === BF.debtUsd(BF.defaultsOf(B.COSTS[4]), 100) && M.inputsOf({}).ds === SF.debtUsd(SF.defaultsOf(M.DEFAULTS.solar), 100), "and it is what inputsOf gave the bare address");
}

// 2: the old names
{
  const d = BF.defaultsOf(B.COSTS[4]), steps = BF.ONLY_DEFAULT;
  let s = BF.parseScenarios({ fom: "30", ds: "4000000" }, d, steps, 100);
  check(s.a.fom === 30 && BF.debtUsd(s.a, 100) === 4000000 && s.a.share === 60 && s.a.rate === 8 && s.a.term === 20, "battery: fom is A's fixed O&M, and ds gives a capital cost at which A pays exactly USD 4,000,000", `capex ${s.a.capex}`);
  check(JSON.stringify(s.b) === JSON.stringify(d), "battery: scenario B is left at the defaults, as it was");
  const q = BF.scenarioQuery(s, d);
  check(q.every(([k]) => !BF.isOldParam(k) && BF.isScenarioParam(k)) && q.some(([k]) => k === "af") && q.some(([k]) => k === "ac") && BF.isOldParam("fom") && BF.isOldParam("ds") && !BF.isOldParam("mw"),
    "battery: the address the scenarios write holds A's own names and no old name", q.map(([k, v]) => `${k}=${v}`).join("&"));
  const again = BF.parseScenarios(Object.fromEntries(q), d, steps, 100);
  check(BF.debtUsd(again.a, 100) === 4000000 && again.a.fom === 30, "battery: that address opens the same debt payment and fixed O&M");
  s = BF.parseScenarios({ fom: String(d.fom), ds: String(BF.debtUsd(d, 100)) }, d, steps, 100);
  check(JSON.stringify(s.a) === JSON.stringify(d) && BF.scenarioQuery(s, d).length === 0, "battery: an older link that held the defaults moves nothing and writes nothing");
  s = BF.parseScenarios({ ac: "1300", ds: "4000000", af: "25", fom: "30" }, d, steps, 100);
  check(s.a.capex === 1300 && s.a.fom === 25, "battery: a scenario's own parameter wins over an old name (ac over ds, af over fom)");
  s = BF.parseScenarios({ ds: "4000000" }, d, steps);
  check(s.a.capex === d.capex, "battery: with no size given, ds is not read");
  s = BF.parseScenarios({ ds: "4000000", as: "0" }, d, steps, 100);
  check(s.a.capex === d.capex && s.a.share === 0, "battery: with no debt share, ds cannot be met by a capital cost and is not read");
  let off = 0, seen = 0;
  for (const mw of SIZES) for (const k of [0.25, 0.5, 0.9, 1.1, 1.7, 3]) for (const as of [undefined, "40", "75"]) {
    const ds = Math.round(BF.debtUsd(d, mw) * k);
    const p = BF.parseScenarios({ ds: String(ds), ...(as ? { as } : {}) }, d, steps, mw);
    if (p.a.capex >= BF.SPECS.capex.max) continue;      // a payment beyond the capital cost's bound is clipped
    seen += 1;
    if (BF.debtUsd(p.a, mw) !== ds) off += 1;
  }
  check(off === 0 && seen > 150, `battery: over ${seen} older links, A's debt payment is the link's to the dollar`, `${off} off`);

  const ds0 = SF.defaultsOf(M.DEFAULTS.solar);
  let t = SF.parseScenarios({ fom: "20", ds: "5000000" }, ds0, 100);
  check(t.a.fom === 20 && SF.debtUsd(t.a, 100) === 5000000 && JSON.stringify(t.b) === JSON.stringify(ds0), "generator: fom is A's fixed O&M, ds gives a capital cost at which A pays exactly USD 5,000,000, and B is left as it was", `capex ${t.a.capex}`);
  t = SF.parseScenarios({ fom: String(ds0.fom), ds: String(SF.debtUsd(ds0, 100)) }, ds0, 100);
  check(JSON.stringify(t.a) === JSON.stringify(ds0) && SF.scenarioQuery(t, ds0).length === 0, "generator: an older link that held the defaults moves nothing and writes nothing");
  t = SF.parseScenarios({ ac: "1500", ds: "5000000", af: "9", fom: "20" }, ds0, 100);
  check(t.a.capex === 1500 && t.a.fom === 9 && SF.isOldParam("ds") && SF.isOldParam("fom") && !SF.isOldParam("hr"), "generator: a scenario's own parameter wins over an old name");
  // session 186's finding: a debt payment kept from another size. The link opens the payment it holds.
  t = SF.parseScenarios({ ds: "3539385" }, ds0, 200);
  check(SF.debtUsd(t.a, 200) === 3539385 && t.a.capex < ds0.capex, "generator: a debt payment kept from another size is still the payment the link opens");

  const dd = DF.defaultsOf({ run: DF.FLAT, gpu: 1.3, pue: 1.56 });
  let u = DF.parseScenarios({ gpu: "1", pue: "1.2" }, dd);
  check(u.a.gpu === 1 && u.b.gpu === 1 && u.a.pue === 1.2 && u.b.pue === 1.2, "datacenter: gpu and pue are both scenarios' power per GPU and overhead ratio, as \"Your load\" was the default of both");
  const uq = DF.scenarioQuery(u, dd);
  check(uq.every(([k]) => !DF.isOldParam(k) && DF.isScenarioParam(k)) && uq.map(([k]) => k).sort().join() === "ag,ap,bg,bp" && DF.isOldParam("gpu") && DF.isOldParam("pue") && !DF.isOldParam("mw"),
    "datacenter: the address the scenarios write holds their own names and no old name", uq.map(([k, v]) => `${k}=${v}`).join("&"));
  u = DF.parseScenarios({ gpu: "1", bg: "2", pue: "1.2", ap: "1.1" }, dd);
  check(u.a.gpu === 1 && u.b.gpu === 2 && u.a.pue === 1.1 && u.b.pue === 1.2, "datacenter: a scenario's own parameter wins over an old name");
  u = DF.parseScenarios({ gpu: "1.3", pue: "1.56" }, dd);
  check(DF.scenarioQuery(u, dd).length === 0, "datacenter: an older link that held the defaults writes nothing");
  check(dd.gpu === 1.3 && dd.pue === 1.56, "datacenter: the two defaults are the page's cited ones");
}

// 3: the last twelve months end with the last complete month
{
  const days = (y, m) => new Date(Date.UTC(y, m, 0)).getUTCDate();
  const rows = (last) => {
    const out = [];
    const put = (y, m, held, left) => {
      const ts = `${y}-${String(m).padStart(2, "0")}-01T00:00:00Z`, pre = "foresight_4h_";
      for (const [k, v] of [["days_held", held], ["days_left_out", left], ["days_in_month", days(y, m)], ["revenue_total_usd_per_mw", 1000 * held], ["revenue_energy_usd_per_mw", 600 * held], ["revenue_ancillary_usd_per_mw", 400 * held]])
        out.push({ variable: pre + k, ts_utc: ts, value: v });
    };
    for (let i = 0; i < 13; i++) { const y = 2025 + Math.floor((8 + i) / 12), m = ((8 + i) % 12) + 1; put(y, m, days(y, m), 0); }   // September 2025 to September 2026, whole
    put(2026, 10, last[0], last[1]);                                                                                                 // October 2026, 31 days
    return out;
  };
  const twelve = (last) => { const ms = B.monthsOf(rows(last), "foresight", 4); return { ms, l: B.lastTwelve(ms), w: B.last36(ms) }; };
  let r = twelve([27, 0]);
  check(!r.ms.at(-1).held && r.l[11].m === "2026-09" && r.l[0].m === "2025-10", "27 of 31 days: the month is not held; the window ends September 2026");
  r = twelve([28, 0]);
  check(r.ms.at(-1).held && !r.ms.at(-1).whole && r.l[11].m === "2026-09" && r.w.to === "2026-09", "28 of 31 days: the month is held and not whole; the window still ends September 2026 (before session 195 it ended October)");
  r = twelve([30, 0]);
  check(r.l[11].m === "2026-09", "30 of 31 days: still September");
  r = twelve([31, 0]);
  check(r.ms.at(-1).whole && r.l[11].m === "2026-10" && r.l[0].m === "2025-11" && r.w.to === "2026-10", "31 of 31 days: the window ends October 2026, and the bad month's window with it");
  r = twelve([30, 1]);
  check(r.ms.at(-1).whole && r.l[11].m === "2026-10", "30 days solved and 1 left out: every day is in the table, so the month is whole");
  r = twelve([20, 11]);
  check(r.ms.at(-1).whole && !r.ms.at(-1).held && r.l[11].m === "2026-09", "a whole month under 90 percent held is not counted, as before");
  // the page's stat for the check keys follows the same window
  const ms = B.monthsOf(rows([28, 0]), "foresight", 4), x = B.inputsOf({});
  check(B.stat(rows([28, 0]), [], x, "l12_kw:total") === B.sumOf(B.lastTwelve(ms), "total") / 1000, "the check key's last twelve months are the same window");
}

console.log(failed ? `\ntest-decisions-195 FAILED: ${failed} of ${n}` : `\ntest-decisions-195: all ${n} passed`);
process.exit(failed ? 1 : 0);
