import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Cite } from "@/components/Cite";
import { InlineSpark } from "@/components/InlineSpark";
import { LineChart, type Line } from "@/components/LineChart";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { ShareBar } from "@/components/ShareBar";
import { StackedArea } from "@/components/StackedArea";
import type { SeriesRow, StorageUnit } from "@/lib/data";
import { count, shown } from "@/lib/format";
import { FUELS, GRIDS, fuelName, fuelOf, gridOf, load, type GridData } from "@/lib/grid";
import { DOCS, render, type GridConfig } from "@/lib/markdown";
import { TIER_LABEL, TIER_TITLE } from "@/lib/tiers";

// Session 35: "Ask your grid". One template, seven pages (docs/grids/grids.json), for a student in a first energy
// course: who runs the grid, where the power comes from now, what it costs, how clean it is, what is being built,
// what is different. Each block renders only when the warehouse holds this grid's rows; otherwise it says so in one
// line and names where EIA (or the ISO) publishes it. Every number is a row of a live-set table or a sum of rows,
// each with a check key that site/scripts/check-values.mjs recomputes. The written layer is docs/grids/<slug>.md.
export const revalidate = 3600;
export const dynamicParams = false;
export function generateStaticParams() {
  return GRIDS.map((g) => ({ iso: g.slug }));
}
export async function generateMetadata({ params }: { params: Promise<{ iso: string }> }): Promise<Metadata> {
  const g = gridOf((await params).iso);
  return { title: g ? `${g.iso}: your grid` : "Your grid" };
}

const H = 3_600_000;
const EIA = (g: GridConfig) => `https://www.eia.gov/electricity/gridmonitor/dashboard/electric_overview/balancing_authority/${g.entity.split(":")[1]}`;
const isoTs = (t: number) => new Date(t).toISOString().replace(/\.\d{3}Z$/, "Z");
const local = (ts: string, tz: string, withDay = true) =>
  new Intl.DateTimeFormat("en-US", { timeZone: tz, ...(withDay ? { month: "short", day: "numeric" } : {}), hour: "numeric", minute: "2-digit", timeZoneName: "short" }).format(new Date(ts));
