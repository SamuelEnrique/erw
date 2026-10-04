import type { Metadata } from "next";
import Link from "next/link";
import { SiteLink } from "@/components/SiteLink";
import { ChartFrame, Fold, HeadlineNumber, HeadlineRow, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { caisoJoinDay } from "@/lib/caisoJoin";
import {
  GRIDS, PROFILE, RECORDS, RECORD_ROWS, SOURCES, acrossYears, calName, choices, highest, hourName, href, localHour, missingMonths, periodName, periodOf,
  recordOf, shares, sideName, sourcesIn, stack, two, whole, type DuckYear, type GridFile, type Period,
} from "@/lib/mix2";
import { FILES } from "./data";

// Session 94: "The energy mix", version 2, in review (lib/release.ts), in the battery page's layout: a panel of choices
// on the left, a sentence, the headline numbers, then the charts. Any of the seven grids, any month or year since 2019:
// generation by fuel by hour as a stack (the average day of the period); a second grid beside it; one calendar month
// across the years, where the midday dip of net load deepens as solar grows; and the records with their dates. Every
// number is a row of generation_mix_hourly_profile or generation_mix_records (warehouse/derived/mix_profile.py;
// docs/methods/generation_mix_hourly.md), read from the site's own copy (app/mix/v2/data.ts); the only arithmetic on
// the page is net load, demand less wind and solar. The page /mix is as it was. The panel's links are plain next/link:
// they point at this same page.
export const metadata: Metadata = { title: "The energy mix, version 2", robots: { index: false, follow: false } };

const METHOD = "/data/methods/generation_mix_hourly";
const INK = "var(--color-ink)";
/** A year's line in the view across years: from the rule grey of the first year to the accent of the last. */
const yearColor = (i: number, n: number) => (n <= 1 ? "var(--color-accent)" : `color-mix(in srgb, var(--color-accent) ${Math.round(12 + (88 * i) / (n - 1))}%, var(--color-rule))`);

function scale(lo: number, hi: number) {
  const span = hi - lo || 1;
  const step = [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000].find((s) => span / s <= 6) ?? 50000;
  const ticks: number[] = [];
  for (let t = Math.ceil(lo / step) * step; t <= hi; t += step) ticks.push(t);
  return ticks;
}
const HOURS = [0, 3, 6, 9, 12, 15, 18, 21];

/** Generation by fuel by hour: the average day of a period as a stack, with demand as a line. */
function StackChart({ p, name, label }: { p: Period; name: string; label: string }) {
  const W = 760, H = 320, L = 62, R = 12, top = 16, bot = 34;
  const st = stack(p);
  const demand = p.avg.demand ?? [];
  const hi = Math.max(st.hi, ...demand.map((v) => v ?? 0)) * 1.06, lo = st.lo * 1.06;
  const x = (h: number) => L + ((h + 0.5) / 24) * (W - L - R);
  const y = (v: number) => top + ((hi - v) / (hi - lo)) * (H - top - bot);
  const area = (upper: number[], lower: number[]) => `${upper.map((v, h) => `${h ? "L" : "M"}${x(h).toFixed(1)},${y(v).toFixed(1)}`).join(" ")} ${[...lower].map((v, h) => [v, h] as const).reverse().map(([v, h]) => `L${x(h).toFixed(1)},${y(v).toFixed(1)}`).join(" ")} Z`;
  const list = (key: string) => (p.avg[key] ?? []).map((v, h) => `${hourName(h)} ${v == null ? "not held" : whole(v)}`).join(", ");
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" data-stack={name} aria-label={`${name}, ${label}: average MW by local hour, by source`}>
      {scale(lo, hi).map((t) => (
        <g key={t}>
          <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke="var(--color-rule)" strokeWidth={t === 0 ? 1.5 : 0.75} />
          <text x={L - 6} y={y(t) + 4} textAnchor="end" fontSize="11" fill="var(--color-muted)">{t.toLocaleString("en-US")}</text>
        </g>
      ))}
      {[...st.up, ...st.down].map((b, i) => (
        <path key={`${b.key}${i}`} d={area(b.upper, b.lower)} fill={b.color} fillOpacity="0.88" stroke="#fff" strokeWidth="0.5" data-band={b.key}>
          <title>{`${b.label}, MW: ${list(b.key)}`}</title>
        </path>
      ))}
      {demand.some((v) => v != null) ? (
        <path d={demand.map((v, h) => (v == null ? "" : `${h && demand[h - 1] != null ? "L" : "M"}${x(h).toFixed(1)},${y(v).toFixed(1)}`)).join(" ")} fill="none" stroke={INK} strokeWidth="2" data-line="demand">
          <title>{`Demand, MW: ${list("demand")}`}</title>
        </path>
      ) : null}
      {HOURS.map((h) => <text key={h} x={x(h)} y={H - bot + 16} textAnchor="middle" fontSize="11" fill="var(--color-muted)">{hourName(h)}</text>)}
      <text x={L} y={11} fontSize="11" fill="var(--color-muted)">MW, local time</text>
    </svg>
  );
}

