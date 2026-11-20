import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { AutoSubmitSelect } from "@/components/AutoSubmit";
import { Hint } from "@/components/demand/Hint";
import { LineChart, type Line } from "@/components/LineChart";
import { ChartFrame, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { TableDownloads } from "@/components/tool/TableDownloads";
import raw from "@/data/queue_places.json";
import { QueuePlacesDecisions } from "./Decisions";

// Session 8014 (chain 581, part F2): the interconnection queues outside the seven grids, by place. Reads
// data/queue_places.json (warehouse/derived/queue_places.py, method docs/methods/queue_places.md): LBNL's compilation of
// the public queues of the West and the Southeast, each under LBNL's name of its owner, and every state with people
// outside the seven grids, a state no entry names listed as such. Two owners side by side. /queues does not change.
// In review, in no menu.
export const metadata: Metadata = { title: "Queues outside the seven grids", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

type Owner = { owner: string; region: string; entries: number; by_status: Record<string, { entries: number; mw: number | null }>;
  active_mw_by_type: Record<string, number | null>; active_mw_by_year: Record<string, number | null>; states: Record<string, number>; first_year: string | null; last_year: string | null };
type State = { state: string; name: string; share_outside_pct: number; entries: number; active_entries: number; active_mw: number | null; owners: string[]; no_public_queue: boolean };
type File = { built: string; tables: string[]; vintage: string; source: string; rule: string; owners: Owner[]; states: State[] };
const F = raw as unknown as File;
type Query = Record<string, string | string[] | undefined>;
const one = (q: Query, k: string) => (typeof q[k] === "string" ? (q[k] as string) : undefined);
const whole = (v: number) => Math.round(v).toLocaleString("en-US");
const SRC = `${F.source}, ${F.vintage}. ${F.rule}`;
const STATUS_WORDS: Record<string, string> = { active: "Active", suspended: "Suspended", operational: "Operational", withdrawn: "Withdrawn", unknown: "Status unknown" };
const key = (o: Owner) => `${o.region}:${o.owner}`;

function Fig({ v, k, src = SRC, reason }: { v: number | null | undefined; k: string; src?: string; reason?: string }) {
  if (v === null || v === undefined) return <span className="cursor-help text-muted" title={reason ?? `Not held. ${src}`} data-not-held={k}>not held</span>;
  return <span className="cursor-help" title={src} data-fig={k}>{whole(v)}</span>;
}

export default async function QueuePlaces({ searchParams }: { searchParams: Promise<Query> }) {
  const q = await searchParams;
  const keys = F.owners.map(key);
  const a = keys.includes(one(q, "a") ?? "") ? (one(q, "a") as string) : keys[0];
  const b = keys.includes(one(q, "b") ?? "") && one(q, "b") !== a ? (one(q, "b") as string) : keys[1];
  const A = F.owners.find((o) => key(o) === a) as Owner, B = F.owners.find((o) => key(o) === b) as Owner;
  const options = F.owners.map((o) => ({ value: key(o), label: `${o.owner} (${o.region})` }));
  const types = [...new Set([...Object.keys(A.active_mw_by_type), ...Object.keys(B.active_mw_by_type)])].sort();
  const pts = (o: Owner) => Object.entries(o.active_mw_by_year).filter(([y, v]) => /^\d{4}$/.test(y) && v !== null).map(([y, v]) => ({ t: Date.UTC(Number(y), 0, 1) / 1000, v: v as number }));
  const lines: Line[] = [{ label: A.owner, color: "accent", points: pts(A) }, { label: B.owner, color: "series-3", points: pts(B) }];
  const none = F.states.filter((s) => s.no_public_queue);

  return (
    <Brand>
    <ToolPage>
      <div data-queue-places="1">
      <ToolHeader
        title="Queues outside the seven grids"
        crumb={<a href="/queues" className="underline">Interconnection queues</a>}
        lead={<>The public interconnection queues of the utilities and federal power marketers of the West and the Southeast, outside the seven grid operators, each under the name Lawrence Berkeley National Laboratory gives its owner; and every state with people outside the seven grids, with what its queues hold. Two owners side by side. <Hint words="What is counted" why={F.rule} /></>}
        under={<p className="mt-2 text-xs text-muted" data-license-line="1">License: public (LBNL). {F.vintage}; file built {F.built.slice(0, 10)}.</p>}
      />
      <form method="get" action="/queues/places#side" className="mb-3 flex flex-wrap items-end gap-3 text-sm [&_label]:max-w-full [&_select]:max-w-full" data-queue-places-form="1">
        <AutoSubmitSelect name="a" value={a} options={options} label="Queue A" />
        <AutoSubmitSelect name="b" value={b} options={options.filter((o) => o.value !== a)} label="Queue B" />
        <button type="submit" className="border border-rule bg-white px-3 py-1 text-sm">Show</button>
      </form>

      <ToolSection title="Two queues side by side" id="side">
        <ToolTable minWidth={520} caption={`${A.owner} and ${B.owner}`} head={["", `A: ${A.owner} (${A.region})`, `B: ${B.owner} (${B.region})`]}
          rows={[
            { key: "entries", cells: ["Entries, every status", <Fig key="a" v={A.entries} k="qa-n" />, <Fig key="b" v={B.entries} k="qb-n" />] },
            ...Object.keys(STATUS_WORDS).map((s) => ({ key: s, cells: [`${STATUS_WORDS[s]}, MW`,
              <Fig key="a" v={A.by_status[s]?.mw ?? null} k={`qa-${s}`} reason="No entry of this status." />, <Fig key="b" v={B.by_status[s]?.mw ?? null} k={`qb-${s}`} reason="No entry of this status." />] })),
            ...types.map((t) => ({ key: `t-${t}`, cells: [`Active ${t}, MW`, <Fig key="a" v={A.active_mw_by_type[t] ?? null} k={`qa-t-${t}`} reason="No active entry of this type." />, <Fig key="b" v={B.active_mw_by_type[t] ?? null} k={`qb-t-${t}`} reason="No active entry of this type." />] })),
            { key: "years", cells: ["Years entered", `${A.first_year ?? "?"} to ${A.last_year ?? "?"}`, `${B.first_year ?? "?"} to ${B.last_year ?? "?"}`] },
            { key: "states", cells: ["States named", Object.keys(A.states).join(", ") || "none", Object.keys(B.states).join(", ") || "none"] },
          ]} />
        <ChartFrame title="Active MW by the year each entry entered the queue" tip={<Hint words=" (source)" why={SRC} />}>
          <LineChart lines={lines} unit="MW" x="year" ariaLabel={`Active queue MW by year entered, ${A.owner} and ${B.owner}`} />
        </ChartFrame>
      </ToolSection>

      <ToolSection title="Every queue owner" id="owners">
        <ToolTable minWidth={640} caption="Queue owners of the West and the Southeast, by active MW" head={["Owner", "Region", "Active MW", "Operational MW", "Withdrawn MW", "Entries"]}
          rows={F.owners.map((o, i) => ({ key: key(o), highlight: key(o) === a || key(o) === b, cells: [
            <a key="n" className="underline" href={`/queues/places?a=${encodeURIComponent(key(o))}&b=${encodeURIComponent(key(o) === b ? a : b)}`} data-rank={i + 1}>{i + 1}. {o.owner}</a>, o.region,
            <Fig key="a" v={o.by_status.active?.mw ?? null} k={`o-${key(o)}-a`} reason="No active entry." />, <Fig key="o" v={o.by_status.operational?.mw ?? null} k={`o-${key(o)}-o`} reason="No operational entry." />,
            <Fig key="w" v={o.by_status.withdrawn?.mw ?? null} k={`o-${key(o)}-w`} reason="No withdrawn entry." />, whole(o.entries)] }))} />
      </ToolSection>

      <ToolSection title="States with people outside the seven grids" id="states">
        <ToolTable minWidth={600} caption="Each state's people outside the seven grids, and the queue entries of the West and the Southeast that name it" head={["State", "People outside the seven grids", "Entries", "Active MW", "Queue owners"]}
          rows={F.states.map((s) => ({ key: s.state, cells: [s.name, `${s.share_outside_pct.toFixed(1)}%`, s.no_public_queue ? <span key="n" className="text-muted" data-no-queue={s.state}>no public queue in the compilation</span> : whole(s.entries),
            <Fig key="m" v={s.active_mw} k={`s-${s.state}-mw`} reason={s.no_public_queue ? "No entry names this state." : "No active entry."} />, s.owners.join(", ") || "none"] }))} />
        <p className="mt-2 text-xs text-muted">{none.length ? `${none.length} state${none.length === 1 ? "" : "s"} with no entry: ${none.map((s) => s.name).join(", ")}.` : "Every state with people outside the seven grids is named by at least one entry of LBNL's West or Southeast."} A share is of the state&apos;s people by county (eia_county_region and the Census Bureau&apos;s county estimates).</p>
      </ToolSection>

      <QueuePlacesDecisions />
      <TableDownloads tables={F.tables} />
      <SourceLine tables={F.tables} note={<>Method: <a href="/data/methods/queue_places">the page&apos;s method note</a>. LBNL&apos;s entries counted and summed by owner and state; nothing estimated.</>} />
      </div>
    </ToolPage>
    </Brand>
  );
}
