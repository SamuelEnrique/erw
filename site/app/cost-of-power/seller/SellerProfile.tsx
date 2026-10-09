"use client";
// Session 162: (c) "Your plant's profile" on /cost-of-power/seller. The reader pastes or uploads one year of hourly
// output; revenue, the capture price and the pair with a battery are computed in this browser (lib/sellerhybrid.ts,
// the same functions the page's own figures use). The profile is this component's state and nothing else: it is in no
// request, no address, no cookie and no storage, and a file chosen is read here by the browser's own FileReader. The
// only thing the box ever asks the server for is the static file of the hub's hourly day-ahead prices for the year
// chosen (public/seller/prices/<grid>_<year>.json), a plain GET that carries nothing of the reader's.
// scripts/check-seller-deeper.mjs proves it in a real browser. docs/methods/cost_of_power.md, "Session 162".
import { useEffect, useMemo, useRef, useState } from "react";
import { hoursOfYear, parseProfile, profileResult, type PriceYear, type YearFile } from "@/lib/sellerhybrid";

const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const whole = (v: number) => Math.round(v).toLocaleString("en-US");
const usd = (v: number) => {
  const r = Math.round(v);
  return `USD ${Math.abs(r) >= 1e9 ? `${two(r / 1e9)} billion` : Math.abs(r) >= 1e6 ? `${two(r / 1e6)} million` : r.toLocaleString("en-US")}`;
};
const field = "w-full border border-rule bg-white px-2 py-1 text-sm";
const hint = "cursor-help border-b border-dotted border-muted";