/** One calendar month across the years: a line per year, by local hour. */
function YearLines({ years, pick, name, what }: { years: DuckYear[]; pick: (d: DuckYear) => (number | null)[]; name: string; what: string }) {
  const W = 760, H = 280, L = 62, R = 12, top = 16, bot = 34;
  const all = years.flatMap((d) => pick(d).filter((v): v is number => v != null));
  if (!all.length) return <p className="border border-rule bg-paper px-3 py-2 text-sm">Not held: {what}.</p>;
  const hi = Math.max(...all) * 1.05, lo = Math.min(0, ...all) * 1.05;
  const x = (h: number) => L + ((h + 0.5) / 24) * (W - L - R);
  const y = (v: number) => top + ((hi - v) / (hi - lo)) * (H - top - bot);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" data-years={what} aria-label={`${name}: ${what} by local hour, one line per year`}>
      {scale(lo, hi).map((t) => (
        <g key={t}>
          <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke="var(--color-rule)" strokeWidth={t === 0 ? 1.5 : 0.75} />
          <text x={L - 6} y={y(t) + 4} textAnchor="end" fontSize="11" fill="var(--color-muted)">{t.toLocaleString("en-US")}</text>
        </g>
      ))}
      {years.map((d, i) => {
        const v = pick(d);
        return (
          <path key={d.year} d={v.map((val, h) => (val == null ? "" : `${h && v[h - 1] != null ? "L" : "M"}${x(h).toFixed(1)},${y(val).toFixed(1)}`)).join(" ")}
            fill="none" stroke={yearColor(i, years.length)} strokeWidth={i === years.length - 1 ? 2.5 : 1.5} data-year={d.year}>
            <title>{`${d.year}, MW: ${v.map((val, h) => `${hourName(h)} ${val == null ? "not held" : whole(val)}`).join(", ")}`}</title>
          </path>
        );
      })}
      {HOURS.map((h) => <text key={h} x={x(h)} y={H - bot + 16} textAnchor="middle" fontSize="11" fill="var(--color-muted)">{hourName(h)}</text>)}
      <text x={L} y={11} fontSize="11" fill="var(--color-muted)">MW, local time</text>
    </svg>
  );
}

const N = ({ k, children }: { k: string; children: string }) => <span data-n={k}>{children}</span>;

function Records({ file, year }: { file: GridFile; year: string }) {
  const cell = (variable: string, period: string) => {
    const r = recordOf(file, variable, period);
    if (!r) return [<span key="v" className="text-muted">not held</span>, <span key="w" className="text-muted">not held</span>];
    return [<N key="v" k={`${file.grid}|${r.variable}|${r.period}`}>{two(r.value)}</N>,
      <span key="w">{localHour(r.ts_utc, file.tz)}{file.join ? <span className="text-muted"> ({r.side === "caiso" ? "CAISO's own data" : "EIA-930"})</span> : null}</span>];
  };
  return (
    <ToolTable minWidth={720} caption={`${file.name}: the records of an hour, since ${periodName(file.first)} and in ${year}`}
      head={["Record", "Unit", `Since ${file.first.slice(0, 4)}`, "When, local time", `In ${year}`, "When, local time"]}
      rows={RECORD_ROWS.map((row) => ({ key: row.variable, cells: [row.label, row.unit, ...cell(row.variable, "all"), ...cell(row.variable, year)] }))} />
  );
}

