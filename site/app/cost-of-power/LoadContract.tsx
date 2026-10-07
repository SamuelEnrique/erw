"use client";
// Session 138: the optional contract of /cost-of-power, the mirror of the battery page's. The two terms are this
// component's state and nothing else: never in the URL, never in a request, never in storage or a log. The result is
// computed in the browser from the twelve months already on the page (lib/datacenter.ts, contractResult).
import { createContext, useContext, useState, type ReactNode } from "react";
import { contractResult, two, usdShort } from "@/lib/datacenter";

type Terms = { share: string; price: string };
const Ctx = createContext<{ t: Terms; set: (t: Terms) => void } | null>(null);

export function ContractProvider({ children }: { children: ReactNode }) {
  const [t, set] = useState<Terms>({ share: "", price: "" });
  return <Ctx.Provider value={{ t, set }}>{children}</Ctx.Provider>;
}

const field = "w-full border border-rule bg-white px-2 py-1 text-sm";

export function ContractInputs() {
  const c = useContext(Ctx)!;
  const on = (k: keyof Terms) => (e: React.ChangeEvent<HTMLInputElement>) => c.set({ ...c.t, [k]: e.target.value });
  // no form and no field names: nothing here can be submitted
  return (
    <div className="space-y-3 text-sm" data-contract-inputs="1">
      <label className="block"><span className="mb-1 block font-semibold">Share of the energy contracted, percent</span>
        <input type="number" min={0} max={100} step="any" inputMode="decimal" autoComplete="off" value={c.t.share} onChange={on("share")} className={field} data-contract="share" />
      </label>
      <label className="block"><span className="mb-1 block font-semibold">Price, USD per MWh</span>
        <input type="number" min={0} step="any" inputMode="decimal" autoComplete="off" value={c.t.price} onChange={on("price")} className={field} data-contract="price" />
      </label>
      <p className="text-xs leading-snug text-muted">Computed on this device. Nothing you type here is sent or stored.</p>
    </div>
  );
}

const usd = (v: number) => `USD ${usdShort(Math.round(v))}`;
const per = (v: number | null) => (v === null ? "not held yet" : `USD ${two(v)} per MWh`);

/** `l12`: the last twelve months of the load, per MW (cost in USD, energy in MWh); `bad`: the bad month's cost per MWh. */
export function ContractResult({ l12, mw, bad, span }: { l12: { cost: number; energy: number } | null; mw: number; bad: number | null; span: string | null }) {
  const c = useContext(Ctx)!;
  const share = Number(c.t.share), price = Number(c.t.price);
  const ready = c.t.share !== "" && c.t.price !== "" && Number.isFinite(share) && Number.isFinite(price) && share >= 0 && share <= 100 && price >= 0;
  if (!ready) {
    return <p className="text-sm text-muted" data-contract-result="empty">Enter a share and a price under &quot;Your contract&quot; to see the load with a contract. The terms stay on this device.</p>;
  }
  if (!l12) {
    return <p className="text-sm text-muted" data-contract-result="empty"><span className="cursor-help border-b border-dotted border-muted italic" title="A contract is set against the last twelve months of market cost, and twelve complete months are not held for this region and market.">not held yet</span></p>;
  }
  const r = contractResult(l12, mw, { share, price });
  const s = share / 100;
  const rows: [string, ReactNode, string][] = [
    ["Contracted energy, a year", usd(r.contracted), `${share} percent of ${Math.round(r.mwh).toLocaleString("en-US")} MWh at USD ${price} per MWh`],
    ["Market cost of the rest", usd(r.market), `${100 - share} percent of the last twelve months' market cost${span ? `, ${span}` : ""}`],
    ["With the contract", <>{usd(r.total)}<div className="text-xs font-normal text-muted">{per(r.per)}</div></>, "the contracted share at its price, the rest at the market's"],
    ["Without it", <>{usd(r.without)}<div className="text-xs font-normal text-muted">{per(r.perWithout)}</div></>, "the same twelve months, market only"],
    ["A bad month, with the contract", per(bad === null ? null : s * price + (1 - s) * bad), bad === null ? "no bad month is held" : `the contracted share at its price, the rest at the bad month's USD ${two(bad)} per MWh`],
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
    </div>
  );
}
