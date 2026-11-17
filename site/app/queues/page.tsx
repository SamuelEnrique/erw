import type { Metadata } from "next";
import Link from "next/link";
import { Brand } from "@/components/Brand";
import { SiteLink } from "@/components/SiteLink";
import { ChartFrame, Fold, HeadlineNumber, HeadlineRow, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import fileJson from "@/data/queues.json";
import { DecisionsBlock } from "@/components/tool/DecisionsBlock";
import { QUEUES_DECISIONS } from "@/lib/decisions";
import { GRIDS, TABLE, TECHS, choices, href, noneWithdrawn, onYears, outcome, peakActive, queueOf, two, viewOf, whole, withdrawnOf, yearsOf, type Grid, type QueueFile, type Tech, type View } from "@/lib/queues";
// Session 7545 (chain 304, part C: the read, docs/reviews/queues-read-2026-11-16.md): every grid for the chosen
// technology side by side (row 1), the one operation year written when it is the only one (row 2), the share withdrawn
// of a view the file labels no withdrawn request with said on the figure (row 3), each year entered as counts (row 5),
// the operators' own queue lists named (row 6), the load the file does not hold (row 7), and three words (rows 8 to 10).

// Session 95: "The interconnection queue", in review (lib/release.ts), in the battery page's layout: choose a grid and a
// technology; the capacity still active by the year it entered; what became of past requests (the share that reached
// operation, the share withdrawn); the median years from request to operation; and storage and solar with storage
// shown apart. Every number is a row of interconnection_queue_summary (warehouse/derived/queue_summary.py;
// docs/methods/interconnection_queue_summary.md), from Berkeley Lab and GridTracker's Queued Up data file (CC BY 4.0),
// read from the site's own copy (data/queues.json). The panel's links are plain next/link: they point at this page.
export const metadata: Metadata = { title: "The interconnection queue", robots: { index: false, follow: false } };

const file = fileJson as unknown as QueueFile;
const METHOD = "/data/methods/interconnection_queue_summary";
const COLOR = { operating: "var(--color-fuel-nuclear)", withdrawn: "var(--color-rule)", open: "var(--color-accent)", active: "var(--color-accent)", line: "var(--color-ink)" };
const N = ({ k, children }: { k: string; children: string }) => <span data-n={k}>{children}</span>;
const NOT = <span className="text-muted">not held</span>;
const DATELESS = "ISO-NE's requests that reached operation carry no operation date in the file, so ISO-NE has no wait to give, in any technology. Source: Lawrence Berkeley National Laboratory and GridTracker, Queued Up: 2026 Edition data file.";
/** "not held" for a median: for ISO-NE, why, on hover (row 10). */
const notMedian = (grid: string) => (grid === "isone" ? <span className="text-muted" title={DATELESS} data-dateless="isone">not held</span> : NOT);
/** Row 3: the hover on a share withdrawn of 0.00 that is the file's labels, not a count. */
function flatWords(grid: Grid, tech: Tech, allWithdrawn: number | null) {
  return `The file holds no withdrawn and no suspended ${tech.noun} in ${grid.place}, in any year${allWithdrawn !== null ? `, while ${whole(allWithdrawn)} of ${grid.place}'s requests of every technology with a year entered are withdrawn` : ""}. `
    + `So 0.00 percent is what the file's labels give, not a count of requests that stayed in the queue: the method note, "What the reader meets", says which labels. Source: Lawrence Berkeley National Laboratory and GridTracker, Queued Up: 2026 Edition data file.`;
}
/** A share cell; for a view the file labels no withdrawn request with, the share withdrawn carries row 3's hover. */
function Withdrawn({ v, k, grid, tech }: { v: View; k: string; grid: Grid; tech: Tech }) {
  const x = v.whole.past_withdrawn_share_pct;
  if (x === undefined) return NOT;
  if (!noneWithdrawn(v, file.min_share)) return <N k={k}>{two(x)}</N>;
  const all = viewOf(file, grid.slug, "all");
  return <span title={flatWords(grid, tech, all ? withdrawnOf(all) : null)} data-none-withdrawn={`${grid.slug}|${tech.slug}`} className="underline decoration-dotted"><N k={k}>{two(x)}</N></span>;
}

/** Active capacity by the year the request entered the queue: one bar per year, MW. */
function ActiveChart({ view, name }: { view: View; name: string }) {
  const W = 760, H = 280, L = 62, R = 12, top = 16, bot = 30;
  const ys = yearsOf(view, file.last_year).filter((y) => y.year >= 2000);
  const hi = Math.max(1, ...ys.map((y) => y.row?.mw_active ?? 0)) * 1.08;
  const step = [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000].find((s) => hi / s <= 6) ?? 200000;
  const bw = (W - L - R) / ys.length;
  const y = (v: number) => top + ((hi - v) / hi) * (H - top - bot);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" data-chart="active" aria-label={`${name}: capacity still active, by the year the request entered the queue, MW`}>
      {Array.from({ length: Math.floor(hi / step) + 1 }, (_, i) => i * step).map((t) => (
        <g key={t}>
          <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke="var(--color-rule)" strokeWidth={t === 0 ? 1.5 : 0.75} />
          <text x={L - 6} y={y(t) + 4} textAnchor="end" fontSize="11" fill="var(--color-muted)">{t.toLocaleString("en-US")}</text>
        </g>
      ))}
      {ys.map((d, i) => {
        const v = d.row?.mw_active ?? 0;
        return (
          <g key={d.year}>
            {v > 0 ? <rect x={L + i * bw + 1.5} y={y(v)} width={Math.max(1, bw - 3)} height={y(0) - y(v)} fill={COLOR.active} data-bar={d.year}>
              <title>{`Entered ${d.year}: ${whole(v)} MW still active, in ${whole(d.row!.requests_active)} requests`}</title>
            </rect> : null}
            {d.year % 5 === 0 ? <text x={L + (i + 0.5) * bw} y={H - 10} textAnchor="middle" fontSize="11" fill="var(--color-muted)">{d.year}</text> : null}
          </g>
        );
      })}
      <text x={L} y={11} fontSize="11" fill="var(--color-muted)">MW, by year entered</text>
    </svg>
  );
}

