"use client";
// Session 145: the optional contract of /cost-of-power/seller, the mirror of the battery page's and of the datacenter
// page's. The two terms are this component's state and nothing else: never in the URL, never in a request, never in
// storage or a log. The result is computed in the browser from the twelve months already on the page, with the
// arithmetic already written (lib/datacenter.ts, contractResult: a share of the energy at the typed price, the rest at
// the market's figure for the same twelve months; lib/capture.ts, contractSpan, hands it the plant's twelve months).
import { createContext, useContext, useState, type ReactNode } from "react";
import { contractSpan, signed, two } from "@/lib/capture";
import { contractResult, usdShort } from "@/lib/datacenter";

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
const per = (v: number | null) => (v === null ? "" : `USD ${two(v)} per MWh`);

/** `energy`: the plant's last twelve months of energy, MWh per MW; `price`: what the market paid per MWh at the hub
 *  chosen over the same months. Null when the plant has no such twelve months: `why` is the reason, shown on hover. */
export function ContractResult({ plant, mw, hub, span, why }: { plant: { energy: number; price: number } | null; mw: number; hub: string; span: string | null; why: string }) {
  const c = useContext(Ctx)!;
  const share = Number(c.t.share), price = Number(c.t.price);
  const ready = c.t.share !== "" && c.t.price !== "" && Number.isFinite(share) && Number.isFinite(price) && share >= 0 && share <= 100 && price >= 0;
  if (!plant) {
    return <p className="text-sm text-muted" data-contract-result="none"><span className="cursor-help border-b border-dotted border-muted italic" title={why} data-missing="1">not held yet</span></p>;
  }
  if (!ready) {
    return <p className="text-sm text-muted" data-contract-result="empty">Enter a share and a price under &quot;Your contract&quot; to see the plant with a contract. The terms stay on this device.</p>;
  }
  const r = contractResult(contractSpan(plant.energy, plant.price), mw, { share, price });
  const rows: [string, ReactNode, string][] = [
    ["Contracted energy, a year", usd(r.contracted), `${share} percent of ${Math.round(r.mwh).toLocaleString("en-US")} MWh at USD ${price} per MWh`],
    ["Market revenue on the rest", usd(r.market), `${100 - share} percent at ${hub}'s generation-weighted price, USD ${two(plant.price)} per MWh${span ? `, ${span}` : ""}`],
    ["Revenue with the contract", <>{usd(r.total)}<div className="text-xs font-normal text-muted">{per(r.per)}</div></>, "the contracted share at its price, the rest at the market's"],
    ["Revenue without it", <>{usd(r.without)}<div className="text-xs font-normal text-muted">{per(r.perWithout)}</div></>, "the same twelve months, market only"],
    ["The contract's difference", `USD ${signed(Math.round(r.total - r.without), 0)}`, "with the contract less without it"],
  ];
  return (
    <div data-contract-result="shown" data-contract-with={Math.round(r.total)} data-contract-without={Math.round(r.without)}>
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
