import type { Metadata } from "next";
import { Cite } from "@/components/Cite";
import { NoData } from "@/components/NoData";
import { Related } from "@/components/Related";
import { Section } from "@/components/Section";
import { policyActions, policyReads, renderTime } from "@/lib/data";
import { attempt } from "@/lib/supabase";
import { PolicyTable, type Row } from "./PolicyTable";

export const revalidate = 3600;
export const metadata: Metadata = { title: "Policy" };

const TYPE: Record<string, string> = { rule: "Final rule", proposed_rule: "Proposed rule", notice: "Notice", press_release: "News release" };

// Session 24: the policy and regulatory monitor (platform tool 12)
export default async function PolicyPage() {
  const [a, r] = await Promise.all([attempt(policyActions), attempt(policyReads)]);
  const now = renderTime();
  if (!a.ok) return <NoData what="policy actions" reason={a.reason} />;
  const reads = new Map((r.ok ? r.data : []).map((x) => [x.action_event_id, x]));
  const rows: Row[] = a.data.map((x) => ({ ...x, event_date: x.event_date.slice(0, 10), read: reads.get(x.event_id) ?? null }));
  const since = new Date(now - 7 * 86_400_000).toISOString().slice(0, 10);
  const week = rows.filter((x) => x.event_date >= since && Number(x.significance) >= 5).sort((p, q) => Number(q.significance) - Number(p.significance)).slice(0, 6);
  return (
    <>
      <h1 className="mb-1 text-3xl">Policy</h1>
      <p className="mb-2 max-w-3xl">
        Energy rules, proposed rules and notices of DOE, FERC, EPA, NRC, BLM and Interior from the Federal Register, and news releases of the NRC, DOE,
        the Texas PUC and the CPUC, since 2025-10-01, each scored for significance and, when it scores 5 or more, read for its impact.
      </p>
      <p className="mb-5 max-w-3xl text-sm text-muted">
        Significance uses the same rubric as the news digest. An impact read is written by a model from the action&apos;s own text, and each field is kept only
        when the exact words it rests on are found in that text; a blank field was dropped for that reason. FERC&apos;s own pages cannot be read automatically,
        so FERC appears through the Federal Register.
      </p>
      <Section title="This week in policy">
        {week.length === 0 ? (
          <p className="text-sm text-muted">No action scored 5 or more since {since}.</p>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {week.map((x) => (
              <a key={x.event_id} href={x.source_url} className="block border border-rule bg-panel p-3 text-sm no-underline hover:border-accent">
                <div className="text-xs text-muted">
                  {x.agency} {TYPE[x.action_type] ?? x.action_type}, {x.event_date}
                </div>
                <div className="mt-1 text-ink">{x.title.length > 160 ? x.title.slice(0, 157) + "..." : x.title}</div>
                {x.read?.plain_read ? <div className="mt-1 text-xs text-muted">{x.read.plain_read}</div> : x.why ? <div className="mt-1 text-xs text-muted">{x.why}</div> : null}
              </a>
            ))}
          </div>
        )}
      </Section>
      <Section title="Every action">
        <PolicyTable rows={rows} />
        <Cite tables={["policy_actions", "policy_reads"]} note="Scores from warehouse/policy/score.py (the news rubric); reads from warehouse/policy/reads.py; the evidence spans are kept in the internal policy_reads_evidence" />
      </Section>
      <Related href="/policy" />
    </>
  );
}
