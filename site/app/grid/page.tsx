import type { Metadata } from "next";
import { Cite } from "@/components/Cite";
import { LineChart, type Line } from "@/components/LineChart";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { daysAgo, renderTime, series, type SeriesRow } from "@/lib/data";
import { count } from "@/lib/format";
import { DOCS } from "@/lib/markdown";
import { attempt } from "@/lib/supabase";

export const revalidate = 3600;
export const metadata: Metadata = { title: "Grid conditions" };

// EIA-930 balancing authorities: table code, label, the ISO's local time zone (for the peak's local hour)
const BAS = [
  { code: "us48", entity: "eia930:US48", label: "US Lower 48", tz: "" },
  { code: "erco", entity: "eia930:ERCO", label: "ERCOT", tz: "America/Chicago" },
  { code: "ciso", entity: "eia930:CISO", label: "CAISO", tz: "America/Los_Angeles" },
  { code: "pjm", entity: "eia930:PJM", label: "PJM", tz: "America/New_York" },
  { code: "miso", entity: "eia930:MISO", label: "MISO", tz: "Etc/GMT+5" },
  { code: "swpp", entity: "eia930:SWPP", label: "SPP", tz: "America/Chicago" },
  { code: "nyis", entity: "eia930:NYIS", label: "NYISO", tz: "America/New_York" },
  { code: "isne", entity: "eia930:ISNE", label: "ISO-NE", tz: "America/New_York" },
];

// fuel groups in the fixed order of the token file; anything else is "other"
const FUELS: { key: string; label: string; vars: string[] }[] = [
  { key: "gas", label: "Natural gas", vars: ["natural_gas"] },
  { key: "coal", label: "Coal", vars: ["coal"] },
  { key: "nuclear", label: "Nuclear", vars: ["nuclear"] },
  { key: "wind", label: "Wind", vars: ["wind", "wind_with_battery"] },
  { key: "solar", label: "Solar", vars: ["solar", "solar_with_battery"] },
  { key: "hydro", label: "Hydro", vars: ["hydro"] },
  { key: "storage", label: "Storage", vars: ["battery", "pumped_storage", "other_storage", "unknown_storage"] },
  { key: "other", label: "Other", vars: [] },
];
const fuelOf = (variable: string) => {
  const f = variable.replace(/^net_generation_/, "").replace(/_mw$/, "");
  return FUELS.find((g) => g.vars.includes(f))?.key ?? "other";
};

const H = 3_600_000;
const iso = (t: number) => new Date(t).toISOString().replace(/\.\d{3}Z$/, "Z");
const hhmm = (t: number, tz: string) =>
  new Intl.DateTimeFormat("en-US", { timeZone: tz, hour: "2-digit", minute: "2-digit", hourCycle: "h23", timeZoneName: "short" }).format(new Date(t));

/** Why a day of a table is not in it: the run history's gap or failure for it, else that no run has loaded it. */
function reason(table: string, dayStr: string): string {
  const rs = DOCS.run_status_eia930.filter((r) => r.table === table);
  const gap = rs.filter((r) => r.market.endsWith(dayStr)).at(-1);
  if (gap) return `run_status.csv, run ${gap.run_id}: ${gap.detail}`;
  const failed = rs.filter((r) => r.status === "failed").at(-1);
  if (failed && failed.run_id.slice(0, 8) >= dayStr.replace(/-/g, "")) return `run_status.csv, run ${failed.run_id}: ${failed.detail}`;
  return "run_status.csv records no gap or failure for this day: no run has loaded it yet (EIA-930 is loaded by UTC day after the day ends)";
}

type BAResult = {
  ba: (typeof BAS)[number];
  day: string | null;
  note: string | null;
  demand: SeriesRow[];
  gen: SeriesRow[];
  genDay: string | null;   // the day of the generation mix: the demand day, or the latest complete generation day
  genNote: string | null;
  error: string | null;
};

