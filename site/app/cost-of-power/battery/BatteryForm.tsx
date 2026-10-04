"use client";
// Session 67: the "Your battery" panel of /cost-of-power/battery. These inputs live in the URL, as on the seller tab.
// The form is a plain GET form (it works without JavaScript); with JavaScript the same address is opened in place, so
// the contract terms typed in the other panel, which live only in this page's memory, are not lost on Show.
import { useRouter } from "next/navigation";
import { SiteLink as Link } from "@/components/SiteLink";
import { COSTS, DURATIONS, GRIDS, STRATEGIES, hrefOf, type Inputs, type Strategy } from "@/lib/batterystack";

const field = "w-full border border-rule bg-white px-2 py-1 text-sm";

export function BatteryForm({ x, internal = false }: { x: Inputs; internal?: boolean }) {
  const router = useRouter();
  return (
    <form
      method="get" action="/cost-of-power/battery" className="space-y-4 text-sm"
      onSubmit={(e) => {
        e.preventDefault();
        const f = new FormData(e.currentTarget);
        const q = new URLSearchParams();
        for (const k of ["grid", "dur", "strat", "mw", "fom", "ds"]) { const v = f.get(k); if (typeof v === "string" && v !== "") q.set(k, v); }
        router.push(`/cost-of-power/battery?${q.toString()}`, { scroll: false });
      }}
    >
      <fieldset>
        <legend className="mb-1 font-semibold">Grid</legend>
        <ul className="space-y-1">
          {GRIDS.map((g) => {
            // session 86: a grid in review is greyed for a visitor, as it was, and open in the internal view
            const open = g.ready || (internal && !!g.review);
            return (
              <li key={g.id}>
                <label className={`flex items-baseline gap-2 ${open ? "" : "text-muted"}`} data-grid={g.id} data-open={open ? "1" : "0"}>
                  <input type="radio" name="grid" value={g.id} defaultChecked={x.grid === g.id} disabled={!open} className="accent-[var(--color-accent)]" />
                  <span>{g.name}</span>
                  {open ? <span className="text-xs text-muted">{g.hub}, from {g.from}{g.review ? "; in review" : ""}</span> : <span className="text-xs">{g.why}</span>}
                </label>
              </li>
            );
          })}
        </ul>
      </fieldset>

      <div>
        <div className="mb-1 font-semibold" id="dur-label">Duration</div>
        <div className="grid grid-cols-3 border border-accent" role="group" aria-labelledby="dur-label">
          {DURATIONS.map((d) => (
            <Link key={d} href={hrefOf(x, { dur: d })} scroll={false} aria-current={x.dur === d ? "true" : undefined} data-duration={d}
              style={x.dur === d ? { color: "#fff" } : undefined}
              className={`px-2 py-1.5 text-center no-underline ${d !== DURATIONS[0] ? "border-l border-accent" : ""} ${x.dur === d ? "bg-accent font-semibold" : "bg-white text-accent"}`}>
              {d} hours
            </Link>
          ))}
        </div>
        <input type="hidden" name="dur" value={x.dur} />
      </div>

      <fieldset>
        <legend className="mb-1 font-semibold">Strategy</legend>
        {(Object.keys(STRATEGIES) as Strategy[]).map((s) => (
          <label key={s} className="flex items-baseline gap-2">
            <input type="radio" name="strat" value={s} defaultChecked={x.strat === s} className="accent-[var(--color-accent)]" />
            <span>{STRATEGIES[s]}</span>
          </label>
        ))}
      </fieldset>

      <label className="block"><span className="mb-1 block font-semibold">Size, MW</span>
        <input name="mw" type="number" min={1} max={5000} step="any" defaultValue={x.mw} className={field} />
      </label>
      <label className="block"><span className="mb-1 block font-semibold">Fixed O&amp;M, USD per kW a year</span>
        <input name="fom" type="number" min={0} max={500} step="any" defaultValue={x.fom} className={field} />
      </label>
      <label className="block"><span className="mb-1 block font-semibold">Annual debt payments, USD</span>
        <input name="ds" type="number" min={0} step="any" defaultValue={x.ds} className={field} />
      </label>
      <div className="flex items-baseline gap-3">
        <button type="submit" className="border border-accent bg-accent px-4 py-1.5 text-white">Show</button>
        <Link href={`/cost-of-power/battery?grid=${x.grid}&dur=${x.dur}&strat=${x.strat}`} scroll={false} className="text-xs">Reset the costs</Link>
      </div>
      <p className="text-xs leading-snug text-muted">
        Defaults for {x.dur} hours: capital {COSTS[x.dur].capex.toLocaleString("en-US")} USD/kW and fixed O&amp;M {COSTS[x.dur].fom} USD/kW a year ({COSTS[x.dur].note}).
      </p>
    </form>
  );
}
