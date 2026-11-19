import type { ReactNode } from "react";
import { AutoSubmitSelect } from "@/components/AutoSubmit";
import { Hint } from "@/components/demand/Hint";
import { LineChart, type Line } from "@/components/LineChart";
import { SiteLink as Link } from "@/components/SiteLink";
import { ToolTable } from "@/components/tool/ToolPage";
import {
  ABROAD, GRID_NAME, REACHED_PCT, REGION_CODES, REGION_NAME, SOURCES, STORAGE_FROM, apartSources, baselineFirstHour, baselineOf, drawnByDay, eventRegionsFile, gwh, heldApart, lineGap,
  localHour, pairs, points, reached, regionOf, regionZones, shortSources, signedGwh, signedPct, signedWhole, summarize, utcHour, whole, NEW_REGIONS,
  type Against, type EventRegionsFile, type RegionSummary,
} from "@/lib/countryfiles";
import { LICENSE_NEEDED, licenseNeeded, licenseTitle } from "@/lib/license";

// Session 8410 (chain 503, part B): "The whole country" on each event page, and the line of regions on the index.
// The older sections of an event page draw up to seven grids; this one draws EIA's thirteen regions of the lower 48
// from the data machine's file of the event (site/data/regions/events/<event>.json, contract
// docs/state/page_files_regions.md): what demand, generation by source and net imports did across the window against
// the baseline the file names, the power between each pair of regions, and a choice of one or two regions whose hours
// are drawn. Add, never change: nothing above it on the page is touched (scripts/test-events-pin.mjs holds that), and
// everything here stands between two marks so the pin can cut it out. Until the file is on the site the section says
// so and draws no figure. Facts and no view: sums and means of what the file holds; no share of a shock covered by
// imports, no ledger of regions that gave and took.

type Query = Record<string, string | string[] | undefined>;
export type PageProps = { searchParams?: Promise<Query> };

/** The regions held under license on these pages: none. EIA's Form EIA-930 is public domain, the file's own license
 *  line says public, and the status file (data/license_status.json) is read for each table the file names. A code put
 *  here is drawn as a blank cell with "license needed" on hover (for the owner's ruling: session 8410's report). */
export const REGIONS_HELD: string[] = [];

/** Why a file is held, or null: its own license line is not "public", or a table it names is "license needed". */
export function heldWhy(file: EventRegionsFile): string | null {
  const t = (file.tables ?? []).find((x) => licenseNeeded(x));
  if (t) return `${LICENSE_NEEDED}: ${licenseTitle(t)}`;
  if (file.license && file.license !== "public") return `${LICENSE_NEEDED}: the file's license line reads "${file.license}"`;
  return null;
}

const N = ({ k, children }: { k: string; children: string }) => <span data-n={k}>{children}</span>;
// session 8470 (the decisions, part E): the switch from hours to days carries its default and its source on hover
const BY_DAY_WORDS = "A window of 21 days or less is drawn by hour and a longer one by day. Default: 21 days, this page's own choice (session 8410); no publisher's rule stands behind it.";
const NOT = ({ why }: { why: string }) => <span className="cursor-help text-muted" title={why} data-not-held="1">not held</span>;
const Held = ({ why }: { why: string }) => <span className="inline-block min-w-8 cursor-help" title={why} data-license-held="1" aria-label={LICENSE_NEEDED}>&nbsp;</span>;
const Head = ({ words, why, mark }: { words: string; why: string; mark?: string }) => <span title={why} data-wc-head={mark ?? "1"} className="cursor-help border-b border-dotted border-white">{words}</span>;

function regionWords(r: RegionSummary): string {
  const grids = r.grids.map((g) => GRID_NAME[g] ?? g);
  return `${r.name}, EIA's region ${r.code} of Form EIA-930.${grids.length ? ` ${grids.join(" and ")} ${grids.length > 1 ? "are" : "is"} among its balancing authorities.` : ""}${r.isNew ? " No page of the site drew this region before 19 November 2026: none of the seven grids is in it." : ""}`;
}

const againstTip = (what: string, a: Against, unit = "GWh") =>
  `${what}: ${gwh(a.mwh)} ${unit} over the window, ${gwh(a.base_mwh)} ${unit} in the baseline, ${signedGwh(a.diff_mwh)} ${unit}${a.pct !== null ? ` (${signedPct(a.pct)} percent)` : ""}, over the ${whole(a.hours)} hours both hold.`;

