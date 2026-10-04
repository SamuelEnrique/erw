import type { Metadata } from "next";
import Link from "next/link";
import { SiteLink } from "@/components/SiteLink";
import { ChartFrame, Fold, HeadlineNumber, HeadlineRow, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import fileJson from "@/data/queues.json";
import { GRIDS, TABLE, TECHS, choices, href, outcome, peakActive, two, viewOf, whole, yearsOf, type QueueFile, type View } from "@/lib/queues";

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
  const pts = Object.entries(view.on).map(([y, r]) => ({ year: Number(y), ...r })).filter((p) => p.year >= 2000).sort((a, b) => a.year - b.year);
  if (pts.length < 2) return <p className="border border-rule bg-paper px-3 py-2 text-sm" data-chart="years-none">Fewer than two operation years hold {file.min_median} dated requests for {name}: no line is drawn.</p>;
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
    <ToolPage>
      <ToolHeader title="The interconnection queue"
        lead={<>Before a power plant or a battery can connect to the grid it waits in a queue for a study and an agreement. Choose a grid and a technology: how much capacity is waiting and since when,
          what became of the requests of earlier years, and how long the ones that were built took. From Berkeley Lab and GridTracker&apos;s record of every request, through the end of {file.last_year}.
          See also <SiteLink href="/storage/buildout">the storage build-out</SiteLink> and <SiteLink href="/map">the project map</SiteLink>.</>} />
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
                At the end of {file.last_year}, <N k="total_active_requests">{whole(w.total_active_requests)}</N> {tech.noun} were active in {grid.place}&apos;s queue{grid.slug === "us" ? "s" : ""}, for <N k="total_active_mw">{whole(w.total_active_mw)}</N> MW.{" "}
                {w.past_operating_share_pct !== undefined
                  ? <>Of the <N k="past_requests">{whole(w.past_requests)}</N> that entered from {p0} to {p1}, <N k="past_operating_share_pct">{two(w.past_operating_share_pct)}</N> percent reached operation and <N k="past_withdrawn_share_pct">{two(w.past_withdrawn_share_pct!)}</N> percent were withdrawn.</>
                  : <>Only <N k="past_requests">{whole(w.past_requests)}</N> entered from {p0} to {p1}: too few for a share.</>}{" "}
                {w.median_years_to_operation !== undefined
                  ? <>Those that were built took a median of <N k="median_years_to_operation">{two(w.median_years_to_operation)}</N> years from request to operation.</>
                  : <>The file dates too few of those that were built to give a median wait.</>}
              </p>
              <HeadlineRow>
                <HeadlineNumber label="Active capacity" value={<N k="head|active_mw">{whole(w.total_active_mw)}</N>} unit="MW"
                  note={<><N k="head|active_requests">{whole(w.total_active_requests)}</N> requests. Suspended, and not counted here: <N k="head|suspended_requests">{whole(w.total_suspended_requests)}</N> requests, <N k="head|suspended_mw">{whole(w.total_suspended_mw)}</N> MW.{peak ? <> The most entered in {peak.year}.</> : null}</>} />
                <HeadlineNumber label={`Reached operation, of ${p0} to ${p1}`} value={share(w.past_operating_share_pct, "head|operating")} unit={w.past_operating_share_pct !== undefined ? "percent" : undefined}
                  note={w.past_operating_share_pct !== undefined ? <>Of <N k="head|past_requests">{whole(w.past_requests)}</N> requests. By capacity: {share(w.past_mw_operating_share_pct, "head|operating_mw")} percent of <N k="head|past_mw">{whole(w.past_mw)}</N> MW.</> : <>Fewer than {file.min_share} requests entered in those years: no share is given.</>} />
                <HeadlineNumber label="Withdrawn" value={share(w.past_withdrawn_share_pct, "head|withdrawn")} unit={w.past_withdrawn_share_pct !== undefined ? "percent" : undefined}
                  note={w.past_withdrawn_share_pct !== undefined ? <>By capacity: {share(w.past_mw_withdrawn_share_pct, "head|withdrawn_mw")} percent. Still active or suspended: {share(w.past_open_share_pct, "head|open")} percent of the requests.</> : null} />
                <HeadlineNumber label="Request to operation" value={share(w.median_years_to_operation, "head|median")} unit={w.median_years_to_operation !== undefined ? "years, median" : undefined}
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
                share(v.whole.past_operating_share_pct, `kind|${t.slug}|past_operating_share_pct`), share(v.whole.past_withdrawn_share_pct, `kind|${t.slug}|past_withdrawn_share_pct`),
                share(v.whole.median_years_to_operation, `kind|${t.slug}|median_years_to_operation`),
              ] : [t.name, "none", "none", NOT, NOT, NOT] }))} />
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
            </ul>
          </Fold>
          <Fold title="How it is computed">
            <p className="max-w-3xl">Counts and sums of the file&apos;s rows, grouped by Berkeley Lab&apos;s region and by its clean technology label. A past request entered from {p0} to {p1} and has a known status. A share is given when at least {file.min_share} past requests are counted,
              a median when at least {file.min_median} requests are dated. Nothing is estimated. The full method: <SiteLink href={METHOD}>the interconnection queue, summarized</SiteLink>.</p>
          </Fold>
          <SourceLine tables={[TABLE, "lbnl_interconnection_queue"]}
            note={<>Data: Lawrence Berkeley National Laboratory and GridTracker, Queued Up: 2026 Edition data file, licensed CC BY 4.0; retrieved {file.input_retrieved.slice(0, 10)}, summarized {file.built.slice(0, 10)}. This page is in review and reads the site&apos;s own copy of the summary.</>} />
        </div>
      </div>
    </ToolPage>
  );
}
