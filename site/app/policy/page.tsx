import type { Metadata } from "next";
import { Cite } from "@/components/Cite";
import { NoData } from "@/components/NoData";
import { Related } from "@/components/Related";
import { Section } from "@/components/Section";
import { SiteLink } from "@/components/SiteLink";
import { policyActions, policyReads, renderTime } from "@/lib/data";
import { FIRST_VIEW_METHOD, METHOD, VIEWS, chosenOf, tagOf, viewHref, viewOf, type View } from "@/lib/policyweek";
import { allTags, weekData } from "@/lib/policyweekdata";
import { attempt } from "@/lib/supabase";
import { PolicyTable, type Row } from "./PolicyTable";
import { WeekView } from "./WeekView";

export const revalidate = 3600;
export const metadata: Metadata = { title: "Policy" };

const dotted = "cursor-help border-b border-dotted border-muted";
const TYPE: Record<string, string> = { rule: "Final rule", proposed_rule: "Proposed rule", notice: "Notice", press_release: "News release" };

// Session 157: the page's two views, both in the address (lib/policyweek.ts), and the Method note. One tool, one page,
// one address: /policy is the page as it was (every action, scored); /policy?view=week is "What changed this week".
function Views({ view }: { view: View }) {
  return (
    <div className="mb-4 flex flex-wrap items-center justify-between gap-x-6 gap-y-2">
      <nav aria-label="Views" className="flex flex-wrap gap-1 text-xs" data-views="1">
        {VIEWS.map(([k, label]) => (
          <a key={k} href={viewHref(k)} aria-current={view === k ? "page" : undefined} data-view={k} style={{ color: view === k ? "#fff" : "var(--color-ink)" }}
            className={`border px-2 py-1 no-underline ${view === k ? "border-accent bg-accent" : "border-rule bg-white hover:border-accent"}`}>{label}</a>
        ))}
      </nav>
      <p className="text-xs text-muted" data-method="1"><SiteLink href={METHOD.href}>Method, sources and gaps</SiteLink></p>
    </div>
  );
}

// Session 157: "What changed this week" (app/policy/WeekView.tsx). The rows are read and worded on the server
// (lib/policyweekdata.ts); the window and the filters the address names are the ones the view opens with.
async function Week({ q }: { q: Record<string, string | undefined> }) {
  const d = await weekData(renderTime());
  const chosen = chosenOf(q, { bodies: d.bodies.map((b) => b.key), topics: d.topics.map((t) => t.key), grids: d.grids.map((g) => g.key) });
  return (
    <>
      <p className="mb-5 max-w-3xl">
        The regulatory actions of the last seven and thirty days, by agency and topic: federal regulators, state commissions and grid operators.
      </p>
      <Section title="What changed this week">
        <WeekView today={d.today} rows={d.rows} bodies={d.bodies} topics={d.topics} grids={d.grids} dropped={d.dropped.length} missing={d.missing} droppedWhy={d.droppedWhy} held={d.held} chosen={chosen} />
        <Cite tables={["policy_actions", "policy_reads"]} note="Proceedings and orders of FERC and the state commissions from the site's own file, data/policy/state_rules.json" />
      </Section>
      <Related href="/policy" />
    </>
  );
}

// Session 24: the policy and regulatory monitor (platform tool 12)
export default async function PolicyPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const q = Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined]));
  const view = viewOf(q);
  if (view === "week") {
    return (
      <div data-policy="week">
        <h1 className="mb-1 text-3xl">Policy</h1>
        <Views view={view} />
        <Week q={q} />
      </div>
    );
  }
  const [a, r] = await Promise.all([attempt(policyActions), attempt(policyReads)]);
  const now = renderTime();
  if (!a.ok) return <NoData what="policy actions" reason={a.reason} />;
  const reads = new Map((r.ok ? r.data : []).map((x) => [x.action_event_id, x]));
  // Session 164: the rule's tags of every action, so that a reader reaches each tagged action whatever its date.
  const tagged = allTags(a.data);
  const rows: Row[] = a.data.map((x) => ({ ...x, event_date: x.event_date.slice(0, 10), read: reads.get(x.event_id) ?? null, tags: tagged.chips[x.event_id] ?? [] }));
  const tag = tagOf(q, tagged.topics.map((t) => t.key));
  const since = new Date(now - 7 * 86_400_000).toISOString().slice(0, 10);
  const week = rows.filter((x) => x.event_date >= since && Number(x.significance) >= 5).sort((p, q) => Number(q.significance) - Number(p.significance)).slice(0, 6);
  return (
    <div data-policy="all">
      <h1 className="mb-1 text-3xl">Policy</h1>
      <Views view={view} />
      {/* Session 164: the method paragraph that stood here is off the face. Each of its three sentences is the hover of
          the words it explains (lib/policyweek.ts, FIRST_VIEW_METHOD) and stands in the Method note. */}
      <p className="mb-5 max-w-3xl" data-policy-lead="1">
        Energy rules, proposed rules and notices of DOE, <span className={dotted} title={FIRST_VIEW_METHOD.ferc} data-policy-hover="ferc">FERC</span>, EPA, NRC, BLM and Interior from the Federal Register, and news releases of the NRC, DOE,
        the Texas PUC and the CPUC, since 2025-10-01, each <span className={dotted} title={FIRST_VIEW_METHOD.scored} data-policy-hover="scored">scored for significance</span> and, when it scores 5 or more,{" "}
        <span className={dotted} title={FIRST_VIEW_METHOD.read} data-policy-hover="read">read for its impact</span>.
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
        <PolicyTable rows={rows} tags={tagged.topics.map((t) => ({ key: t.key, label: t.label, why: t.why }))} tag={tag} missing={tagged.missing} />
        <Cite tables={["policy_actions", "policy_reads"]} note="Scores from warehouse/policy/score.py (the news rubric); reads from warehouse/policy/reads.py; the evidence spans are kept in the internal policy_reads_evidence" />
      </Section>
      <Related href="/policy" />
    </div>
  );
}
