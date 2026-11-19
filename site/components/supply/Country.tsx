import type { ReactNode } from "react";
import { AutoSubmitSelect } from "@/components/AutoSubmit";
import { Hint } from "@/components/demand/Hint";
import { LineChart, type Line } from "@/components/LineChart";
import { SiteLink as Link } from "@/components/SiteLink";
import { ToolTable } from "@/components/tool/ToolPage";
import { GRID_NAME, NEW_REGIONS, REGION_CODES, REGION_GRIDS, REGION_NAME, SOURCES, gwh, regionOf, signedGwh, whole } from "@/lib/countryfiles";
import {
  FIRST_MONTH, LARGE_GAP_PCT, READERS, defaultYear, inOrder, mixMonths, mixYear, monthCell, monthPoints, monthWords, monthsOfYear, neighboursOfYear, pairsOfYear,
  partnersOfYear, pct1, placeName, sharePoints, totalOfYear, yearOf, yearsOf,
  type FileHead, type IndexFile, type MatrixFile, type MixFile, type PairView, type Readers, type TradeFile,
} from "@/lib/countrytrade";
import { LICENSE_NEEDED, licenseNeeded, licenseTitle } from "@/lib/license";

// Session 8430 (chain 503, part D): "The whole country" on /supply. The page above it answers one question for a desk
// (tighter or looser) from the site's own file and draws the seven grids only through links to the Grid page. This
// section draws EIA's thirteen regions of the lower 48, with Canada and Mexico as neighbours, from the data machine's
// files (site/data/regions/, contract docs/state/page_files_regions.md): a region's net imports by month and by
// neighbour with the neighbour's own report of the same flow beside it and the gap between the two
// (trade/<region>.json); who trades with whom in a year, pair by pair, each side's report shown
// (trade_matrix.json); and the region's generation mix by month (mix/<region>.json). Two regions stand side by side.
// Add, never change: nothing above it on the page is touched (scripts/test-supply-pin.mjs holds that), and everything
// here stands between two marks so the pin can cut it out. Until a file is on the site its view says so and draws no
// figure. Facts and no view: the files' own figures and sums of their months; each pair's own flow and each region's
// own months; no region summed against another, no ranking, no share covered by imports.

type Query = Record<string, string | string[] | undefined>;

/** The regions drawn when the address names none: the first two of EIA's thirteen in EIA's own order. */
export const FIRST_A = REGION_CODES[0];
export const FIRST_B = REGION_CODES[1];

/** The regions held under license in this section: none. EIA's Form EIA-930 is public domain, each file's own license
 *  line says public, and the status file (data/license_status.json) is read for each table a file names. A code put
 *  here is drawn as blank cells with "license needed" on hover (for the owner's ruling: session 8430's report). */
export const REGIONS_HELD: string[] = [];
/** What the files hold and the section does not draw until the owner rules: each balancing authority's net imports as
 *  a share of its demand (trade_matrix.json, partners). True draws the column. */
export const SHOWN = { importShare: false };

/** Why a file is held, or null: its own license line is not "public", or a table it names is "license needed". */
export function heldWhy(file: FileHead | null): string | null {
  if (!file) return null;
  const t = (file.tables ?? []).find((x) => licenseNeeded(x));
  if (t) return `${LICENSE_NEEDED}: ${licenseTitle(t)}`;
  if (file.license && file.license !== "public") return `${LICENSE_NEEDED}: the file's license line reads "${file.license}"`;
  return null;
}
const regionHeld = (code: string) => (REGIONS_HELD.includes(code) ? `${LICENSE_NEEDED}: EIA's figures of ${placeName(code)} are held in this section until the owner rules` : null);

const N = ({ k, children }: { k: string; children: string }) => <span data-cn={k}>{children}</span>;
// the page's own words for a value that is not held, and its own look (app/supply/page.tsx, NH)
const NOT = ({ why }: { why: string }) => <span className="cursor-help whitespace-nowrap border-b border-dotted border-muted text-[11px] italic text-muted" title={why} data-not-held="1">not held yet</span>;
const Held = ({ why }: { why: string }) => <span className="inline-block min-w-8 cursor-help" title={why} data-license-held="1" aria-label={LICENSE_NEEDED}>&nbsp;</span>;
const Head = ({ words, why, mark }: { words: string; why: string; mark: string }) => <span title={why} data-wc-head={mark} className="cursor-help border-b border-dotted border-white">{words}</span>;
const NotBuilt = ({ file, what }: { file: string; what: string }) => (
  <p className="text-sm" data-wc-not-built={file}><Hint words="not built yet" why={`${what} Its file (site/data/regions/${file}) is written by the data machine from EIA's Form EIA-930 and is not on the site yet; until it is, no figure is drawn here.`} /></p>
);

const GAP_RULE = `A gap of ${LARGE_GAP_PCT} percent or more of the mean size of the two reports is marked as large. Default: ${LARGE_GAP_PCT} percent, this page's own choice (session 8430); no publisher's threshold stands behind it.`;
const SOURCE_WORDS = "Source: EIA Form EIA-930, interchange as each side filed it.";
/** A name's possessive: "Tennessee's", "Texas's", and "Carolinas'" for the one name that is a plural. */
const poss = (name: string) => (name === "Carolinas" ? "Carolinas'" : `${name}'s`);
const months = (held: number, of: number) => `${held} of the ${of} month${of === 1 ? "" : "s"} of the year in the file`;