/** The line of the index: how many regions an event reached, by the rule of `reached`. */
export function RegionsReached({ event }: { event: string }) {
  const file = eventRegionsFile(event);
  let body: ReactNode;
  if (!file) {
    body = <>Regions reached: <Hint words="not built yet" why={`The file of this event for EIA's thirteen regions (site/data/regions/events/${event}.json) is not on the site yet. The data machine writes it from Form EIA-930.`} /></>;
  } else if (heldWhy(file)) {
    body = <>Regions reached: <Held why={heldWhy(file)!} /></>;
  } else {
    const rows = summarize(file).filter((r) => !REGIONS_HELD.includes(r.code));
    const hit = reached(rows);
    const withDemand = rows.filter((r) => r.demand && r.demand.pct !== null);
    // session 8470 (the real files): a region's percent says on how many hours it rests where that is fewer than the
    // window's, and a region left out of the count is named with the reason
    const n = file.hours.n;
    const list = withDemand.map((r) => `${r.name} ${signedPct(r.demand!.pct!)}${r.demand!.hours < n ? ` (${whole(r.demand!.hours)} of ${whole(n)} hours)` : ""}`).join("; ");
    const left = rows.filter((r) => !(r.demand && r.demand.pct !== null));
    const leftWords = left.length ? ` Not counted, the file holding no hour of their demand with its baseline in the window: ${left.map((r) => r.name).join(", ")}.` : "";
    body = (
      <>
        Reached <strong><N k={`reached|${event}|n`}>{String(hit.length)}</N></strong> of <N k={`reached|${event}|of`}>{String(withDemand.length)}</N> regions:{" "}
        <Hint words={hit.length ? hit.map((r) => r.name).join(", ") : "none"}
          why={`A region is counted when its demand over the window (${file.start} to ${file.end}) stood ${REACHED_PCT} percent or more from the baseline, above or below. Default: ${REACHED_PCT} percent, this page's own choice (session 8410); no publisher's threshold stands behind it. Demand over the window against the baseline, percent: ${list}.${leftWords} Source: EIA Form EIA-930, by region.`} />.{" "}
        <Link href={`/events/${event.replace(/_/g, "-")}#whole-country`}>The whole country</Link>
      </>
    );
  }
  return <><span data-regions-reached={event} className="mt-1 block text-sm">{body}</span><span data-regions-reached-end="1"></span></>;
}

function Charts({ file, code, mark }: { file: EventRegionsFile; code: string; mark: "a" | "b" }) {
  const r = file.regions[code];
  const name = REGION_NAME[code];
  if (!r) return <div data-wc-charts={mark} data-wc-region={code}><h4 className="mb-1 text-base">{name}</h4><p className="text-sm"><NOT why={`The file holds no hours for ${name} in this window.`} /></p></div>;
  const h = file.hours;
  const by = drawnByDay(h) ? "day (the mean of the day's held hours, UTC days)" : "hour (UTC)";
  const gap = lineGap(h);  // session 8470: an hour (or a day) the file does not hold breaks the line
  const demand: Line[] = [
    { label: "The event", color: "accent", gap, points: points(r.demand_mw, h) },
    { label: "The baseline", color: "muted", gap, points: points(r.baseline?.demand_mw, h) },
  ];
  const imports: Line[] = [
    { label: "The event", color: "accent", gap, points: points(r.net_imports_mw, h) },
    { label: "The baseline", color: "muted", gap, points: points(r.baseline?.net_imports_mw, h) },
  ];
  const gen: Line[] = SOURCES.map((s) => ({ label: s.label, color: s.color, gap, points: points(r.gen?.[s.key], h) })).filter((l) => l.points.length);
  const none = (what: string) => <p className="text-sm"><NOT why={`The file holds no ${what} for ${name} in this window.`} /></p>;
  return (
    <div data-wc-charts={mark} data-wc-region={code} className="min-w-0">
      <h4 className="mb-1 text-base">{name}</h4>
      <h5 className="mt-2 text-sm font-semibold">Demand, MW</h5>
      {demand[0].points.length ? <LineChart lines={demand} unit="MW" height={220} ariaLabel={`${name}: demand by ${by}, ${file.start} to ${file.end}, the event and the baseline`} /> : none("demand")}
      <h5 className="mt-3 text-sm font-semibold">Generation by source, MW</h5>
      {gen.length ? <LineChart lines={gen} unit="MW" height={240} ariaLabel={`${name}: generation by source by ${by}, ${file.start} to ${file.end}`} /> : none("generation by source")}
      <h5 className="mt-3 text-sm font-semibold">Net imports, MW</h5>
      {imports[0].points.length ? <LineChart lines={imports} unit="MW" height={200} ariaLabel={`${name}: net imports by ${by}, ${file.start} to ${file.end}, the event and the baseline; above zero the region imports`} /> : none("net imports")}
    </div>
  );
}

