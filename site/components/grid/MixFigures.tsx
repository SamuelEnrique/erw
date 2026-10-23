// Energy Research Warehouse (ERW) site, session 1152 (chain 077): the Grid tool's energy mix panel, `grid_mix_<grid>`,
// at the top of the hourly block of the Mix tab ("Now and by state"). Two views, the choice in the address (mixp):
// - hourly (the default): the 24 hours that end with the newest hour held, each fuel's MWh and share of the net
//   generation, the hour of peak demand (also marked on the 7-day chart below), the newest hour held and its age;
// - by month (mixp=month): the grid's monthly mix from generation_mix_hourly_profile, the last 24 months held, each
//   fuel's MWh and share on hover, the newest month and the last twelve months as keyed figures.
// Every figure is a lib/mixHourly.ts figure: a check key scripts/check-values.mjs recomputes, and a one-line source in
// its hover tip. California's hourly mix stays withheld (the session 118 ruling, said once by the block below).
// Session 1155: on CAISO's monthly view, the months with an Energy Emergency Alert or a Flex Alert day are marked on the
// chart (a dashed line at the month, its days on hover), and the alert days of the months drawn are one keyed count
// (lib/caisoAlerts.ts alertMonths). The hourly mix has nothing to mark: it is withheld for CAISO.
import { Num } from "@/components/Num";
import { scrollRegion } from "@/lib/cells";
import { ALERT_TABLE, alertMonths, type NoticeLike } from "@/lib/caisoAlerts";
import { TimeChart } from "@/components/TimeChart";
import { shown } from "@/lib/format";
import { hourAge, mixMonthly, PROFILE, type Fig, type MixHourly, type MonthFuel } from "@/lib/mixHourly";

const H = 3_600_000;
const hourName = (t: number) => `${new Date(t).toISOString().slice(0, 13).replace("T", " ")}:00 UTC`;
const endName = (t: number) => { const s = hourName(t); return s.endsWith(" 00:00 UTC") ? `${new Date(t - H).toISOString().slice(0, 10)} 24:00 UTC` : s; };

/** A figure with its key and its one-line source as the hover tip. */
function F({ f, unit }: { f: Fig; unit?: string }) {
  return (
    <span title={f.tip} className="cursor-help border-b border-dotted border-muted">
      <Num check={f.check} raw={f.raw}>{shown(f.raw)}</Num>{unit ?? ""}
    </span>
  );
}