function regionWords(code: string): string {
  if (code === "CAN" || code === "MEX") return `${placeName(code)}: a neighbour outside the lower 48. EIA's Form EIA-930 holds the flows across the border as the balancing authorities of the United States file them.`;
  const grids = (REGION_GRIDS[code] ?? []).map((g) => GRID_NAME[g] ?? g);
  return `${placeName(code)}, EIA's region ${code} of Form EIA-930.${grids.length ? ` ${grids.join(" and ")} ${grids.length > 1 ? "are" : "is"} among its balancing authorities.` : ""}${NEW_REGIONS.includes(code) ? " No page of the site drew this region before 19 November 2026: none of the seven grids is in it." : ""}`;
}

/** The gap's percent, marked and said in words where it is large. */
function GapPct({ k, pct, large, words }: { k: string; pct: number; large: boolean; words: string }) {
  return large
    ? <span className="cursor-help border-b border-dotted border-ink font-semibold" data-gap-large="1" title={`${words} That is large by this page's rule: ${LARGE_GAP_PCT} percent or more. Default: ${LARGE_GAP_PCT} percent, this page's own choice (session 8430); no publisher's threshold stands behind it. ${SOURCE_WORDS}`}><N k={k}>{pct1(pct)}</N></span>
    : <span className="cursor-help" title={`${words} ${GAP_RULE} ${SOURCE_WORDS}`}><N k={k}>{pct1(pct)}</N></span>;
}

const SERIES = ["series-1", "series-3", "series-5", "series-6", "series-8", "series-2", "series-4", "series-7"];