async function load(ba: (typeof BAS)[number], yesterday: string): Promise<BAResult> {
  const dt = `eia930_${ba.code}_demand`;
  const d = await attempt(() => series(dt, { since: daysAgo(10) }));
  if (!d.ok) return { ba, day: null, note: null, demand: [], gen: [], genDay: null, genNote: null, error: d.reason };
  const dem = d.data.filter((r) => r.variable === "demand_mw");
  // complete UTC days: 24 demand hours
  const hours = new Map<string, number>();
  for (const r of dem) hours.set(r.ts_utc.slice(0, 10), (hours.get(r.ts_utc.slice(0, 10)) ?? 0) + 1);
  const complete = Array.from(hours.entries()).filter(([, n]) => n === 24).map(([k]) => k).sort();
  if (!complete.length) return { ba, day: null, note: null, demand: d.data, gen: [], genDay: null, genNote: null, error: `${dt} has no complete UTC day in the last 10 days` };
  let day = yesterday, note: string | null = null;
  if (!complete.includes(yesterday)) {
    day = complete[complete.length - 1];
    note = `Yesterday (${yesterday}) is ${hours.has(yesterday) ? `incomplete in ${dt} (${hours.get(yesterday)} of 24 hours)` : `not in ${dt}`}; showing ${day}, the latest complete day. Why: ${reason(dt, yesterday)}`;
  }
  // generation: the same day if complete, else the latest complete day, said so with the reason
  const gt = `eia930_${ba.code}_generation`;
  const g = await attempt(() => series(gt, { since: daysAgo(10) }));
  if (!g.ok) return { ba, day, note, demand: d.data, gen: [], genDay: null, genNote: null, error: `generation: ${g.reason}` };
  const gh = new Map<string, number>();
  for (const r of g.data) if (r.variable === "net_generation_mw") gh.set(r.ts_utc.slice(0, 10), (gh.get(r.ts_utc.slice(0, 10)) ?? 0) + 1);
  const gComplete = Array.from(gh.entries()).filter(([, n]) => n === 24).map(([k]) => k).sort();
  let genDay: string | null = day, genNote: string | null = null;
  if (!gComplete.includes(day)) {
    genDay = gComplete.length ? gComplete[gComplete.length - 1] : null;
    genNote = `${gt} ${gh.has(day) ? `holds ${gh.get(day)} of 24 hours of ${day}` : `does not hold ${day}`}${genDay ? `; the mix shown is ${genDay}, its latest complete day` : ""}. Why: ${reason(gt, day)}`;
  }
  const gen = genDay ? g.data.filter((r) => r.ts_utc.slice(0, 10) === genDay) : [];
  return { ba, day, note, demand: d.data, gen, genDay, genNote, error: null };
}

