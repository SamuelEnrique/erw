// Energy Research Warehouse (ERW) site, session 133: the first view of the one energy mix page (/mix), "Now and by state".
// These are the three sections of the original page (session 18), with their filters and hover, moved here as they
// were: today so far, the hourly mix of the last seven days by grid operator, and the monthly mix by state since 2001.
// They read the live tables (eia930_generation_latest, eia930_all_generation, state_generation_mix_monthly). The notes
// that stood under each chart are in the Method note (docs/methods/generation_mix_hourly.md, "Session 133").
import { ShareBar } from "@/components/ShareBar";
import { Num } from "@/components/Num";
import { Legend, StackedArea, type Layer } from "@/components/StackedArea";
import type { SeriesRow } from "@/lib/data";
import { count, price } from "@/lib/format";
import { STATES } from "@/lib/regions";

export const MONTHLY = "state_generation_mix_monthly";
export const LATEST = "eia930_generation_latest";

/** A short placeholder for something not held, with the reason on hover. */
export function Missing({ why, words = "not held yet" }: { why: string; words?: string }) {
  return <span className="cursor-help border-b border-dotted border-muted text-sm italic text-muted" title={why} data-missing="1">{words}</span>;
}

const H = 3_600_000;

// EIA-930 energy sources grouped as on /grid (the same color tokens)
export const HOURLY_FUELS: { key: string; label: string; vars: string[] }[] = [
  { key: "gas", label: "Natural gas", vars: ["natural_gas"] },
  { key: "coal", label: "Coal", vars: ["coal"] },
  { key: "nuclear", label: "Nuclear", vars: ["nuclear"] },
  { key: "wind", label: "Wind", vars: ["wind", "wind_with_battery"] },
  { key: "solar", label: "Solar", vars: ["solar", "solar_with_battery"] },
  { key: "hydro", label: "Hydro", vars: ["hydro"] },
  { key: "storage", label: "Storage", vars: ["battery", "pumped_storage", "other_storage", "unknown_storage"] },
  { key: "other", label: "Other", vars: [] },
];
const hourlyGroup = (variable: string) => {
  const f = variable.replace(/^net_generation_/, "").replace(/_mw$/, "");
  return HOURLY_FUELS.find((g) => g.vars.includes(f))?.key ?? "other";
};

// the groups of state_generation_mix_monthly (docs/methods/generation_mix.md)
const MONTHLY_FUELS: { key: string; label: string; color: string }[] = [
  { key: "natural_gas", label: "Natural gas", color: "var(--color-fuel-gas)" },
  { key: "coal", label: "Coal", color: "var(--color-fuel-coal)" },
  { key: "nuclear", label: "Nuclear", color: "var(--color-fuel-nuclear)" },
  { key: "wind", label: "Wind", color: "var(--color-fuel-wind)" },
  { key: "solar", label: "Solar (utility scale)", color: "var(--color-fuel-solar)" },
  { key: "hydro", label: "Hydro", color: "var(--color-fuel-hydro)" },
  { key: "other_renewables", label: "Geothermal and biomass", color: "var(--color-fuel-storage)" },
  { key: "oil_and_other", label: "Oil, other gases, pumped storage, other", color: "var(--color-fuel-other)" },
  { key: "not_itemized", label: "Not itemized by EIA", color: "var(--color-muted)" },
];
const monthlyVar = (k: string) => `net_generation_${k}_mwh`;

/** A stored value as the value check reads it: whole numbers with commas, else two decimals. */
const exact = (v: number) => (Number.isInteger(v) ? count(v) : price(v));
const iso = (t: number) => new Date(t).toISOString().replace(/\.\d{3}Z$/, "Z");

function pick(v: string | string[] | undefined, ok: (s: string) => boolean, fallback: string) {
  const s = Array.isArray(v) ? v[0] : v;
  return s && ok(s) ? s : fallback;
}