/** One region's net imports: its chart by month since July 2018, the year with each neighbour, and the year month by month. */
function Trade({ code, file, year, mark }: { code: string; file: TradeFile | null; year: string; mark: "a" | "b" }) {
  const name = placeName(code);
  const frame = (children: ReactNode) => <div data-wc-trade={mark} data-wc-region={code} className="min-w-0"><h4 className="mb-1 text-sm font-semibold" title={regionWords(code)}>{name}</h4>{children}</div>;
  if (!file) return frame(<NotBuilt file={`trade/${code.toLowerCase()}.json`} what={`${poss(name)} net imports by month and by neighbour.`} />);
  const why = heldWhy(file) ?? regionHeld(code);
  const at = monthsOfYear(file.months, year);
  const codes = inOrder(Object.keys(file.neighbors ?? {}));
  const nbHeld = (nb: string) => why ?? regionHeld(nb);
  const cell = (nb: string | null, v: ReactNode | null, missing: string): ReactNode => ((nb ? nbHeld(nb) : why) ? <Held why={(nb ? nbHeld(nb) : why)!} /> : v ?? <NOT why={missing} />);

  const lines: Line[] = why ? [] : [
    { label: "All neighbours", color: "accent", points: monthPoints(file.net_imports_mwh, file.months) },
    ...codes.filter((nb) => !regionHeld(nb)).map((nb, i) => ({ label: placeName(nb), color: SERIES[i % SERIES.length], points: monthPoints(file.neighbors![nb].net_imports_mwh, file.months) })),
  ].filter((l) => l.points.length);

  const total = totalOfYear(file, year);
  const yearRows = [
    ...neighboursOfYear(file, year).map((n) => {
      const facts = n.own && n.their && n.gap
        ? `${name} reported ${signedGwh(n.own.mwh)} GWh of net imports from ${n.name} in ${year}; ${n.name} reported the same flow as ${signedGwh(n.their.mwh)} GWh. Over the hours both reported, the gap is ${signedGwh(n.gap.mwh)} GWh${n.pct !== null ? `, ${pct1(n.pct)} percent of the mean size of the two reports over the ${n.compared} month${n.compared === 1 ? "" : "s"} that hold both` : ""}.`
        : "";
      return {
        key: n.code,
        cells: [
          <span key="n" data-wc-nb={n.code} title={regionWords(n.code)} {...(NEW_REGIONS.includes(n.code) ? { "data-wc-new": "1" } : {})}>{n.name}</span>,
          cell(n.code, n.own ? <span title={`${poss(name)} own report of its net imports from ${n.name} in ${year}, summed over ${months(n.own.held, n.own.of)}${n.hoursOwn ? `, ${whole(n.hoursOwn.mwh)} hours` : ""}. Above zero ${name} imported; below zero it exported.`}><N k={`trade|${code}|${year}|${n.code}|own`}>{signedGwh(n.own.mwh)}</N></span> : null,
            `The file holds no report by ${name} of its flow with ${n.name} in ${year}.`),
          cell(n.code, n.their ? <span title={`The same flow as ${n.name} reported it, with the same sign (above zero ${name} imported), summed over ${months(n.their.held, n.their.of)}${n.hoursTheir ? `, ${whole(n.hoursTheir.mwh)} hours` : ""}.`}><N k={`trade|${code}|${year}|${n.code}|their`}>{signedGwh(n.their.mwh)}</N></span> : null,
            `The file holds no report by ${n.name} of its flow with ${name} in ${year}.`),
          cell(n.code, n.gap ? <span title={`${poss(name)} report less ${poss(n.name)}, over the hours both reported${n.hoursBoth ? ` (${whole(n.hoursBoth.mwh)} hours)` : ""}, summed over ${months(n.gap.held, n.gap.of)}. Each of the two columns before it runs over that side's own hours, so this is not always their difference.`}><N k={`trade|${code}|${year}|${n.code}|gap`}>{signedGwh(n.gap.mwh)}</N></span> : null,
            `The file holds no hour of ${year} that both ${name} and ${n.name} reported.`),
          cell(n.code, n.pct !== null ? <GapPct k={`trade|${code}|${year}|${n.code}|gap_pct`} pct={n.pct} large={n.large} words={facts} /> : null,
            `A percent needs both reports and their gap in the same months of ${year}, and two reports that are not both zero.`),
          cell(n.code, n.own ? <span><N k={`trade|${code}|${year}|${n.code}|months`}>{String(n.own.held)}</N> of {n.own.of}</span> : null, `The file holds no month of ${year} for ${name} and ${n.name}.`),
        ],
      };
    }),
    {
      key: "all", highlight: true,
      cells: [
        <span key="n" data-wc-nb="all">All neighbours</span>,
        cell(null, total ? <span title={`${poss(name)} net imports from all its neighbours in ${year}, from its own side's reports, summed over ${months(total.held, total.of)}. The file leaves a month out when any neighbour holds fewer than half its hours; such a month is not in this sum.`}><N k={`trade|${code}|${year}|all`}>{signedGwh(total.mwh)}</N></span> : null,
          `The file holds no whole month of ${year} for ${poss(name)} net imports from all its neighbours.`),
        "", "", "",
        cell(null, total ? <span><N k={`trade|${code}|${year}|all|months`}>{String(total.held)}</N> of {total.of}</span> : null, `The file holds no whole month of ${year} for ${name}.`),
      ],
    },
  ];

  const monthRows = at.map((i) => {
    const m = file.months[i];
    const all = file.net_imports_mwh?.[i];
    return {
      key: m,
      cells: [
        <span key="m" data-wc-month={m}>{monthWords(m)}</span>,
        cell(null, typeof all === "number" ? <N k={`trade|${code}|${m}|all`}>{signedGwh(all)}</N> : null, `The file leaves ${monthWords(m)} out of ${poss(name)} total: a neighbour holds fewer than half the month's hours.`),
        ...codes.map((nb) => {
          const c = monthCell(file.neighbors![nb], i);
          const nbName = placeName(nb);
          if (c.own === null) return cell(nb, null, `The file holds no report by ${name} of its flow with ${nbName} in ${monthWords(m)}.`);
          const words = `${name} reported ${signedGwh(c.own)} GWh of net imports from ${nbName} in ${monthWords(m)}${c.hoursOwn !== null ? ` (${whole(c.hoursOwn)} hours)` : ""}. ${c.their !== null ? `${nbName} reported the same flow as ${signedGwh(c.their)} GWh${c.hoursTheir !== null ? ` (${whole(c.hoursTheir)} hours)` : ""}.` : `${poss(nbName)} report of the same flow is not held.`}${c.gap !== null ? ` Over the ${c.hoursBoth !== null ? `${whole(c.hoursBoth)} ` : ""}hours both reported, the gap is ${signedGwh(c.gap)} GWh${c.pct !== null ? `, ${pct1(c.pct)} percent of the mean size of the two reports` : ""}.` : ""}`;
          return cell(nb, c.large
            ? <span className="cursor-help border-b border-dotted border-ink font-semibold" data-gap-large="1" title={`${words} That is large by this page's rule: ${LARGE_GAP_PCT} percent or more. Default: ${LARGE_GAP_PCT} percent, this page's own choice (session 8430); no publisher's threshold stands behind it. ${SOURCE_WORDS}`}><N k={`trade|${code}|${m}|${nb}`}>{signedGwh(c.own)}</N></span>
            : <span className="cursor-help" title={`${words} ${SOURCE_WORDS}`}><N k={`trade|${code}|${m}|${nb}`}>{signedGwh(c.own)}</N></span>, "");
        }),
      ],
    };
  });

  return frame(
    <>
      {why ? <p className="text-sm" data-wc-chart-held={mark}><Held why={why} /> {LICENSE_NEEDED}</p>
        : lines.length ? <LineChart lines={lines} unit="GWh" x="month" height={240} ariaLabel={`${name}: net imports by month from ${monthWords(file.months[0] ?? FIRST_MONTH)}, all neighbours and each neighbour, GWh; above zero ${name} imports`} />
        : <p className="text-sm"><NOT why={`The file holds no month of net imports for ${name}.`} /></p>}
      <h5 className="mb-1 mt-3 text-sm font-semibold">Each neighbour in {year}, GWh</h5>
      {at.length ? (
        <>
          <ToolTable minWidth={600} caption={`${name}: net imports from each neighbour in ${year}, its own report, the neighbour's report and the gap`}
            head={[
              "Neighbour",
              <Head key="o" mark="own" words="Own report" why={`${poss(name)} net imports from the neighbour as ${poss(name)} side filed them: EIA's interchange with its sign turned, so above zero ${name} imported and below zero it exported. A year is the sum of the months the file holds. ${SOURCE_WORDS}`} />,
              <Head key="t" mark="their" words="Neighbour's report" why={`The same flow as the neighbour's side filed it, with the same sign. Both ends of a line file with EIA, each from its own meters and schedules; the two need not agree.`} />,
              <Head key="g" mark="gap" words="Gap" why="The own report less the neighbour's, over the hours both reported." />,
              <Head key="p" mark="gappct" words="Gap, percent" why={`The gap as a percent of the mean size of the two reports (the mean of their absolute values), over the months that hold both. ${GAP_RULE}`} />,
              <Head key="m" mark="months" words="Months held" why="The months of the year for which the file holds the own report, of the year's months in the file. A month that is not held is left out of the sums, never filled." />,
            ]}
            rows={yearRows} />
          <h5 className="mb-1 mt-3 text-sm font-semibold">{year} month by month, own report, GWh</h5>
          <ToolTable minWidth={220 + 110 * codes.length} caption={`${name}: net imports in each month of ${year}, from all neighbours and from each, by ${poss(name)} own report`}
            head={[
              "Month",
              <Head key="all" mark="month-all" words="All neighbours" why={`${poss(name)} net imports from all its neighbours in the month (EIA's Eastern month), from its own side's reports. The file leaves a month out when any neighbour holds fewer than half its hours.`} />,
              ...codes.map((nb) => <Head key={nb} mark={`month-${nb}`} words={placeName(nb)} why={`${poss(name)} net imports from ${placeName(nb)} in the month, by ${poss(name)} own report. Hover a figure for ${poss(placeName(nb))} report of the same flow, the gap and the hours each side held; a figure with a dotted line under it has a large gap. ${GAP_RULE}`} />),
            ]}
            rows={monthRows} />
        </>
      ) : <p className="text-sm"><NOT why={`The file holds no month of ${year} for ${name}: its months run from ${monthWords(file.months[0] ?? FIRST_MONTH)} to ${monthWords(file.months[file.months.length - 1] ?? FIRST_MONTH)}.`} /></p>}
    </>,
  );
}