/** The section as drawn from a file (or from none). `first` and `second` are the regions drawn when the address names none. */
export function WholeCountry({ event, path, file, q, first, second, firstWhy }: {
  event: string; path: string; file: EventRegionsFile | null; q: { region?: string; b?: string }; first: string; second?: string; firstWhy: string;
}) {
  const open = (children: ReactNode) => (
    <>
      <section data-whole-country={event} id="whole-country" className="mb-10">
        <div className="mb-3 flex flex-wrap items-baseline justify-between gap-2 border-b border-rule pb-1"><h2 className="text-xl">The whole country</h2></div>
        {children}
      </section>
      <span data-whole-country-end="1"></span>
    </>
  );
  if (!file) {
    return open(
      <p className="text-sm" data-wc-state="not-built">
        <Hint words="not built yet" why={`This section draws EIA's thirteen regions of the lower 48 across the event: ${REGION_CODES.map((c) => REGION_NAME[c]).join(", ")}. Its file (site/data/regions/events/${event}.json) is written by the data machine from Form EIA-930 and is not on the site yet; until it is, no figure is drawn here.`} />
      </p>,
    );
  }
  const why = heldWhy(file);
  const rows = summarize(file);
  const held = (code: string) => (why ? why : REGIONS_HELD.includes(code) ? `${LICENSE_NEEDED}: EIA's figures of this region are held on this page until the owner rules` : null);
  const base = baselineOf(file);
  const a = regionOf(q.region) ?? first;
  const bAsked = q.b === undefined ? second ?? null : regionOf(q.b);
  const b = bAsked && bAsked !== a ? bAsked : null;
  const step = file.hours.step_hours || 1;
  const pick = (code: string) => `${path}?region=${code.toLowerCase()}#whole-country`;
  const cell = (code: string, v: ReactNode | null, missing: string): ReactNode => (held(code) ? <Held why={held(code)!} /> : v ?? <NOT why={missing} />);
  const tables = file.tables ?? [];
  // session 8470 (the real files): the hour in the region's own time on hover, from index.json's time zones
  const zones = regionZones();
  // session 8470: regions whose sources rest on fewer hours than the window's are named under the sources table
  const short = why ? [] : shortSources(rows, file.hours.n, REGIONS_HELD);
  // storage apart, grouped by its hours: its columns begin in July 2024 (the real files: 6 hours or fewer over the 2025 heat)
  const shortStore = why ? [] : shortSources(rows, file.hours.n, REGIONS_HELD, true);
  const storeGroups = [...new Set(shortStore.map((s) => s.hours))].sort((x, y) => y - x).map((h) => `${shortStore.filter((s) => s.hours === h).map((s) => s.name).join(", ")} on ${whole(h)}`);
  const when = (code: string, at: string): ReactNode => {
    const tz = zones[code], local = tz ? localHour(at, tz) : null;
    return local ? <span title={`In the region's own time (${tz}, from index.json): ${local}.`} data-wc-local={code}>{utcHour(at)}</span> : utcHour(at);
  };
  // session 8470: EIA's files carry no storage column before July 2024, so a window or a baseline before it holds none
  const baseFirst = baselineFirstHour(file);
  const beforeStorage = file.hours.start < STORAGE_FROM || (baseFirst !== null && baseFirst < STORAGE_FROM);
  const noStorage = (name: string) => `The file holds no storage for ${name} with its baseline in this window.${beforeStorage ? ` EIA's six-month files carry no storage columns before July 2024, and this window${file.hours.start < STORAGE_FROM ? "" : "'s baseline"} reaches back before then.` : ""}`;
  // session 8470 (case 3, the Northwest over Uri): a source not held says which side holds it, where one does
  const sideWords = (code: string, key: string) => {
    const h = heldApart(file, code, key);
    return h.event || h.base ? ` The window holds ${h.event ? `${whole(h.event)} hours of it` : "no hour of it"} and the baseline ${h.base ? `${whole(h.base)} hours` : "none"}, and no hour is held by both.` : "";
  };
  const apart = why ? [] : apartSources(file, rows, REGIONS_HELD);
  const poss = (name: string) => (name.endsWith("s") ? `${name}'` : `${name}'s`);

  const regionRows = rows.map((r) => ({
    key: r.code, highlight: r.code === a || r.code === b,
    cells: [
      <span key="n" data-wc-row={r.code} {...(r.isNew ? { "data-wc-new": "1" } : {})}><Link href={pick(r.code)} title={regionWords(r)}>{r.name}</Link></span>,
      cell(r.code, r.demand ? <span title={againstTip(`${r.name}, demand`, r.demand)}><N k={`wc|${r.code}|demand_gwh`}>{gwh(r.demand.mwh)}</N></span> : null, `The file holds no hour of demand for ${r.name} with its baseline.`),
      cell(r.code, r.demand && r.demand.pct !== null ? <span title={againstTip(`${r.name}, demand`, r.demand)}><N k={`wc|${r.code}|demand_pct`}>{signedPct(r.demand.pct)}</N></span> : null, `No baseline is held for ${r.name}'s demand.`),
      cell(r.code, r.peak ? <N k={`wc|${r.code}|peak_mw`}>{whole(r.peak.mw)}</N> : null, `The file holds no hour of demand for ${r.name}.`),
      cell(r.code, r.peak ? when(r.code, r.peak.at) : null, `The file holds no hour of demand for ${r.name}.`),
      cell(r.code, r.peak && r.peak.base_mw !== null ? <N k={`wc|${r.code}|peak_base_mw`}>{whole(r.peak.base_mw)}</N> : null, `The baseline does not hold that hour for ${r.name}.`),
      cell(r.code, r.imports ? <span title={`${r.name}: net imports averaged ${signedWhole(r.imports.mean_mw)} MW over the window and ${signedWhole(r.imports.base_mean_mw)} MW in the baseline, over the ${whole(r.imports.hours)} hours both hold. Above zero the region imported; below zero it exported.`}><N k={`wc|${r.code}|imports_mw`}>{signedWhole(r.imports.mean_mw)}</N></span> : null, `The file holds no net imports for ${r.name} with their baseline.`),
      cell(r.code, r.imports ? <N k={`wc|${r.code}|imports_base_mw`}>{signedWhole(r.imports.base_mean_mw)}</N> : null, `The file holds no net imports for ${r.name} with their baseline.`),
      cell(r.code, <span><N k={`wc|${r.code}|hours`}>{whole(r.hoursHeld)}</N> of {whole(file.hours.n)}</span>, ""),
    ],
  }));

  const sourceRows = rows.map((r) => ({
    key: r.code, highlight: r.code === a || r.code === b,
    cells: [
      <Link key="n" href={pick(r.code)} title={regionWords(r)}>{r.name}</Link>,
      ...SOURCES.map((s) => {
        const x = r.sources[s.key];
        return cell(r.code, x ? <span title={againstTip(`${r.name}, ${s.label.toLowerCase()}`, x)}><N k={`wc|${r.code}|gen|${s.key}`}>{signedGwh(x.diff_mwh)}</N></span> : null, (s.key === "storage" ? noStorage(r.name) : `The file holds no ${s.label.toLowerCase()} for ${r.name} with its baseline in this window.`) + sideWords(r.code, s.key));
      }),
      cell(r.code, r.generation ? <span title={againstTip(`${r.name}, net generation`, r.generation)}><N k={`wc|${r.code}|gen|net`}>{signedGwh(r.generation.diff_mwh)}</N></span> : null, `The file holds no net generation for ${r.name} with its baseline.`),
    ],
  }));

  const ps = pairs(file);
  const nm = (c: string | null) => (c ? REGION_NAME[c] ?? c : "");
  const pairRows = ps.map((p) => {
    const h = held(p.a) ?? held(p.b);
    const blank = (v: ReactNode) => (h ? <Held why={h} /> : v);
    // session 8470 (the real files): a pair with Canada or Mexico says whose report it is; a pair whose every held hour
    // is 0 MW says so; the pairs of the regions drawn below are marked as the region tables mark them
    const abroad = [p.a, p.b].filter((c) => ABROAD.includes(c));
    const pairWhy = [
      abroad.length ? `${abroad.map(nm).join(" and ")} file${abroad.length > 1 ? "" : "s"} no Form EIA-930, so this flow is the US region's own report of its interchange with ${abroad.length > 1 ? "them" : "it"}.` : "",
      p.zero ? `Every one of the ${whole(p.hours)} held hours of the window is 0 MW in the file for this pair${p.base && !p.base.zero ? ", while the baseline's hours are not" : ""}.` : "",
    ].filter(Boolean).join(" ");
    const first = <span key="s" data-wc-pair={p.key} {...(abroad.length ? { "data-wc-abroad": "1" } : {})} {...(p.zero ? { "data-wc-zero": "1" } : {})}>{p.sent ? nm(p.sent) : `${nm(p.a)} and ${nm(p.b)}: no net flow`}</span>;
    return {
      key: p.key, highlight: [p.a, p.b].includes(a) || (!!b && [p.a, p.b].includes(b)),
      cells: [
        pairWhy ? <span key="s" title={pairWhy} className="cursor-help">{first}</span> : first,
        p.took ? nm(p.took) : "",
        blank(<N k={`wc|pair|${p.key}|mean_mw`}>{whole(Math.abs(p.mean_mw))}</N>),
        blank(<N k={`wc|pair|${p.key}|gwh`}>{gwh(Math.abs(p.mwh))}</N>),
        p.base ? (p.base.sent ? `${nm(p.base.sent)} to ${nm(p.base.took)}` : "no net flow") : <NOT why="The file holds no baseline hour for this pair." />,
        p.base ? blank(<N k={`wc|pair|${p.key}|base_mean_mw`}>{whole(Math.abs(p.base.mean_mw))}</N>) : <NOT why="The file holds no baseline hour for this pair." />,
        <span key="h">{whole(p.hours)} of {whole(file.hours.n)}</span>,
      ],
    };
  });

  const options = REGION_CODES.map((c) => ({ value: c.toLowerCase(), label: REGION_NAME[c] }));
  return open(
    <div data-wc-state="drawn" data-wc-a={a} data-wc-b={b ?? ""}>
      <p className="mb-3 max-w-3xl text-sm" data-wc-lead="1">
        EIA&apos;s thirteen regions of the lower 48 over {file.start} to {file.end}, each against{" "}
        <Hint words="the baseline" why={`${base.words ? `The file's own words: ${base.words}.` : "The file names no rule."}${base.offsets.length ? (base.offsets.every((o) => typeof o === "number") ? ` Offsets in days: ${base.offsets.join(", ")}.` : ` Offsets: ${base.offsets.join(", ")}.`) : ""}${file.window ? ` The window's hours, in the file's words: ${file.window}.` : ""} For each hour of the window the baseline is the mean of the same hour at each offset that holds it. Source: the event's window and baseline days as the page above uses them (docs/methods/events.md).`} />.{" "}
        <Hint words="Six regions are new to the site" why={`${NEW_REGIONS.map((c) => REGION_NAME[c]).join(", ")}: none of the seven grids of the sections above is in them, so no page drew them before 19 November 2026.`} />.{" "}
        <Hint words="How a figure here is formed" why={`Each figure is a sum or a mean over the hours of the window that the file holds for both the event and the baseline; MW over an hour is MWh, shown as GWh (1,000 MWh). Hours are the file's, in UTC: ${whole(file.hours.n)} steps of ${step} hour${step > 1 ? "s" : ""} each, from ${utcHour(file.hours.start)}. Nothing is filled or estimated. A region's figure is EIA's sum of its balancing authorities, so it is not the figure of a grid above even where they cover nearly the same ground.`} />
      </p>

      <h3 className="mb-1 mt-4 text-base" id="wc-regions">Each region across the event</h3>
      <ToolTable minWidth={980} caption="Each of EIA's thirteen regions across the event against the baseline"
        head={[
          "Region",
          <Head key="d" mark="demand" words="Demand, GWh" why="The region's demand summed over the hours of the window that the event and the baseline both hold. Source: EIA Form EIA-930, demand by region." />,
          <Head key="p" mark="pct" words="On the baseline, percent" why="Demand over the window less the baseline's over the same hours, as a percent of the baseline's." />,
          <Head key="k" mark="peak" words="Highest hour, MW" why="The highest hour of demand the file holds for the region in the window." />,
          <Head key="w" mark="when" words="When" why={`The start of that hour, in UTC as the file writes it.${Object.keys(zones).length ? " Hover a time for the same hour in the region's own time." : ""}`} />,
          <Head key="b" mark="peakbase" words="Baseline that hour, MW" why="The baseline's demand at the same hour of the window: the mean of that hour at each baseline offset. The sections above take each baseline day's own highest hour, so this is not the same comparison." />,
          <Head key="i" mark="imports" words="Net imports, mean MW" why="The mean of the region's net imports over the hours both hold: EIA's total interchange with its sign turned, so above zero the region imported and below zero it exported." />,
          <Head key="j" mark="importsbase" words="Baseline, mean MW" why="The same mean over the baseline's hours." />,
          <Head key="h" mark="hours" words="Hours held" why="The hours of the window for which the file holds the region's demand, of the window's hours." />,
        ]}
        rows={regionRows} />

      <h3 className="mb-1 mt-6 text-base" id="wc-sources">Generation by source, the event less the baseline, GWh</h3>
      <ToolTable minWidth={980} caption="Generation by source in each region: the event less the baseline, in GWh"
        head={["Region", ...SOURCES.map((s) => <Head key={s.key} mark={`src-${s.key}`} words={s.label} why={`${s.label}: the region's generation from this source over the window less the baseline's, over the hours both hold. ${s.key === "storage" ? "Storage is negative while it charges. " : ""}${s.key === "hydro" ? "Hydro includes pumped storage. " : ""}${s.key === "other" ? "Other is petroleum, geothermal, other and unknown sources. " : ""}Hover a cell for the two sums. Source: EIA Form EIA-930, generation by energy source.`} />),
          <Head key="net" mark="src-net" words="Net generation" why="The region's net generation over the window less the baseline's, over the hours both hold." />]}
        rows={sourceRows} />
      {short.length || shortStore.length || apart.length ? (
        <p className="mt-1 max-w-3xl text-sm" data-wc-short-sources={short.map((s) => s.code).join(",")} data-wc-short-storage={shortStore.map((s) => s.code).join(",")} data-wc-apart-sources={apart.map((s) => s.code).join(",")}>
          Fewer hours than the window&apos;s {whole(file.hours.n)}:{" "}
          {short.length ? `${short.map((s) => `${poss(s.name)} sources rest on ${whole(s.hours)} hours${s.net !== null && s.net > s.hours ? ` (its net generation on ${whole(s.net)})` : ""}`).join("; ")}.` : null}
          {apart.length ? `${short.length ? " " : ""}${apart.map((s) => `${poss(s.name)} sources are held for ${s.event ? `${whole(s.event)} hours of the window` : "no hour of the window"} and ${s.base ? `${whole(s.base)} of the baseline, never the same hour` : "no hour of the baseline"}, so none is set against it`).join("; ")}.` : null}
          {shortStore.length ? `${short.length || apart.length ? " " : ""}Storage, counted apart${beforeStorage ? ", its columns beginning in July 2024" : ""}: ${storeGroups.join("; ")} hours.` : null}{" "}
          <Hint words="Why" why="EIA's files leave some hours of a region's generation by source empty while they hold its net generation, so the sources in that row are summed over fewer hours and do not add up to the net generation beside them. Nothing is filled: each cell's hover gives the hours it rests on. Source: EIA Form EIA-930, generation by energy source." />
        </p>
      ) : null}

      <h3 className="mb-1 mt-6 text-base" id="wc-pairs">Power between regions, pair by pair</h3>
      {ps.length ? (
        <ToolTable minWidth={820} caption="Power between each pair of regions over the window and in the baseline" words
          head={[
            <Head key="s" mark="sent" words="Sent" why="Over the window's held hours the net flow between the two regions ran from this region to the other. The file gives the flow by the first region's report where held, else the second's." />,
            <Head key="t" mark="took" words="Took" why="The region the net flow ran to." />,
            <Head key="m" mark="pairmean" words="Mean, MW" why="The mean of the hourly flow over the window's held hours, in the direction shown." />,
            <Head key="g" mark="pairgwh" words="Over the window, GWh" why="The net energy over the window's held hours, in the direction shown." />,
            <Head key="bd" mark="pairbase" words="In the baseline" why="Which way the net flow ran over the baseline's hours." />,
            <Head key="bm" mark="pairbasemean" words="Baseline mean, MW" why="The mean of the baseline's hourly flow, in the baseline's own direction." />,
            <Head key="h" mark="pairhours" words="Hours held" why="The hours of the window for which the file holds the pair's flow." />,
          ]}
          rows={pairRows} />
      ) : <p className="text-sm"><NOT why="The file holds no pair of regions for this event." /></p>}

      <h3 className="mb-1 mt-6 text-base" id="wc-choice">A region hour by hour</h3>
      <form method="get" action={`${path}#whole-country`} className="mb-3 flex flex-wrap items-end gap-3 text-sm" data-wc-form="1">
        <AutoSubmitSelect name="region" value={a.toLowerCase()} options={options} label="Region A" />
        <AutoSubmitSelect name="b" value={b ? b.toLowerCase() : "none"} options={[{ value: "none", label: "None" }, ...options]} label="Region B" />
        <button type="submit" className="border border-rule bg-panel px-3 py-1 text-sm">Show</button>
        <Hint words="The regions drawn first" why={firstWhy} />
      </form>
      {(() => {
        const ha = held(a), hb = b ? held(b) : null;
        return (
          <div className={b ? "grid gap-6 md:grid-cols-2" : ""}>
            {ha ? <p className="text-sm" data-wc-charts="a"><Held why={ha} /> {REGION_NAME[a]}: {LICENSE_NEEDED}</p> : <Charts file={file} code={a} mark="a" />}
            {b ? (hb ? <p className="text-sm" data-wc-charts="b"><Held why={hb} /> {REGION_NAME[b]}: {LICENSE_NEEDED}</p> : <Charts file={file} code={b} mark="b" />) : null}
          </div>
        );
      })()}
      <p className="mt-3 text-sm">
        <Hint words={drawnByDay(file.hours) ? "Drawn by day" : "Drawn by hour"} why={drawnByDay(file.hours) ? `The window is longer than 21 days, so each point is the mean of a UTC day's held hours, and a day with no held hour breaks the line. The tables above are from every held hour. ${BY_DAY_WORDS}` : `Each point is one hour of the file, in UTC. An hour the file does not hold has no point, and the line breaks there. ${BY_DAY_WORDS}`} />
      </p>
      <p className="mt-2 text-xs text-muted" data-wc-source="1">
        Source: EIA Form EIA-930 (public domain), by region{tables.length ? <>; ERW table{tables.length > 1 ? "s" : ""} {tables.map((t, i) => <span key={t}>{i ? ", " : ""}<Link href={`/data#${t}`} className="font-mono" gate="plain">{t}</Link></span>)}</> : null}
        {file.built ? <>; file built {file.built.slice(0, 10)}</> : null}. <Link href={`/data/methods/${(file.method ?? "docs/methods/events.md").replace(/^docs\/methods\//, "").replace(/\.md$/, "")}`}>Method</Link>.
      </p>
    </div>,
  );
}

/** What an event page mounts: the address's choices read, the event's file read, the section drawn. */
export async function WholeCountrySection({ event, path, first, second, firstWhy, searchParams }: {
  event: string; path: string; first: string; second?: string; firstWhy: string; searchParams?: Promise<Query>;
}) {
  const sp = searchParams ? await searchParams : {};
  const one = (v: string | string[] | undefined) => (typeof v === "string" ? v : undefined);
  return <WholeCountry event={event} path={path} file={eventRegionsFile(event)} q={{ region: one(sp.region), b: one(sp.b) }} first={first} second={second} firstWhy={firstWhy} />;
}
