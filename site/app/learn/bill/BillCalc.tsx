"use client";
// Session 43: the bill explainer's calculator. The rates are data/bill_rules.json (each cites its tariff page); the
// arithmetic is lib/bill.ts. The wholesale reference arrives from the server (cost_of_power_monthly).
import { Fragment, useMemo, useState } from "react";
import { billCA, billTX, defaultsCA, defaultsTX, type CAInput, type Line } from "@/lib/bill";

const usd = (v: number) => `${v < 0 ? "-" : ""}$${Math.abs(v).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const field = "w-full border border-rule bg-panel px-2 py-1 text-sm";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function BillCalc({ rules, wholesale }: { rules: any; wholesale: Record<string, { price: number; month: string; partial: boolean } | null> }) {
  const [state, setState] = useState<"CA" | "TX">("CA");
  const [ca, setCa] = useState<CAInput>(defaultsCA(rules));
  const [tx, setTx] = useState(defaultsTX(rules));
  const bill = useMemo(() => (state === "CA" ? billCA(rules, ca) : billTX(rules, tx)), [rules, state, ca, tx]);
  const w = wholesale[state];
  const wholesaleUsd = w ? (bill.kwh * w.price) / 1000 : null;
  const src = (id: string) => rules.sources[id];
  const groups: Record<string, Line[]> = {};
  for (const l of bill.lines) (groups[l.group ?? "Other"] ??= []).push(l);
  const share = wholesaleUsd !== null && bill.total > 0 ? Math.max(0, Math.min(1, wholesaleUsd / bill.total)) : null;

  return (
    <div>
      <div className="mb-3 flex flex-wrap gap-2 text-sm">
        {(["CA", "TX"] as const).map((s) => (
          <button key={s} onClick={() => setState(s)} className={`border px-3 py-1 ${state === s ? "border-accent text-accent" : "border-rule"}`}>{rules.bills[s].name}</button>
        ))}
      </div>
      <p className="mb-3 max-w-3xl text-xs text-muted">{rules.bills[state].note}</p>
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.6fr)]">
        <div className="space-y-3 text-sm">
          <label className="flex flex-col">Electricity used this month, kWh (default 600, an assumption)
            <input type="number" min={0} step={10} value={state === "CA" ? ca.kwh : tx.kwh}
              onChange={(e) => { const v = Math.max(0, Number(e.target.value)); state === "CA" ? setCa({ ...ca, kwh: v }) : setTx({ ...tx, kwh: v }); }} className={field} />
          </label>
          {state === "CA" ? (
            <>
              <label className="flex flex-col">Share of use from 4 to 9 p.m., percent (default 20, the tariff&apos;s own example)
                <input type="number" min={0} max={100} step={5} value={Math.round(ca.peakShare * 100)} onChange={(e) => setCa({ ...ca, peakShare: Math.min(100, Math.max(0, Number(e.target.value))) / 100 })} className={field} />
              </label>
              <label className="flex flex-col">Season
                <select value={ca.season} onChange={(e) => setCa({ ...ca, season: e.target.value as "summer" | "winter" })} className={field}>
                  {Object.entries(rules.bills.CA.seasons).map(([k, s]) => <option key={k} value={k}>{(s as { label: string }).label}</option>)}
                </select>
              </label>
              <label className="flex flex-col">Baseline territory (default T, San Francisco)
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
          ) : (
            <label className="flex flex-col">Your plan&apos;s energy charge, USD per kWh (default ${rules.bills.TX.energy_default.rate}, an assumption)
              <input type="number" min={0} step={0.001} value={tx.energyRate} onChange={(e) => setTx({ ...tx, energyRate: Math.max(0, Number(e.target.value)) })} className={field} />
              <span className="mt-1 text-xs text-muted">Default: {rules.bills.TX.energy_default.derivation}.</span>
            </label>
          )}
        </div>

        <div className="text-sm">
          <table className="w-full">
            <tbody>
              {Object.entries(groups).map(([g, ls]) => (
                <Fragment key={g}>
                  <tr><td colSpan={2} className="pt-2 text-xs uppercase tracking-wide text-muted">{g}</td></tr>
                  {ls.map((l) => (
                    <tr key={l.id} className="border-t border-rule align-top">
                      <td className="py-1 pr-2">
                        <details>
                          <summary className="cursor-pointer">{l.name}</summary>
                          <p className="text-xs">{l.what} <span className="text-muted">Why: {l.why}</span></p>
                          <p className="text-xs text-muted">{l.detail}. Effective {l.effective}. &quot;{l.quote}&quot; (<a href={src(l.cite)?.url}>{src(l.cite)?.title}</a>)</p>
                        </details>
                      </td>
                      <td className="py-1 text-right font-mono">{usd(l.amount)}</td>
                    </tr>
                  ))}
                </Fragment>
              ))}
              <tr className="border-t-2 border-ink font-semibold"><td className="py-1">Total</td><td className="text-right font-mono">{usd(bill.total)}</td></tr>
              <tr><td className="text-xs text-muted">Per kWh, all in</td><td className="text-right font-mono text-xs text-muted">{bill.kwh ? usd(bill.total / bill.kwh) : ""}</td></tr>
            </tbody>
          </table>
          {share !== null && wholesaleUsd !== null && w ? (
            <div className="mt-4">
              <div className="mb-1 flex h-5 w-full overflow-hidden border border-rule" role="img" aria-label={`Wholesale energy ${Math.round(share * 100)} percent of the bill`}>
                <div style={{ width: `${share * 100}%`, background: "var(--color-accent)" }} />
                <div style={{ width: `${(1 - share) * 100}%`, background: "var(--color-rule)" }} />
              </div>
              <p className="text-xs">
                <span className="text-accent">Wholesale energy {usd(wholesaleUsd)}, {Math.round(share * 100)} percent</span>: {bill.kwh} kWh at the load-weighted real-time price of {state === "CA" ? (rules.bills.CA.wholesale_label ?? "CAISO's NP15 zone") : "ERCOT's hub average"}, ${w.price.toFixed(2)} per MWh in {w.month}{w.partial ? " (a partial month, the latest held)" : ""}. <span className="text-muted">Everything else, {usd(bill.total - wholesaleUsd)}: the wires and poles that carry power to the home, the high-voltage grid, fixed charges, state programs and credits.</span>
              </p>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