/** The hourly view's figures: the 24 hours to the newest hour held. */
export function HourlyFigures({ m, label, now }: { m: MixHourly; label: string; now: number }) {
  const age = hourAge(m.newest.t, now);
  return (
    <div className="mb-2">
      <p className="mb-1 max-w-3xl text-sm" data-mix-headline="1">
        The 24 hours from {hourName(m.start)} to {endName(m.end)} ({m.hours} of 24 hours held): <F f={m.total} /> MWh net generation.{" "}
        {m.peak ? <>Peak demand <F f={m.peak.fig} /> MW, in the hour from {hourName(m.peak.t)} (marked on the chart).</> : <>Demand is not held for these hours.</>}
      </p>
      <p className="mb-2 text-xs text-muted" data-mix-age={age}>
        Newest hour held: from {hourName(m.newest.t)}, <F f={m.newest.fig} /> MW net generation. It ended {age} {age === 1 ? "hour" : "hours"} before this page was drawn ({new Date(now).toISOString().slice(0, 16).replace("T", " ")} UTC); EIA publishes fuel data a day or more after the hour.
      </p>
      {/* session 1158: the frame a keyboard can reach and scroll at 390 px (lib/cells.ts scrollRegion, as ToolTable draws it) */}
      <div className="overflow-x-auto" {...scrollRegion(`${label}: net generation by fuel over the 24 hours to the newest hour held`)}>
        <table className="w-full border-collapse text-sm tabular-nums" style={{ minWidth: 320 }}>
          <caption className="sr-only">{label}: net generation by fuel over the 24 hours to the newest hour held</caption>
          <thead>
            <tr className="border-b border-rule text-left text-xs text-muted">
              <th scope="col" className="py-1 pr-3 font-normal">Fuel</th>
              <th scope="col" className="py-1 pr-3 text-right font-normal">MWh, 24 hours</th>
              <th scope="col" className="py-1 pr-3 text-right font-normal">Share of net generation</th>
            </tr>
          </thead>
          <tbody>
            {m.fuels.map((f) => (
              <tr key={f.key} className="border-b border-rule/60" data-mix-fuel={f.key}>
                <th scope="row" className="py-1 pr-3 text-left font-normal"><span aria-hidden="true" className="mr-1 inline-block h-2.5 w-2.5" style={{ background: `var(--color-fuel-${f.key})` }} />{f.label}</th>
                <td className="py-1 pr-3 text-right"><F f={f.mwh} /></td>
                <td className="py-1 pr-3 text-right">{f.share ? <F f={f.share} unit="%" /> : ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/** The generation_mix_hourly_profile fuels, in the hourly chart's order and colors. */
export const MONTH_FUELS: MonthFuel[] = [
  { key: "gas", label: "Natural gas", stem: "natural_gas" },
  { key: "coal", label: "Coal", stem: "coal" },
  { key: "nuclear", label: "Nuclear", stem: "nuclear" },
  { key: "wind", label: "Wind", stem: "wind" },
  { key: "solar", label: "Solar", stem: "solar" },
  { key: "hydro", label: "Hydro", stem: "hydro" },
  { key: "storage", label: "Storage", stem: "storage" },
  { key: "other", label: "Other", stem: "other" },
];
export const MONTH_VARIABLES = [...MONTH_FUELS.flatMap((f) => [`${f.stem}_mwh`, `${f.stem}_share_pct`]), "net_generation_mwh", "days_held", "days_in_month"];

/** The monthly view: the grid's months from generation_mix_hourly_profile (rows read by the caller). */
export function MonthlyFigures({ rows, label, caiso, notices }: { rows: { entity: string; variable: string; ts_utc: string; value: number }[]; label: string; caiso: boolean;
  /** session 1155: CAISO's notices (caiso_grid_emergencies), read or failed; absent for another grid */
  notices?: { ok: true; data: NoticeLike[] } | { ok: false; reason: string } | null }) {
  const m = mixMonthly(rows, MONTH_FUELS);
  if (!m) return <p className="text-sm italic text-muted" data-missing="1">No month of {label} is held in {PROFILE}.</p>;
  const al = notices && notices.ok ? alertMonths(notices.data, m.months) : null;
  const name = (d: string) => d.slice(0, 7);
  const x = m.months.map((d) => Date.parse(`${d}T00:00:00Z`));
  return (
    <div className="mb-2">
      <p className="mb-1 max-w-3xl text-sm" data-mix-month={m.newest}>
        {label} by month, {name(m.months[0])} to {name(m.newest)}: each month&apos;s generation by fuel over its complete days ({PROFILE}, EIA-930
        {caiso ? "; California from January 2026 on CAISO's own data, December 2025 not written, as the method says" : ""}).
        {m.days && m.daysInMonth ? <> {name(m.newest)} is built on <F f={m.days} /> of its <F f={m.daysInMonth} /> days.</> : null}
        {m.notBuilt.length ? <> Not built in the twelve months to {name(m.newest)}: {m.notBuilt.join(", ")} (too few complete days, or the month of a change of source).</> : null}
      </p>
      <TimeChart stack share x="month" unit="MWh" height={300}
        marks={al?.months.length ? al.months.map((a) => ({ t: Date.parse(`${a.month}T00:00:00Z`), name: `EEA or Flex Alert: ${a.days.join(", ")}` })) : undefined}
        ariaLabel={`${label} monthly net generation by fuel, ${name(m.months[0])} to ${name(m.newest)}`}
        series={m.fuels.map((f) => ({ name: f.label, color: `var(--color-fuel-${f.key})`, points: x.map((t, i) => [t, f.values[i]] as [number, number | null]) }))} />
      <div className="mt-3 overflow-x-auto" {...scrollRegion(`${label}: generation by fuel in ${name(m.newest)} and over the twelve months to it`)}>
        <table className="w-full border-collapse text-sm tabular-nums" style={{ minWidth: 380 }}>
          <caption className="sr-only">{label}: generation by fuel in {name(m.newest)} and over the twelve months to it</caption>
          <thead>
            <tr className="border-b border-rule text-left text-xs text-muted">
              <th scope="col" className="py-1 pr-3 font-normal">Fuel</th>
              <th scope="col" className="py-1 pr-3 text-right font-normal">{name(m.newest)}, MWh</th>
              <th scope="col" className="py-1 pr-3 text-right font-normal">{name(m.newest)}, share</th>
              <th scope="col" className="py-1 pr-3 text-right font-normal">12 months to {name(m.newest)}, MWh{m.notBuilt.length ? ` (${12 - m.notBuilt.length} built)` : ""}</th>
            </tr>
          </thead>
          <tbody>
            {m.fuels.map((f) => (
              <tr key={f.key} className="border-b border-rule/60" data-mix-fuel={f.key}>
                <th scope="row" className="py-1 pr-3 text-left font-normal"><span aria-hidden="true" className="mr-1 inline-block h-2.5 w-2.5" style={{ background: `var(--color-fuel-${f.key})` }} />{f.label}</th>
                <td className="py-1 pr-3 text-right">{f.mwh ? <F f={f.mwh} /> : ""}</td>
                <td className="py-1 pr-3 text-right">{f.share ? <F f={f.share} unit="%" /> : ""}</td>
                <td className="py-1 pr-3 text-right">{f.year ? <F f={f.year} /> : ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {notices ? (
        <p className="mt-1 text-xs text-muted" data-mix-alert-months={al ? al.months.length : "unread"}>
          {al ? <>Days with an Energy Emergency Alert or a Flex Alert in force, {al.from} to {al.to} ({ALERT_TABLE}): <F f={{ check: al.signal.check, raw: Number(al.signal.raw), tip: al.signal.tip }} />
            {al.months.length ? `; each month that holds one is marked on the chart (${al.months.map((a) => a.month.slice(0, 7)).join(", ")}).` : ", so no month of the chart is marked."}</>
            : <>The alert days could not be read just now ({ALERT_TABLE}: {notices.ok ? "" : notices.reason}).</>}
        </p>
      ) : null}
      <p className="mt-1 text-xs text-muted">A share is of the sum of the eight sources over the month&apos;s complete days; storage is negative when it charges more than it discharges. Hover the chart for each fuel&apos;s MWh and share in a month.</p>
    </div>
  );
}