/** What became of each year's requests: the share operating, withdrawn and still open, of the requests entered that year. */
function OutcomeChart({ view, name }: { view: View; name: string }) {
  const W = 760, H = 240, L = 46, R = 12, top = 16, bot = 30;
  const ys = yearsOf(view, file.last_year).filter((y) => y.year >= 2000);
  const bw = (W - L - R) / ys.length;
  const y = (v: number) => top + (1 - v) * (H - top - bot);
  const [p0, p1] = file.past;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" data-chart="outcome" aria-label={`${name}: what became of the requests of each year entered, as shares of that year's requests`}>
      {(() => { const a = ys.findIndex((d) => d.year === p0), b = ys.findIndex((d) => d.year === p1); return a >= 0 && b >= a ? <rect x={L + a * bw} y={top - 6} width={(b - a + 1) * bw} height={3} fill="var(--color-ink)"><title>{`Past requests: entered ${p0} to ${p1}`}</title></rect> : null; })()}
      {[0, 0.25, 0.5, 0.75, 1].map((t) => (
        <g key={t}>
          <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke="var(--color-rule)" strokeWidth={t === 0 ? 1.5 : 0.75} />
          <text x={L - 6} y={y(t) + 4} textAnchor="end" fontSize="11" fill="var(--color-muted)">{t * 100}</text>
        </g>
      ))}
      {ys.map((d, i) => {
        const o = outcome(d.row);
        const x = L + i * bw + 1.5, w = Math.max(1, bw - 3);
        return (
          <g key={d.year}>
            {o ? (
              <g data-outcome={d.year}>
                <title>{`Entered ${d.year}, ${whole(o.n)} requests: ${whole(d.row!.requests_operating)} operating, ${whole(d.row!.requests_withdrawn)} withdrawn, ${whole(d.row!.requests_active + d.row!.requests_suspended)} still active or suspended`}</title>
                <rect x={x} y={y(o.operating)} width={w} height={y(0) - y(o.operating)} fill={COLOR.operating} />
                <rect x={x} y={y(o.operating + o.open)} width={w} height={y(o.operating) - y(o.operating + o.open)} fill={COLOR.open} />
                <rect x={x} y={y(1)} width={w} height={y(o.operating + o.open) - y(1)} fill={COLOR.withdrawn} />
              </g>
            ) : null}
            {d.year % 5 === 0 ? <text x={L + (i + 0.5) * bw} y={H - 10} textAnchor="middle" fontSize="11" fill="var(--color-muted)">{d.year}</text> : null}
          </g>
        );
      })}
      <text x={L} y={8} fontSize="11" fill="var(--color-muted)">percent of the year&apos;s requests</text>
    </svg>
  );
}

