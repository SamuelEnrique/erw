import type { Metadata } from "next";
import Link from "next/link";
import { SiteLink } from "@/components/SiteLink";
import { ChartFrame, Fold, HeadlineNumber, HeadlineRow, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import fileJson from "@/data/price_compare.json";
import { MARKETS, MEASURES, TABLE, choices, href, label, lacking, monthName, ordered, periodName, two, valueOf, type CompareFile, type Row } from "@/lib/pricecompare";

// Session 96: "Where power is cheap", in review (lib/release.ts), in the battery page's layout: every public hub and
// zone price the warehouse holds, over the last twelve months (the hubs with a year of history) or over the last whole
// month (every hub and zone), on five measures: the average price, the share of hours below zero, the share above
// USD 200, the spread between the dearest and the cheapest four hours of the average day, and the carbon intensity of
// the hub's grid. Sortable from the address, one chart, a sentence. Every number is a row of hub_price_comparison
// (warehouse/derived/price_compare.py; docs/methods/hub_price_comparison.md), read from the site's own copy. A hub is
// not a site, and the page says so. Hubs whose publisher's terms do not allow it are named and carry no number.
export const metadata: Metadata = { title: "Where power is cheap", robots: { index: false, follow: false } };

const file = fileJson as unknown as CompareFile;
const METHOD = "/data/methods/hub_price_comparison";
const N = ({ k, children }: { k: string; children: string }) => <span data-n={k}>{children}</span>;
const NOT = <span className="text-muted">not held</span>;

/** The measure sorted by, one bar per hub or zone, in the table's order. */
function Bars({ rows, pick, unit, what }: { rows: Row[]; pick: (r: Row) => number | undefined; unit: string; what: string }) {
  const W = 760, L = 292, R = 70, top = 8, bar = 16, gap = 5;
  const vals = rows.map(pick);
  const hi = Math.max(0, ...vals.map((v) => v ?? 0)), lo = Math.min(0, ...vals.map((v) => v ?? 0));
  const span = hi - lo || 1;
  const x = (v: number) => L + ((v - lo) / span) * (W - L - R);
  const H = top + rows.length * (bar + gap) + 8;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" data-chart="bars" aria-label={`${what}, one bar per hub or zone, ${unit}`}>
      <line x1={x(0)} x2={x(0)} y1={top - 4} y2={H - 4} stroke="var(--color-rule)" strokeWidth="1.5" />
      {rows.map((r, i) => {
        const v = vals[i], y = top + i * (bar + gap);
        return (
          <g key={r.entity} data-bar={r.entity}>
            <text x={L - 8} y={y + bar - 4} textAnchor="end" fontSize="11" fill="var(--color-ink)">{label(r)}</text>
            {v === undefined ? <text x={L + 4} y={y + bar - 4} fontSize="11" fill="var(--color-muted)">not held</text> : (
              <>
                <rect x={Math.min(x(0), x(v))} y={y} width={Math.max(1, Math.abs(x(v) - x(0)))} height={bar} fill="var(--color-accent)"><title>{`${label(r)}: ${two(v)} ${unit}`}</title></rect>
                <text x={Math.max(x(0), x(v)) + 5} y={y + bar - 4} fontSize="11" fill="var(--color-muted)">{two(v)}</text>
              </>
            )}
          </g>
        );
      })}
    </svg>
  );
}

