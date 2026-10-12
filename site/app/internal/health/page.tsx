import type { Metadata } from "next";
import { cookies } from "next/headers";
import { notFound } from "next/navigation";
import record from "@/data/health_days.json";
import { COOKIE } from "@/lib/release";
import { internalOk } from "@/lib/thesis/server";

// Session 202: the health of the scheduled jobs, by day, and the green streak: "Scheduled jobs green for N days". That
// line is the counter of the public day's gate (docs/roadmap.md: seven green days of every scheduled job). Internal: no
// nav link, not indexed, and behind the internal view as /internal/waits is: the page answers 404 unless the browser
// holds the internal cookie. A token in the address opens nothing.
//
// The numbers come from one committed file, data/health_days.json, which warehouse/health.py writes from the Supabase
// table erw_health each day with the daily summary (queue/summary/<day>-health.md): the table answers the service key
// only, and the site holds none. So the page is as new as the last daily run, and says which day it is counted to.
// N is computed there (health.py, green_streak) and written into the file: the days in a row, back from the newest day
// recorded, on which no step of a scheduled job failed. It is 0 whenever a job failed on that newest day, and a day
// with no row at all ends the count. A machine's own daily run counts (its steps are named dm_...); a session's other
// rows are shown and do not count. No sentence here judges: each states a count.
export const metadata: Metadata = { title: "Scheduled jobs (internal)", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

type Job = { ok: number; skipped: number; retried: number; failed: number; runs: number };
type Failure = { at: string; workflow: string; step: string; reason: string };
type Day = { rows: number; failed: number; jobs: Record<string, Job>; failures: Failure[] };
type Record_ = { written: string; green_days: number; counted_to: string | null; days: Record<string, Day> };

const JOBS = ["daily prices", "latest prices", "hourly network", "chain watch", "energy roundup", "weekly vacuum"];
const n = (v: number) => Math.round(Number(v)).toLocaleString("en-US");

function Cell({ j }: { j: Job | undefined }) {
  if (!j) return <td className="pr-3 text-right text-muted">no run</td>;
  return (
    <td className="pr-3 text-right">
      {n(j.runs)}{j.failed ? <>, <span className="font-semibold text-accent">{n(j.failed)} failed</span></> : null}{j.retried ? <>, <span className="text-muted">{n(j.retried)} retried</span></> : null}
    </td>
  );
}

export default async function HealthPage() {
  if (!(await internalOk((await cookies()).get(COOKIE)?.value))) notFound();

  const r = record as unknown as Record_;
  const days = Object.entries(r.days ?? {}).sort((a, b) => b[0].localeCompare(a[0]));
  const green = Number(r.green_days) || 0;
  const failures = days.flatMap(([, d]) => d.failures ?? []).sort((a, b) => b.at.localeCompare(a.at));
  const machines = (d: Day): Job | undefined => {
    const ms = Object.entries(d.jobs).filter(([w]) => w.startsWith("local:")).map(([, j]) => j);
    if (!ms.length) return undefined;
    return ms.reduce((a, j) => ({ ok: a.ok + j.ok, skipped: a.skipped + j.skipped, retried: a.retried + j.retried, failed: a.failed + j.failed, runs: a.runs + j.runs }),
      { ok: 0, skipped: 0, retried: 0, failed: 0, runs: 0 });
  };

  return (
    <div data-health="1">
      <h1 className="mb-1 text-3xl">Scheduled jobs (internal)</h1>
      <p className="mb-2 font-serif text-xl" data-green-days={green} data-counted-to={r.counted_to ?? ""}>
        Scheduled jobs green for {n(green)} {green === 1 ? "day" : "days"}.
      </p>
      <p className="mb-5 max-w-3xl text-sm text-muted">
        Counted to {r.counted_to ?? "no day"} (UTC): the days in a row, back from that day, on which no step of a scheduled job was recorded as failed.
        It is 0 whenever a job failed on that day; a day with no record ends the count. A step that failed once and passed at the second try is
        &quot;retried&quot;, not failed. Written {r.written} by <code>warehouse/health.py</code> from the table <code>erw_health</code>, with each
        day&apos;s summary; today&apos;s steps are counted tomorrow.
      </p>

      <h2 className="mb-2 text-xl">By day</h2>
      <div className="mb-8 overflow-x-auto">
        <table className="w-full text-sm tabular-nums" style={{ minWidth: 860 }}>
          <caption className="sr-only">Runs of each scheduled job by UTC day, with the steps that failed</caption>
          <thead>
            <tr className="border-b border-ink text-left text-xs text-muted">
              <th scope="col" className="py-1 pr-3">Day (UTC)</th>
              <th scope="col" className="pr-3">Day&apos;s result</th>
              {JOBS.map((j) => <th scope="col" key={j} className="pr-3 text-right">{j}, runs</th>)}
              <th scope="col" className="pr-3 text-right">machines, steps</th>
            </tr>
          </thead>
          <tbody>
            {days.map(([day, d]) => (
              <tr key={day} className="border-b border-rule" data-health-day={day} data-failed={d.failed}>
                <th scope="row" className="py-1 pr-3 text-left font-mono text-xs font-normal">{day}</th>
                <td className="pr-3">{d.failed ? <span className="font-semibold text-accent">red: {n(d.failed)} failed</span> : <span>green</span>}</td>
                {JOBS.map((j) => <Cell key={j} j={d.jobs[j]} />)}
                <Cell j={machines(d)} />
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2 className="mb-2 text-xl">Failed steps, {days.length ? `${days[days.length - 1][0]} to ${days[0][0]}` : "no day recorded"}</h2>
      {failures.length ? (
        <div className="overflow-x-auto">
          <table className="w-full text-sm" style={{ minWidth: 760 }}>
            <caption className="sr-only">Every step recorded as failed, newest first</caption>
            <thead>
              <tr className="border-b border-ink text-left text-xs text-muted">
                <th scope="col" className="py-1 pr-3">When (UTC)</th>
                <th scope="col" className="pr-3">Job</th>
                <th scope="col" className="pr-3">Step</th>
                <th scope="col">Recorded reason</th>
              </tr>
            </thead>
            <tbody>
              {failures.map((f, i) => (
                <tr key={`${f.at}|${f.workflow}|${f.step}|${i}`} className="border-b border-rule align-top" data-health-failure={f.step}>
                  <td className="whitespace-nowrap py-1 pr-3 font-mono text-xs">{f.at.replace("T", " ")}</td>
                  <td className="whitespace-nowrap pr-3">{f.workflow}</td>
                  <td className="whitespace-nowrap pr-3">{f.step}</td>
                  <td className="break-words text-xs text-muted">{f.reason || "no reason recorded"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="text-sm text-muted">No step is recorded as failed in these days.</p>
      )}
    </div>
  );
}