/** Median years from request to operation, by the year the request began operating. */
function YearsChart({ view, name }: { view: View; name: string }) {
  const W = 760, H = 220, L = 46, R = 12, top = 16, bot = 30;
  const pts = onYears(view).filter((p) => p.year >= 2000);
  // row 2: one year that holds a median is written out, not dropped with "no line"
  if (pts.length === 1) return <p className="border border-rule bg-paper px-3 py-2 text-sm" data-chart="years-one">Only one operation year holds {file.min_median} or more dated requests for {name}: those that began operating in {pts[0].year} took a median of <N k={`on|${pts[0].year}|on_median_years_to_operation`}>{two(pts[0].on_median_years_to_operation)}</N> years from request to operation, over <N k={`on|${pts[0].year}|on_requests_dated`}>{whole(pts[0].on_requests_dated)}</N> dated requests. One year draws no line.</p>;
  if (pts.length < 2) return <p className="border border-rule bg-paper px-3 py-2 text-sm" data-chart="years-none">No operation year holds {file.min_median} or more dated requests for {name}: no line is drawn.</p>;
  const y0 = pts[0].year, y1 = file.last_year;
  const hi = Math.max(...pts.map((p) => p.on_median_years_to_operation)) * 1.15;
  const x = (yr: number) => L + ((yr - y0 + 0.5) / (y1 - y0 + 1)) * (W - L - R);
  const y = (v: number) => top + ((hi - v) / hi) * (H - top - bot);
  const step = hi > 8 ? 2 : 1;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" data-chart="years" aria-label={`${name}: median years from request to operation, by the year operation began`}>
      {Array.from({ length: Math.floor(hi / step) + 1 }, (_, i) => i * step).map((t) => (
        <g key={t}>
          <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke="var(--color-rule)" strokeWidth={t === 0 ? 1.5 : 0.75} />
          <text x={L - 6} y={y(t) + 4} textAnchor="end" fontSize="11" fill="var(--color-muted)">{t}</text>
        </g>
      ))}
      <path d={pts.map((p, i) => `${i && pts[i - 1].year === p.year - 1 ? "L" : "M"}${x(p.year).toFixed(1)},${y(p.on_median_years_to_operation).toFixed(1)}`).join(" ")} fill="none" stroke={COLOR.line} strokeWidth="2" />
      {pts.map((p) => <circle key={p.year} cx={x(p.year)} cy={y(p.on_median_years_to_operation)} r="3" fill={COLOR.line} data-on={p.year}><title>{`Began operating in ${p.year}: median ${two(p.on_median_years_to_operation)} years from request, over ${whole(p.on_requests_dated)} dated requests`}</title></circle>)}
      {Array.from({ length: y1 - y0 + 1 }, (_, i) => y0 + i).filter((yr) => yr % 5 === 0).map((yr) => <text key={yr} x={x(yr)} y={H - 10} textAnchor="middle" fontSize="11" fill="var(--color-muted)">{yr}</text>)}
      <text x={L} y={11} fontSize="11" fill="var(--color-muted)">years, by year operation began</text>
    </svg>
  );
}