function Block({ r }: { r: BAResult }) {
  const table = `eia930_${r.ba.code}_demand`;
  const gtable = `eia930_${r.ba.code}_generation`;
  if (!r.day) return <NoData what={`${r.ba.label} demand`} reason={r.error ?? "no data"} />;
  const d0 = Date.parse(`${r.day}T00:00:00Z`), d1 = d0 + 24 * H;
  const dayRows = r.demand.filter((x) => { const t = Date.parse(x.ts_utc); return t >= d0 && t < d1; });
  const dem = dayRows.filter((x) => x.variable === "demand_mw");
  const fc = new Map(dayRows.filter((x) => x.variable === "demand_forecast_mw").map((x) => [x.ts_utc, x.value]));
  const peak = dem.reduce((a, b) => (b.value > a.value ? b : a));
  const peakT = Date.parse(peak.ts_utc);
  const fAtPeak = fc.get(peak.ts_utc);
  const pairs = dem.filter((x) => fc.has(x.ts_utc));
  const mape = pairs.length ? (100 * pairs.reduce((a, x) => a + Math.abs(x.value - fc.get(x.ts_utc)!) / x.value, 0)) / pairs.length : null;
  // 7-day chart: the 7 UTC days ending with the day shown
  const c0 = d1 - 7 * 24 * H;
  const toLine = (v: string) => r.demand.filter((x) => x.variable === v && Date.parse(x.ts_utc) >= c0 && Date.parse(x.ts_utc) < d1).map((x) => ({ t: Date.parse(x.ts_utc) / 1000, v: x.value }));
  const lines: Line[] = [
    { label: "Demand", points: toLine("demand_mw"), color: "accent" },
    { label: "Day-ahead forecast", points: toLine("demand_forecast_mw"), color: "muted" },
  ];
  const range = `${iso(d0)}|${iso(d1)}`;
  return (
    <div className="grid gap-6 lg:grid-cols-[18rem_1fr]">
      <div>
        {r.note ? <p className="mb-2 border border-dashed border-rule bg-panel px-2 py-1 text-xs text-muted">{r.note}</p> : null}
        <div className="text-xs text-muted">Peak demand, {r.day} (UTC day)</div>
        <div className="text-2xl tabular-nums">
          <Num check={`series_max|${table}|demand_mw|${range}`} raw={peak.value}>{count(peak.value)}</Num> <span className="text-sm text-muted">MW</span>
        </div>
        <div className="mb-3 text-xs text-muted">
          hour starting {new Date(peakT).toISOString().slice(11, 16)} UTC{r.ba.tz ? ` (${hhmm(peakT, r.ba.tz)})` : ""}
        </div>
        <div className="text-xs text-muted">Day-ahead forecast for that hour</div>
        {fAtPeak !== undefined ? (
          <div className="mb-3 tabular-nums">
            <Num check={`series|${table}|${r.ba.entity}|demand_forecast_mw|${peak.ts_utc}`} raw={fAtPeak}>{count(fAtPeak)}</Num> MW; error{" "}
            {peak.value - fAtPeak >= 0 ? "+" : "−"}
            {count(Math.abs(peak.value - fAtPeak))} MW ({(((peak.value - fAtPeak) / peak.value) * 100).toFixed(1)}% of demand)
          </div>
        ) : (
          <div className="mb-3 text-xs text-muted">no data: no forecast for that hour in {table}. Why: {reason(table, r.day)}</div>
        )}
        <div className="text-xs text-muted">Forecast error over the day (mean absolute, % of demand)</div>
        <div className="tabular-nums">
          {mape !== null ? `${mape.toFixed(1)}% over ${pairs.length} hours` : `no data: no forecast hours on ${r.day}`}
        </div>
      </div>
      <div className="min-w-0">
        <LineChart lines={lines} unit="MW" height={200} ariaLabel={`${r.ba.label} hourly demand and day-ahead forecast, 7 days`} />
        <Cite tables={[table]} note={`Hourly demand and EIA's day-ahead demand forecast, the 7 UTC days to ${r.day}. Error is demand minus forecast`} />
        <FuelBar r={r} gtable={gtable} />
      </div>
    </div>
  );
}

function mix(gen: SeriesRow[]) {
  const total = gen.filter((x) => x.variable === "net_generation_mw").reduce((a, x) => a + x.value, 0);
  const hoursTotal = gen.filter((x) => x.variable === "net_generation_mw").length;
  const by = new Map<string, number>();
  for (const x of gen) {
    if (x.variable === "net_generation_mw") continue;
    by.set(fuelOf(x.variable), (by.get(fuelOf(x.variable)) ?? 0) + x.value);
  }
  return { total, hoursTotal, by };
}

