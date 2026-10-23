// Session 241 (batch C): what /datacenters/v2 showed (session 106) and the tracker did not, folded into the one page,
// /datacenters; the old address redirects here (next.config.ts) and its file stands in app/_retired/datacenters-v2.
// ERCOT's Large Load Interconnection Status Update (load approved to energize and load observed running, over time),
// then, beside it, what the ERW's own table of facilities says of Texas. Two sources, each with its date, never added
// together: a request is not a built facility. Every figure carries a check key (components/Num.tsx): ERCOT's by the
// series key of ercot_large_load_status (the site's copy of the table is data/large_load_status.json; a report's row
// is dated the report's day at 00:00 UTC, warehouse/connectors/ercot_large_load_status.py), the facilities' by the
// datacenters keys (scripts/check-values.mjs).
import { SiteLink as Link } from "@/components/SiteLink";
import type { ReactNode } from "react";
import { Num } from "@/components/Num";
import { SeriesChart } from "@/components/tool/SeriesChart";
import { Fold, HeadlineNumber, HeadlineRow, SourceLine, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import loadJson from "@/data/large_load_status.json";
import type { EntityRow } from "@/lib/data";
import { countryOf, dayWords, facilityCounts, impossible, monthMismatch, span, summary, whole, type Facility, type LoadFile, type Report } from "@/lib/largeload";

const KIND: Record<string, string> = { operator: "an operator's own list", news: "news stories", queue: "an interconnection queue" };
const ENTITY = "ercot:large_load";
const VARIABLE = { approved: "approved_to_energize_mw", nonsimultaneous: "observed_nonsimultaneous_peak_mw", simultaneous: "observed_simultaneous_peak_mw",
  new_count: "new_submissions_count", new_mw: "new_submissions_mw" } as const;
type Stated = keyof typeof VARIABLE;
type Figure = "approved" | "nonsimultaneous" | "simultaneous";

const file = () => loadJson as unknown as LoadFile;

/** A figure a report states (one of its three, or its count and megawatts of new submissions), with the key the value check reads it by. */
function Mw({ f, r, k }: { f: LoadFile; r: Report; k: Stated }) {
  return <Num check={`series|${f.table}|${ENTITY}|${VARIABLE[k]}|${r.day}T00:00:00Z`} raw={r[k] as number}>{whole(r[k] as number)}</Num>;
}

type Read = { ok: true; data: EntityRow[] } | { ok: false; reason: string };

export function LargeLoad({ read }: { read: Read }) {
  const f = file();
  const s = span(f);
  const sentence = summary(f);
  const odd = impossible(f);
  const submissions = f.reports.filter((r) => r.new_count !== undefined);
  // The newest report held. The old page wrote "since March 2026" as fixed words; the table has grown since (three
  // more reports), and the words stood beside a table whose first row was later. The month is read from the table now.
  const newest = f.reports[f.reports.length - 1];
  const facilities: Facility[] = read.ok ? read.data.map((r) => ({ name: r.name, operator: r.operator, status: r.status, capacity_mw: r.capacity_mw, state: r.extra?.state ?? "", kind: r.extra?.kind ?? "", country: countryOf(r.extra?.country, r.extra?.state) })) : [];
  const c = facilityCounts(facilities);
  const vintage = read.ok ? read.data.map((r) => r.vintage ?? "").sort().at(-1) ?? "" : "";
  const texas = facilities.filter((r) => r.state === "TX").sort((a, b) => (b.capacity_mw ?? -1) - (a.capacity_mw ?? -1) || (a.name ?? "").localeCompare(b.name ?? ""));
  const cell = (r: Report, k: Figure): ReactNode => (r[k] !== undefined ? <Mw f={f} r={r} k={k} /> : <span className="text-muted">not stated</span>);

  return (
    <section aria-label="Texas large load" data-large-load="1">
      <ToolSection title="ERCOT: large load approved and energized, over time" id="ercot"
        note={<>Source: ERCOT, Large Load Interconnection Status Update, the reports of {dayWords(f.reports[0].day)} to {dayWords(f.reports[f.reports.length - 1].day)}, retrieved {f.retrieved.slice(0, 10)}. The reports cover every large load that asks to connect, not only datacenters; ERCOT&apos;s page for large loads speaks of &quot;a load facility of 75 MW or greater&quot;.</>}>
        <p className="mb-3 max-w-3xl text-sm" data-load-lead="1">
          How much large load Texas has approved and how much is running, from ERCOT&apos;s own monthly report, beside the datacenters the ERW already holds. <strong>A request is not a built facility,</strong> and an approval is not one either{s && s.last.nonsimultaneous! < s.last.approved! / 2 ? <>: of the load ERCOT has approved to energize, less than half has been observed running</> : null}.
        </p>
        {sentence
          ? <p className="mb-6 max-w-3xl text-lg leading-relaxed" data-load-summary="1">{sentence}</p>
          : <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status">No report held states the three figures, so no number is shown.</p>}
        {s ? (
          <HeadlineRow>
            <HeadlineNumber label="Approved to energize" value={<span data-load="approved"><Mw f={f} r={s.last} k="approved" /></span>} unit="MW" note={<>ERCOT&apos;s report of {dayWords(s.last.day)}</>} />
            <HeadlineNumber label="Observed running" value={<span data-load="nonsimultaneous"><Mw f={f} r={s.last} k="nonsimultaneous" /></span>} unit="MW" note={<>the sum of each approved load&apos;s own highest hour in the month</>} />
            <HeadlineNumber label="Served at one moment" value={<span data-load="simultaneous"><Mw f={f} r={s.last} k="simultaneous" /></span>} unit="MW" note={<>the highest hour of those loads together</>} />
          </HeadlineRow>
        ) : null}
        {/* session 304 (the ruling of 18 October 2026 on item 4 of docs/state/morning_2026-10-14.md): the pause, beside the newest figures */}
        <p className="-mt-6 mb-6 max-w-3xl text-sm" data-load-pause="2026-08-03">
          These are the newest figures ERCOT has stated{s ? <>, of {dayWords(s.last.day)}</> : null}: on 3 August 2026 ERCOT paused approvals to energize datacenters and
          virtual currency mining facilities of 75 MW or more, and its Batch Zero study, and no status update since states these figures (ERCOT&apos;s deck to TAC of
          26 August 2026, <span className="font-mono">Batch_Zero_Update_TAC_08262026.pptx</span>; <Link href="/data/methods/ercot_large_load_status">method</Link>).
        </p>
        {/* session 2301 (chain 087): the shared chart (SeriesChart) in place of the plain line chart, so each report has a
            hover with its three figures and the source, and the Chart | Table toggle holds the same figures by keyboard. One
            category a report, in order; the series are the three figures as ERCOT states them. */}
        <div data-source={`${f.table}|${f.retrieved.slice(0, 10)}|one row a report, the three figures as ERCOT states them`}>
          <SeriesChart id="large-load" title="MW, by report" unit="MW" kind="line" scale="linear"
            categories={f.reports.map((r) => ({ label: dayWords(r.day).split(" ").slice(1).join(" "), sub: dayWords(r.day).split(" ")[0] }))}
            series={[{ name: "Approved to energize", color: "var(--color-accent)", values: f.reports.map((r) => r.approved ?? null) },
              { name: "Observed running", color: "var(--color-fuel-storage)", values: f.reports.map((r) => r.nonsimultaneous ?? null) },
              { name: "Served at one moment", color: "var(--color-muted)", values: f.reports.map((r) => r.simultaneous ?? null) }]}
            says={(i) => { const r = f.reports[i]; return `ERCOT's report of ${dayWords(r.day)}: approved to energize ${r.approved === undefined ? "not stated" : `${whole(r.approved)} MW`}, observed running ${r.nonsimultaneous === undefined ? "not stated" : `${whole(r.nonsimultaneous)} MW`} (each load's own peak, summed), served at one moment ${r.simultaneous === undefined ? "not stated" : `${whole(r.simultaneous)} MW`} (${f.table}, ${r.day})`; }}
            note={<>A point is one report. ERCOT published no report in the months without a point, or none that the ERW found on its meeting pages. Read from {f.table} (the site&apos;s copy, retrieved {f.retrieved.slice(0, 10)}); the table below holds the same figures, each with its check key.</>} />
        </div>
        <ToolTable caption="ERCOT's large-load status, by report" minWidth={680} head={["Report", "Approved to energize, MW", "Observed running, MW", "Served at one moment, MW", "The month as ERCOT wrote it"]}
          rows={[...f.reports].reverse().map((r) => ({
            key: r.day,
            cells: [<a key="d" href={r.url.split("#")[0]} className="underline" rel="noopener">{dayWords(r.day)}</a>,
              <span key="a" data-load-row={`${r.day}|approved`}>{cell(r, "approved")}</span>,
              <span key="n">{cell(r, "nonsimultaneous")}</span>,
              <span key="s">{cell(r, "simultaneous")}</span>,
              <span key="m" className={monthMismatch(r) ? "" : "text-muted"}>{r.month_as_written || "not stated"}{monthMismatch(r) ? " (as written; the report is of " + r.day.slice(0, 4) + ")" : ""}</span>],
          }))} />
        <ul className="mt-3 max-w-3xl list-disc space-y-1 pl-5 text-sm">
          <li><strong>Load requested is not held.</strong> ERCOT&apos;s report shows the whole queue by status (no studies submitted, under ERCOT review, planning studies approved, approved to energize, observed energized) as a picture of a chart. The ERW does not read a number off a picture, so those figures are not here.</li>
          {submissions.map((r) => (
            <li key={r.day}><strong>The one figure for requests that a report states in words:</strong> on {dayWords(r.day)} ERCOT wrote that it had &quot;recently received <Mw f={f} r={r} k="new_count" /> new LLI submissions&quot; and that &quot;preliminary review indicates these total approximately <Mw f={f} r={r} k="new_mw" /> MW of new Large Load by 2036&quot;. A submission is a request to study a connection.</li>
          ))}
          {odd.map((r) => (
            <li key={r.day}><strong>One report contradicts itself.</strong> On {dayWords(r.day)} ERCOT stated <Mw f={f} r={r} k="simultaneous" /> MW served at one moment and <Mw f={f} r={r} k="nonsimultaneous" /> MW as the sum of each load&apos;s own peak; the first cannot be the larger. Both are shown as written.</li>
          ))}
          <li><strong>On 3 August 2026 ERCOT paused approvals to energize</strong> datacenters and virtual currency mining facilities of 75 MW or more, and paused its Batch Zero study, in its words to TAC on 26 August 2026. No status update has been found on its meeting pages since <span data-last-report={newest.day}>{dayWords(newest.day).split(" ").slice(1).join(" ")}</span>.</li>
        </ul>
      </ToolSection>

      <ToolSection title="Beside it: the facilities the ERW holds" id="texas-sites"
        note={<>Source: the ERW&apos;s own table of datacenters, built from operators&apos; lists, news stories and interconnection queues{vintage ? <>, as of {vintage.slice(0, 10)}</> : null}. A different source from ERCOT&apos;s: it names sites, most without a size, and it is not a count of ERCOT&apos;s requests. The two are not added.</>}>
        {read.ok ? (
          <>
            <p className="mb-3 max-w-3xl text-sm" data-facilities-summary="1">
              The ERW holds <strong><Num check="datacenters|count" raw={c.all}>{whole(c.all)}</Num></strong> datacenter sites: <strong><Num check="datacenters|sites_us" raw={c.us}>{whole(c.us)}</Num></strong> in a named US state, <strong><Num check="datacenters|sites_texas" raw={c.texas}>{whole(c.texas)}</Num></strong> of those in Texas, and{" "}
              <span title="No source the ERW reads states a country. A site with no US state stated may be outside the US (Firmus's Tasmanian rows are among these) or a US site whose story or operator page names no state."><Num check="datacenters|no_us_state" raw={c.noCountry}>{whole(c.noCountry)}</Num> with no US state stated, sites outside the US among them</span>.
              A size in MW is stated for <Num check="datacenters|sites_n_with_mw" raw={c.withMw}>{whole(c.withMw)}</Num> of them (<Num check="datacenters|sites_mw" raw={c.mw}>{whole(c.mw)}</Num> MW in all, every site held counted, the cancelled and those with no US state among them, so more than the megawatts stated at the top of the page), <Num check="datacenters|texas_n_with_mw" raw={c.texasWithMw}>{whole(c.texasWithMw)}</Num> in Texas{c.texasWithMw ? <> (<Num check="datacenters|texas_mw" raw={c.texasMw}>{whole(c.texasMw)}</Num> MW)</> : null}.
              By where each came from: {Object.entries(c.byKind).sort((a, b) => b[1] - a[1]).map(([k, n], i, a) => <span key={k}><Num check={`datacenters|kind_count|${k}`} raw={n}>{whole(n)}</Num> from {KIND[k] ?? k}{i < a.length - 1 ? ", " : ""}</span>)}.
            </p>
            <ToolTable caption="The Texas sites held" minWidth={640} words head={["Site in Texas", "Operator", "Status", "MW stated", "From"]}
              rows={texas.map((r, i) => ({ key: `${i}`, cells: [r.name ?? "not named", r.operator ?? "not stated", r.status || "not stated", r.capacity_mw !== null ? whole(r.capacity_mw) : "not stated", KIND[r.kind] ?? (r.kind || "not stated")] }))} />
            <p className="mt-2 text-sm">Every site, with its sources: <a href="#every-site" className="underline">the list below</a>.</p>
          </>
        ) : <p className="border border-rule bg-paper px-3 py-2 text-sm" role="status">The table could not be read, so no number is shown: {read.reason}</p>}
      </ToolSection>

      <Fold title="What this does not tell you">
        <ul className="max-w-3xl list-disc space-y-1 pl-5">
          <li><strong>How much of the load is datacenters.</strong> ERCOT&apos;s figures in words are for every large load together. Its split by type is a picture.</li>
          <li><strong>Who and where.</strong> ERCOT&apos;s report aggregates requests because customer data is confidential; it names no customer and no site.</li>
          <li><strong>What will be built.</strong> A request is not a built facility. A request can be withdrawn, an approval can go unused, and a site can take less power than it asked for.</li>
          <li><strong>Any grid but Texas.</strong> No other operator&apos;s large-load report is in the warehouse.</li>
        </ul>
      </Fold>
    </section>
  );
}

/** The source line of the ERCOT section: the table, ERCOT's terms, and the built stamp of the site's own copy. */
export function LargeLoadSource() {
  const f = file();
  return <SourceLine tables={[f.table, "datacenter_facilities"]} note={<>ERCOT&apos;s terms let raw data in public portions of its website be used and redistributed in compilations, charts and analyses. The ERCOT section reads the site&apos;s own copy of the table, built {f.built.slice(0, 10)}.</>} />;
}
