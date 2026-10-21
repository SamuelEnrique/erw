"use client";
// Session 145: the "Your plant" panel of /cost-of-power/seller, the mirror of the battery page's "Your battery". These
// inputs live in the URL. The form is a plain GET form (it works without JavaScript); with JavaScript the same address
// is opened in place, so the contract terms typed in the other panel, which live only in this page's memory, are not
// lost on Show. Choosing another grid or asset opens it at once: the hubs are that grid's and the cost defaults that
// asset's.
// Session 186: the two scenarios live in the address too (SellerScenarios.tsx); Show, the grid, the asset and "Reset
// the costs" carry them. A change of asset (or of a battery's duration) drops a typed capital cost, fixed O&M, term
// and life, whose defaults are the asset's.
// Session 195: the panel no longer holds annual debt payments and a fixed O&M. Scenario A does (SellerScenarios.tsx),
// and sets the headline; the line under Show says where. An older link's `ds` and `fom` are read as scenario A's.
import { useRouter, useSearchParams } from "next/navigation";
import { SiteLink as Link } from "@/components/SiteLink";
import { keyOf, type Asset } from "@/lib/merchant";
import { carry } from "@/lib/seller/finance";

export type FormGrid = { id: string; name: string; open: boolean; words?: string; why?: string; hubs: { id: string; label: string; zone?: boolean }[] };
export type FormValues = { iso: string; hub: string; asset: string; mw: number; mwh: number; hr: number; vom: number; bmw: number; dur: number; strat: string };

const field = "w-full border border-rule bg-white px-2 py-1 text-sm";
const KEYS = ["iso", "hub", "asset", "mw", "mwh", "hr", "vom", "bmw", "dur", "strat"] as const;
const ASSETS: [string, string][] = [["solar", "Solar"], ["wind", "Wind"], ["battery", "Battery"], ["peaker", "Gas peaker"]];
const STRATEGIES: [string, string][] = [["foresight", "Perfect foresight"], ["dayahead", "Day-ahead schedule"]];

