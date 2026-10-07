import type { Metadata } from "next";
import Link from "next/link";
import { SiteLink } from "@/components/SiteLink";
import { ChartFrame, Fold, HeadlineNumber, HeadlineRow, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import fileJson from "@/data/curtailment_profile.json";
import {
  CATS, FUELS, INPUT, REASONS, TABLE, battDay, batteryMonths, byHour, choice, hasBattery, hasCats, hourName, href, peakHour, periodName, periodOf, reasonCover, two, whole,
  type CurtFile, type Row,
} from "@/lib/curtailmentv2";

// Session 98: "Curtailment", version 2, in review (lib/release.ts), in the battery page's layout, for California: wind
// and solar curtailed by hour of the day, by month since 2019, by CAISO's reason, and against what the batteries took
// in during the same hours. Every number is a row of caiso_curtailment_profile (warehouse/derived/curtailment_profile.py;
// docs/methods/caiso_curtailment_intervals.md) or a year's sum the builder wrote into the site's own copy
// (data/curtailment_profile.json). The page /curtailment (every grid, by day and month) is as it was. Credit: California ISO.
export const metadata: Metadata = { title: "Curtailment, version 2", robots: { index: false, follow: false } };

const file = fileJson as unknown as CurtFile;
const METHOD = "/data/methods/caiso_curtailment_intervals";
const N = ({ k, children }: { k: string; children: string }) => <span data-n={k}>{children}</span>;
const INK = "var(--color-ink)", BATT = "var(--color-fuel-storage)";

function axis(hi: number) {
  const step = [50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000].find((s) => hi / s <= 6) ?? 500000;
  return Array.from({ length: Math.floor(hi / step) + 1 }, (_, i) => i * step);
}

/** By hour of the day: the period's MWh in each local hour, solar and wind stacked. */
function HourChart({ r, label }: { r: Row; label: string }) {
  const W = 760, H = 280, L = 70, R = 10, top = 16, bot = 30;
  const s = byHour(r, "solar"), w = byHour(r, "wind");
  const hi = Math.max(1, ...s.map((v, h) => v + w[h])) * 1.08;
  const bw = (W - L - R) / 24;
  const y = (v: number) => top + ((hi - v) / hi) * (H - top - bot);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" data-chart="hours" aria-label={`California, ${label}: wind and solar curtailed by local hour of the day, MWh`}>
      {axis(hi).map((t) => (
        <g key={t}>
          <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke="var(--color-rule)" strokeWidth={t === 0 ? 1.5 : 0.75} />
          <text x={L - 6} y={y(t) + 4} textAnchor="end" fontSize="11" fill="var(--color-muted)">{t.toLocaleString("en-US")}</text>
        </g>
      ))}
      {s.map((v, h) => (
        <g key={h} data-hour={h}>
          <title>{`${hourName(h)}: solar ${whole(v)} MWh, wind ${whole(w[h])} MWh`}</title>
          {v > 0 ? <rect x={L + h * bw + 2} y={y(v)} width={bw - 4} height={y(0) - y(v)} fill={FUELS[0].color} /> : null}
          {w[h] > 0 ? <rect x={L + h * bw + 2} y={y(v + w[h])} width={bw - 4} height={y(v) - y(v + w[h])} fill={FUELS[1].color} /> : null}
          {h % 3 === 0 ? <text x={L + (h + 0.5) * bw} y={H - 10} textAnchor="middle" fontSize="11" fill="var(--color-muted)">{hourName(h)}</text> : null}
        </g>
      ))}
      <text x={L} y={11} fontSize="11" fill="var(--color-muted)">MWh in the period, by local hour</text>
    </svg>
  );
}

