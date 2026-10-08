import type { Metadata } from "next";
import Link from "next/link";
import { SiteLink } from "@/components/SiteLink";
import { ChartFrame, Fold, HeadlineNumber, HeadlineRow, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import fileJson from "@/data/demand_growth.json";
import { caisoJoinDay } from "@/lib/caisoJoin";
import {
  RANKS, TABLE, byHour, byMonth, cells, choices, extremes, hourName, href, localHour, monthName, ranking, signed, slugOf, two, whole, wholeYears, yearToDate,
  type Area, type DemandFile,
} from "@/lib/demandgrowth";

// Session 97: "Demand growth", in review (lib/release.ts), in the battery page's layout: for the seven ISO balancing
// authorities and the Lower 48, annual average and peak demand and their growth since 2019; where the growth
// concentrates by month and by hour of the day; a ranking; a sentence. Weather is not removed, and the page says so
// above everything else. Every number is a row of eia930_demand_growth (warehouse/derived/demand_growth.py;
// docs/methods/demand_growth.md), read from the site's own copy (data/demand_growth.json).
export const metadata: Metadata = { title: "Demand growth", robots: { index: false, follow: false } };

const file = fileJson as unknown as DemandFile;
const METHOD = "/data/methods/demand_growth";
const N = ({ k, children }: { k: string; children: string }) => <span data-n={k}>{children}</span>;
const NOT = <span className="text-muted">not held</span>;
const UP = "var(--color-accent)", DOWN = "var(--color-down)";

/** Average demand by year as bars, the peak as a mark above each. */
function YearsChart({ area }: { area: Area }) {
  const W = 760, H = 300, L = 70, R = 12, top = 18, bot = 30;
  const ys = wholeYears(area);
  const hasPeak = ys.some((y) => y.row.peak_demand_mw !== undefined);
  const hi = Math.max(...ys.map((y) => y.row.peak_demand_mw ?? y.row.avg_demand_mw)) * 1.08;
  const step = [1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000].find((s) => hi / s <= 6) ?? 200000;
  const bw = (W - L - R) / ys.length;
  const y = (v: number) => top + ((hi - v) / hi) * (H - top - bot);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" data-chart="years" aria-label={`${area.name}: average demand by year${hasPeak ? " and the year's peak hour" : ""}, MW`}>
      {Array.from({ length: Math.floor(hi / step) + 1 }, (_, i) => i * step).map((t) => (
        <g key={t}>
          <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke="var(--color-rule)" strokeWidth={t === 0 ? 1.5 : 0.75} />
          <text x={L - 6} y={y(t) + 4} textAnchor="end" fontSize="11" fill="var(--color-muted)">{t.toLocaleString("en-US")}</text>
        </g>
      ))}
      {ys.map((d, i) => (
        <g key={d.year} data-year={d.year}>
          <rect x={L + i * bw + bw * 0.18} y={y(d.row.avg_demand_mw)} width={bw * 0.64} height={y(0) - y(d.row.avg_demand_mw)} fill="var(--color-accent)"><title>{`${d.year}: average ${whole(d.row.avg_demand_mw)} MW`}</title></rect>
          {d.row.peak_demand_mw !== undefined ? <line x1={L + i * bw + bw * 0.1} x2={L + (i + 1) * bw - bw * 0.1} y1={y(d.row.peak_demand_mw)} y2={y(d.row.peak_demand_mw)} stroke="var(--color-ink)" strokeWidth="2.5"><title>{`${d.year}: peak ${whole(d.row.peak_demand_mw)} MW`}</title></line> : null}
          <text x={L + (i + 0.5) * bw} y={H - 10} textAnchor="middle" fontSize="11" fill="var(--color-muted)">{d.year}</text>
        </g>
      ))}
      <text x={L} y={11} fontSize="11" fill="var(--color-muted)">MW</text>
    </svg>
  );
}