/** Row 5: each year entered as the table's counts, so a reader can set one year beside another page's count of it
 *  without reading a bar's hover. Every year of the view with a request, the years before 2000 too. */
function YearsTable({ view, name }: { view: View; name: string }) {
  const ys = Object.entries(view.years).map(([y, r]) => ({ y, r })).sort((a, b) => Number(a.y) - Number(b.y));
  const cols: (keyof View["years"][string])[] = ["requests_entered", "mw_entered", "requests_operating", "requests_withdrawn", "requests_active", "requests_suspended", "mw_active"];
  return (
    <div data-years-table="1">
      <ToolTable minWidth={760} caption={`${name}: every year entered, counted`}
        head={["Year entered", "Requests entered", "MW entered", "Reached operation", "Withdrawn", "Still active", "Suspended", "MW still active"]}
        rows={ys.map(({ y, r }) => ({ key: y, cells: [y, ...cols.map((c) => <N key={c} k={`year|${y}|${c}`}>{whole(r[c])}</N>)] }))} />
      <p className="mt-2 max-w-3xl text-sm">Each row is the requests that entered the queue that year, by their status at the end of {file.last_year}; a request with no year entered is in no row ({whole(view.whole.requests_without_year)} of this view&apos;s {whole(view.whole.total_requests)}). Requests, except the two MW columns. A request of unknown status is counted as entered and in no status.</p>
    </div>
  );
}

