"use client";
// Session 67: the "Your battery" panel of /cost-of-power/battery. These inputs live in the URL, as on the seller tab.
// The form is a plain GET form (it works without JavaScript); with JavaScript the same address is opened in place, so
// the contract terms typed in the other panel, which live only in this page's memory, are not lost on Show.
// Session 195: the panel no longer holds a fixed O&M and annual debt payments. Scenario A does (Scenarios.tsx), and
// sets the headline; the line under Show says where. An older link's `fom` and `ds` are read as scenario A's.
import { useRouter, useSearchParams } from "next/navigation";
import { SiteLink as Link } from "@/components/SiteLink";
import { Tip } from "@/components/tool/ToolPage";
import { COSTS, DURATIONS, GRIDS, STRATEGIES, debtPerMw, hrefOf, type Inputs, type Strategy } from "@/lib/batterystack";
import { carry } from "@/lib/battery/finance";

const field = "w-full border border-rule bg-white px-2 py-1 text-sm";
/** Session 296 (item 10): one line on each strategy, as the hover says it. */
export const STRATEGY_WORDS: Record<Strategy, string> = {
  foresight: "Perfect foresight: energy at the hourly real-time price and ancillary services at day-ahead prices, all known in advance; an upper bound, not a forecast.",
  dayahead: "Day-ahead schedule: the battery is scheduled against day-ahead energy and ancillary prices and paid those prices, with no real-time trading; its offers are assumed to clear.",
};

export function BatteryForm({ x, internal = false }: { x: Inputs; internal?: boolean }) {
  const router = useRouter();
  // session 179: the two scenarios live in the address too (Scenarios.tsx); this panel's links and its Show carry them
  const search = useSearchParams().toString();
  // the links name the grid, the duration, the strategy and the size; the costs travel as scenario A's parameters
  const bare: Inputs = { ...x, fom: COSTS[x.dur].fom, ds: Math.round(debtPerMw(x.dur) * x.mw) };
  return (
    <form
      method="get" action="/cost-of-power/battery" className="space-y-4 text-sm"
      onSubmit={(e) => {
        e.preventDefault();
        const f = new FormData(e.currentTarget);
        const q = new URLSearchParams();
        for (const k of ["grid", "dur", "strat", "mw"]) { const v = f.get(k); if (typeof v === "string" && v !== "") q.set(k, v); }
        { const py = new URLSearchParams(window.location.search).get("py"); if (py) q.set("py", py); }   // session 352: Show keeps the price years chosen
        router.push(`/cost-of-power/battery?${q.toString()}${carry(window.location.search, true)}`, { scroll: false });
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
        {/* session 208: the "Other grids" table is this one line */}
        <p className="mt-2 text-xs leading-snug text-muted" data-other-grids="1">
          The other five grids, in words only: PJM&apos;s prices are licensed and not held; NYISO and SPP are built and in review; ISO-NE&apos;s and MISO&apos;s reserve prices are held, not shown
          (license needed). Their energy prices are on <Link href="/cost-of-power/seller?asset=battery">the seller tab</Link>. No number from a licensed table is shown on this site.
        </p>
      </fieldset>

      {/* session 296 (item 10): one-line hovers on the duration and on each strategy; "perfect foresight" keeps its name */}
      <div>
        <div className="mb-1 font-semibold" id="dur-label">Duration<Tip id="duration" label="the duration">How long the battery can discharge at its rated power: a 4-hour battery holds 4 MWh for each MW. The model is run at 2, 4 and 8 hours; a longer battery can back a reserve that must be held longer and sell more energy in a day.</Tip></div>
        <div className="grid grid-cols-3 border border-accent" role="group" aria-labelledby="dur-label">
          {DURATIONS.map((d) => (
            <Link key={d} href={`${hrefOf(bare, { dur: d })}${carry(search, d === x.dur)}`} scroll={false} aria-current={x.dur === d ? "true" : undefined} data-duration={d}
              title={`${d} hours: the battery discharges at its rated power for ${d} hours, ${d} MWh for each MW`}
              style={x.dur === d ? { color: "#fff" } : undefined}
              className={`px-2 py-1.5 text-center no-underline ${d !== DURATIONS[0] ? "border-l border-accent" : ""} ${x.dur === d ? "bg-accent font-semibold" : "bg-white text-accent hover:bg-paper"}`}>
              {d} hours
            </Link>
          ))}
        </div>
        <input type="hidden" name="dur" value={x.dur} />
      </div>

      <fieldset>
        <legend className="mb-1 font-semibold">Strategy<Tip id="strategy" label="the strategy">{STRATEGY_WORDS.foresight} {STRATEGY_WORDS.dayahead}</Tip></legend>
        {(Object.keys(STRATEGIES) as Strategy[]).map((s) => (
          <label key={s} className="flex items-baseline gap-2" title={STRATEGY_WORDS[s]}>
            <input type="radio" name="strat" value={s} defaultChecked={x.strat === s} className="accent-[var(--color-accent)]" />
            <span>{STRATEGIES[s]}</span>
          </label>
        ))}
      </fieldset>

      <label className="block"><span className="mb-1 block font-semibold">Size, MW</span>
        <input name="mw" type="number" min={1} max={5000} step="any" autoComplete="off" defaultValue={x.mw} className={field} />
      </label>
      <div className="flex items-baseline gap-3">
        <button type="submit" className="border border-accent bg-accent px-4 py-1.5 text-white">Show</button>
      </div>
      {/* session 296: the line on the defaults and on scenario A is the box's own (Settings.tsx, data-costs-in-a) */}
    </form>
  );
}