export default async function MixV2({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const q = Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined]));
  const c = choices(q, FILES);
  const file = FILES[c.grid], other = c.vs ? FILES[c.vs] : null;
  const grid = GRIDS.find((g) => g.slug === c.grid)!;
  const p = periodOf(file, c.period);
  const po = other ? periodOf(other, c.period) : null;
  const label = periodName(c.period);
  const item = (on: boolean) => `no-underline ${on ? "font-semibold text-accent" : "text-ink hover:text-accent"}`;
  const months = Object.keys(file.months).sort();
  const years = [...new Set(months.map((m) => m.slice(0, 4)))];
  const sh = p ? shares(p) : [];
  const solarPeak = p ? highest(p.avg.solar ?? []) : null;
  const windPeak = p ? highest(p.avg.wind ?? []) : null;
  const duck = acrossYears(file, c.cal);
  const duckOther = other ? acrossYears(other, c.cal) : [];
  const first = duck[0], last = duck[duck.length - 1];
  const year = c.period.slice(0, 4);
  const missing = missingMonths(file);
  const california = c.grid === "caiso" || c.vs === "caiso";
  const texas = c.grid === "ercot" || c.vs === "ercot";
  const joinMonth = caisoJoinDay().split(" ").slice(1).join(" ");  // "December 2025", from the one constant
  const legend = (pp: Period) => [...sourcesIn(pp).map((s) => ({ label: s.label, color: s.color })), { label: "Demand (line)", color: INK }];
  const share = (pp: Period | null, key: string) => (pp ? Number(pp[`${key}_share_pct`] ?? 0) : null);
  const days = (pp: Period) => (c.period.length === 7
    ? <>the mean of each hour over the month&apos;s {pp.days_held} complete days of {Number(pp.days_in_month)}</>
    : <>the mean of each hour over the complete days of {pp.months} of the year&apos;s {pp.months_due} months{pp.missing?.length ? ` (${pp.missing.map(periodName).join(", ")} not held)` : ""}, {pp.days_held} days</>);

  return (
    <ToolPage>
      <ToolHeader title="The energy mix"
        crumb={<>Version 2, in review. The page as it is today: <SiteLink href="/mix">the energy mix</SiteLink>.</>}
        lead={<>What generates the power, hour by hour. Choose a grid and a month or a year: the average day of that period as a stack of sources, a second
          grid beside it, the same calendar month across the years (where the midday dip that solar digs can be watched growing), and the records of an hour
          with their dates. Seven grids, from January 2019. See also <SiteLink href="/shoulder">the shoulder hours</SiteLink> and{" "}
          <SiteLink href="/cost-of-power/battery">what a battery earns</SiteLink>.</>} />
      <div className="grid gap-8 lg:grid-cols-[240px_minmax(0,1fr)]">
        <aside>
          <InputPanel title="Choose" note={<>Each month is the average of its complete days. A year is given when at most one of its months is missing. A month that is not listed is not held: see &quot;What is not held&quot; below.</>}>
            <nav aria-label="Grid" className="mb-4 text-sm">
              <div className="mb-1 text-xs uppercase tracking-wide text-muted">Grid</div>
              {GRIDS.map((g) => <div key={g.slug}><Link href={href({ grid: g.slug, period: periodOf(FILES[g.slug], c.period) ? c.period : undefined, vs: c.vs && c.vs !== g.slug ? c.vs : undefined })} aria-current={g.slug === c.grid ? "true" : undefined} className={item(g.slug === c.grid)}>{g.name}</Link></div>)}
            </nav>
            <nav aria-label="Beside it" className="mb-4 text-sm">
              <div className="mb-1 text-xs uppercase tracking-wide text-muted">Beside it</div>
              <div><Link href={href({ grid: c.grid, period: c.period })} aria-current={!c.vs ? "true" : undefined} className={item(!c.vs)}>No second grid</Link></div>
              {GRIDS.filter((g) => g.slug !== c.grid).map((g) => <div key={g.slug}><Link href={href({ grid: c.grid, period: c.period, vs: g.slug })} aria-current={g.slug === c.vs ? "true" : undefined} className={item(g.slug === c.vs)}>{g.name}</Link></div>)}
            </nav>
            <nav aria-label="Period" className="text-sm">
              <div className="mb-1 text-xs uppercase tracking-wide text-muted">Period: a year, or one of its months</div>
              {years.map((y) => (
                <div key={y} className="mb-1.5 flex flex-wrap items-baseline gap-x-1.5 gap-y-0.5">
                  {file.years[y]
                    ? <Link href={href({ grid: c.grid, period: y, vs: c.vs ?? undefined })} aria-current={c.period === y ? "true" : undefined} className={`w-9 text-xs ${item(c.period === y)}`}>{y}</Link>
                    : <span className="w-9 text-xs text-muted" title="too few of its months are held for a year">{y}</span>}
                  {months.filter((m) => m.startsWith(y)).map((m) => (
                    <Link key={m} href={href({ grid: c.grid, period: m, vs: c.vs ?? undefined })} aria-current={m === c.period ? "true" : undefined} className={`text-xs ${item(m === c.period)}`}>{m.slice(5)}</Link>
                  ))}
                </div>
              ))}
            </nav>
          </InputPanel>
        </aside>

        <div className="min-w-0">
          {!p ? (
            <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status"><span className="font-semibold">no data</span> for the energy mix: {PROFILE} holds no month for {grid.name}</p>
          ) : (
            <>
              <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-summary="1">
                In {label}, {sh[0].label.toLowerCase()} was the largest source of {grid.place}&apos;s power, at <N k="share|0">{two(sh[0].share)}</N> percent of what its sources generated,
                then {sh[1].label.toLowerCase()} at <N k="share|1">{two(sh[1].share)}</N> and {sh[2].label.toLowerCase()} at <N k="share|2">{two(sh[2].share)}</N>.{" "}
                {solarPeak && solarPeak.value > 0 ? <>On the average day solar peaked at <N k="solar|peak">{whole(solarPeak.value)}</N> MW at {hourName(solarPeak.hour)}.</> : <>EIA reports no solar output for it.</>}
              </p>
              <HeadlineRow>
                <HeadlineNumber label="Largest source" value={<N k="head|largest">{two(sh[0].share)}</N>} unit="percent"
                  note={<>{sh[0].label}: <N k="head|largest|mwh">{whole(sh[0].mwh)}</N> MWh over the days counted, of the sum of the sources.</>} />
                <HeadlineNumber label="Solar" value={<N k="head|solar">{two(share(p, "solar")!)}</N>} unit="percent"
                  note={solarPeak && solarPeak.value > 0 ? <>At its highest on the average day: <N k="head|solar|peak">{whole(solarPeak.value)}</N> MW at {hourName(solarPeak.hour)}.</> : <>No solar output is reported.</>} />
                <HeadlineNumber label="Wind" value={<N k="head|wind">{two(share(p, "wind")!)}</N>} unit="percent"
                  note={windPeak && windPeak.value > 0 ? <>At its highest on the average day: <N k="head|wind|peak">{whole(windPeak.value)}</N> MW at {hourName(windPeak.hour)}.</> : <>No wind output is reported.</>} />
              </HeadlineRow>

              {california ? (
                <p className="mb-6 max-w-3xl border-l-2 border-accent bg-paper px-3 py-1.5 text-xs" data-caiso-join="1">
                  California is read from two sources, joined and never blended: EIA-930 to {caisoJoinDay()}, when EIA&apos;s generation series for California changed, and CAISO&apos;s own supply by fuel from that day.
                  {joinMonth}, the month that holds the join, is not shown: a month is never built on both. Demand is EIA&apos;s throughout. {periodOf(FILES.caiso, c.period) ? <>The period shown rests on <span data-side={periodOf(FILES.caiso, c.period)!.side}>{sideName(periodOf(FILES.caiso, c.period)!.side)}</span>.</> : null}{" "}
                  <SiteLink href="/data/methods/eia930_caiso_break">The method note</SiteLink>.
                </p>
              ) : null}

              <ToolSection title="Generation by fuel, by hour">
                <div className={other ? "grid gap-x-6 xl:grid-cols-2" : ""} data-side-by-side={other ? "1" : "0"}>
                  <ChartFrame title={`${grid.name}, ${label}`} legend={legend(p)}
                    note={<>Each hour is {days(p)}. What is above zero is stacked up from zero; batteries charging are drawn below it. The line is demand.</>}>
                    <StackChart p={p} name={grid.name} label={label} />
                  </ChartFrame>
                  {other ? (po ? (
                    <ChartFrame title={`${other.name}, ${label}`} legend={legend(po)}
                      note={<>Each hour is {days(po)}. Each chart has its own scale: compare the shapes, and the shares in the table below.</>}>
                      <StackChart p={po} name={other.name} label={label} />
                    </ChartFrame>
                  ) : <p className="mb-10 border border-rule bg-paper px-3 py-2 text-sm" data-other="none">{other.name} does not hold {label}: it has too few complete days, or too few months for a year.</p>) : null}
                </div>
                <ToolTable minWidth={other ? 620 : 420} caption={`Shares of generation by source, ${label}`}
                  head={["Source", `${grid.name}, percent`, `${grid.name}, MWh`, ...(other ? [`${other.name}, percent`, `${other.name}, MWh`] : [])]}
                  rows={sh.map((s) => ({ key: s.key, cells: [
                    <span key="l" className="inline-flex items-center gap-1.5"><span aria-hidden="true" className="inline-block h-2.5 w-2.5" style={{ background: s.color }} />{s.label}</span>,
                    <N key="s" k={`${c.grid}|${s.key}_share_pct`}>{two(s.share)}</N>, <N key="m" k={`${c.grid}|${s.key}_mwh`}>{whole(s.mwh)}</N>,
                    ...(other ? (po ? [<N key="os" k={`${other.grid}|${s.key}_share_pct`}>{two(share(po, s.key)!)}</N>, <N key="om" k={`${other.grid}|${s.key}_mwh`}>{whole(Number(po[`${s.key}_mwh`] ?? 0))}</N>] : ["not held", "not held"]) : []),
                  ] }))} />
                <p className="mt-2 max-w-3xl text-xs text-muted">A share is of the sum of the sources over the days counted. Storage is negative when batteries took in more than they gave back, and it appears
                  as a source only from when EIA itemizes it (Texas from late 2024); before that EIA holds it inside &quot;other&quot; or not at all.</p>
              </ToolSection>

              <ToolSection title={`${calName(c.cal)}, year after year`} id="years"
                note={<>Net load is demand less wind and solar, hour by hour, on the average day of {calName(c.cal)} in each year; the midday low is its lowest hour from 09:00 to 16:00, the evening high its highest from 16:00, and the ramp the difference. As solar grows the low deepens and the ramp steepens: the shape called the duck curve.</>}>
                <nav aria-label="Calendar month" className="mb-3 flex flex-wrap gap-x-3 gap-y-1 text-sm">
                  {Array.from({ length: 12 }, (_, i) => String(i + 1).padStart(2, "0")).map((m) => (
                    <Link key={m} href={`${href({ grid: c.grid, period: c.period, vs: c.vs ?? undefined, cal: m })}#years`} aria-current={m === c.cal ? "true" : undefined} className={item(m === c.cal)}>{calName(m)}</Link>
                  ))}
                </nav>
                {duck.length === 0 ? <p className="border border-rule bg-paper px-3 py-2 text-sm">{grid.name} holds no {calName(c.cal)}.</p> : (
                  <>
                    <div className={other ? "grid gap-x-6 xl:grid-cols-2" : ""}>
                      <ChartFrame title={`${grid.name}: net load, ${calName(c.cal)}`} legend={duck.map((d, i) => ({ label: d.year, color: yearColor(i, duck.length) }))}>
                        <YearLines years={duck} pick={(d) => d.net} name={grid.name} what={`net load in ${calName(c.cal)}`} />
                      </ChartFrame>
                      {other && duckOther.length ? (
                        <ChartFrame title={`${other.name}: net load, ${calName(c.cal)}`} legend={duckOther.map((d, i) => ({ label: d.year, color: yearColor(i, duckOther.length) }))}>
                          <YearLines years={duckOther} pick={(d) => d.net} name={other.name} what={`net load in ${calName(c.cal)}`} />
                        </ChartFrame>
                      ) : null}
                    </div>
                    <ChartFrame title={`${grid.name}: solar, ${calName(c.cal)}`} legend={duck.map((d, i) => ({ label: d.year, color: yearColor(i, duck.length) }))}>
                      <YearLines years={duck} pick={(d) => d.solar} name={grid.name} what={`solar output in ${calName(c.cal)}`} />
                    </ChartFrame>
                    <ToolTable minWidth={720} caption={`${grid.name}, ${calName(c.cal)} by year: solar's peak, net load's midday low and evening high, and the ramp`}
                      head={["Year", "Solar at its peak, MW", "Net load's midday low, MW", "Net load's evening high, MW", "The ramp, MW", ...(file.join ? ["Read from"] : [])]}
                      rows={duck.map((d) => ({ key: d.year, highlight: d.month === c.period, cells: [
                        d.year,
                        d.solarPeak && d.solarPeak.value > 0 ? <><N k={`duck|${d.year}|solar`}>{whole(d.solarPeak.value)}</N> at {hourName(d.solarPeak.hour)}</> : "none reported",
                        d.low ? <><N k={`duck|${d.year}|low`}>{whole(d.low.value)}</N> at {hourName(d.low.hour)}</> : "not held",
                        d.evening ? <><N k={`duck|${d.year}|evening`}>{whole(d.evening.value)}</N> at {hourName(d.evening.hour)}</> : "not held",
                        d.ramp !== null ? <N k={`duck|${d.year}|ramp`}>{whole(d.ramp)}</N> : "not held",
                        ...(file.join ? [sideName(d.side)] : []),
                      ] }))} />
                    {first && last && first !== last && first.low && last.low && first.ramp !== null && last.ramp !== null ? (
                      <p className="mt-3 max-w-3xl text-sm" data-duck="1">
                        In {calName(c.cal)} {first.year} {grid.name}&apos;s net load fell to {whole(first.low.value)} MW at midday and climbed {whole(first.ramp)} MW to its evening high; in {calName(c.cal)} {last.year}, to {whole(last.low.value)} MW and {whole(last.ramp)} MW.
                      </p>
                    ) : null}
                  </>
                )}
              </ToolSection>

              <ToolSection title="The records of an hour" id="records"
                note={<>A share is of the hour&apos;s generation: the sum of what its sources put out, so batteries charging do not push a share above 100. The cleanest and the dirtiest hour are the lowest and the highest carbon intensity of generation. An hour is ranked only when EIA&apos;s own figures for it agree with each other: <SiteLink href={METHOD}>the method</SiteLink>.</>}>
                <h3 className="mb-2 text-sm font-semibold">{grid.name}</h3>
                <Records file={file} year={year} />
                {other ? <><h3 className="mb-2 mt-6 text-sm font-semibold">{other.name}</h3><Records file={other} year={year} /></> : null}
              </ToolSection>
            </>
          )}

          <Fold title="How it is computed">
            <p className="max-w-3xl">From EIA-930&apos;s hourly net generation by energy source for each grid operator, grouped into eight sources (natural gas, coal, nuclear, wind, solar, hydro, storage and other).
              An hour is used when its net generation is positive, its sources add up to that total within 5 percent (PJM: 15 percent, because PJM itemizes no storage and its sources and its total part by 5 to 15 percent in the early morning of most days from 2020 to 2024),
              and no main source is blank. A day is complete when every hour of the local day is used; a month is written when at least 90 percent of its days are complete, as the average of those days. Nothing is filled.
              A year is the average of its months, each weighted by its complete days. The full method: <SiteLink href={METHOD}>the energy mix by hour</SiteLink>.</p>
          </Fold>
          <Fold title="What is not held">
            <ul className="max-w-3xl list-disc space-y-1 pl-5" data-missing={missing.length}>
              <li>{missing.length === 0 ? <>{grid.name} holds every month from {periodName(file.first)} to {periodName(file.upto)}.</> : <>{grid.name} does not hold {missing.length} of the months from {periodName(file.first)} to {periodName(file.upto)}: {missing.map(periodName).join(", ")}. Fewer than 90 percent of their days are complete.</>}</li>
              {california ? <li>California from October 2019 to August 2020: EIA&apos;s file holds no hydro for those months and its total leaves it out too. A month built on them would show California without hydro, so they are not written.</li> : null}
              {california ? <li>California, {joinMonth}: the month of the join between EIA&apos;s data and CAISO&apos;s own.</li> : null}
              {texas ? <li>Texas, December 2025: from 6 to 14 December EIA&apos;s &quot;other&quot; repeats the batteries&apos; output and the sources stand 5 to 8 percent above the total.</li> : null}
              <li>Generation by plant or by zone, imports by source, and anything behind the meter (rooftop solar lowers demand here; it is not a source).</li>
              <li>The weather: a month&apos;s average day is that month&apos;s, hot or mild. Nothing is adjusted.</li>
            </ul>
          </Fold>
          <SourceLine tables={[PROFILE, RECORDS]}
            note={<>Both derived from EIA Form EIA-930 (public domain), and for California from {caisoJoinDay()} from CAISO&apos;s own supply by fuel; built {file.built.slice(0, 10)}. This page is in review and reads the site&apos;s own copy of the two tables.</>} />
        </div>
      </div>
    </ToolPage>
  );
}