/** The pairs of a year as table rows: which side sent and which received, each side's report, the mean and the gap. */
function pairRows(pairs: PairView[], year: string, kind: "pair" | "bapair", nameOf: (c: string) => string, tip: (c: string) => string, heldOf: (c: string) => string | null, lit: string[], pick?: (c: string) => string | null) {
  return pairs.map((p) => {
    const h = heldOf(p.a) ?? heldOf(p.b);
    const blank = (v: ReactNode | null, missing: string) => (h ? <Held why={h} /> : v ?? <NOT why={missing} />);
    const one = p.from ?? p.a, two = p.to ?? p.b;
    const facts = p.fromReport !== null && p.toReport !== null && p.gap !== null
      ? `${nameOf(one)} reported ${gwh(p.fromReport)} GWh sent to ${nameOf(two)} in ${year}; ${nameOf(two)} reported the same flow as ${gwh(p.toReport)} GWh. The gap is ${signedGwh(p.gap)} GWh${p.pct !== null ? `, ${pct1(p.pct)} percent of the mean size of the two reports` : ""}.`
      : "";
    const named = (c: string) => { const href = pick?.(c); return href ? <Link href={href} title={tip(c)}>{nameOf(c)}</Link> : <span title={tip(c)}>{nameOf(c)}</span>; };
    const other = (c: string) => `${nameOf(c)} counted the year's net flow the other way.`;
    return {
      key: p.key, highlight: lit.includes(p.a) || lit.includes(p.b),
      cells: [
        <span key="s" data-wc-pair={p.key} data-wc-kind={kind}>{p.from ? named(p.from) : <>{named(p.a)} and {named(p.b)}</>}</span>,
        p.to ? named(p.to) : p.mean === 0 ? "no net flow" : <NOT why={`The file gives no direction for ${nameOf(p.a)} and ${nameOf(p.b)} in ${year}: it holds no mean of the two reports.`} />,
        blank(p.fromReport !== null ? <span title={`${poss(nameOf(one))} report of the power it sent to ${nameOf(two)} over ${year}, as the file gives it.${p.fromReport < 0 ? ` Below zero: ${other(one)}` : ""}`}><N k={`${kind}|${p.key}|${year}|from_report`}>{gwh(p.fromReport)}</N></span> : null, `The file holds no report by ${nameOf(one)} of this flow in ${year}.`),
        blank(p.toReport !== null ? <span title={`${poss(nameOf(two))} report of the power ${nameOf(one)} sent to it over ${year}, as the file gives it.${p.toReport < 0 ? ` Below zero: ${other(two)}` : ""}`}><N k={`${kind}|${p.key}|${year}|to_report`}>{gwh(p.toReport)}</N></span> : null, `The file holds no report by ${nameOf(two)} of this flow in ${year}.`),
        blank(p.mean !== null ? <N k={`${kind}|${p.key}|${year}|mean`}>{gwh(p.mean)}</N> : null, `The file holds no mean of the two reports for this pair in ${year}.`),
        blank(p.gap !== null ? <span title={`${poss(nameOf(one))} report less ${poss(nameOf(two))}.`}><N k={`${kind}|${p.key}|${year}|gap`}>{signedGwh(p.gap)}</N></span> : null, `The file holds no gap for this pair in ${year}: one side's report is not held.`),
        blank(p.pct !== null ? <GapPct k={`${kind}|${p.key}|${year}|gap_pct`} pct={p.pct} large={p.large} words={facts} /> : null, "A percent needs both reports and their gap, and two reports that are not both zero."),
      ],
    };
  });
}
const pairHead = (who: string) => [
  <Head key="s" mark="sent" words="Sent" why={`Over the year the net flow between the two ${who} ran from this one to the other, by the file's own direction (the sign of the mean of the two reports).`} />,
  <Head key="t" mark="received" words="Received" why="The one the net flow ran to over the year, by the same direction." />,
  <Head key="a" mark="from-report" words="Sender's report, GWh" why={`The flow over the year as the sending side filed it with EIA. A figure below zero says that side counted the year's net flow the other way. ${SOURCE_WORDS}`} />,
  <Head key="b" mark="to-report" words="Receiver's report, GWh" why="The same flow as the receiving side filed it. Both ends of a line file with EIA, each from its own meters and schedules; the two need not agree." />,
  <Head key="m" mark="mean" words="Mean, GWh" why="The mean of the two reports, as the file gives it." />,
  <Head key="g" mark="gap" words="Gap, GWh" why="The sender's report less the receiver's, as the file gives it." />,
  <Head key="p" mark="gappct" words="Gap, percent" why={`The gap as a percent of the mean size of the two reports (the mean of their absolute values). ${GAP_RULE}`} />,
];