export default async function Queues({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const q = Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined]));
  const { grid, tech } = choices(q);
  const view = viewOf(file, grid.slug, tech.slug);
  const w = view?.whole;
  const name = `${grid.name}, ${tech.name.toLowerCase()}`;
  const item = (on: boolean) => `no-underline ${on ? "font-semibold text-accent" : "text-ink hover:text-accent"}`;
  const [p0, p1] = file.past;
  const peak = view ? peakActive(view) : null;
  const share = (v: number | undefined, k: string) => (v === undefined ? NOT : <N k={k}>{two(v)}</N>);
  const kinds = TECHS.filter((t) => t.slug !== "all").map((t) => ({ t, v: viewOf(file, grid.slug, t.slug) }));

  return (
    <Brand>
    <ToolPage>
      <ToolHeader title="The interconnection queue"
        lead={<>Before a power plant or a battery can connect to the grid it waits in a queue for a study and an agreement. Choose a grid and a technology: how much capacity is waiting and since when,
          what became of the requests of earlier years, and how long the ones that were built took. From Berkeley Lab and GridTracker&apos;s record of every request, through the end of {file.last_year}.
          See also <SiteLink href="/storage?tab=buildout">the storage build-out</SiteLink> and <SiteLink href="/map">the project map</SiteLink>.{" "}
          <span data-other-source="1">The grid operators&apos; own queue lists, as the ERW pulls them, are counted on <SiteLink href="/explore/interconnection">the interconnection queue explorer</SiteLink> and <SiteLink href="/map?tab=queues">the map&apos;s Queues tab</SiteLink>: another source, read on another day, so their count for a grid and an entry year is not this page&apos;s.</span></>} />
      <div className="grid gap-8 lg:grid-cols-[240px_minmax(0,1fr)]">
        <aside>
          <InputPanel title="Choose" note={<>Requests through the end of {file.last_year}. A request is counted once, under the operator whose queue holds it.</>}>
            <nav aria-label="Grid" className="mb-4 text-sm">
              <div className="mb-1 text-xs uppercase tracking-wide text-muted">Grid</div>
              {GRIDS.map((g) => <div key={g.slug}><Link href={href(g.slug, tech.slug)} aria-current={g.slug === grid.slug ? "true" : undefined} className={item(g.slug === grid.slug)}>{g.name}</Link></div>)}
            </nav>
            <nav aria-label="Technology" className="text-sm">
              <div className="mb-1 text-xs uppercase tracking-wide text-muted">Technology</div>
              {TECHS.map((t) => <div key={t.slug}><Link href={href(grid.slug, t.slug)} aria-current={t.slug === tech.slug ? "true" : undefined} className={item(t.slug === tech.slug)}>{t.name}</Link></div>)}
            </nav>
          </InputPanel>
        </aside>

        <div className="min-w-0">
          {!view || !w ? (
            <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status" data-empty="1"><span className="font-semibold">no data</span>: the file holds no {tech.noun} in {grid.place}.</p>
          ) : (
            <>
              <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-summary="1">
                At the end of {file.last_year}, <N k="total_active_requests">{whole(w.total_active_requests)}</N> {tech.noun} were active in {queueOf(grid)}, for <N k="total_active_mw">{whole(w.total_active_mw)}</N> MW.{" "}
                {w.past_operating_share_pct !== undefined
                  ? <>Of the <N k="past_requests">{whole(w.past_requests)}</N> that entered from {p0} to {p1}, <N k="past_operating_share_pct">{two(w.past_operating_share_pct)}</N> percent reached operation and <N k="past_withdrawn_share_pct">{two(w.past_withdrawn_share_pct!)}</N> percent were withdrawn.</>
                  : <>Only <N k="past_requests">{whole(w.past_requests)}</N> entered from {p0} to {p1}: too few for a share.</>}{" "}
                {w.median_years_to_operation !== undefined
                  ? <>Those that were built took a median of <N k="median_years_to_operation">{two(w.median_years_to_operation)}</N> years from request to operation.</>
                  : <>The file dates too few of those that were built to give a median wait.</>}
              </p>
              <HeadlineRow>
                <HeadlineNumber label="Active capacity" value={<N k="head|active_mw">{whole(w.total_active_mw)}</N>} unit="MW"
                  note={<><N k="head|active_requests">{whole(w.total_active_requests)}</N> {w.total_active_requests === 1 ? "request" : "requests"}. Suspended, and not counted here: <N k="head|suspended_requests">{whole(w.total_suspended_requests)}</N> {w.total_suspended_requests === 1 ? "request" : "requests"}, <N k="head|suspended_mw">{whole(w.total_suspended_mw)}</N> MW.{peak ? <> The most entered in {peak.year}.</> : null}</>} />
                <HeadlineNumber label={`Reached operation, of ${p0} to ${p1}`} value={share(w.past_operating_share_pct, "head|operating")} unit={w.past_operating_share_pct !== undefined ? "percent" : undefined}
                  note={w.past_operating_share_pct !== undefined ? <>Of <N k="head|past_requests">{whole(w.past_requests)}</N> requests. By capacity: {share(w.past_mw_operating_share_pct, "head|operating_mw")} percent of <N k="head|past_mw">{whole(w.past_mw)}</N> MW.</> : <>Fewer than {file.min_share} requests entered in those years: no share is given.</>} />
                <HeadlineNumber label="Withdrawn" value={<Withdrawn v={view} k="head|withdrawn" grid={grid} tech={tech} />} unit={w.past_withdrawn_share_pct !== undefined ? "percent" : undefined}
                  note={w.past_withdrawn_share_pct !== undefined ? <>By capacity: {share(w.past_mw_withdrawn_share_pct, "head|withdrawn_mw")} percent. Still active or suspended: {share(w.past_open_share_pct, "head|open")} percent of the requests.</> : null} />
                <HeadlineNumber label="Request to operation" value={w.median_years_to_operation === undefined ? notMedian(grid.slug) : share(w.median_years_to_operation, "head|median")} unit={w.median_years_to_operation !== undefined ? "years, median" : undefined}
                  note={<>Over <N k="head|dated">{whole(w.years_to_operation_n)}</N> of the <N k="head|operating_requests">{whole(w.operating_requests)}</N> requests that reached operation: the ones with both dates.</>} />
              </HeadlineRow>

              <ToolSection title="Active capacity, by the year it entered">
                <ChartFrame title={`${name}: MW still active`} legend={[{ label: "Active at the end of " + file.last_year, color: COLOR.active }]}
                  note={<>Each bar is the capacity of the requests that entered the queue that year and are still active. A request&apos;s capacity is what it asked to connect; for solar with storage, both parts. <N k="without_year">{whole(w.requests_without_year)}</N> of this view&apos;s <N k="total_requests">{whole(w.total_requests)}</N> requests have no year entered and are in no bar.</>}>
                  <ActiveChart view={view} name={name} />
                </ChartFrame>
              </ToolSection>

              <ToolSection title="What became of each year's requests"
                note={<>The black line above the bars marks the years counted as past requests, {p0} to {p1}: old enough (five years or more) for most outcomes to be known. Recent years are mostly still open, which is why they are not in the shares above.</>}>
                <ChartFrame title={`${name}: by year entered`} legend={[{ label: "Reached operation", color: COLOR.operating }, { label: "Still active or suspended", color: COLOR.open }, { label: "Withdrawn", color: COLOR.withdrawn }]}>
                  <OutcomeChart view={view} name={name} />
                </ChartFrame>
                <Fold title="Every year entered, in requests and MW">
                  <YearsTable view={view} name={name} />
                </Fold>
              </ToolSection>

              <ToolSection title="How long the built ones took"
                note={<>A point is the median, over the requests that began operating that year and have both dates, of the time from the request to operation. A year with fewer than {file.min_median} such requests has no point. Only requests that were built are here: it is not the wait of a request made today.</>}>
                <ChartFrame title={`${name}: median years from request to operation`}>
                  <YearsChart view={view} name={name} />
                </ChartFrame>
              </ToolSection>
            </>
          )}

          <ToolSection title={`${grid.name}: storage, solar with storage, and the rest`} id="kinds"
            note={<>Storage alone and solar with storage are kept apart from solar and from each other: a solar-with-storage request is one request at one point of interconnection, and its capacity is both parts together. Shares are of the requests that entered from {p0} to {p1}; &quot;not held&quot; means fewer than {file.min_share} such requests, or fewer than {file.min_median} dated ones.</>}>
            <ToolTable minWidth={760} caption={`${grid.name}: the queue by technology`}
              head={["Technology", "Active, MW", "Active requests", "Reached operation, percent", "Withdrawn, percent", "Median years to operation"]}
              rows={kinds.map(({ t, v }) => ({ key: t.slug, highlight: t.slug === tech.slug || (tech.slug === "all" && (t.slug === "battery" || t.slug === "solar_battery")), cells: v ? [
                <Link key="l" href={href(grid.slug, t.slug)} className="text-ink">{t.name}</Link>,
                <N key="a" k={`kind|${t.slug}|total_active_mw`}>{whole(v.whole.total_active_mw)}</N>, <N key="r" k={`kind|${t.slug}|total_active_requests`}>{whole(v.whole.total_active_requests)}</N>,
                share(v.whole.past_operating_share_pct, `kind|${t.slug}|past_operating_share_pct`), <Withdrawn key="w" v={v} k={`kind|${t.slug}|past_withdrawn_share_pct`} grid={grid} tech={t} />,
                v.whole.median_years_to_operation === undefined ? notMedian(grid.slug) : share(v.whole.median_years_to_operation, `kind|${t.slug}|median_years_to_operation`),
              ] : [t.name, "none", "none", NOT, NOT, NOT] }))} />
          </ToolSection>

          {/* row 1: the chosen technology in every grid, side by side, for a reader choosing where to file */}
          <ToolSection title={`${tech.name}: every grid`} id="grids">
            <ToolTable minWidth={760} caption={`${tech.name}: the queue of every grid, side by side`}
              head={["Grid", "Active, MW", "Active requests", "Reached operation, percent", "Withdrawn, percent", "Median years to operation"]}
              rows={GRIDS.map((g) => { const v = viewOf(file, g.slug, tech.slug); return { key: g.slug, highlight: g.slug === grid.slug, cells: v ? [
                <Link key="l" href={href(g.slug, tech.slug)} className="text-ink">{g.name}</Link>,
                <N key="a" k={`grid|${g.slug}|total_active_mw`}>{whole(v.whole.total_active_mw)}</N>, <N key="r" k={`grid|${g.slug}|total_active_requests`}>{whole(v.whole.total_active_requests)}</N>,
                share(v.whole.past_operating_share_pct, `grid|${g.slug}|past_operating_share_pct`), <Withdrawn key="w" v={v} k={`grid|${g.slug}|past_withdrawn_share_pct`} grid={g} tech={tech} />,
                v.whole.median_years_to_operation === undefined ? notMedian(g.slug) : share(v.whole.median_years_to_operation, `grid|${g.slug}|median_years_to_operation`),
              ] : [g.name, "none", "none", NOT, NOT, NOT] }; })} />
          </ToolSection>

          <Fold title="What the file does not hold">
            <ul className="max-w-3xl list-disc space-y-1 pl-5">
              <li>Requests after the end of {file.last_year}: the file is a yearly edition, not a live queue.</li>
              <li>Every plant that operates. A request is &quot;operational&quot; here only when its operator&apos;s queue says so; operators differ in how long they keep finished and withdrawn requests, so a share is of what the queue records, not of everything ever proposed.</li>
              <li>The operation date of many built requests: of {whole(file.counts.operating)} that reached operation, {whole(file.counts.operating_dated)} have both a request date and an operation date in order. ISO-NE&apos;s have none, so it has no median wait.</li>
              <li>The year entered of {whole(file.counts.without_year)} requests, and the status of {whole(file.counts.unknown_status)}.</li>
              <li>The storage part of a hybrid on its own: a solar-with-storage request carries one total here.</li>
              <li>Whether an active request will be built. Most are not: that is what the shares above measure for earlier years.</li>
              <li>Cost, the developer, the network upgrades asked for, or the reason a request was withdrawn.</li>
              <li>The same project twice: a developer may file at several points for one plant, and each request counts.</li>
              <li data-no-load="1">A load. Every request here is a power plant or a battery asking to connect; a data center&apos;s or any other large customer&apos;s request to draw power is in no edition of the file, and no wait here is a load&apos;s.
                ERCOT&apos;s large loads (MW approved to energize, report by report) are on <SiteLink href="/datacenters">the datacenters page</SiteLink>; the All grids tab of <SiteLink href="/cost-of-power?view=allgrids">the cost of power</SiteLink> sets each grid&apos;s wait for generators beside the large-load rules the ERW has read.</li>
            </ul>
          </Fold>
          <Fold title="How it is computed">
            <p className="max-w-3xl">Counts and sums of the file&apos;s rows, grouped by Berkeley Lab&apos;s region and by its clean technology label. A past request entered from {p0} to {p1} and has a known status. A share is given when at least {file.min_share} past requests are counted,
              a median when at least {file.min_median} requests are dated. Nothing is estimated. The full method: <SiteLink href={METHOD}>the interconnection queue, summarized</SiteLink>.</p>
          </Fold>
          <DecisionsBlock id="7018-queues" title="Decisions on this page (each with its default and its source on hover)" items={QUEUES_DECISIONS} />
          <SourceLine tables={[TABLE, "lbnl_interconnection_queue"]}
            note={<>Data: Lawrence Berkeley National Laboratory and GridTracker, Queued Up: 2026 Edition data file, licensed CC BY 4.0; retrieved {file.input_retrieved.slice(0, 10)}, summarized {file.built.slice(0, 10)}. This page is in review and reads the site&apos;s own copy of the summary.</>} />
        </div>
      </div>
    </ToolPage>
    </Brand>
  );
}
