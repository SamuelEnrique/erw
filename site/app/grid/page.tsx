import type { Metadata } from "next";
import Link from "next/link";
import { YOUR_GRID } from "@/lib/pages";
import { Related } from "@/components/Related";
import { Term } from "@/components/Term";
import { Cite } from "@/components/Cite";
import { ShareBar } from "@/components/ShareBar";
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

// EIA-930 balancing authorities: table code, label, the ISO's local time zone (for the peak's local hour);
// session 24: station, the NWS airport at the ISO's load center (warehouse/connectors/weather_nws.py)
const BAS = [
  { code: "us48", entity: "eia930:US48", label: "US Lower 48", tz: "", station: "" },
  { code: "erco", entity: "eia930:ERCO", label: "ERCOT", tz: "America/Chicago", station: "KDFW" },
  { code: "ciso", entity: "eia930:CISO", label: "CAISO", tz: "America/Los_Angeles", station: "KLAX" },
  { code: "pjm", entity: "eia930:PJM", label: "PJM", tz: "America/New_York", station: "KPHL" },
  { code: "miso", entity: "eia930:MISO", label: "MISO", tz: "Etc/GMT+5", station: "KIND" },
  { code: "swpp", entity: "eia930:SWPP", label: "SPP", tz: "America/Chicago", station: "KOKC" },
  { code: "nyis", entity: "eia930:NYIS", label: "NYISO", tz: "America/New_York", station: "KLGA" },
  { code: "isne", entity: "eia930:ISNE", label: "ISO-NE", tz: "America/New_York", station: "KBOS" },
];
const WX = "weather_obs_hourly";
const BASE_F = 65; // degree days: the US convention, base 65 degrees F

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
  weather?: SeriesRow[]; // session 24: the station's hourly observed temperature (weather_obs_hourly)
};

// Session 29: the eight BAs' tables are one table per family (docs/migrations/2026-09-29-consolidation.md), a BA's
// rows told apart by entity (and ba); the run history still names each BA's member table, which the connector writes
const DEMAND = "eia930_all_demand";
const GEN = "eia930_all_generation";

async function load(ba: (typeof BAS)[number], yesterday: string): Promise<BAResult> {
  const dt = DEMAND;
  const dRun = `eia930_${ba.code}_demand`;
  const d = await attempt(() => series(dt, { entity: ba.entity, since: daysAgo(10) }));
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
    note = `Yesterday (${yesterday}) is ${hours.has(yesterday) ? `incomplete in ${dt} (${hours.get(yesterday)} of 24 hours)` : `not in ${dt}`}; showing ${day}, the latest complete day. Why: ${reason(dRun, yesterday)}`;
  }
  // generation: the same day if complete, else the latest complete day, said so with the reason
  const gt = GEN;
  const gRun = `eia930_${ba.code}_generation`;
  const g = await attempt(() => series(gt, { entity: ba.entity, since: daysAgo(10) }));
  if (!g.ok) return { ba, day, note, demand: d.data, gen: [], genDay: null, genNote: null, error: `generation: ${g.reason}` };
  const gh = new Map<string, number>();
  for (const r of g.data) if (r.variable === "net_generation_mw") gh.set(r.ts_utc.slice(0, 10), (gh.get(r.ts_utc.slice(0, 10)) ?? 0) + 1);
  const gComplete = Array.from(gh.entries()).filter(([, n]) => n === 24).map(([k]) => k).sort();
  let genDay: string | null = day, genNote: string | null = null;
  if (!gComplete.includes(day)) {
    genDay = gComplete.length ? gComplete[gComplete.length - 1] : null;
    genNote = `${gt} ${gh.has(day) ? `holds ${gh.get(day)} of 24 hours of ${day}` : `does not hold ${day}`}${genDay ? `; the mix shown is ${genDay}, its latest complete day` : ""}. Why: ${reason(gRun, day)}`;
  }
  const gen = genDay ? g.data.filter((r) => r.ts_utc.slice(0, 10) === genDay) : [];
  const w = ba.station ? await attempt(() => series(WX, { entity: `nws:${ba.station}`, variable: "temperature_f", since: daysAgo(10) })) : null;
  return { ba, day, note, demand: d.data, gen, genDay, genNote, error: null, weather: w && w.ok ? w.data : [] };
}

