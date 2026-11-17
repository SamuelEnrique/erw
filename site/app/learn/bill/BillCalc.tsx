"use client";
// Session 43: the bill explainer's calculator. The rates are data/bill_rules.json (each cites its tariff page); the
// arithmetic is lib/bill.ts. The wholesale reference arrives from the server (cost_of_power_monthly).
// Session 52: five bills: PG&E (E-TOU-C), SCE (TOU-D-4-9PM), SDG&E (TOU-DR1), Oncor and CenterPoint.
// Session 7533 (chain 304): `first`, the bill the calculator opens on (the page passes none: PG&E, as before), so a script
// can draw each of the five without a click (site/scripts/bill-figures.mjs, replication/bill/). And the SCE summer line
// under the super off-peak share: SCE's summer has no super off-peak hours, so the share is billed in winter only.
// Session 7547 (chain 304, part B, the read as a household with its own bill in hand): (1) `history`, every month of the
// bill's wholesale price held, newest first, and a field "Wholesale price, month" (default: the month the cards use), so a
// reader sets the month of the bill in hand, and a student sees the share move with the month; the bill's lines stay at
// the rates as read. (2) Under the bar, the bill's own power line beside the wholesale energy (PG&E's and SCE's
// "Generation", the Texas retailer's energy charge; SDG&E's tariff splits none out), because the "Everything else" of the
// bar holds the rest of that line too, and the sentence said only wires, programs and fixed charges.
import { Fragment, useMemo, useState } from "react";
import { Tip } from "@/components/tool/ToolPage";
import {
  BILL_KEYS, billCA, billTDSP, billTOU, billTX, clampShares, defaultsCA, defaultsTDSP, defaultsTOU, defaultsTX, type BillKey, type CAInput, type Line, type TOUInput, type TXInput,
} from "@/lib/bill";

/** Session 7547: the line of each bill that charges for the power itself (its id in lib/bill.ts and the rules file), and
 * who sets its price. SDG&E's TOU-DR1 is one total line (the commodity rate inside it), so it has none. */
export const POWER_LINE: Record<BillKey, { id: string; who: string } | null> = {
  CA: { id: "gen", who: "PG&E" },
  SCE: { id: "sce_generation", who: "SCE" },
  SDGE: null,
  TX: { id: "rep_energy", who: "the retail electric provider" },
  TXC: { id: "txc_energy", who: "the retail electric provider" },
};
export type WholesaleMonth = { month: string; price: number; partial: boolean };

