"use client";
// Session 294: "Should your family get an EV?". Sessions 3275 to 3278 (chain 198, the owner's ruling of 14 October 2026
// read again): one screen, the household's inputs on the left and the results on the right. Every default is drawn in
// grey with its source in a hover tip (the owner's rule: explanatory text only as hover, never as visible grey text);
// what the family moves turns ink and says "changed by you". The verdict is payback in years and the net present value,
// the upfront cost included; the federal credit is off until the family switches it on. One chart: what each car has
// cost by each year, the crossing marked, a hover with the values. The prices are the warehouse's (data/ev_prices.json);
// the arithmetic is lib/ev.ts; the method docs/methods/ev_game.md. The brand's rules (docs/brand.md): tokens only,
// square, no motion, cardinal for the highlighted series (the EV).
import { useEffect, useRef, useState, type ReactNode } from "react";
import { DEFAULTS, IRS_URL, NO_CREDIT_LINE, chargePrice, cumulative, keyed, verdict, type Inputs } from "@/lib/ev";
import { PrintButton } from "@/app/learn/problems/PrintButton";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { Num } from "@/components/Num";
import { Tip } from "@/components/tool/ToolPage";

export type Cell = { value: number; unit: string; ts: string; entity: string; table: string; where?: string; region?: string } | null;
export type StatePrices = { code: string; name: string; power: Cell; gas: Cell };

const usd = (v: number, d = 0) => `${v < 0 ? "-" : ""}$${Math.abs(v).toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d })}`;
const n2 = (v: number, d = 2) => v.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
const month = (ts: string) => new Date(`${ts}T12:00:00Z`).toLocaleDateString("en-US", { month: "long", year: "numeric", timeZone: "UTC" });
const day = (ts: string) => new Date(`${ts}T12:00:00Z`).toLocaleDateString("en-US", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });
type Key = keyof typeof DEFAULTS;
const FIELDS: Key[] = ["miles", "mpg", "kwhPerMile", "gasCar", "evCar", "homeShare", "years", "rate"];
const FMT: Record<Key, (v: number) => string> = {
  miles: (m) => `${m.toLocaleString("en-US")} miles`, mpg: (m) => `${m} mpg`, kwhPerMile: (m) => `${n2(m)} kWh`, gasCar: (m) => usd(m), evCar: (m) => usd(m),
  homeShare: (m) => `${m} percent`, years: (m) => `${m} year${m === 1 ? "" : "s"}`, rate: (m) => `${n2(m, 1)} percent`, credit: (m) => usd(m),
};

/** One input: its label, its source as a hover tip, the value in grey while it is the default (ink and "changed by you"
 *  once moved), the slider, and a reset named for it. */
function Field({ id, label, tip, value, shown, mine, min, max, step, set, reset }: {
  id: string; label: string; tip: ReactNode; value: number; shown: string; mine: boolean; min: number; max: number; step: number; set: (v: number) => void; reset: () => void;
}) {
  return (
    <div className="mb-4" data-field={id}>
      <div className="flex flex-wrap items-baseline justify-between gap-x-3 text-sm">
        <span><label htmlFor={`ev-${id}`}>{label}</label><Tip id={`ev-${id}`} label={label}>{tip}</Tip></span>
        <span className={`font-mono ${mine ? "font-semibold text-ink" : "text-muted"}`} data-default={mine ? undefined : "1"}>{shown}</span>
      </div>
      <input id={`ev-${id}`} type="range" min={min} max={max} step={step} value={value} onChange={(e) => set(Number(e.target.value))} className="mt-1 h-6 w-full accent-[var(--color-ink)]" />
      {mine ? <div className="text-xs"><span>{"changed by you"}</span> <button type="button" onClick={reset} className="ml-1 border px-2 py-0.5">Reset {label.toLowerCase()}</button></div> : null}
    </div>
  );
}

/** The chart: what each car has cost by the end of each year (its price, then fuel added), the crossing marked. Hover,
 *  a tap or the arrow keys pick a year and show both values. */
