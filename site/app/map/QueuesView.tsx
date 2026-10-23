// Session 349: the map's Queues tab. Each ISO's interconnection queue by the year a position entered it, from
// iso_queue_statistics (session 348, warehouse/derived/queue_statistics.py): entered against operating, the share
// withdrawn and the median wait from entry to operation, through the shared chart (Chart | Table) and a table whose
// every figure is the table's own row, read from Supabase and checked by scripts/check-values.mjs (series| keys).
// What a queue does not hold is said, never filled: ERCOT's withdrawn positions; MISO's and ISO-NE's in-service dates.
// A grid whose queue is licensed (NYISO, MISO, ISO-NE from 21 October 2026) is held by grid, as its queue table is.
import { Num } from "@/components/Num";
import { SiteLink as Link } from "@/components/SiteLink";
import { ToolPicker } from "@/components/tool/Choose";
import { SourceLine, Tip, ToolHeader, ToolTable } from "@/components/tool/ToolPage";
import { LICENSE_NEEDED, licenseHeldGrid } from "@/lib/license";
import { HOURLY, attempt, rest } from "@/lib/supabase";
import { QueueCharts } from "./QueueCharts";

export const QUEUE_TABLE = "iso_queue_statistics";
const METHOD = "/data/methods/energy_projects";
export const QUEUE_ISOS: [string, string][] = [["caiso", "CAISO"], ["ercot", "ERCOT"], ["nyiso", "NYISO"], ["miso", "MISO"], ["spp", "SPP"], ["isone", "ISO-NE"]];
const NOT_HELD: Record<string, string> = {
  ercot: "ERCOT's report lists active and completed positions only, so no withdrawn count and no withdrawal rate are held.",
  miso: "MISO's queue holds no in-service date, so no wait is held.",
  isone: "ISO-NE's queue holds no in-service date, so no wait is held.",
  spp: "SPP's wait reads its Commercial Operation Date, which its queue fills for active and withdrawn positions too: for an operating position it may be the date requested, not achieved.",
};
type Row = { entity: string; variable: string; ts_utc: string; value: number };
const iso8601 = (ts: string) => new Date(ts).toISOString().replace(".000Z", "Z");

function S({ r, share }: { r: Row | undefined; share?: boolean }) {
  if (!r) return <span className="text-muted">not held</span>;
  const v = Number(r.value);
  return <Num check={`series|${QUEUE_TABLE}|${r.entity}|${r.variable}|${iso8601(r.ts_utc)}`} raw={v}>
    {Number.isInteger(v) && !share ? v.toLocaleString("en-US") : v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
  </Num>;
}

export async function QueuesView({ iso: asked }: { iso?: string }) {
  const iso = QUEUE_ISOS.some(([k]) => k === asked) ? asked! : QUEUE_ISOS[0][0];
  const label = QUEUE_ISOS.find(([k]) => k === iso)![1];
  const held = licenseHeldGrid(iso);
  const read = held ? null : await attempt(() => rest<Row>("series", { select: "entity,variable,ts_utc,value", table_name: `eq.${QUEUE_TABLE}`, entity: `like.${iso}:queue_*`, order: "entity,variable" }, HOURLY));
  const rows = read?.ok ? read.data : [];
  const years = Array.from(new Set(rows.map((r) => r.entity.split("_").pop()!))).sort();
  const at = (y: string, v: string) => rows.find((r) => r.entity === `${iso}:queue_${y}` && r.variable === v);
  const val = (y: string, v: string) => { const r = at(y, v); return r ? Number(r.value) : null; };
  return (
    <div data-map-queues={iso}>
      <ToolHeader title="The interconnection queues"
        lead={<>Each ISO&apos;s queue by the year a position entered it: how many entered, how many reached operation, how many were withdrawn or still wait, and how long the ones that reached operation took. Each ISO&apos;s own status words, as the method states them. <Link href={METHOD}>Method</Link>.</>} />
      <ToolPicker label="Queue" items={QUEUE_ISOS.map(([k, name]) => ({ key: k, label: name, href: `/map?tab=queues&iso=${k}`, on: k === iso }))} />
      {NOT_HELD[iso] ? <p className="mb-4 max-w-3xl text-sm" data-queue-not-held={iso}>{NOT_HELD[iso]}</p> : null}
      {held ? (
        <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status" data-license-held={QUEUE_TABLE}>{label}&apos;s queue is held: {LICENSE_NEEDED}. Its figures are not shown.</p>
      ) : !read?.ok ? (
        <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status">The table could not be read, so no number is shown{read && !read.ok ? `: ${read.reason}` : ""}.</p>
      ) : !years.length ? (
        <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status">No year is held for {label}.</p>
      ) : (
        <>
          <QueueCharts label={label} iso={iso} years={years}
            entered={years.map((y) => val(y, "positions_entered"))} operating={years.map((y) => val(y, "positions_operating"))}
            rate={years.map((y) => val(y, "withdrawal_rate"))} wait={years.map((y) => val(y, "wait_years_median"))} />
          {/* session 2303 (chain 087): a second-level heading (the charts' titles are figure captions, not headings), in the same face */}
          <h2 className="mb-2 mt-2 font-serif text-lg text-accent">Every entry year
            <Tip id="queue-table" label="the figures of this table">Every figure is a row of {QUEUE_TABLE} as the live set holds it (its check key names the entity {iso}:queue_&lt;year&gt;, the variable and the timestamp), which the ERW derives from {label}&apos;s own queue table, {iso}_interconnection_queue, as last pulled. A figure the queue does not hold reads &quot;not held&quot; and is never filled.</Tip>
          </h2>
          <ToolTable caption={`${label}'s queue by entry year`} minWidth={760}
            head={["Entry year", "Entered", "Operating", "Withdrawn", "Still waiting", "Status not stated", "Withdrawn, share of entered", "Median wait, years", "Waits counted", "MW entered"]}
            rows={years.map((y) => ({
              key: y,
              cells: [y, <S key="e" r={at(y, "positions_entered")} />, <S key="o" r={at(y, "positions_operating")} />, <S key="w" r={at(y, "positions_withdrawn")} />,
                <S key="a" r={at(y, "positions_waiting")} />, <S key="n" r={at(y, "positions_status_not_stated")} />, <S key="r" r={at(y, "withdrawal_rate")} share />,
                <S key="m" r={at(y, "wait_years_median")} share />, <S key="c" r={at(y, "wait_positions")} />, <S key="mw" r={at(y, "mw_entered")} share />],
            }))} />
          <p className="mt-2 max-w-3xl text-xs text-muted">A position with no queue date is in no year (the table&apos;s header counts them). A recent year&apos;s positions have had less time to reach operation or to be withdrawn: its shares are not final. The cross-check against Berkeley Lab&apos;s Queued Up is in <Link href={METHOD}>the method</Link>.</p>
        </>
      )}
      <SourceLine tables={[QUEUE_TABLE]}
        note={<>Derived by the ERW from the six ISOs&apos; queue tables (<code className="font-mono">{iso}_interconnection_queue</code> for this one), as the ERW last pulled them. This tab is in review.</>} />
    </div>
  );
}