/** Who trades with whom in a year: the pairs of regions, the pairs of balancing authorities and each authority's partners. */
function Matrix({ file, index, year, a, b, pick }: { file: MatrixFile | null; index: IndexFile | null; year: string; a: string; b: string | null; pick: (code: string) => string }) {
  if (!file) return <NotBuilt file="trade_matrix.json" what="Each pair of regions and of balancing authorities in a year, with each side's report of the flow between them." />;
  const why = heldWhy(file);
  const heldOf = (c: string) => why ?? regionHeld(c);
  const bas = new Map((index?.bas ?? []).map((x) => [x.code, x]));
  const baTip = (c: string) => { const x = bas.get(c); return x ? `${x.name ?? c}, balancing authority ${c}${x.region ? `, in EIA's region ${placeName(x.region)}` : ""}.` : c === "CAN" || c === "MEX" ? regionWords(c) : `Balancing authority ${c}, by its EIA-930 code. Its name stands here once the index of the regions (site/data/regions/index.json) is on the site.`; };
  const baHeld = (c: string) => why ?? regionHeld(bas.get(c)?.region ?? c);
  const regionPairs = pairsOfYear(file.region_pairs, year), baPairs = pairsOfYear(file.ba_pairs, year), partners = partnersOfYear(file, year);
  const lit = [a, ...(b ? [b] : [])];
  const litBas = [...bas.values()].filter((x) => x.region && lit.includes(x.region)).map((x) => x.code);
  const list = (codes: string[] | null, ba: string, what: string) => (baHeld(ba) ? <Held why={baHeld(ba)!} /> : codes === null ? <NOT why={`The file holds no list of ${ba}'s partners by ${what} in ${year}.`} /> : codes.length ? <span title={codes.map((c) => bas.get(c)?.name ?? placeName(c)).join("; ")}>{codes.join(", ")}</span> : "none");
  return (
    <div data-wc-matrix={year}>
      {regionPairs.length ? (
        <ToolTable minWidth={860} caption={`Each pair of regions in ${year}: which sent and which received, each side's report, their mean and the gap`}
          head={pairHead("regions")} rows={pairRows(regionPairs, year, "pair", placeName, regionWords, heldOf, lit, (c) => (regionOf(c) ? pick(c) : null))} />
      ) : <p className="text-sm"><NOT why={`The file holds no pair of regions for ${year}.`} /></p>}
      <details className="mt-3 border-t border-rule pt-1" data-wc-fold="bapairs">
        <summary className="cursor-pointer text-sm font-semibold">Balancing authorities, pair by pair, {year}: <span data-cn={`bapairs|${year}|n`}>{String(baPairs.length)}</span> pairs</summary>
        {baPairs.length ? (
          <ToolTable minWidth={860} caption={`Each pair of balancing authorities in ${year}: which sent and which received, each side's report, their mean and the gap`}
            head={pairHead("balancing authorities")} rows={pairRows(baPairs, year, "bapair", (c) => c, baTip, baHeld, litBas)} />
        ) : <p className="text-sm"><NOT why={`The file holds no pair of balancing authorities for ${year}.`} /></p>}
      </details>
      <details className="mt-2 border-t border-rule pt-1" data-wc-fold="partners">
        <summary className="cursor-pointer text-sm font-semibold">Each balancing authority&apos;s partners, {year}: <span data-cn={`partners|${year}|n`}>{String(partners.length)}</span> authorities</summary>
        {partners.length ? (
          <ToolTable minWidth={640} words caption={`Each balancing authority's partners in ${year}, by gross and by net exchange`}
            head={[
              "Authority",
              <Head key="g" mark="by-gross" words="Partners by gross exchange" why="The authorities it exchanged power with over the year, in the file's order: by gross exchange (the power sent and the power received, added), the largest first. Hover a list for the names. Source: ERW table ba_trade_partners, from EIA Form EIA-930." />,
              <Head key="n" mark="by-net" words="Partners by net exchange" why={`The same partners in the file's order by net exchange over the year.${SHOWN.importShare ? "" : " The file also holds each authority's net imports as a share of its demand; that share is not drawn in this section until the owner rules."}`} />,
              ...(SHOWN.importShare ? [<Head key="s" mark="share" words="Net imports, percent of demand" why="The authority's net imports over the year as a percent of its demand, as the file gives it (ERW table ba_trade_partners). Below zero it was a net exporter." />] : []),
            ]}
            rows={partners.map((p) => ({
              key: p.ba, highlight: litBas.includes(p.ba),
              cells: [
                <span key="b" data-wc-partners={p.ba} title={baTip(p.ba)}>{p.ba}</span>,
                list(p.byGross, p.ba, "gross exchange"), list(p.byNet, p.ba, "net exchange"),
                ...(SHOWN.importShare ? [baHeld(p.ba) ? <Held why={baHeld(p.ba)!} /> : p.sharePct !== null ? <N k={`partners|${p.ba}|${year}|share`}>{pct1(p.sharePct)}</N> : <NOT why={`The file holds no share for ${p.ba} in ${year}.`} />] : []),
              ],
            }))} />
        ) : <p className="text-sm"><NOT why={`The file lists no balancing authority's partners for ${year}.`} /></p>}
      </details>
    </div>
  );
}

/** One region's generation mix: each source's share of net generation by month, charted over every month held and
 *  tabled for the year. */
function Mix({ code, file, year, mark }: { code: string; file: MixFile | null; year: string; mark: "a" | "b" }) {
  const name = placeName(code);
  const frame = (children: ReactNode) => <div data-wc-mix={mark} data-wc-region={code} className="min-w-0"><h4 className="mb-1 text-sm font-semibold" title={regionWords(code)}>{name}</h4>{children}</div>;
  if (!file) return frame(<NotBuilt file={`mix/${code.toLowerCase()}.json`} what={`${poss(name)} generation by source, month by month.`} />);
  const why = heldWhy(file) ?? regionHeld(code);
  const rows = mixMonths(file, year);
  const yr = mixYear(rows);
  const all = Object.keys(file.months ?? {}).sort();
  const lines: Line[] = why ? [] : SOURCES.map((s) => ({ label: s.label, color: s.color, points: sharePoints(file, s.key) })).filter((l) => l.points.length);
  const cell = (v: ReactNode | null, missing: string): ReactNode => (why ? <Held why={why} /> : v ?? <NOT why={missing} />);
  const tableRows = [
    ...rows.map((r) => ({
      key: r.month,
      cells: [
        <span key="m" data-wc-month={r.month}>{monthWords(r.month)}</span>,
        ...SOURCES.map((s) => {
          const share = r.share[s.key], e = r.mwh[s.key];
          return cell(share !== null ? <span title={`${s.label} in ${name}, ${monthWords(r.month)}: ${e !== null ? `${gwh(e)} GWh` : "energy not held"}${r.net !== null ? ` of ${gwh(r.net)} GWh of net generation` : ""}.`}><N k={`mix|${code}|${r.month}|${s.key}`}>{pct1(share)}</N></span> : null,
            `The file holds no ${s.label.toLowerCase()} for ${name} in ${monthWords(r.month)}.`);
        }),
        cell(r.net !== null ? <N k={`mix|${code}|${r.month}|net`}>{gwh(r.net)}</N> : null, `The file holds no net generation for ${name} in ${monthWords(r.month)}.`),
        cell(r.daysHeld !== null ? <span>{r.daysHeld}{r.daysInMonth !== null ? ` of ${r.daysInMonth}` : ""}</span> : null, "The file does not say how many days of the month it holds."),
      ],
    })),
    {
      key: "year", highlight: true,
      cells: [
        <span key="y" data-wc-month={year}>{year}, {rows.length} month{rows.length === 1 ? "" : "s"}</span>,
        ...SOURCES.map((s) => cell(yr.share[s.key] !== null ? <span title={`${s.label}'s energy over the ${yr.months[s.key]} month${yr.months[s.key] === 1 ? "" : "s"} of ${year} that hold it, as a percent of the net generation of those same months.`}><N k={`mix|${code}|${year}|${s.key}`}>{pct1(yr.share[s.key]!)}</N></span> : null,
          `The file holds no ${s.label.toLowerCase()} for ${name} in any month of ${year}.`)),
        cell(yr.net ? <N k={`mix|${code}|${year}|net`}>{gwh(yr.net.mwh)}</N> : null, `The file holds no net generation for ${name} in ${year}.`),
        "",
      ],
    },
  ];
  return frame(
    <>
      {why ? <p className="text-sm" data-wc-chart-held={mark}><Held why={why} /> {LICENSE_NEEDED}</p>
        : lines.length ? <LineChart lines={lines} unit="percent" x="month" height={240} ariaLabel={`${name}: each source's share of net generation by month, ${all.length ? `${monthWords(all[0])} to ${monthWords(all[all.length - 1])}` : ""}, percent`} />
        : <p className="text-sm"><NOT why={`The file holds no month of generation by source for ${name}.`} /></p>}
      <h5 className="mb-1 mt-3 text-sm font-semibold">{year}, share of net generation, percent</h5>
      {rows.length ? (
        <ToolTable minWidth={900} caption={`${name}: each source's share of net generation in each month of ${year}, percent`}
          head={[
            "Month",
            ...SOURCES.map((s) => <Head key={s.key} mark={`mix-${s.key}`} words={s.label} why={`${s.label}: its share of the region's net generation in the month, as the file writes it. ${s.key === "storage" ? "Storage is below zero in a month it charged more than it discharged. " : ""}${s.key === "hydro" ? "Hydro includes pumped storage. " : ""}${s.key === "other" ? "Other is petroleum, geothermal, other and unknown sources. " : ""}Hover a figure for the energy. Source: EIA Form EIA-930, generation by energy source.`} />),
            <Head key="net" mark="mix-net" words="Net generation, GWh" why="The region's net generation in the month. A month is in the file when at least 90 percent of its days are complete." />,
            <Head key="d" mark="mix-days" words="Days held" why="The days of the month whose every hour the file holds, of the days in the month." />,
          ]}
          rows={tableRows} />
      ) : <p className="text-sm"><NOT why={`The file holds no month of ${year} for ${name}${all.length ? `: its months run from ${monthWords(all[0])} to ${monthWords(all[all.length - 1])}` : ""}.`} /></p>}
    </>,
  );
}

/** The section as drawn from what `read` gives (the site's files, or a test's). `keep` carries the page's own choices
 *  (its groups and its open chart) through the form and the links, so a choice here moves nothing above. */
export function Country({ q, keep = {}, read = READERS }: { q: { region?: string; b?: string; year?: string }; keep?: { g?: string; s?: string }; read?: Readers }) {
  const open = (children: ReactNode) => (
    <>
      <section data-whole-country="supply" id="whole-country" className="mb-7 scroll-mt-4">
        <h2 className="mb-1 border-b border-accent pb-0.5 font-serif text-lg text-accent">The whole country</h2>
        {children}
      </section>
      <span data-whole-country-end="1"></span>
    </>
  );
  const a = regionOf(q.region) ?? FIRST_A;
  const bAsked = q.b === undefined ? FIRST_B : regionOf(q.b);
  const b = bAsked && bAsked !== a ? bAsked : null;
  const shown = [a, ...(b ? [b] : [])];
  // a trade file with no list of months cannot be read as the contract's form: it is treated as not built
  const formed = (f: TradeFile | null) => (f && Array.isArray(f.months) ? f : null);
  const trade = Object.fromEntries(shown.map((c) => [c, formed(read.trade(c))])) as Record<string, TradeFile | null>;
  const mix = Object.fromEntries(shown.map((c) => [c, read.mix(c)])) as Record<string, MixFile | null>;
  const matrix = read.matrix();
  const held: FileHead[] = [...shown.flatMap((c) => [trade[c], mix[c]]), matrix].filter((f): f is TradeFile | MixFile | MatrixFile => !!f);
  // with none of the chosen regions' files held, any region's file says whether the folder is built at all
  if (!held.length && !REGION_CODES.some((c) => read.trade(c) || read.mix(c))) {
    return open(
      <p className="text-sm" data-wc-state="not-built">
        <Hint words="not built yet" why={`This section draws EIA's thirteen regions of the lower 48 (${REGION_CODES.map((c) => REGION_NAME[c]).join(", ")}), with Canada and Mexico as neighbours: each region's net imports by month and by neighbour since July 2018 with each side's report, who trades with whom in a year, and each region's generation mix by month. Its files (site/data/regions/trade/, trade_matrix.json and mix/) are written by the data machine from Form EIA-930 and are not on the site yet; until they are, no figure is drawn here.`} />
      </p>,
    );
  }
  const index = read.index();
  const years = [...new Set([...shown.flatMap((c) => [...yearsOf(trade[c]?.months), ...yearsOf(Object.keys(mix[c]?.months ?? {}))]), ...(matrix?.years ?? []).map(String)])].sort();
  const built = held.map((f) => f.built ?? "").sort().at(-1) || undefined;
  const first = defaultYear(years, built);
  const year = yearOf(q.year, years) ?? first ?? "";
  const href = (patch: { region?: string; b?: string | null }) => {
    const p = new URLSearchParams();
    if (keep.g) p.set("g", keep.g);
    if (keep.s) p.set("s", keep.s);
    const ra = patch.region ?? a, rb = patch.b === undefined ? b : patch.b;
    p.set("region", ra.toLowerCase());
    p.set("b", rb && rb !== ra ? rb.toLowerCase() : "none");
    if (year) p.set("year", year);
    return `/supply?${p.toString()}#whole-country`;
  };
  const options = REGION_CODES.map((c) => ({ value: c.toLowerCase(), label: REGION_NAME[c] }));
  const tables = [...new Set(held.flatMap((f) => f.tables ?? []))];
  const method = (held.find((f) => f.method)?.method ?? "docs/methods/supply_and_trade.md").replace(/^docs\/methods\//, "").replace(/\.md$/, "");
  const two = b ? "grid gap-6 lg:grid-cols-2" : "";

  return open(
    <div data-wc-state="drawn" data-wc-a={a} data-wc-b={b ?? ""} data-wc-year={year}>
      <p className="mb-2 max-w-3xl text-sm" data-wc-lead="1">
        EIA&apos;s thirteen regions of the lower 48, with Canada and Mexico as neighbours, since July 2018:{" "}
        <Hint words="net imports" why={`A region's net imports are EIA's interchange with each neighbour with its sign turned: above zero the region imported, below zero it exported. Months are EIA's Eastern months. A region's figure is EIA's sum of its balancing authorities, so it is not the figure of one of the seven grids above even where they cover nearly the same ground. ${SOURCE_WORDS}`} />{" "}
        by month and by neighbour,{" "}
        <Hint words="each side's report" why={`Both ends of a line between two regions file the same flow with EIA, each from its own meters and schedules, and the two filings need not agree. The section shows both and the gap between them. ${GAP_RULE}`} />{" "}
        of every flow, and the generation mix by month.{" "}
        <Hint words="Six regions are new to the site" why={`${NEW_REGIONS.map((c) => REGION_NAME[c]).join(", ")}: none of the seven grids of the tables above is in them, so no page drew them before 19 November 2026.`} />.{" "}
        <Hint words="How a figure here is formed" why="Each figure is the file's own or a sum of the file's months, MWh shown as GWh (1,000 MWh). A month the file does not hold is left out of a sum and counted beside it, never filled or scaled. Each pair's own flow and each region's own months are shown; no region is summed against another." />
      </p>
      <form method="get" action="/supply#whole-country" className="mb-3 flex flex-wrap items-end gap-3 text-sm" data-wc-form="1">
        {keep.g ? <input type="hidden" name="g" value={keep.g} /> : null}
        {keep.s ? <input type="hidden" name="s" value={keep.s} /> : null}
        <AutoSubmitSelect name="region" value={a.toLowerCase()} options={options} label="Region A" />
        <AutoSubmitSelect name="b" value={b ? b.toLowerCase() : "none"} options={[{ value: "none", label: "None" }, ...options]} label="Region B" />
        <AutoSubmitSelect name="year" value={year} options={[...years].reverse().map((y) => ({ value: y, label: y }))} label="Year" />
        <button type="submit" className="border border-rule bg-white px-3 py-1 text-sm">Show</button>
        <Hint words="The regions and the year drawn first" why={`Region A is ${REGION_NAME[FIRST_A]} and Region B is ${REGION_NAME[FIRST_B]}: the first two of EIA's thirteen regions in EIA's own order of codes.${first ? ` The year is ${first}: the last calendar year that had ended when the files were built, the newest they can hold whole (the newest year held when they hold no such year).` : ""} Defaults: this page's own choices (session 8430); no publisher's rule stands behind them. The charts run over every month held whatever the year; the year sets the tables.`} />
      </form>

      <h3 className="mb-1 mt-4 font-serif text-base text-accent" id="wc-trade">Net imports by month and by neighbour</h3>
      <div className={two}>
        <Trade code={a} file={trade[a]} year={year} mark="a" />
        {b ? <Trade code={b} file={trade[b]} year={year} mark="b" /> : null}
      </div>

      <h3 className="mb-1 mt-6 font-serif text-base text-accent" id="wc-pairs">Who trades with whom{year ? `, ${year}` : ""}</h3>
      <Matrix file={matrix} index={index} year={year} a={a} b={b} pick={(c) => href({ region: c })} />

      <h3 className="mb-1 mt-6 font-serif text-base text-accent" id="wc-mix">
        Generation mix by month{" "}
        <span className="font-sans text-xs font-normal"><Hint words="shares of net generation" why="The tables above this section draw no generation mix of their own: they link each of the seven grids' Mix view on the Grid page. For a region, each source's share of net generation by month stands here, from the region's own file: a chart over every month held and a table of the chosen year. The year's row is each source's energy over the year's held months as a percent of the net generation of those same months." /></span>
      </h3>
      <div className={two}>
        <Mix code={a} file={mix[a]} year={year} mark="a" />
        {b ? <Mix code={b} file={mix[b]} year={year} mark="b" /> : null}
      </div>

      <p className="mt-3 text-xs text-muted" data-wc-source="1">
        Source: EIA Form EIA-930 (public domain), by region and by balancing authority{tables.length ? <>; ERW table{tables.length > 1 ? "s" : ""} {tables.map((t, i) => <span key={t}>{i ? ", " : ""}<Link href={`/data#${t}`} className="font-mono" gate="plain">{t}</Link></span>)}</> : null}
        {built ? <>; files built {built.slice(0, 10)}</> : null}. <Link href={`/data/methods/${method}`}>Method</Link>.
      </p>
    </div>,
  );
}

/** What /supply mounts: the address's choices read, the section drawn from the site's files. */
export async function SupplyCountry({ searchParams, keep }: { searchParams?: Promise<Query>; keep?: { g?: string; s?: string } }) {
  const sp = searchParams ? await searchParams : {};
  const one = (v: string | string[] | undefined) => (Array.isArray(v) ? v[0] : v);
  return <Country q={{ region: one(sp.region), b: one(sp.b), year: one(sp.year) }} keep={keep} />;
}