const localDay = (t: number, tz: string) => new Intl.DateTimeFormat("en-CA", { timeZone: tz, year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date(t));

function Chip({ tier }: { tier: "source" | "derived" | "model_extracted" | "written" }) {
  const label = tier === "written" ? "written, cited" : TIER_LABEL[tier];
  const title = tier === "written" ? "Text written for this site, with its sources named; not data" : TIER_TITLE[tier];
  return (
    <Link href="/data/standard" title={title} className="ml-1 rounded border border-rule px-1 text-[10px] uppercase tracking-wide text-muted no-underline">
      {label}
    </Link>
  );
}

/** The one line a block shows when the warehouse does not hold this grid's data. */
function NotYet({ what, where, href }: { what: string; where: string; href: string }) {
  return (
    <p className="border border-dashed border-rule bg-panel px-3 py-2 text-sm text-muted" role="status">
      <span className="font-semibold text-ink">Not in the warehouse yet:</span> {what}. {where}: <a href={href}>{href}</a>.
    </p>
  );
}

const key = (t: string, r: SeriesRow) => `series|${t}|${r.entity}|${r.variable}|${r.ts_utc}`;
const N = ({ t, r }: { t: string; r?: SeriesRow }) => (r ? <Num check={key(t, r)} raw={r.value}>{shown(r.value)}</Num> : <span className="text-muted">none</span>);
const latestOf = (rows: SeriesRow[], v: string) => rows.filter((r) => r.variable === v).sort((a, b) => a.ts_utc.localeCompare(b.ts_utc)).at(-1);

// ------------------------------------------------------------------ 1. right now

function RightNow({ g, d }: { g: GridConfig; d: GridData }) {
  const T = "eia930_all_demand";
  const rows = d.demand.filter((r) => r.variable === "demand_mw").sort((a, b) => a.ts_utc.localeCompare(b.ts_utc));
  const last = rows.at(-1);
  if (!last) return <NotYet what={`${g.iso}'s hourly demand`} where="EIA publishes it in its Hourly Electric Grid Monitor" href={EIA(g)} />;
  const lt = Date.parse(last.ts_utc);
  const today = localDay(lt, g.tz);
  const so = rows.filter((r) => localDay(Date.parse(r.ts_utc), g.tz) === today);
  const weekAgo = rows.filter((r) => localDay(Date.parse(r.ts_utc) + 7 * 24 * H, g.tz) === today);
  const sameHour = rows.find((r) => Date.parse(r.ts_utc) === lt - 7 * 24 * H);
  const start = so[0].ts_utc, end = isoTs(lt + H);
  const peak = so.reduce((a, b) => (b.value > a.value ? b : a));
  const lines: Line[] = [
    { label: `${today} so far`, color: "accent", points: so.map((r) => ({ t: Date.parse(r.ts_utc) / 1000, v: r.value })) },
    { label: "Same day last week", color: "muted", points: weekAgo.map((r) => ({ t: (Date.parse(r.ts_utc) + 7 * 24 * H) / 1000, v: r.value })) },
  ];
  return (
    <>
      <div className="grid gap-6 lg:grid-cols-[18rem_1fr]">
        <div className="text-sm">
          <div className="text-xs text-muted">Demand in the latest hour EIA has published ({local(last.ts_utc, g.tz)})</div>
          <div className="mb-2 text-3xl tabular-nums"><N t={T} r={last} /> <span className="text-sm text-muted">MW</span></div>
          <div className="text-xs text-muted">The same hour a week earlier</div>
          <div className="mb-2 tabular-nums">{sameHour ? <><N t={T} r={sameHour} /> MW</> : <span className="text-muted">not held</span>}</div>
          <div className="text-xs text-muted">Highest hour so far on {today} ({g.tz_label})</div>
          <div className="tabular-nums">
            <Num check={`series_max|${T}|demand_mw|${start}|${end}|${g.entity}`} raw={peak.value}>{shown(peak.value)}</Num> MW at {local(peak.ts_utc, g.tz, false)}
          </div>
        </div>
        <div className="min-w-0">
          <LineChart lines={lines} unit="MW" height={220} ariaLabel={`${g.iso} hourly demand today so far and the same day last week`} />
        </div>
      </div>
      <p className="mt-1 text-[11px] text-muted">
        Demand is how much power customers use each hour. EIA publishes each grid&apos;s hourly demand an hour or so after the hour, so &quot;right now&quot;
        is the latest hour it has published. Last week&apos;s line is moved forward seven days so the two days line up.
      </p>
      <Cite tables={[T]} note="EIA-930 hourly demand, MW; hour starts" />
    </>
  );
}

// ------------------------------------------------------------------ 2. where the power comes from

function Power({ g, d }: { g: GridConfig; d: GridData }) {
  const T = "eia930_all_generation";
  const fuelRows = d.gen.filter((r) => r.variable !== "net_generation_mw" && r.variable.startsWith("net_generation_"));
  const totals = d.gen.filter((r) => r.variable === "net_generation_mw");
  if (!fuelRows.length || !totals.length) return <NotYet what={`${g.iso}'s generation by fuel`} where="EIA publishes it in its Hourly Electric Grid Monitor" href={EIA(g)} />;
  const lastT = Math.max(...totals.map((r) => Date.parse(r.ts_utc)));
  const from24 = lastT - 23 * H;
  const x: number[] = [];
  for (let t = from24; t <= lastT; t += H) x.push(t);
  const byT = new Map<string, number>();
  for (const r of fuelRows) byT.set(`${fuelOf(r.variable)}|${Date.parse(r.ts_utc)}`, (byT.get(`${fuelOf(r.variable)}|${Date.parse(r.ts_utc)}`) ?? 0) + r.value);
  const present = FUELS.filter((f) => fuelRows.some((r) => fuelOf(r.variable) === f.key && Date.parse(r.ts_utc) >= from24));
  const layers = present.map((f) => ({ key: f.key, label: f.label, color: `var(--color-fuel-${f.key})`, values: x.map((t) => byT.get(`${f.key}|${t}`) ?? null) }));
  // the last 30 complete UTC days (24 hours of net generation each) to the latest complete one
  const hours = new Map<string, number>();
  for (const r of totals) hours.set(r.ts_utc.slice(0, 10), (hours.get(r.ts_utc.slice(0, 10)) ?? 0) + 1);
  const complete = Array.from(hours.entries()).filter(([, n]) => n === 24).map(([k]) => k).sort();
  const endDay = complete.at(-1);
  const end = endDay ? Date.parse(`${endDay}T00:00:00Z`) + 24 * H : lastT + H;
  const start = end - 30 * 24 * H;
  const inWin = (r: SeriesRow) => Date.parse(r.ts_utc) >= start && Date.parse(r.ts_utc) < end;
  const vars = Array.from(new Set(fuelRows.map((r) => r.variable))).sort();
  const sums = vars.map((v) => ({ v, mwh: fuelRows.filter((r) => r.variable === v && inWin(r)).reduce((a, r) => a + r.value, 0), n: fuelRows.filter((r) => r.variable === v && inWin(r)).length }))
    .filter((s) => s.n > 0).sort((a, b) => b.mwh - a.mwh);
  const total = totals.filter(inWin).reduce((a, r) => a + r.value, 0);
  const s0 = isoTs(start), s1 = isoTs(end);
  return (
    <>
      <div className="mb-1 text-xs text-muted">The last 24 hours EIA has published, by fuel, MW (hour starts, to {local(isoTs(lastT), g.tz)})</div>
      <StackedArea x={x} layers={layers} unit="MW" ariaLabel={`${g.iso} generation by fuel, the last 24 hours`} height={220} />
      <div className="mt-4 text-xs text-muted">
        The mix over 30 UTC days, {s0.slice(0, 10)} to {isoTs(end - 24 * H).slice(0, 10)}: <Num check={`series_sum|${T}|net_generation_mw|${s0}|${s1}|${g.entity}`} raw={total}>{shown(total)}</Num> MWh net
      </div>
      <ShareBar parts={FUELS.map((f) => ({ name: f.label, value: sums.filter((s) => fuelOf(s.v) === f.key).reduce((a, s) => a + s.mwh, 0), color: `var(--color-fuel-${f.key})` }))}
        unit="MWh" ariaLabel={`${g.iso} generation by fuel, 30 days`} file={`erw-${g.slug}-mix-30d`} />
      <div className="mt-2 overflow-x-auto">
        <table className="w-full min-w-[360px] text-sm tabular-nums">
          <thead><tr className="border-b border-rule text-left text-[11px] text-muted"><th className="py-0.5 font-normal">Fuel (as EIA names it)</th><th className="pr-2 text-right font-normal">MWh, 30 days</th><th className="pr-2 text-right font-normal">Hours held</th></tr></thead>
          <tbody>
            {sums.map((s) => (
              <tr key={s.v} className="border-b border-rule">
                <td className="py-0.5 pr-2">{fuelName(s.v)}</td>
                <td className="pr-2 text-right"><Num check={`series_sum|${T}|${s.v}|${s0}|${s1}|${g.entity}`} raw={s.mwh}>{shown(s.mwh)}</Num></td>
                <td className="pr-2 text-right text-muted">{count(s.n)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-1 text-[11px] text-muted">
        Net generation: what the plants produce minus what they use themselves. Storage can be negative: batteries take power in when they charge.
        A fuel with fewer hours than the others is one EIA did not report for every hour.
      </p>
      <Cite tables={[T]} note="EIA-930 hourly net generation by fuel, MW; a day's hourly MW add up to its MWh" />
    </>
  );
}

// ------------------------------------------------------------------ 3. batteries

function Batteries({ g, d }: { g: GridConfig; d: GridData }) {
  const T = "storage_daily_cycle";
  const dis = d.cycle.filter((r) => r.variable === "mwh_discharged").sort((a, b) => a.ts_utc.localeCompare(b.ts_utc));
  const last = dis.at(-1);
  const at = (v: string) => (last ? d.cycle.find((r) => r.variable === v && r.ts_utc === last.ts_utc) : undefined);
  const by = (s: string[]) => d.units.filter((u) => s.includes(u.status ?? ""));
  const mw = (us: StorageUnit[]) => Math.round(us.reduce((a, u) => a + (u.capacity_mw ?? 0), 0) * 10) / 10;
  const mwh = (us: StorageUnit[]) => Math.round(us.filter((u) => u.mwh).reduce((a, u) => a + Number(u.mwh), 0) * 10) / 10;
  const op = by(["operating"]);
  return (
    <>
      {last ? (
        <div className="mb-3 text-sm">
          <div className="text-xs text-muted">
            The latest complete day, {last.ts_utc.slice(0, 10)}{g.storage_source === "caiso" ? <>: CAISO&apos;s own data<Chip tier="derived" /></> : null}
          </div>
          <div className="flex flex-wrap gap-x-6 tabular-nums">
            <span>Discharged <N t={T} r={last} /> MWh</span>
            <span>Charged <N t={T} r={at("mwh_charged")} /> MWh</span>
            {at("peak_discharge_hour") ? <span>Most discharge at <Num check={key(T, at("peak_discharge_hour")!)} raw={at("peak_discharge_hour")!.value}>{String(at("peak_discharge_hour")!.value)}</Num>:00 local</span> : null}
          </div>
          <div className="mt-1 max-w-sm">
            <InlineSpark values={dis.slice(-30).map((r) => ({ t: r.ts_utc, v: r.value }))} label={`${g.iso} battery MWh discharged per day, last 30 days`} />
          </div>
          <Cite tables={[T]} note={g.storage_source === "caiso" ? "CAISO's rows from its own 5-minute Total batteries series (caiso_battery_storage), averaged to hours, complete Pacific days" : "From EIA-930's hourly battery net generation, complete local days"} />
        </div>
      ) : (
        <NotYet what={`a daily battery cycle for ${g.iso}: EIA-930 has no battery series for this grid`} where="EIA publishes each grid's hourly generation by fuel" href={EIA(g)} />
      )}
      {d.units.length ? (
        <div className="text-sm tabular-nums">
          <div className="text-xs text-muted">Battery units in {g.iso}&apos;s footprint (EIA-860M, the unit&apos;s balancing authority)</div>
          <div className="flex flex-wrap gap-x-6">
            <span>Operating: <Num check={`storage|iso_mw|${g.iso}|operating`} raw={mw(op)}>{shown(mw(op))}</Num> MW, <Num check={`storage|iso_mwh|${g.iso}|operating`} raw={mwh(op)}>{shown(mwh(op))}</Num> MWh</span>
            <span>Under construction: <Num check={`storage|iso_mw|${g.iso}|under_construction`} raw={mw(by(["under_construction"]))}>{shown(mw(by(["under_construction"])))}</Num> MW</span>
            <span>Planned: <Num check={`storage|iso_mw|${g.iso}|planned`} raw={mw(by(["planned"]))}>{shown(mw(by(["planned"])))}</Num> MW</span>
          </div>
          <p className="mt-1 text-[11px] text-muted">MW is how fast a battery can deliver power; MWh is how much energy it holds. EIA-860M gives MWh for operating units, not planned ones.</p>
          <Cite tables={["storage_capacity"]} note="Sums of the battery units whose balancing authority is this grid" />
        </div>
      ) : (
        <NotYet what={`battery units mapped to ${g.iso}`} where="EIA publishes the generator inventory, EIA-860M" href="https://www.eia.gov/electricity/data/eia860m/" />
      )}
      <p className="mt-1 text-[11px] text-muted"><Link href="/data/methods/storage">Method</Link>.</p>
    </>
  );
}

// ------------------------------------------------------------------ 4. how clean

function Clean({ g, d }: { g: GridConfig; d: GridData }) {
  const T = "carbon_intensity_hourly", TM = "carbon_intensity_monthly";
  const gen = d.ci.filter((r) => r.variable === "intensity_generation").sort((a, b) => a.ts_utc.localeCompare(b.ts_utc));
  const last = gen.at(-1);
  if (!last) return <NotYet what={`${g.iso}'s carbon intensity`} where="EIA publishes hourly CO2 estimates per grid in its Grid Monitor workbooks" href={EIA(g)} />;
  const dem = d.ci.find((r) => r.variable === "intensity_demand" && r.ts_utc === last.ts_utc);
  const lt = Date.parse(last.ts_utc);
  const m = d.monthly.sort((a, b) => a.ts_utc.localeCompare(b.ts_utc));
  return (
    <>
      <div className="grid gap-6 lg:grid-cols-[18rem_1fr]">
        <div className="text-sm">
          <div className="text-xs text-muted">The latest hour EIA has estimated ({local(last.ts_utc, g.tz)})</div>
          <div className="text-3xl tabular-nums"><N t={T} r={last} /></div>
          <div className="mb-2 text-xs text-muted">kg of CO2 per MWh generated here</div>
          <div className="tabular-nums"><N t={T} r={dem} /> <span className="text-xs text-muted">kg CO2 per MWh used here (imports counted)</span></div>
        </div>
        <div className="min-w-0">
          <LineChart lines={[{ label: "Of generation", color: "accent", points: gen.filter((r) => Date.parse(r.ts_utc) > lt - 24 * H).map((r) => ({ t: Date.parse(r.ts_utc) / 1000, v: r.value })) }]}
            unit="kg CO2/MWh" height={180} ariaLabel={`${g.iso} carbon intensity, the last 24 hours`} />
        </div>
      </div>
      <Cite tables={[T]} note="EIA's hourly CO2 estimates over EIA's net generation and demand, the latest 24 hours" />
      {m.length ? (
        <div className="mt-3">
          <div className="text-xs text-muted">
            Monthly since 2018: <Num check={key(TM, m[0])} raw={m[0].value}>{shown(m[0].value)}</Num> in {m[0].ts_utc.slice(0, 7)},{" "}
            <Num check={key(TM, m.at(-1)!)} raw={m.at(-1)!.value}>{shown(m.at(-1)!.value)}</Num> in {m.at(-1)!.ts_utc.slice(0, 7)} (kg CO2 per MWh generated; months with a missing day are left out)
          </div>
          <LineChart lines={[{ label: "Of generation, monthly", color: "ink", points: m.map((r) => ({ t: Date.parse(r.ts_utc) / 1000, v: r.value })) }]} x="month" unit="kg CO2/MWh" height={180} ariaLabel={`${g.iso} carbon intensity by month since 2018`} />
          <Cite tables={[TM]} />
        </div>
      ) : null}
      <p className="mt-1 text-[11px] text-muted">Carbon intensity is the CO2 released per MWh of electricity: lower is cleaner. <Link href="/data/methods/emissions">Method</Link>.</p>
    </>
  );
}

// ------------------------------------------------------------------ 5. what it costs

function Cost({ g, d }: { g: GridConfig; d: GridData }) {
  const T = "price_board_latest", TP = "price_board_peak_offpeak";
  if (!g.prices_public) return <NotYet what={`${g.iso}'s prices: ${(g.prices_note ?? "not public here").replace(/[.]$/, "")}`} where={`${g.iso} publishes them`} href={g.prices_url ?? "https://www.eia.gov/electricity/wholesale/"} />;
  if (!g.hub || !d.prices.length) return <NotYet what={`${g.iso}'s hub prices`} where="EIA summarizes wholesale prices" href="https://www.eia.gov/electricity/wholesale/" />;
  const daMean = latestOf(d.prices, "da_latest_day_mean"), rtMean = latestOf(d.prices, "rt_latest_day_mean"), avg30 = latestOf(d.prices, "da_avg_30d");
  const daily = d.prices.filter((r) => r.variable === "da_daily_mean").sort((a, b) => a.ts_utc.localeCompare(b.ts_utc));
  const pk = latestOf(d.peak, "da_peak_mean");
  const off = pk ? d.peak.find((r) => r.variable === "da_offpeak_mean" && r.ts_utc === pk.ts_utc) : undefined;
  return (
    <>
      <div className="text-xs text-muted">{g.hub.label}, USD per MWh</div>
      <div className="mt-1 grid grid-cols-2 gap-px border border-rule bg-rule text-sm tabular-nums sm:grid-cols-4">
        <div className="bg-panel p-2"><div className="text-[11px] text-muted">Day-ahead, {daMean?.ts_utc.slice(0, 10)}</div><div className="text-xl"><N t={T} r={daMean} /></div></div>
        <div className="bg-panel p-2"><div className="text-[11px] text-muted">Real-time, {rtMean?.ts_utc.slice(0, 10)}</div><div className="text-xl"><N t={T} r={rtMean} /></div></div>
        <div className="bg-panel p-2"><div className="text-[11px] text-muted">Day-ahead peak, {pk?.ts_utc.slice(0, 10)}</div><div className="text-xl"><N t={TP} r={pk} /></div></div>
        <div className="bg-panel p-2"><div className="text-[11px] text-muted">Day-ahead off-peak, same day</div><div className="text-xl"><N t={TP} r={off} /></div></div>
      </div>
      <div className="mt-2 flex flex-wrap items-center gap-3 text-sm">
        <span className="text-xs text-muted">Day-ahead daily mean, 30 days (average <N t={T} r={avg30} />)</span>
        <span className="w-48"><InlineSpark values={daily.map((r) => ({ t: r.ts_utc, v: r.value }))} label={`${g.iso} day-ahead daily mean price, 30 days`} /></span>
      </div>
      <p className="mt-1 text-[11px] text-muted">
        Wholesale prices, what power plants are paid, not what a household pays. Day-ahead is the price agreed the day before; real-time is the price at
        the moment. Peak hours are the busy daytime hours of working days, as the price board&apos;s method defines them; off-peak is the rest. <Link href="/data/methods/price_board">Method</Link>.
      </p>
      <Cite tables={[T, TP]} note="Daily means of the ISO's own hourly prices" />
    </>
  );
}

// ------------------------------------------------------------------ 6. what is being built

function Building({ g, d }: { g: GridConfig; d: GridData }) {
  const states = Object.keys(g.states).sort();
  const dcMw = Math.round(d.dcs.reduce((a, x) => a + (x.capacity_mw ?? 0), 0) * 10) / 10;
  const dcN = d.dcs.length;
  let queue: React.ReactNode;
  if (!g.queue_table) {
    queue = <NotYet what={`${g.iso}'s interconnection queue`} where={`${g.iso} publishes it`} href={g.queue_url ?? "https://www.eia.gov/electricity/data/eia860m/"} />;
  } else if (!d.queue.length) {
    queue = <NotYet what={`${g.iso}'s interconnection queue in the live set`} where={`${g.iso} publishes it`} href="https://www.eia.gov/electricity/data/eia860m/" />;
  } else {
    const techs = Array.from(new Set(d.queue.map((q) => q.tech ?? "unknown")));
    const rows = techs.map((t) => {
      const a = d.queue.filter((q) => (q.tech ?? "unknown") === t && q.status === "active");
      return { t, n: a.length, mw: Math.round(a.reduce((s, q) => s + (q.capacity_mw ?? 0), 0) * 10) / 10, done: d.queue.filter((q) => (q.tech ?? "unknown") === t && q.status === "completed").length };
    }).filter((r) => r.n || r.done).sort((a, b) => b.mw - a.mw);
    const k = (s: string, t: string, what: string) => `gridq|${g.queue_table}|${s}|${t}|${what}`;
    queue = (
      <>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[420px] text-sm tabular-nums">
            <thead><tr className="border-b border-rule text-left text-[11px] text-muted"><th className="py-0.5 font-normal">Kind of project</th><th className="pr-2 text-right font-normal">Waiting (active)</th><th className="pr-2 text-right font-normal">Active MW</th><th className="pr-2 text-right font-normal">Completed</th></tr></thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.t} className="border-b border-rule">
                  <td className="py-0.5 pr-2">{r.t.replace(/_/g, " ")}</td>
                  <td className="pr-2 text-right"><Num check={k("active", r.t, "n")} raw={r.n}>{count(r.n)}</Num></td>
                  <td className="pr-2 text-right"><Num check={k("active", r.t, "mw")} raw={r.mw}>{shown(r.mw)}</Num></td>
                  <td className="pr-2 text-right"><Num check={k("completed", r.t, "n")} raw={r.done}>{count(r.done)}</Num></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-1 text-[11px] text-muted">
          The interconnection queue is the waiting list of projects asking to connect to the grid; many never get built. Withdrawn projects are left out.
          Kinds are the ERW&apos;s grouping of the ISO&apos;s own fuel names. <Link href="/data/methods/energy_projects">Method</Link>.
        </p>
        <Cite tables={["energy_projects", g.queue_table]} note={`Queue positions of ${g.queue_table}, as energy_projects groups them`} />
      </>
    );
  }
  return (
    <>
      {queue}
      <div className="mt-4 text-sm">
        <div className="text-xs text-muted">Datacenter facilities mapped to {g.iso}<Chip tier="model_extracted" /></div>
        <div className="tabular-nums">
          <Num check={`griddc|${g.slug}|n`} raw={dcN}>{count(dcN)}</Num> facilities; <Num check={`griddc|${g.slug}|mw`} raw={dcMw}>{shown(dcMw)}</Num> MW where a source states it.{" "}
          <Link href="/datacenters">All datacenters</Link>.
        </div>
        <p className="mt-1 text-[11px] text-muted">
          A facility from {g.iso}&apos;s interconnection queue, or whose utility is one of {g.iso}&apos;s, is counted here; any other is counted by its
          state, for the states wholly or mostly inside {g.iso} ({states.map((s) => g.states[s]).join(", ")}), so one there may be served by a
          neighboring grid. Many rows come from news stories read by a model: check each against its source.{" "}
          <Link href="/data/methods/datacenter_facilities">Method</Link>.
        </p>
        <Cite tables={["datacenter_facilities"]} />
      </div>
    </>
  );
}

// ------------------------------------------------------------------ 7. in the news

function News({ g, d }: { g: GridConfig; d: GridData }) {
  const n = d.news.length;
  return (
    <>
      <div className="mb-2 text-sm">
        <Num check={`gridnews|${g.slug}|${d.newsSince}|n`} raw={n}>{count(n)}</Num> scored stories since {d.newsSince.slice(0, 10)} whose headline names{" "}
        {g.names.join(" or ")}{Object.keys(g.states).length ? ` or whose region is ${Object.values(g.states).join(", ")}` : ""}.
      </div>
      {n ? (
        <ul className="space-y-1 text-sm">
          {d.news.slice(0, 12).map((r) => (
            <li key={r.event_id}>
              <a href={r.source_url}>{r.extra?.headline || "(no headline)"}</a>{" "}
              <span className="text-[11px] text-muted">{r.source}, {r.event_date.slice(0, 10)}; significance {r.extra?.significance ?? ""}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-muted">No story in the last 14 days matched. <Link href="/digest">The Energy Digest</Link> has every day&apos;s news.</p>
      )}
      <p className="mt-1 text-[11px] text-muted">Headlines and scores are written by a model reading each story; the link goes to the outlet.</p>
      <Cite tables={["news_index"]} />
    </>
  );
}

// ------------------------------------------------------------------ the page

function Written({ md, slug }: { md: string; slug: string }) {
  return <div className="prose-erw max-w-3xl text-sm" dangerouslySetInnerHTML={{ __html: render(md, `docs/grids/${slug}.md`) }} />;
}

export default async function GridPage({ params }: { params: Promise<{ iso: string }> }) {
  const g = gridOf((await params).iso);
  if (!g) notFound();
  const d = await load(g);
  const md = DOCS.grids[g.slug] ?? "";
  const parts = md.split(/\n(?=## )/).slice(1); // the five sections
  const first = parts[0] ?? "", rest = parts.slice(1).join("\n");
  return (
    <>
      <p className="mb-1 text-xs text-muted"><Link href="/grid">Grid</Link> / Your grid</p>
      <h1 className="mb-1 text-3xl">{g.iso}: {g.name}</h1>
      <p className="mb-4 max-w-3xl text-sm text-muted">
        Who runs this grid, where its power comes from, what it costs, how clean it is, what is being built and what makes it different. Numbers come
        from the warehouse&apos;s tables, each with its source; the text is written for this page and cites its sources. Times are {g.tz_label} unless marked UTC.
      </p>
      <nav aria-label="Other grids" className="mb-5 flex flex-wrap gap-x-3 text-sm">
        {GRIDS.map((x) => (x.slug === g.slug ? <span key={x.slug} className="text-accent">{x.iso}</span> : <Link key={x.slug} href={`/grid/${x.slug}`}>{x.iso}</Link>))}
      </nav>

      <Section title="Who runs this grid" aside={<Chip tier="written" />}>
        <Written md={first.replace(/^## [^\n]*\n/, "")} slug={g.slug} />
      </Section>

      <form action="/ask" method="get" className="mb-8 flex max-w-3xl flex-col gap-2 border border-rule p-3 sm:flex-row sm:items-center">
        <label htmlFor="ask-grid" className="text-sm font-semibold">Ask {g.iso}</label>
        <input type="hidden" name="grid" value={g.slug} />
        <input id="ask-grid" name="q" maxLength={500} placeholder={`For example: what was ${g.iso}'s highest demand this week?`} className="flex-1 border border-rule bg-panel px-3 py-1.5 text-sm" />
        <button type="submit" className="border border-accent px-3 py-1.5 text-sm text-accent">Ask</button>
      </form>

      <Section title="Right now: demand" aside={<Chip tier="source" />}><RightNow g={g} d={d} /></Section>
      <Section title="Where the power comes from" aside={<Chip tier="source" />}><Power g={g} d={d} /></Section>
      <Section title="Batteries" aside={<><Chip tier="derived" /></>}><Batteries g={g} d={d} /></Section>
      <Section title="How clean" aside={<Chip tier="derived" />}><Clean g={g} d={d} /></Section>
      <Section title="What it costs" aside={<Chip tier="derived" />}><Cost g={g} d={d} /></Section>
      <Section title="What is being built" aside={<Chip tier="derived" />}><Building g={g} d={d} /></Section>
      <Section title="In the news" aside={<Chip tier="model_extracted" />}><News g={g} d={d} /></Section>

      <Section title={`About ${g.iso}`} aside={<Chip tier="written" />}>
        <Written md={rest} slug={g.slug} />
      </Section>
      {Object.keys(d.errors).length ? (
        <p className="text-[11px] text-muted">Reads that failed: {Object.entries(d.errors).map(([k, v]) => `${k}: ${v}`).join("; ")}</p>
      ) : null}
    </>
  );
}
