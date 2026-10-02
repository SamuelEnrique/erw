"use client";
// Session 67: the optional contract of /cost-of-power/battery. The three terms are this component's state and nothing
// else: never in the URL, never in a request, never in storage or a log. The result is computed in the browser from
// the monthly table already on the page (lib/batterystack.ts, contractResult).
import { createContext, useContext, useState, type ReactNode } from "react";
import { contractResult, monthName, usdShort, type Inputs, type Month } from "@/lib/batterystack";

type Terms = { share: string; price: string; end: string };
const Ctx = createContext<{ t: Terms; set: (t: Terms) => void } | null>(null);

export function ContractProvider({ children }: { children: ReactNode }) {
  const [t, set] = useState<Terms>({ share: "", price: "", end: "" });
  return <Ctx.Provider value={{ t, set }}>{children}</Ctx.Provider>;
}

const field = "w-full border border-rule bg-white px-2 py-1 text-sm";

export function ContractInputs() {
  const c = useContext(Ctx)!;
  const on = (k: keyof Terms) => (e: React.ChangeEvent<HTMLInputElement>) => c.set({ ...c.t, [k]: e.target.value });
  // no form and no field names: nothing here can be submitted
  return (
    <div className="space-y-3 text-sm" data-contract-inputs="1">
      <label className="block"><span className="mb-1 block font-semibold">Share contracted, percent</span>
        <input type="number" min={0} max={100} step="any" inputMode="decimal" autoComplete="off" value={c.t.share} onChange={on("share")} className={field} data-contract="share" />
      </label>
      <label className="block"><span className="mb-1 block font-semibold">Price, USD per kW-month</span>
        <input type="number" min={0} step="any" inputMode="decimal" autoComplete="off" value={c.t.price} onChange={on("price")} className={field} data-contract="price" />
      </label>
      <label className="block"><span className="mb-1 block font-semibold">Contract end, month and year</span>
        <input type="month" autoComplete="off" value={c.t.end} onChange={on("end")} className={field} data-contract="end" />
      </label>
      <p className="text-xs leading-snug text-muted">Computed on this device. Nothing you type here is sent or stored.</p>
    </div>
  );
}

const ratio = (v: number | null) => (v === null ? "not held" : `${v.toFixed(2)} times`);
const usd = (v: number | null) => (v === null ? "not held" : `USD ${usdShort(Math.round(v))}`);

export function ContractResult({ ms, x }: { ms: Month[]; x: Inputs }) {
  const c = useContext(Ctx)!;
  const share = Number(c.t.share), price = Number(c.t.price);
  const ready = c.t.share !== "" && c.t.price !== "" && Number.isFinite(share) && Number.isFinite(price) && share >= 0 && share <= 100 && price >= 0;
  if (!ready) {
    return <p className="text-sm text-muted" data-contract-result="empty">Enter a share and a price under &quot;Your contract&quot; to see the battery with a contract. The terms stay on this device.</p>;
  }
  const r = contractResult(ms, x, { share, price, end: c.t.end });
  const end = /^\d{4}-\d{2}$/.test(c.t.end) ? c.t.end : null;
  const rows: [string, string, string][] = [
    ["Contracted income a year", usd(r.contracted), `${share} percent of ${x.mw} MW at USD ${price} per kW-month, twelve months`],
    ["Market income on the uncontracted share", usd(r.marketAverage), `${100 - share} percent of an average year of market revenue`],
    ["Debt coverage with the contract", ratio(r.coverageWith), r.last ? `the twelve months to ${monthName(r.last)}: contract plus market on the rest, less fixed O&M, over the debt payments` : "no twelve consecutive months are held"],
    ["Debt coverage without it", ratio(r.coverageWithout), "the same twelve months, market only"],
    [end ? `From the market after ${monthName(end)}` : "From the market after the contract ends", usd(r.afterAverage), "an average year, the whole battery in the market"],
  ];
  return (
    <div data-contract-result="shown">
      <table className="w-full border-collapse text-left text-sm tabular-nums">
        <thead><tr className="bg-accent text-white"><th scope="col" className="px-3 py-1.5 font-normal">With the contract</th><th scope="col" className="px-3 py-1.5 text-right font-normal">Result</th></tr></thead>
        <tbody>
          {rows.map(([k, v, note], i) => (
            <tr key={k} className={`border-b border-rule ${i === 2 ? "bg-paper font-semibold" : ""}`}>
              <th scope="row" className="px-3 py-1.5 font-normal">{k}<div className="text-xs font-normal text-muted">{note}</div></th>
              <td className="whitespace-nowrap px-3 py-1.5 text-right align-top">{v}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="mt-2 max-w-3xl text-xs text-muted">
        The contracted share is paid the contract price for its power, every month, and earns nothing from the market; the rest earns what the market
        paid. A real contract has availability terms, penalties and an operator&apos;s share that are not here.
      </p>
    </div>
  );
}
