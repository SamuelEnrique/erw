import type { Metadata } from "next";
import Link from "next/link";
import { SiteLink } from "@/components/SiteLink";
import { Band, Trend } from "@/components/supply/SupplyCharts";
import fileJson from "@/data/supply.json";
import { HEADLINE, PLACEHOLDER, choiceOf, dateWords, easternNow, fmt, nextRelease, hrefOf, pct, reading, releaseWords, rowsOf, shortDate, signed, surprises, toggled, withUnitWords, type Choice, type Group, type Row, type SupplyFile } from "@/lib/supply";

// Session 134: Supply and trade, for a trader in oil, gas and power. One question: is the market tighter or looser than
// last week, last year and normal for the season. Every number stands against those three, and the week's change against
// the five-year average change, with the surprise marked. Every figure is in the site's own file (data/supply.json,
// written by warehouse/derived/supply_page.py from tables in the warehouse). No method stands on the page face: it is in
// docs/methods/supply_and_trade.md. The whole state is in the address.
export const metadata: Metadata = { title: "Supply and trade", robots: { index: false, follow: false } };

const file = withUnitWords(fileJson as unknown as SupplyFile);
const METHOD = "/data/methods/supply_and_trade";
const NH = ({ why, words = "not held yet" }: { why: string; words?: string }) => <span className="cursor-help whitespace-nowrap border-b border-dotted border-muted text-[11px] italic text-muted" title={why} data-missing="1">{words}</span>;

/** A difference the page writes as zero carries no reading. */
const moved = (diff: number, row: Row) => /[1-9]/.test(signed(diff, row.unit, row.last!.v));

function Tag({ r }: { r: "tighter" | "looser" | null }) {
  if (!r) return null;
  return <span className={`ml-1 rounded-sm border px-1 text-[10px] ${r === "tighter" ? "border-up text-up" : "border-down text-down"}`}>{r}</span>;
}

/** One comparison: the difference with its sign, the percent where the series cannot be negative, and the reading. */
function Against({ row, diff, percent, from, what }: { row: Row; diff: number | null | undefined; percent?: number | null; from?: { t: string; v: number }; what: string }) {
  if (diff === null || diff === undefined) return <NH why={`The value this is measured against is not held (${what}).`} />;
  return (
    <span className="whitespace-nowrap" title={from ? `against ${fmt(from.v, row.unit)} ${row.unit}, ${what}${from.t ? ` (${dateWords(from.t, row.freq)})` : ""}` : what}>
      {signed(diff, row.unit, row.last!.v)}
      {percent !== null && percent !== undefined ? <span className="ml-1 text-[10px] text-muted">{pct(percent)}</span> : null}
      <Tag r={moved(diff, row) ? reading(row.sense, diff) : null} />
    </span>
  );
}

function Surprise({ row }: { row: Row }) {
  const c = row.change;
  if (!c) return <NH why="The value one step before the latest is not held." />;
  if (c.surprise === null || c.avg5 === null) return <NH why="The same change is not held for each of the five years before." />;
  const title = `this ${row.freq === "M" ? "month" : "week"}'s change ${signed(c.v, row.unit, row.last!.v)} ${row.unit}; the five-year average change of the same ${row.freq === "M" ? "month" : "week"} ${signed(c.avg5, row.unit, row.last!.v)}; the five years' changes ran from ${signed(c.lo!, row.unit, row.last!.v)} to ${signed(c.hi!, row.unit, row.last!.v)}`;
  return (
    <span className={`whitespace-nowrap ${c.outside ? "border border-accent bg-paper px-1 font-semibold" : ""}`} title={title} data-surprise={c.outside ? row.id : undefined}>
      {signed(c.surprise, row.unit, row.last!.v)}{c.outside ? <span className="ml-1 text-[10px] font-normal text-accent">outside range</span> : null}
    </span>
  );
}