function FuelBar({ r, gtable }: { r: BAResult; gtable: string }) {
  if (r.error && !r.gen.length) return <NoData what="generation mix" reason={r.error} />;
  const { total, hoursTotal, by } = mix(r.gen);
  if (!r.genDay || hoursTotal !== 24) return <NoData what={`generation mix, ${r.day}`} reason={r.genNote ?? `${gtable} has no complete day in the last 10 days`} />;
  const pos = FUELS.map((f) => ({ ...f, mwh: by.get(f.key) ?? 0 }));
  const drawn = pos.reduce((a, f) => a + Math.max(0, f.mwh), 0);
  const W = 600, GAP = 2;
  // segment offsets computed first: each fuel's share of the drawn (positive) total
  const segs = pos
    .filter((f) => f.mwh > 0 && drawn > 0)
    .map((f) => ({ ...f, w: (f.mwh / drawn) * W }))
    .map((f, i, arr) => ({ ...f, x: arr.slice(0, i).reduce((a, g) => a + g.w, 0) }));
  return (
    <div className="mt-4">
      <div className="mb-1 text-xs text-muted">
        {r.genNote ? <span className="mb-1 block border border-dashed border-rule px-2 py-1">{r.genNote}</span> : null}Generation mix, {r.genDay}: <Num check={`series_sum|${gtable}|net_generation_mw|${r.genDay}T00:00:00Z|${iso(Date.parse(`${r.genDay}T00:00:00Z`) + 24 * H)}`} raw={total}>{count(total)}</Num> MWh net
      </div>
      <svg viewBox={`0 0 ${W} 22`} className="block h-6 w-full" preserveAspectRatio="none" role="img" aria-label={`${r.ba.label} generation by fuel, ${r.genDay}`}>
        {segs.map((f) => (
          <rect key={f.key} x={f.x} y={0} width={Math.max(0, f.w - GAP)} height={22} rx={2} fill={`var(--color-fuel-${f.key})`}>
            <title>{`${f.label}: ${count(f.mwh)} MWh, ${((f.mwh / total) * 100).toFixed(1)}% of net generation`}</title>
          </rect>
        ))}
      </svg>
      <Cite tables={[gtable]} note="Sum of the day's 24 hourly values by fuel, in MWh; storage charging (negative net generation) is not drawn but is in the table below" />
    </div>
  );
}

export default async function GridPage() {
  const now = renderTime();
  const yesterday = new Date(now - 24 * H).toISOString().slice(0, 10);
  const results = await Promise.all(BAS.map((b) => load(b, yesterday)));
  return (
    <>
      <h1 className="mb-1 text-3xl">Grid conditions</h1>
      <p className="mb-5 max-w-3xl text-sm text-muted">
        Yesterday on the grid, from EIA&apos;s Hourly Electric Grid Monitor (Form EIA-930): each ISO&apos;s peak demand and when it came, how far EIA&apos;s
        day-ahead demand forecast missed, the generation mix, and the last seven days of demand. Days are UTC days, as EIA publishes them; the peak
        hour is also given in the ISO&apos;s local time.
      </p>
      <div className="mb-8 flex flex-wrap gap-3 text-xs" aria-label="Fuel colors">
        {FUELS.map((f) => (
          <span key={f.key} className="flex items-center gap-1">
            <span className="inline-block h-3 w-3 rounded-sm" style={{ background: `var(--color-fuel-${f.key})` }} />
            {f.label}
          </span>
        ))}
      </div>
      {results.map((r) => (
        <Section key={r.ba.code} title={r.ba.label} id={r.ba.code}>
          <Block r={r} />
        </Section>
      ))}
      <Section title="Generation mix, as a table" id="mix-table">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-b border-rule text-left text-xs text-muted">
                <th className="py-1 pr-3 font-normal">Region</th>
                <th className="py-1 pr-3 font-normal">Day</th>
                {FUELS.map((f) => (
                  <th key={f.key} className="py-1 pr-3 text-right font-normal">{f.label}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {results.map((r) => {
                const { total, hoursTotal, by } = mix(r.gen);
                return (
                  <tr key={r.ba.code} className="border-b border-rule/60">
                    <td className="py-1 pr-3">{r.ba.label}</td>
                    <td className="py-1 pr-3 text-xs">{r.genDay ?? ""}</td>
                    {hoursTotal === 24
                      ? FUELS.map((f) => (
                          <td key={f.key} className="py-1 pr-3 text-right tabular-nums">
                            {by.has(f.key) ? `${((by.get(f.key)! / total) * 100).toFixed(1)}%` : ""}
                          </td>
                        ))
                      : <td colSpan={FUELS.length} className="py-1 pr-3 text-xs text-muted">no data for this day</td>}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <p className="mt-1 text-xs text-muted">
          Share of the day&apos;s net generation (MWh) by fuel. Storage can be negative when it charged more than it discharged. Blank: the region
          reports no such fuel.
        </p>
        <Cite tables={BAS.map((b) => `eia930_${b.code}_generation`)} />
      </Section>
    </>
  );
}