/** The "today so far" strip: the latest UTC day in eia930_generation_latest for one BA. */
export function Today({ rows, label }: { rows: SeriesRow[]; label: string }) {
  if (!rows.length) return <Missing why={`EIA publishes fuel data a day or more after the hour, and no complete hour of ${label} is held yet.`} />;
  const day = rows.reduce((a, r) => (r.ts_utc > a ? r.ts_utc : a), "").slice(0, 10);
  const today = rows.filter((r) => r.ts_utc.slice(0, 10) === day);
  const hours = Array.from(new Set(today.filter((r) => r.variable === "net_generation_mw").map((r) => r.ts_utc))).sort();
  const total = today.filter((r) => r.variable === "net_generation_mw").reduce((a, r) => a + r.value, 0);
  const by = new Map<string, number>();
  for (const r of today) if (r.variable !== "net_generation_mw") by.set(hourlyGroup(r.variable), (by.get(hourlyGroup(r.variable)) ?? 0) + r.value);
  const pos = HOURLY_FUELS.map((f) => ({ ...f, mwh: by.get(f.key) ?? 0 })).filter((f) => f.mwh > 0);
  const last = hours[hours.length - 1];
  const entity = today[0].entity;
  return (
    <div>
      <p className="mb-2 text-sm">
        {day} (UTC), {hours.length} complete {hours.length === 1 ? "hour" : "hours"}, 00:00 to {new Date(Date.parse(last) + H).toISOString().slice(11, 16)} UTC:{" "}
        <Num check={`series_esum|${LATEST}|${entity}|net_generation_mw|${day}T00:00:00Z|${iso(Date.parse(`${day}T00:00:00Z`) + 24 * H)}`} raw={total}>
          {exact(total)}
        </Num>{" "}
        MWh net generation
      </p>
      <ShareBar
        parts={pos.map((f) => ({ name: f.label, value: f.mwh, color: `var(--color-fuel-${f.key})` }))}
        unit="MWh"
        ariaLabel={`${label} generation by fuel so far on ${day}`}
        file={`erw-mix-today-${day}`}
      />
      <p className="mt-1 text-xs text-muted">
        {pos.map((f) => `${f.label} ${((f.mwh / total) * 100).toFixed(1)}%`).join("; ")}
      </p>
    </div>
  );
}

export function Hourly({ rows, table, label }: { rows: SeriesRow[]; table: string; label: string }) {
  const nh = new Map<string, number>();
  for (const r of rows) if (r.variable === "net_generation_mw") nh.set(r.ts_utc.slice(0, 10), (nh.get(r.ts_utc.slice(0, 10)) ?? 0) + 1);
  const days = Array.from(nh.entries()).filter(([, n]) => n === 24).map(([d]) => d).sort().slice(-7);
  if (days.length === 0) return <Missing why={`No complete day of ${label} is held in the last 9 days.`} />;
  const t0 = Date.parse(`${days[0]}T00:00:00Z`), t1 = Date.parse(`${days[days.length - 1]}T00:00:00Z`) + 24 * H;
  const x: number[] = [];
  for (let t = t0; t < t1; t += H) x.push(t);
  const idx = new Map(x.map((t, i) => [t, i])); // by parsed time: Supabase writes "+00:00", not "Z"
  const layers: Layer[] = HOURLY_FUELS.map((f) => ({ key: f.key, label: f.label, color: `var(--color-fuel-${f.key})`, values: new Array(x.length).fill(null) }));
  const lk = new Map(layers.map((l) => [l.key, l]));
  for (const r of rows) {
    if (r.variable === "net_generation_mw") continue;
    const i = idx.get(Date.parse(r.ts_utc));
    if (i === undefined) continue;
    const l = lk.get(hourlyGroup(r.variable))!;
    l.values[i] = (l.values[i] ?? 0) + r.value;
  }
  const ticks = days.map((d) => Date.parse(`${d}T00:00:00Z`));
  return (
    <>
      <StackedArea
        x={x}
        layers={layers}
        unit="MW"
        ariaLabel={`${label} hourly net generation by fuel, ${days[0]} to ${days[days.length - 1]}`}
        tick={(t) => new Date(t).toISOString().slice(5, 10)}
        ticks={ticks}
      />
    </>
  );
}

