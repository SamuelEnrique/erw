import type { Metadata } from "next";
import { cookies } from "next/headers";
import { notFound } from "next/navigation";
import { COOKIE } from "@/lib/release";
import { internalOk } from "@/lib/thesis/server";
import { Section } from "@/components/Section";
import { rpc } from "@/lib/supabase";

// Session 30 (Part B1): the Anthropic API spend of the ERW, internal. No nav link, not indexed, and gated by a token:
// /internal/costs?token=<INTERNAL_COSTS_TOKEN>. The page answers 404 unless the token equals the server's
// INTERNAL_COSTS_TOKEN, and the database answers nothing unless it equals the secret apply.py wrote (migration 010).
// Rows: api_cost_ledger (warehouse/llm.py: the daily run and sessions) and site_api_calls (the site's /ask).
export const metadata: Metadata = { title: "Costs (internal)", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

type Call = {
  ts_utc: string;
  session: string | null;
  step: string | null;
  model: string | null;
  input_tokens: number | null;
  cached_input_tokens: number | null;
  cache_write_tokens: number | null;
  output_tokens: number | null;
  usd: number | null;
};

const usd = (v: number) => `USD ${v.toFixed(2)}`;
const num = (v: number) => Math.round(v).toLocaleString("en-US");

function group(calls: Call[], key: (c: Call) => string) {
  const m = new Map<string, { calls: number; input: number; cached: number; output: number; usd: number; unpriced: number }>();
  for (const c of calls) {
    const k = key(c);
    const g = m.get(k) ?? { calls: 0, input: 0, cached: 0, output: 0, usd: 0, unpriced: 0 };
    g.calls += 1;
    g.input += (c.input_tokens ?? 0) + (c.cache_write_tokens ?? 0);
    g.cached += c.cached_input_tokens ?? 0;
    g.output += c.output_tokens ?? 0;
    if (c.usd === null || c.usd === undefined) g.unpriced += 1;
    else g.usd += Number(c.usd);
    m.set(k, g);
  }
  return [...m.entries()];
}

function Table({ rows, label }: { rows: ReturnType<typeof group>; label: string }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm tabular-nums">
        <thead>
          <tr className="border-b border-rule text-left text-xs text-muted">
            <th className="py-1 pr-3">{label}</th>
            <th className="pr-3 text-right">Calls</th>
            <th className="pr-3 text-right">Input tokens</th>
            <th className="pr-3 text-right">Cached input</th>
            <th className="pr-3 text-right">Output tokens</th>
            <th className="text-right">USD</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(([k, g]) => (
            <tr key={k} className="border-b border-rule">
              <td className="py-1 pr-3 font-mono text-xs">{k}</td>
              <td className="pr-3 text-right">{num(g.calls)}</td>
              <td className="pr-3 text-right">{num(g.input)}</td>
              <td className="pr-3 text-right">{num(g.cached)}</td>
              <td className="pr-3 text-right">{num(g.output)}</td>
              <td className="text-right">
                {g.usd.toFixed(4)}
                {g.unpriced ? <span className="text-muted"> ({g.unpriced} unpriced)</span> : null}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default async function Costs({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const token = typeof sp.token === "string" ? sp.token : "";
  const want = process.env.INTERNAL_COSTS_TOKEN ?? "";
  // session 177: the internal view's cookie opens the page as well, so the token need not travel in an address
  // (/internal/open). The old address, with ?token=, works as it did.
  if (want.length < 24 || (token !== want && !(await internalOk((await cookies()).get(COOKIE)?.value)))) notFound();

  let calls: Call[];
  try {
    calls = await rpc<Call[]>("internal_costs", { p_token: want });
  } catch (e) {
    return <p className="text-sm">The cost ledger could not be read: {(e as Error).message}</p>;
  }
  const now = Date.now();
  const since = now - 30 * 86_400_000;
  const last30 = calls.filter((c) => new Date(c.ts_utc).getTime() >= since);
  const total = last30.reduce((a, c) => a + Number(c.usd ?? 0), 0);
  const byDay = group(last30, (c) => c.ts_utc.slice(0, 10)).sort((a, b) => b[0].localeCompare(a[0]));
  const byStep = group(last30, (c) => `${c.session ?? ""} / ${c.step ?? ""}`).sort((a, b) => b[1].usd - a[1].usd);
  const byModel = group(last30, (c) => c.model ?? "").sort((a, b) => b[1].usd - a[1].usd);
  // projected monthly bill: the mean daily spend of the last 7 days (today included) times 30
  const week = last30.filter((c) => new Date(c.ts_utc).getTime() >= now - 7 * 86_400_000);
  const weekUsd = week.reduce((a, c) => a + Number(c.usd ?? 0), 0);
  const projected = (weekUsd / 7) * 30;
  const scheduled = last30.filter((c) => c.session === "daily");
  const schedWeek = scheduled.filter((c) => new Date(c.ts_utc).getTime() >= now - 7 * 86_400_000);
  const schedProjected = (schedWeek.reduce((a, c) => a + Number(c.usd ?? 0), 0) / 7) * 30;

  return (
    <>
      <h1 className="mb-1 text-3xl">API costs (internal)</h1>
      <p className="mb-5 max-w-3xl text-sm text-muted">
        Every Anthropic API call the ERW made in the last 30 days: the scheduled runs, the sessions and the site&apos;s /ask. From the
        internal cost ledger (<code className="font-mono">api_cost_ledger</code>, written by warehouse/llm.py at each call, and the
        site&apos;s <code className="font-mono">site_api_calls</code>), priced at warehouse/config/model_prices.yaml.
      </p>
      <div className="mb-8 grid grid-cols-1 gap-px border border-rule bg-rule sm:grid-cols-3">
        <div className="bg-panel p-3">
          <div className="text-xs text-muted">Last 30 days</div>
          <div className="text-2xl tabular-nums">{usd(total)}</div>
          <div className="text-xs text-muted">{num(last30.length)} calls</div>
        </div>
        <div className="bg-panel p-3">
          <div className="text-xs text-muted">Projected monthly bill, all calls</div>
          <div className="text-2xl tabular-nums">{usd(projected)}</div>
          <div className="text-xs text-muted">mean of the last 7 days ({usd(weekUsd)}) times 30</div>
        </div>
        <div className="bg-panel p-3">
          <div className="text-xs text-muted">Projected monthly bill, scheduled runs only</div>
          <div className="text-2xl tabular-nums">{usd(schedProjected)}</div>
          <div className="text-xs text-muted">session &quot;daily&quot;: the GitHub workflows, the same rule</div>
        </div>
      </div>
      {last30.length === 0 ? <p className="mb-8 text-sm">No call is recorded in the last 30 days.</p> : null}
      <Section title="Per day">
        <Table rows={byDay} label="Day (UTC)" />
      </Section>
      <Section title="Per step">
        <Table rows={byStep} label="Session / step" />
      </Section>
      <Section title="Per model">
        <Table rows={byModel} label="Model" />
      </Section>
    </>
  );
}
