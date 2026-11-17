import type { Metadata } from "next";
import Link from "next/link";
import { SiteLink } from "@/components/SiteLink";
import { Brand } from "@/components/Brand";  // session 242: the page takes the brand (it was built on ToolPage and carried no wrapper)
import { ChartFrame, Fold, HeadlineNumber, HeadlineRow, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import fileJson from "@/data/price_compare.json";
import { DecisionsBlock } from "@/components/tool/DecisionsBlock";
import { COMPARE_DECISIONS } from "@/lib/decisions";
import { MARKETS, MEASURES, NAME_WORDS, TABLE, choices, heldGrids, hold, href, label, lacking, monthName, ordered, pairOf, periodName, two, valueOf, type CompareFile, type HeldRow, type Row } from "@/lib/pricecompare";
import { LICENSE_FROM, LICENSE_TITLE_SUFFIX, licenseHeldRow, licensePublishers, licenseTitle } from "@/lib/license";

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
// session 7540: "not held" is drawn in the page's own ink, its reason on hover (the page standard: no grey text)
const NOT = <span title="Fewer than 95 percent of the period's hours are held (90 percent of its days for the grid's carbon intensity); nothing is filled.">not held</span>;
// session 7540: a figure of a grid that holds hub_price_comparison under a license is drawn "license needed", the
// publishers on hover (lib/license.ts); the row is held on the server, so no figure of it is in the page
const HELD = <span data-license-held={TABLE} title={licenseTitle(TABLE)}>license needed</span>;

/** The measure sorted by, one bar per hub or zone, in the table's order; a held row last, with no bar. */
function Bars({ rows, held = [], pick, unit, what }: { rows: Row[]; held?: HeldRow[]; pick: (r: Row) => number | undefined; unit: string; what: string }) {
  const W = 760, L = 292, R = 70, top = 8, bar = 16, gap = 5;
  const vals = rows.map(pick);
  const hi = Math.max(0, ...vals.map((v) => v ?? 0)), lo = Math.min(0, ...vals.map((v) => v ?? 0));
  const span = hi - lo || 1;
  const x = (v: number) => L + ((v - lo) / span) * (W - L - R);
  const H = top + (rows.length + held.length) * (bar + gap) + 8;
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
      {held.map((r, j) => {
        const y = top + (rows.length + j) * (bar + gap);
        return (
          <g key={r.entity} data-bar={r.entity} data-bar-held="1">
            <text x={L - 8} y={y + bar - 4} textAnchor="end" fontSize="11" fill="var(--color-ink)">{label(r)}</text>
            <text x={L + 4} y={y + bar - 4} fontSize="11" fill="var(--color-ink)"><title>{licenseTitle(TABLE)}</title>license needed</text>
          </g>
        );
      })}
    </svg>
  );
}

/** Session 7540: A and B side by side over the same hours, in both markets, B less A on the figures drawn; a held row
 *  "license needed", a row not in the period said so. Every figure is the row's own in the table. */