function CostChart({ rows, cross, years }: { rows: { year: number; gas: number; ev: number }[]; cross: number | null; years: number }) {
  const [at, setAt] = useState<number | null>(null);
  // session 3277: the chart is drawn at the width it is shown (at 390 px a 640-wide drawing scaled its 12 px labels to 6)
  const [W, setW] = useState(640);
  const box = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const el = box.current;
    if (!el || typeof ResizeObserver === "undefined") return;
    const ro = new ResizeObserver(() => setW(Math.max(280, Math.round(el.clientWidth))));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  const H = W < 500 ? 240 : 300, L = W < 500 ? 48 : 64, R = 16, T = 24, B = 40;
  const top = Math.max(...rows.flatMap((r) => [r.gas, r.ev]));
  const step = top > 100000 ? 20000 : top > 40000 ? 10000 : 5000;
  const ymax = Math.ceil(top / step) * step;
  const x = (t: number) => L + (t / Math.max(1, years)) * (W - L - R);
  const y = (v: number) => T + (1 - v / ymax) * (H - T - B);
  const line = (k: "gas" | "ev") => rows.map((r, i) => `${i ? "L" : "M"}${x(r.year).toFixed(1)},${y(r[k]).toFixed(1)}`).join(" ");
  const ticks = Array.from({ length: ymax / step + 1 }, (_, i) => i * step);
  const crossY = cross !== null ? y(rows[0].gas + ((rows[1]?.gas ?? rows[0].gas) - rows[0].gas) * cross) : 0;
  const pick = (clientX: number, box: DOMRect) => {
    const px = ((clientX - box.left) / box.width) * W;
    setAt(Math.max(0, Math.min(years, Math.round(((px - L) / (W - L - R)) * years))));
  };
  const hover = at !== null ? rows[at] : null;
  const summary = `Cumulative cost by year, ${years} years. Gasoline car from ${usd(rows[0].gas)} to ${usd(rows[rows.length - 1].gas)}; EV from ${usd(rows[0].ev)} to ${usd(rows[rows.length - 1].ev)}.${cross !== null ? ` The lines cross at ${n2(cross, 1)} years.` : ""}`;
  return (
    <div className="relative" data-ev-chart ref={box}>
      <svg viewBox={`0 0 ${W} ${H}`} className="h-auto w-full touch-none select-none" role="img" aria-label={summary} tabIndex={0}
        onPointerMove={(e) => pick(e.clientX, e.currentTarget.getBoundingClientRect())} onPointerDown={(e) => pick(e.clientX, e.currentTarget.getBoundingClientRect())} onPointerLeave={() => setAt(null)}
        onKeyDown={(e) => { if (e.key === "ArrowRight") { setAt(Math.min(years, (at ?? -1) + 1)); e.preventDefault(); } if (e.key === "ArrowLeft") { setAt(Math.max(0, (at ?? 1) - 1)); e.preventDefault(); } if (e.key === "Escape") setAt(null); }}
        onBlur={() => setAt(null)}>
        {ticks.map((v) => (
          <g key={v}>
            <line x1={L} x2={W - R} y1={y(v)} y2={y(v)} stroke="var(--color-rule)" strokeWidth={1} />
            <text x={L - 6} y={y(v) + 4} textAnchor="end" fontSize={12} fill="var(--color-muted)">{v === 0 ? "$0" : `$${v / 1000}k`}</text>
          </g>
        ))}
        {rows.map((r) => <text key={r.year} x={x(r.year)} y={H - B + 18} textAnchor="middle" fontSize={12} fill="var(--color-muted)">{years > 10 && r.year % 2 ? "" : r.year}</text>)}
        <text x={(L + W - R) / 2} y={H - 4} textAnchor="middle" fontSize={12} fill="var(--color-muted)">years</text>
        <path d={line("gas")} fill="none" stroke="var(--color-ink)" strokeWidth={2} strokeDasharray="6 4" />
        <path d={line("ev")} fill="none" stroke="var(--color-accent)" strokeWidth={2.5} />
        {cross !== null ? (
          <g data-ev-cross>
            <line x1={x(cross)} x2={x(cross)} y1={T} y2={H - B} stroke="var(--color-muted)" strokeWidth={1} strokeDasharray="2 3" />
            <circle cx={x(cross)} cy={crossY} r={5} fill="var(--color-paper)" stroke="var(--color-accent)" strokeWidth={2} />
            <text x={x(cross) > W - R - 150 ? x(cross) - 8 : x(cross) + 8} textAnchor={x(cross) > W - R - 150 ? "end" : "start"} y={T - 8} fontSize={12} fill="var(--color-ink)">they cross at {n2(cross, 1)} years</text>
          </g>
        ) : null}
        {hover ? (
          <g>
            <line x1={x(hover.year)} x2={x(hover.year)} y1={T} y2={H - B} stroke="var(--color-ink)" strokeWidth={1} />
            <circle cx={x(hover.year)} cy={y(hover.gas)} r={4} fill="var(--color-ink)" />
            <circle cx={x(hover.year)} cy={y(hover.ev)} r={4} fill="var(--color-accent)" />
          </g>
        ) : null}
      </svg>
      <div role="status" aria-live="polite" className="min-h-[1.5rem] text-sm" data-ev-hover>
        {hover ? <>Year {hover.year}: gasoline car <strong className="font-mono">{usd(hover.gas)}</strong>, EV <strong className="font-mono text-accent">{usd(hover.ev)}</strong></> : null}
      </div>
    </div>
  );
}