/** By month since 2019: a bar a month, stacked by fuel or by CAISO's reason. */
function MonthChart({ by, period }: { by: "fuel" | "reason"; period: string }) {
  const W = 760, H = 260, L = 70, R = 10, top = 16, bot = 30;
  const ms = Object.keys(file.months).sort();
  const parts = (r: Row) => (by === "fuel"
    ? FUELS.map((f) => ({ color: f.color, v: r[`curtailed_${f.key}_mwh`] ?? 0 }))
    : REASONS.map((x) => ({ color: x.color, v: (r[`curtailed_solar_${x.key}_mwh`] ?? 0) + (r[`curtailed_wind_${x.key}_mwh`] ?? 0) })));
  const hi = Math.max(1, ...ms.map((m) => parts(file.months[m]).reduce((a, p) => a + p.v, 0))) * 1.06;
  const bw = (W - L - R) / ms.length;
  const y = (v: number) => top + ((hi - v) / hi) * (H - top - bot);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" data-chart={`months-${by}`} aria-label={`California: wind and solar curtailed by month since ${file.first.slice(0, 4)}, by ${by}, MWh`}>
      {axis(hi).map((t) => (
        <g key={t}>
          <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke="var(--color-rule)" strokeWidth={t === 0 ? 1.5 : 0.75} />
          <text x={L - 6} y={y(t) + 4} textAnchor="end" fontSize="11" fill="var(--color-muted)">{t.toLocaleString("en-US")}</text>
        </g>
      ))}
      {ms.map((m, i) => {
        let at = 0;
        const on = m === period || m.slice(0, 4) === period;
        return (
          <g key={m} data-month={m} opacity={on || period.length === 0 ? 1 : 0.55}>
            <title>{`${periodName(m)}: ${whole(parts(file.months[m]).reduce((a, p) => a + p.v, 0))} MWh`}</title>
            {parts(file.months[m]).map((p, j) => { const y0 = at; at += p.v; return p.v > 0 ? <rect key={j} x={L + i * bw + 0.5} y={y(at)} width={Math.max(1, bw - 1)} height={y(y0) - y(at)} fill={p.color} /> : null; })}
            {m.endsWith("-01") ? <text x={L + i * bw} y={H - 10} fontSize="11" fill="var(--color-muted)">{m.slice(0, 4)}</text> : null}
          </g>
        );
      })}
      <text x={L} y={11} fontSize="11" fill="var(--color-muted)">MWh a month</text>
    </svg>
  );
}

/** The average day of a month: wind and solar curtailed, against what the batteries took in, by local hour, MW. */
function BatteryChart({ r, label }: { r: Row; label: string }) {
  const W = 760, H = 280, L = 70, R = 10, top = 16, bot = 30;
  const d = battDay(r);
  const hi = Math.max(1, ...d.map((x) => Math.max(x.curtailed, x.charging))) * 1.08;
  const x = (h: number) => L + ((h + 0.5) / 24) * (W - L - R);
  const y = (v: number) => top + ((hi - v) / hi) * (H - top - bot);
  const line = (k: "curtailed" | "charging") => d.map((p, i) => `${i ? "L" : "M"}${x(p.hour).toFixed(1)},${y(p[k]).toFixed(1)}`).join(" ");
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" data-chart="battery" aria-label={`California, ${label}: the average day's wind and solar curtailment and battery charging by local hour, MW`}>
      {axis(hi).map((t) => (
        <g key={t}>
          <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke="var(--color-rule)" strokeWidth={t === 0 ? 1.5 : 0.75} />
          <text x={L - 6} y={y(t) + 4} textAnchor="end" fontSize="11" fill="var(--color-muted)">{t.toLocaleString("en-US")}</text>
        </g>
      ))}
      <path d={`${line("curtailed")} L${x(23).toFixed(1)},${y(0).toFixed(1)} L${x(0).toFixed(1)},${y(0).toFixed(1)} Z`} fill="var(--color-fuel-solar)" fillOpacity="0.45"><title>{`Curtailed, MW: ${d.map((p) => `${hourName(p.hour)} ${whole(p.curtailed)}`).join(", ")}`}</title></path>
      <path d={line("charging")} fill="none" stroke={BATT} strokeWidth="2.5"><title>{`Battery charging, MW: ${d.map((p) => `${hourName(p.hour)} ${whole(p.charging)}`).join(", ")}`}</title></path>
      {[0, 3, 6, 9, 12, 15, 18, 21].map((h) => <text key={h} x={x(h)} y={H - 10} textAnchor="middle" fontSize="11" fill="var(--color-muted)">{hourName(h)}</text>)}
      <text x={L} y={11} fontSize="11" fill="var(--color-muted)">MW, average day, local time</text>
    </svg>
  );
}

