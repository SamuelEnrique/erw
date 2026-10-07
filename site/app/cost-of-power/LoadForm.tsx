"use client";
// Session 138: the "Your load" panel of /cost-of-power, the mirror of the battery page's "Your battery". These inputs
// live in the URL. The form is a plain GET form (it works without JavaScript); with JavaScript the same address is
// opened in place, so the contract terms typed in the other panel, which live only in this page's memory, are not lost
// on Show. Choosing another grid opens that grid at once, so the list of regions is that grid's.
import { useRouter } from "next/navigation";
import { SiteLink as Link } from "@/components/SiteLink";
import { ASSUMED, BUYS, DEFAULTS, LIMITS, ORDER, RUNS, hrefOf, type Buy, type Index, type Inputs, type Run } from "@/lib/datacenter";

const field = "w-full border border-rule bg-white px-2 py-1 text-sm";
const small = "w-20 border border-rule bg-white px-1.5 py-0.5 text-sm";
const KEYS = ["grid", "region", "mw", "run", "n", "pct", "shift", "buy", "gpu", "pue"] as const;

export function LoadForm({ x, grids, blank }: { x: Inputs; grids: Record<string, { name: string; regions: { id: string; held: string }[] }>; blank: Index["blank"] }) {
  const router = useRouter();
  const g = grids[x.grid];
  return (
    <form
      method="get" action="/cost-of-power" className="space-y-4 text-sm" data-load-form="1"
      onSubmit={(e) => {
        e.preventDefault();
        const f = new FormData(e.currentTarget);
        const q = new URLSearchParams();
        for (const k of KEYS) { const v = f.get(k); if (typeof v === "string" && v !== "") q.set(k, v); }
        router.push(`/cost-of-power?${q.toString()}`, { scroll: false });
      }}
    >
      <fieldset>
        <legend className="mb-1 font-semibold">Grid</legend>
        <ul className="space-y-1">
          {ORDER.map((id) => {
            const open = !!grids[id];
            return (
              <li key={id}>
                <label className={`flex items-baseline gap-2 ${open ? "" : "text-muted"}`} data-grid={id} data-open={open ? "1" : "0"}>
                  <input type="radio" name="grid" value={id} defaultChecked={x.grid === id} disabled={!open} className="accent-[var(--color-accent)]"
                    onChange={() => router.push(hrefOf(x, { grid: id, region: "" }), { scroll: false })} />
                  <span>{open ? grids[id].name : blank[id]?.name ?? id.toUpperCase()}</span>
                  {open ? <span className="text-xs text-muted">{grids[id].regions.length} regions</span> : <span className="text-xs italic">{blank[id]?.words ?? "not held yet"}</span>}
                </label>
              </li>
            );
          })}
        </ul>
      </fieldset>

      <label className="block"><span className="mb-1 block font-semibold">Region</span>
        <select name="region" defaultValue={x.region} className={field} data-region="1">
          {g?.regions.map((r) => <option key={r.id} value={r.id}>{r.id} ({r.held})</option>)}
        </select>
      </label>

      <label className="block"><span className="mb-1 block font-semibold">Size, MW</span>
        <input name="mw" type="number" min={LIMITS.mw[0]} max={LIMITS.mw[1]} step="any" defaultValue={x.mw} className={field} />
      </label>

      <fieldset>
        <legend className="mb-1 font-semibold">How it runs</legend>
        <div className="space-y-1.5">
          {(Object.keys(RUNS) as Run[]).map((r) => (
            <label key={r} className="flex items-baseline gap-2" data-run={r}>
              <input type="radio" name="run" value={r} defaultChecked={x.run === r} className="accent-[var(--color-accent)]" />
              <span>{RUNS[r]}
                {r === "hours" ? <span className="mt-0.5 block text-xs text-muted">hours a year <input name="n" type="number" min={0} max={8784} step={1} defaultValue={x.n} className={small} aria-label="Hours a year turned off" /></span> : null}
                {r === "share" ? <span className="mt-0.5 block text-xs text-muted">percent of hours <input name="pct" type="number" min={0} max={100} step="any" defaultValue={x.pct} className={small} aria-label="Percent of hours turned off" /></span> : null}
                {r === "shift" ? <span className="mt-0.5 block text-xs text-muted">percent of a day&apos;s energy <input name="shift" type="number" min={0} max={50} step="any" defaultValue={x.shift} className={small} aria-label="Percent of the energy of each day moved" /></span> : null}
              </span>
            </label>
          ))}
        </div>
      </fieldset>

      <fieldset>
        <legend className="mb-1 font-semibold">How it buys</legend>
        {(Object.keys(BUYS) as Buy[]).map((b) => (
          <label key={b} className="flex items-baseline gap-2" data-buy={b}>
            <input type="radio" name="buy" value={b} defaultChecked={x.buy === b} className="accent-[var(--color-accent)]" />
            <span>{BUYS[b]}</span>
          </label>
        ))}
        <p className="mt-1 text-xs text-muted">A contract for a share of the energy is the panel below.</p>
      </fieldset>

      <label className="block"><span className="mb-1 block font-semibold"><span className="cursor-help border-b border-dotted border-muted" title={ASSUMED.gpu.source}>Power per GPU, kW</span></span>
        <input name="gpu" type="number" min={LIMITS.gpu[0]} max={LIMITS.gpu[1]} step="any" defaultValue={x.gpu} className={field} />
      </label>
      <label className="block"><span className="mb-1 block font-semibold"><span className="cursor-help border-b border-dotted border-muted" title={ASSUMED.pue.source}>Facility overhead ratio (PUE)</span></span>
        <input name="pue" type="number" min={LIMITS.pue[0]} max={LIMITS.pue[1]} step="any" defaultValue={x.pue} className={field} />
      </label>
      <div className="flex items-baseline gap-3">
        <button type="submit" className="border border-accent bg-accent px-4 py-1.5 text-white">Show</button>
        <Link href={hrefOf(x, { mw: DEFAULTS.mw, run: "flat", buy: "rt", gpu: DEFAULTS.gpu, pue: DEFAULTS.pue })} scroll={false} className="text-xs">Reset</Link>
      </div>
    </form>
  );
}