export function Monthly({ rows, st }: { rows: SeriesRow[]; st: string }) {
  const months = Array.from(new Set(rows.map((r) => r.ts_utc))).sort();
  if (!months.length) return <Missing why={`No month of ${STATES[st]} is held.`} />;
  const x = months.map((m) => Date.parse(m));
  const idx = new Map(months.map((m, i) => [m, i]));
  const val = new Map(rows.map((r) => [`${r.variable}|${r.ts_utc}`, r.value]));
  const layers: Layer[] = MONTHLY_FUELS.map((f) => ({
    key: f.key,
    label: f.label,
    color: f.color,
    values: months.map((m) => val.get(`${monthlyVar(f.key)}|${m}`) ?? null),
  }));
  const present = MONTHLY_FUELS.filter((f) => rows.some((r) => r.variable === monthlyVar(f.key)));
  const lastM = months[months.length - 1];
  const lastYear = Number(lastM.slice(0, 4)) - (lastM.slice(5, 7) === "12" ? 0 : 1);
  // share columns: whole calendar years, and the latest 12 months
  const years = [2001, 2010, 2020, lastYear].filter((y, i, a) => a.indexOf(y) === i && months.some((m) => m.startsWith(`${y}-12`)));
  const cols = [
    ...years.map((y) => ({ label: String(y), from: `${y}-01`, to: `${y}-12` })),
    { label: `12 months to ${lastM.slice(0, 7)}`, from: months[Math.max(0, months.length - 12)].slice(0, 7), to: lastM.slice(0, 7) },
  ];
  const sumOver = (key: string | null, from: string, to: string) =>
    rows.filter((r) => r.ts_utc.slice(0, 7) >= from && r.ts_utc.slice(0, 7) <= to && (key === null || r.variable === monthlyVar(key))).reduce((a, r) => a + r.value, 0);
  const ticks = x.filter((t) => {
    const d = new Date(t);
    return d.getUTCMonth() === 0 && d.getUTCFullYear() % 5 === 0;
  });
  return (
    <>
      <Legend items={present} />
      <StackedArea
        x={x}
        layers={layers}
        unit="MWh"
        ariaLabel={`${STATES[st]} monthly net generation by fuel group, ${months[0].slice(0, 7)} to ${lastM.slice(0, 7)}`}
        tick={(t) => String(new Date(t).getUTCFullYear())}
        ticks={ticks}
      />
      <div className="mt-4 overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-rule text-left text-xs text-muted">
              <th className="py-1 pr-3 font-normal">Fuel group</th>
              {cols.map((c) => (
                <th key={c.label} className="py-1 pr-3 text-right font-normal">
                  {c.label}
                </th>
              ))}
              <th className="py-1 pr-3 text-right font-normal">{lastM.slice(0, 7)}, MWh</th>
            </tr>
          </thead>
          <tbody>
            {present.map((f) => (
              <tr key={f.key} className="border-b border-rule/60">
                <td className="py-1 pr-3">
                  <span className="mr-1 inline-block h-2.5 w-2.5 rounded-sm" style={{ background: f.color }} />
                  {f.label}
                </td>
                {cols.map((c) => {
                  const tot = sumOver(null, c.from, c.to);
                  const v = sumOver(f.key, c.from, c.to);
                  return (
                    <td key={c.label} className="py-1 pr-3 text-right tabular-nums">
                      {tot > 0 ? `${Math.abs((v / tot) * 100) < 0.05 ? "0.0" : ((v / tot) * 100).toFixed(1)}%` : ""}
                    </td>
                  );
                })}
                <td className="py-1 pr-3 text-right tabular-nums">
                  {idx.has(lastM) && val.has(`${monthlyVar(f.key)}|${lastM}`) ? (
                    <Num check={`series|${MONTHLY}|eia:${st}|${monthlyVar(f.key)}|${lastM}`} raw={val.get(`${monthlyVar(f.key)}|${lastM}`)!}>
                      {exact(val.get(`${monthlyVar(f.key)}|${lastM}`)!)}
                    </Num>
                  ) : (
                    ""
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
