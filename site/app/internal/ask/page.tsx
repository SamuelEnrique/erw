import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Section } from "@/components/Section";
import { rpc } from "@/lib/supabase";
import { readLimits, readSalt } from "@/lib/chat/limits";

// Session 128: what the question-answering tools spend, by day, against their ceilings. Internal: no nav link, not
// indexed, and gated by a token exactly as /internal/costs is: /internal/ask?token=<INTERNAL_COSTS_TOKEN>. The page
// answers 404 unless the token equals the server's, and the database answers nothing unless it equals the secret
// apply.py wrote (migration 023, internal_ask_spend). Rows: site_api_calls, the site's own model calls.
export const metadata: Metadata = { title: "Ask: spend (internal)", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

type Day = { day: string; step: string; calls: number; questions: number; calls_without_question: number; usd: number; unpriced: number };
type Spend = { today: string; days: Day[]; costliest: { day: string; step: string; calls: number; usd: number | null }[]; visitors_today: number; questions_today: number };

const usd = (v: number) => v.toFixed(4);
const STEP: Record<string, string> = { site_ask: "The general chat", site_ask_ercot: "Ask ERCOT" };

export default async function AskSpend({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const token = typeof sp.token === "string" ? sp.token : "";
  const want = process.env.INTERNAL_COSTS_TOKEN ?? "";
  if (want.length < 24 || token !== want) notFound();

  let s: Spend;
  try {
    s = await rpc<Spend>("internal_ask_spend", { p_token: token });
  } catch (e) {
    return <p className="text-sm">The spend could not be read: {(e as Error).message}</p>;
  }
  const limits = readLimits();
  const month = s.today.slice(0, 7);
  const sum = (rows: Day[]) => rows.reduce((a, r) => a + Number(r.usd), 0);
  const todayUsd = sum(s.days.filter((r) => r.day === s.today));
  const monthUsd = sum(s.days.filter((r) => r.day.startsWith(month)));
  const unpriced = s.days.reduce((a, r) => a + Number(r.unpriced), 0);
  const byDay = [...new Set(s.days.map((r) => r.day))].sort().reverse();
  const closed = !limits || !readSalt();
  return (
    <div data-ask-spend="1">
      <h1 className="mb-2 font-serif text-3xl text-accent">Ask: spend by day</h1>
      <p className="mb-6 max-w-3xl text-sm">What the question-answering tools (the general chat and Ask ERCOT) spent on model calls, by UTC day, against their ceilings. When a ceiling is reached the tools answer with a plain message and call no model until the day or the month turns over.</p>
      <Section title="Against the ceilings">
        <div className="overflow-x-auto">
          <table className="w-full max-w-2xl text-sm tabular-nums">
            <thead><tr className="border-b border-rule text-left text-xs text-muted"><th className="py-1 pr-3"></th><th className="pr-3 text-right">Spent, USD</th><th className="pr-3 text-right">Ceiling, USD</th><th className="text-right">State</th></tr></thead>
            <tbody>
              <tr className="border-b border-rule"><td className="py-1 pr-3">Today, {s.today}</td><td className="pr-3 text-right" data-n="today">{usd(todayUsd)}</td><td className="pr-3 text-right">{limits ? limits.daily_usd.toFixed(2) : "not set"}</td><td className="text-right">{limits && todayUsd >= limits.daily_usd ? "reached: not answering" : "under"}</td></tr>
              <tr className="border-b border-rule"><td className="py-1 pr-3">This month, {month}</td><td className="pr-3 text-right" data-n="month">{usd(monthUsd)}</td><td className="pr-3 text-right">{limits ? limits.monthly_usd.toFixed(2) : "not set"}</td><td className="text-right">{limits && monthUsd >= limits.monthly_usd ? "reached: not answering" : "under"}</td></tr>
            </tbody>
          </table>
        </div>
        <p className="mt-2 max-w-3xl text-xs text-muted">
          Questions per visitor per day: {limits ? limits.per_visitor_per_day : "not set"}. Today: {s.questions_today} questions admitted from {s.visitors_today} visitors (a visitor is counted by a keyed hash of its address that changes each day; no address is stored).
          {closed ? <span className="font-semibold text-ink"> The tools are closed: {limits ? "ASK_VISITOR_SALT is not set on the server" : "the ceilings are not set"}.</span> : null}
          {unpriced ? <span className="font-semibold text-ink"> {unpriced} calls in the last 62 days have no price: while one stands in the current month the tools are closed, because the spend cannot be counted.</span> : null}
        </p>
      </Section>
      <Section title="By day, last 62 days">
        <div className="overflow-x-auto">
          <table className="w-full text-sm tabular-nums">
            <thead><tr className="border-b border-rule text-left text-xs text-muted"><th className="py-1 pr-3">Day (UTC)</th><th className="pr-3">Tool</th><th className="pr-3 text-right">Questions</th><th className="pr-3 text-right">Model calls</th><th className="pr-3 text-right">USD</th><th className="text-right">USD a question</th></tr></thead>
            <tbody>
              {byDay.flatMap((d) => s.days.filter((r) => r.day === d).map((r) => (
                <tr key={`${d}|${r.step}`} className="border-b border-rule" data-day={d}>
                  <td className="py-1 pr-3 font-mono text-xs">{d}</td>
                  <td className="pr-3">{STEP[r.step] ?? r.step}</td>
                  <td className="pr-3 text-right">{r.questions}{r.calls_without_question ? <span className="text-muted"> ({r.calls_without_question} calls before questions were numbered)</span> : null}</td>
                  <td className="pr-3 text-right">{r.calls}</td>
                  <td className="pr-3 text-right">{usd(Number(r.usd))}{r.unpriced ? <span className="text-muted"> ({r.unpriced} unpriced)</span> : null}</td>
                  <td className="text-right">{r.questions && !r.calls_without_question ? usd(Number(r.usd) / r.questions) : <span className="text-muted">not held</span>}</td>
                </tr>
              )))}
            </tbody>
          </table>
        </div>
      </Section>
      <Section title="The ten costliest questions, last 62 days">
        {s.costliest.length ? (
          <div className="overflow-x-auto">
            <table className="w-full max-w-2xl text-sm tabular-nums">
              <thead><tr className="border-b border-rule text-left text-xs text-muted"><th className="py-1 pr-3">Day (UTC)</th><th className="pr-3">Tool</th><th className="pr-3 text-right">Model calls</th><th className="text-right">USD</th></tr></thead>
              <tbody>{s.costliest.map((q, i) => <tr key={i} className="border-b border-rule"><td className="py-1 pr-3 font-mono text-xs">{q.day}</td><td className="pr-3">{STEP[q.step] ?? q.step}</td><td className="pr-3 text-right">{q.calls}</td><td className="text-right">{q.usd === null ? "unpriced" : usd(Number(q.usd))}</td></tr>)}</tbody>
            </table>
          </div>
        ) : <p className="text-sm text-muted">No question has been numbered yet: questions carry a number from migration 023 on.</p>}
        <p className="mt-2 max-w-3xl text-xs text-muted">A question&apos;s text is not kept in the database, and neither is who asked it: this table holds its day, its tool, its calls and its cost.</p>
      </Section>
    </div>
  );
}
