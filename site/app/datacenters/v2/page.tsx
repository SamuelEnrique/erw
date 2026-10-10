import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";
import { LineChart } from "@/components/LineChart";
import { ChartFrame, Fold, HeadlineNumber, HeadlineRow, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import loadJson from "@/data/large_load_status.json";
import { datacenters } from "@/lib/data";
import { attempt } from "@/lib/supabase";
import { countryOf, dayWords, facilityCounts, impossible, monthMismatch, span, summary, whole, type Facility, type LoadFile } from "@/lib/largeload";

// Session 106: the datacenter tracker, version 2, in the battery page's layout. Two sections, each with its source and
// its date, never added together: what ERCOT's Large Load Interconnection Status Update states (load approved to
// energize and load observed running, over time), and the facilities the ERW already holds. A request is not a built
// facility, and the page says so plainly. The older tracker (/datacenters) is as it was.

export const revalidate = 3600;
export const metadata: Metadata = { title: "The datacenter tracker", robots: { index: false, follow: false } };

const KIND: Record<string, string> = { operator: "an operator's own list", news: "news stories", queue: "an interconnection queue" };

export default async function TrackerTwo() {
  const f = loadJson as unknown as LoadFile;
  const s = span(f);
  const sentence = summary(f);
  const odd = impossible(f);
  const submissions = f.reports.filter((r) => r.new_count !== undefined);
  const read = await attempt(datacenters);
  const facilities: Facility[] = read.ok ? read.data.map((r) => ({ name: r.name, operator: r.operator, status: r.status, capacity_mw: r.capacity_mw, state: r.extra?.state ?? "", kind: r.extra?.kind ?? "", country: countryOf(r.extra?.country, r.extra?.state) })) : [];
  const c = facilityCounts(facilities);
  const vintage = read.ok ? read.data.map((r) => r.vintage ?? "").sort().at(-1) ?? "" : "";
  const texas = facilities.filter((r) => r.state === "TX").sort((a, b) => (b.capacity_mw ?? -1) - (a.capacity_mw ?? -1) || (a.name ?? "").localeCompare(b.name ?? ""));
  const t = (d: string) => Date.parse(`${d}T00:00:00Z`) / 1000;
  const line = (k: "approved" | "nonsimultaneous" | "simultaneous") => f.reports.filter((r) => r[k] !== undefined).map((r) => ({ t: t(r.day), v: r[k] as number }));

  return (
    <ToolPage>
      <ToolHeader title="The datacenter tracker" crumb={<>Version 2, in review. The tracker as it was: <Link href="/datacenters" className="underline">/datacenters</Link></>}
        lead={<>How much large load Texas has approved and how much is running, from ERCOT&apos;s own monthly report, beside the datacenters the ERW already holds. <strong>A request is not a built facility,</strong> and an approval is not one either{s && s.last.nonsimultaneous! < s.last.approved! / 2 ? <>: of the load ERCOT has approved to energize, less than half has been observed running</> : null}.</>} />

      {sentence
        ? <p className="mb-6 max-w-3xl text-lg leading-relaxed" data-load-summary="1">{sentence}</p>
        : <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status">No report held states the three figures, so no number is shown.</p>}

      {s ? (
        <HeadlineRow>
          <HeadlineNumber label="Approved to energize" value={<span data-load="approved">{whole(s.last.approved!)}</span>} unit="MW" note={<>ERCOT&apos;s report of {dayWords(s.last.day)}</>} />
          <HeadlineNumber label="Observed running" value={<span data-load="nonsimultaneous">{whole(s.last.nonsimultaneous!)}</span>} unit="MW" note={<>the sum of each approved load&apos;s own highest hour in the month</>} />
          <HeadlineNumber label="Served at one moment" value={<span data-load="simultaneous">{whole(s.last.simultaneous!)}</span>} unit="MW" note={<>the highest hour of those loads together</>} />
        </HeadlineRow>
      ) : null}

      <ToolSection title="ERCOT: large load approved and energized, over time" id="ercot"
        note={<>Source: ERCOT, Large Load Interconnection Status Update, the reports of {dayWords(f.reports[0].day)} to {dayWords(f.reports[f.reports.length - 1].day)}, retrieved {f.retrieved.slice(0, 10)}. The reports cover every large load that asks to connect, not only datacenters; ERCOT&apos;s page for large loads speaks of &quot;a load facility of 75 MW or greater&quot;.</>}>
        <ChartFrame title="MW, by report" legend={[{ label: "Approved to energize", color: "var(--color-accent)" }, { label: "Observed running (each load's own peak, summed)", color: "var(--color-fuel-storage)" }, { label: "Served at one moment", color: "var(--color-muted)" }]}
          note={<>A point is one report. ERCOT published no report in the months without a point, or none that the ERW found on its meeting pages.</>}>
          <LineChart unit="MW" height={280} x="month" ariaLabel="ERCOT large load approved to energize and observed running, by report"
            lines={[{ label: "Approved to energize", color: "accent", points: line("approved") }, { label: "Observed running", color: "var(--color-fuel-storage)", points: line("nonsimultaneous") }, { label: "Served at one moment", color: "muted", points: line("simultaneous") }]} />
        </ChartFrame>
        <ToolTable caption="ERCOT's large-load status, by report" minWidth={680} head={["Report", "Approved to energize, MW", "Observed running, MW", "Served at one moment, MW", "The month as ERCOT wrote it"]}
          rows={[...f.reports].reverse().map((r) => ({
            key: r.day,
            cells: [<a key="d" href={r.url.split("#")[0]} className="underline" rel="noopener">{dayWords(r.day)}</a>,
              r.approved !== undefined ? <span key="a" data-load-row={`${r.day}|approved`}>{whole(r.approved)}</span> : <span key="a" className="text-muted">not stated</span>,
              r.nonsimultaneous !== undefined ? whole(r.nonsimultaneous) : <span key="n" className="text-muted">not stated</span>,
              r.simultaneous !== undefined ? whole(r.simultaneous) : <span key="s" className="text-muted">not stated</span>,
              <span key="m" className={monthMismatch(r) ? "" : "text-muted"}>{r.month_as_written || "not stated"}{monthMismatch(r) ? " (as written; the report is of " + r.day.slice(0, 4) + ")" : ""}</span>],
          }))} />
        <ul className="mt-3 max-w-3xl list-disc space-y-1 pl-5 text-sm">
          <li><strong>Load requested is not held.</strong> ERCOT&apos;s report shows the whole queue by status (no studies submitted, under ERCOT review, planning studies approved, approved to energize, observed energized) as a picture of a chart. The ERW does not read a number off a picture, so those figures are not here.</li>
          {submissions.map((r) => (
            <li key={r.day}><strong>The one figure for requests that a report states in words:</strong> on {dayWords(r.day)} ERCOT wrote that it had &quot;recently received {whole(r.new_count!)} new LLI submissions&quot; and that &quot;preliminary review indicates these total approximately {whole(r.new_mw!)} MW of new Large Load by 2036&quot;. A submission is a request to study a connection.</li>
          ))}
          {odd.map((r) => (
            <li key={r.day}><strong>One report contradicts itself.</strong> On {dayWords(r.day)} ERCOT stated {whole(r.simultaneous!)} MW served at one moment and {whole(r.nonsimultaneous!)} MW as the sum of each load&apos;s own peak; the first cannot be the larger. Both are shown as written.</li>
          ))}
          <li><strong>On 3 August 2026 ERCOT paused approvals to energize</strong> datacenters and virtual currency mining facilities of 75 MW or more, and paused its Batch Zero study, in its words to TAC on 26 August 2026. No status update has been found on its meeting pages since March 2026.</li>
        </ul>
      </ToolSection>

      <ToolSection title="Beside it: the facilities the ERW holds" id="facilities"
        note={<>Source: the ERW&apos;s own table of datacenters, built from operators&apos; lists, news stories and interconnection queues{vintage ? <>, as of {vintage.slice(0, 10)}</> : null}. A different source from ERCOT&apos;s: it names sites, most without a size, and it is not a count of ERCOT&apos;s requests. The two are not added.</>}>
        {read.ok ? (
          <>
            <p className="mb-3 max-w-3xl text-sm" data-facilities-summary="1">
              The ERW holds <strong>{whole(c.all)}</strong> datacenter sites: <strong>{whole(c.us)}</strong> in a named US state, <strong>{whole(c.texas)}</strong> of those in Texas, and{" "}
              <span title="No source the ERW reads states a country. A site with no US state stated may be outside the US (Firmus's Tasmanian rows are among these) or a US site whose story or operator page names no state.">{whole(c.noCountry)} with no US state stated, sites outside the US among them</span>.
              A size in MW is stated for {whole(c.withMw)} of them ({whole(c.mw)} MW in all), {whole(c.texasWithMw)} in Texas{c.texasWithMw ? <> ({whole(c.texasMw)} MW)</> : null}.
              By where each came from: {Object.entries(c.byKind).sort((a, b) => b[1] - a[1]).map(([k, n], i, a) => <span key={k}>{whole(n)} from {KIND[k] ?? k}{i < a.length - 1 ? ", " : ""}</span>)}.
            </p>
            <ToolTable caption="The Texas sites held" minWidth={640} words head={["Site in Texas", "Operator", "Status", "MW stated", "From"]}
              rows={texas.map((r, i) => ({ key: `${i}`, cells: [r.name ?? "not named", r.operator ?? "not stated", r.status || "not stated", r.capacity_mw !== null ? whole(r.capacity_mw) : "not stated", KIND[r.kind] ?? (r.kind || "not stated")] }))} />
            <p className="mt-2 text-sm">Every site, with its sources: <Link href="/datacenters" className="underline">the tracker as it was</Link>.</p>
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
      <SourceLine tables={[f.table, "datacenter_facilities"]} note={<>ERCOT&apos;s terms let raw data in public portions of its website be used and redistributed in compilations, charts and analyses. This page is in review; the ERCOT section reads the site&apos;s own copy of the table, built {f.built.slice(0, 10)}.</>} />
    </ToolPage>
  );
}