export default async function CurtailmentV2({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const q = Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined]));
  const period = choice(q, file);
  const r = periodOf(file, period)!;
  const label = periodName(period);
  const months = Object.keys(file.months).sort();
  const years = [...new Set(months.map((m) => m.slice(0, 4)))];
  const item = (on: boolean) => `no-underline ${on ? "font-semibold text-accent" : "text-ink hover:text-accent"}`;
  const peak = peakHour(r);
  const cover = reasonCover(r);
  const bm = batteryMonths(file);
  // the batteries are compared by month: the period's own month, or for a year the newest month of it that holds them
  const battMonth = period.length === 7 ? (hasBattery(r) ? period : null) : bm.filter((m) => m.startsWith(period)).at(-1) ?? null;
  const br = battMonth ? file.months[battMonth] : null;
  const days = period.length === 7 ? <><N k="days_held">{whole(r.days_held)}</N> of {whole(r.days_in_month)} days</> : <><N k="days_held">{whole(r.days_held)}</N> of {whole(r.days_in_period)} days, {r.months} months</>;

  return (
    <ToolPage>
      <ToolHeader title="Curtailment"
        crumb={<>Version 2, in review, for California. Every grid by day and month: <SiteLink href="/curtailment">curtailment</SiteLink>.</>}
        lead={<>When there is more wind and sun than the grid can take, the operator turns plants down: curtailment. For California, from the grid operator&apos;s own five-minute record since 2019: at what hours it happens, in which months, for what reason,
          and how it compares with what the batteries take in during the same hours. See also <SiteLink href="/mix/v2">the energy mix</SiteLink> and <SiteLink href="/cost-of-power/battery">what a battery earns</SiteLink>.</>} />
      <p className="mb-8 max-w-3xl border-l-2 border-accent bg-paper px-3 py-2 text-sm" data-not-located="1">
        <span className="font-semibold">The data does not say where.</span> CAISO publishes one figure for its whole system: not the plant, not the node or zone, and for a &quot;local&quot; curtailment not which line was congested.
        So nothing here says whether a battery at a given place could have taken the power that was turned down.
      </p>
      <div className="grid gap-8 lg:grid-cols-[240px_minmax(0,1fr)]">
        <aside>
          <InputPanel title="Choose" note={<>California (CAISO). A year, or one of its months. {file.days_not_held.length ? <>Not held: {file.days_not_held.join(", ")} (CAISO&apos;s report for the day could not be read whole).</> : null}</>}>
            <nav aria-label="Period" className="text-sm">
              <div className="mb-1 text-xs uppercase tracking-wide text-muted">Period</div>
              {years.map((y) => (
                <div key={y} className="mb-1.5 flex flex-wrap items-baseline gap-x-1.5 gap-y-0.5">
                  {file.years[y] ? <Link href={href(y)} aria-current={period === y ? "true" : undefined} className={`w-9 text-xs ${item(period === y)}`}>{y}</Link> : <span className="w-9 text-xs text-muted">{y}</span>}
                  {months.filter((m) => m.startsWith(y)).map((m) => <Link key={m} href={href(m)} aria-current={m === period ? "true" : undefined} className={`text-xs ${item(m === period)}`}>{m.slice(5)}</Link>)}
                </div>
              ))}
            </nav>
          </InputPanel>
        </aside>

        <div className="min-w-0">
          <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-summary="1">
            In {label}, California curtailed <N k="sum|solar">{whole(r.curtailed_solar_mwh)}</N> MWh of solar and <N k="sum|wind">{whole(r.curtailed_wind_mwh)}</N> MWh of wind, more in the hour from {hourName(peak.hour)} than in any other.{" "}
            {cover === "none" ? <>CAISO published no reason for it then.</> : <><N k="sum|local">{whole(r.curtailed_solar_local_mwh + r.curtailed_wind_local_mwh)}</N> MWh was for local congestion and <N k="sum|system">{whole(r.curtailed_solar_system_mwh + r.curtailed_wind_system_mwh)}</N> MWh for system-wide oversupply{cover === "part" ? ", with no reason published for the rest" : ""}.</>}{" "}
            {br && br.curtailed_while_charging_share_pct !== undefined ? <>In {periodName(battMonth!)}, <N k="sum|while">{two(br.curtailed_while_charging_share_pct)}</N> percent of it fell in hours in which the batteries were already charging.</> : null}
          </p>
          <HeadlineRow>
            <HeadlineNumber label="Solar curtailed" value={<N k="head|solar">{whole(r.curtailed_solar_mwh)}</N>} unit="MWh" note={<>Over {days}.</>} />
            <HeadlineNumber label="Wind curtailed" value={<N k="head|wind">{whole(r.curtailed_wind_mwh)}</N>} unit="MWh" note={<>The hour with the most, wind and solar: {hourName(peak.hour)} (<N k="head|peak_solar">{whole(peak.solar)}</N> MWh of solar, <N k="head|peak_wind">{whole(peak.wind)}</N> of wind in the period).</>} />
            <HeadlineNumber label="For local congestion" value={cover === "none" ? <span className="text-muted">not published</span> : <N k="head|local">{whole(r.curtailed_solar_local_mwh + r.curtailed_wind_local_mwh)}</N>} unit={cover === "none" ? undefined : "MWh"}
              note={cover === "none" ? <>CAISO&apos;s file gives a reason from 2022.</> : <>System-wide oversupply: <N k="head|system">{whole(r.curtailed_solar_system_mwh + r.curtailed_wind_system_mwh)}</N> MWh.{cover === "part" ? <> No reason published: <N k="head|unspecified">{whole(r.curtailed_solar_unspecified_mwh + r.curtailed_wind_unspecified_mwh)}</N> MWh.</> : null}</>} />
          </HeadlineRow>

          <ToolSection title="By hour of the day">
            <ChartFrame title={`California, ${label}`} legend={FUELS.map((f) => ({ label: f.label, color: f.color }))}
              note={<>Each bar is everything curtailed in that hour of the day over the period, in Pacific time. To 2025 from CAISO&apos;s five-minute record (MW over five minutes, as MWh); from 2026 from its daily report, which gives the hour by fuel.</>}>
              <HourChart r={r} label={label} />
            </ChartFrame>
          </ToolSection>

          <ToolSection title="By month" id="months" note={<>The months of the period chosen are drawn at full strength. A month is held when at least {Math.round(file.near * 100)} percent of its days are; its figure is the sum over the days held, never scaled up.</>}>
            <ChartFrame title={`Wind and solar curtailed, by month since ${file.first.slice(0, 4)}`} legend={FUELS.map((f) => ({ label: f.label, color: f.color }))}>
              <MonthChart by="fuel" period={period} />
            </ChartFrame>
          </ToolSection>

          <ToolSection title="By reason" id="reason"
            note={<>CAISO&apos;s two reasons. Local: turned down to relieve a congested line somewhere on the grid. System: turned down because the whole system had more supply than it could use or export. Its file gives a reason from 2022 (9,241 five-minute rows of 2022 have none), and nothing before.</>}>
            <ChartFrame title="By CAISO's reason, by month" legend={REASONS.map((x) => ({ label: x.label, color: x.color }))}>
              <MonthChart by="reason" period={period} />
            </ChartFrame>
            <ToolTable minWidth={620} caption={`California, ${label}: curtailment by fuel and by CAISO's reason, MWh`}
              head={["", "Local congestion", "System-wide oversupply", "No reason published", "All"]}
              rows={FUELS.map((f) => ({ key: f.key, cells: [f.label, ...REASONS.map((x) => <N key={x.key} k={`reason|${f.key}|${x.key}`}>{whole(r[`curtailed_${f.key}_${x.key}_mwh`] ?? 0)}</N>), <N key="all" k={`reason|${f.key}|all`}>{whole(r[`curtailed_${f.key}_mwh`])}</N>] }))} />
            {hasCats(r) ? (
              <div className="mt-6" data-cats="1">
                <ToolTable minWidth={620} caption={`California, ${label}: curtailment by CAISO's category, MWh`}
                  head={["From 2026, CAISO also says how", ...FUELS.map((f) => `${f.label}, MWh`)]}
                  rows={CATS.map((c) => ({ key: c.key, cells: [<span key="l">{c.label}<span className="block text-xs text-muted">{c.what}</span></span>, ...FUELS.map((f) => <N key={f.key} k={`cat|${f.key}|${c.key}`}>{whole(r[`curtailed_${f.key}_${c.key}_mwh`] ?? 0)}</N>)] }))} />
              </div>
            ) : null}
          </ToolSection>

          <ToolSection title="Against battery charging, in the same hours" id="batteries"
            note={<>CAISO&apos;s own battery output is held from late August 2025, so the comparison is by month from September 2025. Charging is what the batteries took in, as a positive number; an hour counts as a charging hour when they took in more than they gave back over the hour.
              Both are system totals: a battery charges where it stands, and a curtailment happens where it happens. That the two fall in the same hours does not say the batteries could have taken what was turned down.</>}>
            {br && battMonth ? (
              <>
                {period !== battMonth ? <p className="mb-3 max-w-3xl text-sm" data-battery-month={battMonth}>Shown for {periodName(battMonth)}, the newest month of {label} with the batteries. Other months: {bm.map((m, i) => <span key={m}>{i ? ", " : ""}<Link href={`${href(m)}#batteries`} className={item(m === battMonth)}>{m}</Link></span>)}.</p> : null}
                <HeadlineRow>
                  <HeadlineNumber label={`Curtailed, ${periodName(battMonth)}`} value={<N k="batt|curtailed">{whole(br.curtailed_mwh_battery_days)}</N>} unit="MWh" note={<>Wind and solar, over the <N k="batt|days">{whole(br.battery_days_held)}</N> days both tables hold.</>} />
                  <HeadlineNumber label="Taken in by the batteries" value={<N k="batt|charging">{whole(br.battery_charging_mwh)}</N>} unit="MWh" note={<>Over the same days, at every hour.</>} />
                  <HeadlineNumber label="Curtailed while they charged" value={br.curtailed_while_charging_share_pct !== undefined ? <N k="batt|while">{two(br.curtailed_while_charging_share_pct)}</N> : <span className="text-muted">not held</span>} unit="percent" note={<>Of the curtailed MWh, the share in hours in which the batteries were charging on balance.</>} />
                </HeadlineRow>
                <ChartFrame title={`The average day of ${periodName(battMonth)}, MW`} legend={[{ label: "Wind and solar curtailed", color: "var(--color-fuel-solar)" }, { label: "Battery charging", color: BATT }]}>
                  <BatteryChart r={br} label={periodName(battMonth)} />
                </ChartFrame>
              </>
            ) : <p className="border border-rule bg-paper px-3 py-2 text-sm" data-battery="none">Not held for {label}: CAISO&apos;s battery output is in the warehouse from late August 2025. Months with it: {bm.map((m, i) => <span key={m}>{i ? ", " : ""}<Link href={`${href(m)}#batteries`} className="text-ink">{m}</Link></span>)}.</p>}
          </ToolSection>

          <Fold title="What the data does not locate, or say">
            <ul className="max-w-3xl list-disc space-y-1 pl-5">
              <li>Where. One figure for the whole system: no plant, no node, no zone, and for a local curtailment not the line that was congested.</li>
              <li>The reason before 2022, and for part of 2022.</li>
              <li>The five-minute detail by fuel from 2026: CAISO&apos;s daily report gives wind and solar apart only by the hour.</li>
              <li>{file.days_not_held.length ? <>The day{file.days_not_held.length === 1 ? "" : "s"} {file.days_not_held.join(", ")}: the report could not be read whole, so the day is not held, and is not counted as a day with none.</> : <>Every day from {file.first_day} to {file.last_day} is held.</>}</li>
              <li>What was not built or not bid: curtailment is output turned down, not output that never had a place.</li>
              <li>The price. A curtailed hour is usually an hour of low or negative prices; <SiteLink href="/prices/compare">where power is cheap</SiteLink> has the hours below zero.</li>
              <li>The other grids: <SiteLink href="/curtailment">curtailment, every grid</SiteLink> has what each publishes.</li>
            </ul>
          </Fold>
          <Fold title="How it is computed">
            <p className="max-w-3xl">CAISO lists each five-minute interval with a curtailment, in MW; its energy is the MW over five minutes. From 2026 its daily report gives each hour&apos;s MWh by fuel and category. The intervals are added by hour of the day and by month in Pacific time; nothing is estimated or filled.
              Each day&apos;s total equals the daily table the site already had, for every day both hold. The full method: <SiteLink href={METHOD}>CAISO curtailment by interval</SiteLink>.</p>
          </Fold>
          <SourceLine tables={[TABLE, INPUT, "caiso_battery_storage"]}
            note={<>Data: California ISO, Production and curtailments data and the Daily Renewable Report (curtailment), and Today&apos;s Outlook (batteries). Credit: California ISO. Built {file.built.slice(0, 10)}. This page is in review and reads the site&apos;s own copy of the table.</>} />
        </div>
      </div>
    </ToolPage>
  );
}
