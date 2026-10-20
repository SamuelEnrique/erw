"use client";
// Energy Research Warehouse (ERW) site, session 352: the "Price years" choice of the three economics pages' boxes. A
// select of the windows the data machine's table price_years_by_window holds for the page's price point and
// configuration (lib/priceyears.ts): the last twelve months (the default), each calendar year held, the averages of the
// last three and seven full years, every month held, and every month held with a stress event taken out. The default is
// written in grey beside it, with its source; Reset puts it back. A window the table does not hold is not offered.
import { DEFAULT_WINDOW, windowWords, type PriceYear } from "@/lib/priceyears";

export function PriceYearsChoice({ ws, read, value, onChange, unit }: { ws: PriceYear[]; read: boolean; value: string; onChange: (id: string) => void; unit: string }) {
  const offered = ws.some((w) => w.id === DEFAULT_WINDOW) ? ws : [];
  const fmt = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  return (
    <div className="mt-3 text-sm" data-price-years-choice={offered.length}>
      <label className="block">
        <span className="font-semibold">Price years</span>
        <select value={offered.some((w) => w.id === value) ? value : DEFAULT_WINDOW} onChange={(e) => onChange(e.target.value)} disabled={!offered.length}
          className="mt-1 block w-full max-w-full border border-rule bg-white px-2 py-1 text-sm text-ink" data-price-years-select="1">
          {offered.length ? offered.map((w) => <option key={w.id} value={w.id}>{windowWords(w).label}: {fmt(w.value)} {unit}</option>)
            : <option value={DEFAULT_WINDOW}>The last twelve months (default)</option>}
        </select>
      </label>
      <p className="mt-1 text-xs leading-snug text-muted" data-default="py">
        Default: the last twelve months, the page&apos;s own figure. Each window is the page&apos;s figure under those years
        (price_years_by_window, built from the same tables).{!read ? " The price years could not be read when the page was drawn: the last twelve months are shown." : !offered.length ? " None is held for this case." : ""}
      </p>
      {value !== DEFAULT_WINDOW ? <button type="button" data-reset="py" aria-label="Reset the price years" onClick={() => onChange(DEFAULT_WINDOW)} className="mt-1 border border-rule px-1.5 py-px text-xs">Reset</button> : null}
    </div>
  );
}