function Table({ group, c }: { group: Group; c: Choice }) {
  const rows = rowsOf(file, group.id);
  const pos = group.id === "position";
  return (
    <section id={group.id} className="mb-7 scroll-mt-4" data-group={group.id}>
      <h2 className="mb-1 border-b border-accent pb-0.5 font-serif text-lg text-accent">{group.title}</h2>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[1080px] border-collapse text-sm tabular-nums">
          <thead>
            <tr className="border-b border-rule text-[10px] uppercase tracking-wide text-muted">
              <th className="py-1 pl-2 text-left font-normal">Series</th>
              <th className="pr-3 text-right font-normal">Latest</th>
              <th className="pr-3 text-right font-normal">Its date</th>
              <th className="pr-3 text-right font-normal" title="The latest less the value one step before: a week for a weekly series, a month for a monthly one">On the period before</th>
              <th className="pr-3 text-right font-normal">On last year</th>
              <th className="pr-3 text-right font-normal">Five-year average</th>
              <th className="pr-3 text-right font-normal">Against the average</th>
              <th className="pr-3 text-right font-normal" title="The period's change less the five-year average change of the same period">Change against the five-year average change</th>
              <th className="pr-3 text-right font-normal">Last 52</th>
              {pos ? <><th className="pr-3 text-right font-normal">Long</th><th className="pr-3 text-right font-normal">Short</th><th className="pr-2 text-right font-normal">In its three-year range</th></> : null}
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => {
              const name = (
                <th scope="row" className="whitespace-nowrap py-1 pl-2 pr-3 text-left font-normal">
                  {r.status === "ok"
                    ? <Link href={`${hrefOf(c, { s: r.id })}#chart`} scroll className="text-ink underline decoration-rule underline-offset-2 hover:text-accent" title={`${r.source !== undefined ? `Source: ${file.sources[r.source]}. ` : ""}Open its seasonal chart.`} data-open={r.id}>{r.label}</Link>
                    : <span className="text-muted">{r.label}</span>}
                  <span className="ml-1.5 text-[11px] text-muted">{r.at}</span>
                </th>
              );
              if (r.status !== "ok") {
                return <tr key={r.id} className="border-b border-rule/70" data-row={r.id} data-status={r.status}>{name}<td colSpan={pos ? 11 : 8} className="py-1 pr-2 text-left"><NH why={r.note ?? ""} words={PLACEHOLDER[r.status]} /></td></tr>;
              }
              const last = r.last!;
              return (
                <tr key={r.id} className={`border-b border-rule/70 ${c.s === r.id ? "bg-paper" : ""}`} data-row={r.id}>
                  {name}
                  <td className="whitespace-nowrap py-1 pr-3 text-right font-semibold"><span data-n={`${r.id}|last`}>{fmt(last.v, r.unit)}</span><span className="ml-1 text-[10px] font-normal text-muted">{r.unit}</span></td>
                  <td className="whitespace-nowrap py-1 pr-3 text-right text-[11px] text-muted" title={r.freq === "M" ? "a monthly series" : "a weekly series: the date its week ends"}>{dateWords(last.t, r.freq)}</td>
                  <td className="py-1 pr-3 text-right text-xs"><Against row={r} diff={r.prev?.ch} from={r.prev ?? undefined} what={r.freq === "M" ? "the month before" : "the week before"} /></td>
                  <td className="py-1 pr-3 text-right text-xs"><Against row={r} diff={r.year?.ch} percent={r.year?.pct} from={r.year ?? undefined} what="a year before" /></td>
                  <td className="py-1 pr-3 text-right text-xs">{r.avg5 ? <span title={`the five years before ran from ${fmt(r.avg5.lo, r.unit, last.v)} to ${fmt(r.avg5.hi, r.unit, last.v)} ${r.unit} at this point of the year`} data-n={`${r.id}|avg5`}>{fmt(r.avg5.v, r.unit, last.v)}</span> : <NH why="One of the five years before does not hold this point of the year." />}</td>
                  <td className={`py-1 pr-3 text-right text-xs ${r.avg5?.outside ? "font-semibold" : ""}`}>{r.avg5 ? <Against row={r} diff={r.avg5.ch} percent={r.avg5.pct} what={`the five-year average${r.avg5.outside ? "; the latest is outside the five years' range" : ""}`} /> : <NH why="One of the five years before does not hold this point of the year." />}</td>
                  <td className="py-1 pr-3 text-right text-xs"><Surprise row={r} /></td>
                  <td className="py-0.5 pr-3 text-right"><Trend row={r} /></td>
                  {pos ? <>
                    <td className="py-1 pr-3 text-right text-xs">{r.long !== undefined ? fmt(r.long, "contracts") : ""}</td>
                    <td className="py-1 pr-3 text-right text-xs">{r.short !== undefined ? fmt(r.short, "contracts") : ""}</td>
                    <td className="whitespace-nowrap py-1 pr-2 text-right text-xs">{r.three_year?.pos !== null && r.three_year?.pos !== undefined
                      ? <span title={`between ${fmt(r.three_year.lo, "contracts")} and ${fmt(r.three_year.hi, "contracts")} contracts over the last ${r.three_year.n} weeks; open interest ${fmt(r.open_interest ?? 0, "contracts")}, net position ${r.net_share_pct ?? ""}% of it`}>{Math.round(r.three_year.pos * 100)}% of the way up</span> : null}</td>
                  </> : null}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default async function Supply({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const c = choiceOf(await searchParams, file);
  const shown = file.groups.filter((g) => !c.groups.length || c.groups.includes(g.id));
  const open = c.s ? file.rows.find((r) => r.id === c.s) ?? null : null;
  const head = HEADLINE.map((id) => file.rows.find((r) => r.id === id && r.status === "ok")).filter((r): r is Row => !!r);
  const sur = surprises(file).slice(0, 8);
  const eastern = easternNow(new Date());      // the page is rendered when it is asked for: the next releases are as of now
  const bands = shown.filter((g) => g.band).flatMap((g) => rowsOf(file, g.id).filter((r) => r.status === "ok" && r.season && !/salt/.test(r.at) && r.id !== "eia-wcsstus1"));
  return (
    <div className="border border-rule bg-white px-3 py-4 text-ink sm:px-5" data-supply="1">
      <header className="mb-3 flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1 border-b border-rule pb-2">
        <h1 className="font-serif text-3xl text-accent">Supply and trade</h1>
        <p className="text-xs text-muted"><SiteLink href={METHOD}>Method, sources and gaps</SiteLink>{" | "}<span title={`The page's file was built at ${file.built}.`}>built {dateWords(file.built)}</span></p>
      </header>

      <section className="mb-5" aria-label="Tighter or looser" data-headline="1">
        <h2 className="mb-1 text-xs uppercase tracking-wide text-muted">Tighter or looser than last week, last year and normal for the season</h2>
        <div className="grid gap-px border border-rule bg-rule sm:grid-cols-2 xl:grid-cols-5">
          {head.map((r) => (
            <Link key={r.id} href={`${hrefOf(c, { s: r.id })}#chart`} className="block bg-white px-2 py-1.5 text-ink no-underline hover:bg-paper" title={`${r.label}, ${r.at}. Open its seasonal chart.`}>
              <span className="block text-[10px] uppercase tracking-wide text-muted">{r.label}, {r.at}</span>
              <span className="block font-serif text-xl tabular-nums"><span data-n={`head|${r.id}`}>{fmt(r.last!.v, r.unit)}</span><span className="ml-1 font-sans text-[10px] text-muted">{r.unit}, {shortDate(r.last!.t)}</span></span>
              {([["Week", r.prev?.ch, null], ["Year", r.year?.ch, r.year?.pct], ["Normal", r.avg5?.ch, r.avg5?.pct]] as const).map(([k, d, p]) => (
                <span key={k} className="block text-[11px] tabular-nums">
                  <span className="inline-block w-12 text-muted">{k}</span>
                  {d === null || d === undefined ? <NH why="The value this is measured against is not held." /> : <>{signed(d, r.unit, r.last!.v)}{p !== null && p !== undefined ? <span className="ml-1 text-muted">{pct(p)}</span> : null}<Tag r={moved(d, r) ? reading(r.sense, d) : null} /></>}
                </span>
              ))}
            </Link>
          ))}
        </div>
      </section>

      <div className="mb-5 grid gap-4 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
        <section aria-label="Surprises" className="min-w-0" data-surprises="1">
          <h2 className="mb-1 text-xs uppercase tracking-wide text-muted">Changes outside the five years&apos; range, in the newest reports</h2>
          {sur.length ? (
            <ul className="grid grid-cols-1 gap-x-6 text-xs tabular-nums sm:grid-cols-2">
              {sur.map((r) => (
                <li key={r.id} className="flex min-w-0 justify-between gap-2 border-b border-rule/60 py-0.5">
                  <Link href={`${hrefOf(c, { s: r.id })}#chart`} className="min-w-0 truncate text-ink underline decoration-rule underline-offset-2" title={`${r.label}, ${r.at}, ${dateWords(r.last!.t, r.freq)}`}>{r.label}, {r.at}</Link>
                  <span className="whitespace-nowrap" title={`changed ${signed(r.change!.v, r.unit, r.last!.v)} ${r.unit}; the five-year average change is ${signed(r.change!.avg5!, r.unit, r.last!.v)}`}>
                    <strong>{signed(r.change!.surprise!, r.unit, r.last!.v)}</strong> <span className="text-muted">{r.unit}</span>
                  </span>
                </li>
              ))}
            </ul>
          ) : <NH why="No series' newest change stands outside its five years' changes." words="none this week" />}
        </section>
        <section aria-label="Release calendar" className="min-w-0" data-calendar="1">
          <h2 className="mb-1 text-xs uppercase tracking-wide text-muted">Next releases</h2>
          <ul className="text-xs">
            {file.calendar.reports.map((r) => { const n = nextRelease(r, eastern);
              return (
                <li key={r.id} className="flex justify-between gap-2 border-b border-rule/60 py-0.5" title={`${r.publisher}, ${r.name}: ${r.rule}; ${r.covers}. ${n.moved ? `This one is ${n.moved}. ` : ""}Read from ${r.read}.`}>
                  <span>{r.publisher} {r.name}</span>
                  <span className="whitespace-nowrap tabular-nums" data-release={r.id}>{releaseWords(n.next)}{n.moved ? <span className="ml-1 text-accent">moved</span> : null}</span>
                </li>
              ); })}
          </ul>
        </section>
      </div>

      <div className="mb-5 flex flex-wrap items-center gap-1 border-y border-rule py-2 text-[11px]" role="group" aria-label="Select" data-controls="1">
        <span className="mr-1 text-muted">Select</span>
        <Link href={hrefOf(c, { groups: [] })} scroll={false} style={{ color: c.groups.length ? "var(--color-ink)" : "#fff" }} className={`border px-1.5 py-px no-underline ${c.groups.length ? "border-rule bg-white hover:border-accent" : "border-accent bg-accent"}`}>Everything</Link>
        {file.groups.map((g) => { const on = c.groups.includes(g.id);
          return <Link key={g.id} href={hrefOf(c, { groups: toggled(c.groups, g.id) })} scroll={false} data-chip={g.id} style={{ color: on ? "#fff" : "var(--color-ink)" }} className={`border px-1.5 py-px no-underline ${on ? "border-accent bg-accent" : "border-rule bg-white hover:border-accent"}`}>{g.title.replace(/, (weekly|monthly).*$/, "")}</Link>; })}
      </div>

      {open ? (
        <section id="chart" className="mb-6 scroll-mt-4 border border-accent bg-paper/40 p-3" data-open-chart={open.id}>
          <div className="mb-1 flex flex-wrap items-baseline justify-between gap-2">
            <h2 className="font-serif text-lg text-accent">{open.label}, {open.at}: this year against the five years before</h2>
            <Link href={hrefOf(c, { s: null })} scroll={false} className="border border-rule bg-white px-1.5 py-0.5 text-[11px] text-ink no-underline hover:border-accent">Close</Link>
          </div>
          <Band row={open} height={360} />
        </section>
      ) : null}

      {bands.length ? (
        <section className="mb-7" aria-label="Seasonal bands" data-bands="1">
          <h2 className="mb-2 border-b border-accent pb-0.5 font-serif text-lg text-accent">Storage and stocks through the year, against the five years before</h2>
          <div className="grid gap-4 lg:grid-cols-2 2xl:grid-cols-3">
            {bands.map((r) => <div key={r.id} className="min-w-0"><h3 className="mb-1 text-sm font-semibold">{r.label}, {r.at}</h3><Band row={r} height={250} /></div>)}
          </div>
        </section>
      ) : null}

      {shown.map((g) => <Table key={g.id} group={g} c={c} />)}
    </div>
  );
}