function AandB({ file, c, shown, held, a, b }: { file: CompareFile; c: ReturnType<typeof choices>; shown: Row[]; held: HeldRow[]; a?: string; b?: string }) {
  const when = periodName(file, c.period);
  const options = [...shown.map((r) => ({ entity: r.entity, words: label(r) })), ...held.map((r) => ({ entity: r.entity, words: `${label(r)} (license needed)` }))]
    .sort((x, y) => x.words.localeCompare(y.words));
  type Pick = { kind: "none" } | { kind: "row"; r: Row } | { kind: "held"; h: HeldRow } | { kind: "absent"; e: string };
  const find = (e?: string): Pick => {
    if (!e) return { kind: "none" };
    const r = shown.find((x) => x.entity === e);
    if (r) return { kind: "row", r };
    const h = held.find((x) => x.entity === e);
    return h ? { kind: "held", h } : { kind: "absent", e };
  };
  const pa = find(a), pb = find(b);
  const name = (p: Pick) => (p.kind === "row" ? label(p.r) : p.kind === "held" ? label(p.h) : p.kind === "absent" ? p.e : "none chosen");
  const absent = <span title={`Not in ${when}: the zones and the hubs other than the eleven with a year of history are held since late August 2026, so they are in the month and not in the twelve months.`}>not in this period</span>;
  const valueCell = (p: Pick, k: string, v: (r: Row) => number | undefined, fmt: (x: number) => string) =>
    p.kind === "none" ? "" : p.kind === "held" ? HELD : p.kind === "absent" ? absent : v(p.r) === undefined ? NOT : <N k={k}>{fmt(v(p.r)!)}</N>;
  const diff = (k: string, v: (r: Row) => number | undefined, fmt: (x: number) => string) => {
    if (pa.kind !== "row" || pb.kind !== "row") return "";
    const x = v(pa.r), y = v(pb.r);
    if (x === undefined || y === undefined) return "";
    const d = Math.round((y - x) * 100) / 100 || 0;   // on the figures drawn (two places), never "-0.00"
    return <>{d > 0 ? "+" : ""}<N k={k}>{fmt(d)}</N></>;
  };
  const td = "px-3 py-1.5 text-right";
  const line = (key: string, head: string, v: (r: Row) => number | undefined, fmt: (x: number) => string = two) => (
    <tr key={key} className="border-b border-rule"><th scope="row" className="px-3 py-1.5 text-left font-normal">{head}</th>
      <td className={td}>{valueCell(pa, `ab|a|${key}`, v, fmt)}</td><td className={td}>{valueCell(pb, `ab|b|${key}`, v, fmt)}</td><td className={td}>{diff(`ab|diff|${key}`, v, fmt)}</td></tr>
  );
  const hours = (m: "dam" | "rtm") => (r: Row) => (m === "dam" ? r.dam_hours_held : r.rtm_hours_held);
  return (
    <ToolSection title="A and B, side by side" id="ab">
      <form method="get" action="/prices/compare" className="mb-3 flex flex-wrap items-end gap-3 text-sm" data-ab-form="1">
        <input type="hidden" name="period" value={c.period} /><input type="hidden" name="market" value={c.market} />
        <input type="hidden" name="sort" value={c.sort.slug} /><input type="hidden" name="dir" value={c.dir} />
        {(["a", "b"] as const).map((k) => (
          <label key={k} className="block max-w-full"><span className="mr-1 font-semibold">{k.toUpperCase()}</span>
            <select name={k} defaultValue={(k === "a" ? a : b) ?? ""} className="max-w-full border border-rule bg-white px-2 py-1" data-ab-pick={k}>
              <option value="">none</option>
              {options.map((o) => <option key={o.entity} value={o.entity}>{o.words}</option>)}
            </select>
          </label>
        ))}
        <button type="submit" className="border border-accent bg-accent px-3 py-1 text-white" data-ab-show="1">Set side by side</button>
      </form>
      {pa.kind === "none" && pb.kind === "none" ? (
        <p className="max-w-3xl text-sm" data-ab-empty="1">Choose A and B to set two hubs or zones side by side over {when}, in both markets, with B less A.</p>
      ) : (
        <>
          <div className="overflow-x-auto" role="region" aria-label="A and B, the table" tabIndex={0}>
            <table className="w-full border-collapse text-sm tabular-nums" style={{ minWidth: 480 }} data-ab-table="1">
              <caption className="sr-only">{`A and B side by side, ${when}`}</caption>
              <thead><tr className="bg-accent text-white"><th scope="col" className="px-3 py-1.5 text-left font-normal">{when}</th><th scope="col" className={`${td} font-normal`} data-ab-head="a">A: {name(pa)}</th><th scope="col" className={`${td} font-normal`} data-ab-head="b">B: {name(pb)}</th><th scope="col" className={`${td} font-normal`}>B less A</th></tr></thead>
              <tbody>
                {MARKETS.map((m) => [
                  <tr key={`h${m.slug}`} className="border-b border-rule bg-paper"><th scope="colgroup" colSpan={4} className="px-3 py-1.5 text-left font-semibold">{m.name}</th></tr>,
                  ...MEASURES.filter((x) => x.slug !== "carbon").map((x) => line(`${m.slug}|${x.slug}`, `${x.name}, ${x.unit}`, (r) => valueOf(r, m.slug, x))),
                  line(`${m.slug}|hours`, "Hours held", hours(m.slug), (x) => x.toLocaleString("en-US")),
                ])}
                <tr key="hc" className="border-b border-rule bg-paper"><th scope="colgroup" colSpan={4} className="px-3 py-1.5 text-left font-semibold">The grid</th></tr>
                {line("carbon", `${MEASURES[4].name}, ${MEASURES[4].unit}`, (r) => r.grid_carbon_intensity)}
              </tbody>
            </table>
          </div>
          <p className="mt-1 max-w-3xl text-xs" data-ab-note="1">Each figure is the row&apos;s own in the table below, over the same hours of {when} in each grid&apos;s clock time; B less A is taken on the figures drawn.
            {" "}<SiteLink href="/cost-of-power?view=allgrids">The cost of power page</SiteLink> prices the same hubs over its own last twelve whole months and in each grid&apos;s standard time (no daylight saving), so its twelve months can end a month later than these and a month read on both can differ by a few cents; over the same hours the two agree.</p>
        </>
      )}
    </ToolSection>
  );
}

