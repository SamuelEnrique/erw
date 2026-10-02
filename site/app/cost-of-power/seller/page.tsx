import type { Metadata } from "next";
import Link from "next/link";
import fs from "node:fs";
import path from "node:path";
import { Cite } from "@/components/Cite";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { shown } from "@/lib/format";
import {
  ASSET_NAMES, DEBT, DEFAULT_SIZE, DEFAULTS, durationOf, EVENTS, HEAT_RATE, inputsKey, inputsOf, ISO_NAMES, keyOf, months, stress, summary, ttm, VOM,
  type Asset, type Month, type Snapshot,
} from "@/lib/merchant";
import { TIER_LABEL, TIER_TITLE } from "@/lib/tiers";
import { CostTabs } from "../Tabs";

// Session 51: the cost of power, the seller's side ("What a generator earns"). Merchant revenue per month at an ISO's
// main hub for a solar, wind, battery or gas peaker asset of the reader's size, the bad months, the ERCOT stress days,
// and debt service coverage. Every number is computed by lib/merchant.ts from data/merchant_snapshot.json
// (warehouse/derived/merchant_revenue.py; its table merchant_revenue_monthly holds the same monthly figures) and carries
// a check key (mr|<inputs>|<stat>) that scripts/check-values.mjs recomputes. The snapshot is not in Supabase.
export const metadata: Metadata = { title: "Cost of power: what a generator earns" };
export const dynamic = "force-dynamic";

const METHOD = "/data/methods/cost_of_power";
const T = "merchant_revenue_monthly";
let SNAP: Snapshot | null = null;
function snapshot(): Snapshot {
  if (!SNAP) SNAP = JSON.parse(fs.readFileSync(path.join(process.cwd(), "data", "merchant_snapshot.json"), "utf8")) as Snapshot;
  return SNAP;
}

function Tier() {
  return (
    <Link href="/data/standard" title={TIER_TITLE.derived} className="ml-1 rounded border border-rule px-1 text-[10px] uppercase tracking-wide text-muted no-underline">
      {TIER_LABEL.derived}
    </Link>
  );
}
/** US dollars, short, as scripts/check-values.mjs formats data-format usd. */
function usdShort(v: number) {
  const t = (x: number) => x.toLocaleString("en-US", { maximumFractionDigits: 2 });
  if (Math.abs(v) >= 1e9) return `${t(v / 1e9)} billion`;
  if (Math.abs(v) >= 1e6) return `${t(v / 1e6)} million`;
  return v.toLocaleString("en-US");
}
/** A number with its check key (mr|<inputs>|<stat>); a count, a ratio or USD as the page shows it. */
function V({ pre, stat, v, d }: { pre: string; stat: string; v: number | null; d?: (v: number) => string }) {
  return v === null ? <span className="text-muted">not held</span> : <Num check={`mr|${pre}|${stat}`} raw={v}>{d ? d(v) : shown(v)}</Num>;
}
function U({ pre, stat, v }: { pre: string; stat: string; v: number | null }) {
  return v === null ? <span className="text-muted">not held</span> : <span data-format="usd"><Num check={`mr|${pre}|${stat}`} raw={v}>{usdShort(v)}</Num></span>;
}
const count = (v: number) => String(v);
/** Session 65: where the hubs outside ERCOT start and how many months they hold, read from the snapshot's own months
 * (the months of merchant_revenue_monthly), so the sentences that state them cannot go stale when the history grows. */
function otherHubs(snap: Snapshot) {
  const spans = Object.values(snap.isos).filter((s) => s.iso !== "ercot").map((s) => {
    const ks = Object.keys(s.months).sort();
    return { first: ks[0], n: ks.length };
  });
  const first = spans.map((s) => s.first).sort()[0];
  const lo = Math.min(...spans.map((s) => s.n)), hi = Math.max(...spans.map((s) => s.n));
  return { first, count: lo === hi ? `${lo}` : `${lo} to ${hi}` };
}
const firstMonth = (snap: Snapshot, iso: string) => Object.keys(snap.isos[iso].months).sort()[0];
const monthName = (m: string) => new Date(`${m}-15T12:00:00Z`).toLocaleString("en-US", { month: "long", year: "numeric", timeZone: "UTC" });

/** Monthly revenue, one bar per month: held months in ink, the ones below the debt service's month in cardinal, months
 * held for less than 90 percent of their hours hatched grey. */