export function SellerForm({ x, grids, hybrid, defaults }: { x: FormValues; grids: FormGrid[]; hybrid: boolean; defaults: string }) {
  const router = useRouter();
  const search = useSearchParams().toString();
  const g = grids.find((k) => k.id === x.iso);
  const own = keyOf({ asset: x.asset as Asset, mw: x.mw, mwh: x.mwh });
  const open = (iso: string, asset: string, hub?: string) => `/cost-of-power/seller?iso=${iso}&asset=${asset}${hub ? `&hub=${encodeURIComponent(hub)}` : ""}`;
  return (
    <form
      method="get" action="/cost-of-power/seller" className="space-y-4 text-sm" data-seller-form="1"
      onSubmit={(e) => {
        e.preventDefault();
        const f = new FormData(e.currentTarget);
        const q = new URLSearchParams();
        for (const k of KEYS) { const v = f.get(k); if (typeof v === "string" && v !== "") q.set(k, v); }
        { const py = new URLSearchParams(window.location.search).get("py"); if (py) q.set("py", py); }   // session 352: Show keeps the price years chosen
        for (const k of ["nb", "ps"]) { const v = new URLSearchParams(window.location.search).get(k); if (v) q.set(k, v); }   // session 353: and the node and the contract's shape
        const mw = Number(q.get("mw") ?? x.mw), mwh = Number(q.get("mwh") ?? x.mwh);
        const same = keyOf({ asset: x.asset as Asset, mw: mw > 0 ? mw : x.mw, mwh: mwh > 0 ? mwh : x.mwh }) === own;
        router.push(`/cost-of-power/seller?${q.toString()}${carry(window.location.search, same)}`, { scroll: false });
      }}
    >
      <fieldset>
        <legend className="mb-1 font-semibold">Grid</legend>
        <ul className="space-y-1">
          {grids.map((k) => (
            <li key={k.id}>
              <label className={`flex items-baseline gap-2 ${k.open ? "" : "text-muted"}`} data-grid={k.id} data-open={k.open ? "1" : "0"}>
                <input type="radio" name="iso" value={k.id} defaultChecked={x.iso === k.id} disabled={!k.open} className="accent-[var(--color-accent)]"
                  onChange={() => router.push(`${open(k.id, x.asset)}${carry(window.location.search, true)}`, { scroll: false })} />
                <span>{k.name}</span>
                {k.open ? <span className="text-xs text-muted">{k.hubs.length} hubs and zones</span> : <span className="cursor-help text-xs italic" title={k.why}>{k.words}</span>}
              </label>
            </li>
          ))}
        </ul>
      </fieldset>

      {/* session 353: the settlement point, its hubs and its load zones apart; a node is chosen under the form (ParamChoice) */}
      <label className="block"><span className="mb-1 block font-semibold">Settlement point</span>
        <select name="hub" defaultValue={x.hub} className={field} data-hub="1">
          {g && g.hubs.some((h) => !h.zone) ? <optgroup label="Hubs">{g.hubs.filter((h) => !h.zone).map((h) => <option key={h.id} value={h.id}>{h.label}</option>)}</optgroup> : null}
          {g && g.hubs.some((h) => h.zone) ? <optgroup label="Load zones">{g.hubs.filter((h) => h.zone).map((h) => <option key={h.id} value={h.id}>{h.label}</option>)}</optgroup> : null}
        </select>
      </label>

      <fieldset>
        <legend className="mb-1 font-semibold">Asset</legend>
        {ASSETS.map(([id, name]) => (
          <label key={id} className="flex items-baseline gap-2" data-asset={id}>
            <input type="radio" name="asset" value={id} defaultChecked={x.asset === id} className="accent-[var(--color-accent)]"
              onChange={() => router.push(`${open(x.iso, id, x.hub)}${carry(window.location.search, id === x.asset)}`, { scroll: false })} />
            <span>{name}</span>
          </label>
        ))}
      </fieldset>

      <label className="block"><span className="mb-1 block font-semibold">Size, MW</span>
        <input name="mw" type="number" autoComplete="off" min={1} max={5000} step="any" defaultValue={x.mw} className={field} />
      </label>
      {x.asset === "battery" ? (
        <label className="block"><span className="mb-1 block font-semibold">Energy, MWh</span>
          <input name="mwh" type="number" autoComplete="off" min={x.mw} max={x.mw * 8} step="any" defaultValue={x.mwh} className={field} />
        </label>
      ) : null}
      {x.asset === "peaker" ? (
        <>
          <label className="block"><span className="mb-1 block font-semibold">Heat rate, MMBtu per MWh</span>
            <input name="hr" type="number" autoComplete="off" min={6} max={16} step="any" defaultValue={x.hr} className={field} />
          </label>
          <label className="block"><span className="mb-1 block font-semibold">Variable O&amp;M, USD per MWh</span>
            <input name="vom" type="number" autoComplete="off" min={0} max={50} step="any" defaultValue={x.vom} className={field} />
          </label>
        </>
      ) : null}
      {hybrid ? (
        <fieldset className="border-t border-rule pt-3" data-hybrid-inputs="1">
          <legend className="mb-1 font-semibold">A battery beside it</legend>
          <label className="mb-2 block"><span className="mb-1 block">Battery size, MW</span>
            <input name="bmw" type="number" autoComplete="off" min={1} max={5000} step="any" defaultValue={x.bmw} className={field} />
          </label>
          <label className="mb-2 block"><span className="mb-1 block">Duration</span>
            <select name="dur" defaultValue={String(x.dur)} className={field} data-duration="1">
              {[2, 4, 8].map((d) => <option key={d} value={d}>{d} hours</option>)}
            </select>
          </label>
          {STRATEGIES.map(([id, name]) => (
            <label key={id} className="flex items-baseline gap-2">
              <input type="radio" name="strat" value={id} defaultChecked={x.strat === id} className="accent-[var(--color-accent)]" />
              <span>{name}</span>
            </label>
          ))}
        </fieldset>
      ) : null}
      <div className="flex items-baseline gap-3">
        <button type="submit" className="border border-accent bg-accent px-4 py-1.5 text-white">Show</button>
        <Link href={`${open(x.iso, x.asset, x.hub)}${carry(search, x.asset !== "battery" || own === "battery_4h")}`} scroll={false} className="text-xs" data-reset-costs="1">Reset the costs</Link>
      </div>
      <p className="text-xs leading-snug text-muted" data-costs-in-a="1">{defaults} The costs and the debt are set under <a href="#scenarios">Scenarios A and B</a>: scenario A gives the headline.</p>
    </form>
  );
}