export default async function Compare({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const q = Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined]));
  const c = choices(q);
  // session 7540: the license hold of the day, on the server (lib/pricecompare.ts hold): every figure below is of the
  // rows shown; a held row is named, drawn "license needed", and carries no figure
  const { shown: all, held } = hold(file[c.period], (e) => licenseHeldRow(TABLE, e));
  const ab = pairOf(q);
  const keep = { a: ab.a, b: ab.b };
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
  const heldWho = heldGrids(held);
  const nameCell = (r: { entity: string; grid: string; node: string }) => (NAME_WORDS[r.entity] ? <span title={NAME_WORDS[r.entity]} data-name-words={r.entity}>{label(r)}</span> : label(r));

  return (
    <Brand>
    <ToolPage>
      <ToolHeader title="Where power is cheap"
        lead={<>The hub and zone prices of five grids, side by side: the average price, how often it falls below zero or climbs above USD 200, how far the dearest hours of the day stand above the cheapest, and how clean the grid behind it is.
          Sort by any of them. See also <SiteLink href="/prices">prices by hub</SiteLink> and <SiteLink href="/cost-of-power/battery">what a battery earns</SiteLink>.</>} />
      <p className="mb-8 max-w-3xl border-l-2 border-accent bg-paper px-3 py-2 text-sm" data-not-a-site="1">
        <span className="font-semibold">A hub is not a site.</span> A hub or zone price is an average over many points of a grid. The price at one substation differs from it by congestion and losses, sometimes by a lot,
        and what a buyer pays adds delivery, capacity and other charges that are not here. This page compares markets; it does not price a location.
      </p>
      <div className="grid gap-8 lg:grid-cols-[240px_minmax(0,1fr)]">
        <aside>
          <InputPanel title="Choose" reset={{ href: "/prices/compare", defaults: "twelve months, day-ahead, ordered by the average price, cheapest first." }} note={<>Twelve months of history are held for {file.year.length} hubs; the zones and the other hubs are held since late August 2026, so they are in the month and not in the year.</>}>
            <nav aria-label="Period" className="mb-4 text-sm">
              <div className="mb-1 text-xs uppercase tracking-wide text-muted">Period</div>
              <div><Link href={href({ ...c, ...keep, period: "year", sort: c.sort.slug, dir: c.dir })} aria-current={c.period === "year" ? "true" : undefined} className={item(c.period === "year")}>Twelve months to {monthName(file.end_month)}: {file.year.length} hubs</Link></div>
              <div><Link href={href({ ...c, ...keep, period: "month", sort: c.sort.slug, dir: c.dir })} aria-current={c.period === "month" ? "true" : undefined} className={item(c.period === "month")}>{monthName(file.end_month)}: {file.month.length} hubs and zones</Link></div>
            </nav>
            <nav aria-label="Market" className="mb-4 text-sm">
              <div className="mb-1 text-xs uppercase tracking-wide text-muted">Market</div>
              {MARKETS.map((m) => <div key={m.slug}><Link href={href({ ...c, ...keep, market: m.slug, sort: c.sort.slug, dir: c.dir })} aria-current={m.slug === c.market ? "true" : undefined} className={item(m.slug === c.market)}>{m.name}</Link></div>)}
            </nav>
            <nav aria-label="Sort" className="text-sm">
              <div className="mb-1 text-xs uppercase tracking-wide text-muted">Sort by</div>
              {MEASURES.map((m) => <div key={m.slug}><Link href={href({ ...c, ...keep, sort: m.slug })} aria-current={m.slug === c.sort.slug ? "true" : undefined} className={item(m.slug === c.sort.slug)}>{m.name}</Link></div>)}
              <div className="mt-2 text-xs"><Link href={href({ ...c, ...keep, sort: c.sort.slug, dir: c.dir === "asc" ? "desc" : "asc" })} className="text-ink">{c.dir === "asc" ? "Lowest first: show highest first" : "Highest first: show lowest first"}</Link></div>
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
                {held.length ? <span data-summary-held={heldWho.join(",")}>{" "}<span title={licenseTitle(TABLE)}>{heldWho.map((g) => `${g}'s`).join(" and ")} {held.length} hubs and zones</span> are named in the table with no figure: license needed.</span> : null}
              </p>
              <HeadlineRow>
                <HeadlineNumber label="Lowest average price" value={<N k="head|cheapest">{two(valueOf(cheapest, c.market, avg)!)}</N>} unit="USD per MWh" note={<>{label(cheapest)}. The highest: {label(dearest)}, <N k="head|dearest">{two(valueOf(dearest, c.market, avg)!)}</N>.</>} />
                <HeadlineNumber label="Most hours below zero" value={<N k="head|negative">{two(valueOf(negative, c.market, neg)!)}</N>} unit="percent" note={valueOf(negative, c.market, neg)! > 0 ? <>{label(negative)}.</> : <>No hub or zone here had an hour below zero in {when}.</>} />
                <HeadlineNumber label="Widest daily spread" value={<N k="head|spread">{two(valueOf(widest, c.market, spread)!)}</N>} unit="USD per MWh" note={<>{label(widest)}: the four dearest hours of its average day less the four cheapest.</>} />
              </HeadlineRow>

              <AandB file={file} c={c} shown={all} held={held} a={ab.a} b={ab.b} />

              <ToolSection title={`${c.sort.name}, ${c.dir === "asc" ? "lowest first" : "highest first"}`}>
                <ChartFrame title={`${market.name}, ${when}: ${c.sort.unit}`}
                  note={c.sort.slug === "carbon" ? <>The carbon intensity is the grid&apos;s, so every hub of a grid has the same bar.</> : <>One bar per hub or zone, in the order of the table below.</>}>
                  <Bars rows={rows} held={held} pick={(r) => valueOf(r, c.market, c.sort)} unit={c.sort.unit} what={`${c.sort.name}, ${market.name.toLowerCase()}, ${when}`} />
                </ChartFrame>
              </ToolSection>

              <ToolSection title="The table" id="table"
                note={<>{market.name} prices by the hour, in each grid&apos;s own clock time (daylight saving included), from {w.start} to {w.end} (the end not included). Hours below zero and above USD 200 are shares of the hours held. The spread is read off the average day: the mean price of each hour of the day over the period, its four dearest hours less its four cheapest.
                  It is not the mean of each day&apos;s own spread, which is larger, since the dearest and the cheapest hours move from day to day.
                  The carbon intensity is the grid&apos;s generation over the same period (kg of CO2 per MWh), not the hub&apos;s. A heading sorts by its column.</>}>
                <ToolTable minWidth={700} caption={`Hub and zone prices compared, ${market.name.toLowerCase()}, ${when}`}
                  head={["Hub or zone", ...MEASURES.map((m) => (
                    <Link key={m.slug} href={`${href({ ...c, ...keep, sort: m.slug, dir: m.slug === c.sort.slug ? (c.dir === "asc" ? "desc" : "asc") : undefined })}#table`} className="underline" data-sort={m.slug}>
                      {m.slug === "spread" ? "Spread, 4 hours" : m.slug === "carbon" ? "Grid carbon" : m.slug === "high" ? "Hours above 200" : m.name}{m.slug === c.sort.slug ? (c.dir === "asc" ? " ↑" : " ↓") : ""}
                    </Link>)), "Hours held"]}
                  rows={[...rows.map((r) => ({ key: r.entity, cells: [nameCell(r), ...MEASURES.map((m) => cell(r, m)),
                    <span key="h"><N k={`${r.entity}|hours`}>{(c.market === "dam" ? r.dam_hours_held! : r.rtm_hours_held!).toLocaleString("en-US")}</N> of {(c.market === "dam" ? r.dam_hours_in_window! : r.rtm_hours_in_window!).toLocaleString("en-US")}</span>] })),
                    // session 7540: a held row stays in the table, last, every cell "license needed" (nothing dropped, no figure)
                    ...held.map((r) => ({ key: r.entity, cells: [<span key="n" data-held-row={r.entity}>{label(r)}</span>, ...MEASURES.map((m) => <span key={m.slug}>{HELD}</span>), <span key="h">{HELD}</span>] }))]} />
                {none.length ? <p className="mt-3 max-w-3xl text-sm" data-lacking={none.length}>Not held for {when} in the {market.name.toLowerCase()} market (fewer than {Math.round(file.near_hours * 100)} percent of its hours): {none.map(label).join("; ")}.</p> : null}
                <p className="mt-2 max-w-3xl text-xs">Grids in this view: {grids.join(", ")}. {noCarbon.length ? <span data-no-carbon={noCarbon.join(",")}>A grid&apos;s carbon intensity is given when at least {Math.round(file.near_days * 100)} percent of the period&apos;s days are held; not held for this period: {noCarbon.join(", ")}.</span> : null}</p>
              </ToolSection>
            </>
          )}

          <ToolSection title="Held, not shown" id="held"
            note={<>A price the warehouse holds but whose publisher&apos;s terms do not allow a figure to be derived from it and published is named here and carries no number. A license, or the publisher&apos;s word, is needed.</>}>
            <ToolTable words minWidth={520} caption="Hubs held and not shown, with the reason"
              head={["Hub", "Why it is not shown"]}
              rows={[...heldWho.map((g) => ({ key: `held-${g}`, cells: [`${g}, ${held.filter((h) => h.grid === g).length === 1 ? "1 hub or zone" : `${held.filter((h) => h.grid === g).length} hubs and zones`}`,
                  <span key="r" data-held-grid={g}>Held, not shown: license needed. {TABLE} is held for {licensePublishers(TABLE).join(", ")} from {LICENSE_FROM}: {LICENSE_TITLE_SUFFIX}. Each is named in the table and the chart, every figure &quot;license needed&quot;.</span>] })),
                ...file.held_not_shown.map((h) => ({ key: h.entity, cells: [`${h.grid}, ${h.node}`, <span key="r" data-hidden={h.entity}>Held, not shown: license needed. {h.reason}.</span>] })),
                ...file.not_held.map((g) => ({ key: g, cells: [g, <span key="r" data-not-held={g}>Not held: the warehouse has no {g} hub or zone price. {g}&apos;s prices are licensed.</span>] }))]} />
            {/* ruling alternative 1 (wip/alt-compare-1, not a default on main): the held grids' carbon intensity, EIA's public figure */}
            {file.held_carbon && Object.keys(file.held_carbon).length ? (
              <p className="mt-2 max-w-3xl text-sm" data-held-carbon="1">
                <span title="The grid's generation over the same period, kg of CO2 per MWh, from EIA-930 through the public table carbon_intensity_daily, which the Grid tool draws; the grid's prices stay license needed. Default on the site: license needed with the rest of the row.">The grid&apos;s carbon intensity
                of the grids held, {when}:</span>{" "}
                {Object.entries(file.held_carbon).map(([g, ws], i) => {
                  const x = ws[c.period];
                  return <span key={g} data-held-carbon-grid={g}>{i ? "; " : ""}{g} {x && x.intensity !== null ? <>{two(x.intensity)} kg CO2 per MWh ({x.days_held} of {x.days_due} days)</> : NOT}</span>;
                })}.
              </p>
            ) : null}
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
              <li>ERCOT&apos;s eight load zones. Their prices are held in the warehouse since 2015 and priced on <SiteLink href="/cost-of-power?view=allgrids">the cost of power page</SiteLink>; they are not in this comparison.</li>
            </ul>
          </Fold>
          <DecisionsBlock id="7018-compare" title="Decisions on this page (each with its default and its source on hover)" items={COMPARE_DECISIONS} />
          <SourceLine tables={[TABLE, "iso_hub_prices_history", "ercot_all_hub_prices_history", "iso_dam_hub_prices", "iso_rtm_hub_prices", "isone_dam_zone_prices", "isone_rtm_zone_prices_hourly", "nyiso_dam_zone_prices", "nyiso_rtm_zone_prices", "carbon_intensity_daily"]}
            note={<>Built {file.built.slice(0, 10)}. This page is in review and reads the site&apos;s own copy of the comparison.</>} />
        </div>
      </div>
    </ToolPage>
    </Brand>
  );
}
