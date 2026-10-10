import type { Metadata } from "next";
import { cookies } from "next/headers";
import { notFound } from "next/navigation";
import { Section } from "@/components/Section";
import { COOKIE } from "@/lib/release";
import { rpc } from "@/lib/supabase";
import { internalOk } from "@/lib/thesis/server";

// Session 177: how the site's tools are used, as counts (docs/methods/usage_counts.md). Internal: no nav link, not
// indexed, and behind the internal view exactly as /internal/costs is: the page answers 404 unless the browser holds
// the internal cookie (or the address carries ?token=<INTERNAL_COSTS_TOKEN>, as the older internal pages take it), and
// the database answers nothing unless the token equals the secret apply.py wrote (internal_usage, migration 028).
// What comes back is counts: no hash, no address. A line of "*" is a total over that column.
export const metadata: Metadata = { title: "Usage (internal)", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

type Row = { day: string; path: string; tool: string; event: string; events: number; visitors: number };
type Usage = { today: string; since: string; rows: Row[] };

const n = (v: number) => Math.round(Number(v)).toLocaleString("en-US");
const EVENTS = ["tool opened", "input changed", "scenario compared", "download"];

/** Sum the finest lines (a real path, tool and event) by a key, with the events split by kind. */
function by(rows: Row[], key: (r: Row) => string) {
  const m = new Map<string, { events: number; kinds: Record<string, number> }>();
  for (const r of rows) {
    if (r.path === "*" || r.tool === "*" || r.event === "*") continue;
    const g = m.get(key(r)) ?? { events: 0, kinds: {} };
    g.events += Number(r.events);
    g.kinds[r.event] = (g.kinds[r.event] ?? 0) + Number(r.events);
    m.set(key(r), g);
  }
  return [...m.entries()];
}

function Counts({ rows, label, visitors }: { rows: ReturnType<typeof by>; label: string; visitors?: Map<string, number> }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm tabular-nums">
        <thead>
          <tr className="border-b border-rule text-left text-xs text-muted">
            <th className="py-1 pr-3">{label}</th>
            {EVENTS.map((e) => <th key={e} className="pr-3 text-right">{e}</th>)}
            <th className="pr-3 text-right">All events</th>
            {visitors ? <th className="text-right">Browser-days</th> : null}
          </tr>
        </thead>
        <tbody>
          {rows.map(([k, g]) => (
            <tr key={k} className="border-b border-rule" data-usage-row={k}>
              <td className="py-1 pr-3 font-mono text-xs">{k || "(no tool name)"}</td>
              {EVENTS.map((e) => <td key={e} className="pr-3 text-right">{n(g.kinds[e] ?? 0)}</td>)}
              <td className="pr-3 text-right">{n(g.events)}</td>
              {visitors ? <td className="text-right">{n(visitors.get(k) ?? 0)}</td> : null}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default async function UsagePage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const token = typeof sp.token === "string" ? sp.token : "";
  const want = process.env.INTERNAL_COSTS_TOKEN ?? "";
  if (want.length < 24 || (token !== want && !(await internalOk((await cookies()).get(COOKIE)?.value)))) notFound();

  let u: Usage;
  try {
    u = await rpc<Usage>("internal_usage", { p_token: want });
  } catch (e) {
    return (
      <div data-usage="unread">
        <h1 className="mb-2 text-3xl">Usage (internal)</h1>
        <p className="text-sm">The usage counts could not be read: {(e as Error).message.slice(0, 160)}. Until migration 028 is applied the site records nothing.</p>
      </div>
    );
  }
  const rows = u.rows ?? [];
  // browser-days: a day's distinct browsers, added over the days (the same browser on two days is two: nobody is followed)
  const sumVisitors = (pick: (r: Row) => string | null) => {
    const m = new Map<string, number>();
    for (const r of rows) {
      const k = pick(r);
      if (k !== null) m.set(k, (m.get(k) ?? 0) + Number(r.visitors));
    }
    return m;
  };
  const dayVisitors = sumVisitors((r) => (r.path === "*" && r.tool === "*" && r.event === "*" ? r.day : null));
  const pageVisitors = sumVisitors((r) => (r.path !== "*" && r.tool === "*" && r.event === "*" ? r.path : null));
  const toolVisitors = sumVisitors((r) => (r.path === "*" && r.tool !== "*" && r.event === "*" ? r.tool : null));
  const byDay = by(rows, (r) => r.day).sort((a, b) => b[0].localeCompare(a[0]));
  const byPage = by(rows, (r) => r.path).sort((a, b) => b[1].events - a[1].events);
  const byTool = by(rows, (r) => r.tool).sort((a, b) => b[1].events - a[1].events);
  const total = byDay.reduce((a, [, g]) => a + g.events, 0);
  const today = dayVisitors.get(u.today) ?? 0;

  return (
    <div data-usage="1">
      <h1 className="mb-1 text-3xl">Usage (internal)</h1>
      <p className="mb-5 max-w-3xl text-sm text-muted">
        How the tools are used since {u.since}, as counts: no cookie, no address, nothing that follows a person. A browser is counted by a
        code that lasts one UTC day, so the same reader on two days is two browser-days. A visitor who asked for a page in review is counted
        under that page with the tool &quot;In review (not opened)&quot;. Browsers that send Do Not Track or Global Privacy Control are not counted.
      </p>
      <div className="mb-8 grid grid-cols-1 gap-px border border-rule bg-rule sm:grid-cols-3">
        <div className="bg-panel p-3"><div className="text-xs text-muted">Events since {u.since}</div><div className="text-2xl tabular-nums" data-n="events">{n(total)}</div></div>
        <div className="bg-panel p-3"><div className="text-xs text-muted">Browsers today, {u.today}</div><div className="text-2xl tabular-nums" data-n="today">{n(today)}</div></div>
        <div className="bg-panel p-3"><div className="text-xs text-muted">Days with any event</div><div className="text-2xl tabular-nums" data-n="days">{n(byDay.length)}</div></div>
      </div>
      {rows.length === 0 ? <p className="mb-8 text-sm">No event is recorded yet.</p> : null}
      <Section title="By day"><Counts rows={byDay} label="Day (UTC)" visitors={dayVisitors} /></Section>
      <Section title="By page"><Counts rows={byPage} label="Path" visitors={pageVisitors} /></Section>
      <Section title="By tool"><Counts rows={byTool} label="Tool" visitors={toolVisitors} /></Section>
    </div>
  );
}