function Block({ r }: { r: BAResult }) {
  const table = DEMAND;
  const gtable = GEN;
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
  // session 24: the load center's observed temperature on a second axis, and degree days per UTC day
  const temps = (r.weather ?? []).filter((x) => Date.parse(x.ts_utc) >= c0 && Date.parse(x.ts_utc) < d1);
  if (temps.length) lines.push({ label: `Temperature, ${r.ba.station}`, points: temps.map((x) => ({ t: Date.parse(x.ts_utc) / 1000, v: x.value })), color: "var(--color-fuel-gas)", y2: true });
  const dd: { day: string; n: number; mean: number }[] = [];
  for (let t = c0; t < d1; t += 24 * H) {
    const day = iso(t).slice(0, 10);
    const h = temps.filter((x) => x.ts_utc.slice(0, 10) === day);
    dd.push({ day, n: h.length, mean: h.length ? h.reduce((a, x) => a + x.value, 0) / h.length : 0 });
  }
  const range = `${iso(d0)}|${iso(d1)}`;
  return (
    <div className="grid gap-6 lg:grid-cols-[18rem_1fr]">
      <div>
        {r.note ? <p className="mb-2 border border-dashed border-rule bg-panel px-2 py-1 text-xs text-muted">{r.note}</p> : null}
        <div className="text-xs text-muted">Peak demand, {r.day} (UTC day)</div>
        <div className="text-2xl tabular-nums">
          <Num check={`series_max|${table}|demand_mw|${range}|${r.ba.entity}`} raw={peak.value}>{count(peak.value)}</Num> <span className="text-sm text-muted">MW</span>
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
        <LineChart lines={lines} unit="MW" unit2="degF" height={220} ariaLabel={`${r.ba.label} hourly demand, day-ahead forecast and temperature, 7 days`} />
        <Cite tables={temps.length ? [table, WX] : [table]} note={`Hourly demand and EIA's day-ahead demand forecast, the 7 UTC days to ${r.day}. Error is demand minus forecast${temps.length ? `. Temperature: the hourly mean observed at ${r.ba.station}, the load center's airport (right axis, degrees F); weather data: National Weather Service` : ""}`} />
        {r.ba.station ? (
          <p className="mt-1 text-xs">
            <span className="text-muted">Degree days at {r.ba.station} (base {BASE_F} F, from the UTC day&apos;s 24 hourly mean temperatures; CDD cooling, HDD heating):</span>{" "}
            {dd.map((x, i) => (
              <span key={x.day}>
                {i ? "; " : ""}
                {x.day.slice(5)}{" "}
                {x.n === 24
                  ? x.mean >= BASE_F
                    ? `CDD ${(x.mean - BASE_F).toFixed(1)}`
                    : `HDD ${(BASE_F - x.mean).toFixed(1)}`
                  : `not computed (${x.n} of 24 hours in ${WX})`}
              </span>
            ))}
          </p>
        ) : null}
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
  return (
    <div className="mt-4">
      <div className="mb-1 text-xs text-muted">
        {r.genNote ? <span className="mb-1 block border border-dashed border-rule px-2 py-1">{r.genNote}</span> : null}Generation mix, {r.genDay}: <Num check={`series_sum|${gtable}|net_generation_mw|${r.genDay}T00:00:00Z|${iso(Date.parse(`${r.genDay}T00:00:00Z`) + 24 * H)}|${r.ba.entity}`} raw={total}>{count(total)}</Num> MWh net
      </div>
      <ShareBar
        parts={pos.map((f) => ({ name: f.label, value: f.mwh, color: `var(--color-fuel-${f.key})` }))}
        unit="MWh"
        ariaLabel={`${r.ba.label} generation by fuel, ${r.genDay}`}
        file={`erw-${r.ba.code}-mix-${r.genDay}`}
      />
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
      <p className="mb-2 max-w-3xl">
        Yesterday&apos;s electricity demand, day-ahead demand forecast and generation by fuel for seven <Term t="ISO" first />s and the Lower 48, with the last seven
        days of demand, from <Term t="EIA" first />&apos;s Hourly Electric Grid Monitor (Form EIA-930).
      </p>
      <p className="mb-5 max-w-3xl text-sm text-muted">
        Each ISO&apos;s peak demand and when it came, how far EIA&apos;s
        day-ahead demand forecast missed, the generation mix, and the last seven days of demand. Days are UTC days, as EIA publishes them; the peak
        hour is also given in the ISO&apos;s local time.
      </p>
      {/* session 35: the seven grid pages */}
      <p className="mb-4 text-sm">
        <span className="font-semibold">Your grid:</span>{" "}
        {YOUR_GRID.map((l, i) => (
          <span key={l.href}>{i ? " · " : ""}<Link href={l.href}>{l.label}</Link></span>
        ))}
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
        <Cite tables={[GEN]} />
      </Section>
      <Related href="/grid" />
    </>
  );
}