export function EvGame({ states, us, built }: { states: StatePrices[]; us: StatePrices; built: string }) {
  const [code, setCode] = useState("US");
  const [v, setV] = useState<Record<Key, number>>(Object.fromEntries(Object.entries(DEFAULTS).map(([k, d]) => [k, d.value])) as Record<Key, number>);
  const [creditOn, setCreditOn] = useState(false);
  const [gasOver, setGasOver] = useState<number | null>(null);
  const [powerOver, setPowerOver] = useState<number | null>(null);
  const [publicCents, setPublicCents] = useState<string>("");
  const set = (k: Key) => (x: number) => setV({ ...v, [k]: x });
  const st = states.find((s) => s.code === code) ?? null;
  const place = st ?? us;
  const where = st ? st.name : "the United States as a whole";
  const gas = gasOver ?? place.gas?.value ?? null, power = powerOver ?? place.power?.value ?? null;
  const pub = publicCents.trim() === "" ? null : Number(publicCents) * 10;   // cents a kWh to USD/MWh
  const x: Inputs | null = gas !== null && power !== null ? { miles: v.miles, mpg: v.mpg, kwhPerMile: v.kwhPerMile, gasUsdPerGal: gas, powerUsdPerMwh: power, gasCar: v.gasCar, evCar: v.evCar, years: v.years, rate: v.rate, credit: creditOn ? v.credit : 0, homeShare: v.homeShare, publicUsdPerMwh: pub !== null && Number.isFinite(pub) && pub >= 0 ? pub : null } : null;
  const priced = x !== null && chargePrice(x) !== null;
  const r = x && priced ? verdict(x) : null;
  const c = x && priced ? cumulative(x) : null;
  // the server's page (the United States, every default, nothing moved) carries the keyed figures for check-values
  const atDefaults = !creditOn && gasOver === null && powerOver === null && FIELDS.every((k) => v[k] === DEFAULTS[k].value);
  const k = atDefaults && place.power && place.gas ? keyed(place.power.value, place.gas.value) : null;
  const ck = (f: string) => `ev|${place.code}|${f}`;
  const gasWhere = place.gas?.where === "region" ? `${place.gas.region}: EIA does not publish a weekly price for ${st?.name}, so this is its region's` : place.gas?.where === "us" ? "the US average" : `${st?.name}'s own weekly series`;
  const fieldOf = (key: Key) => {
    const d = DEFAULTS[key];
    return <Field key={key} id={key} label={d.label} tip={<>Default {FMT[key](d.value)}. {d.source}.</>} value={v[key]} shown={FMT[key](v[key])} mine={v[key] !== d.value} min={d.min} max={d.max} step={d.step} set={set(key)} reset={() => set(key)(d.value)} />;
  };
  const resetAll = () => { setV(Object.fromEntries(Object.entries(DEFAULTS).map(([kk, d]) => [kk, d.value])) as Record<Key, number>); setCreditOn(false); setGasOver(null); setPowerOver(null); setPublicCents(""); };

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,24rem)_minmax(0,1fr)]" data-ev-one-screen>
      {/* the household, on the left */}
      <section className="bg-paper px-4 py-4" aria-label="Your family's choices" data-ev-inputs>
        <h2 className="mb-3 font-serif text-lg text-accent">Your family</h2>
        <div className="mb-4 text-sm">
          <label htmlFor="ev-state">Your state</label><Tip id="ev-state-tip" label="Your state">Each state&apos;s newest prices from the warehouse&apos;s copies of two EIA tables. Before you choose, the game uses the average of the whole country.</Tip>
          <select id="ev-state" value={code} onChange={(e) => { setCode(e.target.value); setGasOver(null); setPowerOver(null); }} className="mt-1 block w-full max-w-full border bg-white px-2 py-2">
            <option value="US">United States (average)</option>
            {states.map((s) => <option key={s.code} value={s.code}>{s.name}</option>)}
          </select>
        </div>
        {place.power ? (
          <Field id="power" label="Electricity at home, cents a kWh" value={power!} shown={`${n2(power! / 10)} cents`} mine={powerOver !== null} min={50} max={600} step={1}
            tip={<>Default {n2(place.power.value / 10)} cents: the average price homes paid in {where} in {month(place.power.ts)}, the newest month EIA has published. Table {place.power.table}, entity {place.power.entity}.</>}
            set={setPowerOver} reset={() => setPowerOver(null)} />
        ) : <p className="mb-4 text-sm">Electricity: not held for {where}.</p>}
        {place.gas ? (
          <Field id="gas" label="Gasoline, a gallon" value={gas!} shown={usd(gas!, 3)} mine={gasOver !== null} min={2} max={8} step={0.01}
            tip={<>Default {usd(place.gas.value, 3)}: regular gasoline, the week of {day(place.gas.ts)}; {gasWhere}. Table {place.gas.table}, entity {place.gas.entity}.</>}
            set={setGasOver} reset={() => setGasOver(null)} />
        ) : <p className="mb-4 text-sm">Gasoline: not held for {where}.</p>}
        {(["miles", "mpg", "kwhPerMile", "gasCar", "evCar", "homeShare"] as Key[]).map(fieldOf)}
        {v.homeShare < 100 ? (
          <div className="mb-4 text-sm" data-field="public">
            <label htmlFor="ev-public">A public charger&apos;s price, cents a kWh</label><Tip id="ev-public-tip" label="A public charger's price">The warehouse holds no prices for public chargers, so the game does not guess one. Type the price a charger near you shows. Until you do, the results wait.</Tip>
            <input id="ev-public" type="number" inputMode="decimal" min={0} max={200} step={1} value={publicCents} onChange={(e) => setPublicCents(e.target.value)} className="mt-1 block w-32 border bg-white px-2 py-1 font-mono" />
          </div>
        ) : null}
        {(["years", "rate"] as Key[]).map(fieldOf)}
        <div className="mb-4 border border-rule bg-white p-3 text-sm" data-credit>
          <span className="flex items-center gap-2">
            <input id="ev-credit" type="checkbox" role="switch" checked={creditOn} onChange={(e) => setCreditOn(e.target.checked)} />
            <label htmlFor="ev-credit">Federal tax credit for the EV</label>
            <Tip id="ev-credit-tip" label="The federal tax credit">{NO_CREDIT_LINE} The IRS: <a href={IRS_URL}>Credits for new clean vehicles purchased in 2023 or after</a> (reviewed 13 July 2026). Switch it on to see what a credit would change; the amount is then your family&apos;s assumption.</Tip>
            <span className={creditOn ? "font-semibold" : "text-muted"}>{creditOn ? "on" : "off"}</span>
          </span>
          {creditOn ? <div className="mt-3">{fieldOf("credit")}</div> : null}
        </div>
        <button type="button" onClick={resetAll} className="border px-3 py-1 text-sm">Reset everything</button>
      </section>

      {/* the results, on the right */}
      <section aria-label="What it comes to" data-ev-results>
        {r && x && c ? (
          <>
            <div className="mb-6 grid gap-6 sm:grid-cols-2">
              <div className="border-t-2 border-accent pt-2" data-payback>
                <div className="text-xs uppercase tracking-wide text-muted">Payback<span className="normal-case tracking-normal"><Tip id="ev-payback-tip" label="Payback">How many years until the money saved on fuel adds up to what the EV costs more to buy{creditOn ? ", after the credit" : ""}: {usd(r.extra)}. &quot;At once&quot; when the EV costs no more; &quot;never&quot; when it saves nothing a year.</Tip></span></div>
                <div className="mt-1 font-serif text-3xl tabular-nums text-ink">
                  {r.payback === null ? "never" : r.payback === 0 ? "at once" : k && k.payback !== null ? <><Num check={ck("payback")} raw={k.payback}>{String(k.payback)}</Num> years</> : `${n2(r.payback, 1)} years`}
                </div>
              </div>
              <div className="border-t-2 border-accent pt-2" data-npv>
                <div className="text-xs uppercase tracking-wide text-muted">Net present value, {x.years} year{x.years === 1 ? "" : "s"}<span className="normal-case tracking-normal"><Tip id="ev-npv-tip" label="Net present value">What choosing the EV is worth today: each year&apos;s saving on fuel, counted for less the later it comes (at {n2(x.rate, 1)} percent a year), added up, less what the EV costs more to buy. Above zero, the EV comes out ahead at these prices; below zero, the gasoline car does. Left out: repairs and maintenance, insurance, a home charger, state incentives, and what each car is worth when sold.</Tip></span></div>
                <div className="mt-1 font-serif text-3xl tabular-nums text-ink">
                  {k && k.npv >= 0 ? <>$<Num check={ck("npv")} raw={k.npv}>{k.npv.toLocaleString("en-US")}</Num></> : usd(r.npv)}
                </div>
              </div>
            </div>
            <table className="mb-6 w-full max-w-xl text-sm tabular-nums" aria-label="A year of fuel">
              <tbody>
                <tr className="border-b border-rule"><th scope="row" className="py-1 text-left font-normal">A year of gasoline</th><td className="py-1 text-right font-mono">{usd(r.gasYear)}</td></tr>
                <tr className="border-b border-rule"><th scope="row" className="py-1 text-left font-normal">A year of electricity</th><td className="py-1 text-right font-mono">{usd(r.evYear)}</td></tr>
                <tr className="border-b border-rule"><th scope="row" className="py-1 text-left font-normal">{r.saveYear >= 0 ? "Saved a year with the EV" : "Extra a year with the EV"}</th><td className="py-1 text-right font-mono">{usd(Math.abs(r.saveYear))}</td></tr>
              </tbody>
            </table>
            {k ? <p className="sr-only">The prices used: <Num check={ck("power_cents")} raw={k.power_cents}>{n2(k.power_cents)}</Num> cents a kWh and <Num check={ck("gas")} raw={k.gas}>{String(k.gas)}</Num> dollars a gallon.</p> : null}
            <figure className="mb-6">
              <figcaption className="mb-2 flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1 border-b border-rule pb-1">
                <span className="font-serif text-xl text-accent">What each car has cost, year by year<Tip id="ev-chart-tip" label="The chart">Each line starts at the car&apos;s price and adds a year of fuel at a time, at today&apos;s prices, not discounted. Where they cross, the EV has paid back what it cost more to buy. Point at the chart, tap it, or use the arrow keys to read a year.</Tip></span>
                <span className="flex flex-wrap gap-x-4 text-xs text-ink">
                  <span className="inline-flex items-center gap-1.5"><span aria-hidden="true" className="inline-block h-0 w-5 border-t-2 border-dashed border-ink" />Gasoline car</span>
                  <span className="inline-flex items-center gap-1.5"><span aria-hidden="true" className="inline-block h-0.5 w-5 bg-accent" />EV</span>
                </span>
              </figcaption>
              <CostChart rows={c.rows} cross={c.cross} years={x.years} />
            </figure>
          </>
        ) : (
          <p className="mb-6 text-base" data-ev-waiting>Type a public charger&apos;s price on the left to see the results.</p>
        )}
        <details className="border-b border-rule py-2" data-parents>
          <summary className="cursor-pointer font-serif text-lg text-accent">Every number, for your parents</summary>
          <table className="mt-3 w-full text-sm" aria-label="Every number used">
            <thead><tr className="text-left text-xs"><th className="py-1 font-normal">Number</th><th className="py-1 pl-2 text-right font-normal">Value</th><th className="py-1 pl-2 font-normal">Where it comes from</th></tr></thead>
            <tbody>
              <tr className="border-b border-rule"><th scope="row" className="py-1 text-left font-normal">Electricity at home</th><td className="py-1 pl-2 text-right font-mono">{power !== null ? `${n2(power / 10)} cents/kWh` : "not held"}</td><td className="py-1 pl-2 text-xs [overflow-wrap:anywhere]">{powerOver !== null ? "changed by you" : place.power ? `${place.power.table}, ${place.power.entity}, ${month(place.power.ts)}` : ""}</td></tr>
              <tr className="border-b border-rule"><th scope="row" className="py-1 text-left font-normal">Gasoline</th><td className="py-1 pl-2 text-right font-mono">{gas !== null ? `${usd(gas, 3)}/gal` : "not held"}</td><td className="py-1 pl-2 text-xs [overflow-wrap:anywhere]">{gasOver !== null ? "changed by you" : place.gas ? `${place.gas.table}, ${place.gas.entity}, week of ${day(place.gas.ts)}` : ""}</td></tr>
              {FIELDS.map((kk) => (
                <tr key={kk} className="border-b border-rule"><th scope="row" className="py-1 text-left font-normal">{DEFAULTS[kk].label}</th><td className="py-1 pl-2 text-right font-mono">{FMT[kk](v[kk])}</td><td className="py-1 pl-2 text-xs [overflow-wrap:anywhere]">{v[kk] !== DEFAULTS[kk].value ? "changed by you" : DEFAULTS[kk].source}</td></tr>
              ))}
              {v.homeShare < 100 ? <tr className="border-b border-rule"><th scope="row" className="py-1 text-left font-normal">A public charger&apos;s price</th><td className="py-1 pl-2 text-right font-mono">{publicCents.trim() === "" ? "not typed" : `${publicCents} cents/kWh`}</td><td className="py-1 pl-2 text-xs">typed by you</td></tr> : null}
              <tr className="border-b border-rule"><th scope="row" className="py-1 text-left font-normal">Federal tax credit</th><td className="py-1 pl-2 text-right font-mono">{usd(creditOn ? v.credit : 0)}</td><td className="py-1 pl-2 text-xs [overflow-wrap:anywhere]">{creditOn ? "your family's assumption; " : ""}{NO_CREDIT_LINE} (irs.gov)</td></tr>
            </tbody>
          </table>
          <div className="mt-3 flex flex-wrap items-center gap-4 text-sm">
            <PrintButton label="Print for my parents" />
            <span>Prices built into the game on {built.slice(0, 10)}. <Link href="/data/methods/ev_game">How it works</Link>.</span>
          </div>
        </details>
      </section>
    </div>
  );
}