export function SellerProfile({ grid, gridName, hub, zone, years, battery, hybridWhy }: {
  grid: string; gridName: string; hub: string; zone: string; years: YearFile[];
  /** the battery of the form: MW and hours */
  battery: { mw: number; hours: number };
  /** why this grid shows no pair, or null when it does */
  hybridWhy: string | null;
}) {
  const [year, setYear] = useState<number | null>(years.length ? years[years.length - 1].year : null);
  // what was last read, with the grid and year it is for: another year's file is never set against this year's profile
  const [read, setRead] = useState<{ key: string; prices: PriceYear | null; failed: string | null } | null>(null);
  const [text, setText] = useState("");
  const file = useRef<HTMLInputElement>(null);

  // the hub's hourly prices of the year chosen: a static file, asked for when the year is chosen, never with the profile
  useEffect(() => {
    if (year === null) return;
    let live = true;
    const key = `${grid}|${year}`;
    fetch(`/seller/prices/${grid}_${year}.json`, { credentials: "omit", cache: "force-cache" })
      .then((r) => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then((j: PriceYear) => { if (live) setRead({ key, prices: j, failed: null }); })
      .catch((e: Error) => { if (live) setRead({ key, prices: null, failed: e.message }); });
    return () => { live = false; };
  }, [grid, year]);

  const current = read && read.key === `${grid}|${year}` ? read : null;
  const prices = current?.prices ?? null, failed = current?.failed ?? null;
  const parsed = useMemo(() => (text.trim() === "" || year === null ? null : parseProfile(text, year)), [text, year]);
  const result = useMemo(
    () => (parsed && parsed.ok && prices && prices.year === year ? profileResult(parsed.values, prices.price, hybridWhy ? 0 : battery.mw, battery.hours) : null),
    [parsed, prices, year, battery.mw, battery.hours, hybridWhy],
  );
  const upload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    const reader = new FileReader();  // read on this device; nothing is uploaded
    reader.onload = () => setText(typeof reader.result === "string" ? reader.result : "");
    reader.readAsText(f);
  };
  const clear = () => { setText(""); if (file.current) file.current.value = ""; };

  if (!years.length || year === null) {
    return <p className="text-sm" data-profile="none"><span className={`${hint} italic text-muted`} title={`No calendar year of day-ahead prices is held whole at ${hub} of ${gridName}: a year is offered when at least 95 percent of its hours hold a price.`} data-missing="1">not held yet</span></p>;
  }
  const need = hoursOfYear(year);
  const accepted = `Accepted: ${need.toLocaleString("en-US")} values for ${year} (8,760 hours, or 8,784 in a leap year), one for each hour, in order. One number a line, or a CSV (comma, semicolon or tab) with exactly one column of numbers; a first line without a number is read as a header. Each value is the plant's output in that hour, in MW (the hour's average) or MWh in the hour, which are the same number. Hour 1 runs from 00:00 to 01:00 on 1 January ${year} in ${zone}, with no daylight saving shift. A profile of another length, with a value below zero, an empty line or a value that is not a number is refused: nothing is filled, cut or repaired.`;
  const h = result?.hybrid ?? null;
  const left = result && result.daysOut ? ` (${result.daysOut} left out, never filled)` : "";
  const share = h && h.charged > 0 ? `${((100 * h.fromPlant) / h.charged).toFixed(0)} percent of its charging came from the plant's own output` : "it did not charge";
  const plantWhy = h ? `The plant's revenue over the ${h.days} days of ${year} whose 24 hours all hold a price${left}: the days the pair is solved on.` : "";
  const batteryWhy = `A ${battery.mw.toLocaleString("en-US")} MW, ${battery.hours}-hour battery on an interconnection of its own, energy only, on the same days and prices and under the same rules: round trip 86 percent, each day from empty, at most one full cycle a day, no discharge in an hour priced below zero.`;
  const pairWhy = h ? `The plant and the battery behind one interconnection of ${two(h.limit)} MW, the profile's highest hour. Each day the battery's schedule is the best one against that day's day-ahead prices, all known in advance: an upper bound for a schedule made the day before. It may charge from the plant's output or from the grid, and ${share}.` : "";
  const addedWhy = "The plant alone and the battery alone, added: two interconnections and no limit shared. The pair is the same two assets under one more limit, so it is never above this.";
  const rows: [string, string, string, string][] = result ? [
    ["Generation", `${whole(result.energy)} MWh`, "energy", `The sum of the ${result.hours.toLocaleString("en-US")} values. Highest hour: ${two(result.peak)} MW.${result.priced < result.hours ? ` ${whole(result.energyPriced)} MWh of it fall in hours that hold a price.` : ""}`],
    ["Revenue at the hub price", usd(result.revenue), "revenue", `Each hour's output times that hour's day-ahead price at ${hub}, summed over the ${result.priced.toLocaleString("en-US")} hours of ${year} that hold a price (of ${result.hours.toLocaleString("en-US")}). An hour without a price is in no figure.`],
    ["Capture price", result.capture === null ? "none" : `USD ${two(result.capture)} per MWh`, "capture", "Revenue over the generation of the same hours: the capture price times that generation is the revenue."],
    ["The hub's simple average", result.flat === null ? "none" : `USD ${two(result.flat)} per MWh`, "flat", `The plain mean of the same ${result.priced.toLocaleString("en-US")} hourly prices.`],
    ["Capture ratio", result.ratio === null ? "none" : `${result.ratio.toFixed(1)} percent`, "ratio", "The capture price over the hub's simple average."],
  ] : [];
  return (
    <div data-profile="box">
      <div className="grid gap-3 sm:grid-cols-[minmax(0,1fr)_200px]">
        {/* no form and no field names: nothing here can be submitted */}
        <label className="block text-sm"><span className="mb-1 block font-semibold"><span className={hint} title={accepted}>{need.toLocaleString("en-US")} hourly values, MW</span>, one a line</span>
          <textarea rows={5} value={text} onChange={(e) => setText(e.target.value)} spellCheck={false} autoComplete="off" className={`${field} font-mono text-xs`} data-profile="text"
            placeholder={`${need.toLocaleString("en-US")} lines, one number each`} />
        </label>
        <div className="space-y-2 text-sm">
          <label className="block"><span className="mb-1 block font-semibold">Year</span>
            <select value={year} onChange={(e) => setYear(Number(e.target.value))} className={field} data-profile="year">
              {years.map((y) => <option key={y.year} value={y.year}>{y.year}</option>)}
            </select>
          </label>
          <label className="block"><span className="mb-1 block font-semibold">Or a file</span>
            <input ref={file} type="file" accept=".csv,.txt,text/csv,text/plain" onChange={upload} className="w-full text-xs" data-profile="file" />
          </label>
          {text ? <button type="button" onClick={clear} className="border border-rule bg-white px-2 py-0.5 text-xs" data-profile="clear">Clear</button> : null}
        </div>
      </div>
      <p className="mt-1 text-xs leading-snug text-muted" data-profile="promise">Computed on this device. Nothing you paste or upload is sent or stored.</p>
      <p className="mt-1 text-xs leading-snug text-muted">
        Priced at {hub}, {gridName}, day-ahead, hour by hour. <span className={hint} title={accepted}>Hour 1 is 00:00 on 1 January {year}, {zone}</span>.
        {prices ? <> <span className={hint} data-profile="prices" data-profile-held={prices.held} title={`The static file /seller/prices/${grid}_${year}.json: ${prices.held.toLocaleString("en-US")} of ${prices.hours.toLocaleString("en-US")} hours of ${year} hold a price. From ${prices.tables.join(", ")}; built ${prices.built.slice(0, 10)}.`}>{prices.held.toLocaleString("en-US")} of {prices.hours.toLocaleString("en-US")} hours priced</span>.</> : failed ? <> <span className="italic" data-profile="prices-failed" title={failed}>The prices of {year} could not be read.</span></> : <> Reading the prices of {year}.</>}
      </p>
      {parsed && !parsed.ok ? <p className="mt-3 border border-rule bg-paper px-3 py-2 text-sm" role="alert" data-profile="refused">Not read. {parsed.why}</p> : null}
      {result ? (
        <div className="mt-3" data-profile="result" data-profile-revenue={result.revenue.toFixed(2)} data-profile-energy={result.energyPriced.toFixed(4)} data-profile-capture={result.capture === null ? "" : result.capture.toFixed(6)}
          data-profile-flat={result.flat === null ? "" : result.flat.toFixed(6)} data-profile-pair={h ? h.pair.toFixed(2) : ""} data-profile-plant={h ? h.plant.toFixed(2) : ""}>
          <table className="w-full border-collapse text-left text-sm tabular-nums">
            <thead><tr className="bg-accent text-white"><th scope="col" className="px-3 py-1.5 font-normal">Your profile, {year}</th><th scope="col" className="px-3 py-1.5 text-right font-normal">Result</th></tr></thead>
            <tbody>
              {rows.map(([k, v, id, why]) => (
                <tr key={id} className={`border-b border-rule ${id === "capture" ? "bg-paper font-semibold" : ""}`}>
                  <th scope="row" className="px-3 py-1.5 font-normal"><span className={hint} title={why}>{k}</span></th>
                  <td className="whitespace-nowrap px-3 py-1.5 text-right" data-profile-cell={id}>{v}</td>
                </tr>
              ))}
              {hybridWhy ? (
                <tr className="border-b border-rule"><th scope="row" className="px-3 py-1.5 font-normal">With a battery beside it</th>
                  <td className="px-3 py-1.5 text-right"><span className={`${hint} italic text-muted`} title={hybridWhy} data-missing="1">not modeled for this grid</span></td></tr>
              ) : h ? (
                <>
                  <tr className="border-b border-rule"><th scope="row" className="px-3 py-1.5 font-normal"><span className={hint} title={plantWhy}>Plant alone, the days solved</span></th>
                    <td className="whitespace-nowrap px-3 py-1.5 text-right" data-profile-cell="plant">{usd(h.plant)}</td></tr>
                  <tr className="border-b border-rule"><th scope="row" className="px-3 py-1.5 font-normal"><span className={hint} title={batteryWhy}>Battery alone, {battery.mw.toLocaleString("en-US")} MW, {battery.hours}-hour</span></th>
                    <td className="whitespace-nowrap px-3 py-1.5 text-right" data-profile-cell="battery">{usd(h.battery)}</td></tr>
                  <tr className="border-b border-rule bg-paper font-semibold"><th scope="row" className="px-3 py-1.5 font-normal"><span className={hint} title={pairWhy}>Co-optimized pair, one interconnection</span></th>
                    <td className="whitespace-nowrap px-3 py-1.5 text-right" data-profile-cell="pair">{usd(h.pair)}</td></tr>
                  <tr className="border-b border-rule"><th scope="row" className="px-3 py-1.5 font-normal"><span className={hint} title={addedWhy}>Added, not co-optimized: upper bound</span></th>
                    <td className="whitespace-nowrap px-3 py-1.5 text-right" data-profile-cell="added">{usd(h.added)}</td></tr>
                </>
              ) : null}
            </tbody>
          </table>
        </div>
      ) : parsed && parsed.ok && !prices ? <p className="mt-3 text-sm text-muted" data-profile="waiting">{failed ? "No result: the prices could not be read." : "Reading the prices."}</p> : null}
    </div>
  );
}
