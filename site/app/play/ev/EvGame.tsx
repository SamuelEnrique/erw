"use client";
// Session 294: "Should your family get an EV?", five screens for a middle-schooler of about 12 to work through and show
// their parents. Where you live (the state's power and gasoline prices, each with its table and date), your car, the
// money, the verdict, and every number on one page to print. The prices are the warehouse's (data/ev_prices.json); the
// defaults are fueleconomy.gov's and the maker's, each labelled; anything the family changes is marked as theirs.
// The arithmetic is lib/ev.ts. The brand's rules (docs/brand.md): tokens only, square, no motion, cardinal for a link, a
// control in its active state and the highlighted series (the EV's bar).
import { useState } from "react";
import { DEFAULTS, IRS_URL, NO_CREDIT_LINE, verdict, type Inputs } from "@/lib/ev";
import { PrintButton } from "@/app/learn/problems/PrintButton";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate

export type Cell = { value: number; unit: string; ts: string; entity: string; table: string; where?: string; region?: string } | null;
export type StatePrices = { code: string; name: string; power: Cell; gas: Cell };

const usd = (v: number, d = 2) => `${v < 0 ? "-" : ""}$${Math.abs(v).toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d })}`;
const n2 = (v: number, d = 2) => v.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
const month = (ts: string) => new Date(`${ts}T12:00:00Z`).toLocaleDateString("en-US", { month: "long", year: "numeric", timeZone: "UTC" });
const day = (ts: string) => new Date(`${ts}T12:00:00Z`).toLocaleDateString("en-US", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });
const SCREENS = ["Where do you live?", "Your car", "The money", "The verdict", "Show your parents"];
type Key = keyof typeof DEFAULTS;

/** A slider with its number, its default in grey with its source, and a reset named for it (docs/brand.md, section 7). */
function Slider({ k, value, set, fmt }: { k: Key; value: number; set: (v: number) => void; fmt: (v: number) => string }) {
  const d = DEFAULTS[k];
  const mine = value !== d.value;
  return (
    <div className="mb-5" data-field={k}>
      <label className="block text-sm" htmlFor={`ev-${k}`}>{d.label}: <strong className="font-mono">{fmt(value)}</strong>{mine ? <span className="ml-2 text-xs text-muted">changed by you</span> : null}</label>
      <input id={`ev-${k}`} type="range" min={d.min} max={d.max} step={d.step} value={value} onChange={(e) => set(Number(e.target.value))} className="mt-1 w-full max-w-xl" />
      <p className="max-w-3xl text-xs text-muted">Default {fmt(d.value)}. {d.source}.{mine ? <> <button type="button" onClick={() => set(d.value)} className="ml-1 border px-2 py-0.5">Reset {d.label.toLowerCase()}</button></> : null}</p>
    </div>
  );
}

