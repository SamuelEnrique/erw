// Session 3061 (chain 166): the monitor's calendar: the actions of the past week and the dated steps of the month ahead
// (comment and intervention deadlines, effective dates, hearings and sessions, lease sales' steps), each date with the
// words it stands in as its hover and a key (data-check) that scripts/check_policy.py traces to its document's row of
// policy_actions. Every value is data/policy/monitor.json's; lib/policymonitor.ts's calendarOf only chooses and orders.
import { INSTRUMENT_WORDS, KIND_WORDS, STATUS_WORDS, calendarOf, stepKey, type MonitorRow } from "@/lib/policymonitor";

const tip = "cursor-help border-b border-dotted border-muted";

// Session 1876 (policy faults rows 4 and 6): `last` is the file's newest document date (the week runs to it when the file
// stops before today, and its heading says so); `hidden` is how many steps of the month ahead the significance floor
// hides, given as a count with a click that lifts the floor, never as "no dated step".
export function MonitorCalendar({ rows, today, last = "", built = "", hidden = 0, floor = null, liftHref = "", onLift }: {
  rows: MonitorRow[]; today: string; last?: string; built?: string; hidden?: number; floor?: number | null; liftHref?: string; onLift?: () => void;
}) {
  const c = calendarOf(rows, today, last);
  const lift = (n: number, words: string) => (
    <a href={liftHref} data-monitor-lift={n} className={tip} title={`Steps on records scored below significance ${floor}; this lifts the floor, the other filters kept.`}
      onClick={(e) => { if (onLift) { e.preventDefault(); onLift(); } }}>{words}</a>
  );
  return (
    <div className="mb-4 grid gap-4 md:grid-cols-2" data-monitor-calendar="1">
      <div>
        <h3 className="mb-1 text-sm">{c.stale ? "The file's last week" : "The past week"} <span className={`text-xs text-muted ${tip}`} data-monitor-week-to={c.weekTo}
          title={c.stale ? `Records whose newest document is dated in the seven days to ${c.weekTo}, the file's newest document (data/policy/monitor.json, built ${built}); this page's day is ${c.today}.`
            : "Records whose newest document is dated from seven days before this page's day to its day."}>{c.weekFrom} to {c.weekTo}</span></h3>
        {c.week.length === 0 ? <p className="text-xs text-muted">No action in these seven days.</p> : (
          <ul className="max-h-72 overflow-y-auto text-xs" data-monitor-week={c.week.length}>
            {c.week.slice(0, 60).map((r) => (
              <li key={r.id} className="border-b border-rule/60 py-1">
                <span className="tabular-nums">{r.date}</span> {r.body} {INSTRUMENT_WORDS[r.instrument] ?? r.instrument}, {(STATUS_WORDS[r.status] ?? r.status).toLowerCase()}:{" "}
                <a href={r.sources?.[0]}>{r.title.length > 110 ? r.title.slice(0, 107) + "..." : r.title}</a>
              </li>
            ))}
          </ul>
        )}
        {c.week.length > 60 ? <p className="mt-1 text-xs text-muted">The first 60 of {c.week.length}; the table below lists every one.</p> : null}
      </div>
      <div>
        <h3 className="mb-1 text-sm">The month ahead <span className={`text-xs text-muted ${tip}`} title="Every dated step a document states, from this page's day to thirty days on.">{c.today} to {c.aheadTo}</span></h3>
        {c.ahead.length === 0 ? (hidden > 0
          ? <p className="text-xs text-muted" data-monitor-ahead-hidden={hidden}>None at significance {floor} or more; {lift(hidden, `${hidden} below it`)}.</p>
          : <p className="text-xs text-muted">No dated step in these thirty days.</p>) : (
          <ul className="max-h-72 overflow-y-auto text-xs" data-monitor-ahead={c.ahead.length}>
            {c.ahead.slice(0, 80).map(({ row, step }) => (
              <li key={stepKey(row, step)} className="border-b border-rule/60 py-1">
                <span className={`tabular-nums ${tip}`} title={`"${step.words}"`} data-check={stepKey(row, step)}>{step.date}</span>{" "}
                {KIND_WORDS[step.kind] ?? step.kind}: {row.body}, <a href={row.sources?.[0]}>{row.title.length > 100 ? row.title.slice(0, 97) + "..." : row.title}</a>
              </li>
            ))}
          </ul>
        )}
        {c.ahead.length > 80 ? <p className="mt-1 text-xs text-muted">The first 80 of {c.ahead.length}.</p> : null}
        {c.ahead.length > 0 && hidden > 0 ? <p className="mt-1 text-xs text-muted" data-monitor-ahead-hidden={hidden}>{lift(hidden, `${hidden} more below significance ${floor}`)}</p> : null}
      </div>
    </div>
  );
}