/** Where growth concentrates: a cell per month and hour of the day, shaded by the percent change since the base year. */
function Heat({ area }: { area: Area }) {
  const cs = cells(file, area);
  if (!cs.length) return <p className="border border-rule bg-paper px-3 py-2 text-sm">Not held: the table has no month-and-hour cell for {area.name} in both {file.base} and {file.last_year}.</p>;
  const W = 760, L = 84, R = 8, top = 22, ch = 20;
  const cw = (W - L - R) / 24;
  const H = top + 12 * ch + 6;
  const max = Math.max(...cs.map((c) => Math.abs(c.pct)));
  const at = new Map(cs.map((c) => [`${c.month}|${c.hour}`, c]));
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" data-chart="heat" data-cells={cs.length} aria-label={`${area.name}: change in average demand from ${file.base} to ${file.last_year}, by month and local hour of the day, percent`}>
      {[0, 3, 6, 9, 12, 15, 18, 21].map((h) => <text key={h} x={L + (h + 0.5) * cw} y={14} textAnchor="middle" fontSize="11" fill="var(--color-muted)">{hourName(h)}</text>)}
      {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
        <g key={m}>
          <text x={L - 8} y={top + (m - 1) * ch + 14} textAnchor="end" fontSize="11" fill="var(--color-ink)">{monthName(m)}</text>
          {Array.from({ length: 24 }, (_, h) => {
            const c = at.get(`${m}|${h}`);
            return c
              ? <rect key={h} x={L + h * cw} y={top + (m - 1) * ch} width={cw - 1} height={ch - 1} fill={c.pct >= 0 ? UP : DOWN} fillOpacity={0.08 + 0.92 * (Math.abs(c.pct) / max)} data-cell={`${m}|${h}`}><title>{`${monthName(m)}, ${hourName(h)}: ${signed(c.pct)} percent, ${c.mw > 0 ? "+" : ""}${whole(c.mw)} MW`}</title></rect>
              : <rect key={h} x={L + h * cw} y={top + (m - 1) * ch} width={cw - 1} height={ch - 1} fill="none" stroke="var(--color-rule)"><title>{`${monthName(m)}, ${hourName(h)}: not held`}</title></rect>;
          })}
        </g>
      ))}
    </svg>
  );
}

/** The change since the base year by month or by hour: a bar each, percent. */
function ChangeBars({ items, what }: { items: { label: string; pct: number | undefined }[]; what: string }) {
  const W = 760, H = 200, L = 46, R = 8, top = 14, bot = 28;
  const vals = items.map((i) => i.pct ?? 0);
  const hi = Math.max(0, ...vals) * 1.1 || 1, lo = Math.min(0, ...vals) * 1.1;
  const bw = (W - L - R) / items.length;
  const y = (v: number) => top + ((hi - v) / (hi - lo)) * (H - top - bot);
  const step = [1, 2, 5, 10, 20].find((s) => (hi - lo) / s <= 6) ?? 20;
  const ticks: number[] = [];
  for (let t = Math.ceil(lo / step) * step; t <= hi; t += step) ticks.push(t);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" data-chart={what} aria-label={`Change in average demand from ${file.base} to ${file.last_year}, ${what}, percent`}>
      {ticks.map((t) => (
        <g key={t}>
          <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke="var(--color-rule)" strokeWidth={t === 0 ? 1.5 : 0.75} />
          <text x={L - 6} y={y(t) + 4} textAnchor="end" fontSize="11" fill="var(--color-muted)">{t}</text>
        </g>
      ))}
      {items.map((it, i) => (
        <g key={it.label}>
          {it.pct !== undefined ? <rect x={L + i * bw + bw * 0.15} y={Math.min(y(0), y(it.pct))} width={bw * 0.7} height={Math.max(1, Math.abs(y(it.pct) - y(0)))} fill={it.pct >= 0 ? UP : DOWN}><title>{`${it.label}: ${signed(it.pct)} percent`}</title></rect> : null}
          {items.length <= 12 || i % 3 === 0 ? <text x={L + (i + 0.5) * bw} y={H - 10} textAnchor="middle" fontSize="11" fill="var(--color-muted)">{items.length <= 12 ? it.label.slice(0, 3) : it.label}</text> : null}
        </g>
      ))}
      <text x={L} y={10} fontSize="11" fill="var(--color-muted)">percent</text>
    </svg>
  );
}