export function EvGame({ states, us, built }: { states: StatePrices[]; us: StatePrices; built: string }) {
  const [step, setStep] = useState(0);
  const [code, setCode] = useState("");
  const [v, setV] = useState<Record<Key, number>>(Object.fromEntries(Object.entries(DEFAULTS).map(([k, d]) => [k, d.value])) as Record<Key, number>);
  const [creditOn, setCreditOn] = useState(false);
  const [gasOver, setGasOver] = useState<number | null>(null);    // "what would change the answer": the family's own prices
  const [powerOver, setPowerOver] = useState<number | null>(null);
  const set = (k: Key) => (x: number) => setV({ ...v, [k]: x });
  const st = states.find((s) => s.code === code) ?? null;
  const place = st ?? us;
  const gas = gasOver ?? place.gas?.value ?? null, power = powerOver ?? place.power?.value ?? null;
  const ready = gas !== null && power !== null;
  const x: Inputs | null = ready ? { miles: v.miles, mpg: v.mpg, kwhPerMile: v.kwhPerMile, gasUsdPerGal: gas, powerUsdPerMwh: power, gasCar: v.gasCar, evCar: v.evCar, years: v.years, rate: v.rate, credit: creditOn ? v.credit : 0 } : null;
  const r = x ? verdict(x) : null;
  const where = st ? st.name : "the United States as a whole";
  const gasWhere = place.gas?.where === "region" ? `${place.gas.region}: EIA does not publish a weekly price for ${st?.name}, so this is its region's` : place.gas?.where === "us" ? "the US average" : `${st?.name}'s own`;

  const card = (
    <div className="mb-4 grid gap-3 sm:grid-cols-2">
      <div className="border border-rule bg-paper p-4">
        <div className="text-xs text-muted">Electricity for homes in {where}</div>
        <div className="font-serif text-2xl">{place.power ? `${n2(place.power.value / 10)} cents a kWh` : "not held"}</div>
        {place.power ? <p className="text-xs text-muted">{month(place.power.ts)}, the newest month EIA has published. Table <span className="font-mono">{place.power.table}</span>, {place.power.entity}.</p> : null}
      </div>
      <div className="border border-rule bg-paper p-4">
        <div className="text-xs text-muted">Regular gasoline</div>
        <div className="font-serif text-2xl">{place.gas ? `${usd(place.gas.value, 3)} a gallon` : "not held"}</div>
        {place.gas ? <p className="text-xs text-muted">The week of {day(place.gas.ts)}; {gasWhere}. Table <span className="font-mono">{place.gas.table}</span>, {place.gas.entity}.</p> : null}
      </div>
    </div>
  );
  const nav = (
    <div className="mt-6 flex flex-wrap items-center gap-4 print:hidden">
      {step > 0 ? <button type="button" onClick={() => setStep(step - 1)} className="border px-4 py-2">Back</button> : null}
      {step < SCREENS.length - 1 ? <button onClick={() => setStep(step + 1)} disabled={step === 0 && !code} className="border border-accent bg-accent px-4 py-2 text-white">Next</button> : null}
    </div>
  );
  const bar = (label: string, value: number, max: number, accent: boolean) => (
    <div className="mb-3">
      <div className="mb-1 flex justify-between text-sm"><span>{label}</span><span className="font-mono">{usd(value)}</span></div>
      <div className="h-6 w-full bg-[var(--color-rule)]"><div className={`h-6 ${accent ? "bg-accent" : "bg-[var(--color-ink)]"}`} style={{ width: `${max > 0 ? Math.max(0, (value / max) * 100) : 0}%` }} /></div>
    </div>
  );
  const fmtMiles = (m: number) => m.toLocaleString("en-US");

  return (
    <div data-ev-step={step}>
      {/* the five screens, as a bar and a count (as the tour's: app/tour/TourBar.tsx) */}
      <div className="mb-1 flex gap-1 print:hidden" aria-hidden="true">
        {SCREENS.map((s, i) => <span key={s} className={`block h-2 flex-1 ${i <= step ? "bg-[var(--color-ink)]" : "bg-[var(--color-rule)]"}`} />)}
      </div>
      <p className="mb-4 text-sm text-muted print:hidden">Step {step + 1} of {SCREENS.length}: {SCREENS[step]}</p>
      <h2 className="mb-3 text-xl">{SCREENS[step]}</h2>

      {step === 0 ? (
        <div>
          <label className="mb-4 block text-sm" htmlFor="ev-state">Your state:{" "}
            <select id="ev-state" value={code} onChange={(e) => { setCode(e.target.value); setGasOver(null); setPowerOver(null); }} className="border px-2 py-2">
              <option value="">Choose your state</option>
              {states.map((s) => <option key={s.code} value={s.code}>{s.name}</option>)}
            </select>
          </label>
          {st ? card : <p className="max-w-3xl text-sm text-muted">Pick your state to see what power and gasoline cost there. The game uses real prices from the U.S. Energy Information Administration (EIA).</p>}
        </div>
      ) : null}

      {step === 1 ? (
        <div>
          <p className="mb-4 max-w-3xl text-sm">How far your family drives, and how much fuel each car needs. Start from the numbers below and slide them to match your family.</p>
          <Slider k="miles" value={v.miles} set={set("miles")} fmt={(m) => `${fmtMiles(m)} miles`} />
          <Slider k="mpg" value={v.mpg} set={set("mpg")} fmt={(m) => `${m} mpg`} />
          <Slider k="kwhPerMile" value={v.kwhPerMile} set={set("kwhPerMile")} fmt={(m) => `${n2(m)} kWh`} />
          <button type="button" onClick={() => setV({ ...v, miles: DEFAULTS.miles.value, mpg: DEFAULTS.mpg.value, kwhPerMile: DEFAULTS.kwhPerMile.value })} className="border px-3 py-1 text-sm">Reset the car</button>
        </div>
      ) : null}

      {step === 2 ? (
        <div>
          <p className="mb-4 max-w-3xl text-sm">What each car costs to buy, and how long you keep it. Ask a dealer for real prices and slide these to match.</p>
          <Slider k="gasCar" value={v.gasCar} set={set("gasCar")} fmt={(m) => usd(m, 0)} />
          <Slider k="evCar" value={v.evCar} set={set("evCar")} fmt={(m) => usd(m, 0)} />
          <Slider k="years" value={v.years} set={set("years")} fmt={(m) => `${m} year${m === 1 ? "" : "s"}`} />
          <div className="mb-4 border border-rule p-4 text-sm" data-credit>
            <label className="flex items-center gap-2"><input type="checkbox" role="switch" checked={creditOn} onChange={(e) => setCreditOn(e.target.checked)} /> A federal tax credit for the EV</label>
            <p className="mt-1 max-w-3xl text-xs text-muted">{NO_CREDIT_LINE} The IRS: <a href={IRS_URL}>Credits for new clean vehicles purchased in 2023 or after</a> (the page reviewed 13 July 2026).</p>
            {creditOn ? <div className="mt-3"><Slider k="credit" value={v.credit} set={set("credit")} fmt={(m) => usd(m, 0)} /></div> : null}
          </div>
        </div>
      ) : null}

      {step === 3 && r && x ? (
        <div data-verdict>
          <p className="mb-3 max-w-3xl text-sm">Driving 100 miles in {where}:</p>
          {bar("Gasoline car", r.gasPer100, Math.max(r.gasPer100, r.evPer100), false)}
          {bar("EV", r.evPer100, Math.max(r.gasPer100, r.evPer100), true)}
          <p className="mb-4 max-w-3xl text-base">A year of driving, {fmtMiles(x.miles)} miles: <strong>{usd(r.gasYear, 0)}</strong> of gasoline or <strong>{usd(r.evYear, 0)}</strong> of electricity charged at home. {r.saveYear >= 0 ? <>The EV saves <strong>{usd(r.saveYear, 0)}</strong> a year.</> : <>The gasoline car costs <strong>{usd(-r.saveYear, 0)}</strong> less a year to fuel.</>}</p>
          <div className="mb-4 grid gap-3 sm:grid-cols-2">
            <div className="border border-rule p-4">
              <div className="text-xs text-muted">Payback</div>
              <div className="font-serif text-2xl" data-payback>{r.payback === null ? "never" : r.payback === 0 ? "at once" : `${n2(r.payback, 1)} years`}</div>
              <p className="text-xs text-muted">How long until the money saved on fuel adds up to what the EV costs more to buy{creditOn ? " (after the credit)" : ""}: {usd(r.extra, 0)}.</p>
            </div>
            <div className="border border-rule p-4">
              <div className="text-xs text-muted">Net present value, over {x.years} year{x.years === 1 ? "" : "s"}</div>
              <div className="font-serif text-2xl" data-npv>{usd(r.npv, 0)}</div>
              <p className="text-xs text-muted">What choosing the EV is worth today: each year&apos;s savings, counted for less the later they come (at {n2(x.rate, 1)} percent a year), less what it costs more to buy. Above zero, the EV comes out ahead.</p>
            </div>
          </div>
          <Slider k="rate" value={v.rate} set={set("rate")} fmt={(m) => `${n2(m, 1)} percent`} />
          <h3 className="mb-2 mt-6 text-base">What would change the answer</h3>
          <div className="mb-4 max-w-xl">
            <label className="block text-sm" htmlFor="ev-gas">Gasoline, a gallon: <strong className="font-mono">{usd(gas!, 3)}</strong>{gasOver !== null ? <span className="ml-2 text-xs text-muted">changed by you</span> : null}</label>
            <input id="ev-gas" type="range" min={2} max={8} step={0.01} value={gas!} onChange={(e) => setGasOver(Number(e.target.value))} className="w-full" />
            <label className="mt-3 block text-sm" htmlFor="ev-power">Electricity, a kWh: <strong className="font-mono">{n2(power! / 10)} cents</strong>{powerOver !== null ? <span className="ml-2 text-xs text-muted">changed by you</span> : null}</label>
            <input id="ev-power" type="range" min={50} max={600} step={1} value={power!} onChange={(e) => setPowerOver(Number(e.target.value))} className="w-full" />
            {gasOver !== null || powerOver !== null ? <button type="button" onClick={() => { setGasOver(null); setPowerOver(null); }} className="mt-2 border px-3 py-1 text-sm">Back to {where}&apos;s real prices</button> : null}
          </div>
          <p className="max-w-3xl text-xs text-muted">Left out: insurance, repairs, charging away from home (it costs more), a home charger, and what the car is worth when you sell it. The game does not tell you what to buy: it shows what each choice costs at these prices.</p>
        </div>
      ) : null}

      {step === 4 && r && x ? (
        <div data-parents>
          <p className="mb-3 max-w-3xl text-base">For {where}: driving 100 miles costs {usd(r.gasPer100)} on gasoline and {usd(r.evPer100)} on electricity. Over a year that is {usd(r.saveYear, 0)} {r.saveYear >= 0 ? "saved with the EV" : "more with the EV"}; payback {r.payback === null ? "never comes" : r.payback === 0 ? "is at once" : `takes ${n2(r.payback, 1)} years`}, and the net present value over {x.years} years is {usd(r.npv, 0)}.</p>
          <table className="mb-4 w-full max-w-3xl text-sm" aria-label="Every number used">
            <thead><tr className="text-left text-xs text-muted"><th className="py-1 font-normal">Number</th><th className="py-1 pl-2 text-right font-normal">Value</th><th className="py-1 pl-2 font-normal">Where it comes from</th></tr></thead>
            <tbody>
              <tr className="border-b border-rule"><th scope="row" className="py-1 text-left font-normal">Electricity</th><td className="py-1 pl-2 text-right font-mono">{n2(power! / 10)} cents/kWh</td><td className="py-1 pl-2 text-xs">{powerOver !== null ? "changed by you" : place.power ? `${place.power.table}, ${place.power.entity}, ${month(place.power.ts)} (EIA)` : ""}</td></tr>
              <tr className="border-b border-rule"><th scope="row" className="py-1 text-left font-normal">Gasoline</th><td className="py-1 pl-2 text-right font-mono">{usd(gas!, 3)}/gal</td><td className="py-1 pl-2 text-xs">{gasOver !== null ? "changed by you" : place.gas ? `${place.gas.table}, ${place.gas.entity}, the week of ${day(place.gas.ts)} (EIA; ${gasWhere})` : ""}</td></tr>
              {(["miles", "mpg", "kwhPerMile", "gasCar", "evCar", "years", "rate"] as Key[]).map((k) => (
                <tr key={k} className="border-b border-rule"><th scope="row" className="py-1 text-left font-normal">{DEFAULTS[k].label}</th><td className="py-1 pl-2 text-right font-mono">{k === "gasCar" || k === "evCar" ? usd(v[k], 0) : k === "kwhPerMile" ? n2(v[k]) : v[k].toLocaleString("en-US")}</td><td className="py-1 pl-2 text-xs">{v[k] === DEFAULTS[k].value ? DEFAULTS[k].source : "changed by you"}</td></tr>
              ))}
              <tr className="border-b border-rule"><th scope="row" className="py-1 text-left font-normal">Federal tax credit</th><td className="py-1 pl-2 text-right font-mono">{usd(x.credit, 0)}</td><td className="py-1 pl-2 text-xs">{creditOn ? "your family's assumption; " : ""}{NO_CREDIT_LINE} (irs.gov)</td></tr>
            </tbody>
          </table>
          <PrintButton label="Print for my parents" />
          <p className="mt-3 max-w-3xl text-xs text-muted">Prices built into the game on {built.slice(0, 10)} from the Energy Research Warehouse&apos;s copies of EIA&apos;s tables. How it works: <Link href="/data/methods/ev_game">the method</Link>.</p>
        </div>
      ) : null}

      {nav}
    </div>
  );
}