const usd = (v: number) => `${v < 0 ? "-" : ""}$${Math.abs(v).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const field = "w-full border border-rule bg-panel px-2 py-1 text-sm";
const pct = (v: string) => Math.min(100, Math.max(0, Number(v))) / 100;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function BillCalc({ rules, wholesale, first = "CA", history = {}, firstMonth = null }: { rules: any; wholesale: Record<string, { price: number; month: string; partial: boolean } | null>; first?: BillKey; history?: Record<string, WholesaleMonth[]>; firstMonth?: string | null }) {
  const [key, setKey] = useState<BillKey>(first);
  // session 7547: the month the reader chose for the wholesale price; null is the default (the cards' month). `firstMonth`
  // lets a script draw a chosen month without a click, as `first` does for the bill
  const [month, setMonth] = useState<string | null>(firstMonth);
  const [ca, setCa] = useState<CAInput>(defaultsCA(rules));
  const [tou, setTou] = useState<Record<"SCE" | "SDGE", TOUInput>>({ SCE: defaultsTOU(rules, "SCE"), SDGE: defaultsTOU(rules, "SDGE") });
  const [tx, setTx] = useState<Record<"TX" | "TXC", TXInput>>({ TX: defaultsTX(rules), TXC: defaultsTDSP(rules, "TXC") });
  const bill = useMemo(() => (key === "CA" ? billCA(rules, ca) : key === "SCE" || key === "SDGE" ? billTOU(rules, key, tou[key]) : key === "TX" ? billTX(rules, tx.TX) : billTDSP(rules, key, tx.TXC)),
    [rules, key, ca, tou, tx]);
  const b = rules.bills[key];
  const months = history[key] ?? [];
  const picked = month !== null ? months.find((m) => m.month === month) ?? null : null;
  const w = picked ?? wholesale[key];
  const wholesaleUsd = w ? (bill.kwh * w.price) / 1000 : null;
  const src = (id: string) => rules.sources[id];
  const groups: Record<string, Line[]> = {};
  for (const l of bill.lines) (groups[l.group ?? "Other"] ??= []).push(l);
  const share = wholesaleUsd !== null && bill.total > 0 ? Math.max(0, Math.min(1, wholesaleUsd / bill.total)) : null;
  // session 7547: the bill's own power line, drawn beside the wholesale energy under the bar
  const pl = POWER_LINE[key];
  const plLine = pl ? bill.lines.find((l) => l.id === pl.id) : undefined;
  const power = pl && plLine ? { line: plLine, who: pl.who } : null;
  const kwh = key === "CA" ? ca.kwh : key === "SCE" || key === "SDGE" ? tou[key].kwh : tx[key].kwh;
  const setKwh = (v: number) => {
    if (key === "CA") setCa({ ...ca, kwh: v });
    else if (key === "SCE" || key === "SDGE") setTou({ ...tou, [key]: { ...tou[key], kwh: v } });
    else setTx({ ...tx, [key]: { ...tx[key], kwh: v } });
  };
  // session 261: one press puts the chosen bill's inputs back to its defaults (docs/brand.md, section 7); the other
  // four bills keep what the reader typed
  const reset = () => {
    setMonth(null);  // session 7547: the wholesale month back to the cards' month
    if (key === "CA") setCa(defaultsCA(rules));
    else if (key === "SCE" || key === "SDGE") { setTou({ ...tou, [key]: defaultsTOU(rules, key) }); setHeld(null); }
    else setTx({ ...tx, [key]: key === "TX" ? defaultsTX(rules) : defaultsTDSP(rules, key) });
  };
  const t = key === "SCE" || key === "SDGE" ? tou[key] : null;
  const setT = (x: Partial<TOUInput>) => { if (key === "SCE" || key === "SDGE") setTou({ ...tou, [key]: { ...tou[key], ...x } }); };
  // session 288 (ruling 10b): the two shares are clamped at 100 together; the line under them says when a share was held
  const [held, setHeld] = useState<string | null>(null);
  const setShare = (typed: "peakShare" | "superShare", v: number) => {
    if (key !== "SCE" && key !== "SDGE") return;
    const next = clampShares(tou[key], typed, v);
    setHeld(next[typed] < v ? `Held at ${Math.round(next[typed] * 1000) / 10} percent: the two shares together can be at most 100 percent.` : null);
    setTou({ ...tou, [key]: next });
  };

  return (
    <div>
      <div className="mb-3 flex flex-wrap gap-2 text-sm">
        {BILL_KEYS.map((s) => (
          <button key={s} onClick={() => setKey(s)} className={`border px-3 py-1 ${key === s ? "border-accent text-accent" : "border-rule"}`}>{rules.bills[s].name}</button>
        ))}
      </div>
      <p className="mb-3 max-w-3xl text-xs text-muted">{b.note}</p>
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.6fr)]">
        <div className="space-y-3 text-sm">
          <label className="flex flex-col">Electricity used this month, kWh (default 600, an assumption)
            <input type="number" min={0} step={10} value={kwh} onChange={(e) => setKwh(Math.max(0, Number(e.target.value)))} className={field} />
          </label>
          {key === "CA" ? (
            <>
              <label className="flex flex-col">Share of use from 4 to 9 p.m., percent (default 20, the tariff&apos;s own example)
                <input type="number" min={0} max={100} step={5} value={Math.round(ca.peakShare * 100)} onChange={(e) => setCa({ ...ca, peakShare: pct(e.target.value) })} className={field} />
              </label>
              <label className="flex flex-col">Season
                <select value={ca.season} onChange={(e) => setCa({ ...ca, season: e.target.value as "summer" | "winter" })} className={field}>
                  {Object.entries(rules.bills.CA.seasons).map(([k, s]) => <option key={k} value={k}>{(s as { label: string }).label}</option>)}
                </select>
              </label>
              <label className="flex flex-col" data-territory-tip="7547"><span>Baseline territory (default T, San Francisco)
                {/* session 7547: a reader outside San Francisco (Fresno, in the read's cases) is told where the letter is found */}
                <Tip id="bill-territory-7547" label="which baseline territory a home is in">
                  PG&amp;E&apos;s Electric Preliminary Statement Part A gives each county&apos;s territory, by elevation where a county spans several:
                  for example, {rules.bills.CA.default_territory.examples.words} ({rules.bills.CA.default_territory.examples.sheet}: &quot;{rules.bills.CA.default_territory.examples.quote}&quot;),
                  and San Francisco is all T. The daily quantities are Sheet 5&apos;s, Code B (basic, not all-electric).
                </Tip></span>
                <select value={ca.territory} onChange={(e) => setCa({ ...ca, territory: e.target.value })} className={field}>
                  {Object.entries(rules.bills.CA.baseline_quantities.code_B).map(([k, q]) => <option key={k} value={k}>Territory {k}: {(q as number[])[0]} kWh a day in summer, {(q as number[])[1]} in winter</option>)}
                </select>
              </label>
              <label className="flex flex-col">Income tier (default 3: no CARE or FERA discount)
                <select value={ca.tier} onChange={(e) => setCa({ ...ca, tier: e.target.value })} className={field}>
                  {Object.entries(rules.bills.CA.base_services.tiers).map(([k, r]) => <option key={k} value={k}>Tier {k}: ${String(r)} a day</option>)}
                </select>
              </label>
              <label className="block"><input type="checkbox" checked={ca.climateCredit} onChange={(e) => setCa({ ...ca, climateCredit: e.target.checked })} /> This bill carries the California Climate Credit (August or September)</label>
            </>
          ) : t ? (
            <>
              <label className="flex flex-col">Share of use from 4 to 9 p.m., percent ({b.defaults.labels.peak_share})
                <input type="number" min={0} max={100} step={1} value={Math.round(t.peakShare * 1000) / 10} onChange={(e) => setShare("peakShare", pct(e.target.value))} className={field} />
              </label>
              <label className="flex flex-col">Share in super off-peak hours, percent ({b.defaults.labels.super_share})
                {key === "SCE" && t.season === "summer" ? (
                  <span className="text-xs" data-sce-summer-super="1">Not billed in summer: SCE&apos;s summer has no super off-peak hours (8 a.m. to 4 p.m. is off-peak then), so this share moves nothing until the season is winter. It still counts toward the 100 percent the two shares can hold.</span>
                ) : null}
                <input type="number" min={0} max={100} step={1} value={Math.round(t.superShare * 1000) / 10} onChange={(e) => setShare("superShare", pct(e.target.value))} className={field} />
              </label>
              {held ? <p className="text-xs text-muted" role="status">{held}</p> : null}
              <label className="flex flex-col">Season
                <select value={t.season} onChange={(e) => setT({ season: e.target.value as "summer" | "winter" })} className={field}>
                  {Object.entries(b.seasons).map(([k, s]) => <option key={k} value={k}>{(s as { label: string }).label}</option>)}
                </select>
              </label>
              {key === "SCE" ? (
                <>
                  <label className="flex flex-col">Baseline region ({b.defaults.labels.region})
                    <select value={t.region} onChange={(e) => setT({ region: e.target.value })} className={field}>
                      {Object.entries(b.baseline_quantities.basic).map(([k, q]) => <option key={k} value={k}>Region {k}: {(q as number[])[0]} kWh a day in summer, {(q as number[])[1]} in winter</option>)}
                    </select>
                  </label>
                  <label className="block"><input type="checkbox" checked={!!t.climateCredit} onChange={(e) => setT({ climateCredit: e.target.checked })} /> This bill carries the California Climate Credit</label>
                </>
              ) : (
                <label className="flex flex-col">Your baseline allowance for this bill, kWh (on your SDG&amp;E bill; default 0, so no credit)
                  <input type="number" min={0} step={10} value={t.baselineKwh ?? 0} onChange={(e) => setT({ baselineKwh: Math.max(0, Number(e.target.value)) })} className={field} />
                </label>
              )}
            </>
          ) : (
            <label className="flex flex-col">Your plan&apos;s energy charge, USD per kWh (default ${b.energy_default.rate}, an assumption)
              <input type="number" min={0} step={0.001} value={tx[key as "TX" | "TXC"].energyRate} onChange={(e) => setTx({ ...tx, [key]: { ...tx[key as "TX" | "TXC"], energyRate: Math.max(0, Number(e.target.value)) } })} className={field} />
              <span className="mt-1 text-xs text-muted">Default: {b.energy_default.derivation}.</span>
            </label>
          )}
          {months.length ? (
            <label className="flex flex-col" data-bill-month="7547">
              <span>Wholesale price, month (default: the latest complete month, as on the cards)
                <Tip id="bill-month-7547" label="the wholesale price's month">
                  Set the month of the bill in hand. Only the wholesale price, and so the wholesale energy and its share, change with
                  the month: every line of the bill stays at the tariff&apos;s rates as read ({b.iso === "ercot" ? "Oncor 2026-09-30, CenterPoint 2026-10-01" : "PG&E 2026-09-30, SCE and SDG&E 2026-10-01"}), and a bill of an earlier
                  month was charged that month&apos;s rates, which this page does not hold. A month marked partial lacks a price in some hours.
                  Source: the ERW table cost_of_power_monthly, {b.wholesale_label ?? "ERCOT's hub average"}, the load-weighted real-time price.
                </Tip>
              </span>
              <select value={picked ? picked.month : ""} onChange={(e) => setMonth(e.target.value === "" ? null : e.target.value)} className={field}>
                <option value="">{wholesale[key] ? `${wholesale[key]!.month}, the default` : "the default"}</option>
                {months.map((m) => <option key={m.month} value={m.month}>{m.month}: ${m.price.toFixed(2)} per MWh{m.partial ? " (partial)" : ""}</option>)}
              </select>
            </label>
          ) : null}
          <button type="button" onClick={reset} className="border border-rule px-3 py-1">Reset this bill to its defaults</button>
        </div>

        <div className="text-sm">
          {/* session 2403: the table in its own scroll container, as every table of the site at 390 px (check-390.mjs) */}
          <div className="overflow-x-auto">
          <table className="w-full">
            <caption className="sr-only">The bill, line by line, with its total</caption>
            <tbody>
              {Object.entries(groups).map(([g, ls]) => (
                <Fragment key={g}>
                  {/* session 7547: in Texas the wires company's lines together, the one sum a retailer's bill passes through */}
                  {(key === "TX" || key === "TXC") && g.startsWith("Delivery") ? (
                    <tr><th scope="rowgroup" className="pt-2 text-left text-xs font-normal uppercase tracking-wide text-muted">{g}<Tip id={`bill-delivery-${key}-7547`} label="the delivery lines together">Every line of {key === "TX" ? "Oncor" : "CenterPoint"} below, added: the delivery charges a retail electric provider passes through to the customer, which a retailer&apos;s bill may show as one sum. The energy charge above is the retailer&apos;s own.</Tip></th><td className="pt-2 text-right font-mono text-xs" data-group-sum={g}>{usd(ls.reduce((a, l) => a + l.amount, 0))}</td></tr>
                  ) : (
                    <tr><th scope="rowgroup" colSpan={2} className="pt-2 text-left text-xs font-normal uppercase tracking-wide text-muted">{g}</th></tr>
                  )}
                  {ls.map((l) => (
                    <tr key={l.id} className="border-t border-rule align-top">
                      <th scope="row" className="py-1 pr-2 text-left font-normal">
                        <details>
                          <summary className="cursor-pointer">{l.name}</summary>
                          <p className="text-xs">{l.what} <span className="text-muted">Why: {l.why}</span></p>
                          <p className="text-xs text-muted">{l.detail}. Effective {l.effective}. &quot;{l.quote}&quot; (<a href={src(l.cite)?.url}>{src(l.cite)?.title}</a>)</p>
                        </details>
                      </th>
                      <td className="py-1 text-right font-mono">{usd(l.amount)}</td>
                    </tr>
                  ))}
                </Fragment>
              ))}
              <tr className="border-t-2 border-ink font-semibold"><th scope="row" className="py-1 text-left">Total</th><td className="text-right font-mono">{usd(bill.total)}</td></tr>
              <tr><th scope="row" className="text-left text-xs font-normal text-muted">Per kWh, all in</th><td className="text-right font-mono text-xs text-muted">{bill.kwh ? usd(bill.total / bill.kwh) : ""}</td></tr>
            </tbody>
          </table>
          </div>
          {share !== null && wholesaleUsd !== null && w ? (
            <div className="mt-4">
              <div className="mb-1 flex h-5 w-full overflow-hidden border border-rule" role="img" aria-label={`Wholesale energy ${Math.round(share * 100)} percent of the bill`}>
                <div style={{ width: `${share * 100}%`, background: "var(--color-accent)" }} />
                <div style={{ width: `${(1 - share) * 100}%`, background: "var(--color-rule)" }} />
              </div>
              <p className="text-xs">
                <span className="text-accent">Wholesale energy {usd(wholesaleUsd)}, {Math.round(share * 100)} percent</span>: {bill.kwh} kWh at the load-weighted real-time price of {b.wholesale_label ?? (b.iso === "ercot" ? "ERCOT's hub average" : "the ISO's zone")}, ${w.price.toFixed(2)} per MWh in {w.month}{w.partial ? (picked ? " (a partial month)" : " (a partial month, the latest held)") : ""}. <span className="text-muted">Everything else, {usd(bill.total - wholesaleUsd)}: {power ? "the rest of the bill's power line (below), " : key === "SDGE" ? "the rest of the power, inside SDG&E's one line, " : ""}the wires and poles that carry power to the home, the high-voltage grid, fixed charges, state programs and credits.</span>
              </p>
              {power ? (
                <p className="mt-1 text-xs" data-power-line={power.line.id}>
                  The bill&apos;s own power line: <span data-power-usd={power.line.amount}>{power.line.name} {usd(power.line.amount)}, {Math.round((power.line.amount / bill.total) * 100)} percent of the bill</span>, beside the wholesale energy&apos;s {usd(wholesaleUsd)}.
                  <Tip id="bill-power-7547" label="the power line beside the wholesale energy">
                    The power line is what {power.who} charges for the power. {b.iso === "ercot"
                      ? "It is the plan's price, set by the retailer, which pays for the power the retailer buys (much of it ahead, at fixed prices) and the retailer's own costs."
                      : `It is the tariff's generation rate, which pays for all the power ${power.who} buys and makes over the year (its contracts, its own plants, capacity held for the hottest hours), not the hour's market price alone.`}
                    {" "}The wholesale energy is the same kWh at the grid&apos;s real-time market price; the difference between the two is part of &quot;Everything else&quot;. Source: the line&apos;s own tariff passage (open it in the table) and the ERW table cost_of_power_monthly.
                  </Tip>
                </p>
              ) : key === "SDGE" ? (
                <p className="mt-1 text-xs" data-power-line="none">
                  SDG&amp;E&apos;s tariff gives the power and the wires together in one line (its commodity rate is inside the total), so no power line of this bill is set beside the wholesale energy.
                </p>
              ) : null}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