function RevenueBars({ ms, dsMonth }: { ms: Month[]; dsMonth: number }) {
  const W = 760, H = 230, L = 70, R = 8, top = 10, bot = 26;
  const vals = ms.map((r) => r.revenue);
  const hi = Math.max(dsMonth, ...vals, 1), lo = Math.min(0, ...vals);
  const y = (v: number) => top + ((hi - v) / (hi - lo)) * (H - top - bot);
  const bw = (W - L - R) / ms.length;
  const years = ms.map((r, i) => ({ i, y: r.m.slice(0, 4), first: i === 0 || ms[i - 1].m.slice(0, 4) !== r.m.slice(0, 4) })).filter((x) => x.first);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="Revenue per month, USD; a dashed line marks one month of debt service">
      {[lo, (lo + hi) / 2, hi].map((t, k) => (
        <g key={k}>
          <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke="var(--color-rule)" />
          <text x={L - 6} y={y(t) + 4} textAnchor="end" fontSize="10" fill="var(--color-muted)">{usdShort(Math.round(t))}</text>
        </g>
      ))}
      {ms.map((r, i) => (
        <rect key={r.m} x={L + i * bw + 0.5} width={Math.max(1, bw - 1)} y={Math.min(y(r.revenue), y(0))} height={Math.max(1, Math.abs(y(r.revenue) - y(0)))}
          fill={!r.held ? "var(--color-rule)" : r.revenue < dsMonth ? "var(--color-accent)" : "var(--color-ink)"}>
          <title>{`${r.m}: ${usdShort(Math.round(r.revenue))} USD${r.held ? "" : ` (only ${Math.round(r.share * 100)} percent of the month held)`}`}</title>
        </rect>
      ))}
      {dsMonth > 0 ? <line x1={L} x2={W - R} y1={y(dsMonth)} y2={y(dsMonth)} stroke="var(--color-accent)" strokeDasharray="5 4" /> : null}
      {years.map((x) => <text key={x.i} x={L + x.i * bw} y={H - 8} fontSize="10" fill="var(--color-muted)">{x.y}</text>)}
    </svg>
  );
}