export default async function Demand({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const q = Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined]));
  const { ba, rank } = choices(q);
  const area = file.areas[ba];
  const slug = slugOf(ba);
  const ys = wholeYears(area);
  const first = ys[0], last = ys[ys.length - 1];
  const ytd = yearToDate(file, area);
  const ex = extremes(cells(file, area));
  const ranked = ranking(file, rank);
  const item = (on: boolean) => `no-underline ${on ? "font-semibold text-accent" : "text-ink hover:text-accent"}`;
  const g = (v: number | undefined, k: string) => (v === undefined ? NOT : <N k={k}>{signed(v)}</N>);
  /** A growth figure of a year's row: the base year has none, and says so. */
  const gy = (year: string, v: number | undefined, k: string) => (v === undefined && Number(year) === file.base ? <span className="text-muted">the base year</span> : g(v, k));
  const through = monthName(Number(file.ytd_through.slice(5)));
  const earlier = file.caiso_break.rows.slice(1).map((r) => r.ratio);
  const inside = file.caiso_break.rows.length > 1 && file.caiso_break.rows[0].ratio >= Math.min(...earlier) && file.caiso_break.rows[0].ratio <= Math.max(...earlier);
  const peakAt = (y: string, k = "peak_demand_mw") => (area.at[y]?.[k] ? localHour(area.at[y][k], area.tz) : null);

  return (
    <ToolPage>
      <ToolHeader title="Demand growth"
        lead={<>How much more power each grid uses than it did in {file.base}: the average over the year, the highest hour of the year, and in which months and hours of the day the growth sits. The seven grid operators and the Lower 48, from EIA&apos;s hourly record.
          See also <SiteLink href="/queues">the interconnection queue</SiteLink> and <SiteLink href="/prices/compare">where power is cheap</SiteLink>.</>} />
      <p className="mb-8 max-w-3xl border-l-2 border-accent bg-paper px-3 py-2 text-sm" data-weather="1">
        <span className="font-semibold">Weather is not removed.</span> A year&apos;s demand is what was metered that year, hot summer and cold snap included. A grid whose {file.last_year} was mild shows less growth than its customers added, and a single heat wave can set a peak.
        These are differences between years, not a trend line.
      </p>
      <div className="grid gap-8 lg:grid-cols-[240px_minmax(0,1fr)]">
        <aside>
          <InputPanel title="Choose" note={<>Whole years {first.year} to {last.year}. The year so far is January to {through} of each year, so {Number(last.year) + 1} is compared with the same months of {file.base}.</>}>
            <nav aria-label="Area" className="mb-4 text-sm">
              <div className="mb-1 text-xs uppercase tracking-wide text-muted">Grid</div>
              {file.order.map((b) => <div key={b}><Link href={href(slugOf(b), rank.slug)} aria-current={b === ba ? "true" : undefined} className={item(b === ba)}>{file.areas[b].name}</Link></div>)}
            </nav>
            <nav aria-label="Ranking" className="text-sm">
              <div className="mb-1 text-xs uppercase tracking-wide text-muted">Rank the grids by growth in</div>
              {RANKS.map((r) => <div key={r.slug}><Link href={`${href(slug, r.slug)}#ranking`} aria-current={r.slug === rank.slug ? "true" : undefined} className={item(r.slug === rank.slug)}>{r.name}</Link></div>)}
            </nav>
          </InputPanel>
        </aside>

        <div className="min-w-0">
          <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-summary="1">
            From {first.year} to {last.year}, {area.name}&apos;s average demand went from <N k="sum|avg0">{whole(first.row.avg_demand_mw)}</N> MW to <N k="sum|avg1">{whole(last.row.avg_demand_mw)}</N> MW, a change of <N k="sum|avg_growth">{signed(last.row.avg_demand_growth_since_2019_pct)}</N> percent
            {last.row.peak_demand_mw !== undefined ? <>, and its highest hour from <N k="sum|peak0">{whole(first.row.peak_demand_mw)}</N> MW to <N k="sum|peak1">{whole(last.row.peak_demand_mw)}</N> MW (<N k="sum|peak_growth">{signed(last.row.peak_demand_growth_since_2019_pct)}</N> percent)</> : null}.{" "}
            {ytd ? <>January to {through} of {ytd.year} ran <N k="sum|ytd_growth">{signed(ytd.row.ytd_avg_demand_growth_since_2019_pct)}</N> percent against the same months of {file.base}.</> : null}{" "}
            {ex ? <>The growth is largest in {monthName(ex.most.month)} at {hourName(ex.most.hour)} (<N k="sum|cell_most">{signed(ex.most.pct)}</N> percent).</> : null} Weather is not removed.
          </p>
          <HeadlineRow>
            <HeadlineNumber label={`Average demand, ${first.year} to ${last.year}`} value={<N k="head|avg_growth">{signed(last.row.avg_demand_growth_since_2019_pct)}</N>} unit="percent"
              note={<><N k="head|avg0">{whole(first.row.avg_demand_mw)}</N> MW to <N k="head|avg1">{whole(last.row.avg_demand_mw)}</N> MW, the mean of the year&apos;s hours.</>} />
            <HeadlineNumber label="Peak demand" value={g(last.row.peak_demand_growth_since_2019_pct, "head|peak_growth")} unit={last.row.peak_demand_mw !== undefined ? "percent" : undefined}
              note={last.row.peak_demand_mw !== undefined
                ? <><N k="head|peak1">{whole(last.row.peak_demand_mw)}</N> MW on {peakAt(last.year)}, against <N k="head|peak0">{whole(first.row.peak_demand_mw)}</N> MW on {peakAt(first.year)}.</>
                : <>No peak is given for the Lower 48: its total holds its members&apos; faulty hours, and one of them would be the peak.</>} />
            <HeadlineNumber label={ytd ? `${ytd.year} so far, against ${file.base}` : "The year so far"} value={ytd ? <N k="head|ytd_growth">{signed(ytd.row.ytd_avg_demand_growth_since_2019_pct)}</N> : NOT} unit={ytd ? "percent" : undefined}
              note={ytd ? <>January to {through}: <N k="head|ytd1">{whole(ytd.row.ytd_avg_demand_mw)}</N> MW on average, against <N k="head|ytd0">{whole(ytd.base.ytd_avg_demand_mw)}</N> MW in the same months of {file.base}.</> : null} />
          </HeadlineRow>

          <ToolSection title="Year by year">
            <ChartFrame title={`${area.name}: demand, MW`} legend={[{ label: "Average over the year", color: "var(--color-accent)" }, ...(last.row.peak_demand_mw !== undefined ? [{ label: "The year's highest hour", color: "var(--color-ink)" }] : [])]}>
              <YearsChart area={area} />
            </ChartFrame>
            <ToolTable minWidth={760} caption={`${area.name}: average and peak demand by year`}
              head={["Year", "Average, MW", `Since ${file.base}, percent`, "On the year before, percent", "Peak, MW", "When, local time", `Peak since ${file.base}, percent`, "Hours used"]}
              rows={[...ys.map(({ year, row }) => ({ key: year, cells: [year, <N key="a" k={`y|${year}|avg`}>{whole(row.avg_demand_mw)}</N>, gy(year, row.avg_demand_growth_since_2019_pct, `y|${year}|avg_growth`), gy(year, row.avg_demand_growth_yoy_pct, `y|${year}|yoy`),
                row.peak_demand_mw !== undefined ? <N key="p" k={`y|${year}|peak`}>{whole(row.peak_demand_mw)}</N> : NOT, peakAt(year) ?? NOT, gy(year, row.peak_demand_growth_since_2019_pct, `y|${year}|peak_growth`),
                <span key="h"><N k={`y|${year}|hours`}>{whole(row.hours_used)}</N> of {whole(row.hours_in_year)}</span>] })),
              ...(ytd ? [{ key: "ytd", highlight: true, cells: [`${ytd.year}, to ${through}`, <N key="a" k="ytd|avg">{whole(ytd.row.ytd_avg_demand_mw)}</N>, g(ytd.row.ytd_avg_demand_growth_since_2019_pct, "ytd|avg_growth"), <span key="n" className="text-muted">same months</span>,
                ytd.row.ytd_peak_demand_mw !== undefined ? <N key="p" k="ytd|peak">{whole(ytd.row.ytd_peak_demand_mw)}</N> : NOT, peakAt(ytd.year, "ytd_peak_demand_mw") ?? NOT, g(ytd.row.ytd_peak_demand_growth_since_2019_pct, "ytd|peak_growth"),
                <span key="h"><N k="ytd|hours">{whole(ytd.row.ytd_hours_used)}</N> of {whole(ytd.row.ytd_hours_in_window)}</span>] }] : [])]} />
            <p className="mt-2 max-w-3xl text-xs text-muted">The last row compares January to {through} of {ytd?.year ?? "the newest year"} with January to {through} of {file.base}: its growth is against those months, not against the whole of {file.base}.</p>
          </ToolSection>

          <ToolSection title="Where the growth is" id="where"
            note={<>Each cell is one hour of the day in one month: the average demand of that hour over the month in {file.last_year}, against the same in {file.base}. Red is growth, green a fall; the deeper, the larger. One hot or mild month colors a whole row, which is the weather and not a trend. Hover for the figures.</>}>
            <ChartFrame title={`${area.name}: change from ${file.base} to ${file.last_year}, percent, by month and hour of the day`} legend={[{ label: "Growth", color: UP }, { label: "Fall", color: DOWN }]}>
              <Heat area={area} />
            </ChartFrame>
            {ex ? <p className="mb-6 max-w-3xl text-sm" data-extremes="1">Largest: {monthName(ex.most.month)} at {hourName(ex.most.hour)}, <N k="cell|most|pct">{signed(ex.most.pct)}</N> percent (<N k="cell|most|mw">{whole(ex.most.mw)}</N> MW). Smallest: {monthName(ex.least.month)} at {hourName(ex.least.hour)}, <N k="cell|least|pct">{signed(ex.least.pct)}</N> percent (<N k="cell|least|mw">{whole(ex.least.mw)}</N> MW).</p> : null}
            <div className="grid gap-x-6 xl:grid-cols-2">
              <ChartFrame title="By month"><ChangeBars items={byMonth(file, area).map((m) => ({ label: monthName(m.month), pct: m.pct }))} what="by month" /></ChartFrame>
              <ChartFrame title="By hour of the day"><ChangeBars items={byHour(file, area).map((h) => ({ label: hourName(h.hour), pct: h.pct }))} what="by hour" /></ChartFrame>
            </div>
          </ToolSection>

          <ToolSection title={`The ranking: growth in ${rank.name.toLowerCase()}`} id="ranking"
            note={<>Percent change since {file.base}: average and peak demand to {file.last_year}; the year so far is January to {through} against the same months of {file.base}. The Lower 48 is the total, not a grid among the seven.</>}>
            <ToolTable minWidth={620} caption={`The grids ranked by growth in ${rank.name.toLowerCase()} since ${file.base}`}
              head={["", "Grid", ...RANKS.map((r) => <Link key={r.slug} href={`${href(slug, r.slug)}#ranking`} className="underline" style={{ color: "var(--color-surface)" }} data-rank={r.slug}>{r.name}{r.slug === rank.slug ? " ↓" : ""}</Link>)]}
              rows={ranked.map((r, i) => ({ key: r.ba, highlight: r.ba === ba, muted: r.ba === "US48", cells: [r.ba === "US48" ? "" : String(ranked.filter((x) => x.ba !== "US48").findIndex((x) => x.ba === r.ba) + 1), <Link key="l" href={href(slugOf(r.ba), rank.slug)} className="text-ink" data-ranked={`${i}|${r.ba}`}>{r.name}</Link>,
                g(r.avg, `rank|${r.ba}|avg`), g(r.peak, `rank|${r.ba}|peak`), g(r.ytd, `rank|${r.ba}|ytd`)] }))} />
          </ToolSection>

          {ba === "CISO" ? (
            <ToolSection title="California across the break of December 2025" id="break"
              note={<>EIA&apos;s generation series for California changed on {caisoJoinDay()}; this page uses demand, which is a different series. The check: the average demand of the 28 days before that date and of the 28 days from it, in 2025 and on the same dates of every earlier year. A step in the series would show as a ratio outside the earlier years&apos; range.</>}>
              <ToolTable minWidth={520} caption="California's demand in the 28 days before and after the date of the break, by year"
                head={["Year", "28 days before, MW", "28 days from the date, MW", "The second over the first"]}
                rows={file.caiso_break.rows.map((r) => ({ key: String(r.year), highlight: r.year === file.caiso_break.rows[0].year, cells: [String(r.year), <N key="b" k={`break|${r.year}|before`}>{whole(r.before_mw)}</N>, <N key="a" k={`break|${r.year}|after`}>{whole(r.after_mw)}</N>, <N key="r" k={`break|${r.year}|ratio`}>{r.ratio.toFixed(4)}</N>] }))} />
              <p className="mt-3 max-w-3xl text-sm" data-break="1">In {file.caiso_break.rows[0].year} the ratio is {file.caiso_break.rows[0].ratio.toFixed(4)}; in the six earlier years it runs from {Math.min(...file.caiso_break.rows.slice(1).map((r) => r.ratio)).toFixed(4)} to {Math.max(...file.caiso_break.rows.slice(1).map((r) => r.ratio)).toFixed(4)}.
                {inside ? <>California&apos;s demand does not step at the break.</> : <>That is outside the earlier years&apos; range: read California&apos;s growth across that date with care.</>} Its hours of November 2023 to early December 2025, which EIA dates one hour late, are set back before anything is computed.</p>
            </ToolSection>
          ) : null}

          <Fold title="How it is computed">
            <p className="max-w-3xl">From EIA-930&apos;s hourly demand. An hour is used when its demand is above zero and within {Math.round(file.jump * 100)} percent of the median of the four hours around it: EIA&apos;s file holds faulty hours (for {area.name}, {whole(area.screened.jumps)} that stand apart from their neighbours and {whole(area.screened.not_positive)} at or below zero, with {whole(area.screened.blank)} blank), and a faulty high hour would otherwise be a year&apos;s peak.
              A year is written when at least {Math.round(file.near_year * 100)} percent of its hours are used; its average is the mean of those hours. Nothing is filled. The full method: <SiteLink href={METHOD}>demand growth</SiteLink>.</p>
          </Fold>
          <Fold title="What is not here">
            <ul className="max-w-3xl list-disc space-y-1 pl-5">
              <li>A weather adjustment. Nothing is normalized to a typical year.</li>
              <li>The larger balancing authorities outside the seven grid operators (the Tennessee Valley Authority, Southern Company, Bonneville, Duke, Florida Power and Light and others): the warehouse does not hold their hourly demand since {file.base}. It is the same public EIA record and can be added by a pull.</li>
              <li>Who is using the power: data centers, industry, electrification and population are not told apart in a grid&apos;s demand.</li>
              <li>Demand served behind the meter. Rooftop solar lowers the demand a grid sees at midday, so a falling cell there can be more solar and not less use.</li>
              <li>The instant peak. An hour&apos;s figure is the average over the hour; an operator&apos;s own record peak is a few minutes and reads a little higher.</li>
              <li>A forecast.</li>
            </ul>
          </Fold>
          <SourceLine tables={[TABLE]} note={<>Derived from EIA Form EIA-930, hourly demand (public domain); built {file.built.slice(0, 10)}. This page is in review and reads the site&apos;s own copy of the table.</>} />
        </div>
      </div>
    </ToolPage>
  );
}
