import type { Metadata } from "next";
import { LineChart, type Line } from "@/components/LineChart";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { SiteLink as Link } from "@/components/SiteLink";
import { ExploreFrame, FilterForm, Freshness } from "@/components/explore/Explore";
import { SeriesChart } from "@/components/tool/SeriesChart";
import { ChartFrame, HeadlineNumber, HeadlineRow, Tip, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { headers } from "@/lib/data";
import { choose, isoKey, longDay, longTime, type Params } from "@/lib/explore";
import {
  MEASURES, METHOD, NOT_HELD, QUEUED_UP_GRIDS, QUEUES, QUEUE_COLUMNS, STATUSES, STATUS_WHY, STATUS_WORDS, TABLE, UNDATED, builtAt, entityOf, faultyBuild, figureText,
  headerCount, headerKey, inputRetrieved, partialYear, queuedUpHref, statusWords, valueOf, waitTip, yearOf, yearTs, type Measure, type Row,
} from "@/lib/explore/interconnection";
import { sourceOf } from "@/lib/explore/source";
import { shown } from "@/lib/format";
import { LICENSE_NEEDED, licenseHeldGrid, licenseTitle } from "@/lib/license";
import { HOURLY, attempt, rest } from "@/lib/supabase";
// by the site's alias, not "./": tests/test_session405.py holds this page to no private import
import { InterconnectionDecisions } from "@/app/explore/interconnection/Decisions";

// Session 405: the interconnection explorer (platform tool 5, the third signature explorer), in review. The six ISO
// queues by the year a position entered and what became of it (reached operation, withdrawn, still waiting, status not
// stated), in positions or MW, from iso_queue_statistics as it stands. The filters are a GET form, so every figure is
// drawn on the server from one row of the table (or one count its header states) and carries that row's check key
// (scripts/check-values.mjs reads it again). Nothing is computed here. The table is the first build's until the data
// machine rebuilds it (the method note's fault of 20 October 2026): the page says so in one line, from the table's own
// header, and shows the counts the table holds, never a corrected guess. A queue whose publisher asks for permission
// (NYISO, MISO, ISO-NE from 21 October 2026, lib/license.ts) is held by grid, as the map's Queues tab holds it: not read,
// its figures not shown. The same table is drawn one queue at a time on the map's Queues tab (app/map/QueuesView.tsx).
// Session 2202 (chain 086): every figure carries its source in its hover (Num's `source`, the words of
// lib/explore/source.ts read from the figure's own key: the table, the queue and its entry year, the variable, the ISO's
// own queue table and the method note; the header's count names the header line it is read from), each headline number a
// Tip with the same words, and the stacked chart (SeriesChart) the brand's hover card. A held queue's figures stay
// "license needed", with no source words: Num draws the hold before the source.
// Session 7509 (chain 304, the done line): a figure is written by its variable (lib/explore/interconnection.ts,
// figureText: positions whole; MW, the share and the wait always with two decimals); the two year filters show the
// years as the page reads them (the earlier first) when the address names them the other way round; and the choices
// that move the figures are a decisions block at the foot (./Decisions.tsx), under a held queue's line too.
// Session 7518 (chain 304, part B: the page read as a developer deciding where to file,
// docs/reviews/interconnection-read-2026-11-16.md): ERCOT's two statuses are headed by what they are ("Agreement signed",
// "No agreement yet": lib/explore/interconnection.ts, STATUS_WORDS), in the headlines, the chart and the table of years,
// and ERCOT's row of the six queues carries the same words in a tip; the six queues' table, in positions, also draws the
// withdrawn share, the median wait and the waits counted of the one entry year, queue beside queue; the wait's chart
// says in a tip whose waits a point counts and which two pages count a wait another way; a held queue's line and an
// address that asks for PJM point to Berkeley Lab's Queued Up on /queues; and one line says a large load's request is in
// no figure here and where the load side is. Nothing the page drew is dropped, and it still computes nothing.
export const metadata: Metadata = { title: "Interconnection queue explorer" };
export const dynamic = "force-dynamic";

const PATH = "/explore/interconnection";
const SELECT = "entity,variable,ts_utc,value";

export default async function InterconnectionExplorer({ searchParams }: { searchParams: Promise<Params> }) {
  const sp = await searchParams;
  const [iso, badIso] = choose(sp, "queue", QUEUES.map(([k]) => k), QUEUES[0][0]);
  const name = QUEUES.find(([k]) => k === iso)![1];
  const [measureS, badMeasure] = choose(sp, "measure", MEASURES.map((m) => m.key), "positions");
  const measure = measureS as Measure;
  const unit = MEASURES.find((m) => m.key === measure)!.unit;
  const held = licenseHeldGrid(iso);

  const [header, read] = await Promise.all([
    attempt(() => headers(TABLE)),
    held ? Promise.resolve(null) : attempt(() => rest<Row>("series", { select: SELECT, table_name: `eq.${TABLE}`, entity: `like.${iso}:queue_*`, order: "entity,variable" }, HOURLY)),
  ]);
  const head = header.ok ? header.data : [];
  const built = builtAt(head);
  const retrieved = inputRetrieved(head, iso);

  const fresh = (
    <Freshness
      tables={[TABLE, `${iso}_interconnection_queue`]}
      // session 7509: the queues are pulled once a week (warehouse/run_daily.sh, Mondays UTC), so the frame's three days
      // called the queue's table stale on four days of every seven; eight days is a missed weekly pull
      staleAfterDays={8}
      detail={built ? <>The table&apos;s header says it was built at {longTime(built)}{retrieved ? <>, from {name}&apos;s queue as the ERW retrieved it on {longDay(retrieved)}</> : null}.</> : <>The table&apos;s header could not be read, so when it was built is not shown.</>}
    />
  );
  const fault = !header.ok ? (
    <p className="mb-6 max-w-3xl border-l-2 border-accent bg-paper px-3 py-2 text-sm" role="note" data-queue-fault="unread">
      The table&apos;s header could not be read, so whether these counts are still its first build&apos;s (the fault of 20 October 2026 in <Link href={METHOD}>the method note</Link>) is not known.
    </p>
  ) : faultyBuild(head) ? (
    <p className="mb-6 max-w-3xl border-l-2 border-accent bg-paper px-3 py-2 text-sm" role="note" data-queue-fault={built ?? "undated"}>
      <strong>These counts are the table&apos;s first build{built ? <>, of {longDay(built)}</> : null}.</strong> Its read cut a row of the queue
      tables at a &quot;#&quot; inside a cell and lost those rows&apos; queue dates, most of them ERCOT&apos;s, so a year&apos;s counts and the count with no
      queue date are that build&apos;s, not the queues&apos;; the page shows them as the table holds them, corrects none, and they stand right once
      the data machine rebuilds the table (<Link href={METHOD}>the method note</Link>, &quot;A fault in the first build&quot;).
    </p>
  ) : null;

  const frame = (filters: React.ReactNode, body: React.ReactNode, decisions = false) => (
    <ExploreFrame
      id="interconnection"
      title="Interconnection queues"
      definition={<>An interconnection queue is a grid operator&apos;s list of the plants and batteries asking to connect: for each of six ISOs, the positions that entered in each year and what became of them, reached operation, withdrawn or still waiting, in the ISO&apos;s own status words.</>}
      fresh={<>{fresh}{fault}</>}
      filters={filters}
      method={{ href: METHOD, label: "Energy projects, Queue statistics" }}
      tables={[TABLE]}
      sourceNote={<>Derived by the ERW from the six ISOs&apos; queue tables (<code className="font-mono">{iso}_interconnection_queue</code> for this one), as the ERW held them when this table was built{retrieved ? <>: {name}&apos;s as pulled on {longDay(retrieved)}</> : null}. This page is in review.</>}
    >
      {body}
      {decisions ? <InterconnectionDecisions /> : null}
    </ExploreFrame>
  );

  const rows = read?.ok ? read.data : [];
  const years = Array.from(new Set(rows.map((r) => yearOf(r.entity)).filter((y): y is number => y !== null))).sort((a, b) => a - b);
  const partial = (y: number) => partialYear(y, retrieved);
  const complete = years.filter((y) => !partial(y));
  const ys = years.map(String);
  const [fromS, badFrom] = choose(sp, "from", ys, String(years[0] ?? ""));
  const [toS, badTo] = choose(sp, "to", ys, String(complete[complete.length - 1] ?? years[years.length - 1] ?? ""));
  const [lo, hi] = [Number(fromS), Number(toS)].sort((a, b) => a - b);
  const span = years.filter((y) => y >= lo && y <= hi);
  const asked = [badIso && "queue", badMeasure && "measure", badFrom && "first year", badTo && "last year"].filter(Boolean);
  const yearOpt = (y: number) => ({ value: String(y), label: `${y}${partial(y) ? " (partial)" : ""}` });

  const filters = (
    <FilterForm
      action={PATH}
      fields={[
        { name: "queue", label: "Queue", value: iso, options: QUEUES.map(([k, n]) => ({ value: k, label: `${n}${licenseHeldGrid(k) ? ` (${LICENSE_NEEDED})` : ""}` })) },
        { name: "measure", label: "Count", value: measure, options: MEASURES.map((m) => ({ value: m.key, label: m.label })) },
        ...(years.length ? [
          { name: "from", label: "First entry year", value: String(lo), options: years.map(yearOpt) },
          { name: "to", label: "Last entry year", value: String(hi), options: years.map(yearOpt) },
        ] : []),
      ]}
      reset={{ href: PATH, defaults: `${QUEUES[0][1]}'s queue, in positions, every entry year it holds to the newest complete one` }}
      note={asked.length ? <>
        <span data-asked-unknown="1">The address asked for a {asked.join(" and a ")} the table does not hold; the page shows the default in its place.</span>
        {/* session 7518: the reader who asks for PJM is told where it is counted (the words stay outside the span above,
            which replication/interconnection/replicate.py reads for what was asked) */}
        {badIso && sp.queue === "pjm" ? <span data-asked-pjm="1"> The ERW holds no table of PJM&apos;s own list; Berkeley Lab&apos;s Queued Up counts PJM on <Link href={queuedUpHref("pjm")}>the interconnection queue page</Link>.</span> : null}
      </> : undefined}
    />
  );

  const notHeld = NOT_HELD[iso] ? <p className="mb-6 max-w-3xl text-sm" data-queue-not-held={iso}>{NOT_HELD[iso]}</p> : null;
  if (held) {
    return frame(filters, (
      <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status" data-license-held={TABLE} title={licenseTitle(TABLE)}>
        {name}&apos;s queue is held: {LICENSE_NEEDED}. Its figures are not shown; the queues of {QUEUES.filter(([k]) => !licenseHeldGrid(k)).map(([, n]) => n).join(", ").replace(/, (?=[^,]*$)/, " and ")} are.
        {QUEUED_UP_GRIDS.includes(iso) ? <span data-held-elsewhere={iso}> Berkeley Lab&apos;s Queued Up, another source under its own license, counts {name}&apos;s requests on <Link href={queuedUpHref(iso)}>the interconnection queue page</Link>.</span> : null}
      </p>
    ), true);
  }
  if (!read?.ok || rows.length === 0) {
    return frame(filters, <>{notHeld}<NoData what={TABLE} reason={read && !read.ok ? read.reason : `no row for ${name}`} /></>);
  }

  // the other unheld queues in the last entry year, one read (the held grids are not asked for)
  const others = QUEUES.filter(([k]) => !licenseHeldGrid(k));
  const across = await attempt(() => rest<Row>("series", {
    select: SELECT, table_name: `eq.${TABLE}`, entity: `in.(${others.map(([k]) => entityOf(k, hi)).join(",")})`, order: "entity,variable",
  }, HOURLY));
  const acrossRows = across.ok ? across.data : [];

  const key = (q: string, y: number, v: string) => `series|${TABLE}|${entityOf(q, y)}|${v}|${isoKey(yearTs(y))}`;
  const queueName = (q: string) => QUEUES.find(([k]) => k === q)?.[1] ?? q.toUpperCase();
  const sourceWords = (q: string, y: number, v: string) => sourceOf(key(q, y, v), `${queueName(q)}'s queue, entry year ${y}`);
  const N = ({ q = iso, y, v, from = rows }: { q?: string; y: number; v: string; from?: Row[] }) => {
    const x = valueOf(from, q, y, v);
    return x === undefined ? <span className="text-muted">not held</span> : <Num check={key(q, y, v)} raw={x} source={sourceWords(q, y, v)}>{figureText(v, x)}</Num>;
  };
  // the tip beside a headline's label: the figure's source, in the brand's keyboard-reachable tip
  const tipOf = (v: string, label: string) => <Tip id={`source-${v}`} label={`where ${label.toLowerCase()} comes from`}>{sourceWords(iso, hi, v)}</Tip>;
  const has = (v: string) => rows.some((r) => r.variable === v);
  const prefix = measure === "mw" ? "mw" : "positions";
  // session 7518: a queue's own words for a status where it has them (ERCOT: "Agreement signed", "No agreement yet")
  const words = (key: (typeof STATUSES)[number]["key"]) => statusWords(iso, key);
  // ruling alternative 3 (wip/alt-interconnection-3, not a default on main): in the MW view the withdrawn share is by MW
  const rateVar = measure === "mw" && has("mw_withdrawal_rate") ? "mw_withdrawal_rate" : "withdrawal_rate";
  const third: [string, string] = has(rateVar) ? [rateVar, rateVar === "mw_withdrawal_rate" ? "Withdrawn, share of MW entered" : "Withdrawn, share of positions entered"] : [`${prefix}_waiting`, `${words("waiting").label}, ${unit}`];
  const along = (v: string): Line["points"] => span
    .map((y) => ({ t: Date.UTC(y, 0, 1) / 1000, v: valueOf(rows, iso, y, v) }))
    .filter((p): p is { t: number; v: number } => p.v !== undefined);
  const undated = headerCount(head, UNDATED, name);
  const statusHead = STATUSES.map((s) => s.label);
  const ownHead = STATUSES.map((s) => words(s.key).label);
  // the six queues' table: in positions, the share and the wait of the one entry year too, queue beside queue
  const queueColumns = measure === "mw" ? [] : QUEUE_COLUMNS;
  const ownWords = (q: string) => STATUS_WORDS[q]
    ? <Tip id={`queue-words-${q}`} label={`what ${queueName(q)}'s statuses count`}>In {queueName(q)}&apos;s row, {STATUSES.filter((s) => STATUS_WORDS[q][s.key]).map((s) => `"${s.label}" is "${STATUS_WORDS[q][s.key]!.label}"`).join(" and ")}. {STATUS_WHY[q]}</Tip>
    : null;

  const body = (
    <>
      {notHeld}
      <HeadlineRow>
        {([[`${prefix}_entered`, `Entered, ${unit}`], [`${prefix}_operating`, `${words("operating").label}, ${unit}`], third] as [string, string][]).map(([v, label]) => (
          <HeadlineNumber key={v} label={`${label}, ${name}, entered ${hi}`} value={<N y={hi} v={v} />} tip={tipOf(v, label)}
            note={lo !== hi ? <>Entered {lo}: <N y={lo} v={v} /></> : undefined} />
        ))}
      </HeadlineRow>

      <div className="mb-10" data-queue-status-chart={iso}>
        <SeriesChart id={`queue-status-${iso}`} title={`${name}'s queue by entry year and status, ${lo} to ${hi}, ${unit}`} unit={unit} kind="stacked" scale="linear"
          categories={span.map((y) => ({ label: String(y), partial: partial(y) }))} partialWords="Entry year not over"
          series={STATUSES.map((s) => ({ name: words(s.key).short, color: s.color, values: span.map((y) => valueOf(rows, iso, y, `${prefix}_${s.key}`) ?? null) }))}
          note={<>Each bar is one entry year&apos;s {measure === "mw" ? "MW, as the queue states it" : "positions"}, split by what became of them; a status the queue does not hold has no part. A recent year&apos;s positions have had less time to reach operation or to be withdrawn: its parts are not final.{measure === "mw" ? " A position with no MW is in the positions and not in the MW." : ""}</>} />
      </div>

      {has("withdrawal_rate") ? (
        <ChartFrame title={rateVar === "mw_withdrawal_rate" ? `${name}: the share of each entry year's MW withdrawn` : `${name}: the share of each entry year's positions withdrawn`}
          note={rateVar === "mw_withdrawal_rate" ? "Withdrawn MW over MW entered, as the queue states MW, one point an entry year (ruling alternative 3; on the site the share is by count in both views)." : "Withdrawn positions over positions entered, by count, one point an entry year."}>
          <LineChart x="year" unit="share" height={240} ariaLabel={`${name}: withdrawn share of positions entered, by entry year`}
            lines={[{ label: "Withdrawn, share of entered", points: along(rateVar), color: "accent" }]} />
        </ChartFrame>
      ) : null}
      {has("wait_years_median") ? (
        <ChartFrame title={`${name}: the median wait from entry to operation`} note="Years from the queue date to the in-service date, for the positions of each entry year that reached operation with both dates."
          tip={<Tip id="wait-counts" label="whose waits a point counts">{waitTip(iso)}</Tip>}>
          <LineChart x="year" unit="years" height={240} ariaLabel={`${name}: median years from queue entry to operation, by entry year`}
            lines={[{ label: "Median wait", points: along("wait_years_median"), color: "accent" }]} />
        </ChartFrame>
      ) : null}

      <ToolSection title={`Every entry year, ${lo} to ${hi}, ${unit}`}
        note={<>Each figure is one row of the table; the page adds none up. {undated !== null ? <>The table&apos;s header counts <Num check={headerKey(iso, UNDATED, name)} raw={undated} source={`${TABLE}: the header line "${UNDATED}", ${name}. Source: the table's own header, written when the table was built from ${name}'s queue (${iso}_interconnection_queue). Method: Energy projects, Queue statistics.`}>{shown(undated)}</Num> of {name}&apos;s positions with no queue date, in no year.</> : null}</>}>
        <ToolTable caption={`${name}'s queue by entry year and status, ${unit}`} minWidth={measure === "mw" ? 640 : 820}
          head={measure === "mw"
            ? ["Entry year", "Entered", ...ownHead, ...(rateVar === "mw_withdrawal_rate" ? ["Withdrawn, share of MW entered"] : [])]
            : ["Entry year", "Entered", ...ownHead, "Withdrawn, share of entered", "Median wait, years", "Waits counted"]}
          rows={span.map((y) => ({
            key: String(y), muted: partial(y),
            cells: [`${y}${partial(y) ? " (partial)" : ""}`, <N key="e" y={y} v={`${prefix}_entered`} />, ...STATUSES.map((s) => <N key={s.key} y={y} v={`${prefix}_${s.key}`} />),
              ...(measure === "mw" ? (rateVar === "mw_withdrawal_rate" ? [<N key="r" y={y} v="mw_withdrawal_rate" />] : []) : [<N key="r" y={y} v="withdrawal_rate" />, <N key="m" y={y} v="wait_years_median" />, <N key="c" y={y} v="wait_positions" />])],
          }))} />
      </ToolSection>

      <ToolSection title={`The six queues, entered ${hi}, ${unit}`}
        note={<>Each queue&apos;s positions of the one entry year, in its own status words. A queue whose publisher asks for permission is held.{across.ok ? "" : " The other queues could not be read."}</>}>
        <ToolTable caption={`The six queues' positions entered in ${hi}, by status, ${unit}`} minWidth={measure === "mw" ? 640 : 940}
          head={["Queue", "Entered", ...statusHead, ...queueColumns.map(([, label]) => label)]}
          rows={QUEUES.map(([q, n]) => licenseHeldGrid(q)
            ? { key: q, cells: [n], wide: <span data-license-held={TABLE} title={licenseTitle(TABLE)}>{LICENSE_NEEDED}</span> }
            : { key: q, highlight: q === iso, cells: [<span key="q" data-queue-row={q}>{n}{ownWords(q)}</span>, <N key="e" q={q} y={hi} v={`${prefix}_entered`} from={q === iso ? rows : acrossRows} />,
              ...STATUSES.map((s) => <N key={s.key} q={q} y={hi} v={`${prefix}_${s.key}`} from={q === iso ? rows : acrossRows} />),
              ...queueColumns.map(([v]) => <N key={v} q={q} y={hi} v={v} from={q === iso ? rows : acrossRows} />)] })} />
      </ToolSection>

      <p className="max-w-3xl text-sm" data-related-view="1">
        The same table is drawn one queue at a time on the <Link href={`/map?tab=queues&iso=${iso}`}>map&apos;s Queues tab</Link>; Berkeley Lab&apos;s
        Queued Up, by grid and technology, is on <Link href="/queues">the interconnection queue page</Link>. Queued Up is another source, a
        yearly record of every request, PJM&apos;s, MISO&apos;s, NYISO&apos;s and ISO-NE&apos;s among them: its count for a queue and an entry
        year is not this page&apos;s, which is the operator&apos;s own report on the day it was pulled.
      </p>
      <p className="mt-3 max-w-3xl text-sm" data-load-side="1">
        Every position here is a plant or a battery asking to connect to the grid. A customer&apos;s request for power, a datacenter&apos;s among them,
        is in no figure of this page: ERCOT&apos;s large-load status is on <Link href="/datacenters">the datacenter tracker</Link>, and a grid&apos;s
        generator wait stands beside the large-load rules held in the &quot;Time to connect&quot; column of <Link href="/cost-of-power?view=allgrids">the All grids tab</Link>.
      </p>
      <InterconnectionDecisions />
    </>
  );
  return frame(filters, body);
}