/** Coverage: the trailing-twelve-month DSCR, with the 1.0x and 1.25x lines. */
function CoverageLine({ t }: { t: { m: string; dscr: number }[] }) {
  if (t.length < 2) return null;
  const W = 760, H = 200, L = 44, R = 8, top = 10, bot = 26;
  const vals = t.map((r) => r.dscr);
  const hi = Math.max(1.5, ...vals), lo = Math.min(0, ...vals);
  const y = (v: number) => top + ((hi - v) / (hi - lo)) * (H - top - bot);
  const x = (i: number) => L + (i / (t.length - 1)) * (W - L - R);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="Trailing-twelve-month debt service coverage; lines at 1.0 and 1.25 times">
      {[1, 1.25].map((v) => (
        <g key={v}>
          <line x1={L} x2={W - R} y1={y(v)} y2={y(v)} stroke="var(--color-accent)" strokeDasharray={v === 1 ? "" : "5 4"} />
          <text x={L - 6} y={y(v) + 4} textAnchor="end" fontSize="10" fill="var(--color-accent)">{v}x</text>
        </g>
      ))}
      <text x={L - 6} y={y(hi) + 4} textAnchor="end" fontSize="10" fill="var(--color-muted)">{hi.toFixed(1)}x</text>
      <path d={t.map((r, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(r.dscr).toFixed(1)}`).join(" ")} fill="none" stroke="var(--color-ink)" strokeWidth="2" />
      {[0, Math.floor((t.length - 1) / 2), t.length - 1].map((i) => <text key={i} x={x(i)} y={H - 8} fontSize="10" textAnchor="middle" fill="var(--color-muted)">{t[i].m}</text>)}
    </svg>
  );
}

export default async function Seller({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const q = Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined]));
  const snap = snapshot();
  const x = inputsOf(q);
  const key = inputsKey(x);
  const s = snap.isos[x.iso];
  const k = keyOf(x);
  const ms = months(snap, x);
  const others = otherHubs(snap);
  const sm = summary(ms);
  const t = ttm(ms, x.ds);
  const st = stress(snap, x);
  const held = ms.filter((r) => r.held);
  const dsMonth = x.ds / 12;
  const under1 = held.filter((r) => r.dscr !== null && r.dscr < 1), under125 = held.filter((r) => r.dscr !== null && r.dscr < 1.25);
  const annual = held.length ? (held.reduce((a, r) => a + r.revenue, 0) / held.length) * 12 : null;
  const D = DEFAULTS[k];
  const field = "border border-rule bg-panel px-2 py-1 text-sm";
  const sizeLabel = x.asset === "battery" ? `${x.mw} MW / ${x.mwh} MWh` : `${x.mw} MW`;
  const isos = Object.keys(ISO_NAMES);

  return (
    <>
      <h1 className="mb-1 text-3xl">Cost of power</h1>
      <CostTabs active="sell" />
      <div className="mb-4 max-w-3xl space-y-2 text-sm">
        <p>
          What a power plant earns selling at an ISO&apos;s main hub, month by month: a solar or wind farm, a battery, or a gas peaker of your size, at the
          real-time price. For a lender the question is the downside: the bad months, the stress days, and whether the revenue covers the debt.
        </p>
        <p className="border-l-2 border-accent pl-2 text-muted">
          <strong>Merchant only.</strong> No power purchase agreement, hedge, capacity payment or ancillary service: the asset sells every MWh at the hub&apos;s
          real-time price. Real projects are rarely fully merchant, because lenders size debt on contracted cash flows; this tab shows what is left when the
          contract is gone, or what an uncontracted tail earns. <Link href={METHOD}>Method</Link>.
        </p>
      </div>

      <Section title="Your asset">
        <form method="get" className="flex flex-wrap items-end gap-3 text-sm">
          <label className="flex flex-col">ISO and hub
            <select name="iso" defaultValue={x.iso} className={field}>{isos.map((i) => <option key={i} value={i}>{ISO_NAMES[i]}, {snap.isos[i].hub}</option>)}</select>
          </label>
          <label className="flex flex-col">Asset
            <select name="asset" defaultValue={x.asset} className={field}>{(Object.keys(ASSET_NAMES) as Asset[]).map((a) => <option key={a} value={a}>{ASSET_NAMES[a]}</option>)}</select>
          </label>
          <label className="flex flex-col">Size, MW<input name="mw" type="number" min={1} max={5000} step="any" defaultValue={x.mw} className={`${field} w-24`} /></label>
          {x.asset === "battery" ? <label className="flex flex-col">Energy, MWh<input name="mwh" type="number" min={x.mw} max={x.mw * 8} step="any" defaultValue={x.mwh} className={`${field} w-24`} /></label> : null}
          <label className="flex flex-col">Annual debt service, USD<input name="ds" type="number" min={0} step="any" defaultValue={x.ds} className={`${field} w-36`} /></label>
          <label className="flex flex-col">Fixed O&amp;M, USD/kW-yr<input name="fom" type="number" min={0} step="any" defaultValue={x.fom} className={`${field} w-24`} /></label>
          {x.asset === "peaker" ? (
            <>
              <label className="flex flex-col">Heat rate, MMBtu/MWh<input name="hr" type="number" min={6} max={16} step="any" defaultValue={x.hr} className={`${field} w-24`} /></label>
              <label className="flex flex-col">Variable O&amp;M, USD/MWh<input name="vom" type="number" min={0} max={50} step="any" defaultValue={x.vom} className={`${field} w-24`} /></label>
            </>
          ) : null}
          <button type="submit" className="border border-accent px-3 py-1 text-accent">Show</button>
          <Link href="/cost-of-power/seller" className="text-xs">Reset to the defaults</Link>
        </form>
        <p className="mt-2 max-w-3xl text-xs text-muted">
          Defaults, each an assumption from Lazard&apos;s Levelized Cost of Energy+ (June 2025), the midpoint of its range: capital cost {D.capex.toLocaleString("en-US")} USD/kW
          (Lazard {D.capexRange}), fixed O&amp;M {D.fom} USD/kW-yr ({D.fomRange}), life {D.life} years; debt service = capital x {DEBT.share * 100} percent debt at{" "}
          {DEBT.rate * 100} percent, levelized over the life (Lazard&apos;s financing), so the default for {sizeLabel} is {usdShort(Math.round(D.capex * 1000 * x.mw * DEBT.share * (DEBT.rate / (1 - (1 + DEBT.rate) ** -D.life))))} USD a year.
          {x.asset === "peaker" ? ` Peaker: heat rate ${HEAT_RATE} MMBtu/MWh and variable O&M ${VOM} USD/MWh (Lazard gas peaking, new build, 10,275 to 11,175 Btu/kWh and 3.50 to 5.00 USD/MWh).` : ""}
          {x.asset === "battery" ? ` Battery: priced as a ${durationOf(x.mw, x.mwh)}-hour battery (the nearer of the two durations Lazard prices), round trip ${snap.defaults.rte * 100} percent (Lazard's low end), one full cycle a day at most, perfect foresight of each day's prices: an upper bound.` : ""}
          {" "}Default sizes: {DEFAULT_SIZE.solar.mw} MW solar, wind or peaker; {DEFAULT_SIZE.battery.mw} MW / {DEFAULT_SIZE.battery.mwh} MWh battery.
        </p>
      </Section>

      <Section title={`${ASSET_NAMES[x.asset]}, ${sizeLabel}, at ${ISO_NAMES[x.iso]} ${s.hub}: monthly revenue`} aside={<Tier />}>
        {sm.n ? (
          <>
            <p className="mb-2 max-w-3xl text-sm">
              Over <V pre={key} stat="n" v={sm.n} d={count} /> months held, {monthName(sm.first!)} to {monthName(sm.last!)}, the median month earned{" "}
              <strong><U pre={key} stat="median" v={sm.median!.revenue} /></strong> USD ({monthName(sm.median!.m)}) and the 10th-percentile month{" "}
              <strong><U pre={key} stat="p10" v={sm.p10!.revenue} /></strong> USD ({monthName(sm.p10!.m)}): one month in ten earned that or less. The year&apos;s average,
              twelve times the mean month, is <U pre={key} stat="annual_mean" v={annual} /> USD.
            </p>
            <p className="mb-2 max-w-3xl text-sm">
              The worst three months:{" "}
              {sm.worst.map((r, i) => <span key={r.m}>{i ? "; " : ""}{monthName(r.m)}, <U pre={key} stat={`worst:${i}`} v={r.revenue} /> USD</span>)}.
            </p>
            <RevenueBars ms={ms} dsMonth={dsMonth} />
            <p className="mb-2 text-xs text-muted">
              USD per month for {sizeLabel}. Cardinal: a month below one month of debt service (the dashed line, <U pre={key} stat="ds" v={x.ds} /> USD a year over twelve).
              Grey: a month with less than 90 percent of its hours (a battery: days) priced, shown but not counted.
            </p>
          </>
        ) : <p className="text-sm text-muted">No month is held for this asset at this hub.</p>}
        <details className="mt-2 text-sm">
          <summary className="cursor-pointer text-muted">Every month: revenue, energy, capture price and rate, coverage</summary>
          <div className="overflow-x-auto">
            <table className="mt-1 w-full min-w-[640px] text-left text-xs tabular-nums">
              <thead><tr className="text-muted"><th>Month</th><th className="text-right">Revenue, USD</th><th className="text-right">Energy, MWh</th><th className="text-right">Capture, USD/MWh</th><th className="text-right">Flat, USD/MWh</th><th className="text-right">Capture rate, pct</th><th className="text-right">DSCR</th><th className="text-right">Held</th></tr></thead>
              <tbody>
                {ms.map((r) => (
                  <tr key={r.m} className={`border-t border-rule ${r.held ? "" : "text-muted"}`}>
                    <td>{r.m}</td>
                    <td className="text-right"><U pre={key} stat={`month:${r.m}`} v={r.revenue} /></td>
                    <td className="text-right">{Math.round(r.energy).toLocaleString("en-US")}</td>
                    <td className="text-right">{r.capture === null ? "" : <V pre={key} stat={`capture:${r.m}`} v={r.capture} />}</td>
                    <td className="text-right">{shown(r.flat)}</td>
                    <td className="text-right">{r.rate === null ? "" : <V pre={key} stat={`rate:${r.m}`} v={r.rate} />}</td>
                    <td className="text-right">{r.dscr === null ? "" : <V pre={key} stat={`dscr:${r.m}`} v={r.dscr} />}</td>
                    <td className="text-right">{Math.round(r.share * 100)} percent</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
        <Cite tables={[T, "eia_fuel_spot_prices", "eia860m_operating_generators"]} note={`Real-time prices at ${s.hub}; ${x.asset === "solar" || x.asset === "wind" ? "the fleet's hourly output per MW installed (EIA-930 generation by fuel over EIA-860M nameplate)" : x.asset === "battery" ? "the perfect-foresight daily optimum" : "Henry Hub that day"}; snapshot ${snap.built}`} />
      </Section>

      <Section title="Debt service coverage">
        {held.length ? (
          <>
            <p className="mb-2 max-w-3xl text-sm">
              Cash flow available for debt service is the month&apos;s revenue less fixed O&amp;M ({x.fom} USD/kW-yr); coverage is that over one month of the{" "}
              <U pre={key} stat="ds" v={x.ds} /> USD annual debt service. Of the <V pre={key} stat="n" v={sm.n} d={count} /> months held,{" "}
              <strong><V pre={key} stat="under1" v={under1.length} d={count} /></strong> covered less than 1.0x and{" "}
              <strong><V pre={key} stat="under125" v={under125.length} d={count} /></strong> less than 1.25x.
              {t.length ? (
                <> Over trailing twelve months, coverage was <V pre={key} stat="ttm_last" v={t.at(-1)!.dscr} />x at {monthName(t.at(-1)!.m)}, at its lowest{" "}
                  <V pre={key} stat="ttm_min" v={Math.min(...t.map((r) => r.dscr))} />x; <V pre={key} stat="ttm_under1" v={t.filter((r) => r.dscr < 1).length} d={count} /> of {t.length} twelve-month
                  windows fell under 1.0x and <V pre={key} stat="ttm_under125" v={t.filter((r) => r.dscr < 1.25).length} d={count} /> under 1.25x.</>
              ) : <> No twelve consecutive months are held here, so there is no trailing-twelve-month figure.</>}
            </p>
            <CoverageLine t={t} />
            {under1.length ? <p className="mt-1 text-xs text-muted">Months under 1.0x: {under1.map((r) => r.m).join(", ")}.</p> : null}
          </>
        ) : null}
      </Section>

      <Section title="Stress days: Uri, Elliott and the 2023 heat">
        {st && st.length ? (
          <>
            <p className="mb-2 max-w-3xl text-sm">
              Revenue on the days of each event (event_window_daily&apos;s window, local days) against the same event&apos;s baseline days (the same days or
              weekdays of earlier years), for {sizeLabel}.
            </p>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[560px] text-left text-sm tabular-nums">
                <thead><tr className="border-b border-rule text-xs text-muted"><th className="py-1">Event</th><th className="text-right">Days</th><th className="text-right">Per day, USD</th><th className="text-right">The window, USD</th><th className="text-right">A normal week, USD</th><th className="text-right">The best day, USD</th></tr></thead>
                <tbody>
                  {st.map((e) => (
                    <tr key={e.event} className="border-b border-rule">
                      <td className="py-1">{EVENTS[e.event]}, {e.start} to {e.end}</td>
                      <td className="text-right">{e.days}</td>
                      <td className="text-right"><U pre={key} stat={`stress_mean:${e.event}`} v={e.windowMean} /></td>
                      <td className="text-right"><U pre={key} stat={`stress_total:${e.event}`} v={e.windowTotal} /></td>
                      <td className="text-right"><U pre={key} stat={`stress_week:${e.event}`} v={e.normalWeek} /></td>
                      <td className="text-right"><U pre={key} stat={`stress_best:${e.event}`} v={e.best.v} /> ({e.best.day})</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="mt-1 text-xs text-muted">A normal week: seven times the mean of the baseline days. A merchant asset&apos;s best days are the grid&apos;s worst: what it earns in a storm depends on being available in it, which this model assumes (no outage, no frozen equipment, no fuel shortage).</p>
          </>
        ) : (
          <p className="max-w-3xl text-sm text-muted">The stress days are ERCOT&apos;s: the warehouse holds {ISO_NAMES[x.iso]}&apos;s hub prices from {monthName(firstMonth(snap, x.iso))} only, after these events.</p>
        )}
      </Section>

      <Section title="How a lender should read this">
        <ul className="max-w-3xl list-disc space-y-1 pl-5 text-sm">
          <li><strong>Size on the bad months, not the average.</strong> The 10th-percentile month and the worst three are what debt must survive; the trailing-twelve-month coverage shows whether a bad stretch outlasts a year.</li>
          <li><strong>The battery is an upper bound.</strong> It knows each day&apos;s prices in advance; a real one captures a fraction of this. The peaker runs on perfect hourly information too, with no start costs.</li>
          <li><strong>Solar and wind are the fleet, not your site.</strong> Hourly output per MW is the whole balancing authority&apos;s, so a single site&apos;s curtailment, congestion and node price are not here, and new capacity listed late in EIA-860M inflates the early hours of a new fleet.</li>
          <li><strong>The hub, not your node.</strong> A plant is paid its own node&apos;s price; the gap to the hub (basis) can be large and negative exactly in the windy, sunny hours.</li>
          <li><strong>Gas is Henry Hub.</strong> A peaker in New England or New York pays a delivered gas price that spikes in winter; Henry Hub understates it there, so the peaker&apos;s margin is overstated.</li>
          <li><strong>The few months outside ERCOT.</strong> The other hubs&apos; prices start in {monthName(others.first)}: {others.count} months is a short sample of weather and gas, not a distribution.</li>
        </ul>
      </Section>
      <p className="text-xs text-muted">
        The buyer&apos;s side is <Link href="/cost-of-power">what power costs to buy</Link>. Shapes: hours above installed nameplate at {ISO_NAMES[x.iso]}: solar {s.over_nameplate.solar}, wind {s.over_nameplate.wind}; hours EIA reports negative: solar {s.negative.solar}, wind {s.negative.wind}.
      </p>
    </>
  );
}
