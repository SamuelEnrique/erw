"use client";
// Session 145: the "Your plant" panel of /cost-of-power/seller, the mirror of the battery page's "Your battery". These
// inputs live in the URL. The form is a plain GET form (it works without JavaScript); with JavaScript the same address
// is opened in place, so the contract terms typed in the other panel, which live only in this page's memory, are not
// lost on Show. Choosing another grid or asset opens it at once: the hubs are that grid's and the cost defaults that
// asset's.
import { useRouter } from "next/navigation";
import { SiteLink as Link } from "@/components/SiteLink";

export type FormGrid = { id: string; name: string; open: boolean; words?: string; why?: string; hubs: { id: string; label: string }[] };
export type FormValues = { iso: string; hub: string; asset: string; mw: number; mwh: number; ds: number; fom: number; hr: number; vom: number; bmw: number; dur: number; strat: string };

const field = "w-full border border-rule bg-white px-2 py-1 text-sm";
const KEYS = ["iso", "hub", "asset", "mw", "mwh", "ds", "fom", "hr", "vom", "bmw", "dur", "strat"] as const;
const ASSETS: [string, string][] = [["solar", "Solar"], ["wind", "Wind"], ["battery", "Battery"], ["peaker", "Gas peaker"]];
const STRATEGIES: [string, string][] = [["foresight", "Perfect foresight"], ["dayahead", "Day-ahead schedule"]];

export function SellerForm({ x, grids, hybrid, defaults }: { x: FormValues; grids: FormGrid[]; hybrid: boolean; defaults: string }) {
  const router = useRouter();
  const g = grids.find((k) => k.id === x.iso);
  const open = (iso: string, asset: string, hub?: string) => `/cost-of-power/seller?iso=${iso}&asset=${asset}${hub ? `&hub=${encodeURIComponent(hub)}` : ""}`;
  return (
    <form
      method="get" action="/cost-of-power/seller" className="space-y-4 text-sm" data-seller-form="1"
      onSubmit={(e) => {
        e.preventDefault();
        const f = new FormData(e.currentTarget);
        const q = new URLSearchParams();
        for (const k of KEYS) { const v = f.get(k); if (typeof v === "string" && v !== "") q.set(k, v); }
        router.push(`/cost-of-power/seller?${q.toString()}`, { scroll: false });
      }}
    >
      <fieldset>
        <legend className="mb-1 font-semibold">Grid</legend>
        <ul className="space-y-1">
          {grids.map((k) => (
            <li key={k.id}>
              <label className={`flex items-baseline gap-2 ${k.open ? "" : "text-muted"}`} data-grid={k.id} data-open={k.open ? "1" : "0"}>
                <input type="radio" name="iso" value={k.id} defaultChecked={x.iso === k.id} disabled={!k.open} className="accent-[var(--color-accent)]"
                  onChange={() => router.push(open(k.id, x.asset), { scroll: false })} />
                <span>{k.name}</span>
                {k.open ? <span className="text-xs text-muted">{k.hubs.length} hubs and zones</span> : <span className="cursor-help text-xs italic" title={k.why}>{k.words}</span>}
              </label>
            </li>
          ))}
        </ul>
      </fieldset>

      <label className="block"><span className="mb-1 block font-semibold">Hub or zone</span>
        <select name="hub" defaultValue={x.hub} className={field} data-hub="1">
          {g?.hubs.map((h) => <option key={h.id} value={h.id}>{h.label}</option>)}
        </select>
      </label>

      <fieldset>
        <legend className="mb-1 font-semibold">Asset</legend>
        {ASSETS.map(([id, name]) => (
          <label key={id} className="flex items-baseline gap-2" data-asset={id}>
            <input type="radio" name="asset" value={id} defaultChecked={x.asset === id} className="accent-[var(--color-accent)]"
              onChange={() => router.push(open(x.iso, id, x.hub), { scroll: false })} />
            <span>{name}</span>
          </label>
        ))}
      </fieldset>

      <label className="block"><span className="mb-1 block font-semibold">Size, MW</span>
        <input name="mw" type="number" min={1} max={5000} step="any" defaultValue={x.mw} className={field} />
      </label>
      {x.asset === "battery" ? (
        <label className="block"><span className="mb-1 block font-semibold">Energy, MWh</span>
          <input name="mwh" type="number" min={x.mw} max={x.mw * 8} step="any" defaultValue={x.mwh} className={field} />
        </label>
      ) : null}
      <label className="block"><span className="mb-1 block font-semibold">Annual debt payments, USD</span>
        <input name="ds" type="number" min={0} step="any" defaultValue={x.ds} className={field} />
      </label>
      <label className="block"><span className="mb-1 block font-semibold">Fixed O&amp;M, USD per kW a year</span>
        <input name="fom" type="number" min={0} max={200} step="any" defaultValue={x.fom} className={field} />
      </label>
      {x.asset === "peaker" ? (
        <>
          <label className="block"><span className="mb-1 block font-semibold">Heat rate, MMBtu per MWh</span>
            <input name="hr" type="number" min={6} max={16} step="any" defaultValue={x.hr} className={field} />
          </label>
          <label className="block"><span className="mb-1 block font-semibold">Variable O&amp;M, USD per MWh</span>
            <input name="vom" type="number" min={0} max={50} step="any" defaultValue={x.vom} className={field} />
          </label>
        </>
      ) : null}
      {hybrid ? (
        <fieldset className="border-t border-rule pt-3" data-hybrid-inputs="1">
          <legend className="mb-1 font-semibold">A battery beside it</legend>
          <label className="mb-2 block"><span className="mb-1 block">Battery size, MW</span>
            <input name="bmw" type="number" min={1} max={5000} step="any" defaultValue={x.bmw} className={field} />
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
        <Link href={open(x.iso, x.asset, x.hub)} scroll={false} className="text-xs">Reset the costs</Link>
      </div>
      <p className="text-xs leading-snug text-muted">{defaults}</p>
    </form>
  );
}