export default async function Compare({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const q = Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined]));
  const c = choices(q);
  const all = file[c.period];
  const rows = ordered(all, c);
  const none = lacking(all, c.market);
  const market = MARKETS.find((m) => m.slug === c.market)!;
  const when = periodName(file, c.period);
  const item = (on: boolean) => `no-underline ${on ? "font-semibold text-accent" : "text-ink hover:text-accent"}`;
  const by = (slug: string, dir: "asc" | "desc") => ordered(all, { ...c, sort: MEASURES.find((m) => m.slug === slug)!, dir })[0];
  const cheapest = by("avg", "asc"), dearest = by("avg", "desc"), negative = by("neg", "desc"), widest = by("spread", "desc");
  const avg = MEASURES[0], neg = MEASURES[1], spread = MEASURES[3];
  const cell = (r: Row, m: (typeof MEASURES)[number]) => { const v = valueOf(r, c.market, m); return v === undefined ? NOT : <N k={`${r.entity}|${m.slug}`}>{two(v)}</N>; };
  const grids = [...new Set(rows.map((r) => r.grid))];
  const w = file.windows[c.period];
  const noCarbon = [...new Set(rows.filter((r) => r.grid_carbon_intensity === undefined).map((r) => r.grid))];

  return (
    <ToolPage>
      <ToolHeader title="Where power is cheap"
        lead={<>Every public hub and zone price the warehouse holds, side by side: the average price, how often it falls below zero or climbs above USD 200, how far the dearest hours of the day stand above the cheapest, and how clean the grid behind it is.
          Sort by any of them. See also <SiteLink href="/prices">prices by hub</SiteLink> and <SiteLink href="/cost-of-power/battery">what a battery earns</SiteLink>.</>} />
      <p className="mb-8 max-w-3xl border-l-2 border-accent bg-paper px-3 py-2 text-sm" data-not-a-site="1">
        <span className="font-semibold">A hub is not a site.</span> A hub or zone price is an average over many points of a grid. The price at one substation differs from it by congestion and losses, sometimes by a lot,
        and what a buyer pays adds delivery, capacity and other charges that are not here. This page compares markets; it does not price a location.
      </p>
      <div className="grid gap-8 lg:grid-cols-[240px_minmax(0,1fr)]">
        <aside>
          <InputPanel title="Choose" note={<>Twelve months of history are held for {file.year.length} hubs; the zones and the other hubs are held since late August 2026, so they are in the month and not in the year.</>}>
            <nav aria-label="Period" className="mb-4 text-sm">
              <div className="mb-1 text-xs uppercase tracking-wide text-muted">Period</div>
              <div><Link href={href({ ...c, period: "year", sort: c.sort.slug, dir: c.dir })} aria-current={c.period === "year" ? "true" : undefined} className={item(c.period === "year")}>Twelve months to {monthName(file.end_month)}: {file.year.length} hubs</Link></div>
              <div><Link href={href({ ...c, period: "month", sort: c.sort.slug, dir: c.dir })} aria-current={c.period === "month" ? "true" : undefined} className={item(c.period === "month")}>{monthName(file.end_month)}: {file.month.length} hubs and zones</Link></div>
            </nav>
            <nav aria-label="Market" className="mb-4 text-sm">
              <div className="mb-1 text-xs uppercase tracking-wide text-muted">Market</div>
              {MARKETS.map((m) => <div key={m.slug}><Link href={href({ ...c, market: m.slug, sort: c.sort.slug, dir: c.dir })} aria-current={m.slug === c.market ? "true" : undefined} className={item(m.slug === c.market)}>{m.name}</Link></div>)}
            </nav>
            <nav aria-label="Sort" className="text-sm">
              <div className="mb-1 text-xs uppercase tracking-wide text-muted">Sort by</div>
              {MEASURES.map((m) => <div key={m.slug}><Link href={href({ ...c, sort: m.slug })} aria-current={m.slug === c.sort.slug ? "true" : undefined} className={item(m.slug === c.sort.slug)}>{m.name}</Link></div>)}
              <div className="mt-2 text-xs"><Link href={href({ ...c, sort: c.sort.slug, dir: c.dir === "asc" ? "desc" : "asc" })} className="text-ink">{c.dir === "asc" ? "Lowest first: show highest first" : "Highest first: show lowest first"}</Link></div>
            </nav>
          </InputPanel>
        </aside>

        <div className="min-w-0">
          {rows.length === 0 || !cheapest ? (
            <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status"><span className="font-semibold">no data</span>: {TABLE} holds no {market.name.toLowerCase()} price for {when}.</p>
          ) : (
            <>
              <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-summary="1">
                Over {when}, {label(cheapest)} had the lowest average {market.name.toLowerCase()} price of the <N k="count">{String(rows.length)}</N> hubs{c.period === "month" ? " and zones" : ""} compared, USD <N k="sum|cheapest">{two(valueOf(cheapest, c.market, avg)!)}</N> per MWh,
                and {label(dearest)} the highest, USD <N k="sum|dearest">{two(valueOf(dearest, c.market, avg)!)}</N>.{" "}
                {valueOf(negative, c.market, neg)! > 0
                  ? <>{label(negative)} spent the most hours below zero: <N k="sum|negative">{two(valueOf(negative, c.market, neg)!)}</N> percent of them.</>
                  : <>None of them had an hour below zero.</>}
              </p>
              <HeadlineRow>
                <HeadlineNumber label="Lowest average price" value={<N k="head|cheapest">{two(valueOf(cheapest, c.market, avg)!)}</N>} unit="USD per MWh" note={<>{label(cheapest)}. The highest: {label(dearest)}, <N k="head|dearest">{two(valueOf(dearest, c.market, avg)!)}</N>.</>} />
                <HeadlineNumber label="Most hours below zero" value={<N k="head|negative">{two(valueOf(negative, c.market, neg)!)}</N>} unit="percent" note={valueOf(negative, c.market, neg)! > 0 ? <>{label(negative)}.</> : <>No hub or zone here had an hour below zero in {when}.</>} />
                <HeadlineNumber label="Widest daily spread" value={<N k="head|spread">{two(valueOf(widest, c.market, spread)!)}</N>} unit="USD per MWh" note={<>{label(widest)}: the four dearest hours of its average day less the four cheapest.</>} />
              </HeadlineRow>

              <ToolSection title={`${c.sort.name}, ${c.dir === "asc" ? "lowest first" : "highest first"}`}>
                <ChartFrame title={`${market.name}, ${when}: ${c.sort.unit}`}
                  note={c.sort.slug === "carbon" ? <>The carbon intensity is the grid&apos;s, so every hub of a grid has the same bar.</> : <>One bar per hub or zone, in the order of the table below.</>}>
                  <Bars rows={rows} pick={(r) => valueOf(r, c.market, c.sort)} unit={c.sort.unit} what={`${c.sort.name}, ${market.name.toLowerCase()}, ${when}`} />
                </ChartFrame>
              </ToolSection>

              <ToolSection title="The table" id="table"
                note={<>{market.name} prices by the hour, in each grid&apos;s own time, from {w.start} to {w.end} (the end not included). Hours below zero and above USD 200 are shares of the hours held. The spread is read off the average day: the mean price of each hour of the day over the period, its four dearest hours less its four cheapest.
                  The carbon intensity is the grid&apos;s generation over the same period (kg of CO2 per MWh), not the hub&apos;s. A heading sorts by its column.</>}>
                <ToolTable minWidth={700} caption={`Hub and zone prices compared, ${market.name.toLowerCase()}, ${when}`}
                  head={["Hub or zone", ...MEASURES.map((m) => (
                    <Link key={m.slug} href={`${href({ ...c, sort: m.slug, dir: m.slug === c.sort.slug ? (c.dir === "asc" ? "desc" : "asc") : undefined })}#table`} className="underline" style={{ color: "var(--color-surface)" }} data-sort={m.slug}>
                      {m.slug === "spread" ? "Spread, 4 hours" : m.slug === "carbon" ? "Grid carbon" : m.slug === "high" ? "Hours above 200" : m.name}{m.slug === c.sort.slug ? (c.dir === "asc" ? " ↑" : " ↓") : ""}
                    </Link>)), "Hours held"]}
                  rows={rows.map((r) => ({ key: r.entity, cells: [label(r), ...MEASURES.map((m) => cell(r, m)),
                    <span key="h"><N k={`${r.entity}|hours`}>{(c.market === "dam" ? r.dam_hours_held! : r.rtm_hours_held!).toLocaleString("en-US")}</N> of {(c.market === "dam" ? r.dam_hours_in_window! : r.rtm_hours_in_window!).toLocaleString("en-US")}</span>] }))} />
                {none.length ? <p className="mt-3 max-w-3xl text-sm" data-lacking={none.length}>Not held for {when} in the {market.name.toLowerCase()} market (fewer than {Math.round(file.near_hours * 100)} percent of its hours): {none.map(label).join("; ")}.</p> : null}
                <p className="mt-2 max-w-3xl text-xs text-muted">Grids in this view: {grids.join(", ")}. {noCarbon.length ? <span data-no-carbon={noCarbon.join(",")}>A grid&apos;s carbon intensity is given when at least {Math.round(file.near_days * 100)} percent of the period&apos;s days are held; not held for this period: {noCarbon.join(", ")}.</span> : null}</p>
              </ToolSection>
            </>
          )}

          <ToolSection title="Held, not shown" id="held"
            note={<>A price the warehouse holds but whose publisher&apos;s terms do not allow a figure to be derived from it and published is named here and carries no number. A license, or the publisher&apos;s word, is needed.</>}>
            <ToolTable words minWidth={520} caption="Hubs held and not shown, with the reason"
              head={["Hub", "Why it is not shown"]}
              rows={[...file.held_not_shown.map((h) => ({ key: h.entity, cells: [`${h.grid}, ${h.node}`, <span key="r" data-hidden={h.entity}>Held, not shown: license needed. {h.reason}.</span>] })),
                ...file.not_held.map((g) => ({ key: g, cells: [g, <span key="r" data-not-held={g}>Not held: the warehouse has no {g} hub or zone price. {g}&apos;s prices are licensed.</span>] }))]} />
          </ToolSection>

          <Fold title="How it is computed">
            <p className="max-w-3xl">From each grid operator&apos;s public day-ahead and real-time prices at its hubs and zones. A real-time hour is the mean of its four 15-minute prices and is counted only when all four are held; ISO-NE&apos;s is its own hourly report.
              A hub is in a period when at least {Math.round(file.near_hours * 100)} percent of the period&apos;s hours are held; nothing is filled. The full method: <SiteLink href={METHOD}>where power is cheap</SiteLink>.</p>
          </Fold>
          <Fold title="What this does not tell you">
            <ul className="max-w-3xl list-disc space-y-1 pl-5">
              <li>The price at a site. Nodal prices inside a hub or zone differ from its average, and the gap is the thing a developer most needs to know.</li>
              <li>A delivered price: transmission, distribution, capacity, ancillary services and retail charges are not in a hub price.</li>
              <li>Next year. Twelve months hold one winter and one summer; a cold snap or a mild season moves every figure here.</li>
              <li>The carbon of the power a site would take. The intensity is the grid&apos;s average generation, not the marginal plant and not a hub&apos;s.</li>
              <li>Whether power can be had there at all: an interconnection or a large-load request is its own queue.</li>
            </ul>
          </Fold>
          <SourceLine tables={[TABLE, "iso_hub_prices_history", "ercot_all_hub_prices_history", "iso_dam_hub_prices", "iso_rtm_hub_prices", "isone_dam_zone_prices", "isone_rtm_zone_prices_hourly", "nyiso_dam_zone_prices", "nyiso_rtm_zone_prices", "carbon_intensity_daily"]}
            note={<>Built {file.built.slice(0, 10)}. This page is in review and reads the site&apos;s own copy of the comparison.</>} />
        </div>
      </div>
    </ToolPage>
  );
}
